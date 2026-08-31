"""NovaCode TUI Message Rendering System.

Renders different message types in the terminal with ANSI colors,
markdown support, code highlighting, and streaming capabilities.
Uses Python standard library only.
"""

import os
import re
import textwrap
import shutil
from typing import Optional


ANSI = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "italic": "\033[3m",
    "underline": "\033[4m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "gray": "\033[90m",
    "bright_red": "\033[91m",
    "bright_green": "\033[92m",
    "bright_yellow": "\033[93m",
    "bright_blue": "\033[94m",
    "bright_magenta": "\033[95m",
    "bright_cyan": "\033[96m",
    "bg_dark": "\033[48;5;235m",
    "bg_darker": "\033[48;5;233m",
}

BOX = {
    "tl": "┌", "tr": "┐", "bl": "└", "br": "┘",
    "h": "─", "v": "│", "lm": "├", "rm": "┤",
    "tm": "┬", "bm": "┴", "cross": "┼",
}

STATUS_SYMBOLS = {
    "pending": "◐",
    "running": "◐",
    "done": "✓",
    "success": "✓",
    "failed": "✗",
    "error": "✗",
}

STATUS_COLORS = {
    "pending": ANSI["yellow"],
    "running": ANSI["yellow"],
    "done": ANSI["green"],
    "success": ANSI["green"],
    "failed": ANSI["red"],
    "error": ANSI["red"],
}


