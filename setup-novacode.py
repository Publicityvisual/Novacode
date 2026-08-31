#!/usr/bin/env python3
"""Novacode Super Subagents & Ultra-Fast Direct Thinking Setup."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
SHARE = HOME / ".local" / "share" / "novacode"
ENGINE = SHARE / "engine"
LIBEXEC = ENGINE / "libexec"
BIN_DIR = HOME / ".local" / "bin"
CONFIG_NC = HOME / ".config" / "novacode"
CONFIG_NOVA = HOME / ".config" / "nova"
ICONS = SHARE / "icons"

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
        "id": "nvidia/nemotron-3-super-120b-a12b",
        "name": "Nova Super 120B",
        "limit": {"context": 131072, "output": 8192},
    },
    "apex": {
        "id": "nvidia/nemotron-3-ultra-550b-a55b",
        "name": "Nova Apex 550B",
        "limit": {"context": 262144, "output": 8192},
    },
    "jet": {
        "id": "nvidia/nemotron-3-nano-30b-a3b",
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
        "id": "meta/llama-3.2-11b-vision-instruct",
        "name": "Nova Iris Vision",
        "limit": {"context": 131072, "output": 8192},
    },
    "pro": {
        "id": "nvidia/nemotron-3-super-120b-a12b",
        "name": "Nova Pro 120B",
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
        "api": "https://integrate.api.nvidia.com/v1",
        "env": ["NVIDIA_API_KEY"],
        "options": {
            "baseURL": "https://integrate.api.nvidia.com/v1",
            "timeout": 300000,
            "headerTimeout": 60000,
            "chunkTimeout": 120000,
            "retryAttempts": 2,
            "retryDelay": 3000,
            "maxRetries": 2,
            "retryBackoff": True,
            "connectionPoolSize": 2,
            "keepAlive": True,
            "keepAliveTimeout": 30000,
            "threadPoolSize": 1,
            "batchSize": 1,
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
        "security": {"model": "novacode/wild", "permission": "allow"},
        "pentest": {"model": "novacode/raw", "permission": "allow"},
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
        }
    }


def write_text(path: Path, content: str, mode: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    if mode is not None:
        path.chmod(mode)


def write_configs() -> None:
    cfg = build_config()
    text = json.dumps(cfg, indent=2, ensure_ascii=False) + "\n"
    write_text(CONFIG_NC / "novacode.jsonc", text)
    print("wrote", CONFIG_NC / "novacode.jsonc")
    write_text(CONFIG_NOVA / "nova.jsonc", text)
    print("wrote", CONFIG_NOVA / "nova.jsonc")


def write_wrappers() -> None:
    launcher = """#!/usr/bin/env bash
# Novacode CLI — NVIDIA NIM professional models, branded TUI.
set -euo pipefail

export COLORTERM="${COLORTERM:-truecolor}"
export FORCE_COLOR="${FORCE_COLOR:-1}"
export LANG="${LANG:-es_MX.UTF-8}"
export LC_ALL="${LC_ALL:-es_MX.UTF-8}"
export UV_THREADPOOL_SIZE="${UV_THREADPOOL_SIZE:-4}"
export BUN_JSC_forceRAMSize="${BUN_JSC_forceRAMSize:-2147483648}"

ROOT="${NOVACODE_ROOT:-$HOME/.local/share/novacode/engine}"
BIN="$ROOT/libexec/nova"
EDITOR_BIN="${NOVACODE_EDITOR:-$HOME/.local/share/novacode/editor.py}"

load_env() {
  local f
  for f in \\
    "$HOME/.config/nova/secrets.env" \\
    "$HOME/.config/env/nvidia.env"
  do
    if [[ -f "$f" ]]; then
      set -a
      # shellcheck disable=SC1090
      source "$f"
      set +a
    fi
  done
}

load_env

export NOVACODE_APP_NAME="Novacode"
export NOVACODE_CLIENT="cli"
export NOVACODE_TREE_SITTER_WASM_DIR="${NOVACODE_TREE_SITTER_WASM_DIR:-$ROOT/libexec/tree-sitter}"
if [[ -d "$ROOT/libexec/console" ]]; then
  export NOVACODE_CONSOLE_ASSET_DIR="${NOVACODE_CONSOLE_ASSET_DIR:-$ROOT/libexec/console}"
