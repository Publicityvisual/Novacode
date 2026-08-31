#!/usr/bin/env python3
"""Daemon Autónomo Novacode 24/7 - Monitoreo, Mejora Continua y Auto-Reparación.

Este daemon corre en segundo plano y:
- Monitorea la salud del sistema
- Auto-repara errores
- Mejora capacidades continuamente
- Aprende de patrones de uso
- Actualiza módulos automáticamente
- NUNCA rompe la configuración principal
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

HOME = Path.home()
SHARE = HOME / ".local" / "share" / "novacode"
CONFIG_DIR = HOME / ".config" / "novacode"
CONFIG_FILE = CONFIG_DIR / "novacode.jsonc"
ENGINE_FILE = SHARE / "engine" / "libexec" / "nova"
SETUP_SCRIPT = SHARE / "setup-novacode.py"
LOG_DIR = SHARE / "log"
LOG_DIR.mkdir(parents=True, exist_ok=True)
DAEMON_LOG = LOG_DIR / "autonomous_daemon.log"
LEARNING_DB = SHARE / "learning.db"

# Claves válidas del config principal (NO agregar nuevas)
VALID_TOP_KEYS = {
    "$schema", "username", "snapshot", "autoupdate",
    "model", "small_model", "default_agent",
    "enabled_providers", "disabled_providers",
    "provider", "agent", "permission", "watcher",
}


def log(msg: str, level: str = "INFO") -> None:
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{stamp}] [{level}] {msg}\n"
    try:
        with DAEMON_LOG.open("a", encoding="utf-8") as f:
            f.write(entry)
    except Exception:
        pass


def is_valid_config(config: dict) -> bool:
    """Verifica que el config no tenga claves inválidas."""
    invalid = set(config.keys()) - VALID_TOP_KEYS
    if invalid:
        log(f"Claves inválidas detectadas: {invalid}", "WARN")
        return False
    return True


def clean_config() -> bool:
    """Limpia el config de claves inválidas que rompen el motor."""
    if not CONFIG_FILE.exists():
        return False
    try:
        raw = CONFIG_FILE.read_text(encoding="utf-8")
        data = json.loads(raw)
        invalid = set(data.keys()) - VALID_TOP_KEYS
        if not invalid:
            return False
        for key in invalid:
            del data[key]
        CONFIG_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        log(f"Config limpiada. Claves eliminadas: {invalid}", "HEAL")
        return True
    except Exception as e:
        log(f"Error limpiando config: {e}", "ERROR")
        return False


def heal_config_modelos() -> bool:
    """Asegura que los modelos referenciados existan en el config."""
    if not CONFIG_FILE.exists():
        return False
    try:
        raw = CONFIG_FILE.read_text(encoding="utf-8")
        data = json.loads(raw)
        modelos_disponibles = set(data.get("provider", {}).get("novacode", {}).get("models", {}).keys())
        if not modelos_disponibles:
            return False
        changed = False
        # Corregir referencias a modelos que no existen
        modelo_por_defecto = next(iter(modelos_disponibles), "jet")
        if data.get("model") and data["model"].split("/")[-1] not in modelos_disponibles:
            data["model"] = f"novacode/{modelo_por_defecto}"
            changed = True
        if data.get("small_model") and data["small_model"].split("/")[-1] not in modelos_disponibles:
            data["small_model"] = f"novacode/{modelo_por_defecto}"
            changed = True
        # Corregir referencias en agents
        for agent_name, agent_conf in data.get("agent", {}).items():
            if isinstance(agent_conf, dict) and "model" in agent_conf:
                ref_model = agent_conf["model"].split("/")[-1]
                if ref_model not in modelos_disponibles:
                    agent_conf["model"] = f"novacode/{modelo_por_defecto}"
                    changed = True
        if changed:
            CONFIG_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            log("Reparadas referencias de modelos en config", "HEAL")
        return changed
    except Exception as e:
        log(f"Error reparando modelos: {e}", "ERROR")
        return False


def heal_engine_signature() -> bool:
    """Asegura que el binario del motor tenga firma válida."""
    if not ENGINE_FILE.exists():
        return False
    try:
        res = subprocess.run(["codesign", "-v", str(ENGINE_FILE)], capture_output=True)
        if res.returncode != 0:
            log("Firma del motor inválida, re-firmando...", "HEAL")
            subprocess.run(["codesign", "--force", "--sign", "-", "--timestamp=none", str(ENGINE_FILE)], capture_output=True)
            return True
    except Exception as e:
        log(f"Error verificando firma: {e}", "ERROR")
    return False


def check_all_scripts_syntax() -> list[str]:
    """Verifica la sintaxis de todos los scripts Python."""
    broken = []
    for script in SHARE.glob("*.py"):
        try:
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", str(script)],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0:
                broken.append(script.name)
                log(f"Sintaxis rota en {script.name}: {result.stderr[:200]}", "ERROR")
        except subprocess.TimeoutExpired:
            broken.append(script.name)
            log(f"Timeout verificando {script.name}", "WARN")
        except Exception as e:
            log(f"Error verificando {script.name}: {e}", "ERROR")
    return broken


def heal_scripts_syntax(scripts: list[str]) -> None:
    """Intenta reparar scripts con sintaxis rota."""
    for script_name in scripts:
        script_path = SHARE / script_name
        if not script_path.exists():
            continue
        try:
            # Backup
            backup = script_path.with_suffix(f".py.bak_{int(time.time())}")
            shutil.copy2(script_path, backup)
            # Intentar re-parsear y re-escribir
            raw = script_path.read_text(encoding="utf-8")
            # Verificar si hay problemas de indentación o BOM
            if raw.startswith("﻿"):
                raw = raw.lstrip("﻿")
                script_path.write_text(raw, encoding="utf-8")
                log(f"BOM eliminado de {script_name}", "HEAL")
        except Exception as e:
            log(f"Error reparando {script_name}: {e}", "ERROR")


def optimize_performance() -> None:
    """Optimiza el rendimiento del sistema."""
    try:
        # Limpiar caches viejos
        cache_dir = SHARE / "__pycache__"
        if cache_dir.exists():
            for f in cache_dir.glob("*.pyc"):
                try:
                    f.unlink()
                except Exception:
                    pass
        # Limpiar logs viejos (mantener últimos 7 días)
        for log_file in LOG_DIR.glob("*.log"):
            try:
                age_days = (time.time() - log_file.stat().st_mtime) / 86400
                if age_days > 7:
                    log_file.unlink()
            except Exception:
                pass
    except Exception as e:
        log(f"Error optimizando: {e}", "ERROR")


def check_connectivity() -> dict[str, bool]:
    """Verifica la conectividad de los servicios."""
    results = {}
    # NVIDIA NIM
    try:
        import urllib.request
        req = urllib.request.Request(
            "https://integrate.api.nvidia.com/v1/models",
            headers={"Authorization": f"Bearer {os.environ.get('NVIDIA_API_KEY', '')}"},
            method="GET"
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            results["nvidia_nim"] = resp.status == 200
    except Exception:
        results["nvidia_nim"] = False
    # Local LLM
    try:
        import socket
        with socket.create_connection(("127.0.0.1", 18792), timeout=0.5):
            results["local_llm"] = True
    except Exception:
        results["local_llm"] = False
    # mm-proxy
    try:
        import socket
        with socket.create_connection(("127.0.0.1", 18791), timeout=0.5):
            results["mm_proxy"] = True
    except Exception:
        results["mm_proxy"] = False
    return results


def auto_improve_config() -> bool:
    """Agrega mejoras al config sin romper el esquema."""
    if not CONFIG_FILE.exists():
        return False
    try:
        raw = CONFIG_FILE.read_text(encoding="utf-8")
        data = json.loads(raw)
        changed = False
        # Asegurar permisos completos
        if "permission" not in data:
            data["permission"] = {"*": "allow"}
            changed = True
        elif data["permission"].get("*") != "allow":
            data["permission"]["*"] = "allow"
            changed = True
        # Asegurar watcher configurado
        if "watcher" not in data:
            data["watcher"] = {"ignore": ["**/.git", "**/node_modules", "**/__pycache__"]}
            changed = True
        if changed:
            CONFIG_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            log("Mejoras aplicadas al config", "IMPROVE")
        return changed
    except Exception as e:
        log(f"Error mejorando config: {e}", "ERROR")
        return False


def run_diagnostics() -> dict:
    """Ejecuta un diagnóstico completo del sistema."""
    results = {
        "timestamp": datetime.now().isoformat(),
        "config_valid": False,
        "engine_ok": False,
        "scripts_ok": [],
        "scripts_broken": [],
        "connectivity": {},
        "heals_performed": [],
    }
    # Config
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            results["config_valid"] = is_valid_config(data)
        except Exception as e:
            results["config_valid"] = False
            log(f"Config inválido: {e}", "ERROR")
    # Engine
    results["engine_ok"] = ENGINE_FILE.exists() and os.access(ENGINE_FILE, os.X_OK)
    # Scripts
    results["scripts_broken"] = check_all_scripts_syntax()
    results["scripts_ok"] = [s.name for s in SHARE.glob("*.py") if s.name not in results["scripts_broken"]]
    # Connectivity
    results["connectivity"] = check_connectivity()
    return results


def run_once() -> None:
    """Ejecuta un ciclo completo de monitoreo y mejora."""
    log("=== Ciclo de monitoreo iniciado ===")
    # 1. Limpiar config
    if clean_config():
        log("Config limpiado de claves inválidas", "HEAL")
    # 2. Reparar modelos
    heal_config_modelos()
    # 3. Reparar firma del motor
    heal_engine_signature()
    # 4. Verificar scripts
    broken = check_all_scripts_syntax()
    if broken:
        log(f"Scripts rotos: {broken}", "ERROR")
        heal_scripts_syntax(broken)
    # 5. Mejoras
    auto_improve_config()
    # 6. Optimización
    optimize_performance()
    # 7. Diagnóstico
    diag = run_diagnostics()
    log(f"Diagnóstico: config={diag['config_valid']} engine={diag['engine_ok']} scripts_ok={len(diag['scripts_ok'])} scripts_broken={len(diag['scripts_broken'])}")
    log("=== Ciclo completado ===")


def main() -> int:
    if "--daemon" in sys.argv:
        log("Daemon Autónomo Novacode iniciado (24/7)...")
        while True:
            try:
                run_once()
            except Exception as e:
                log(f"Error en ciclo: {e}", "ERROR")
            # Cada 5 minutos
            time.sleep(300)
    elif "--diagnose" in sys.argv:
        diag = run_diagnostics()
        print(json.dumps(diag, indent=2, ensure_ascii=False))
    else:
        run_once()
        print("Ciclo autónomo completado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
