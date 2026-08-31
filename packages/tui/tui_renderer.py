#!/usr/bin/env python3
"""NovaCode Advanced Terminal UI Renderer.

A sophisticated terminal rendering engine providing split-panel layouts,
streaming markdown rendering with syntax highlighting, autocomplete,
progress bars, spinners, color themes, mouse support detection, and
terminal resize handling.

Uses only Python standard library.
"""

from __future__ import annotations

import os
import re
import shutil
import sys
import time
import threading
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Iterator,
    List,
    Optional,
    Tuple,
    Union,
)


# ─── ANSI Escape Helpers ───────────────────────────────────────────────────

class ANSI:
    """ANSI escape sequence builder."""

    ESC = "\033["
    CSI = "\033["

    @staticmethod
    def fg(r: int, g: int, b: int) -> str:
        return f"\033[38;2;{r};{g};{b}m"

    @staticmethod
    def bg(r: int, g: int, b: int) -> str:
        return f"\033[48;2;{r};{g};{b}m"

    @staticmethod
    def fg256(code: int) -> str:
        return f"\033[38;5;{code}m"

    @staticmethod
    def bg256(code: int) -> str:
        return f"\033[48;5;{code}m"

    @staticmethod
    def move_to(col: int, row: int) -> str:
        return f"\033[{row};{col}H"

    @staticmethod
    def move_up(n: int = 1) -> str:
        return f"\033[{n}A"

    @staticmethod
    def move_down(n: int = 1) -> str:
        return f"\033[{n}B"

    @staticmethod
    def move_left(n: int = 1) -> str:
        return f"\033[{n}D"

    @staticmethod
    def move_right(n: int = 1) -> str:
        return f"\033[{n}C"

    @staticmethod
    def clear_line() -> str:
        return "\033[2K"

    @staticmethod
    def clear_screen() -> str:
        return "\033[2J\033[H"

    @staticmethod
    def hide_cursor() -> str:
        return "\033[?25l"

    @staticmethod
    def show_cursor() -> str:
        return "\033[?25h"

    @staticmethod
    def enable_mouse() -> str:
        return "\033[?1000h\033[?1002h\033[?1015h\033[?1006h"

    @staticmethod
    def disable_mouse() -> str:
        return "\033[?1006l\033[?1015l\033[?1002l\033[?1000l"

    @staticmethod
    def enable_alt_screen() -> str:
        return "\033[?1049h"

    @staticmethod
    def disable_alt_screen() -> str:
        return "\033[?1049l"

    @staticmethod
    def reset() -> str:
        return "\033[0m"

    @staticmethod
    def bold() -> str:
        return "\033[1m"

    @staticmethod
    def dim() -> str:
        return "\033[2m"

    @staticmethod
    def italic() -> str:
        return "\033[3m"

    @staticmethod
    def underline() -> str:
        return "\033[4m"


# ─── Color Themes ──────────────────────────────────────────────────────────

class ThemeName(str, Enum):
    DARK = "dark"
    LIGHT = "light"
    NORD = "nord"


@dataclass(frozen=True)
class Theme:
    """Terminal color theme definition."""
    name: str
    bg: Tuple[int, int, int]
    fg: Tuple[int, int, int]
    muted: Tuple[int, int, int]
    accent: Tuple[int, int, int]
    success: Tuple[int, int, int]
    warning: Tuple[int, int, int]
    error: Tuple[int, int, int]
    code_bg: Tuple[int, int, int]
    border: Tuple[int, int, int]
    highlight: Tuple[int, int, int]
    user_bubble: Tuple[int, int, int]
    assistant_bubble: Tuple[int, int, int]


THEMES: Dict[ThemeName, Theme] = {
    ThemeName.DARK: Theme(
        name="dark",
        bg=(12, 12, 18),
        fg=(220, 220, 230),
        muted=(140, 140, 160),
        accent=(86, 156, 214),
        success=(80, 200, 120),
        warning=(255, 198, 109),
        error=(255, 85, 85),
        code_bg=(25, 25, 35),
        border=(60, 60, 80),
        highlight=(45, 45, 65),
        user_bubble=(40, 50, 80),
        assistant_bubble=(30, 35, 50),
    ),
    ThemeName.LIGHT: Theme(
        name="light",
        bg=(250, 250, 252),
        fg=(30, 30, 40),
        muted=(120, 120, 140),
        accent=(0, 102, 204),
        success=(0, 150, 80),
        warning=(200, 130, 0),
        error=(200, 40, 40),
        code_bg=(240, 240, 245),
        border=(200, 200, 210),
        highlight=(230, 230, 240),
        user_bubble=(220, 230, 250),
        assistant_bubble=(235, 235, 240),
    ),
    ThemeName.NORD: Theme(
        name="nord",
        bg=(46, 52, 64),
        fg=(216, 222, 233),
        muted=(120, 130, 150),
        accent=(136, 192, 208),
        success=(163, 190, 140),
        warning=(235, 203, 139),
        error=(191, 97, 106),
        code_bg=(59, 66, 82),
        border=(76, 86, 106),
        highlight=(67, 76, 94),
        user_bubble=(76, 86, 106),
        assistant_bubble=(59, 66, 82),
    ),
}


# ─── Syntax Highlighting ───────────────────────────────────────────────────

# Token types with semantic meaning
TOKEN_KEYWORD = "keyword"
TOKEN_STRING = "string"
TOKEN_COMMENT = "comment"
TOKEN_NUMBER = "number"
TOKEN_FUNCTION = "function"
TOKEN_OPERATOR = "operator"
TOKEN_TYPE = "type"
TOKEN_PUNCTUATION = "punctuation"

# Language keyword sets
PY_KEYWORDS = {
    "False", "None", "True", "and", "as", "assert", "async", "await",
    "break", "class", "continue", "def", "del", "elif", "else", "except",
    "finally", "for", "from", "global", "if", "import", "in", "is",
    "lambda", "nonlocal", "not", "or", "pass", "raise", "return",
    "try", "while", "with", "yield",
}

JS_KEYWORDS = {
    "break", "case", "catch", "class", "const", "continue", "debugger",
    "default", "delete", "do", "else", "export", "extends", "false",
    "finally", "for", "function", "if", "import", "in", "instanceof",
    "let", "new", "null", "return", "super", "switch", "this", "throw",
    "true", "try", "typeof", "undefined", "var", "void", "while", "with",
    "yield", "async", "await", "of",
}

RUST_KEYWORDS = {
    "as", "break", "const", "continue", "crate", "else", "enum", "extern",
    "false", "fn", "for", "if", "impl", "in", "let", "loop", "match",
    "mod", "move", "mut", "pub", "ref", "return", "self", "Self",
    "static", "struct", "super", "trait", "true", "type", "unsafe",
    "use", "where", "while", "async", "await", "dyn",
}

GO_KEYWORDS = {
    "break", "case", "chan", "const", "continue", "default", "defer",
    "else", "fallthrough", "for", "func", "go", "goto", "if", "import",
    "interface", "map", "package", "range", "return", "select", "struct",
    "switch", "type", "var",
}

