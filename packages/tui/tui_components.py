#!/usr/bin/env python3
"""NovaCode TUI Components — Reusable terminal UI components."""

from __future__ import annotations

import os
import re
import shutil
import sys
import threading
import time
from contextlib import contextmanager
from typing import Callable, Iterator, List, Optional


class C:
    """ANSI color codes."""
    R = "\033[0m"; B = "\033[1m"; D = "\033[2m"
    RED = "\033[91m"; GRN = "\033[92m"; YLW = "\033[93m"
    BLU = "\033[94m"; MAG = "\033[95m"; CYN = "\033[96m"; WHT = "\033[97m"


@contextmanager
def ProgressBar(total: int, label: str = "", width: int = 40) -> Iterator[Callable[[int], None]]:
    """Progress bar context manager. Call update(n) to set progress."""
    state = {"current": 0, "start": time.time()}

    def update(n: int = None, delta: int = 1):
        if n is not None:
            state["current"] = n
        else:
            state["current"] += delta
        pct = min(state["current"] / max(total, 1), 1.0)
        filled = int(width * pct)
        bar = "█" * filled + "░" * (width - filled)
        elapsed = time.time() - state["start"]
        eta = (elapsed / pct - elapsed) if pct > 0 and pct < 1 else 0
        sys.stdout.write(f"\r  {C.CYN}{label}{C.R} [{bar}] {int(pct*100):3d}% {elapsed:.0f}s")
        sys.stdout.flush()
        if state["current"] >= total:
            print()

    try:
        yield update
    finally:
        if state["current"] < total:
            print()


@contextmanager
def Spinner(label: str = "", style: str = "dots") -> Iterator[None]:
    """Animated spinner context manager."""
    styles = {"dots": "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠇", "line": "-\\|/", "pulse": "░▒▓█▓▒░"}
    frames = styles.get(style, styles["dots"])
    running = True

    def _spin():
        i = 0
        while running:
            frame = frames[i % len(frames)]
            sys.stdout.write(f"\r  {C.CYN}{frame}{C.R} {label}")
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1
        sys.stdout.write(f"\r  {' ' * (len(label) + 4)}\r")
        sys.stdout.flush()

    t = threading.Thread(target=_spin, daemon=True)
    t.start()
    try:
        yield
    finally:
        running = False
        t.join(timeout=1)


def render_table(headers: List[str], rows: List[List[str]], title: str = "") -> str:
    """Render a formatted table."""
    if not rows:
        return f"{C.D}(no data){C.R}"
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))
    lines = []
    if title:
        lines.append(f"\n{C.B}{C.CYN} {title}{C.R}")
        lines.append(C.D + "─" * (sum(col_widths) + 3 * (len(headers) - 1) + 4) + C.R)
    header = " │ ".join(C.B + h.ljust(col_widths[i]) + C.R for i, h in enumerate(headers))
    lines.append(f"  {header}")
    lines.append(C.D + " ├" + "─┼─".join("─" * w for w in col_widths) + "┤" + C.R)
    for row in rows:
        line = " │ ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row))
        lines.append(f"  {line}")
    return "\n".join(lines)


def render_markdown(text: str) -> str:
    """Basic markdown rendering with colors."""
    lines = []
    in_code = False
    for line in text.split("\n"):
        if line.startswith("```"):
            in_code = not in_code
            lines.append(C.D + "  " + "─" * 40 + C.R)
            continue
        if in_code:
            lines.append(f"  {C.GRN}{line}{C.R}")
        elif line.startswith("# "):
            lines.append(f"\n{C.B}{C.CYN}{line[2:]}{C.R}")
        elif line.startswith("## "):
            lines.append(f"\n{C.B}{line[3:]}{C.R}")
        elif line.startswith("- ") or line.startswith("* "):
            lines.append(f"  {C.GRN}•{C.R} {line[2:]}")
        else:
            line = re.sub(r'\*\*(.+?)\*\*', f"{C.B}\\1{C.R}", line)
            lines.append(f"  {line}")
    return "\n".join(lines)


def prompt_input(history: List[str] = None) -> str:
    """Input with basic history support."""
    try:
        return input(f"{C.B}{C.GRN}▶>{C.R} ").strip()
    except (EOFError, KeyboardInterrupt):
        return ""


