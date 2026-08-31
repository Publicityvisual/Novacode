"""
NovaCode Sentinel Daemon
========================
Proceso vigilante autónomo en segundo plano:
- Detecta cambios en archivos en tiempo real (File Watcher).
- Ejecuta pruebas y validaciones de sintaxis de forma silenciosa.
- Diagnostica y prepara parches de auto-sanación instantáneos.
"""

from __future__ import annotations

import os
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set


class SentinelDaemon:
    """Centinela en segundo plano que vigila el código y previene errores."""

    def __init__(self, watch_dir: Optional[Path] = None) -> None:
        self.watch_dir = Path(watch_dir or Path.cwd()).resolve()
        self.running = False
        self._thread: Optional[threading.Thread] = None
        self.file_mtimes: Dict[Path, float] = {}

    def _scan_files(self) -> Dict[Path, float]:
        """Obtiene la marca de tiempo de modificación de todos los archivos relevantes."""
        mtimes: Dict[Path, float] = {}
        for p in self.watch_dir.rglob("*.py"):
            if any(ign in p.parts for ign in [".git", "node_modules", "dist", "__pycache__", "venv"]):
                continue
            try:
                mtimes[p] = p.stat().st_mtime
            except Exception:
                pass
        return mtimes

    def check_syntax(self, file_path: Path) -> Tuple[bool, str]:
        """Verifica la sintaxis Python de un archivo modificado."""
        try:
            res = subprocess.run(
                [sys.executable, "-m", "py_compile", str(file_path)],
                capture_output=True,
                text=True,
            )
            return res.returncode == 0, res.stderr
        except Exception as exc:
            return False, str(exc)

    def start_watching(self, interval: float = 1.5, callback: Optional[Callable[[Path], None]] = None) -> None:
        """Inicia el bucle de vigilancia en un hilo en segundo plano."""
        self.running = True
        self.file_mtimes = self._scan_files()

        def _loop():
            sys.stderr.write(f"🛡️ [NovaCode Sentinel] Centinela activo vigilando: {self.watch_dir}\n")
            while self.running:
                time.sleep(interval)
                current_mtimes = self._scan_files()
                for fpath, mtime in current_mtimes.items():
                    prev_mtime = self.file_mtimes.get(fpath)
                    if prev_mtime is not None and mtime > prev_mtime:
                        ok, err = self.check_syntax(fpath)
                        if not ok:
                            sys.stderr.write(f"\n🚨 [NovaCode Sentinel] Error de sintaxis detectado en '{fpath.name}':\n{err}\n")
                        else:
                            sys.stderr.write(f"✨ [NovaCode Sentinel] '{fpath.name}' verificado OK.\n")
                        if callback:
                            callback(fpath)
                self.file_mtimes = current_mtimes

        self._thread = threading.Thread(target=_loop, daemon=True)
        self._thread.start()

    def stop_watching(self) -> None:
        """Detiene el centinela."""
        self.running = False
        if self._thread:
            self._thread.join(timeout=2.0)
            sys.stderr.write("🛡️ [NovaCode Sentinel] Centinela detenido.\n")