COMMON_TYPES = {
    "int", "str", "float", "bool", "list", "dict", "tuple", "set",
    "bytes", "bytearray", "Optional", "Union", "List", "Dict", "Tuple",
    "Set", "Any", "None", "String", "Number", "Boolean", "Array",
    "Promise", "void", "null", "undefined", "string", "number",
    "Vec", "Option", "Result", "String", "HashMap", "i32", "i64",
    "u32", "u64", "f32", "f64", "bool", "char", "usize", "isize",
}


class SyntaxHighlighter:
    """Regex-based syntax highlighter for common languages."""

    # Pattern definitions
    TRIPLE_QUOTE = r'(?s)("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\')'
    SINGLE_STRING = r'("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')'
    COMMENT_HASH = r'(#[^\n]*)'
    COMMENT_SLASH = r'(//[^\n]*)'
    COMMENT_BLOCK = r'(?s)/\*[\s\S]*?\*/'
    NUMBER = r'\b(?:0x[0-9a-fA-F]+|0b[01]+|0o[0-7]+|\d+\.?\d*(?:[eE][+-]?\d+)?)\b'
    FUNCTION = r'\b([a-zA-Z_]\w*)\s*\('
    TYPE_CAPS = r'\b([A-Z]\w+)\b'

    def __init__(self):
        self._patterns: Dict[str, List[Tuple[str, str]]] = {}
        self._build_patterns()

    def _build_patterns(self):
        """Build compiled regex patterns per language."""
        for lang in ("python", "javascript", "typescript", "rust", "go",
                     "c", "cpp", "java", "ruby", "shell", "sql"):
            patterns: List[Tuple[str, str]] = []

            # Comments first (highest priority)
            if lang in ("python", "ruby", "shell", "sql", "yaml"):
                patterns.append((self.COMMENT_HASH, TOKEN_COMMENT))
            elif lang in ("javascript", "typescript", "rust", "go", "c", "cpp", "java"):
                patterns.append((self.COMMENT_SLASH, TOKEN_COMMENT))
                patterns.append((self.COMMENT_BLOCK, TOKEN_COMMENT))

            # Strings
            if lang == "python":
                patterns.append((self.TRIPLE_QUOTE, TOKEN_STRING))
            patterns.append((self.SINGLE_STRING, TOKEN_STRING))

            # Numbers
            patterns.append((self.NUMBER, TOKEN_NUMBER))

            # Functions
            patterns.append((self.FUNCTION, TOKEN_FUNCTION))

            # Types (capitalized words)
            patterns.append((self.TYPE_CAPS, TOKEN_TYPE))

            self._patterns[lang] = patterns

    def highlight(self, code: str, language: str) -> str:
        """Return code with ANSI color codes applied."""
        theme = Renderer.theme
        if language not in self._patterns:
            language = "python"

        colors = {
            TOKEN_KEYWORD: ANSI.fg(theme.accent[0], theme.accent[1], theme.accent[2]),
            TOKEN_STRING: ANSI.fg(theme.success[0], theme.success[1], theme.success[2]),
            TOKEN_COMMENT: ANSI.fg(theme.muted[0], theme.muted[1], theme.muted[2]),
            TOKEN_NUMBER: ANSI.fg(theme.warning[0], theme.warning[1], theme.warning[2]),
            TOKEN_FUNCTION: ANSI.fg(200, 180, 255),
            TOKEN_TYPE: ANSI.fg(100, 200, 220),
        }

        keywords = self._get_keywords(language)
        patterns = self._patterns[language]

        # Build a combined regex for all tokens
        tokens: List[Tuple[int, int, str, str]] = []  # start, end, type, text

        # Find all keyword matches
        for kw in keywords:
            for m in re.finditer(rf'\b{re.escape(kw)}\b', code):
                tokens.append((m.start(), m.end(), TOKEN_KEYWORD, m.group(0)))

        # Find all pattern matches
        for pattern, token_type in patterns:
            for m in re.finditer(pattern, code):
                if token_type == TOKEN_FUNCTION:
                    tokens.append((m.start(1), m.end(1), token_type, m.group(1)))
                elif token_type == TOKEN_TYPE:
                    word = m.group(1)
                    if word in COMMON_TYPES:
                        tokens.append((m.start(1), m.end(1), token_type, word))
                else:
                    tokens.append((m.start(), m.end(), token_type, m.group(0)))

        if not tokens:
            return code

        # Sort by start position and resolve overlaps (first match wins)
        tokens.sort(key=lambda t: t[0])
        filtered: List[Tuple[int, int, str, str]] = []
        last_end = -1
        for start, end, ttype, text in tokens:
            if start >= last_end:
                filtered.append((start, end, ttype, text))
                last_end = end

        # Build output
        result: List[str] = []
        pos = 0
        for start, end, ttype, text in filtered:
            if start > pos:
                result.append(code[pos:start])
            color = colors.get(ttype, "")
            result.append(f"{color}{text}{ANSI.reset()}")
            pos = end

        if pos < len(code):
            result.append(code[pos:])

        return "".join(result)

    def _get_keywords(self, language: str) -> set:
        keyword_map = {
            "python": PY_KEYWORDS,
            "javascript": JS_KEYWORDS,
            "typescript": JS_KEYWORDS,
            "rust": RUST_KEYWORDS,
            "go": GO_KEYWORDS,
            "c": C_KEYWORDS,
            "cpp": CPP_KEYWORDS,
            "java": JAVA_KEYWORDS,
        }
        return keyword_map.get(language, set())


# Extended keyword sets
C_KEYWORDS = {
    "auto", "break", "case", "char", "const", "continue", "default", "do",
    "double", "else", "enum", "extern", "float", "for", "goto", "if",
    "inline", "int", "long", "register", "restrict", "return", "short",
    "signed", "sizeof", "static", "struct", "switch", "typedef", "union",
    "unsigned", "void", "volatile", "while",
}

CPP_KEYWORDS = C_KEYWORDS | {
    "alignas", "alignof", "and", "and_eq", "asm", "bitand", "bitor",
    "bool", "catch", "class", "compl", "concept", "constexpr", "const_cast",
    "decltype", "delete", "dynamic_cast", "explicit", "export", "false",
    "friend", "mutable", "namespace", "new", "noexcept", "not", "not_eq",
    "nullptr", "operator", "or", "or_eq", "private", "protected", "public",
    "reinterpret_cast", "requires", "static_assert", "static_cast",
    "template", "this", "thread_local", "throw", "true", "try", "typeid",
    "typename", "using", "virtual", "wchar_t", "xor", "xor_eq",
}

JAVA_KEYWORDS = {
    "abstract", "assert", "boolean", "break", "byte", "case", "catch",
    "char", "class", "const", "continue", "default", "do", "double",
    "else", "enum", "extends", "final", "finally", "float", "for",
    "goto", "if", "implements", "import", "instanceof", "int",
    "interface", "long", "native", "new", "package", "private",
    "protected", "public", "return", "short", "static", "strictfp",
    "super", "switch", "synchronized", "this", "throw", "throws",
    "transient", "try", "void", "volatile", "while", "true", "false", "null",
}


# ─── Markdown Parser ───────────────────────────────────────────────────────

