#!/usr/bin/env python3
"""
NOVACODE CLI — Interfaz profesional de línea de comandos
Diseñada para ofrecer la mejor experiencia local de IA: velocidad, control y claridad.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "memory"))


def main(argv: list[str] | None = None) -> int:
    from nexus import main as nexus_main
    return nexus_main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
