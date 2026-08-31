#!/usr/bin/env python3
"""Novacode Rebranding Utility."""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

SHARE = Path.home() / ".local" / "share" / "novacode"
if str(SHARE) not in sys.path:
    sys.path.insert(0, str(SHARE))

def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] in ("--help", "-h"):
        print("Novacode Rebranding Utility")
        print("Aplica branding y configuraciones de Novacode al entorno.")
        return 0
    setup_file = SHARE / "setup-novacode.py"
    if setup_file.exists():
        print("Aplicando branding de Novacode...")
        runpy.run_path(str(setup_file), run_name="__main__")
        print("Branding de Novacode aplicado con éxito.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