@dataclass
class MarkdownBlock:
    """A parsed markdown block."""
    type: str  # paragraph, heading, code, list, quote, table, hr, empty
    content: str
    language: str = ""
    level: int = 0
    items: List[str] = field(default_factory=list)
    headers: List[str] = field(default_factory=list)
    rows: List[List[str]] = field(default_factory=list)


class MarkdownParser:
    """Lightweight markdown block parser."""

    def parse(self, text: str) -> List[MarkdownBlock]:
        """Parse markdown text into blocks."""
        blocks: List[MarkdownBlock] = []
        lines = text.split("\n")
        i = 0

        while i < len(lines):
            line = lines[i]

            # Empty line
            if not line.strip():
                i += 1
                continue

            # Code fence
            if line.strip().startswith("```"):
                fence = line.strip()
                lang = fence[3:].strip()
                i += 1
                code_lines: List[str] = []
                while i < len(lines) and not lines[i].strip().startswith("```"):
                    code_lines.append(lines[i])
                    i += 1
                i += 1  # skip closing fence
                blocks.append(MarkdownBlock(
                    type="code",
                    content="\n".join(code_lines),
                    language=lang or "text",
                ))
                continue

            # Heading
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if heading_match:
                level = len(heading_match.group(1))
                blocks.append(MarkdownBlock(
                    type="heading",
                    content=heading_match.group(2),
                    level=level,
                ))
                i += 1
                continue

            # HR
            if re.match(r'^(\*{3,}|-{3,}|_{3,})$', line.strip()):
                blocks.append(MarkdownBlock(type="hr", content=""))
                i += 1
                continue

            # Blockquote
            if line.strip().startswith(">"):
                quote_lines: List[str] = []
                while i < len(lines) and lines[i].strip().startswith(">"):
                    quote_lines.append(lines[i].strip().lstrip(">").strip())
                    i += 1
                blocks.append(MarkdownBlock(
                    type="quote",
                    content="\n".join(quote_lines),
                ))
                continue

            # Table
            if "|" in line and i + 1 < len(lines) and re.match(r'^[\s|:-]+$', lines[i + 1]):
                headers = [c.strip() for c in line.strip("|").split("|")]
                i += 2  # skip header and separator
                rows: List[List[str]] = []
                while i < len(lines) and "|" in lines[i] and lines[i].strip():
                    row = [c.strip() for c in lines[i].strip("|").split("|")]
                    rows.append(row)
                    i += 1
                blocks.append(MarkdownBlock(
                    type="table",
                    content="",
                    headers=headers,
                    rows=rows,
                ))
                continue

            # List
            if re.match(r'^(\s*)([-*+]|\d+\.)\s', line):
                items: List[str] = []
                while i < len(lines) and re.match(r'^(\s*)([-*+]|\d+\.)\s', lines[i]):
                    item = re.sub(r'^(\s*)([-*+]|\d+\.)\s+', '', lines[i])
                    items.append(item)
                    i += 1
                blocks.append(MarkdownBlock(
                    type="list",
                    content="",
                    items=items,
                ))
                continue

            # Paragraph (collect lines until blank)
            para_lines: List[str] = []
            while i < len(lines) and lines[i].strip():
                para_lines.append(lines[i])
                i += 1
            blocks.append(MarkdownBlock(
                type="paragraph",
                content=" ".join(para_lines),
            ))

        return blocks


# ─── Autocomplete ───────────────────────────────────────────────────────────

@dataclass
class CompletionItem:
    """A single autocomplete suggestion."""
    text: str
    display: str
    description: str = ""
    icon: str = ""


class AutocompleteEngine:
    """Provides autocomplete suggestions for slash commands and @file refs."""

    SLASH_COMMANDS: List[CompletionItem] = [
        CompletionItem("/quit", "/quit", "Exit NovaCode", "⏻"),
        CompletionItem("/clear", "/clear", "Clear chat history", "✦"),
        CompletionItem("/model", "/model <name>", "Switch model", "◇"),
        CompletionItem("/mode", "/mode <mode>", "Switch mode", "◈"),
        CompletionItem("/nsfw", "/nsfw", "Toggle unrestricted mode", "⚠"),
        CompletionItem("/plan", "/plan <desc>", "Create implementation plan", "◧"),
        CompletionItem("/tasks", "/tasks", "Show task list", "☑"),
        CompletionItem("/memory", "/memory save|search", "Memory operations", "◆"),
        CompletionItem("/sessions", "/sessions", "List saved sessions", "◫"),
        CompletionItem("/resume", "/resume <id>", "Resume a session", "▶"),
        CompletionItem("/files", "/files [path]", "Browse files", "▤"),
        CompletionItem("/search", "/search <pattern>", "Search codebase", "⚲"),
        CompletionItem("/git", "/git <subcommand>", "Git operations", "⎇"),
        CompletionItem("/review", "/review [path]", "Code review", "◉"),
        CompletionItem("/mcp", "/mcp", "List MCP servers", "⬡"),
        CompletionItem("/rules", "/rules", "Show loaded rules", "▣"),
        CompletionItem("/stats", "/stats", "Session statistics", "◫"),
        CompletionItem("/help", "/help", "Show help", "?"),
    ]

    def complete(self, text: str) -> List[CompletionItem]:
        """Get autocomplete suggestions for current input."""
        if not text:
            return []

        # Slash command completion
        if text.startswith("/") and " " not in text:
            prefix = text.lower()
            return [
                cmd for cmd in self.SLASH_COMMANDS
                if cmd.text.startswith(prefix)
            ]

        # @file completion
        if "@" in text:
            at_pos = text.rfind("@")
            if at_pos >= 0 and (at_pos == 0 or text[at_pos - 1] == " "):
                partial = text[at_pos + 1:]
                return self._file_completions(partial)

        return []

    def _file_completions(self, partial: str) -> List[CompletionItem]:
        """Get file path completions."""
        from pathlib import Path
        results: List[CompletionItem] = []

        base_dir = Path(".")
        if "/" in partial:
            dir_part = partial.rsplit("/", 1)[0]
            base_dir = Path(dir_part) if dir_part else Path(".")
            partial = partial.rsplit("/", 1)[-1]

        if not base_dir.exists():
            return results

        try:
            for entry in sorted(base_dir.iterdir()):
                name = entry.name
                if name.startswith("."):
                    continue
                if name.startswith(partial):
                    icon = "📁" if entry.is_dir() else "📄"
                    suffix = "/" if entry.is_dir() else ""
                    full = (base_dir / name).as_posix() + suffix
                    results.append(CompletionItem(
                        text=f"@{full}",
                        display=f"{icon} {name}{suffix}",
                        description="directory" if entry.is_dir() else "file",
                        icon=icon,
                    ))
                    if len(results) >= 20:
                        break
        except PermissionError:
            pass

        return results


# ─── Terminal Info ──────────────────────────────────────────────────────────