fi
export NOVACODE_CONFIG="${NOVACODE_CONFIG:-$HOME/.config/novacode/novacode.jsonc}"
export NOVACODE_DISABLE_MODELS_FETCH=1
export NOVACODE_DISABLE_AUTOUPDATE=1
export NOVACODE_DISABLE_TELEMETRY=1
export NOVACODE_TELEMETRY_LEVEL="off"
export TELEMETRY_DISABLED=1
export OTEL_SDK_DISABLED=true
export DO_NOT_TRACK=1
export NOVA_DISABLE_MODELS_FETCH=1
export NOVA_DISABLE_AUTOUPDATE=1
export NOVA_TELEMETRY_LEVEL="off"
export NOVA_APP_NAME="Novacode"
export NOVA_MODELS_URL="http://127.0.0.1:18791/v1/models"
export NOVACODE_MODELS_URL="http://127.0.0.1:18791/v1/models"
export NOVACODE_NVIDIA_PROFESSIONAL=1

cmd="${1:-}"
case "$cmd" in
  python|py|swarm|sandbox|sentinel|graph|canvas|refactor|sync|bench|docker|api|net|secret|auto)
    shift
    export PYTHONPATH="$HOME/.local/share/novacode:$HOME/novacode-cli:${PYTHONPATH:-}"
    exec python3 "$HOME/.local/share/novacode/nova.py" "$cmd" "$@"
    ;;
  sudo)
    shift
    export PYTHONPATH="$HOME/.local/share/novacode:$HOME/novacode-cli:${PYTHONPATH:-}"
    exec python3 "$HOME/.local/share/novacode/nova.py" sudo "$@"
    ;;
  forge)
    shift
    export PYTHONPATH="$HOME/.local/share/novacode:$HOME/novacode-cli:${PYTHONPATH:-}"
    exec python3 "$HOME/.local/share/novacode/nova.py" forge "$@"
    ;;
  editor)
    shift
    exec python3 "$EDITOR_BIN" "$@"
    ;;
  doctor)
    shift
    exec python3 "$HOME/.local/share/novacode/doctor.py" "$@"
    ;;
  setup|repair)
    shift
    exec python3 "$HOME/.local/share/novacode/setup-novacode.py" "$@"
    ;;
  mm-proxy)
    shift
    exec "$HOME/.local/bin/nova-mm-proxy" "$@"
    ;;
  gen|generate|imagine|image|img|video|audio|music|tts|nsfw|uncensored|omni|studio)
    GEN="$HOME/.local/share/novacode/generate.py"
    if [[ ! -f "$GEN" ]]; then
      GEN="$HOME/novacode-cli/generate.py"
    fi
    exec python3 "$GEN" "$@"
    ;;
  nova|super|chat|code|analyze|learn|evolve|models|security|test|docs)
    exec python3 "$HOME/.local/share/novacode/nova.py" "$@"
    ;;
esac

if [[ ! -x "$BIN" ]]; then
  echo "Novacode engine not found: $BIN" >&2
  echo "Ejecuta: python3 $HOME/.local/share/novacode/setup-novacode.py" >&2
  exit 1
fi

# Auto-start resilient anti-overload proxy if not running
if ! nc -z 127.0.0.1 18791 2>/dev/null; then
  nohup python3 "$HOME/.local/share/novacode/mm-proxy.py" >/dev/null 2>&1 &
  sleep 0.2
fi

