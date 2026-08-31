"""Advanced input handler for NovaCode TUI.

Provides multi-line input, history navigation, autocomplete with fuzzy matching,
file search, and comprehensive key bindings using Python standard library.
"""

from __future__ import annotations

import os
import sys
import tty
import termios
import re
import json
import glob
import fnmatch
import subprocess
from pathlib import Path
from typing import Optional, Callable, List, Tuple, Dict, Any
from dataclasses import dataclass, field


HISTORY_FILE = os.path.expanduser("~/.local/share/novacode/history.json")
COMMANDS = [
    "/model <name>      - Switch model",
    "/mode <mode>       - Switch mode",
    "/lang <code>       - Change language",
    "/nsfw              - Toggle unrestricted",
    "/plan <text>       - Create plan",
    "/search <pattern>  - Search code",
    "/review [path]     - Code review",
    "/git <cmd>         - Git operations",
    "/memory save/search - Memory",
    "/sessions          - List sessions",
    "/resume <id>       - Resume session",
    "/index             - Index project",
    "/improve           - Auto-improve",
    "/agents <task>     - Multi-agent",
    "/clear             - Clear chat",
    "/help              - Help",
    "/quit              - Exit",
    "/thinking          - Toggle thinking",
    "/editor            - External editor",
    "/export            - Export conversation",
]

FILE_TYPE_ICONS: Dict[str, str] = {
    ".py": "🐍", ".js": "📜", ".ts": "📘", ".tsx": "⚛️", ".jsx": "⚛️",
    ".html": "🌐", ".css": "🎨", ".json": "📋", ".md": "📝", ".txt": "📄",
    ".sh": "⚙️", ".bash": "⚙️", ".zsh": "⚙️", ".yml": "⚙️", ".yaml": "⚙️",
    ".toml": "⚙️", ".cfg": "⚙️", ".ini": "⚙️", ".env": "🔒",
    ".rs": "🦀", ".go": "🐹", ".java": "☕", ".c": "©️", ".cpp": "➕",
    ".h": "📐", ".hpp": "📐", ".rb": "💎", ".php": "🐘", ".sql": "🗃️",
    ".xml": "📰", ".csv": "📊", ".log": "📃", ".lock": "🔒",
    ".gitignore": "👁️", ".dockerfile": "🐳", "docker-compose": "🐳",
    "makefile": "🔨", "dockerfile": "🐳",
}


@dataclass
class Suggestion:
    """A single autocomplete suggestion."""
    text: str
    display: str
    icon: str = ""
    description: str = ""
    score: float = 0.0


@dataclass
class InputState:
    """Current state of the input buffer."""
    lines: List[str] = field(default_factory=lambda: [""])
    cursor_line: int = 0
    cursor_col: int = 0
    history_index: int = -1
    saved_current: str = ""
    autocomplete_active: bool = False
    suggestions: List[Suggestion] = field(default_factory=list)
    suggestion_index: int = -1
    trigger_char: str = ""
    trigger_start: int = 0
    search_query: str = ""
    reverse_search: bool = False
    reverse_search_index: int = -1