@dataclass
class TerminalInfo:
    """Terminal capabilities and state."""
    columns: int = 80
    rows: int = 24
    color_depth: int = 8  # 8, 256, or 16777216 (24-bit)
    supports_mouse: bool = False
    supports_unicode: bool = False
    is_tty: bool = False
    term_program: str = ""

    def refresh(self):
        """Update terminal info from environment."""
        size = shutil.get_terminal_size((80, 24))
        self.columns = size.columns
        self.rows = size.lines
        self.is_tty = sys.stdout.isatty()

        term = os.environ.get("TERM", "")
        colorterm = os.environ.get("COLORTERM", "")
        self.term_program = os.environ.get("TERM_PROGRAM", "")

        # Detect color depth
        if colorterm in ("truecolor", "24bit") or "24bit" in term:
            self.color_depth = 16777216
        elif "256" in term:
            self.color_depth = 256
        else:
            self.color_depth = 8

        # Detect unicode support
        lang = os.environ.get("LANG", "")
        lc_all = os.environ.get("LC_ALL", "")
        self.supports_unicode = "UTF-8" in lang or "UTF-8" in lc_all or "utf8" in lang.lower()

        # Mouse support is always available via ANSI escapes in modern terminals
        self.supports_mouse = self.is_tty


# ─── Streaming Buffer ──────────────────────────────────────────────────────

class StreamBuffer:
    """Buffer for accumulating and rendering streaming content."""

    def __init__(self):
        self._buffer: List[str] = []
        self._raw: str = ""
        self._lock = threading.Lock()

    def append(self, text: str):
        """Append text to the buffer."""
        with self._lock:
            self._buffer.append(text)
            self._raw += text

    def get_and_clear(self) -> str:
        """Get accumulated text and clear buffer."""
        with self._lock:
            text = "".join(self._buffer)
            self._buffer.clear()
            return text

    @property
    def raw(self) -> str:
        with self._lock:
            return self._raw

    @property
    def pending(self) -> str:
        with self._lock:
            return "".join(self._buffer)


# ─── Progress Bar ───────────────────────────────────────────────────────────

class ProgressBar:
    """Visual progress bar with ETA and percentage."""

    BAR_STYLES = {
        "blocks": ("█", "░"),
        "arrows": ("▶", "·"),
        "dots": ("●", "○"),
        "thin": ("┃", "│"),
    }

    def __init__(
        self,
        context: str,
        total: int,
        width: int = 40,
        style: str = "blocks",
        show_eta: bool = True,
        show_percent: bool = True,
    ):
        self.context = context
        self.total = total
        self.width = width
        self.style = style
        self.show_eta = show_eta
        self.show_percent = show_percent
        self.current = 0
        self.start_time = time.time()
        self._done = False
        self._last_render = ""

    def update(self, amount: int = 1):
        """Update progress by amount."""
        self.current = min(self.current + amount, self.total)
        self.render()

    def set(self, value: int):
        """Set progress to specific value."""
        self.current = min(value, self.total)
        self.render()

    def render(self) -> str:
        """Render the progress bar string."""
        if self._done:
            return self._last_render

        theme = Renderer.theme
        fill_char, empty_char = self.BAR_STYLES.get(self.style, self.BAR_STYLES["blocks"])

        ratio = self.current / self.total if self.total > 0 else 0
        filled = int(self.width * ratio)
        empty = self.width - filled

        pct = f"{ratio * 100:5.1f}%" if self.show_percent else ""

        elapsed = time.time() - self.start_time
        eta_str = ""
        if self.show_eta and self.current > 0 and self.current < self.total:
            eta = (elapsed / self.current) * (self.total - self.current)
            eta_str = f" ETA:{eta:.0f}s"
        elif self.show_eta and self.current >= self.total:
            eta_str = f" {elapsed:.1f}s"

        bar = (
            f"{ANSI.fg(theme.accent[0], theme.accent[1], theme.accent[2])}"
            f"{fill_char * filled}"
            f"{ANSI.fg(theme.muted[0], theme.muted[1], theme.muted[2])}"
            f"{empty_char * empty}"
            f"{ANSI.reset()}"
        )

        result = f"  {self.context} {bar} {pct}{eta_str}"
        self._last_render = result
        return result

    def finish(self, message: str = ""):
        """Mark as complete."""
        self.current = self.total
        self._done = True
        theme = Renderer.theme
        msg = message or f"{self.context} complete"
        result = (
            f"  {ANSI.fg(theme.success[0], theme.success[1], theme.success[2])}"
            f"✓{ANSI.reset()} {msg}"
        )
        self._last_render = result
        return result

    def __enter__(self):
        return self

    def __exit__(self, *args):
        if not self._done:
            print(self.finish())


# ─── Spinner ───────────────────────────────────────────────────────────────

