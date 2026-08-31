"""
NovaCode CLI Unified Main Entrypoint
"""
import sys
import os

from packages.cli.launcher import launch_native_tui, find_native_engine

# NovaCode standard native subcommands handled directly by the high-speed engine
NOVACODE_NATIVE_COMMANDS = {
    "completion", "acp", "mcp", "attach", "run", "debug", "providers",
    "auth", "agent", "upgrade", "uninstall", "serve", "web", "models",
    "stats", "export", "import", "github", "pr", "session", "plugin",
    "plug", "db"
}

def main(args=None):
    if args is None:
        args = sys.argv[1:]

    if not args:
        # Default: Launch native high-performance TUI
        return launch_native_tui([])

    cmd = args[0]

    # If it's a native command or option, delegate directly to the engine
    if cmd in NOVACODE_NATIVE_COMMANDS or cmd.startswith("-"):
        return launch_native_tui(args)

    # Route extended commands to Python modules
    if cmd in ("doctor", "diagnose"):
        from packages.tools.doctor import main as doctor_main
        return doctor_main(args[1:])
    elif cmd in ("generate", "gen", "imagine", "image", "video", "audio", "music", "tts", "omni"):
        from packages.media.generator import main as gen_main
        return gen_main(args[1:])
    elif cmd in ("forge", "train"):
        import runpy
        return runpy.run_module("packages.forge.trainer", run_name="__main__")
    elif cmd in ("swarm",):
        from packages.agents.swarm import main as swarm_main
        return swarm_main(args[1:])
    elif cmd in ("auto", "pilot"):
        from packages.agents.autonomous_pilot import main as auto_main
        return auto_main(args[1:])
    else:
        # If unknown, try native engine first (might be project path or custom subcommand)
        return launch_native_tui(args)

if __name__ == "__main__":
    sys.exit(main())
