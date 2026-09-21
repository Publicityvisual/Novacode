#!/usr/bin/env python3
"""
HYBRID OLLAMA - Wrapper híbrido online/offline
Funciona con proveedores locales y APIs online.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict

# Añadir hybrid al path
sys.path.insert(0, str(Path.home() / ".novacode/hybrid"))
from hybrid_router import get_hybrid_router


class HybridOllama:
    """Wrapper híbrido de Ollama"""

    def __init__(self):
        self.router = get_hybrid_router()
        self.default_task = "general"

    def run(self, prompt: str, task_type: str = None, force_provider: str = None) -> Dict:
        """
        Ejecuta consulta con mejor proveedor disponible.
        Si force_provider se indica, se respeta directamente.
        """
        task = task_type or self.default_task

        if force_provider:
            providers = self.router.config.get("providers", {})
            forced = providers.get(force_provider)
            if not forced:
                return {
                    "error": f"Proveedor '{force_provider}' no configurado",
                    "provider": None,
                    "model": None
                }
            model = self.router._pick_model(forced.get("models", {}), task)
            if not model:
                return {
                    "error": f"Proveedor '{force_provider}' sin modelo para tarea '{task}'",
                    "provider": force_provider,
                    "model": None
                }
            if forced.get("type") == "local":
                return self._run_local(prompt, {
                    "model": model,
                    "provider": force_provider,
                    "type": "local"
                })
            return self._run_api(prompt, {
                "model": model,
                "provider": force_provider,
                "type": "api",
                "url": self.router._resolve_api_url(forced),
                "api_key": os.getenv(forced.get("env_key", ""))
            })

        # Obtener mejor proveedor
        provider_id, provider_config = self.router.get_best_provider(task)

        if provider_id == "none":
            return {
                "error": "No hay proveedores disponibles",
                "provider": None,
                "model": None
            }

        # Ejecutar según tipo
        if provider_config.get("type") == "local":
            return self._run_local(prompt, provider_config)
        else:
            return self._run_api(prompt, provider_config)

    def _run_local(self, prompt: str, config: Dict) -> Dict:
        """Ejecuta modelo local"""
        model = config.get("model", "nexus-think:latest")

        try:
            result = subprocess.run(
                ["ollama", "run", model, prompt],
                capture_output=True,
                text=True,
                timeout=300
            )
            return {
                "provider": "ollama_local",
                "model": model,
                "response": result.stdout,
                "error": None
            }
        except subprocess.TimeoutExpired:
            return {
                "provider": "ollama_local",
                "model": model,
                "response": None,
                "error": "Timeout"
            }
        except Exception as e:
            return {
                "provider": "ollama_local",
                "model": model,
                "response": None,
                "error": str(e)
            }

    def _run_api(self, prompt: str, config: Dict) -> Dict:
        """Ejecuta API online"""
        import urllib.request
        import urllib.error

        url = config.get("url")
        api_key = config.get("api_key")
        model = config.get("model")

        if not url or not api_key or not model:
            return {
                "provider": config.get("provider"),
                "model": model,
                "response": None,
                "error": "Configuración incompleta"
            }

        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 2048,
            "temperature": 0.7
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode('utf-8'),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {api_key}'
                },
                method='POST'
            )

            with urllib.request.urlopen(req, timeout=config.get("timeout", 60)) as response:
                data = json.loads(response.read().decode('utf-8'))
                return {
                    "provider": config.get("provider"),
                    "model": model,
                    "response": data.get("choices", [{}])[0].get("message", {}).get("content"),
                    "error": None
                }
        except urllib.error.HTTPError as e:
            return {
                "provider": config.get("provider"),
                "model": model,
                "response": None,
                "error": f"HTTP {e.code}: {e.reason}"
            }
        except Exception as e:
            return {
                "provider": config.get("provider"),
                "model": model,
                "response": None,
                "error": str(e)
            }

    def get_status(self) -> Dict:
        """Estado de todos los proveedores"""
        return self.router.get_status()


# Instancia global
_hybrid = None


def get_hybrid_ollama() -> HybridOllama:
    """Singleton"""
    global _hybrid
    if _hybrid is None:
        _hybrid = HybridOllama()
    return _hybrid


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Hybrid Ollama - wrapper híbrido online/offline"
    )
    parser.add_argument(
        "--online", nargs="?", const=True, default=False, metavar="PROMPT",
        help="Modo online (APIs externas). Acepta prompt opcional."
    )
    parser.add_argument(
        "--offline", nargs="?", const=True, default=False, metavar="PROMPT",
        help="Modo offline (solo modelos locales). Acepta prompt opcional."
    )
    parser.add_argument("--task", default="general", help="Tipo de tarea (default: general)")
    parser.add_argument("--provider", default=None, help="Forzar proveedor por id")
    parser.add_argument("prompt", nargs="*", help="Prompt posicional")
    return parser


def print_status(hybrid: HybridOllama) -> None:
    print("🔍 Estado de proveedores:")
    status = hybrid.get_status()
    for provider, info in status.items():
        print(f"  {provider}: {'✅' if info['available'] else '❌'} ({info['type']}, priority {info['priority']})")


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    hybrid = get_hybrid_ollama()

    prompt_parts = list(args.prompt or [])
    if isinstance(args.online, str) and args.online:
        prompt_parts.insert(0, args.online)
    if isinstance(args.offline, str) and args.offline:
        prompt_parts.insert(0, args.offline)
    prompt_text = " ".join(prompt_parts).strip()

    force_provider = args.provider
    if args.offline is not False and not force_provider:
        force_provider = "ollama_local"

    # Sin prompt: comportamiento legacy (status + test), backward compatible.
    if not prompt_text:
        print_status(hybrid)
        print("\n🧪 Test de consulta:")
        result = hybrid.run("Hola, ¿estás funcionando?", task_type=args.task, force_provider=force_provider or None)
        print(f"Proveedor: {result.get('provider')}")
        print(f"Modelo: {result.get('model')}")
        print(f"Respuesta: {result.get('response', result.get('error'))}")
        return 0

    result = hybrid.run(prompt_text, task_type=args.task, force_provider=force_provider or None)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
