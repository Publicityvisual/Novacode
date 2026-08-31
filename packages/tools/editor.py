#!/usr/bin/env python3
"""
Novacode Terminal Code Editor
Full-screen terminal code editor with syntax highlighting, file browser, and command bar.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import List, Optional

try:
    from prompt_toolkit import Application
    from prompt_toolkit.buffer import Buffer
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.layout.containers import HSplit, VSplit, Window
    from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
    from prompt_toolkit.layout.layout import Layout
    from prompt_toolkit.lexers import PygmentsLexer
    from prompt_toolkit.styles import Style
    from prompt_toolkit.widgets import Frame
    from pygments.lexers import get_lexer_for_filename
    from pygments.util import ClassNotFound
    HAS_PROMPT_TOOLKIT = True
except ImportError:
    HAS_PROMPT_TOOLKIT = False


class NovacodeEditor:
    def __init__(self, initial_path: Optional[str] = None):
        self.initial_path = Path(initial_path).resolve() if initial_path else Path.cwd()
        self.current_file = self.initial_path if self.initial_path.is_file() else None
        self.root_dir = self.initial_path.parent if self.initial_path.is_file() else self.initial_path
        self.status_message = "⚡ Novacode Editor | Ctrl+S: Save | Ctrl+Q: Quit | Ctrl+O: Toggle Sidebar"
        self.show_sidebar = True

    def run(self):
        if not HAS_PROMPT_TOOLKIT:
            print("prompt_toolkit is required for Novacode Editor. Falling back to $EDITOR or nano...")
            target = str(self.current_file or self.root_dir)
            editor = os.environ.get("EDITOR", "nano")
            os.system(f"{editor} '{target}'")
            return 0

        content = ""
        if self.current_file and self.current_file.exists():
            try:
                content = self.current_file.read_text(encoding="utf-8", errors="replace")
            except Exception as e:
                self.status_message = f"Error leyendo archivo: {e}"

        main_buffer = Buffer(name="editor_buffer")
        main_buffer.text = content

        try:
            if self.current_file:
                lexer = PygmentsLexer(get_lexer_for_filename(self.current_file.name).__class__)
            else:
                lexer = None
        except ClassNotFound:
            lexer = None

        editor_window = Window(
            content=BufferControl(buffer=main_buffer, lexer=lexer),
            wrap_lines=True,
        )

        def get_sidebar_text():
            if not self.show_sidebar:
                return []
            lines = [("class:sidebar-header", f" 📁 {self.root_dir.name}\n")]
            try:
                entries = sorted(self.root_dir.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
                for entry in entries[:30]:
                    if entry.name.startswith((".", "__pycache__", "node_modules")):
                        continue
                    if entry.is_dir():
                        lines.append(("class:sidebar-dir", f"  📁 {entry.name}/\n"))
                    else:
                        is_active = self.current_file and entry == self.current_file
                        prefix = "  ▸ " if is_active else "    "
                        style = "class:sidebar-active" if is_active else "class:sidebar-file"
                        lines.append((style, f"{prefix}{entry.name}\n"))
            except Exception:
                pass
            return lines

        sidebar_window = Window(
            content=FormattedTextControl(get_sidebar_text),
            width=26,
        )

        def get_status_bar():
            fname = self.current_file.name if self.current_file else "[No Name]"
            return [
                ("class:status-bar", f" ⚡ NOVACODE │ {fname} │ {self.status_message} ")
            ]

        status_window = Window(
            content=FormattedTextControl(get_status_bar),
            height=1,
        )

        main_split = VSplit([
            sidebar_window,
            editor_window,
        ])

        root_container = HSplit([
            main_split,
            status_window,
        ])

        layout = Layout(root_container, focused_element=editor_window)
        kb = KeyBindings()

        @kb.add("c-q")
        def exit_(event):
            event.app.exit()

        @kb.add("c-s")
        def save_(event):
            if self.current_file:
                try:
                    self.current_file.write_text(main_buffer.text, encoding="utf-8")
                    self.status_message = f"✓ Saved to {self.current_file.name} ({len(main_buffer.text)} bytes)"
                except Exception as e:
                    self.status_message = f"✗ Error saving: {e}"
            else:
                self.status_message = "No hay archivo activo para guardar."

        @kb.add("c-o")
        def toggle_sidebar_(event):
            self.show_sidebar = not self.show_sidebar

        style = Style.from_dict({
            "status-bar": "bg:#161b22 #00ebff bold",
            "sidebar-header": "#00ebff bold",
            "sidebar-dir": "#10b981",
            "sidebar-file": "#8b949e",
            "sidebar-active": "#fa32c8 bold",
        })

        app = Application(
            layout=layout,
            key_bindings=kb,
            style=style,
            full_screen=True,
            mouse_support=True,
        )
        app.run()
        return 0


def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg in ("--help", "-h"):
            print("Novacode Terminal Code Editor")
            print("Uso: novacode editor [archivo_o_directorio]")
            print("")
            print("Atajos de teclado:")
            print("  Ctrl+S: Guardar archivo")
            print("  Ctrl+Q: Salir")
            print("  Ctrl+O: Alternar barra lateral")
            return 0
        if arg in ("--version", "-v"):
            print("Novacode Editor v1.0.0")
            return 0
    target = sys.argv[1] if len(sys.argv) > 1 else None
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print("Novacode Editor requiere una terminal interactiva TTY.")
        return 0
    editor = NovacodeEditor(target)
    return editor.run()

if __name__ == "__main__":
    sys.exit(main())
