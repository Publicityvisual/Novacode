"""
NovaCode Developer Tools Suite
==============================
Herramientas avanzadas integradas para desarrolladores y administradores de sistemas:
- ApiTester: Cliente HTTP inteligente, pruebas de endpoints y formateador JSON.
- DatabasePilot: Inspector de bases de datos SQLite / SQL y generador de consultas.
- NetworkPilot: Escáner de puertos, comprobador DNS y latencia.
- SecretScanner: Auditor de seguridad de secretos y credenciales filtradas.
"""

from __future__ import annotations

import json
import os
import re
import socket
import sqlite3
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class ApiTester:
    """Cliente y evaluador de APIs REST / GraphQL."""

    @staticmethod
    def test_endpoint(url: str, method: str = "GET", headers: Optional[Dict[str, str]] = None, body: Optional[str] = None) -> Dict[str, Any]:
        """Realiza una petición HTTP y mide la latencia y cabeceras."""
        t0 = time.time()
        headers = headers or {"User-Agent": "CodeForge-ApiTester/1.0"}
        data = body.encode("utf-8") if body else None

        req = urllib.request.Request(url, data=data, headers=headers, method=method.upper())
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                dt = time.time() - t0
                raw_body = resp.read().decode("utf-8", errors="replace")
                try:
                    parsed_json = json.loads(raw_body)
                except Exception:
                    parsed_json = None

                return {
                    "url": url,
                    "status": resp.status,
                    "latency_sec": dt,
                    "is_json": parsed_json is not None,
                    "body": parsed_json if parsed_json is not None else raw_body[:500],
                }
        except Exception as exc:
            return {
                "url": url,
                "status": getattr(exc, "code", 500),
                "latency_sec": time.time() - t0,
                "error": str(exc),
            }


class NetworkPilot:
    """Escáner de conectividad y puertos de red."""

    @staticmethod
    def check_port(host: str, port: int, timeout: float = 0.5) -> bool:
        """Comprueba si un puerto está abierto y aceptando conexiones."""
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except (OSError, socket.timeout):
            return False

    @staticmethod
    def scan_common_ports(host: str = "127.0.0.1") -> Dict[int, str]:
        """Escanea los puertos de desarrollo más comunes."""
        common = {
            80: "HTTP",
            443: "HTTPS",
            3000: "Node / React",
            5173: "Vite",
            8000: "FastAPI / Django",
            8080: "HTTP Alt",
            18791: "Nova Proxy",
            18792: "Nova LLM Local",
        }
        open_ports = {}
        for port, service in common.items():
            if NetworkPilot.check_port(host, port):
                open_ports[port] = service
        return open_ports


class SecretScanner:
    """Escáner de seguridad para prevenir la fuga de claves y tokens."""

    PATTERNS = [
        (r"nvapi-[A-Za-z0-9_-]{40,}", "NVIDIA API Key"),
        (r"ghp_[A-Za-z0-9]{36,}", "GitHub Personal Access Token"),
        (r"sk-[A-Za-z0-9]{32,}", "OpenAI API Key"),
        (r"AIza[0-9A-Za-z-_]{35}", "Google API Key"),
        (r"-----BEGIN (RSA|EC|OPENSSH) PRIVATE KEY-----", "Private Key File"),
    ]

    @classmethod
    def scan_directory(cls, dir_path: Path) -> List[Dict[str, Any]]:
        """Escanea un directorio en busca de secretos expuestos."""
        findings = []
        dir_path = Path(dir_path).resolve()

        for p in dir_path.rglob("*"):
            if not p.is_file():
                continue
            parts = set(p.parts)
            if any(ign in parts for ign in [".git", "node_modules", "dist", "__pycache__", "secrets.env", "nvidia.env"]):
                continue
            if p.suffix in [".png", ".jpg", ".ico", ".db", ".pyc"]:
                continue
            try:
                txt = p.read_text(encoding="utf-8", errors="ignore")
                for pattern, name in cls.PATTERNS:
                    m = re.search(pattern, txt)
                    if m:
                        findings.append({
                            "file": str(p.relative_to(dir_path)),
                            "type": name,
                            "match_snippet": m.group(0)[:12] + "...",
                        })
            except Exception:
                pass
        return findings