class MessageRenderer:
    """Renders messages for the NovaCode terminal UI."""

    def __init__(self, max_width: Optional[int] = None, padding: int = 2):
        self.padding = padding
        self._max_width = max_width
        self._thinking_visible = False

    @property
    def terminal_width(self) -> int:
        try:
            cols = shutil.get_terminal_size().columns
            return min(cols, self._max_width) if self._max_width else cols
        except OSError:
            return 80

    @property
    def content_width(self) -> int:
        return max(self.terminal_width - (self.padding * 2) - 2, 20)

    def _wrap_text(self, text: str, width: Optional[int] = None) -> str:
        w = width or self.content_width
        lines = []
        for paragraph in text.split("\n"):
            if paragraph.strip() == "":
                lines.append("")
            else:
                wrapped = textwrap.wrap(paragraph, width=w, break_long_words=False, replace_whitespace=False)
                lines.extend(wrapped if wrapped else [""])
        return "\n".join(lines)

    def _pad_line(self, text: str) -> str:
        pad = " " * self.padding
        return f"{pad}{text}"

    def _colorize(self, text: str, *codes: str) -> str:
        return "".join(codes) + text + ANSI["reset"]

    def _make_box(self, lines: list[str], border_color: str = "") -> str:
        w = self.content_width
        top = BOX["tl"] + BOX["h"] * (w + 2) + BOX["tr"]
        bottom = BOX["bl"] + BOX["h"] * (w + 2) + BOX["br"]
        result = [self._colorize(top, border_color)]
        for line in lines:
            visible_len = len(self._strip_ansi(line))
            padding = " " * max(w - visible_len, 0)
            result.append(
                self._colorize(BOX["v"] + " ", border_color)
                + line
                + padding
                + self._colorize(" " + BOX["v"], border_color)
            )
        result.append(self._colorize(bottom, border_color))
        return "\n".join(result)

    def _strip_ansi(self, text: str) -> str:
        return re.sub(r"\033\[[0-9;]*m", "", text)

    def _format_attachments(self, attachments: list[str]) -> str:
        if not attachments:
            return ""
        chips = []
        for att in attachments:
            chip = self._colorize(f" 📎 {att} ", ANSI["bg_dark"], ANSI["cyan"])
            chips.append(chip)
        return "\n" + "\n".join(chips)

    def render_user_message(self, text: str, attachments: Optional[list[str]] = None) -> str:
        """Render a user message with green color and 'You>' prefix."""
        w = self.content_width
        prefix = self._colorize("You> ", ANSI["green"], ANSI["bold"])
        prefix_len = 5

        lines = []
        wrapped = textwrap.wrap(text, width=w - prefix_len, break_long_words=False, replace_whitespace=False)
        if wrapped:
            lines.append(prefix + self._colorize(wrapped[0], ANSI["green"]))
            for line in wrapped[1:]:
                lines.append(" " * prefix_len + self._colorize(line, ANSI["green"]))

        if attachments:
            att_text = self._format_attachments(attachments)
            if att_text:
                lines.append("")
                lines.append(self._colorize("Attached:", ANSI["dim"]))
                for att in attachments:
                    lines.append(self._colorize(f"  📎 {att} ", ANSI["bg_dark"], ANSI["cyan"]))

        return "\n".join(lines)

    def render_assistant_message(self, text: str, stream: bool = False) -> str:
        """Render an assistant message with cyan/magenta color and markdown support."""
        prefix = self._colorize("Nova> ", ANSI["cyan"], ANSI["bold"])
        prefix_len = 6

        rendered = self._render_markdown(text, prefix, prefix_len)

        if stream:
            rendered += self._colorize("▌", ANSI["bright_cyan"])

        return rendered

    def _render_markdown(self, text: str, prefix: str, prefix_len: int) -> str:
        """Render markdown text with headers, bold, italic, lists, and code blocks."""
        lines = text.split("\n")
        result = []
        first_line = True
        in_code_block = False
        code_lines = []
        code_language = ""

        i = 0
        while i < len(lines):
            line = lines[i]

            if line.strip().startswith("```"):
                if not in_code_block:
                    in_code_block = True
                    code_language = line.strip()[3:].strip()
                    code_lines = []
                else:
                    in_code_block = False
                    code_text = "\n".join(code_lines)
                    rendered_code = self.render_code_block(code_text, code_language)
                    for cl in rendered_code.split("\n"):
                        if first_line:
                            result.append(prefix + cl)
                            first_line = False
                        else:
                            result.append(" " * prefix_len + cl)
                i += 1
                continue

            if in_code_block:
                code_lines.append(line)
                i += 1
                continue

            if line.strip() == "":
                result.append("")
                i += 1
                continue

            rendered_line = self._render_inline_markdown(line)

            if first_line:
                result.append(prefix + rendered_line)
                first_line = False
            else:
                result.append(" " * prefix_len + rendered_line)

            i += 1

        return "\n".join(result)

    def _render_inline_markdown(self, text: str) -> str:
        """Render inline markdown elements (bold, italic, inline code)."""
        result = []
        i = 0
        while i < len(text):
            if text[i:i+3] == "***":
                end = text.find("***", i+3)
                if end != -1:
                    inner = text[i+3:end]
                    result.append(self._colorize(inner, ANSI["bold"], ANSI["italic"], ANSI["bright_magenta"]))
                    i = end + 3
                    continue

            if text[i:i+2] == "**":
                end = text.find("**", i+2)
                if end != -1:
                    inner = text[i+2:end]
                    result.append(self._colorize(inner, ANSI["bold"], ANSI["bright_magenta"]))
                    i = end + 2
                    continue

            if text[i:i+2] == "*(" :
                result.append(text[i])
                i += 1
                continue

            if text[i] == "*" and i + 1 < len(text) and text[i+1] != '*':
                end = text.find("*", i+1)
                if end != -1 and end > i+1:
                    inner = text[i+1:end]
                    result.append(self._colorize(inner, ANSI["italic"], ANSI["bright_magenta"]))
                    i = end + 1
                    continue

            if text[i] == "`":
                end = text.find("`", i+1)
                if end != -1:
                    inner = text[i+1:end]
                    result.append(self._colorize(inner, ANSI["bg_dark"], ANSI["bright_green"]))
                    i = end + 1
                    continue

            result.append(text[i])
            i += 1

        return "".join(result)

    def render_system_message(self, text: str, level: str = "info") -> str:
        """Render a system message with dim/gray styling."""
        level = level.lower()
        prefix = "[system] "

        if level == "error":
            color = ANSI["red"]
            prefix = self._colorize("[error] ", ANSI["red"], ANSI["bold"])
        elif level == "warning":
            color = ANSI["yellow"]
            prefix = self._colorize("[warning] ", ANSI["yellow"], ANSI["bold"])
        elif level == "success":
            color = ANSI["green"]
            prefix = self._colorize("[success] ", ANSI["green"], ANSI["bold"])
        else:
            color = ANSI["gray"]
            prefix = self._colorize("[system] ", ANSI["gray"], ANSI["dim"])

        wrapped = self._wrap_text(text)
        lines = []
        first = True
        for line in wrapped.split("\n"):
            if first:
                lines.append(prefix + self._colorize(line, color, ANSI["dim"]))
                first = False
            else:
                lines.append(" " * len(self._strip_ansi(prefix)) + self._colorize(line, color, ANSI["dim"]))

        return "\n".join(lines)

    def render_tool_execution(self, name: str, status: str, output: str = "", duration: Optional[float] = None) -> str:
        """Render tool execution with status, collapsible output, and timing."""
        status_lower = status.lower()
        symbol = STATUS_SYMBOLS.get(status_lower, "?")
        color = STATUS_COLORS.get(status_lower, ANSI["white"])

        duration_str = f" ({duration:.2f}s)" if duration is not None else ""
        header = self._colorize(f"{symbol} {name}{duration_str}", color, ANSI["bold"])

        if status_lower in ("done", "success", "failed", "error") and output:
            output_lines = output.strip().split("\n")
            max_lines = 10
            truncated = len(output_lines) > max_lines
            display_lines = output_lines[:max_lines] if truncated else output_lines

            result_lines = [header]
            result_lines.append(self._colorize(BOX["lm"] + BOX["h"] * (self.content_width) + BOX["rm"], ANSI["dim"]))
            for ol in display_lines:
                wrapped = textwrap.wrap(ol, width=self.content_width - 2, break_long_words=False)
                for wl in wrapped:
                    result_lines.append(self._colorize(BOX["v"], ANSI["dim"]) + " " + self._colorize(wl, ANSI["dim"]) + " " + self._colorize(BOX["v"], ANSI["dim"]))
            if truncated:
                remaining = len(output_lines) - max_lines
                more_text = f" ... ({remaining} more lines) "
                result_lines.append(self._colorize(BOX["v"], ANSI["dim"]) + self._colorize(more_text, ANSI["dim"], ANSI["italic"]) + self._colorize(BOX["v"], ANSI["dim"]))
            result_lines.append(self._colorize(BOX["bl"] + BOX["h"] * (self.content_width) + BOX["br"], ANSI["dim"]))

            return "\n".join(result_lines)
        else:
            return header

    def render_thinking(self, text: str) -> str:
        """Render a collapsible thinking/reasoning block with dim styling."""
        if not self._thinking_visible:
            summary = self._colorize(" ◐ Thinking... (/thinking to expand)", ANSI["dim"], ANSI["italic"])
            return summary

        w = self.content_width
        lines = text.strip().split("\n")
        result = [self._colorize(BOX["tl"] + BOX["h"] * (w) + BOX["tr"], ANSI["dim"])]
        result.append(
            self._colorize(BOX["v"], ANSI["dim"])
            + self._colorize(" Thinking ", ANSI["dim"], ANSI["italic"])
            + self._colorize(" " * (w - 10), ANSI["dim"])
            + self._colorize(BOX["v"], ANSI["dim"])
        )
        result.append(self._colorize(BOX["lm"] + BOX["h"] * (w) + BOX["rm"], ANSI["dim"]))

        for line in lines:
            wrapped = textwrap.wrap(line, width=w - 2, break_long_words=False) or [""]
            for wl in wrapped:
                visible = len(wl)
                pad = " " * max(w - 2 - visible, 0)
                result.append(
                    self._colorize(BOX["v"], ANSI["dim"])
                    + " "
                    + self._colorize(wl, ANSI["dim"], ANSI["italic"])
                    + pad
                    + " "
                    + self._colorize(BOX["v"], ANSI["dim"])
                )

        result.append(self._colorize(BOX["bl"] + BOX["h"] * (w) + BOX["br"], ANSI["dim"]))
        return "\n".join(result)

    def toggle_thinking(self) -> None:
        """Toggle visibility of thinking blocks."""
        self._thinking_visible = not self._thinking_visible

    def render_code_block(self, code: str, language: str = "") -> str:
        """Render a code block with syntax highlighting."""
        w = self.content_width
        lines = code.split("\n")

        header = f" {language} " if language else " code "
        result = [self._colorize(BOX["tl"] + header + BOX["h"] * max(w - len(header), 0) + BOX["tr"], ANSI["dim"])]

        for line in lines:
            highlighted = self._highlight_syntax(line, language)
            visible_len = len(self._strip_ansi(highlighted))
            pad = " " * max(w - visible_len, 0)
            result.append(
                self._colorize(BOX["v"], ANSI["dim"])
                + highlighted
                + self._colorize(pad + BOX["v"], ANSI["dim"])
            )

        result.append(self._colorize(BOX["bl"] + BOX["h"] * w + BOX["br"], ANSI["dim"]))
        return "\n".join(result)

    def _highlight_syntax(self, line: str, language: str) -> str:
        """Apply basic syntax highlighting based on language."""
        if not line:
            return line

        lang = language.lower()

        if lang in ("python", "py"):
            return self._highlight_python(line)
        elif lang in ("javascript", "js", "typescript", "ts"):
            return self._highlight_js(line)
        elif lang in ("bash", "sh", "shell", "zsh"):
            return self._highlight_bash(line)
        elif lang in ("json",):
            return self._highlight_json(line)
        elif lang in ("rust", "rs"):
            return self._highlight_rust(line)
        else:
            return self._highlight_generic(line)

    def _highlight_python(self, line: str) -> str:
        keywords = {"def", "class", "import", "from", "return", "if", "elif", "else", "for", "while", "try", "except", "finally", "with", "as", "yield", "lambda", "pass", "break", "continue", "raise", "and", "or", "not", "in", "is", "None", "True", "False", "async", "await"}
        builtins = {"print", "len", "range", "int", "str", "float", "list", "dict", "set", "tuple", "type", "isinstance", "super", "self"}

        result = []
        i = 0
        in_string = False
        string_char = None

        while i < len(line):
            if in_string:
                end = line.find(string_char, i)
                if end == -1:
                    result.append(self._colorize(line[i:], ANSI["bright_green"]))
                    break
                else:
                    result.append(self._colorize(line[i:end+1], ANSI["bright_green"]))
                    i = end + 1
                    in_string = False
                    continue

            if line[i] in ('"', "'"):
                in_string = True
                string_char = line[i]
                result.append(line[i])
                i += 1
                continue

            if line[i] == "#":
                result.append(self._colorize(line[i:], ANSI["gray"], ANSI["italic"]))
                break

            if line[i].isalpha() or line[i] == "_":
                j = i
                while j < len(line) and (line[j].isalnum() or line[j] == "_"):
                    j += 1
                word = line[i:j]
                if word in keywords:
                    result.append(self._colorize(word, ANSI["bright_magenta"], ANSI["bold"]))
                elif word in builtins:
                    result.append(self._colorize(word, ANSI["bright_cyan"]))
                elif word == "self":
                    result.append(self._colorize(word, ANSI["red"], ANSI["italic"]))
                else:
                    result.append(word)
                i = j
                continue

            if line[i].isdigit():
                j = i
                while j < len(line) and (line[j].isdigit() or line[j] == "."):
                    j += 1
                result.append(self._colorize(line[i:j], ANSI["bright_yellow"]))
                i = j
                continue

            result.append(line[i])
            i += 1

        return "".join(result)

    def _highlight_js(self, line: str) -> str:
        keywords = {"function", "const", "let", "var", "return", "if", "else", "for", "while", "class", "extends", "new", "this", "async", "await", "import", "export", "from", "default", "try", "catch", "finally", "throw", "typeof", "instanceof", "null", "undefined", "true", "false"}
        result = []
        i = 0
        in_string = False
        string_char = None

        while i < len(line):
            if in_string:
                end = line.find(string_char, i)
                if end == -1:
                    result.append(self._colorize(line[i:], ANSI["bright_green"]))
                    break
                else:
                    result.append(self._colorize(line[i:end+1], ANSI["bright_green"]))
                    i = end + 1
                    in_string = False
                    continue

            if line[i] in ('"', "'", "`"):
                in_string = True
                string_char = line[i]
                result.append(line[i])
                i += 1
                continue

            if line[i:i+2] == "//":
                result.append(self._colorize(line[i:], ANSI["gray"], ANSI["italic"]))
                break

            if line[i].isalpha() or line[i] == "_":
                j = i
                while j < len(line) and (line[j].isalnum() or line[j] == "_"):
                    j += 1
                word = line[i:j]
                if word in keywords:
                    result.append(self._colorize(word, ANSI["bright_magenta"], ANSI["bold"]))
                else:
                    result.append(word)
                i = j
                continue

            if line[i].isdigit():
                j = i
                while j < len(line) and (line[j].isdigit() or line[j] == "."):
                    j += 1
                result.append(self._colorize(line[i:j], ANSI["bright_yellow"]))
                i = j
                continue

            result.append(line[i])
            i += 1

        return "".join(result)

    def _highlight_bash(self, line: str) -> str:
        keywords = {"if", "then", "else", "elif", "fi", "for", "while", "do", "done", "case", "esac", "function", "return", "export", "source", "echo", "cd", "ls", "mkdir", "rm", "cp", "mv", "cat", "grep", "find", "sudo"}
        result = []
        i = 0

        if line.strip().startswith("#"):
            return self._colorize(line, ANSI["gray"], ANSI["italic"])

        while i < len(line):
            if line[i] == "$" and i + 1 < len(line):
                j = i + 1
                if j < len(line) and line[j] == "{":
                    while j < len(line) and line[j] != "}":
                        j += 1
                    j += 1
                else:
                    while j < len(line) and (line[j].isalnum() or line[j] == "_"):
                        j += 1
                result.append(self._colorize(line[i:j], ANSI["bright_yellow"]))
                i = j
                continue

            if line[i] == "#":
                result.append(self._colorize(line[i:], ANSI["gray"], ANSI["italic"]))
                break

            if line[i] in ('"', "'"):
                char = line[i]
                j = i + 1
                while j < len(line) and line[j] != char:
                    j += 1
                j += 1
                result.append(self._colorize(line[i:j], ANSI["bright_green"]))
                i = j
                continue

            if line[i].isalpha():
                j = i
                while j < len(line) and (line[j].isalnum() or line[j] == "_"):
                    j += 1
                word = line[i:j]
                if word in keywords:
                    result.append(self._colorize(word, ANSI["bright_magenta"], ANSI["bold"]))
                else:
                    result.append(word)
                i = j
                continue

            result.append(line[i])
            i += 1

        return "".join(result)

    def _highlight_json(self, line: str) -> str:
        result = []
        i = 0
        in_string = False
        is_key = False

        while i < len(line):
            if line[i] == '"' and not in_string:
                in_string = True
                j = i + 1
                while j < len(line) and line[j] != '"':
                    if line[j] == "\\":
                        j += 1
                    j += 1
                j += 1
                word = line[i:j]
                if j < len(line) and line[j:].lstrip().startswith(":"):
                    result.append(self._colorize(word, ANSI["bright_cyan"]))
                    is_key = True
                else:
                    result.append(self._colorize(word, ANSI["bright_green"]))
                    is_key = False
                i = j
                continue

            if line[i].isdigit():
                j = i
                while j < len(line) and (line[j].isdigit() or line[j] == "."):
                    j += 1
                result.append(self._colorize(line[i:j], ANSI["bright_yellow"]))
                i = j
                continue

            if line[i:i+4] == "true":
                result.append(self._colorize("true", ANSI["bright_magenta"]))
                i += 4
                continue
            if line[i:i+5] == "false":
                result.append(self._colorize("false", ANSI["bright_magenta"]))
                i += 5
                continue
            if line[i:i+4] == "null":
                result.append(self._colorize("null", ANSI["gray"]))
                i += 4
                continue

            result.append(line[i])
            i += 1

        return "".join(result)

    def _highlight_rust(self, line: str) -> str:
        keywords = {"fn", "let", "mut", "pub", "struct", "impl", "enum", "match", "if", "else", "for", "while", "loop", "return", "use", "mod", "crate", "self", "Self", "true", "false", "Some", "None", "Ok", "Err", "Vec", "String", "Option", "Result"}
        result = []
        i = 0

        if line.strip().startswith("//"):
            return self._colorize(line, ANSI["gray"], ANSI["italic"])

        while i < len(line):
            if line[i] in ('"', "'"):
                char = line[i]
                j = i + 1
                while j < len(line) and line[j] != char:
                    if line[j] == "\\":
                        j += 1
                    j += 1
                j += 1
                result.append(self._colorize(line[i:j], ANSI["bright_green"]))
                i = j
                continue

            if line[i].isalpha() or line[i] == "_":
                j = i
                while j < len(line) and (line[j].isalnum() or line[j] == "_"):
                    j += 1
                word = line[i:j]
                if word in keywords:
                    result.append(self._colorize(word, ANSI["bright_magenta"], ANSI["bold"]))
                else:
                    result.append(word)
                i = j
                continue

            if line[i].isdigit():
                j = i
                while j < len(line) and (line[j].isdigit() or line[j] == "." or line[j] == "_"):
                    j += 1
                result.append(self._colorize(line[i:j], ANSI["bright_yellow"]))
                i = j
                continue

            result.append(line[i])
            i += 1

        return "".join(result)

    def _highlight_generic(self, line: str) -> str:
        result = []
        i = 0

        while i < len(line):
            if line[i] in ('"', "'"):
                char = line[i]
                j = i + 1
                while j < len(line) and line[j] != char:
                    if line[j] == "\\":
                        j += 1
                    j += 1
                j += 1
                result.append(self._colorize(line[i:j], ANSI["bright_green"]))
                i = j
                continue

            if line[i].isdigit():
                j = i
                while j < len(line) and (line[j].isdigit() or line[j] == "."):
                    j += 1
                result.append(self._colorize(line[i:j], ANSI["bright_yellow"]))
                i = j
                continue

            result.append(line[i])
            i += 1

        return "".join(result)

    def render_message_bubble(self, text: str, role: str = "assistant") -> str:
        """Render a message in a box-drawing bubble."""
        if role == "user":
            border_color = ANSI["green"]
        elif role == "system":
            border_color = ANSI["gray"]
        else:
            border_color = ANSI["cyan"]

        wrapped = self._wrap_text(text)
        lines = wrapped.split("\n")
        return self._make_box(lines, border_color)
