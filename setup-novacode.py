#!/usr/bin/env python3
"""NovaCode Super Subagents & Ultra-Fast Direct Thinking Setup."""
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

CLEAN_SHORT_MODELS = {
    "nova": {
        "id": "meta/llama-3.2-11b-vision-instruct",
        "name": "Nova Super Fast",
        "limit": {"context": 131072, "output": 8192},
    },
    "apex": {
        "id": "meta/llama-3.2-90b-vision-instruct",
        "name": "Nova Apex 90B",
        "limit": {"context": 131072, "output": 8192},
    },
    "jet": {
        "id": "meta/llama-3.2-11b-vision-instruct",
        "name": "Nova Jet Lightning",
        "limit": {"context": 65536, "output": 8192},
    },
    "dev": {
        "id": "nvidia/nemotron-3-nano-30b-a3b",
        "name": "Nova Dev Fast",
        "limit": {"context": 65536, "output": 8192},
    },
    "pulse": {
        "id": "nvidia/nemotron-3-nano-30b-a3b",
        "name": "Nova Pulse Reasoner",
        "limit": {"context": 65536, "output": 8192},
    },
    "iris": {
        "id": "meta/llama-3.2-90b-vision-instruct",
        "name": "Nova Iris Vision",
        "limit": {"context": 131072, "output": 8192},
    },
    "pro": {
        "id": "meta/llama-3.2-90b-vision-instruct",
        "name": "Nova Pro 90B",
        "limit": {"context": 131072, "output": 8192},
    },
    "lite": {
        "id": "nvidia/nemotron-3-nano-30b-a3b",
        "name": "Nova Lite Ultra-Fast",
        "limit": {"context": 32768, "output": 4096},
    },
    "diffusion": {
        "id": "google/diffusiongemma-26b-a4b-it",
        "name": "Nova Diffusion Gemma",
        "limit": {"context": 32768, "output": 4096},
    },
}


def build_models() -> dict:
    out = {}
    for key, spec in CLEAN_SHORT_MODELS.items():
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
        "env": ["NVIDIA_API_KEY"],
        "options": {
            "baseURL": "http://127.0.0.1:18791/v1",
            "timeout": 120000,
            "headerTimeout": 30000,
            "chunkTimeout": 60000,
            "retryAttempts": 3,
            "retryDelay": 1000,
            "maxRetries": 3,
            "retryBackoff": True,
            "connectionPoolSize": 6,
            "keepAlive": True,
            "keepAliveTimeout": 30000,
            "threadPoolSize": 4,
            "batchSize": 2,
            "disableChunkedEncoding": False,
            "decompressResponse": True,
        },
        "models": models,
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
        "enabled_providers": ["novacode"],
        "disabled_providers": ["openrouter", "huggingface", "nvidia"],
        "provider": {"novacode": novacode_provider},
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


def main() -> None:
    write_configs()


if __name__ == "__main__":
    main()
