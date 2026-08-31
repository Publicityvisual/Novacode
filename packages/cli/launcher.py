"""
NovaCode CLI Launcher Bridge
Handles routing between native high-performance NovaCode engine and extended Python modules.
"""
import os
import sys
import shutil
import subprocess

NATIVE_BINARY_PATHS = [
    os.path.expanduser("~/.opencode/bin/opencode"),
    os.path.expanduser("~/.local/bin/novacode-core"),
    os.path.expanduser("~/.local/bin/novacode"),
    shutil.which("novacode") or ""
]

def find_native_engine() -> str:
    for path in NATIVE_BINARY_PATHS:
        if path and os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    return ""

def launch_native_tui(args=None) -> int:
    """Launch the modern NovaCode TUI engine directly."""
    engine = find_native_engine()
    if not engine:
        print("\033[31m[NovaCode Error] Native NovaCode engine not found\033[0m", file=sys.stderr)
        return 1

    cmd_args = [engine] + (args or [])
    env = os.environ.copy()
    env["NOVACODE_APP_NAME"] = "Novacode"
    env["OPENCODE_APP_NAME"] = "Novacode"
    env["NOVACODE_CLIENT"] = "novacode"
    env["OPENCODE_CLIENT"] = "novacode"
    env["COLORTERM"] = env.get("COLORTERM", "truecolor")
    env["FORCE_COLOR"] = "1"

    try:
        return subprocess.call(cmd_args, env=env)
    except KeyboardInterrupt:
        return 130
    except Exception as e:
        print(f"\033[31m[NovaCode Error] Failed to launch TUI: {e}\033[0m", file=sys.stderr)
        return 1
