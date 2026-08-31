"""
NovaCode Auto-Git Continuous Sync Engine
========================================
Sincronización continua y autónoma con el repositorio oficial de GitHub:
- Detección automática del directorio raíz de Git.
- Creación de mensajes de commit semánticos con IA (Conventional Commits).
- Push seguro hacia la rama principal de GitHub (`origin main`).
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple


class AutoGitSync:
    """Motor de sincronización y publicación continua en GitHub."""

    def __init__(self, repo_dir: Optional[Path] = None, ai_client: Optional[Callable[[str], str]] = None) -> None:
        self.repo_dir = self._detect_repo_dir(repo_dir)
        self.ai_client = ai_client

    def _detect_repo_dir(self, explicit_dir: Optional[Path] = None) -> Path:
        """Detecta de forma inteligente la raíz del repositorio Git."""
        if explicit_dir:
            return Path(explicit_dir).resolve()

        # 1. Comprobar si el directorio actual es un repo
        curr = Path.cwd().resolve()
        for p in [curr, *curr.parents]:
            if (p / ".git").is_dir():
                return p

        # 2. Comprobar la ruta estándar ~/novacode-cli
        default_repo = Path.home() / "novacode-cli"
        if (default_repo / ".git").is_dir():
            return default_repo

        # 3. Fallback al directorio del archivo
        return Path(__file__).resolve().parent

    def has_uncommitted_changes(self) -> bool:
        """Comprueba si hay archivos modificados o sin rastrear."""
        res = subprocess.run(["git", "-C", str(self.repo_dir), "status", "--porcelain"], capture_output=True, text=True)
        return bool(res.stdout.strip())

    def generate_commit_message(self, diff_text: str) -> str:
        """Genera un mensaje de commit convencional profesional."""
        if self.ai_client:
            prompt = (
                "Genera un mensaje de commit convencional conciso (ej: 'feat: ...' o 'fix: ...') "
                f"para el siguiente diff de git:\n\n{diff_text[:1500]}\n\n"
                "Devuelve ÚNICAMENTE el mensaje en una línea."
            )
            try:
                msg = self.ai_client(prompt).strip().strip("\"'")
                if msg:
                    return msg
            except Exception:
                pass
        return f"feat: automated continuous innovation sync at {time.strftime('%Y-%m-%d %H:%M:%S')}"

    def sync_and_push(self, custom_msg: Optional[str] = None) -> Tuple[bool, str]:
        """Agrega cambios, realiza commit y hace push a GitHub."""
        sys.stderr.write(f"\n🚀 [NovaCode Auto-Git] Iniciando sincronización con GitHub ({self.repo_dir})...\n")

        # 1. Comprobar cambios
        if not self.has_uncommitted_changes():
            sys.stderr.write("ℹ [NovaCode Auto-Git] Repositorio limpio. No hay cambios pendientes.\n")
            # Push por si hay commits locales sin subir
            push_res = subprocess.run(["git", "-C", str(self.repo_dir), "push", "origin", "main"], capture_output=True, text=True)
            return push_res.returncode == 0, push_res.stdout or push_res.stderr

        # 2. Stage changes
        subprocess.run(["git", "-C", str(self.repo_dir), "add", "."], check=True)

        # 3. Get diff for commit message
        diff_res = subprocess.run(["git", "-C", str(self.repo_dir), "diff", "--cached", "--stat"], capture_output=True, text=True)
        commit_msg = custom_msg or self.generate_commit_message(diff_res.stdout)

        # 4. Commit
        commit_res = subprocess.run(["git", "-C", str(self.repo_dir), "commit", "-m", commit_msg], capture_output=True, text=True)
        if commit_res.returncode != 0:
            return False, f"Fallo en commit: {commit_res.stderr}"

        sys.stderr.write(f"✓ [NovaCode Auto-Git] Commit creado: '{commit_msg}'\n")

        # 5. Push to GitHub
        push_res = subprocess.run(["git", "-C", str(self.repo_dir), "push", "origin", "main"], capture_output=True, text=True)
        if push_res.returncode == 0:
            sys.stderr.write("🎉 [NovaCode Auto-Git] ¡Sincronizado exitosamente con GitHub!\n\n")
            return True, "Sincronización exitosa con GitHub"
        else:
            sys.stderr.write(f"✗ [NovaCode Auto-Git] Error al hacer push: {push_res.stderr}\n\n")
            return False, push_res.stderr
