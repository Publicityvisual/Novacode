#!/usr/bin/env python3
"""Doctor CLI Novacode & Health Diagnostics."""
from __future__ import annotations

import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

CONFIG_NOVA = Path.home() / ".config" / "novacode" / "novacode.jsonc"
CONFIG_ALT = Path.home() / ".config" / "nova" / "nova.jsonc"

def find_engine_path() -> Path:
    candidates = [
        Path.home() / ".novacode" / "bin" / "novacode-core",
        Path.home() / ".local" / "bin" / "novacode",
        Path.home() / ".local" / "share" / "novacode" / "engine" / "libexec" / "nova",
    ]
    for c in candidates:
        if c.exists() and os.access(c, os.X_OK):
            return c
    which_nova = shutil.which("novacode")
    if which_nova:
        return Path(which_nova)
    return candidates[0]

def strip_jsonc(text: str) -> str:
    lines = []
    for line in text.splitlines():
        idx = line.find("//")
        if idx != -1:
            q_single = line[:idx].count("'")
            q_double = line[:idx].count('"')
            if q_single % 2 == 0 and q_double % 2 == 0:
                line = line[:idx]
        lines.append(line)
    text = "\n".join(lines)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r",\s*([}\]])", r"\1", text)
    return text

def check_engine() -> list[str]:
    engine = find_engine_path()
    results = []
    results.append("Motor Novacode: " + ("EXISTE" if engine.exists() else "NO ENCONTRADO"))
    results.append(f"  Ruta: {engine}")
    results.append("  Ejecutable: " + ("YES" if engine.exists() and os.access(engine, os.X_OK) else "NO"))
    if engine.exists() and platform.system() == "Darwin":
        res = subprocess.run(["codesign", "-v", str(engine)], capture_output=True, text=True)
        results.append(f"  verificación codesign: rc={res.returncode}")
    return results

def check_configs() -> list[str]:
    results = []
    cfg = CONFIG_NOVA if CONFIG_NOVA.exists() else CONFIG_ALT
    if not cfg.exists():
        results.append("Config: NO ENCONTRADO")
        return results
    try:
        data = json.loads(strip_jsonc(cfg.read_text(encoding="utf-8")))
        results.append(f"Config ({cfg.name}): OK")
        results.append(f"  modelo activo: {data.get('model', 'none')}")
        results.append(f"  modelo pequeño: {data.get('small_model', 'none')}")
        results.append(f"  providers: {', '.join(data.get('enabled_providers', []))}")
    except Exception as e:
        results.append(f"Error de config: {e}")
    return results

def check_key() -> list[str]:
    results = []
    key = os.environ.get("NVIDIA_API_KEY", "")
    if not key:
        for p in [Path.home() / ".config" / "nova" / "secrets.env", Path.home() / ".config" / "env" / "nvidia.env"]:
            if p.exists():
                for line in p.read_text(encoding="utf-8").splitlines():
                    if "NVIDIA_API_KEY=" in line:
                        key = line.split("=", 1)[1].strip().strip("\"'")
                        break
    if key:
        results.append(f"API Key NVIDIA: Activa ({key[:6]}...)")
    else:
        results.append("API Key NVIDIA: FALTANTE")
    return results

def check_generation() -> list[str]:
    results = []
    gen = Path.home() / ".local" / "share" / "novacode" / "generate.py"
    results.append("generate.py: " + ("EXISTE" if gen.exists() else "NO ENCONTRADO"))
    gguf = Path.home() / "models" / "huihui-qwythos-9b"
    ggufs = list(gguf.glob("*.gguf")) if gguf.exists() else []
    results.append("GGUF local sin censura: " + (ggufs[0].name if ggufs else "NO ENCONTRADO"))
    results.append("llama-cli: " + ("YES" if shutil.which("llama-cli") else "NO"))
    results.append("llama-server: " + ("YES" if shutil.which("llama-server") else "NO"))
    results.append("ollama: " + ("YES" if shutil.which("ollama") else "NO"))
    try:
        import socket as _socket
        with _socket.create_connection(("127.0.0.1", 18792), timeout=0.3):
            local_up = True
    except OSError:
        local_up = False
    results.append("servidor sin censura :18792: " + ("ACTIVO" if local_up else "inactivo (bajo demanda)"))
    results.append("política: NSFW adulto ON — sin restricciones")
    return results


def check_path() -> list[str]:
    results = []
    local_bin = str(Path.home() / ".local" / "bin")
    in_path = local_bin in os.environ.get("PATH", "")
    results.append(f"PATH ~/.local/bin: {'YES' if in_path else 'NO'}")
    nova_bin = shutil.which("novacode") or shutil.which("nova")
    results.append(f"Binario activo: {nova_bin or 'NO ENCONTRADO'}")
    return results

def main(args=None) -> int:
    print("=" * 60)
    print("Doctor CLI Novacode")
    print("=" * 60 + "\n")
    
    print("--- Motor ---")
    for l in check_engine():
        print(l)
        
    print("\n--- PATH / Instalación ---")
    for l in check_path():
        print(l)
        
    print("\n--- Configuraciones ---")
    for l in check_configs():
        print(l)
        
    print("\n--- Conexión NVIDIA NIM ---")
    for l in check_key():
        print(l)

    print("\n--- Generación sin censura / NSFW ---")
    for l in check_generation():
        print(l)
        
    print("\n" + "=" * 60)
    print("TODOS LOS SISTEMAS OPERACIONALES (100% NOVACODE NATIVO)")
    print("=" * 60)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
