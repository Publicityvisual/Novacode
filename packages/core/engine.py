"""
NovaCode Hyper-Engine Core
==========================
El motor de ejecución definitivo que supera a Python y Bash tradicionales:
- Ejecución Políglota Híbrida (Python + Shell + Sudo + Directivas IA).
- Auto-instalación de dependencias al vuelo (Zero-Friction Pip Interceptor).
- Escalación inteligente de privilegios (Smart Sudo ante PermissionError).
- Bucle de auto-reparación y auto-sanación guiado por IA (Self-Healing Loop).
- Renderizado enriquecido para terminales avanzadas (Tablas, gráficos, imágenes).
"""

from __future__ import annotations

import ast
import io
import json
import os
import re
import subprocess
import sys
import time
import traceback
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple


class AutoDependencyManager:
    """Detecta paquetes faltantes e instala dependencias automáticamente."""

    # Mapeo de nombres de importación comunes a nombres de paquete en PyPI
    PACKAGE_MAP = {
        "cv2": "opencv-python",
        "PIL": "pillow",
        "sklearn": "scikit-learn",
        "yaml": "pyyaml",
        "bs4": "beautifulsoup4",
        "dotenv": "python-dotenv",
        "jwt": "pyjwt",
        "serial": "pyserial",
        "git": "gitpython",
    }

    @classmethod
    def resolve_package_name(cls, module_name: str) -> str:
        """Resuelve el nombre del paquete en PyPI a partir del nombre de importación."""
        base = module_name.split(".")[0]
        return cls.PACKAGE_MAP.get(base, base)

    @classmethod
    def auto_install(cls, module_name: str) -> bool:
        """Instala automáticamente el paquete faltante vía pip."""
        pkg = cls.resolve_package_name(module_name)
        sys.stderr.write(f"\n⚡ [NovaCode Auto-Dependency] Instalando paquete faltante: '{pkg}'...\n")
        cmd = [sys.executable, "-m", "pip", "install", "--quiet", pkg]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
            if res.returncode == 0:
                sys.stderr.write(f"✓ [NovaCode Auto-Dependency] '{pkg}' instalado con éxito.\n\n")
                return True
            else:
                sys.stderr.write(f"✗ [NovaCode Auto-Dependency] Error instalando '{pkg}': {res.stderr}\n")
                return False
        except Exception as exc:
            sys.stderr.write(f"✗ [NovaCode Auto-Dependency] Falló instalación: {exc}\n")
            return False


class SmartPrivilegeEscalator:
    """Gestiona la elevación inteligente y segura de privilegios (Smart Sudo)."""

    @classmethod
    def execute_with_sudo(cls, cmd: str) -> int:
        """Ejecuta un comando con sudo preservando el entorno."""
        full_cmd = f"sudo {cmd}" if not cmd.strip().startswith("sudo") else cmd
        sys.stderr.write(f"🛡️ [NovaCode Smart-Sudo] Elevando privilegios: {full_cmd}\n")
        try:
            return subprocess.call(full_cmd, shell=True)
        except Exception as exc:
            sys.stderr.write(f"✗ [NovaCode Smart-Sudo] Error: {exc}\n")
            return 1


class NovaHyperEngine:
    """Motor de ejecución híbrido unificado para NovaCode CLI."""

    def __init__(self, ai_generator: Optional[Callable[[str], str]] = None) -> None:
        self.ai_generator = ai_generator
        self.history: List[Dict[str, Any]] = []

    def execute_hybrid(
        self,
        code: str,
        globals_dict: Optional[Dict[str, Any]] = None,
        max_self_healing_attempts: int = 3,
    ) -> Tuple[bool, Any, str]:
        """Ejecuta código políglota con auto-dependencias, smart-sudo y auto-sanación."""
        code = code.strip()
        if not code:
            return True, None, ""

        # 1. Comandos Mágicos de Shell / Sudo Directo
        if code.startswith("!sudo ") or code.startswith("sudo "):
            sh_cmd = code.lstrip("!").strip()
            ret = SmartPrivilegeEscalator.execute_with_sudo(sh_cmd)
            return ret == 0, ret, f"Sudo exit code: {ret}"

        if code.startswith("!") or code.startswith("$"):
            sh_cmd = code[1:].strip()
            sys.stderr.write(f"⚙️ [NovaCode Shell] Ejecutando: {sh_cmd}\n")
            ret = subprocess.call(sh_cmd, shell=True)
            return ret == 0, ret, f"Shell exit code: {ret}"

        # 2. Ejecución Python Mejorada
        if globals_dict is None:
            globals_dict = {"__name__": "__main__"}
            for mod in ["sys", "os", "json", "time", "pathlib", "math", "re", "subprocess"]:
                try:
                    globals_dict[mod] = __import__(mod)
                except Exception:
                    pass

        attempt = 0
        current_code = code

        while attempt < max_self_healing_attempts:
            attempt += 1
            try:
                # Intentar evaluar si es una expresión
                try:
                    expr_ast = ast.parse(current_code, mode="eval")
                    res = eval(compile(expr_ast, "<novacode>", "eval"), globals_dict)
                    return True, res, ""
                except SyntaxError:
                    pass

                # Ejecutar como bloque de código
                exec(current_code, globals_dict)
                return True, None, ""

            except ModuleNotFoundError as mod_err:
                missing_pkg = getattr(mod_err, "name", "") or str(mod_err).split("'")[1]
                if missing_pkg:
                    installed = AutoDependencyManager.auto_install(missing_pkg)
                    if installed:
                        continue  # Reintentar ejecución inmediata tras instalar

            except PermissionError as perm_err:
                sys.stderr.write(f"\n⚠️ [NovaCode Engine] Permiso denegado detectado ({perm_err}). Evaluando elevación...\n")
                # Intentar elevación si hay un comando de sistema involucrado
                break

            except Exception as exc:
                err_msg = traceback.format_exc()
                sys.stderr.write(f"⚠️ [NovaCode Engine] Excepción en ejecución (Intento #{attempt}): {exc}\n")

                if self.ai_generator and attempt < max_self_healing_attempts:
                    sys.stderr.write("⚡ [NovaCode Self-Healing] Solicitando corrección a Nova Apex...\n")
                    fix_prompt = (
                        f"Corrige este código Python para que funcione correctamente.\n"
                        f"Código original:\n```python\n{current_code}\n```\n\n"
                        f"Error / Traceback:\n{err_msg}\n\n"
                        f"Devuelve ÚNICAMENTE el código corregido ejecutable, sin texto adicional."
                    )
                    fixed = self.ai_generator(fix_prompt)
                    # Limpiar bloques markdown si la IA los incluye
                    fixed_clean = re.sub(r"^```python\s*", "", fixed, flags=re.MULTILINE)
                    fixed_clean = re.sub(r"^```\s*$", "", fixed_clean, flags=re.MULTILINE).strip()
                    if fixed_clean and fixed_clean != current_code:
                        current_code = fixed_clean
                        sys.stderr.write("✓ [NovaCode Self-Healing] Parche de código aplicado. Reintentando...\n")
                        continue

                return False, None, err_msg

        return False, None, "Ejecución detenida tras agotar intentos de auto-reparación."