def render_code_block(code: str, language: str = "python") -> str:
    """Render code with basic syntax highlighting."""
    keywords = {
        "python": ["def", "class", "import", "from", "return", "if", "else", "for", "while", "try", "except", "with", "as", "async", "await", "lambda", "yield"],
        "javascript": ["function", "const", "let", "var", "return", "if", "else", "for", "while", "try", "catch", "async", "await", "class", "import", "export"],
    }
    lines = []
    for line in code.split("\n"):
        highlighted = line
        for kw in keywords.get(language, []):
            highlighted = re.sub(rf"\b{kw}\b", f"{C.M}{kw}{C.R}", highlighted)
        highlighted = re.sub(r'(".*?"|\'.*?\')', f"{C.GRN}\\1{C.R}", highlighted)
        highlighted = re.sub(r"(#.*$|//.*$)", f"{C.D}\\1{C.R}", highlighted)
        lines.append(f"  {highlighted}")
    return "\n".join(lines)


def clear_screen():
    """Clear terminal screen."""
    os.system("clear" if os.name != "nt" else "cls")


def get_terminal_size() -> tuple:
    """Get terminal dimensions."""
    return shutil.get_terminal_size()


def enable_mouse():
    """Enable mouse tracking."""
    sys.stdout.write("\033[?1000h\033[?1002h\033[?1015h\033[?1006h")
    sys.stdout.flush()


def disable_mouse():
    """Disable mouse tracking."""
    sys.stdout.write("\033[?1006l\033[?1015l\033[?1002l\033[?1000l")
    sys.stdout.flush()


@contextmanager
def terminal_raw():
    """Context manager for raw terminal mode."""
    import termios
    import tty
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        yield
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


class Window:
    """Resizable terminal window."""

    def __init__(self, title: str = "", width: int = 80, height: int = 24):
        self.title = title
        self.width = width
        self.height = height
        self.content: List[str] = []

    def add_line(self, text: str):
        self.content.append(text)

    def render(self) -> str:
        cols = shutil.get_terminal_size().columns
        lines = []
        # Top border
        title_str = f" {self.title} " if self.title else ""
        border = "─" * ((cols - len(title_str)) // 2)
        lines.append(f"{C.D}┌{border}{title_str}{border}{'─' * (cols - len(border) * 2 - len(title_str) - 2)}┐{C.R}")
        # Content
        for line in self.content[:self.height - 2]:
            padded = line[:cols - 4].ljust(cols - 4)
            lines.append(f"{C.D}│{C.R} {padded} {C.D}│{C.R}")
        # Fill remaining
        for _ in range(self.height - 2 - len(self.content)):
            lines.append(f"{C.D}│{' ' * (cols - 2)}│{C.R}")
        # Bottom border
        lines.append(f"{C.D}└{'─' * (cols - 2)}┘{C.R}")
        return "\n".join(lines)


class Panel:
    """Content panel with scroll and title."""

    def __init__(self, title: str = ""):
        self.title = title
        self.lines: List[str] = []
        self.scroll_pos = 0

    def add(self, text: str):
        self.lines.append(text)

    def clear(self):
        self.lines.clear()
        self.scroll_pos = 0

    def render(self, height: int = 20) -> str:
        cols = shutil.get_terminal_size().columns
        visible = self.lines[self.scroll_pos:self.scroll_pos + height]
        out = []
        if self.title:
            out.append(f"{C.B}{C.CYN}── {self.title} {'─' * (cols - len(self.title) - 5)}{C.R}")
        for line in visible:
            out.append(line[:cols - 2])
        return "\n".join(out)


class Menu:
    """Interactive menu with keyboard navigation."""

    def __init__(self, items: List[tuple]):
        self.items = items  # [(key, label, callback), ...]
        self.selected = 0

    def render(self) -> str:
        lines = []
        for i, (key, label, _) in enumerate(self.items):
            if i == self.selected:
                lines.append(f"  {C.B}{C.GRN}▸ {label}{C.R}")
            else:
                lines.append(f"    {C.D}{label}{C.R}")
        return "\n".join(lines)

    def next(self):
        self.selected = (self.selected + 1) % len(self.items)

    def prev(self):
        self.selected = (self.selected - 1) % len(self.items)

    def select(self):
        if self.items:
            cb = self.items[self.selected][2]
            if cb:
                return cb()
        return None


if __name__ == "__main__":
    # Demo
    print(render_table(
        ["Name", "Status", "Latency"],
        [["Nova Super", "ONLINE", "0.38s"], ["Nova Jet", "ONLINE", "0.12s"]],
        "Model Status"
    ))
    print(render_markdown("# Hello\nThis is **bold** text\n- Item 1\n- Item 2"))
