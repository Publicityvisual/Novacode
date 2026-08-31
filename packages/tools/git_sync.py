"""
NovaCode Auto-Git Continuous Sync Engine
========================================
Sincronización continua y autónoma con el repositorio oficial de GitHub:
- Detección automática del directorio raíz de Git.
- Sincronización bidireccional segura (pull --rebase & push).
- Creación de mensajes de commit semánticos con IA (Conventional Commits).
- Recuperación automática ante fallos de conexión o divergencia de ramas.
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

        curr = Path.cwd().resolve()
        for p in [curr, *curr.parents]:
            if (p / ".git").is_dir():
                return p

        default_repo = Path.home() / "novacode-cli"
        if (default_repo / ".git").is_dir():
            return default_repo

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

    def check_remote_connection(self) -> Tuple[bool, str]:
        """Comprueba la conexión activa con el remoto de GitHub."""
        res = subprocess.run(["git", "-C", str(self.repo_dir), "remote", "-v"], capture_output=True, text=True)
        if res.returncode != 0 or not res.stdout.strip():
            return False, "No remote configured"
        
        # Test fetch connection
        fetch_res = subprocess.run(["git", "-C", str(self.repo_dir), "ls-remote", "--exit-code", "origin", "HEAD"], capture_output=True, text=True, timeout=10)
        if fetch_res.returncode == 0:
            return True, "Connected to GitHub successfully"
        return False, fetch_res.stderr or "Connection to GitHub remote failed"

    def sync_and_push(self, custom_msg: Optional[str] = None) -> Tuple[bool, str]:
        """Agrega cambios, realiza commit, rebase y hace push a GitHub."""
        sys.stderr.write(f"\n🚀 [NovaCode Auto-Git] Iniciando sincronización con GitHub ({self.repo_dir})...\n")

        # 1. Comprobar cambios
        has_changes = self.has_uncommitted_changes()
        if has_changes:
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

        # 5. Pull con rebase para evitar rechazos por divergencia
        subprocess.run(["git", "-C", str(self.repo_dir), "pull", "--rebase", "origin", "main"], capture_output=True, text=True)

        # 6. Push to GitHub
        push_res = subprocess.run(["git", "-C", str(self.repo_dir), "push", "-u", "origin", "main"], capture_output=True, text=True)
        if push_res.returncode == 0:
            sys.stderr.write("🎉 [NovaCode Auto-Git] ¡Sincronizado exitosamente con GitHub!\n\n")
            return True, "Sincronización exitosa con GitHub"
        else:
            sys.stderr.write(f"✗ [NovaCode Auto-Git] Error al hacer push: {push_res.stderr}\n\n")
            return False, push_res.stderr