class Spinner:
    """Animated spinner for indeterminate operations."""

    STYLES = {
        "dots": ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
        "line": ["-", "\\", "|", "/"],
        "pulse": ["●", "◐", "○", "◑"],
        "star": ["✶", "✸", "✹", "✺", "✹", "✷"],
        "bounce": ["( ●    )", "(  ●   )", "(   ●  )", "(    ● )", "(     ●)", "(    ● )", "(   ●  )", "(  ●   )"],
    }

    def __init__(self, label: str = "Loading", style: str = "dots", interval: float = 0.08):
        self.label = label
        self.style = style
        self.interval = interval
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._frame = 0
        self._lock = threading.Lock()
        self._done = False
        self._result = ""

    def _animate(self):
        """Animation loop running in background thread."""
        chars = self.STYLES.get(self.style, self.STYLES["dots"])
        while self._running:
            with self._lock:
                char = chars[self._frame % len(chars)]
                self._frame += 1
            theme = Renderer.theme
            line = (
                f"\r  {ANSI.fg(theme.accent[0], theme.accent[1], theme.accent[2])}"
                f"{char}{ANSI.reset()} {self.label}..."
            )
            sys.stdout.write(line)
            sys.stdout.flush()
            time.sleep(self.interval)

    def start(self):
        """Start the spinner animation."""
        self._running = True
        self._thread = threading.Thread(target=self._animate, daemon=True)
        self._thread.start()
        return self

    def stop(self, message: str = ""):
        """Stop the spinner."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=0.5)
        theme = Renderer.theme
        msg = message or f"{self.label} done"
        self._result = (
            f"\r  {ANSI.fg(theme.success[0], theme.success[1], theme.success[2])}"
            f"✓{ANSI.reset()} {msg}"
        )
        sys.stdout.write(self._result)
        sys.stdout.flush()
        self._done = True

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        if self._running:
            self.stop()


# ─── Layout Engine ──────────────────────────────────────────────────────────

@dataclass
class Panel:
    """A panel in the split layout."""
    x: int
    y: int
    width: int
    height: int
    title: str = ""
    content: List[str] = field(default_factory=list)
    scroll_pos: int = 0
    border: bool = True


class SplitLayout:
    """Manages split-panel terminal layout."""

    def __init__(self, columns: int, rows: int, sidebar_width: int = 30):
        self.columns = columns
        self.rows = rows
        self.sidebar_width = min(sidebar_width, columns // 3)
        self.chat_width = columns - self.sidebar_width - 1
        self._chat_panel = Panel(x=1, y=3, width=self.chat_width, height=rows - 4, title="Chat")
        self._sidebar_panel = Panel(x=self.chat_width + 2, y=3, width=self.sidebar_width, height=rows - 4, title="Info")

    def resize(self, columns: int, rows: int):
        """Update layout dimensions."""
        self.columns = columns
        self.rows = rows
        self.sidebar_width = min(self.sidebar_width, columns // 3)
        self.chat_width = columns - self.sidebar_width - 1
        self._chat_panel.width = self.chat_width
        self._chat_panel.height = rows - 4
        self._sidebar_panel.x = self.chat_width + 2
        self._sidebar_panel.width = self.sidebar_width
        self._sidebar_panel.height = rows - 4

    def render_chat(self, lines: List[str]) -> str:
        """Render the chat panel with content."""
        return self._render_panel(self._chat_panel, lines)

    def render_sidebar(self, lines: List[str]) -> str:
        """Render the sidebar panel with content."""
        return self._render_panel(self._sidebar_panel, lines)

    def _render_panel(self, panel: Panel, lines: List[str]) -> str:
        """Render a single panel with border and content."""
        theme = Renderer.theme
        out: List[str] = []

        if panel.border:
            # Top border with title
            tl = "┌"
            tr = "┐"
            h = "─"
            v = "│"

            title_str = f" {panel.title} " if panel.title else ""
            border_width = panel.width - 2
            h_fill = max(0, border_width - len(title_str))

            top = (
                ANSI.move_to(panel.x, panel.y)
                + ANSI.fg(theme.border[0], theme.border[1], theme.border[2])
                + tl + title_str + h * h_fill + tr
                + ANSI.reset()
            )
            out.append(top)

            # Content lines
            visible_lines = lines[panel.scroll_pos:panel.scroll_pos + panel.height - 2]
            for i in range(panel.height - 2):
                if i < len(visible_lines):
                    line = visible_lines[i]
                else:
                    line = ""
                # Truncate/pad to fit
                display = self._truncate_line(line, panel.width - 2)
                padded = display + " " * max(0, panel.width - 2 - self._display_width(display))
                out.append(
                    ANSI.move_to(panel.x, panel.y + 1 + i)
                    + ANSI.fg(theme.border[0], theme.border[1], theme.border[2]) + v
                    + ANSI.reset()
                    + padded
                    + ANSI.fg(theme.border[0], theme.border[1], theme.border[2]) + v
                    + ANSI.reset()
                )

            # Bottom border
            bottom = (
                ANSI.move_to(panel.x, panel.y + panel.height - 1)
                + ANSI.fg(theme.border[0], theme.border[1], theme.border[2])
                + "└" + h * (panel.width - 2) + "┘"
                + ANSI.reset()
            )
            out.append(bottom)
        else:
            for i, line in enumerate(lines[:panel.height]):
                display = self._truncate_line(line, panel.width)
                out.append(ANSI.move_to(panel.x, panel.y + i) + display)

        return "\n".join(out)

    @staticmethod
    def _truncate_line(line: str, max_width: int) -> str:
        """Truncate line to fit width, handling ANSI codes."""
        if max_width <= 0:
            return ""
        result = []
        visible = 0
        in_ansi = False
        for ch in line:
            if ch == '\033':
                in_ansi = True
                result.append(ch)
            elif in_ansi:
                result.append(ch)
                if ch == 'm':
                    in_ansi = False
            else:
                visible += 1
                if visible > max_width:
                    break
                result.append(ch)
        return "".join(result)

    @staticmethod
    def _display_width(text: str) -> int:
        """Calculate display width excluding ANSI codes."""
        stripped = re.sub(r'\033\[[0-9;]*m', '', text)
        return len(stripped)


# ─── Main Renderer ─────────────────────────────────────────────────────────

class Renderer:
    """Advanced terminal UI renderer for NovaCode.

    Provides a comprehensive rendering engine with split-panel layouts,
    streaming markdown, syntax highlighting, autocomplete, progress bars,
    spinners, color themes, mouse support, and resize handling.
    """

    theme: Theme = THEMES[ThemeName.DARK]
    _terminal: TerminalInfo = TerminalInfo()
    _highlighter: SyntaxHighlighter = SyntaxHighlighter()
    _md_parser: MarkdownParser = MarkdownParser()
    _autocomplete: AutocompleteEngine = AutocompleteEngine()
    _stream_buffer: StreamBuffer = StreamBuffer()
    _layout: Optional[SplitLayout] = None
    _initialized: bool = False
    _resize_callbacks: List[Callable] = []

    @classmethod
    def initialize(cls, theme: ThemeName = ThemeName.DARK, sidebar_width: int = 30):
        """Initialize the renderer with theme and terminal detection."""
        cls.theme = THEMES.get(theme, THEMES[ThemeName.DARK])
        cls._terminal = TerminalInfo()
        cls._terminal.refresh()
        cls._layout = SplitLayout(
            cls._terminal.columns,
            cls._terminal.rows,
            sidebar_width,
        )
        cls._initialized = True

    @classmethod
    def shutdown(cls):
        """Clean up renderer state."""
        sys.stdout.write(ANSI.disable_mouse())
        sys.stdout.write(ANSI.show_cursor())
        sys.stdout.flush()
        cls._initialized = False

    # ── Screen Control ──────────────────────────────────────────────────

    @classmethod
    def clear(cls):
        """Clear the terminal screen."""
        sys.stdout.write(ANSI.clear_screen())
        sys.stdout.flush()

    @classmethod
    def reset_cursor(cls):
        """Move cursor to top-left."""
        sys.stdout.write(ANSI.move_to(1, 1))
        sys.stdout.flush()

    # ── Header / Status Bar ─────────────────────────────────────────────

    @classmethod
    def header(
        cls,
        model: str = "Nova",
        mode: str = "agent",
        tokens: int = 0,
        elapsed: float = 0.0,
    ) -> str:
        """Render the status bar header.

        Args:
            model: Current model name
            mode: Current mode (agent, ask, plan, debug)
            tokens: Total tokens used
            elapsed: Session elapsed time in seconds

        Returns:
            Formatted header string
        """
        theme = cls.theme
        cols = cls._terminal.columns

        mode_colors = {
            "agent": theme.success,
            "ask": theme.accent,
            "plan": theme.warning,
            "debug": theme.error,
        }
        mode_col = mode_colors.get(mode, theme.fg)

        # Build segments
        logo = f"{ANSI.bold()}{ANSI.fg(theme.accent[0], theme.accent[1], theme.accent[2])}NOVACODE{ANSI.reset()}"
        model_seg = f"{ANSI.fg(theme.muted[0], theme.muted[1], theme.muted[2])}│{ANSI.reset()} {ANSI.fg(theme.fg[0], theme.fg[1], theme.fg[2])}{model}{ANSI.reset()}"
        mode_seg = f"{ANSI.fg(theme.muted[0], theme.muted[1], theme.muted[2])}│{ANSI.reset()} {ANSI.fg(mode_col[0], mode_col[1], mode_col[2])}{mode.upper()}{ANSI.reset()}"
        token_seg = f"{ANSI.fg(theme.muted[0], theme.muted[1], theme.muted[2])}│{ANSI.reset()} {ANSI.fg(theme.success[0], theme.success[1], theme.success[2])}tokens:{tokens}{ANSI.reset()}"
        time_seg = f"{ANSI.fg(theme.muted[0], theme.muted[1], theme.muted[2])}│{ANSI.reset()} {ANSI.fg(theme.warning[0], theme.warning[1], theme.warning[2])}{elapsed:.0f}s{ANSI.reset()}"

        segments = [logo, model_seg, mode_seg, token_seg, time_seg]
        content = " ".join(segments)

        # Pad and add background
        padding = " " * max(0, cols - SplitLayout._display_width(content) - 1)

        bar = (
            ANSI.bg(theme.bg[0], theme.bg[1], theme.bg[2])
            + ANSI.fg(theme.fg[0], theme.fg[1], theme.fg[2])
            + content + padding
            + ANSI.reset()
        )

        # Separator line
        sep = (
            ANSI.fg(theme.border[0], theme.border[1], theme.border[2])
            + "─" * cols
            + ANSI.reset()
        )

        return f"{bar}\n{sep}"

    # ── Streaming Output ────────────────────────────────────────────────

    @classmethod
    def stream_chunk(cls, text: str, flush: bool = True):
        """Output a streaming text chunk.

        Args:
            text: Text chunk to output
            flush: Whether to flush stdout immediately
        """
        cls._stream_buffer.append(text)
        sys.stdout.write(text)
        if flush:
            sys.stdout.flush()

    @classmethod
    def stream_start(cls):
        """Begin a streaming session."""
        cls._stream_buffer = StreamBuffer()

    @classmethod
    def stream_end(cls) -> str:
        """End streaming and return full accumulated text."""
        return cls._stream_buffer.raw

    # ── Code Block Rendering ────────────────────────────────────────────

    @classmethod
    def code_block(cls, code: str, language: str = "python") -> str:
        """Render a syntax-highlighted code block.

        Args:
            code: Source code to highlight
            language: Programming language for syntax highlighting

        Returns:
            Formatted code block string with ANSI colors
        """
        theme = cls.theme
        cols = cls._terminal.columns
        max_width = min(cols - 4, 100)

        highlighted = cls._highlighter.highlight(code, language)

        lines = highlighted.split("\n")
        out: List[str] = []

        # Top border with language tag
        lang_tag = f" {language} " if language else " code "
        top = (
            ANSI.fg(theme.border[0], theme.border[1], theme.border[2])
            + "  ┌" + lang_tag
            + "─" * max(0, max_width - len(lang_tag) - 2)
            + "┐"
            + ANSI.reset()
        )
        out.append(top)

        # Code lines
        for line in lines:
            truncated = SplitLayout._truncate_line(line, max_width - 1)
            padding = " " * max(0, max_width - 1 - SplitLayout._display_width(truncated))
            out.append(
                ANSI.fg(theme.border[0], theme.border[1], theme.border[2]) + "  │" + ANSI.reset()
                + truncated + padding
                + ANSI.fg(theme.border[0], theme.border[1], theme.border[2]) + "│" + ANSI.reset()
            )

        # Bottom border
        bottom = (
            ANSI.fg(theme.border[0], theme.border[1], theme.border[2])
            + "  └" + "─" * max_width + "┘"
            + ANSI.reset()
        )
        out.append(bottom)

        return "\n".join(out)

    # ── Markdown Rendering ──────────────────────────────────────────────

    @classmethod
    def markdown(cls, text: str) -> str:
        """Render markdown text with ANSI colors.

        Supports: headings, code blocks, lists, blockquotes,
        tables, horizontal rules, inline formatting.

        Args:
            text: Markdown text to render

        Returns:
            Formatted string with ANSI color codes
        """
        theme = cls.theme
        blocks = cls._md_parser.parse(text)
        out: List[str] = []

        for block in blocks:
            if block.type == "heading":
                prefix = "#" * block.level + " "
                colors = {
                    1: ANSI.fg(theme.accent[0], theme.accent[1], theme.accent[2]),
                    2: ANSI.fg(100, 200, 255),
                    3: ANSI.fg(150, 220, 200),
                }
                col = colors.get(block.level, ANSI.fg(theme.fg[0], theme.fg[1], theme.fg[2]))
                out.append(f"\n{col}{ANSI.bold()}{prefix}{block.content}{ANSI.reset()}\n")

            elif block.type == "code":
                out.append(cls.code_block(block.content, block.language))

            elif block.type == "paragraph":
                rendered = cls._render_inline(block.content)
                out.append(rendered)

            elif block.type == "list":
                for i, item in enumerate(block.items):
                    bullet = f"  {ANSI.fg(theme.accent[0], theme.accent[1], theme.accent[2])}•{ANSI.reset()}"
                    rendered = cls._render_inline(item)
                    out.append(f"{bullet} {rendered}")

            elif block.type == "quote":
                for line in block.content.split("\n"):
                    out.append(
                        f"  {ANSI.fg(theme.muted[0], theme.muted[1], theme.muted[2])}│{ANSI.reset()} "
                        f"{ANSI.italic()}{line}{ANSI.reset()}"
                    )

            elif block.type == "table":
                out.append(cls.table(block.headers, block.rows))

            elif block.type == "hr":
                out.append(
                    ANSI.fg(theme.border[0], theme.border[1], theme.border[2])
                    + "  " + "─" * (cls._terminal.columns - 4)
                    + ANSI.reset()
                )

        return "\n".join(out)

    @classmethod
    def _render_inline(cls, text: str) -> str:
        """Render inline markdown (bold, italic, code, links)."""
        theme = cls.theme
        result: List[str] = []
        pos = 0

        # Combined inline pattern
        pattern = re.compile(
            r'(\*\*\*(.+?)\*\*\*|\*\*(.+?)\*\*|\*(.+?)\*|`(.+?)`|\[(.+?)\]\((.+?)\))'
        )

        for m in pattern.finditer(text):
            # Text before match
            if m.start() > pos:
                result.append(text[pos:m.start()])

            if m.group(2):  # ***bold italic***
                result.append(
                    f"{ANSI.bold()}{ANSI.italic()}{m.group(2)}{ANSI.reset()}"
                )
            elif m.group(3):  # **bold**
                result.append(
                    f"{ANSI.bold()}{m.group(3)}{ANSI.reset()}"
                )
            elif m.group(4):  # *italic*
                result.append(
                    f"{ANSI.italic()}{m.group(4)}{ANSI.reset()}"
                )
            elif m.group(5):  # `code`
                result.append(
                    f"{ANSI.bg(theme.code_bg[0], theme.code_bg[1], theme.code_bg[2])}"
                    f"{ANSI.fg(theme.warning[0], theme.warning[1], theme.warning[2])}"
                    f" {m.group(5)} "
                    f"{ANSI.reset()}"
                )
            elif m.group(6):  # [text](url)
                result.append(
                    f"{ANSI.fg(theme.accent[0], theme.accent[1], theme.accent[2])}"
                    f"{ANSI.underline()}{m.group(6)}{ANSI.reset()}"
                )

            pos = m.end()

        if pos < len(text):
            result.append(text[pos:])

        return "".join(result)

    # ── Table Rendering ─────────────────────────────────────────────────

    @classmethod
    def table(cls, headers: List[str], rows: List[List[str]]) -> str:
        """Render a formatted table.

        Args:
            headers: Column headers
            rows: Table data rows

        Returns:
            Formatted table string
        """
        theme = cls.theme
        cols = cls._terminal.columns

        if not headers:
            return ""

        # Calculate column widths
        num_cols = len(headers)
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row[:num_cols]):
                col_widths[i] = max(col_widths[i], len(cell))

        # Cap total width
        total_width = sum(col_widths) + (num_cols - 1) * 3 + 4
        if total_width > cols:
            scale = (cols - (num_cols - 1) * 3 - 4) / max(sum(col_widths), 1)
            col_widths = [max(3, int(w * scale)) for w in col_widths]

        out: List[str] = []

        # Top border
        top = "  ┌" + "┬".join("─" * (w + 2) for w in col_widths) + "┐"
        out.append(ANSI.fg(theme.border[0], theme.border[1], theme.border[2]) + top + ANSI.reset())

        # Header row
        header_cells = []
        for i, h in enumerate(headers):
            w = col_widths[i] if i < len(col_widths) else len(h)
            header_cells.append(f" {ANSI.bold()}{h:<{w}}{ANSI.reset()} ")
        header_row = "  │" + "│".join(header_cells) + "│"
        out.append(
            ANSI.fg(theme.border[0], theme.border[1], theme.border[2]) + "  │" + ANSI.reset()
            + ANSI.fg(theme.accent[0], theme.accent[1], theme.accent[2])
            + "│".join(header_cells)
            + ANSI.reset()
            + ANSI.fg(theme.border[0], theme.border[1], theme.border[2]) + "│" + ANSI.reset()
        )

        # Separator
        sep = "  ├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤"
        out.append(ANSI.fg(theme.border[0], theme.border[1], theme.border[2]) + sep + ANSI.reset())

        # Data rows
        for row in rows:
            cells = []
            for i in range(num_cols):
                cell = row[i] if i < len(row) else ""
                w = col_widths[i] if i < len(col_widths) else len(cell)
                cells.append(f" {cell:<{w}} ")
            row_str = "  │" + "│".join(cells) + "│"
            out.append(ANSI.fg(theme.border[0], theme.border[1], theme.border[2]) + row_str + ANSI.reset())

        # Bottom border
        bottom = "  └" + "┴".join("─" * (w + 2) for w in col_widths) + "┘"
        out.append(ANSI.fg(theme.border[0], theme.border[1], theme.border[2]) + bottom + ANSI.reset())

        return "\n".join(out)

    # ── Split Panel Layout ──────────────────────────────────────────────

    @classmethod
    def split_layout(
        cls,
        chat_lines: List[str],
        sidebar_lines: List[str],
    ) -> str:
        """Render split-panel layout with chat and sidebar.

        Args:
            chat_lines: Lines for the main chat area
            sidebar_lines: Lines for the sidebar

        Returns:
            Combined layout string
        """
        if cls._layout is None:
            cls.initialize()
        assert cls._layout is not None
        cls._layout.resize(cls._terminal.columns, cls._terminal.rows)
        return cls._layout.render_chat(chat_lines) + "\n" + cls._layout.render_sidebar(sidebar_lines)

    # ── Autocomplete ────────────────────────────────────────────────────

    @classmethod
    def autocomplete(cls, text: str) -> List[CompletionItem]:
        """Get autocomplete suggestions for input text.

        Args:
            text: Current input text

        Returns:
            List of completion items
        """
        return cls._autocomplete.complete(text)

    @classmethod
    def render_completions(cls, items: List[CompletionItem], selected: int = 0) -> str:
        """Render autocomplete dropdown.

        Args:
            items: Completion items to display
            selected: Index of currently selected item

        Returns:
            Formatted completion dropdown string
        """
        theme = cls.theme
        out: List[str] = []

        for i, item in enumerate(items[:8]):
            if i == selected:
                prefix = f"{ANSI.bg(theme.highlight[0], theme.highlight[1], theme.highlight[2])} ▶"
                suffix = ANSI.reset()
            else:
                prefix = "   "
                suffix = ""

            icon = f" {item.icon}" if item.icon else ""
            desc = (
                f" {ANSI.fg(theme.muted[0], theme.muted[1], theme.muted[2])}"
                f"{item.description}{ANSI.reset()}"
            ) if item.description else ""

            out.append(f"{prefix}{icon} {item.display}{desc}{suffix}")

        return "\n".join(out)

    # ── Progress Bar ────────────────────────────────────────────────────

    @classmethod
    def progress_bar(
        cls,
        context: str,
        total: int,
        width: int = 40,
        style: str = "blocks",
    ) -> ProgressBar:
        """Create a progress bar context manager.

        Args:
            context: Label for the progress bar
            total: Total steps
            width: Bar width in characters
            style: Visual style (blocks, arrows, dots, thin)

        Returns:
            ProgressBar instance (use as context manager)
        """
        return ProgressBar(context, total, width, style)

    # ── Spinner ─────────────────────────────────────────────────────────

    @classmethod
    def spinner(cls, label: str = "Loading", style: str = "dots") -> Spinner:
        """Create a spinner context manager.

        Args:
            label: Label text
            style: Animation style (dots, line, pulse, star, bounce)

        Returns:
            Spinner instance (use as context manager)
        """
        return Spinner(label, style)

    # ── Input with History ──────────────────────────────────────────────

    @classmethod
    def prompt_input(
        cls,
        history: Optional[List[str]] = None,
        prompt_text: str = ">",
    ) -> str:
        """Input prompt with history navigation.

        Supports Up/Down arrow keys for history navigation.
        Returns input string when Enter is pressed.

        Args:
            history: List of previous inputs
            prompt_text: Prompt prefix text

        Returns:
            User input string
        """
        theme = cls.theme
        history = history or []
        hist_idx = len(history)

        buf = ""
        cursor_pos = 0

        sys.stdout.write(f"\n{ANSI.bold()}{ANSI.fg(theme.success[0], theme.success[1], theme.success[2])}{prompt_text}>{ANSI.reset()} ")
        sys.stdout.flush()

        # Use raw terminal input for arrow key detection
        import termios
        import tty

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setraw(fd)

            while True:
                ch = sys.stdin.read(1)

                # Enter
                if ch in ("\r", "\n"):
                    sys.stdout.write("\r\n")
                    sys.stdout.flush()
                    return buf

                # Ctrl+C
                if ch == "\x03":
                    raise KeyboardInterrupt

                # Ctrl+D
                if ch == "\x04":
                    raise EOFError

                # Escape sequence (arrow keys)
                if ch == "\x1b":
                    seq = sys.stdin.read(2)
                    if seq == "[A":  # Up
                        if hist_idx > 0:
                            hist_idx -= 1
                            buf = history[hist_idx]
                            cursor_pos = len(buf)
                            cls._redraw_prompt(prompt_text, buf)
                    elif seq == "[B":  # Down
                        if hist_idx < len(history) - 1:
                            hist_idx += 1
                            buf = history[hist_idx]
                            cursor_pos = len(buf)
                            cls._redraw_prompt(prompt_text, buf)
                        elif hist_idx == len(history) - 1:
                            hist_idx = len(history)
                            buf = ""
                            cursor_pos = 0
                            cls._redraw_prompt(prompt_text, buf)
                    elif seq == "[C":  # Right
                        cursor_pos = min(cursor_pos + 1, len(buf))
                    elif seq == "[D":  # Left
                        cursor_pos = max(cursor_pos - 1, 0)
                    continue

                # Backspace
                if ch in ("\x7f", "\b"):
                    if cursor_pos > 0:
                        buf = buf[:cursor_pos - 1] + buf[cursor_pos:]
                        cursor_pos -= 1
                        cls._redraw_prompt(prompt_text, buf, cursor_pos)
                    continue

                # Tab (autocomplete trigger)
                if ch == "\t":
                    completions = cls.autocomplete(buf)
                    if completions:
                        buf = completions[0].text
                        cursor_pos = len(buf)
                        cls._redraw_prompt(prompt_text, buf, cursor_pos)
                    continue

                # Regular character
                if 32 <= ord(ch) < 127:
                    buf = buf[:cursor_pos] + ch + buf[cursor_pos:]
                    cursor_pos += 1
                    cls._redraw_prompt(prompt_text, buf, cursor_pos)

        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    @classmethod
    def _redraw_prompt(cls, prompt_text: str, buf: str, cursor_pos: int = -1):
        """Redraw the prompt line with current buffer."""
        theme = cls.theme
        if cursor_pos < 0:
            cursor_pos = len(buf)

        sys.stdout.write(
            "\r" + ANSI.clear_line()
            + f"{ANSI.bold()}{ANSI.fg(theme.success[0], theme.success[1], theme.success[2])}{prompt_text}>{ANSI.reset()} "
            + buf
        )
        # Position cursor
        sys.stdout.write(f"\r\033[{5 + cursor_pos}C")
        sys.stdout.flush()

    # ── Theme Management ────────────────────────────────────────────────

    @classmethod
    def set_theme(cls, theme_name: ThemeName):
        """Switch color theme.

        Args:
            theme_name: Theme to apply
        """
        if theme_name in THEMES:
            cls.theme = THEMES[theme_name]

    @classmethod
    def get_theme_names(cls) -> List[str]:
        """Get available theme names."""
        return [t.value for t in ThemeName]

    # ── Terminal Resize ─────────────────────────────────────────────────

    @classmethod
    def handle_resize(cls) -> bool:
        """Check for and handle terminal resize.

        Returns:
            True if terminal was resized
        """
        old_cols = cls._terminal.columns
        old_rows = cls._terminal.rows
        cls._terminal.refresh()

        if cls._terminal.columns != old_cols or cls._terminal.rows != old_rows:
            if cls._layout:
                cls._layout.resize(cls._terminal.columns, cls._terminal.rows)
            for cb in cls._resize_callbacks:
                cb(cls._terminal.columns, cls._terminal.rows)
            return True
        return False

    @classmethod
    def on_resize(cls, callback: Callable[[int, int], None]):
        """Register a resize callback.

        Args:
            callback: Function called with (columns, rows) on resize
        """
        cls._resize_callbacks.append(callback)

    # ── Mouse Support ───────────────────────────────────────────────────

    @classmethod
    def enable_mouse(cls) -> str:
        """Enable mouse tracking. Returns ANSI sequence."""
        cls._terminal.supports_mouse = True
        return ANSI.enable_mouse()

    @classmethod
    def disable_mouse(cls) -> str:
        """Disable mouse tracking. Returns ANSI sequence."""
        return ANSI.disable_mouse()

    @classmethod
    def mouse_enabled(cls) -> bool:
        """Check if mouse tracking is enabled."""
        return cls._terminal.supports_mouse

    # ── Utility ─────────────────────────────────────────────────────────

    @classmethod
    def terminal_info(cls) -> TerminalInfo:
        """Get current terminal information."""
        cls._terminal.refresh()
        return cls._terminal

    @classmethod
    def colorize(cls, text: str, r: int, g: int, b: int) -> str:
        """Wrap text in RGB color ANSI codes.

        Args:
            text: Text to colorize
            r, g, b: RGB color values (0-255)

        Returns:
            Colorized text string
        """
        return f"{ANSI.fg(r, g, b)}{text}{ANSI.reset()}"

    @classmethod
    def strip_ansi(cls, text: str) -> str:
        """Remove all ANSI escape sequences from text.

        Args:
            text: Text containing ANSI codes

        Returns:
            Plain text without ANSI codes
        """
        return re.sub(r'\033\[[0-9;]*m', '', text)


# ─── Convenience Exports ────────────────────────────────────────────────────

__all__ = [
    "Renderer",
    "Theme",
    "ThemeName",
    "THEMES",
    "ProgressBar",
    "Spinner",
    "CompletionItem",
    "AutocompleteEngine",
    "SyntaxHighlighter",
    "MarkdownParser",
    "SplitLayout",
    "Panel",
    "TerminalInfo",
    "ANSI",
    "StreamBuffer",
]


# ─── Demo ───────────────────────────────────────────────────────────────────

def _demo():
    """Demonstrate renderer capabilities."""
    Renderer.initialize(ThemeName.DARK)
    Renderer.clear()

    # Header
    print(Renderer.header("Nova Super 120B", "agent", 15420, 127.5))
    print()

    # Markdown rendering
    md_text = """