# Si el usuario pide modelo local uncensored/NSFW, levanta llama-server
if [[ "$*" == *uncensored* || "$*" == *nsfw* || "$*" == *local/* ]]; then
  python3 "$HOME/.local/share/novacode/generate.py" serve --daemon >/dev/null 2>&1 || true
fi

exec -a novacode "$BIN" "$@"
"""
    for name in ["novacode", "nova"]:
        p = BIN_DIR / name
        write_text(p, launcher, 0o755)
    print("wrappers ready")


def patch_novacode_ascii_logo(bin_path: Path) -> bool:
    if not bin_path.exists():
        return False
    data = bin_path.read_bytes()
    idx1 = data.find(b"cS1=")
    idx2 = data.find(b",MS1=")
    if idx1 == -1 or idx2 == -1:
        return False

    total_len = idx2 - idx1
    tui_lines = [
        "      ███╗   ██╗ ██████╗ ██╗   ██╗ █████╗  ██████╗ ██████╗ ██████╗ ███████╗",
        "      ████╗  ██║██╔═══██╗██║   ██║██╔══██╗██╔════╝██╔═══██╗██╔══██╗██╔════╝",
        "      ██╔██╗ ██║██║   ██║██║   ██║███████║██║     ██║   ██║██║  ██║█████╗  ",
        "      ██║╚██╗██║██║   ██║╚██╗ ██╔╝██╔══██║██║     ██║   ██║██║  ██║██╔══╝  ",
        "      ██║ ╚████║╚██████╔╝ ╚████╔╝ ██║  ██║╚██████╗╚██████╔╝██████╔╝███████╗",
        "      ╚═╝  ╚═══╝ ╚═════╝   ╚═══╝  ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝",
        "                     ───  ◆  N O V A C O D E   C L I  ◆  ───               ",
    ]
    exit_lines = [
        "███╗  ██╗",
        "████╗ ██║",
        "██╔██╗██║",
    ]
    tui_json = json.dumps(tui_lines, ensure_ascii=False)
    exit_json = json.dumps(exit_lines, ensure_ascii=False)
    js_expr = f"cS1=(()=>{{let T={tui_json},E={exit_json};return {{tui:T,plain:T,exit:E}}}})()"
    raw_expr = js_expr.encode("utf-8")
    pad_needed = total_len - len(raw_expr)
    if pad_needed < 4:
        return False
    pad = b"/*" + b" " * (pad_needed - 4) + b"*/"
    new_block = raw_expr + pad
    new_data = data[:idx1] + new_block + data[idx2:]
    
    new_data = new_data.replace(b"if(H===\"_\")", b"if(H===\"\\x00\")")
    new_data = new_data.replace(b"\"Nova CLI\"", b"\"Novacode\"")
    new_data = new_data.replace(b"Nova CLI ", b"Novacode ")
    
    t_start = b"function BgR(){let{theme:A}=a9()"
    t_end = b"var jAh;var $gR="
    i1 = new_data.find(t_start)
    i2 = new_data.find(t_end, i1)
    if i1 != -1 and i2 != -1:
        o_len = i2 - i1
        n_js = r"""function BgR(){let{theme:A}=a9(),C=["#00F0FF","#00C8FF","#3896FF","#7864FF","#A855F7","#C084FC","#E0E7FF"].map($j.fromHex),j=IHT(),R=(q,c)=>{var G=rA("text");return s(G,"fg",c),s(G,"selectable",!1),b0(G,q),G};return(()=>{var q=rA("box");s(q,"alignItems","center");return b0(q,N0(A8,{each:j,children:(B,I)=>(()=>{let idx=typeof I==="function"?I():(I||0),c=C[idx]||C[0],h=rA("box");return s(h,"flexDirection","row"),b0(h,()=>R(B,c)),h})()})),q})()}"""
        raw_n = n_js.encode("utf-8")
        if o_len >= len(raw_n) + 4:
            p_pad = b"/*" + b" " * (o_len - len(raw_n) - 4) + b"*/"
            new_data = new_data[:i1] + raw_n + p_pad + new_data[i2:]
            
    bin_path.write_bytes(new_data)
    subprocess.run(["codesign", "--force", "--sign", "-", "--timestamp=none", str(bin_path)], check=True)
    return True


def patch_engine() -> bool:
    target = LIBEXEC / "nova"
    if not target.exists():
        return False
    return patch_novacode_ascii_logo(target)


def main() -> int:
    print("=== Novacode Super Subagents Setup ===")
    write_configs()
    write_wrappers()
    patch_engine()
    print("=== done ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
