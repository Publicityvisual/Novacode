#!/usr/bin/env python3
"""
Novacode Git Hook Manager & Code Quality Guard
Installs and runs pre-commit quality checks to prevent breaking builds.
"""
import os, sys, subprocess
from pathlib import Path

HOOK_SCRIPT = """#!/bin/sh
# Novacode Automated Quality Guard Pre-Commit Hook
echo "🛡️ Novacode Quality Guard: Verificando staged files..."
novacode hook run
"""

def install_hook():
    git_dir = Path.cwd() / ".git"
    if not git_dir.exists():
        print("❌ Error: No se encontró repositorio Git en el directorio actual.")
        sys.exit(1)
    
    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    pre_commit = hooks_dir / "pre-commit"
    
    pre_commit.write_text(HOOK_SCRIPT, encoding="utf-8")
    pre_commit.chmod(0o755)
    print("✅ Novacode Quality Guard Hook instalado en .git/hooks/pre-commit")

def run_checks():
    print("🔍 Ejecutando verificación de calidad...")
    # 1. Check for syntax / linters if available
    errors = 0
    
    # Check Python syntax if python files are modified
    res = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"], capture_output=True, text=True)
    files = [f.strip() for f in res.stdout.splitlines() if f.strip()]
    
    for f in files:
        if f.endswith(".py"):
            chk = subprocess.run([sys.executable, "-m", "py_compile", f], capture_output=True, text=True)
            if chk.returncode != 0:
                print(f"❌ Error de sintaxis en {f}:\n{chk.stderr}")
                errors += 1
                
    if errors > 0:
        print(f"\n❌ Pre-commit abortado: {errors} archivo(s) con errores de sintaxis.")
        print("💡 Ejecuta 'novacode \"corrige los errores de sintaxis\"' para auto-sanar.")
        sys.exit(1)
        
    print("✨ Calidad verificada: 0 errores. Commit aprobado.")
    sys.exit(0)

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "install":
        install_hook()
    elif len(sys.argv) > 1 and sys.argv[1] == "run":
        run_checks()
    else:
        print("Uso: novacode hook [install|run]")

if __name__ == "__main__":
    main()
