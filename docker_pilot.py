"""
NovaCode Docker Pilot & Container AI Suite
==========================================
Gestión, generación, optimización y auto-sanación de Docker y contenedores:
- Generador automático de Dockerfiles multi-etapa y docker-compose.yml optimizados.
- Auto-diagnóstico y auto-reparación de contenedores caídos a partir de logs de error.
- Auditoría de seguridad de imágenes (detección de usuarios root y secretos expuestos).
- Ejecución aislada de código en contenedores seguros.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple


class DockerPilot:
    """Piloto autónomo de Docker y orquestación de contenedores."""

    def __init__(self, ai_client: Optional[Callable[[str, str], str]] = None) -> None:
        self.ai_client = ai_client

    def is_docker_available(self) -> bool:
        """Comprueba si Docker está instalado y el daemon está corriendo."""
        try:
            res = subprocess.run(["docker", "info"], capture_output=True, text=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def detect_project_stack(self, project_dir: Path) -> Dict[str, Any]:
        """Detecta automáticamente el lenguaje y framework del proyecto."""
        project_dir = Path(project_dir).resolve()
        stack = {"language": "unknown", "framework": "generic", "entrypoint": "", "port": 8080}

        if (project_dir / "package.json").exists():
            stack["language"] = "nodejs"
            try:
                pkg = json.loads((project_dir / "package.json").read_text(encoding="utf-8"))
                deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
                if "next" in deps:
                    stack["framework"] = "nextjs"
                    stack["port"] = 3000
                elif "vite" in deps or "react" in deps:
                    stack["framework"] = "react"
                    stack["port"] = 5173
                elif "express" in deps:
                    stack["framework"] = "express"
                    stack["port"] = 3000
            except Exception:
                pass
        elif (project_dir / "requirements.txt").exists() or (project_dir / "pyproject.toml").exists() or any(project_dir.glob("*.py")):
            stack["language"] = "python"
            stack["port"] = 8000
            if (project_dir / "app.py").exists():
                stack["entrypoint"] = "app.py"
            elif (project_dir / "main.py").exists():
                stack["entrypoint"] = "main.py"
        elif (project_dir / "Cargo.toml").exists():
            stack["language"] = "rust"
            stack["port"] = 8080
        elif (project_dir / "go.mod").exists():
            stack["language"] = "golang"
            stack["port"] = 8080

        return stack

    def generate_dockerfile(self, project_dir: Path) -> Tuple[str, Path]:
        """Genera un Dockerfile multi-etapa ultra optimizado para el proyecto."""
        stack = self.detect_project_stack(project_dir)
        lang = stack["language"]
        port = stack["port"]
        dockerfile_path = project_dir / "Dockerfile"

        if lang == "python":
            content = f"""# Dockerfile ultra optimizado generado por NovaCode Docker Pilot
FROM python:3.12-slim AS builder

WORKDIR /app
COPY requirements.txt* ./
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir --user -r requirements.txt; fi

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . /app

ENV PATH=/root/.local/bin:$PATH \\
    PYTHONUNBUFFERED=1

EXPOSE {port}
USER 1001

CMD ["python", "{stack.get('entrypoint') or 'main.py'}"]
"""
        elif lang == "nodejs":
            content = f"""# Dockerfile multi-etapa generado por NovaCode Docker Pilot
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN if npm run | grep -q "build"; then npm run build; fi

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app ./
EXPOSE {port}
USER node
CMD ["npm", "start"]
"""
        else:
            content = f"""# Dockerfile universal generado por NovaCode Docker Pilot
FROM alpine:latest
RUN apk add --no-cache bash curl
WORKDIR /app
COPY . .
EXPOSE {port}
CMD ["sh", "-c", "echo 'NovaCode Container Ready' && sleep infinity"]
"""
        dockerfile_path.write_text(content.strip() + "\n", encoding="utf-8")
        return content, dockerfile_path

    def generate_compose(self, project_dir: Path, service_name: str = "app") -> Tuple[str, Path]:
        """Genera un docker-compose.yml completo con networking y volúmenes."""
        stack = self.detect_project_stack(project_dir)
        port = stack["port"]
        compose_path = project_dir / "docker-compose.yml"

        content = f"""version: '3.8'

services:
  {service_name}:
    build: .
    container_name: {service_name}-service
    restart: unless-stopped
    ports:
      - "{port}:{port}"
    environment:
      - NODE_ENV=production
      - PORT={port}
    networks:
      - novacode-net

networks:
  novacode-net:
    driver: bridge
"""
        compose_path.write_text(content.strip() + "\n", encoding="utf-8")
        return content, compose_path

    def audit_dockerfile(self, dockerfile_path: Path) -> Dict[str, Any]:
        """Audita un Dockerfile en busca de malas prácticas o vulnerabilidades de seguridad."""
        if not dockerfile_path.exists():
            return {"valid": False, "error": "Dockerfile no existe"}

        text = dockerfile_path.read_text(encoding="utf-8")
        issues = []

        if ":latest" in text:
            issues.append("Uso de tag ':latest' sin versión fijada (puede causar incompatibilidades).")
        if "USER root" in text or ("USER" not in text and "USER " not in text):
            issues.append("El contenedor se ejecuta como root (riesgo de seguridad).")
        if re.search(r"(SECRET|API_KEY|PASSWORD|TOKEN)\s*=", text, re.IGNORECASE):
            issues.append("Posible secreto o credencial hardcodeada en el Dockerfile.")

        return {
            "valid": True,
            "issues_count": len(issues),
            "issues": issues,
            "is_secure": len(issues) == 0,
        }
