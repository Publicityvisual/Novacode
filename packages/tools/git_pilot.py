#!/usr/bin/env python3
"""Novacode Git Auto-Pilot: Conventional Commits and PR Generator."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


def find_nova_bin() -> str:
    candidates = [
        Path.home() / ".opencode" / "bin" / "opencode",
        Path.home() / ".local" / "bin" / "novacode",
        Path.home() / ".local" / "share" / "novacode" / "engine" / "libexec" / "nova",
    ]
    for c in candidates:
        if c.exists() and os.access(c, os.X_OK):
            return str(c)
    return shutil.which("novacode") or shutil.which("opencode") or "novacode"


def run_cmd(cmd: list[str]) -> tuple[int, str]:
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.returncode, res.stdout.strip()


def get_diff() -> str:
    rc, staged = run_cmd(["git", "diff", "--cached"])
    if staged:
        return staged
    rc, unstaged = run_cmd(["git", "diff"])
    if unstaged:
        run_cmd(["git", "add", "-u"])
        rc, staged = run_cmd(["git", "diff", "--cached"])
        return staged or unstaged
    return ""


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "commit"
    diff = get_diff()
    
    if not diff:
        print("Git Auto-Pilot: No se detectaron cambios para commitear o analizar.")
        return 0
        
    diff_snippet = diff[:4000]
    nova_bin = find_nova_bin()
    
    if cmd == "commit":
        prompt = (
            f"Genera un mensaje de commit Convencional único y preciso (e.g. feat(scope): message or fix(scope): message) "
            f"para este git diff. Devuelve ÚNICAMENTE el mensaje en una sola línea:\n\n{diff_snippet}"
        )
        res = subprocess.run([nova_bin, "run", prompt], capture_output=True, text=True)
        msg = res.stdout.strip().splitlines()[-1].strip().strip('"\'') if res.stdout else ""
        if not msg or "error" in msg.lower():
            msg = "chore: update project codebase"
        print(f"Mensaje de Commit Git Auto-Pilot: {msg}")
        rc, out = run_cmd(["git", "commit", "-m", msg])
        print(out)
        return rc
        
    elif cmd in ("pr", "pull-request"):
        prompt = (
            f"Genera una descripción de Pull Request para GitHub completa y clara en Markdown "
            f"con Resumen de Cambios y Checklist para este diff:\n\n{diff_snippet}"
        )
        subprocess.run([nova_bin, "run", prompt])
        return 0
        
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