class InputHandler:
    """Advanced terminal input handler for NovaCode TUI.

    Supports multi-line input, history navigation, autocomplete with fuzzy
    file search, command completion, and comprehensive key bindings.

    Usage:
        handler = InputHandler()
        result = handler.read_input()
    """

    def __init__(
        self,
        history_file: Optional[str] = None,
        max_history: int = 1000,
        max_height_ratio: float = 0.4,
        on_command: Optional[Callable[[str], Optional[str]]] = None,
        file_filter: Optional[Callable[[str], bool]] = None,
    ):
        self.history_file = history_file or HISTORY_FILE
        self.max_history = max_history
        self.max_height_ratio = max_height_ratio
        self.on_command = on_command
        self.file_filter = file_filter or (lambda _: True)
        self.history: List[str] = []
        self.filtered_files: List[str] = []
        self._load_history()
        self._refresh_files()

    def _load_history(self) -> None:
        """Load input history from disk."""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.history = data[-self.max_history:]
        except (json.JSONDecodeError, OSError):
            self.history = []

    def _save_history(self) -> None:
        """Persist input history to disk."""
        try:
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history[-self.max_history:], f, ensure_ascii=False)
        except OSError:
            pass

    def _add_to_history(self, text: str) -> None:
        """Add a non-empty entry to history, avoiding duplicates."""
        text = text.strip()
        if not text:
            return
        if self.history and self.history[-1] == text:
            return
        self.history.append(text)
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
        self._save_history()

    def _refresh_files(self) -> None:
        """Refresh the cached file list for fuzzy search."""
        files: List[str] = []
        cwd = os.getcwd()
        try:
            for entry in Path(cwd).rglob("*"):
                if entry.is_file():
                    rel = os.path.relpath(str(entry), cwd)
                    if self.file_filter(rel):
                        files.append(rel)
        except OSError:
            pass
        self.filtered_files = sorted(files)

    def _get_terminal_size(self) -> Tuple[int, int]:
        """Get terminal dimensions."""
        try:
            return os.get_terminal_size()
        except OSError:
            return (80, 24)

    def _max_height(self) -> int:
        """Calculate maximum input height based on terminal size."""
        _, rows = self._get_terminal_size()
        return max(3, int(rows * self.max_height_ratio))

    def _visible_height(self, state: InputState) -> int:
        """Calculate visible height needed for current content."""
        _, term_cols = self._get_terminal_size()
        max_h = self._max_height()
        height = 0
        for line in state.lines:
            line_len = len(line) + 2
            height += max(1, (line_len + term_cols - 1) // term_cols)
        return min(max_h, max(1, height))

    def _get_file_icon(self, filepath: str) -> str:
        """Get icon for a file based on its extension or name."""
        basename = os.path.basename(filepath).lower()
        if basename in FILE_TYPE_ICONS:
            return FILE_TYPE_ICONS[basename]
        ext = os.path.suffix(filepath).lower()
        return FILE_TYPE_ICONS.get(ext, "📄")

    def _fuzzy_score(self, query: str, target: str) -> float:
        """Calculate fuzzy match score. Higher is better. 0 = no match."""
        if not query:
            return 1.0
        query_lower = query.lower()
        target_lower = target.lower()

        if target_lower == query_lower:
            return 100.0
        if target_lower.startswith(query_lower):
            return 80.0 - len(target) * 0.01
        if query_lower in target_lower:
            return 60.0 - (target_lower.index(query_lower) * 0.1)

        score = 0.0
        qi = 0
        consecutive = 0
        for ti, ch in enumerate(target_lower):
            if qi < len(query_lower) and ch == query_lower[qi]:
                score += 1.0 + consecutive * 0.5
                consecutive += 1
                qi += 1
            else:
                consecutive = 0
            if qi >= len(query_lower):
                break

        if qi >= len(query_lower):
            score -= len(target) * 0.01
            return max(score, 1.0)
        return 0.0

    def _get_command_suggestions(self, query: str) -> List[Suggestion]:
        """Get command autocomplete suggestions."""
        if not query.startswith("/"):
            return []
        cmd_part = query[1:].strip()
        suggestions = []
        for cmd in COMMAND_NAMES:
            score = self._fuzzy_score(cmd_part, cmd)
            if score > 0:
                desc = COMMAND_DESCRIPTIONS.get(cmd, "")
                suggestions.append(Suggestion(
                    text=f"/{cmd}",
                    display=f"/{cmd}",
                    icon="⚡",
                    description=desc,
                    score=score,
                ))
        suggestions.sort(key=lambda s: -s.score)
        return suggestions

    def _get_file_suggestions(self, query: str) -> List[Suggestion]:
        """Get fuzzy file search suggestions."""
        suggestions = []
        for filepath in self.filtered_files:
            score = self._fuzzy_score(query, filepath)
            if score > 0:
                icon = self._get_file_icon(filepath)
                suggestions.append(Suggestion(
                    text=f"{filepath} ",
                    display=filepath,
                    icon=icon,
                    score=score,
                ))
        suggestions.sort(key=lambda s: -s.score)
        return suggestions[:20]

    def _get_line_range_suggestions(self, query: str) -> List[Suggestion]:
        """Get line range suggestions for # trigger."""
        suggestions = []
        for i in range(5):
            start = (i + 1) * 10
            end = start + 10
            suggestions.append(Suggestion(
                text=f"#{start}-{end}",
                display=f"#{start}-{end}",
                icon="📏",
                description=f"Lines {start}-{end}",
                score=float(5 - i),
            ))
        return suggestions

    def _update_autocomplete(self, state: InputState) -> None:
        """Update autocomplete suggestions based on current input."""
        line = state.lines[state.cursor_line]
        cursor = state.cursor_col

        if state.trigger_char:
            trigger_end = cursor
            query = line[state.trigger_start + 1:trigger_end]

            if state.trigger_char == "/":
                state.suggestions = self._get_command_suggestions("/" + query)
            elif state.trigger_char == "@":
                if "#" in query:
                    file_part, range_part = query.split("#", 1)
                    state.suggestions = self._get_line_range_suggestions(range_part)
                else:
                    state.suggestions = self._get_file_suggestions(query)
            elif state.trigger_char == "#":
                state.suggestions = self._get_line_range_suggestions(query)

            state.suggestion_index = 0 if state.suggestions else -1
            state.autocomplete_active = bool(state.suggestions)
            return

        for i in range(cursor - 1, -1, -1):
            ch = line[i]
            if ch == "@" and (i == 0 or line[i - 1] == " "):
                state.trigger_char = "@"
                state.trigger_start = i
                query = line[i + 1:cursor]
                if "#" in query:
                    state.suggestions = self._get_line_range_suggestions("")
                else:
                    state.suggestions = self._get_file_suggestions(query)
                state.suggestion_index = 0 if state.suggestions else -1
                state.autocomplete_active = bool(state.suggestions)
                return
            elif ch == "/" and i == 0:
                state.trigger_char = "/"
                state.trigger_start = i
                query = line[i + 1:cursor]
                state.suggestions = self._get_command_suggestions("/" + query)
                state.suggestion_index = 0 if state.suggestions else -1
                state.autocomplete_active = bool(state.suggestions)
                return
            elif ch == "#" and i > 0 and line[i - 1] != " ":
                state.trigger_char = "#"
                state.trigger_start = i
                query = line[i + 1:cursor]
                state.suggestions = self._get_line_range_suggestions(query)
                state.suggestion_index = 0 if state.suggestions else -1
                state.autocomplete_active = bool(state.suggestions)
                return
            elif ch == " ":
                break

        state.autocomplete_active = False
        state.suggestions = []
        state.suggestion_index = -1
        state.trigger_char = ""

    def _accept_suggestion(self, state: InputState) -> None:
        """Accept the current autocomplete suggestion."""
        if not state.autocomplete_active or state.suggestion_index < 0:
            return
        suggestion = state.suggestions[state.suggestion_index]
        line = state.lines[state.cursor_line]
        new_line = line[:state.trigger_start] + suggestion.text + line[state.cursor_col:]
        state.lines[state.cursor_line] = new_line
        state.cursor_col = state.trigger_start + len(suggestion.text)
        state.autocomplete_active = False
        state.suggestions = []
        state.suggestion_index = -1
        state.trigger_char = ""

    def _navigate_history(self, state: InputState, direction: int) -> None:
        """Navigate through input history. direction=-1 for up, 1 for down."""
        if not self.history:
            return
        if state.history_index == -1:
            state.saved_current = "\n".join(state.lines)
            state.history_index = len(self.history) - 1
            entry = self.history[state.history_index]
            state.lines = entry.split("\n")
            state.cursor_line = len(state.lines) - 1
            state.cursor_col = len(state.lines[-1])
        else:
            new_index = state.history_index + direction
            if new_index < 0:
                return
            if new_index >= len(self.history):
                state.history_index = -1
                state.lines = state.saved_current.split("\n") if state.saved_current else [""]
                state.cursor_line = len(state.lines) - 1
                state.cursor_col = len(state.lines[-1])
                state.saved_current = ""
                return
            state.history_index = new_index
            entry = self.history[state.history_index]
            state.lines = entry.split("\n")
            state.cursor_line = len(state.lines) - 1
            state.cursor_col = len(state.lines[-1])

    def _reverse_search(self, state: InputState) -> None:
        """Perform reverse incremental search through history."""
        if not self.history:
            return
        state.reverse_search = True
        state.reverse_search_index = -1
        state.search_query = ""

        for i in range(len(self.history) - 1, -1, -1):
            if state.search_query in self.history[i]:
                state.reverse_search_index = i
                entry = self.history[i]
                state.lines = entry.split("\n")
                state.cursor_line = len(state.lines) - 1
                state.cursor_col = len(state.lines[-1])
                return

    def _reverse_search_next(self, state: InputState) -> None:
        """Find next match in reverse search."""
        if not state.reverse_search or not state.search_query:
            return
        start = state.reverse_search_index - 1 if state.reverse_search_index >= 0 else len(self.history) - 1
        for i in range(start, -1, -1):
            if state.search_query in self.history[i]:
                state.reverse_search_index = i
                entry = self.history[i]
                state.lines = entry.split("\n")
                state.cursor_line = len(state.lines) - 1
                state.cursor_col = len(state.lines[-1])
                return

    def _render(self, state: InputState, fd) -> None:
        """Render the input area to the terminal."""
        term_cols, _ = self._get_terminal_size()
        max_h = self._max_height()
        lines: List[str] = []

        lines.append("┌─ " + "─" * (term_cols - 4))

        for line_content in state.lines[:max_h - 2]:
            if len(line_content) > term_cols - 2:
                lines.append("│ " + line_content[:term_cols - 3] + "…")
            else:
                lines.append("│ " + line_content)

        while len(lines) < max_h - 1:
            lines.append("│")

        if state.autocomplete_active and state.suggestions:
            lines.append("├─ Suggestions " + "─" * (term_cols - 16))
            visible_suggestions = state.suggestions[:5]
            for idx, sug in enumerate(visible_suggestions):
                prefix = "▸ " if idx == state.suggestion_index else "  "
                entry = f"{prefix}{sug.icon} {sug.display}"
                if sug.description:
                    entry += f" — {sug.description}"
                if len(entry) > term_cols - 2:
                    entry = entry[:term_cols - 4] + "…"
                lines.append("│ " + entry)

        if state.reverse_search:
            query_display = state.search_query or "..."
            lines.append("└─ (reverse-i-search)`{0}': ".format(query_display))
        else:
            lines.append("└" + "─" * (term_cols - 1))

        output = "\r\n".join(lines[:max_h]) + "\r\n"
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.write(output)

        render_line = state.cursor_line
        render_col = state.cursor_col + 2
        sys.stdout.write(f"\033[{render_line + 1};{render_col + 1}H")
        sys.stdout.flush()

    def _read_key(self, fd) -> str:
        """Read a single keypress from stdin in raw mode."""
        ch = os.read(fd, 1)
        if not ch:
            return ""
        if ch == b"\x1b":
            seq = os.read(fd, 1)
            if seq == b"[":
                seq2 = os.read(fd, 1)
                if seq2 == b"A":
                    return "UP"
                elif seq2 == b"B":
                    return "DOWN"
                elif seq2 == b"C":
                    return "RIGHT"
                elif seq2 == b"D":
                    return "LEFT"
                elif seq2 == b"H":
                    return "HOME"
                elif seq2 == b"F":
                    return "END"
                elif seq2 in (b"3",):
                    seq3 = os.read(fd, 1)
                    if seq3 == b"~":
                        return "DELETE"
            elif seq == b"O":
                seq2 = os.read(fd, 1)
                if seq2 == b"H":
                    return "HOME"
                elif seq2 == b"F":
                    return "END"
            return "ESC"
        elif ch == b"\x7f" or ch == b"\x08":
            return "BACKSPACE"
        elif ch == b"\t":
            return "TAB"
        elif ch == b"\r" or ch == b"\n":
            return "ENTER"
        elif ch == b"\x01":
            return "CTRL_A"
        elif ch == b"\x03":
            return "CTRL_C"
        elif ch == b"\x04":
            return "CTRL_D"
        elif ch == b"\x05":
            return "CTRL_E"
        elif ch == b"\x0b":
            return "CTRL_K"
        elif ch == b"\x0e":
            return "CTRL_N"
        elif ch == b"\x12":
            return "CTRL_R"
        elif ch == b"\x15":
            return "CTRL_U"
        elif ch == b"\x17":
            return "CTRL_W"
        elif ch == b"\x18":
            return "CTRL_X"
        elif ch == b"\x1a":
            return "CTRL_Z"
        elif ch == b"\x10":
            return "CTRL_P"
        elif ch == b"\x00":
            return "CTRL_SPACE"
        elif ch == b"\x1b":
            return "ESC"
        else:
            try:
                return ch.decode("utf-8")
            except UnicodeDecodeError:
                return ""

    def read_input(self, prompt: str = "") -> Optional[str]:
        """Read input from the user with full editing capabilities.

        Returns the entered text, or None if cancelled (Ctrl+C) or empty.
        Returns "EXIT" signal on Ctrl+D.
        """
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setraw(fd)
            state = InputState()
            self._render(state, fd)

            while True:
                key = self._read_key(fd)
                if not key:
                    continue

                if key == "CTRL_C":
                    return None

                elif key == "CTRL_D":
                    if not any(line.strip() for line in state.lines):
                        return "EXIT"
                    else:
                        continue

                elif key == "CTRL_R":
                    if state.reverse_search:
                        self._reverse_search_next(state)
                    else:
                        self._reverse_search(state)
                    self._render(state, fd)
                    continue

                elif key == "ESC":
                    if state.reverse_search:
                        state.reverse_search = False
                        state.lines = [""]
                        state.cursor_line = 0
                        state.cursor_col = 0
                    state.autocomplete_active = False
                    state.suggestions = []
                    state.suggestion_index = -1
                    state.trigger_char = ""
                    self._render(state, fd)
                    continue

                elif state.reverse_search:
                    if key == "BACKSPACE":
                        if state.search_query:
                            state.search_query = state.search_query[:-1]
                            self._reverse_search(state)
                    elif key == "ENTER":
                        state.reverse_search = False
                        self._render(state, fd)
                        continue
                    elif len(key) == 1 and key.isprintable():
                        state.search_query += key
                        self._reverse_search(state)
                    self._render(state, fd)
                    continue

                elif key == "ENTER":
                    if state.autocomplete_active:
                        self._accept_suggestion(state)
                    else:
                        full_text = "\n".join(state.lines).strip()
                        if full_text:
                            self._add_to_history(full_text)
                            return full_text
                        return None

                elif key == "TAB":
                    if state.autocomplete_active:
                        self._accept_suggestion(state)
                    elif state.cursor_col > 0:
                        line = state.lines[state.cursor_line]
                        state.lines[state.cursor_line] = line[:state.cursor_col] + "    " + line[state.cursor_col:]
                        state.cursor_col += 4
                    self._render(state, fd)
                    continue

                elif key == "UP":
                    if state.autocomplete_active and state.suggestions:
                        state.suggestion_index = max(0, state.suggestion_index - 1)
                    else:
                        self._navigate_history(state, -1)
                        state.autocomplete_active = False
                        state.suggestions = []
                        state.trigger_char = ""
                    self._render(state, fd)
                    continue

                elif key == "DOWN":
                    if state.autocomplete_active and state.suggestions:
                        state.suggestion_index = min(len(state.suggestions) - 1, state.suggestion_index + 1)
                    else:
                        self._navigate_history(state, 1)
                        state.autocomplete_active = False
                        state.suggestions = []
                        state.trigger_char = ""
                    self._render(state, fd)
                    continue

                elif key == "LEFT":
                    if state.cursor_col > 0:
                        state.cursor_col -= 1
                    elif state.cursor_line > 0:
                        state.cursor_line -= 1
                        state.cursor_col = len(state.lines[state.cursor_line])
                    self._update_autocomplete(state)
                    self._render(state, fd)
                    continue

                elif key == "RIGHT":
                    if state.cursor_col < len(state.lines[state.cursor_line]):
                        state.cursor_col += 1
                    elif state.cursor_line < len(state.lines) - 1:
                        state.cursor_line += 1
                        state.cursor_col = 0
                    self._update_autocomplete(state)
                    self._render(state, fd)
                    continue

                elif key == "HOME" or key == "CTRL_A":
                    state.cursor_col = 0
                    self._render(state, fd)
                    continue

                elif key == "END" or key == "CTRL_E":
                    state.cursor_col = len(state.lines[state.cursor_line])
                    self._render(state, fd)
                    continue

                elif key == "BACKSPACE":
                    if state.cursor_col > 0:
                        line = state.lines[state.cursor_line]
                        state.lines[state.cursor_line] = line[:state.cursor_col - 1] + line[state.cursor_col:]
                        state.cursor_col -= 1
                    elif state.cursor_line > 0:
                        prev_len = len(state.lines[state.cursor_line - 1])
                        state.lines[state.cursor_line - 1] += state.lines[state.cursor_line]
                        del state.lines[state.cursor_line]
                        state.cursor_line -= 1
                        state.cursor_col = prev_len
                    self._update_autocomplete(state)
                    self._render(state, fd)
                    continue

                elif key == "DELETE":
                    if state.cursor_col < len(state.lines[state.cursor_line]):
                        line = state.lines[state.cursor_line]
                        state.lines[state.cursor_line] = line[:state.cursor_col] + line[state.cursor_col + 1:]
                    elif state.cursor_line < len(state.lines) - 1:
                        state.lines[state.cursor_line] += state.lines[state.cursor_line + 1]
                        del state.lines[state.cursor_line + 1]
                    self._update_autocomplete(state)
                    self._render(state, fd)
                    continue

                elif key == "CTRL_K":
                    state.lines[state.cursor_line] = state.lines[state.cursor_line][:state.cursor_col]
                    self._render(state, fd)
                    continue

                elif key == "CTRL_U":
                    state.lines[state.cursor_line] = state.lines[state.cursor_line][state.cursor_col:]
                    state.cursor_col = 0
                    self._render(state, fd)
                    continue

                elif key == "CTRL_W":
                    line = state.lines[state.cursor_line]
                    before = line[:state.cursor_col]
                    after = line[state.cursor_col:]
                    match = re.search(r"(\S+\s*)$", before)
                    if match:
                        state.lines[state.cursor_line] = before[:match.start()] + after
                        state.cursor_col = match.start()
                    else:
                        state.lines[state.cursor_line] = after
                        state.cursor_col = 0
                    self._update_autocomplete(state)
                    self._render(state, fd)
                    continue

                elif key == "CTRL_N":
                    if state.cursor_line < len(state.lines) - 1:
                        state.cursor_line += 1
                        state.cursor_col = min(state.cursor_col, len(state.lines[state.cursor_line]))
                    self._render(state, fd)
                    continue

                elif key == "CTRL_P":
                    if state.cursor_line > 0:
                        state.cursor_line -= 1
                        state.cursor_col = min(state.cursor_col, len(state.lines[state.cursor_line]))
                    self._render(state, fd)
                    continue

                elif len(key) == 1 and key.isprintable():
                    line = state.lines[state.cursor_line]
                    state.lines[state.cursor_line] = line[:state.cursor_col] + key + line[state.cursor_col:]
                    state.cursor_col += 1
                    self._update_autocomplete(state)
                    self._render(state, fd)
                    continue

        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            sys.stdout.write("\r\n")
            sys.stdout.flush()


COMMAND_NAMES = [
    "model", "mode", "lang", "nsfw", "plan", "search", "review",
    "git", "memory", "sessions", "resume", "index", "improve",
    "agents", "clear", "help", "quit", "thinking", "editor", "export",
]

COMMAND_DESCRIPTIONS: Dict[str, str] = {
    "model": "Switch model",
    "mode": "Switch mode",
    "lang": "Change language",
    "nsfw": "Toggle unrestricted",
    "plan": "Create plan",
    "search": "Search code",
    "review": "Code review",
    "git": "Git operations",
    "memory": "Memory",
    "sessions": "List sessions",
    "resume": "Resume session",
    "index": "Index project",
    "improve": "Auto-improve",
    "agents": "Multi-agent",
    "clear": "Clear chat",
    "help": "Help",
    "quit": "Exit",
    "thinking": "Toggle thinking",
    "editor": "External editor",
    "export": "Export conversation",
}


if __name__ == "__main__":
    handler = InputHandler()
    print("NovaCode Input Handler - Press Ctrl+D to exit, Ctrl+C to cancel")
    print("Triggers: @file /command #range | History: Up/Down, Ctrl+R")
    print("─" * 50)
    while True:
        result = handler.read_input()
        if result == "EXIT" or result is None:
            break
        print(f"\n[Submitted]: {result}\n")