# NovaCode Renderer Demo

This is a **bold** statement with *italic* and `inline code`.

## Features

- Split panel layouts
- Syntax highlighting
- Progress bars and spinners
- Color themes

```python
def hello(name: str) -> str:
    return f"Hello, {name}!"
```

> This is a blockquote with important information.

| Feature | Status | Priority |
|---------|--------|----------|
| Markdown | Done | High |
| Themes | Done | Medium |
| Mouse | WIP | Low |
"""
    print(Renderer.markdown(md_text))

    # Code block
    print()
    code = '''class Example:
    def __init__(self, value: int):
        self.value = value

    def process(self) -> str:
        # Process the value
        result = self.value * 2
        return f"Result: {result}"'''
    print(Renderer.code_block(code, "python"))

    # Table
    print()
    print(Renderer.table(
        ["Model", "Params", "Speed"],
        [
            ["Nova Super", "120B", "fast"],
            ["Nova Apex", "550B", "medium"],
            ["Nova Jet", "30B", "ultra"],
        ],
    ))

    # Progress bar demo
    print()
    with Renderer.progress_bar("Processing", 100) as pb:
        for _ in range(20):
            pb.update(5)
            time.sleep(0.05)
    print()

    # Spinner demo
    with Renderer.spinner("Analyzing", "dots"):
        time.sleep(1.5)
    print()

    # Autocomplete demo
    print("\nAutocomplete for '/m':")
    completions = Renderer.autocomplete("/m")
    print(Renderer.render_completions(completions, selected=0))

    print(f"\nTerminal: {Renderer.terminal_info()}")
    print(f"Themes: {Renderer.get_theme_names()}")

    Renderer.shutdown()


if __name__ == "__main__":
    _demo()
