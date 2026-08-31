#!/usr/bin/env python3
"""NovaCode Multi-Modal Ultra-Fast Unrestricted Engine Configuration."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
SHARE = HOME / ".local" / "share" / "novacode"
BIN_DIR = HOME / ".local" / "bin"
CONFIG_NC = HOME / ".config" / "novacode"

def get_key(env_var: str, default_path: str = "") -> str:
    key = os.environ.get(env_var, "").strip()
    if key:
        return key
    auth_file = Path.home() / ".local" / "share" / "novacode" / "auth.json"
    if auth_file.exists():
        try:
            data = json.loads(auth_file.read_text())
            for k in ["novacode", "nvidia", "openrouter"]:
                if k in data and data[k].get("key"):
                    if env_var == "NVIDIA_API_KEY" and "nvapi" in data[k]["key"]:
                        return data[k]["key"]
                    if env_var == "OPENROUTER_API_KEY" and "sk-or" in data[k]["key"]:
                        return data[k]["key"]
        except Exception:
            pass
    return ""

NVIDIA_KEY = get_key("NVIDIA_API_KEY")
OPENROUTER_KEY = get_key("OPENROUTER_API_KEY")

FLAGSHIP_POWER_SPEC = {
    "tool_call": True,
    "temperature": True,
    "attachment": True,
    "reasoning": True,
    "cost": {"input": 0, "output": 0, "cache_read": 0},
    "modalities": {
        "input": ["text", "image", "audio", "video"],
        "output": ["text"],
    },
}

CLEAN_MODELS = {
    "nova": {
        "id": "meta/llama-3.2-11b-vision-instruct",
        "name": "NovaCode Super Vision (128K)",
        "limit": {"context": 131072, "output": 16384},
    },
    "apex": {
        "id": "meta/llama-3.2-90b-vision-instruct",
        "name": "NovaCode Apex 90B Multimodal (128K)",
        "limit": {"context": 131072, "output": 16384},
    },
    "jet": {
        "id": "meta/llama-3.2-11b-vision-instruct",
        "name": "NovaCode Jet Lightning (64K)",
        "limit": {"context": 65536, "output": 16384},
    },
    "dev": {
        "id": "nvidia/nemotron-3-nano-30b-a3b",
        "name": "NovaCode Dev Fast (64K)",
        "limit": {"context": 65536, "output": 8192},
    },
    "pulse": {
        "id": "nvidia/nemotron-3-nano-30b-a3b",
        "name": "NovaCode Pulse Reasoner (64K)",
        "limit": {"context": 65536, "output": 8192},
    },
    "iris": {
        "id": "meta/llama-3.2-90b-vision-instruct",
        "name": "NovaCode Iris Vision & Media (128K)",
        "limit": {"context": 131072, "output": 16384},
    },
    "pro": {
        "id": "meta/llama-3.2-90b-vision-instruct",
        "name": "NovaCode Pro 90B Architect (128K)",
        "limit": {"context": 131072, "output": 16384},
    },
    "lite": {
        "id": "nvidia/nemotron-3-nano-30b-a3b",
        "name": "NovaCode Lite Ultra-Fast (64K)",
        "limit": {"context": 65536, "output": 8192},
    },
    "uncensored": {
        "id": "novacode-uncensored",
        "name": "NovaCode Unrestricted Local Abliterated (32K)",
        "limit": {"context": 32768, "output": 4096},
    },
    "omni": {
        "id": "meta/llama-3.2-90b-vision-instruct",
        "name": "NovaCode Omni Studio (128K)",
        "limit": {"context": 131072, "output": 16384},
    },
}


def build_models() -> dict:
    out = {}
    for key, spec in CLEAN_MODELS.items():
        item = dict(FLAGSHIP_POWER_SPEC)
        item.update(spec)
        out[key] = item
    return out


def build_config() -> dict:
    models = build_models()

    novacode_provider = {
        "npm": "@ai-sdk/openai-compatible",
        "name": "Novacode",
        "api": "http://127.0.0.1:18791/v1",
        "env": ["NVIDIA_API_KEY", "OPENROUTER_API_KEY"],
        "options": {
            "baseURL": "http://127.0.0.1:18791/v1",
            "timeout": 120000,
            "headerTimeout": 30000,
            "chunkTimeout": 60000,
            "retryAttempts": 4,
            "retryDelay": 1000,
            "maxRetries": 4,
            "retryBackoff": True,
            "connectionPoolSize": 8,
            "keepAlive": True,
            "keepAliveTimeout": 60000,
            "threadPoolSize": 6,
            "batchSize": 4,
            "disableChunkedEncoding": False,
            "decompressResponse": True,
        },
        "models": models,
    }

    openrouter_provider = {
        "npm": "@ai-sdk/openai-compatible",
        "name": "OpenRouter",
        "api": "https://openrouter.ai/api/v1",
        "env": ["OPENROUTER_API_KEY"],
        "options": {
            "baseURL": "https://openrouter.ai/api/v1",
            "timeout": 120000,
            "retryAttempts": 3,
        },
        "models": {
            "llama-70b": {
                "id": "meta-llama/llama-3.3-70b-instruct",
                "name": "Llama 3.3 70B Instruct",
                "limit": {"context": 131072, "output": 8192},
                **FLAGSHIP_POWER_SPEC,
            },
            "deepseek-r1": {
                "id": "deepseek/deepseek-r1",
                "name": "DeepSeek R1 Reasoning",
                "limit": {"context": 65536, "output": 8192},
                **FLAGSHIP_POWER_SPEC,
            },
            "qwen-coder": {
                "id": "qwen/qwen-2.5-coder-32b-instruct",
                "name": "Qwen 2.5 Coder 32B",
                "limit": {"context": 65536, "output": 8192},
                **FLAGSHIP_POWER_SPEC,
            },
        },
    }

    ollama_provider = {
        "npm": "@ai-sdk/openai-compatible",
        "name": "Ollama",
        "api": "http://127.0.0.1:11434/v1",
        "options": {
            "baseURL": "http://127.0.0.1:11434/v1",
            "timeout": 180000,
        },
        "models": {
            "local": {
                "id": "llama3.2:latest",
                "name": "Ollama Local",
                "limit": {"context": 32768, "output": 4096},
                **FLAGSHIP_POWER_SPEC,
            }
        },
    }

    agents = {
        "code": {"model": "novacode/nova", "mode": "primary", "permission": "allow"},
        "clone": {"model": "novacode/jet", "permission": "allow"},
        "refactor": {"model": "novacode/dev", "permission": "allow"},
        "fullstack": {"model": "novacode/nova", "permission": "allow"},
        "autoheal": {"model": "novacode/jet", "permission": "allow"},
        "evolver": {"model": "novacode/nova", "permission": "allow"},
        "updater": {"model": "novacode/jet", "permission": "allow"},
        "guardian": {"model": "novacode/pro", "permission": "allow"},
        "study": {"model": "novacode/nova", "permission": "allow"},
        "analyst": {"model": "novacode/apex", "permission": "allow"},
        "swarm": {"model": "novacode/apex", "permission": "allow"},
        "tdd": {"model": "novacode/dev", "permission": "allow"},
        "memory": {"model": "novacode/lite", "permission": "allow"},
        "commit": {"model": "novacode/lite", "permission": "allow"},
        "scraper": {"model": "novacode/jet", "permission": "allow"},
        "turbo": {"model": "novacode/jet", "permission": "allow"},
        "build": {"model": "novacode/dev", "permission": "allow"},
        "fixer": {"model": "novacode/jet", "permission": "allow"},
        "architect": {"model": "novacode/apex", "permission": "allow"},
        "plan": {"model": "novacode/nova", "permission": "allow"},
        "security": {"model": "novacode/iris", "permission": "allow"},
        "pentest": {"model": "novacode/iris", "permission": "allow"},
        "explore": {"model": "novacode/jet", "permission": "allow"},
        "debugger": {"model": "novacode/dev", "permission": "allow"},
        "reviewer": {"model": "novacode/pro", "permission": "allow"},
        "ui": {"model": "novacode/iris", "permission": "allow"},
        "general": {"model": "novacode/jet", "permission": "allow"},
        "title": {"model": "novacode/lite", "permission": "allow"},
        "summary": {"model": "novacode/lite", "permission": "allow"},
        "compaction": {"model": "novacode/lite", "permission": "allow"},
        "orchestrator": {"model": "novacode/nova", "permission": "allow"},
    }

    return {
        "$schema": "https://novacode.ai/config.json",
        "username": "djkoveck",
        "snapshot": False,
        "autoupdate": False,
        "plugin": [],
        "model": "novacode/nova",
        "small_model": "novacode/lite",
        "default_agent": "code",
        "enabled_providers": ["novacode", "openrouter", "ollama"],
        "disabled_providers": ["huggingface"],
        "provider": {
            "novacode": novacode_provider,
            "openrouter": openrouter_provider,
            "ollama": ollama_provider,
        },
        "agent": agents,
        "permission": {
            "*": "allow",
            "bash": "allow",
            "read": "allow",
            "edit": "allow",
            "write": "allow",
            "delete": "allow",
            "glob": "allow",
            "grep": "allow",
            "list": "allow",
            "webfetch": "allow",
            "websearch": "allow",
            "external_directory": "allow",
            "task": "allow",
            "suggest": "allow",
            "question": "allow",
            "background_process": "allow",
            "interactive_terminal": "allow",
            "todowrite": "allow",
            "doom_loop": "allow",
            "skill": "allow",
            "lsp": "allow",
            "notebook_read": "allow",
            "notebook_edit": "allow",
            "notebook_execute": "allow",
            "repo_clone": "allow",
            "sudo": "allow",
            "docker": "allow",
            "forge": "allow",
            "sandbox": "allow",
            "sync": "allow",
            "network": "allow",
            "camera": "allow",
            "microphone": "allow",
        },
        "watcher": {
            "ignore": [
                "**/.git",
                "**/node_modules",
                "**/.Trash/**",
                "**/Library/**",
                "**/Pictures/**",
                "**/Music/**",
                "**/Movies/**",
                "**/Downloads/**",
                "**/Documents/**",
                "**/*.photoslibrary/**",
                "**/Applications/**",
                "**/.cache/**",
                "**/.local/**",
                "**/.npm/**",
                "**/.nvm/**",
                "**/.nova/**",
                "**/.novacode/**",
                "**/.vscode-oss/**",
                "**/.cursor/**",
                "**/.codex/**",
                "**/.cargo/**",
                "**/.rustup/**",
                "**/go/pkg/**",
                "**/__pycache__/**",
                "**/.DS_Store",
                "**/dist/**",
                "**/build/**",
                "**/.next/**",
                "**/.nuxt/**",
                "**/coverage/**",
            ]
        },
    }


def write_configs() -> None:
    CONFIG_NC.mkdir(parents=True, exist_ok=True)
    cfg = build_config()
    target = CONFIG_NC / "novacode.jsonc"
    with open(target, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
    print(f"\033[32m✓ Configuración de NovaCode escrita en:\033[0m {target}")

    # Write auth.json
    auth_data = {
        "novacode": {"type": "api", "key": NVIDIA_KEY},
        "nvidia": {"type": "api", "key": NVIDIA_KEY},
        "openrouter": {"type": "api", "key": OPENROUTER_KEY},
        "ollama": {"type": "api", "key": "ollama"},
    }
    for auth_path in [
        HOME / ".local" / "share" / "novacode" / "auth.json",
        HOME / ".local" / "share" / "opencode" / "auth.json",
    ]:
        auth_path.parent.mkdir(parents=True, exist_ok=True)
        with open(auth_path, "w", encoding="utf-8") as f:
            json.dump(auth_data, f, indent=2)
    print("\033[32m✓ Credenciales multi-proveedor escritas en auth.json\033[0m")


def main() -> None:
    write_configs()


if __name__ == "__main__":
    main()
