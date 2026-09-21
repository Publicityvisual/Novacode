#!/usr/bin/env python3
"""
HYBRID ROUTER - Sistema de enrutamiento híbrido online/offline
Selecciona automáticamente el mejor proveedor según disponibilidad.
"""

import json
import os
import urllib.request
from pathlib import Path
from typing import Dict, Tuple
from enum import Enum

NVIDIA_DEFAULT_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

# Normalización de tipos de tarea hacia claves reales de providers.json.
# providers.json solo define: multimodal / code / fast / general / vision.
TASK_ALIASES: Dict[str, str] = {
    "thinking": "general",
    "analysis": "general",
    "creative": "general",
    "technical": "code",
    "vision": "multimodal",
}


class ProviderType(Enum):
    LOCAL = "local"
    API = "api"


class HybridRouter:
    """Router híbrido que combina online y offline"""

    def __init__(self, config_path: str = None):
        self.config_path = Path(config_path or os.path.expanduser("~/.novacode/hybrid/providers.json"))
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # Cargar configuración
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = self._default_config()

        # Estado de proveedores
        self.provider_status: Dict[str, bool] = {}
        self._check_all_providers()

    def _default_config(self) -> Dict:
        """Configuración por defecto"""
        return {
            "providers": {
                "ollama_local": {
                    "enabled": True,
                    "type": "local",
                    "url": "http://localhost:11434",
                    "priority": 1
                }
            },
            "routing": {
                "prefer_local": True,
                "fallback_to_online": True,
                "check_interval": 30,
                "timeout": 60
            }
        }

    def _resolve_api_url(self, provider_config: Dict) -> str:
        """Resuelve la URL de un proveedor API, con soporte Nvidia vía env."""
        url = provider_config.get("url")
        if url:
            return url
        if provider_config.get("env_key") == "NVIDIA_API_KEY":
            return os.getenv("NVIDIA_BASE_URL", NVIDIA_DEFAULT_URL)
        return ""

    def _check_provider(self, provider_id: str, provider_config: Dict) -> bool:
        """Verifica si un proveedor está disponible"""
        provider_type = provider_config.get("type")

        if provider_type == "local":
            try:
                base = provider_config.get("url", "http://localhost:11434").rstrip("/")
                req = urllib.request.urlopen(f"{base}/api/tags", timeout=2)
                return req.status == 200
            except Exception:
                return False

        elif provider_type == "api":
            env_key = provider_config.get("env_key")
            if not env_key:
                return False

            api_key = os.getenv(env_key)
            if not api_key:
                return False

            if provider_id == "nvidia":
                try:
                    url = self._resolve_api_url(provider_config)
                    req = urllib.request.urlopen(
                        urllib.request.Request(
                            url,
                            data=json.dumps({
                                "model": "nvidia/llama-3.1-nemotron-70b-instruct",
                                "messages": [{"role": "user", "content": "ping"}],
                                "max_tokens": 1,
                            }).encode("utf-8"),
                            headers={
                                "Content-Type": "application/json",
                                "Authorization": f"Bearer {api_key}",
                            },
                            method="POST",
                        ),
                        timeout=10,
                    )
                    return req.status == 200
                except Exception:
                    return False

            return True

        return False

    def _check_all_providers(self) -> None:
        """Verifica todos los proveedores"""
        try:
            providers = self.config.get("providers", {})
        except Exception:
            providers = {}
        for provider_id, provider_config in providers.items():
            try:
                if provider_config.get("enabled", False):
                    self.provider_status[provider_id] = self._check_provider(
                        provider_id, provider_config
                    )
                else:
                    self.provider_status[provider_id] = False
            except Exception:
                self.provider_status[provider_id] = False

    @staticmethod
    def _normalize_task(task_type: str) -> str:
        """Mapea alias de tarea a claves reales de providers.json."""
        return TASK_ALIASES.get(task_type, task_type)

    @staticmethod
    def _pick_model(models: Dict, task_type: str) -> str:
        """
        Elige modelo para una tarea con fallback:
        1) clave exacta, 2) clave normalizada, 3) 'general', 4) primer modelo.
        Retorna cadena vacía si no hay modelos.
        """
        if not models:
            return ""
        if task_type in models:
            return models[task_type]
        canonical = HybridRouter._normalize_task(task_type)
        if canonical in models:
            return models[canonical]
        if "general" in models:
            return models["general"]
        return next(iter(models.values()))

    def get_best_provider(self, task_type: str) -> Tuple[str, Dict]:
        """
        Obtiene el mejor proveedor para una tarea.
        Prefiere local, fallback a online. Nunca retorna 'none'
        si hay ollama_local configurado.
        """
        providers = self.config.get("providers", {})
        routing = self.config.get("routing", {})

        # Ordenar por prioridad
        sorted_providers = sorted(
            providers.items(),
            key=lambda x: x[1].get("priority", 999)
        )

        # Si prefiere local, intentar primero
        if routing.get("prefer_local", True):
            local_provider = providers.get("ollama_local")
            if local_provider and self.provider_status.get("ollama_local", False):
                model = self._pick_model(local_provider.get("models", {}), task_type)
                if model:
                    return "ollama_local", {
                        "model": model,
                        "provider": "ollama_local",
                        "type": "local"
                    }

        # Fallback a online
        if routing.get("fallback_to_online", True):
            for provider_id, provider_config in sorted_providers:
                if provider_id == "ollama_local":
                    continue

                if self.provider_status.get(provider_id, False):
                    model = self._pick_model(provider_config.get("models", {}), task_type)
                    if model:
                        return provider_id, {
                            "model": model,
                            "provider": provider_id,
                            "type": "api",
                            "url": self._resolve_api_url(provider_config),
                            "api_key": os.getenv(provider_config.get("env_key", ""))
                        }

        # Fallback final a local aunque el health-check haya fallado:
        # si ollama_local está configurado, nunca retornar "none".
        local_provider = providers.get("ollama_local")
        if local_provider:
            model = self._pick_model(local_provider.get("models", {}), task_type)
            if model:
                return "ollama_local", {
                    "model": model,
                    "provider": "ollama_local",
                    "type": "local",
                    "fallback": True
                }

        # Sin proveedores disponibles
        return "none", {}

    def get_status(self) -> Dict:
        """Estado de todos los proveedores"""
        try:
            providers_cfg = self.config.get("providers", {})
        except Exception:
            providers_cfg = {}
        status: Dict[str, Dict] = {}
        for provider_id, available in self.provider_status.items():
            cfg = providers_cfg.get(provider_id, {})
            status[provider_id] = {
                "available": available,
                "type": cfg.get("type"),
                "priority": cfg.get("priority")
            }
        return status


# Instancia global
_router = None


def get_hybrid_router() -> HybridRouter:
    """Singleton"""
    global _router
    if _router is None:
        _router = HybridRouter()
    return _router
