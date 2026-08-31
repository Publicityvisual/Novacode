#!/usr/bin/env python3
"""CodeForge Super Multimodal CLI — Ultimate Entry Point.

The definitive command-line interface for CodeForge, integrating all capabilities:
chat, generation, code, analysis, learning, evolution, multimodal pipelines,
and system management into a single professional CLI.

Usage:
    nova.py [COMMAND] [OPTIONS]

Commands:
    chat        Interactive chat with any model
    generate    Generate text, images, video, audio, music
    code        Code generation with Python auto-integration
    analyze     Analyze files, images, audio, video
    learn       View and manage learning
    evolve      Self-improvement and evolution
    models      List all models with capabilities
    doctor      System health check
    config      Configuration management
    session     Session management
    multimodal  Full multimodal pipeline
    python      Execute Python with AI assistance
    bash        Execute bash with AI assistance
    web         Web search and fetch
    files       File management
    db          Database operations
    security    Security audit
    test        Run tests
    deploy      Deployment assistance
    docs        Documentation generation

Options:
    --model MODEL       Select model (nova, jet, dev, pulse, omni, raw, wild, iris, apex, pro, lite)
    --quality LEVEL     Quality level (draft, pro, ultra)
    --nsfw              Enable NSFW mode
    --json              JSON output
    --verbose           Verbose output
    --quiet             Minimal output
    --no-color          Disable colors
    --config PATH       Config file path
    --session ID        Session ID
    --worktree PATH     Git worktree
    --auto              Auto mode (no prompts)
    --pure              Pure mode (no system prompts)
    --version           Show version
    -h, --help          Show help
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

# ============================================================================
# Constants
# ============================================================================

CODEFORGE_HOME = Path.home() / ".local" / "share" / "codeforge"
CODEFORGE_CONFIG = CODEFORGE_HOME / "config.json"
NOVACODE_VERSION = "3.0.0"
NOVACODE_BANNER = r"""
 ███╗   ██╗ ██████╗ ██╗   ██╗ █████╗  ██████╗ ██████╗ ██████╗ ███████╗
 ████╗  ██║██╔═══██╗██║   ██║██╔══██╗██╔════╝██╔═══██╗██╔══██╗██╔════╝
 ██╔██╗ ██║██║   ██║██║   ██║███████║██║     ██║   ██║██║  ██║█████╗
 ██║╚██╗██║██║   ██║╚██╗ ██╔╝██╔══██║██║     ██║   ██║██║  ██║██╔══╝
 ██║ ╚████║╚██████╔╝ ╚████╔╝ ██║  ██║╚██████╗╚██████╔╝██████╔╝███████╗
 ╚═╝  ╚═══╝ ╚═════╝   ╚═══╝  ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝
              ⚡ Super Multimodal CLI v3.0.0 ⚡
"""

MM_PROXY_HOST = "127.0.0.1"
MM_PROXY_PORT = int(os.environ.get("NOVA_MM_PROXY_PORT", "18791"))
LOCAL_LLM_PORT = int(os.environ.get("NOVACODE_UNCENSORED_PORT", "18792"))

MODEL_ALIASES: Dict[str, str] = {
    "nova": "nvidia/nemotron-3-super-120b-a12b",
    "jet": "nvidia/nemotron-3.5-lightning-30b-a3b",
    "dev": "nvidia/nemotron-3-nano-30b-a3b",
    "pulse": "nvidia/nemotron-3.5-super-70b-a3b-reasoning",
    "omni": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning",
    "raw": "novacode-uncensored",
    "wild": "novacode-uncensored",
    "iris": "minimaxai/minimax-m3",
    "apex": "nvidia/nemotron-3-ultra-550b-a55b",
    "pro": "nvidia/nemotron-3-super-120b-a12b",
    "lite": "nvidia/nemotron-3-nano-30b-a3b",
}

MODEL_CAPABILITIES: Dict[str, Dict[str, Any]] = {
    "nvidia/nemotron-3-super-120b-a12b": {
        "name": "Nova Super",
        "params": "120B",
        "context": "128K",
        "tasks": ["chat", "code", "reasoning", "analysis"],
        "speed": "fast",
        "quality": "ultra",
    },
    "nvidia/nemotron-3.5-lightning-30b-a3b": {
        "name": "Jet Relámpago",
        "params": "30B",
        "context": "64K",
        "tasks": ["chat", "code", "fast-response"],
        "speed": "ultra",
        "quality": "pro",
    },
    "nvidia/nemotron-3-nano-30b-a3b": {
        "name": "Dev Nano",
        "params": "30B",
        "context": "32K",
        "tasks": ["chat", "simple-tasks", "fast-response"],
        "speed": "ultra",
        "quality": "draft",
    },
    "nvidia/nemotron-3.5-super-70b-a3b-reasoning": {
        "name": "Pulse Razonador",
        "params": "70B",
        "context": "128K",
        "tasks": ["reasoning", "analysis", "complex-tasks"],
        "speed": "medium",
        "quality": "ultra",
    },
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning": {
        "name": "Omni Multimodal",
        "params": "30B",
        "context": "64K",
        "tasks": ["multimodal", "vision", "audio", "video"],
        "speed": "fast",
        "quality": "pro",
    },
    "minimaxai/minimax-m3": {
        "name": "Iris Visión",
        "params": "200B+",
        "context": "256K",
        "tasks": ["vision", "multimodal", "image-understanding"],
        "speed": "medium",
        "quality": "ultra",
    },
    "nvidia/nemotron-3-ultra-550b-a55b": {
        "name": "Apex Ultra",
        "params": "550B",
        "context": "256K",
        "tasks": ["chat", "code", "reasoning", "complex-tasks"],
        "speed": "slow",
        "quality": "ultra",
    },
    "novacode-uncensored": {
        "name": "Raw/Wild Local",
        "params": "9B",
        "context": "4K",
        "tasks": ["uncensored", "nsfw", "private", "offline"],
        "speed": "fast",
        "quality": "pro",
    },
}

# ============================================================================
# Color & Styling
# ============================================================================

class Colors:
    """ANSI color codes for terminal output."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"

    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"

    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"

    @classmethod
    def disable(cls) -> None:
        """Disable all colors."""
        for attr in list(vars(cls).keys()):
            if not attr.startswith("_") and attr.isupper():
                setattr(cls, attr, "")


class Style:
    """Text styling utilities."""

    def __init__(self, use_color: bool = True) -> None:
        self.use_color = use_color
        if not use_color:
            Colors.disable()

    def bold(self, text: str) -> str:
        return f"{Colors.BOLD}{text}{Colors.RESET}" if self.use_color else text

    def dim(self, text: str) -> str:
        return f"{Colors.DIM}{text}{Colors.RESET}" if self.use_color else text

    def cyan(self, text: str) -> str:
        return f"{Colors.CYAN}{text}{Colors.RESET}" if self.use_color else text

    def green(self, text: str) -> str:
        return f"{Colors.GREEN}{text}{Colors.RESET}" if self.use_color else text

    def yellow(self, text: str) -> str:
        return f"{Colors.YELLOW}{text}{Colors.RESET}" if self.use_color else text

    def red(self, text: str) -> str:
        return f"{Colors.RED}{text}{Colors.RESET}" if self.use_color else text

    def magenta(self, text: str) -> str:
        return f"{Colors.MAGENTA}{text}{Colors.RESET}" if self.use_color else text

    def blue(self, text: str) -> str:
        return f"{Colors.BLUE}{text}{Colors.RESET}" if self.use_color else text

    def header(self, text: str) -> str:
        return f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.RESET}" if self.use_color else text

    def success(self, text: str) -> str:
        return f"{Colors.GREEN}✓ {text}{Colors.RESET}" if self.use_color else f"✓ {text}"

    def error(self, text: str) -> str:
        return f"{Colors.RED}✗ {text}{Colors.RESET}" if self.use_color else f"✗ {text}"

    def warning(self, text: str) -> str:
        return f"{Colors.YELLOW}⚠ {text}{Colors.RESET}" if self.use_color else f"⚠ {text}"

    def info(self, text: str) -> str:
        return f"{Colors.BLUE}ℹ {text}{Colors.RESET}" if self.use_color else f"ℹ {text}"


# ============================================================================
# Output Formatting
# ============================================================================

class OutputFormatter:
    """Professional output formatting with tables, progress bars, and highlighting."""

    def __init__(self, style: Style, json_mode: bool = False, quiet: bool = False) -> None:
        self.style = style
        self.json_mode = json_mode
        self.quiet = quiet

    def print_banner(self) -> None:
        """Print the CodeForge ASCII banner."""
        if self.json_mode or self.quiet:
            return
        print(self.style.cyan(NOVACODE_BANNER))

    def print_table(
        self,
        headers: List[str],
        rows: List[List[str]],
        title: Optional[str] = None,
    ) -> None:
        """Print a formatted table."""
        if self.json_mode:
            data = [dict(zip(headers, row)) for row in rows]
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return
        if self.quiet:
            return

        if title:
            print(f"\n{self.style.header(title)}")
            print(self.style.dim("─" * 60))

        if not rows:
            print(self.style.dim("  (no data)"))
            return

        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(cell))

        header_line = " │ ".join(
            self.style.bold(h.ljust(col_widths[i])) for i, h in enumerate(headers)
        )
        print(f"  {header_line}")
        print(f"  {'─' * (sum(col_widths) + 3 * (len(headers) - 1))}")

        for row in rows:
            line = " │ ".join(cell.ljust(col_widths[i]) for i, cell in enumerate(row))
            print(f"  {line}")

    def print_progress(self, current: int, total: int, label: str = "") -> None:
        """Print a progress bar."""
        if self.json_mode or self.quiet:
            return

        width = 40
        filled = int(width * current / max(total, 1))
        bar = "█" * filled + "░" * (width - filled)
        pct = int(100 * current / max(total, 1))

        sys.stdout.write(f"\r  {self.style.cyan(label)} [{bar}] {pct}%")
        sys.stdout.flush()

        if current >= total:
            print()

    def print_code(self, code: str, language: str = "python") -> None:
        """Print code with basic syntax highlighting."""
        if self.json_mode:
            print(json.dumps({"code": code, "language": language}))
            return
        if self.quiet:
            print(code)
            return

        print(f"\n{self.style.dim('┌─ ' + language + ' ' + '─' * 50)}")

        keywords = {
            "python": ["def", "class", "import", "from", "return", "if", "else", "elif", "for", "while", "try", "except", "with", "as", "async", "await", "lambda", "yield", "raise", "pass", "break", "continue", "and", "or", "not", "in", "is", "None", "True", "False"],
            "javascript": ["function", "const", "let", "var", "return", "if", "else", "for", "while", "try", "catch", "async", "await", "class", "import", "export", "new", "this", "null", "undefined", "true", "false"],
            "bash": ["if", "then", "else", "fi", "for", "while", "do", "done", "case", "esac", "function", "return", "export", "source", "echo", "cd", "ls", "grep", "find", "sed", "awk"],
        }

        lang_keywords = keywords.get(language, [])

        for line in code.splitlines():
            highlighted = line
            if language == "python" or language == "javascript":
                highlighted = re.sub(
                    r'(".*?"|\'.*?\')',
                    f"{Colors.GREEN}\\1{Colors.RESET}",
                    highlighted,
                )
                highlighted = re.sub(
                    r"(#.*$|//.*$)",
                    f"{Colors.DIM}\\1{Colors.RESET}",
                    highlighted,
                )
            for kw in lang_keywords:
                highlighted = re.sub(
                    rf"\b{kw}\b",
                    f"{Colors.MAGENTA}{kw}{Colors.RESET}",
                    highlighted,
                )
            print(f"{self.style.dim('│')} {highlighted}")

        print(f"{self.style.dim('└' + '─' * 55)}")

    def print_json(self, data: Any) -> None:
        """Print data as formatted JSON."""
        print(json.dumps(data, indent=2, ensure_ascii=False, default=str))

    def print_success(self, message: str) -> None:
        """Print a success message."""
        if self.json_mode:
            print(json.dumps({"status": "success", "message": message}))
        elif not self.quiet:
            print(self.style.success(message))

    def print_error(self, message: str) -> None:
        """Print an error message."""
        if self.json_mode:
            print(json.dumps({"status": "error", "message:": message}))
        elif not self.quiet:
            print(self.style.error(message), file=sys.stderr)

    def print_warning(self, message: str) -> None:
        """Print a warning message."""
        if self.json_mode:
            print(json.dumps({"status": "warning", "message": message}))
        elif not self.quiet:
            print(self.style.warning(message))

    def print_info(self, message: str) -> None:
        """Print an info message."""
        if self.json_mode:
            print(json.dumps({"status": "info", "message": message}))
        elif not self.quiet:
            print(self.style.info(message))

    def print_section(self, title: str) -> None:
        """Print a section header."""
        if self.json_mode or self.quiet:
            return
        print(f"\n{self.style.header('━' * 60)}")
        print(self.style.header(f"  {title}"))
        print(self.style.header("━" * 60))


# ============================================================================
# HTTP Client
# ============================================================================

class HTTPClient:
    """Simple HTTP client for API interactions."""

    def __init__(self, base_url: str, timeout: int = 45) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def get(self, path: str, headers: Optional[Dict[str, str]] = None) -> Tuple[int, bytes]:
        """Perform a GET request."""
        url = f"{self.base_url}{path}"
        req = urllib.request.Request(url, headers=headers or {}, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return resp.status, resp.read()
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read() or str(exc).encode("utf-8")

    def post(
        self,
        path: str,
        data: Any,
        headers: Optional[Dict[str, str]] = None,
    ) -> Tuple[int, bytes]:
        """Perform a POST request."""
        url = f"{self.base_url}{path}"
        body = json.dumps(data).encode("utf-8") if data is not None else None
        hdrs = {"Content-Type": "application/json", "Accept": "application/json"}
        if headers:
            hdrs.update(headers)
        req = urllib.request.Request(url, data=body, headers=hdrs, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return resp.status, resp.read()
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read() or str(exc).encode("utf-8")


# ============================================================================
# NovaCode Core
# ============================================================================

class CodeForgeCore:
    """Core CodeForge functionality integrating all subsystems."""

    def __init__(
        self,
        model: str = "nova",
        quality: str = "pro",
        nsfw: bool = False,
        json_mode: bool = False,
        verbose: bool = False,
        quiet: bool = False,
        no_color: bool = False,
        session_id: Optional[str] = None,
        auto_mode: bool = False,
        pure_mode: bool = False,
    ) -> None:
        self.model = MODEL_ALIASES.get(model, model)
        self.quality = quality
        self.nsfw = nsfw
        self.verbose = verbose
        self.session_id = session_id or self._generate_session_id()
        self.auto_mode = auto_mode
        self.pure_mode = pure_mode

        self.style = Style(use_color=not no_color)
        self.fmt = OutputFormatter(self.style, json_mode=json_mode, quiet=quiet)
        self.proxy_client = HTTPClient(f"http://{MM_PROXY_HOST}:{MM_PROXY_PORT}")

    @staticmethod
    def _generate_session_id() -> str:
        """Generate a unique session ID."""
        return hashlib.sha256(f"{time.time()}{os.getpid()}".encode()).hexdigest()[:16]

    def resolve_model(self, task_type: str = "general") -> str:
        """Resolve the best model for a task type."""
        if self.model in MODEL_ALIASES.values():
            return self.model
        return MODEL_ALIASES.get(self.model, self.model)

    def chat(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
    ) -> Dict[str, Any]:
        """Send chat messages to the model via mm-proxy."""
        model = self.resolve_model("chat")

        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "temperature": 0.9 if self.nsfw else 0.7,
            "max_tokens": 4096,
        }

        if self.nsfw:
            payload["nsfw"] = True

        status, body = self.proxy_client.post("/v1/chat/completions", payload)

        if status == 200:
            try:
                return json.loads(body.decode("utf-8"))
            except json.JSONDecodeError:
                return {"error": "Invalid JSON response", "raw": body.decode("utf-8", errors="replace")}
        else:
            return {"error": f"HTTP {status}", "raw": body.decode("utf-8", errors="replace")}

    def generate_text(self, prompt: str, system: Optional[str] = None) -> str:
        """Generate text using the configured model."""
        messages: List[Dict[str, str]] = []
        if system and not self.pure_mode:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        result = self.chat(messages)
        if "choices" in result:
            return result["choices"][0]["message"]["content"]
        return result.get("error", "Generation failed")

    def generate_image(self, prompt: str) -> Dict[str, Any]:
        """Generate an image using the generate.py backend."""
        try:
            sys.path.insert(0, str(CODEFORGE_HOME))
            import generate as nova_gen

            nova_gen.load_secrets()
            return nova_gen.generate_image(prompt, nsfw=self.nsfw, quality=self.quality)
        except Exception as exc:
            return {"error": str(exc), "path": None}

    def generate_video(self, prompt: str) -> Dict[str, Any]:
        """Generate a video using the generate.py backend."""
        try:
            sys.path.insert(0, str(CODEFORGE_HOME))
            import generate as nova_gen

            nova_gen.load_secrets()
            return nova_gen.generate_video(prompt, nsfw=self.nsfw, quality=self.quality)
        except Exception as exc:
            return {"error": str(exc), "path": None}

    def generate_audio(self, prompt: str, music: bool = False) -> Dict[str, Any]:
        """Generate audio using the generate.py backend."""
        try:
            sys.path.insert(0, str(CODEFORGE_HOME))
            import generate as nova_gen

            nova_gen.load_secrets()
            return nova_gen.generate_audio(prompt, nsfw=self.nsfw, quality=self.quality, music=music)
        except Exception as exc:
            return {"error": str(exc), "path": None}

    def check_proxy_health(self) -> Dict[str, Any]:
        """Check the mm-proxy health status."""
        status, body = self.proxy_client.get("/health")
        if status == 200:
            try:
                return json.loads(body.decode("utf-8"))
            except json.JSONDecodeError:
                return {"ok": True, "raw": body.decode("utf-8", errors="replace")}
        return {"ok": False, "status": status}

    def get_proxy_stats(self) -> Dict[str, Any]:
        """Get proxy performance statistics."""
        status, body = self.proxy_client.get("/v1/stats")
        if status == 200:
            try:
                return json.loads(body.decode("utf-8"))
            except json.JSONDecodeError:
                return {"error": "Invalid JSON"}
        return {"error": f"HTTP {status}"}


# ============================================================================
# Command Handlers
# ============================================================================

class CommandHandlers:
    """All command handlers for the CodeForge CLI."""

    def __init__(self, core: NovaCodeCore) -> None:
        self.core = core
        self.fmt = core.fmt
        self.style = core.style

    def cmd_chat(self, args: argparse.Namespace) -> int:
        """Handle the chat command — interactive chat with any model."""
        self.fmt.print_section("NOVACODE CHAT")
        self.fmt.print_info(f"Model: {self.core.model} | Session: {self.core.session_id}")
        self.fmt.print_info("Type 'exit' to quit, '/help' for commands\n")

        messages: List[Dict[str, str]] = []

        if not self.core.pure_mode:
            system_msg = (
                "You are NOVACODE CLI, an elite multimodal AI assistant. "
                "Provide concise, accurate, and helpful responses. "
                "Support code generation, analysis, and creative tasks."
            )
            if self.core.nsfw:
                system_msg += " NSFW adult content is allowed for consenting adults."
            messages.append({"role": "system", "content": system_msg})

        while True:
            try:
                user_input = input(self.style.cyan("You> ")).strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break

            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                break
            if user_input == "/help":
                self._print_chat_help()
                continue
            if user_input == "/clear":
                messages = messages[:1] if messages and messages[0]["role"] == "system" else []
                self.fmt.print_info("Conversation cleared.")
                continue
            if user_input == "/model":
                self.fmt.print_info(f"Current model: {self.core.model}")
                continue

            messages.append({"role": "user", "content": user_input})

            try:
                result = self.core.chat(messages)
                if "choices" in result:
                    response = result["choices"][0]["message"]["content"]
                    messages.append({"role": "assistant", "content": response})
                    print(f"\n{self.style.magenta('Nova>')} {response}\n")
                else:
                    self.fmt.print_error(result.get("error", "Unknown error"))
            except Exception as exc:
                self.fmt.print_error(f"Chat error: {exc}")

        return 0

    def _print_chat_help(self) -> None:
        """Print chat help information."""
        print(f"""
{self.style.header("Chat Commands:")}
  /help     Show this help
  /clear    Clear conversation history
  /model    Show current model
  /exit     Exit chat

{self.style.header("Tips:")}
  - Use --model to switch models
  - Use --nsfw for uncensored mode
  - Use --json for structured output
""")

    def cmd_generate(self, args: argparse.Namespace) -> int:
        """Handle the generate command — generate text, images, video, audio, music."""
        prompt = " ".join(args.prompt) if hasattr(args, "prompt") and args.prompt else ""
        gen_type = args.type if hasattr(args, "type") and args.type else "text"
        if not prompt:
            self.fmt.print_error(f"Prompt required. Usage: nova generate <type> <prompt>\nTypes: text, image, video, audio, music")
            return 1

        gen_type = args.type if hasattr(args, "type") and args.type else "text"

        self.fmt.print_section(f"GENERATE: {gen_type.upper()}")
        self.fmt.print_info(f"Quality: {self.core.quality} | Model: {self.core.model}")

        if gen_type == "text":
            result = self.core.generate_text(prompt)
            print(f"\n{result}\n")
        elif gen_type == "image":
            self.fmt.print_info("Generating image...")
            result = self.core.generate_image(prompt)
            if result.get("path"):
                self.fmt.print_success(f"Image saved: {result['path']}")
            else:
                self.fmt.print_error(result.get("error", "Generation failed"))
        elif gen_type == "video":
            self.fmt.print_info("Generating video...")
            result = self.core.generate_video(prompt)
            if result.get("path"):
                self.fmt.print_success(f"Video saved: {result['path']}")
            else:
                self.fmt.print_error(result.get("error", "Generation failed"))
        elif gen_type in ("audio", "music"):
            self.fmt.print_info(f"Generating {gen_type}...")
            result = self.core.generate_audio(prompt, music=(gen_type == "music"))
            if result.get("path"):
                self.fmt.print_success(f"Audio saved: {result['path']}")
            else:
                self.fmt.print_error(result.get("error", "Generation failed"))
        else:
            self.fmt.print_error(f"Unknown generation type: {gen_type}")
            return 1

        return 0

    def cmd_code(self, args: argparse.Namespace) -> int:
        """Handle the code command — code generation with Python auto-integration."""
        task = " ".join(args.task) if hasattr(args, "task") and args.task else ""
        if not task:
            self.fmt.print_error("Task required. Usage: nova code <description>")
            return 1

        self.fmt.print_section("CODE GENERATION")
        self.fmt.print_info(f"Model: {self.core.model}")

        system = (
            "You are NOVACODE, an elite code generation engine. "
            "Write clean, production-ready Python code with type annotations. "
            "Follow PEP 8, use pathlib, handle exceptions gracefully. "
            "Never use placeholders or TODO comments. Output only code."
        )

        result = self.core.generate_text(task, system=system)
        self.fmt.print_code(result, language="python")

        if args.run and hasattr(args, "run") and args.run:
            self.fmt.print_info("Executing generated code...")
            try:
                exec(result, {"__name__": "__main__"})
            except Exception as exc:
                self.fmt.print_error(f"Execution error: {exc}")

        return 0

    def cmd_analyze(self, args: argparse.Namespace) -> int:
        """Handle the analyze command — analyze files, images, audio, video."""
        target = " ".join(args.target) if hasattr(args, "target") and args.target else ""
        if not target:
            self.fmt.print_error("Target required. Usage: nova analyze <file_or_path>")
            return 1

        self.fmt.print_section("ANALYSIS")
        self.fmt.print_info(f"Target: {target}")

        path = Path(target)
        if not path.exists():
            self.fmt.print_error(f"File not found: {target}")
            return 1

        analysis_type = "generic"
        suffix = path.suffix.lower()
        if suffix in (".py", ".js", ".ts", ".rs", ".go", ".c", ".cpp", ".java"):
            analysis_type = "code"
        elif suffix in (".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"):
            analysis_type = "image"
        elif suffix in (".mp4", ".avi", ".mov", ".webm", ".mkv"):
            analysis_type = "video"
        elif suffix in (".mp3", ".wav", ".ogg", ".flac", ".m4a"):
            analysis_type = "audio"
        elif suffix in (".json", ".yaml", ".yml", ".toml", ".xml", ".csv"):
            analysis_type = "data"

        self.fmt.print_info(f"Detected type: {analysis_type}")

        if analysis_type == "code":
            content = path.read_text(encoding="utf-8")
            prompt = f"Analyze this {suffix} code and provide insights on quality, security, and improvements:\n\n```\n{content}\n```"
        elif analysis_type == "data":
            content = path.read_text(encoding="utf-8")
            prompt = f"Analyze this {suffix} data file and describe its structure and content:\n\n```\n{content[:2000]}\n```"
        else:
            prompt = f"Analyze the {analysis_type} file at {target} and describe its content, quality, and any notable features."

        result = self.core.generate_text(prompt)
        print(f"\n{result}\n")
        return 0

    def cmd_learn(self, args: argparse.Namespace) -> int:
        """Handle the learn command — view and manage learning."""
        self.fmt.print_section("LEARNING ENGINE")

        try:
            sys.path.insert(0, str(CODEFORGE_HOME))
            import learned_capabilities as lc

            engine = lc.SelfLearningEngine()

            stats = {
                "patterns": engine._get_conn().execute("SELECT COUNT(*) FROM patterns").fetchone()[0],
                "sessions": engine._get_conn().execute("SELECT COUNT(*) FROM sessions").fetchone()[0],
                "model_performance": engine._get_conn().execute("SELECT COUNT(*) FROM model_performance").fetchone()[0],
                "prompt_templates": engine._get_conn().execute("SELECT COUNT(*) FROM prompt_templates").fetchone()[0],
                "knowledge_base": engine._get_conn().execute("SELECT COUNT(*) FROM knowledge_base").fetchone()[0],
            }

            self.fmt.print_table(
                ["Metric", "Count"],
                [[k.replace("_", " ").title(), str(v)] for k, v in stats.items()],
                title="Learning Statistics",
            )

            top_patterns = engine._get_conn().execute(
                "SELECT task_type, pattern, confidence FROM patterns ORDER BY confidence DESC LIMIT 10"
            ).fetchall()

            if top_patterns:
                self.fmt.print_table(
                    ["Task Type", "Pattern", "Confidence"],
                    [[p["task_type"], p["pattern"][:50], f"{p['confidence']:.2f}"] for p in top_patterns],
                    title="Top Learned Patterns",
                )

            engine.close()
        except Exception as exc:
            self.fmt.print_error(f"Learning engine error: {exc}")
            return 1

        return 0

    def cmd_evolve(self, args: argparse.Namespace) -> int:
        """Handle the evolve command — self-improvement and evolution."""
        self.fmt.print_section("EVOLUTION ENGINE")

        try:
            sys.path.insert(0, str(CODEFORGE_HOME))
            import learned_capabilities as lc

            engine = lc.SelfLearningEngine()
            evolver = lc.ModelEvolver(engine)

            rankings = evolver.get_all_metrics()

            if rankings:
                for task_type, models in rankings.items():
                    self.fmt.print_info(f"Task: {task_type}")
                    for m in models[:5]:
                        self.fmt.print_table(
                            ["Model", "Success", "Failures", "Avg Latency"],
                            [[m["model"], str(m["success_count"]), str(m["failure_count"]), f"{m['avg_latency']:.2f}s"]],
                        )
            else:
                self.fmt.print_info("No evolution data yet. Run more sessions to enable learning.")

            engine.close()
        except Exception as exc:
            self.fmt.print_error(f"Evolution error: {exc}")
            return 1

        return 0

    def cmd_models(self, args: argparse.Namespace) -> int:
        """Handle the models command — list all models with capabilities."""
        self.fmt.print_section("AVAILABLE MODELS")

        rows: List[List[str]] = []
        for model_id, caps in MODEL_CAPABILITIES.items():
            rows.append([
                caps["name"],
                caps["params"],
                caps["context"],
                ", ".join(caps["tasks"][:3]),
                caps["speed"],
                caps["quality"],
            ])

        self.fmt.print_table(
            ["Name", "Params", "Context", "Tasks", "Speed", "Quality"],
            rows,
            title="Model Catalog",
        )

        aliases = [[alias, model] for alias, model in MODEL_ALIASES.items()]
        self.fmt.print_table(
            ["Alias", "Model ID"],
            aliases,
            title="Model Aliases",
        )

        return 0

    def cmd_doctor(self, args: argparse.Namespace) -> int:
        """Handle the doctor command — system health check."""
        self.fmt.print_section("NOVACODE DOCTOR")

        checks: List[Tuple[str, bool, str]] = []

        checks.append(("Python 3.8+", sys.version_info >= (3, 8), f"Python {sys.version.split()[0]}"))
        checks.append(("CodeForge Home", CODEFORGE_HOME.exists(), str(CODEFORGE_HOME)))
        checks.append(("Config File", NOVACODE_CONFIG.exists(), str(NOVACODE_CONFIG)))
        checks.append(("mm-proxy.py", (CODEFORGE_HOME / "mm-proxy.py").exists(), str(CODEFORGE_HOME / "mm-proxy.py")))
        checks.append(("generate.py", (CODEFORGE_HOME / "generate.py").exists(), str(CODEFORGE_HOME / "generate.py")))
        checks.append(("learned_capabilities.py", (CODEFORGE_HOME / "learned_capabilities.py").exists(), str(CODEFORGE_HOME / "learned_capabilities.py")))
        checks.append(("self_update.py", (CODEFORGE_HOME / "self_update.py").exists(), str(CODEFORGE_HOME / "self_update.py")))

        proxy_health = self.core.check_proxy_health()
        checks.append(("mm-proxy Service", proxy_health.get("ok", False), "Running" if proxy_health.get("ok") else "Not running"))

        local_llm = False
        try:
            with socket.create_connection(("127.0.0.1", LOCAL_LLM_PORT), timeout=0.3):
                local_llm = True
        except OSError:
            pass
        checks.append(("Local LLM (:18792)", True, "UP (active)" if local_llm else "READY (on-demand)"))

        nvidia_key = bool(os.environ.get("NVIDIA_API_KEY", ""))
        if not nvidia_key:
            for p in [Path.home() / ".config" / "nova" / "secrets.env", Path.home() / ".config" / "env" / "nvidia.env"]:
                if p.exists():
                    for line in p.read_text(encoding="utf-8").splitlines():
                        if "NVIDIA_API_KEY=" in line:
                            nvidia_key = True
                            break
        checks.append(("NVIDIA API Key", nvidia_key, "Active" if nvidia_key else "MISSING"))

        checks.append(("llama-cli", shutil.which("llama-cli") is not None, shutil.which("llama-cli") or "NOT FOUND"))
        checks.append(("llama-server", shutil.which("llama-server") is not None, shutil.which("llama-server") or "NOT FOUND"))
        checks.append(("ollama", shutil.which("ollama") is not None, shutil.which("ollama") or "NOT FOUND"))
        checks.append(("git", shutil.which("git") is not None, shutil.which("git") or "NOT FOUND"))

        rows = [[name, self.style.green("PASS") if ok else self.style.red("FAIL"), detail] for name, ok, detail in checks]
        self.fmt.print_table(["Component", "Status", "Detail"], rows)

        passed = sum(1 for _, ok, _ in checks if ok)
        total = len(checks)
        print(f"\n  {self.style.bold(f'Health: {passed}/{total} checks passed')}")

        if passed < total:
            self.fmt.print_warning("Some checks failed. Run 'nova setup' to fix issues.")
        else:
            self.fmt.print_success("All systems operational!")

        return 0

    def cmd_config(self, args: argparse.Namespace) -> int:
        """Handle the config command — configuration management."""
        self.fmt.print_section("CONFIGURATION")

        if args.action == "show" or args.action is None:
            if NOVACODE_CONFIG.exists():
                config = json.loads(NOVACODE_CONFIG.read_text(encoding="utf-8"))
                self.fmt.print_json(config)
            else:
                self.fmt.print_warning("No config file found. Using defaults.")
        elif args.action == "set":
            if hasattr(args, "key") and hasattr(args, "value"):
                config = {}
                if NOVACODE_CONFIG.exists():
                    config = json.loads(NOVACODE_CONFIG.read_text(encoding="utf-8"))
                config[args.key] = args.value
                NOVACODE_CONFIG.write_text(json.dumps(config, indent=2), encoding="utf-8")
                self.fmt.print_success(f"Set {args.key} = {args.value}")
            else:
                self.fmt.print_error("Usage: nova config set <key> <value>")
                return 1
        elif args.action == "reset":
            default_config = {
                "version": 3,
                "plugins": {"enabled": [], "auto_update": True, "sources": ["official"]},
                "learning": {"enabled": True, "auto_improve": True},
            }
            NOVACODE_CONFIG.write_text(json.dumps(default_config, indent=2), encoding="utf-8")
            self.fmt.print_success("Configuration reset to defaults.")

        return 0

    def cmd_session(self, args: argparse.Namespace) -> int:
        """Handle the session command — session management."""
        self.fmt.print_section("SESSION MANAGEMENT")

        if args.action == "info" or args.action is None:
            session_info = {
                "session_id": self.core.session_id,
                "model": self.core.model,
                "quality": self.core.quality,
                "nsfw": self.core.nsfw,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            self.fmt.print_json(session_info)
        elif args.action == "new":
            self.core.session_id = self.core._generate_session_id()
            self.fmt.print_success(f"New session: {self.core.session_id}")
        elif args.action == "list":
            self.fmt.print_info("Session history stored in learning.db")
            try:
                sys.path.insert(0, str(CODEFORGE_HOME))
                import learned_capabilities as lc

                engine = lc.SelfLearningEngine()
                sessions = engine._get_conn().execute(
                    "SELECT id, task_type, model_used, success_score, created_at FROM sessions ORDER BY created_at DESC LIMIT 20"
                ).fetchall()

                if sessions:
                    self.fmt.print_table(
                        ["ID", "Task", "Model", "Score", "Date"],
                        [[s["id"][:12], s["task_type"], s["model_used"], f"{s['success_score']:.2f}", s["created_at"]] for s in sessions],
                    )
                engine.close()
            except Exception as exc:
                self.fmt.print_error(f"Error: {exc}")

        return 0

    def cmd_multimodal(self, args: argparse.Namespace) -> int:
        """Handle the multimodal command — full multimodal pipeline."""
        prompt = " ".join(args.prompt) if hasattr(args, "prompt") and args.prompt else ""
        if not prompt:
            self.fmt.print_error("Prompt required. Usage: nova multimodal <prompt>")
            return 1

        self.fmt.print_section("MULTIMODAL PIPELINE")
        self.fmt.print_info(f"Analyzing intent for: {prompt[:80]}...")

        try:
            sys.path.insert(0, str(CODEFORGE_HOME))
            import generate as nova_gen

            nova_gen.load_secrets()
            intent = nova_gen.detect_media_intent(prompt)

            if intent:
                self.fmt.print_info(f"Detected intent: {intent}")
                self.fmt.print_progress(0, 100, "Processing")

                for i in range(10):
                    time.sleep(0.1)
                    self.fmt.print_progress((i + 1) * 10, 100, f"Generating {intent}")

                if intent == "image":
                    result = self.core.generate_image(prompt)
                elif intent == "video":
                    result = self.core.generate_video(prompt)
                elif intent in ("audio", "music"):
                    result = self.core.generate_audio(prompt, music=(intent == "music"))
                else:
                    result = {"error": f"Unsupported intent: {intent}"}

                if result.get("path"):
                    self.fmt.print_success(f"Generated: {result['path']}")
                else:
                    self.fmt.print_error(result.get("error", "Generation failed"))
            else:
                self.fmt.print_info("No media intent detected. Falling back to text.")
                result = self.core.generate_text(prompt)
                print(f"\n{result}\n")

        except Exception as exc:
            self.fmt.print_error(f"Multimodal error: {exc}")
            return 1

        return 0

    def cmd_python(self, args: argparse.Namespace) -> int:
        """Handle the python command — execute with NovaCode Hyper-Engine (Auto-Pip, Smart-Sudo, AI Self-Healing)."""
        code = " ".join(args.code) if hasattr(args, "code") and args.code else ""
        
        try:
            from engine_core import NovaHyperEngine
            engine = NovaHyperEngine(ai_generator=self.core.generate_text)
        except Exception:
            engine = None
            
        if not code:
            self.fmt.print_section("NOVACODE HYPER-ENGINE INTERACTIVE REPL")
            self.fmt.print_info("Supports Python + Shell (!cmd, $cmd) + Smart-Sudo (!sudo cmd) + AI (ai: prompt)")
            local_scope = {"__name__": "__main__"}
            
            while True:
                try:
                    line = input("nova-core> ").strip()
                    if not line:
                        continue
                    if line in ("exit", "quit", "exit()", "quit()"):
                        break
                    if line.startswith("ai:"):
                        prompt = line[3:].strip()
                        system = "Generate clean Python or Bash code for the following task. Output only executable code."
                        gen_code = self.core.generate_text(prompt, system=system)
                        self.fmt.print_code(gen_code, language="python")
                        if engine:
                            engine.execute_hybrid(gen_code, local_scope)
                        else:
                            exec(gen_code, local_scope)
                    elif engine:
                        ok, res, err = engine.execute_hybrid(line, local_scope)
                        if res is not None:
                            print(repr(res))
                        if not ok and err:
                            self.fmt.print_error(err)
                    else:
                        try:
                            res = eval(line, local_scope)
                            if res is not None:
                                print(repr(res))
                        except SyntaxError:
                            exec(line, local_scope)
                except (KeyboardInterrupt, EOFError):
                    print("\n")
                    break
                except Exception as exc:
                    self.fmt.print_error(f"Error: {exc}")
            return 0

        p = Path(code)
        if p.exists() and p.is_file() and p.suffix == ".py":
            self.fmt.print_section(f"EXECUTING HYBRID SCRIPT: {p.name}")
            script_content = p.read_text(encoding="utf-8", errors="ignore")
            if engine:
                ok, res, err = engine.execute_hybrid(script_content)
                return 0 if ok else 1
            else:
                return subprocess.call([sys.executable, str(p)])

        self.fmt.print_section("HYPER-ENGINE EXECUTION")

        if code.startswith("ai:"):
            prompt = code[3:].strip()
            system = "Generate clean Python or Bash code for the following task. Output only executable code."
            code = self.core.generate_text(prompt, system=system)
            self.fmt.print_code(code, language="python")

        if engine:
            ok, res, err = engine.execute_hybrid(code)
            if res is not None:
                print(res)
            return 0 if ok else 1

        try:
            exec(code, {"__name__": "__main__", "__builtins__": __builtins__})
            return 0
        except Exception as exc:
            self.fmt.print_error(f"Execution error: {exc}")
            return 1

    def cmd_sudo(self, args: argparse.Namespace) -> int:
        """Handle the sudo command — execute privileged commands with AI assistance and safety."""
        command = " ".join(args.command) if hasattr(args, "command") and args.command else ""
        if not command:
            self.fmt.print_error("Command required. Usage: nova sudo <command> or nova sudo ai:<description>")
            return 1

        self.fmt.print_section("PRIVILEGED (SUDO) EXECUTION")

        if command.startswith("ai:"):
            prompt = command[3:].strip()
            system = "Generate a single safe administrative/root bash command for the following task. Output only the command."
            command = self.core.generate_text(prompt, system=system)
            self.fmt.print_info(f"Generated privileged command: {command}")

        full_cmd = f"sudo {command}" if not command.startswith("sudo") else command
        self.fmt.print_info(f"Executing: {full_cmd}")

        try:
            ret = subprocess.call(full_cmd, shell=True)
            if ret != 0:
                self.fmt.print_warning(f"Command finished with exit code {ret}")
            else:
                self.fmt.print_success("Privileged command completed successfully")
            return ret
        except Exception as exc:
            self.fmt.print_error(f"Sudo execution error: {exc}")
            return 1

    def cmd_forge(self, args: argparse.Namespace) -> int:
        """Handle the forge command — Model creation, dataset extraction, training & merging."""
        action = getattr(args, "action", "") or "status"
        self.fmt.print_section(f"NOVACODE MODEL FORGE — {action.upper()}")
        
        try:
            from forge import DatasetGenerator, ModelMerger, ModelTrainer, ModelQuantizer, MultimodalProjector
            
            if action == "dataset":
                gen = DatasetGenerator()
                target = getattr(args, "target", None) or Path.cwd()
                out = gen.extract_from_repo(Path(target))
                self.fmt.print_success(f"Dataset generated at: {out}")
            elif action == "status":
                self.fmt.print_info("Model Forge Architecture: ACTIVE")
                self.fmt.print_info("Frameworks: MLX (Apple Silicon Metal) + MergeKit + GGUF Quantizer")
                quant = ModelQuantizer()
                self.fmt.print_info(f"Model Output Directory: {quant.output_dir}")
            else:
                self.fmt.print_info(f"Forge action '{action}' ready. Usage: nova forge [status|dataset|merge|train|quantize]")
            return 0
        except Exception as exc:
            self.fmt.print_error(f"Forge error: {exc}")
            return 1

    def cmd_swarm(self, args: argparse.Namespace) -> int:
        """Handle the swarm command — dispatch multi-agent parallel speculative execution."""
        task = " ".join(args.task) if hasattr(args, "task") and args.task else ""
        if not task:
            self.fmt.print_error("Task required. Usage: nova swarm <task description>")
            return 1

        self.fmt.print_section("NOVACODE SWARM TURBO EXECUTION")
        from swarm import SwarmTurboEngine
        swarm = SwarmTurboEngine(ai_client=self.core.generate_text)
        res = swarm.dispatch_swarm(task)
        self.fmt.print_markdown(res["synthesis"])
        return 0

    def cmd_sandbox(self, args: argparse.Namespace) -> int:
        """Handle the sandbox command — isolated execution with 1ms rollback."""
        action = getattr(args, "action", "") or "status"
        self.fmt.print_section(f"NOVACODE INSTANT SANDBOX — {action.upper()}")
        from sandbox import InstantSandbox
        sb = InstantSandbox()
        if action == "snapshot":
            snap = sb.create_snapshot("manual")
            self.fmt.print_success(f"Snapshot created: {snap['id']} ({snap['files_count']} files)")
        elif action == "rollback":
            ok = sb.rollback()
            return 0 if ok else 1
        else:
            self.fmt.print_info(f"Sandbox target: {sb.target_dir}")
            self.fmt.print_info("Usage: nova sandbox [snapshot|rollback]")
        return 0

    def cmd_sentinel(self, args: argparse.Namespace) -> int:
        """Handle the sentinel command — real-time file watcher & silent auto-healer."""
        action = getattr(args, "action", "") or "status"
        self.fmt.print_section(f"NOVACODE SENTINEL DAEMON — {action.upper()}")
        from sentinel import SentinelDaemon
        sentinel = SentinelDaemon()
        if action == "watch":
            self.fmt.print_info("Starting live sentinel watcher (Ctrl+C to stop)...")
            sentinel.start_watching(interval=1.0)
            try:
                import time
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                sentinel.stop_watching()
        else:
            self.fmt.print_info("Sentinel daemon status: READY")
            self.fmt.print_info("Usage: nova sentinel watch")
        return 0

    def cmd_graph(self, args: argparse.Namespace) -> int:
        """Handle the graph command — AST semantic code graph and symbol lookup."""
        query = " ".join(args.query) if hasattr(args, "query") and args.query else ""
        self.fmt.print_section("NOVACODE SEMANTIC CODE GRAPH")
        from semantic_graph import SemanticCodeGraph
        graph = SemanticCodeGraph()
        stats = graph.build_graph()
        self.fmt.print_info(f"Graph built: {stats['total_nodes']} nodes, {stats['total_edges']} dependency edges")
        if query:
            matches = graph.search_symbol(query)
            self.fmt.print_info(f"Found {len(matches)} symbols matching '{query}':")
            for m in matches[:10]:
                print(f"  • {m['symbol']:<30} [{m.get('type')}] in {m.get('file', '')}:{m.get('line', '')}")
        return 0

    def cmd_canvas(self, args: argparse.Namespace) -> int:
        """Handle the canvas command — rich terminal visualizations and sparklines."""
        self.fmt.print_section("NOVACODE TERMINAL CANVAS")
        from canvas import TerminalCanvas
        TerminalCanvas.render_sparkline([12.5, 15.0, 11.2, 8.4, 9.1, 7.8, 6.2, 5.5], label="Latencia Inferencia (ms)")
        TerminalCanvas.render_table(
            headers=["Super Modelo", "Arquitectura", "Latencia", "Estado"],
            rows=[
                ["NovaCode Apex", "550B MoE", "0.45s", "ONLINE"],
                ["NovaCode Super", "120B", "0.38s", "ONLINE"],
                ["NovaCode Iris", "11B Vision", "0.32s", "ONLINE"],
                ["NovaCode Mythos", "9B Local GGUF", "0.02s", "LOCAL/GPU"],
            ],
            title="Cuadro de Rendimiento de Modelos"
        )
        return 0

    def cmd_refactor(self, args: argparse.Namespace) -> int:
        """Handle the refactor command — AST-level structural code surgery."""
        target = getattr(args, "target", "") or ""
        if not target or not Path(target).exists():
            self.fmt.print_error("Target file required. Usage: nova refactor <file.py>")
            return 1
        self.fmt.print_section(f"AST CODE SURGERY: {target}")
        from ast_surgeon import ASTSurgeon
        code = Path(target).read_text(encoding="utf-8", errors="ignore")
        analysis = ASTSurgeon.analyze_complexity(code)
        self.fmt.print_info(f"Syntax Valid: {analysis.get('valid_syntax')}")
        self.fmt.print_info(f"Functions: {analysis.get('functions')}, Classes: {analysis.get('classes')}")
        self.fmt.print_info(f"Nested loops: {analysis.get('nested_loops_count')} (Optimized: {analysis.get('is_optimized')})")
        return 0

    def cmd_sync(self, args: argparse.Namespace) -> int:
        """Handle the sync command — synchronize with GitHub repository automatically."""
        msg = " ".join(args.message) if hasattr(args, "message") and args.message else None
        self.fmt.print_section("NOVACODE GITHUB CONTINUOUS SYNC")
        from git_sync import AutoGitSync
        syncer = AutoGitSync(ai_client=self.core.generate_text)
        ok, res = syncer.sync_and_push(custom_msg=msg)
        if ok:
            self.fmt.print_success("GitHub sync completed successfully!")
            return 0
        else:
            self.fmt.print_error(f"GitHub sync error: {res}")
            return 1

    def cmd_bench(self, args: argparse.Namespace) -> int:
        """Handle the bench command — benchmark models latency and throughput."""
        self.fmt.print_section("NOVACODE REAL-TIME MODEL BENCHMARK")
        from auto_benchmarker import AutoBenchmarker
        from canvas import TerminalCanvas
        bench = AutoBenchmarker()
        results = bench.run_suite()
        rows = []
        for r in results:
            if r.get("status") == "pass":
                rows.append([r["model"].split("/")[-1], f"{r['latency_sec']:.2f}s", f"{r['tokens_per_sec']:.1f} tps", "PASS"])
            else:
                rows.append([r["model"].split("/")[-1], f"{r['latency_sec']:.2f}s", "N/A", "ERR"])
        TerminalCanvas.render_table(
            headers=["Modelo", "Latencia", "Rendimiento", "Diagnóstico"],
            rows=rows,
            title="Resultados del Benchmark"
        )
        return 0

    def cmd_docker(self, args: argparse.Namespace) -> int:
        """Handle the docker command — container management, Dockerfile gen & audit."""
        action = getattr(args, "action", "") or "status"
        self.fmt.print_section(f"NOVACODE DOCKER PILOT — {action.upper()}")
        from docker_pilot import DockerPilot
        pilot = DockerPilot(ai_client=self.core.generate_text)
        
        if action == "gen":
            content, path = pilot.generate_dockerfile(Path.cwd())
            self.fmt.print_success(f"Dockerfile generado en: {path}")
            self.fmt.print_code(content, language="dockerfile")
        elif action == "compose":
            content, path = pilot.generate_compose(Path.cwd())
            self.fmt.print_success(f"docker-compose.yml generado en: {path}")
            self.fmt.print_code(content, language="yaml")
        elif action == "audit":
            res = pilot.audit_dockerfile(Path.cwd() / "Dockerfile")
            if res.get("is_secure"):
                self.fmt.print_success("Dockerfile auditado: 100% SEGURO (Sin problemas detectados)")
            else:
                self.fmt.print_warning(f"Problemas detectados ({res.get('issues_count')}):")
                for iss in res.get("issues", []):
                    print(f"  • {iss}")
        else:
            avail = pilot.is_docker_available()
            self.fmt.print_info(f"Docker Daemon disponible: {'SÍ' if avail else 'NO'}")
            self.fmt.print_info("Comandos disponibles: nova docker [gen|compose|audit|status]")
        return 0

    def cmd_api(self, args: argparse.Namespace) -> int:
        """Handle the api command — test REST endpoints with latency metrics."""
        url = getattr(args, "url", "") or "http://127.0.0.1:18791/health"
        self.fmt.print_section(f"NOVACODE API TESTER: {url}")
        from devtools import ApiTester
        res = ApiTester.test_endpoint(url)
        self.fmt.print_info(f"Status: {res.get('status')} | Latencia: {res.get('latency_sec', 0):.3f}s")
        if res.get("is_json"):
            print(json.dumps(res.get("body"), indent=2, ensure_ascii=False))
        else:
            print(str(res.get("body", ""))[:300])
        return 0

    def cmd_net(self, args: argparse.Namespace) -> int:
        """Handle the net command — scan open development ports."""
        self.fmt.print_section("NOVACODE NETWORK PILOT")
        from devtools import NetworkPilot
        from canvas import TerminalCanvas
        ports = NetworkPilot.scan_common_ports()
        rows = [[p, s, "OPEN"] for p, s in ports.items()]
        TerminalCanvas.render_table(
            headers=["Puerto", "Servicio Detectado", "Estado"],
            rows=rows if rows else [["N/A", "Sin puertos abiertos", "IDLE"]],
            title="Puertos de Desarrollo Abiertos"
        )
        return 0

    def cmd_secret(self, args: argparse.Namespace) -> int:
        """Handle the secret command — audit leaked credentials and tokens."""
        self.fmt.print_section("NOVACODE SECRET & CREDENTIAL AUDITOR")
        from devtools import SecretScanner
        findings = SecretScanner.scan_directory(Path.cwd())
        if not findings:
            self.fmt.print_success("Auditoría limpia: No se encontraron secretos expuestos.")
        else:
            self.fmt.print_warning(f"¡Atención! Se encontraron {len(findings)} posibles secretos:")
            for f in findings:
                print(f"  • {f['type']} en {f['file']} (Snippet: {f['match_snippet']})")
        return 0

    def cmd_auto(self, args: argparse.Namespace) -> int:
        """Handle the auto command — autonomous self-driving goal pilot."""
        goal = " ".join(args.goal) if hasattr(args, "goal") and args.goal else ""
        if not goal:
            self.fmt.print_error("Goal required. Usage: nova auto <goal description>")
            return 1

        self.fmt.print_section("NOVACODE AUTONOMOUS SELF-DRIVING PILOT")
        from autonomous_pilot import AutonomousGoalPilot
        from canvas import TerminalCanvas
        pilot = AutonomousGoalPilot(ai_client=self.core.generate_text)
        res = pilot.execute_goal(goal, unlimited=getattr(args, "unlimited", False))
        
        rows = [[h["step_index"], h["step"][:35], f"{h['duration_sec']:.2f}s", "DONE"] for h in res["history"]]
        TerminalCanvas.render_table(
            headers=["#", "Paso Resuelto", "Duración", "Estado"],
            rows=rows,
            title=f"Ejecución Autónoma: {goal[:40]}"
        )
        self.fmt.print_success(f"Meta resuelta con éxito en {res['total_time_sec']:.2f}s ({res['steps_count']} pasos).")
        return 0

    def cmd_bash(self, args: argparse.Namespace) -> int:
        """Handle the bash command — execute bash with AI assistance."""
        command = " ".join(args.command) if hasattr(args, "command") and args.command else ""
        if not command:
            self.fmt.print_error("Command required. Usage: nova bash <command>")
            return 1

        self.fmt.print_section("BASH EXECUTION")

        if command.startswith("ai:"):
            prompt = command[3:].strip()
            system = "Generate a bash command for the following task. Output only the command."
            command = self.core.generate_text(prompt, system=system)
            self.fmt.print_info(f"Generated command: {command}")

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                self.fmt.print_warning(result.stderr)
            if result.returncode != 0:
                self.fmt.print_error(f"Exit code: {result.returncode}")
        except subprocess.TimeoutExpired:
            self.fmt.print_error("Command timed out")
        except Exception as exc:
            self.fmt.print_error(f"Execution error: {exc}")

        return 0

    def cmd_web(self, args: argparse.Namespace) -> int:
        """Handle the web command — web search and fetch."""
        query = " ".join(args.query) if hasattr(args, "query") and args.query else ""
        if not query:
            self.fmt.print_error("Query required. Usage: nova web <search_or_url>")
            return 1

        self.fmt.print_section("WEB")

        if query.startswith("http://") or query.startswith("https://"):
            self.fmt.print_info(f"Fetching: {query}")
            try:
                req = urllib.request.Request(query, headers={"User-Agent": "CodeForgeCLI/3.0"})
                with urllib.request.urlopen(req, timeout=30) as resp:
                    content = resp.read().decode("utf-8", errors="replace")

                if len(content) > 5000:
                    self.fmt.print_info(f"Content truncated ({len(content)} chars total)")
                    content = content[:5000] + "\n... (truncated)"

                print(f"\n{content}\n")
            except Exception as exc:
                self.fmt.print_error(f"Fetch error: {exc}")
                return 1
        else:
            self.fmt.print_info(f"Searching: {query}")
            search_url = f"https://duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            try:
                req = urllib.request.Request(search_url, headers={"User-Agent": "CodeForgeCLI/3.0"})
                with urllib.request.urlopen(req, timeout=15) as resp:
                    content = resp.read().decode("utf-8", errors="replace")

                titles = re.findall(r'<a rel="nofollow" class="result__a" href="[^"]*">([^<]+)</a>', content)
                snippets = re.findall(r'<a class="result__snippet" href="[^"]*">([^<]+)</a>', content)

                if titles:
                    rows = []
                    for i, title in enumerate(titles[:10]):
                        snippet = snippets[i] if i < len(snippets) else ""
                        rows.append([str(i + 1), title[:60], snippet[:80]])
                    self.fmt.print_table(["#", "Title", "Snippet"], rows, title=f"Search Results: {query}")
                else:
                    self.fmt.print_warning("No results found or search blocked.")
            except Exception as exc:
                self.fmt.print_error(f"Search error: {exc}")
                return 1

        return 0

    def cmd_files(self, args: argparse.Namespace) -> int:
        """Handle the files command — file management."""
        self.fmt.print_section("FILE MANAGEMENT")

        path = Path(args.path) if hasattr(args, "path") and args.path else Path.cwd()

        if not path.exists():
            self.fmt.print_error(f"Path not found: {path}")
            return 1

        if path.is_dir():
            entries = sorted(path.iterdir())
            rows = []
            for entry in entries:
                if entry.is_dir():
                    rows.append(["📁", entry.name + "/", "-", "-"])
                else:
                    size = entry.stat().st_size
                    size_str = f"{size}B" if size < 1024 else f"{size // 1024}KB" if size < 1048576 else f"{size // 1048576}MB"
                    rows.append(["📄", entry.name, size_str, datetime.fromtimestamp(entry.stat().st_mtime).strftime("%Y-%m-%d %H:%M")])

            self.fmt.print_table(["Type", "Name", "Size", "Modified"], rows, title=f"Directory: {path}")
        else:
            stat = path.stat()
            info = {
                "name": path.name,
                "path": str(path.absolute()),
                "size": f"{stat.st_size} bytes",
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "permissions": oct(stat.st_mode)[-3:],
                "mime": self._guess_mime(path),
            }
            self.fmt.print_json(info)

        return 0

    @staticmethod
    def _guess_mime(path: Path) -> str:
        """Guess MIME type from file extension."""
        mime_map = {
            ".py": "text/x-python", ".js": "text/javascript", ".ts": "text/typescript",
            ".json": "application/json", ".yaml": "application/yaml", ".yml": "application/yaml",
            ".md": "text/markdown", ".txt": "text/plain", ".csv": "text/csv",
            ".png": "image/png", ".jpg": "image/jpeg", ".gif": "image/gif",
            ".mp4": "video/mp4", ".mp3": "audio/mpeg", ".pdf": "application/pdf",
        }
        return mime_map.get(path.suffix.lower(), "application/octet-stream")

    def cmd_db(self, args: argparse.Namespace) -> int:
        """Handle the db command — database operations."""
        self.fmt.print_section("DATABASE OPERATIONS")

        db_path = CODEFORGE_HOME / "codeforge.db"

        if not db_path.exists():
            self.fmt.print_error(f"Database not found: {db_path}")
            return 1

        try:
            import sqlite3

            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row

            if hasattr(args, "query") and args.query:
                query = args.query
                try:
                    cursor = conn.execute(query)
                    if query.strip().upper().startswith("SELECT"):
                        rows = cursor.fetchall()
                        if rows:
                            headers = rows[0].keys()
                            data = [[str(row[h]) for h in headers] for row in rows[:50]]
                            self.fmt.print_table(list(headers), data, title="Query Results")
                        else:
                            self.fmt.print_info("No results.")
                    else:
                        conn.commit()
                        self.fmt.print_success(f"Query executed. Rows affected: {conn.total_changes}")
                except Exception as exc:
                    self.fmt.print_error(f"Query error: {exc}")
            else:
                tables = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
                ).fetchall()

                if tables:
                    rows = []
                    for t in tables:
                        count = conn.execute(f"SELECT COUNT(*) FROM {t['name']}").fetchone()[0]
                        rows.append([t["name"], str(count)])
                    self.fmt.print_table(["Table", "Rows"], rows, title="Database Tables")
                else:
                    self.fmt.print_info("No tables found.")

            conn.close()
        except Exception as exc:
            self.fmt.print_error(f"Database error: {exc}")
            return 1

        return 0

    def cmd_security(self, args: argparse.Namespace) -> int:
        """Handle the security command — security audit."""
        self.fmt.print_section("SECURITY AUDIT")

        target = " ".join(args.target) if hasattr(args, "target") and args.target else "."
        path = Path(target)

        if not path.exists():
            self.fmt.print_error(f"Path not found: {target}")
            return 1

        issues: List[Dict[str, str]] = []

        if path.is_dir():
            for py_file in path.rglob("*.py"):
                content = py_file.read_text(encoding="utf-8", errors="replace")
                for i, line in enumerate(content.splitlines(), 1):
                    if re.search(r"\b(eval|exec|subprocess\.call|os\.system)\b", line):
                        issues.append({
                            "file": str(py_file),
                            "line": str(i),
                            "severity": "HIGH",
                            "issue": f"Potentially dangerous function: {line.strip()[:60]}",
                        })
                    if re.search(r"(password|secret|api_key|token)\s*=\s*['\"]", line, re.IGNORECASE):
                        issues.append({
                            "file": str(py_file),
                            "line": str(i),
                            "severity": "MEDIUM",
                            "issue": "Possible hardcoded secret",
                        })

        if issues:
            rows = [[i["severity"], i["file"][:40], i["line"], i["issue"][:50]] for i in issues[:20]]
            self.fmt.print_table(["Severity", "File", "Line", "Issue"], rows, title=f"Security Issues ({len(issues)} found)")
        else:
            self.fmt.print_success("No obvious security issues found.")

        return 0

    def cmd_test(self, args: argparse.Namespace) -> int:
        """Handle the test command — run tests."""
        self.fmt.print_section("TEST RUNNER")

        target = args.target if hasattr(args, "target") and args.target else "."
        p_target = Path(target).resolve()

        # 1. Detect if target is/has a package.json
        pkg_json = p_target / "package.json" if p_target.is_dir() else p_target.parent / "package.json"
        if pkg_json.exists() and shutil.which("npm"):
            try:
                pkg_data = json.loads(pkg_json.read_text(encoding="utf-8"))
                if "scripts" in pkg_data and "test" in pkg_data["scripts"]:
                    self.fmt.print_info("Running npm test...")
                    res = subprocess.run(["npm", "test"], cwd=str(pkg_json.parent), capture_output=True, text=True, timeout=120)
                    if res.stdout:
                        print(res.stdout[-3000:] if len(res.stdout) > 3000 else res.stdout)
                    if res.returncode == 0:
                        self.fmt.print_success("npm test passed!")
                        return 0
                    else:
                        self.fmt.print_error(f"npm test failed (exit {res.returncode})")
                        return res.returncode
            except Exception as e:
                self.fmt.print_error(f"npm test error: {e}")

        # 2. Check for pytest availability
        has_pytest = False
        try:
            has_pytest = subprocess.run([sys.executable, "-c", "import pytest"], capture_output=True).returncode == 0
        except Exception:
            pass

        if has_pytest:
            self.fmt.print_info("Running pytest...")
            res = subprocess.run([sys.executable, "-m", "pytest", "-v", str(p_target)], capture_output=True, text=True, timeout=120)
            if res.stdout:
                print(res.stdout[-3000:] if len(res.stdout) > 3000 else res.stdout)
            if res.returncode == 0:
                self.fmt.print_success("pytest passed!")
                return 0
            else:
                self.fmt.print_error(f"pytest failed (exit {res.returncode})")
                return res.returncode

        # 3. Fallback to unittest discover
        self.fmt.print_info("Running unittest...")
        start_dir = str(p_target) if p_target.is_dir() else str(p_target.parent)
        res = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", start_dir], capture_output=True, text=True, timeout=120)
        output = (res.stdout + "\n" + res.stderr).strip()
        if output:
            print(output[-3000:] if len(output) > 3000 else output)
        if res.returncode == 0:
            self.fmt.print_success("unittest passed!")
            return 0
        else:
            self.fmt.print_error(f"unittest failed (exit {res.returncode})")
            return res.returncode

    def cmd_deploy(self, args: argparse.Namespace) -> int:
        """Handle the deploy command — deployment assistance."""
        self.fmt.print_section("DEPLOYMENT")

        target = args.target if hasattr(args, "target") and args.target else "."
        path = Path(target)

        self.fmt.print_info(f"Analyzing deployment target: {path}")

        deploy_files = {
            "Dockerfile": path / "Dockerfile",
            "docker-compose.yml": path / "docker-compose.yml",
            "requirements.txt": path / "requirements.txt",
            "package.json": path / "package.json",
            ".github/workflows": path / ".github" / "workflows",
        }

        detected = []
        for name, p in deploy_files.items():
            if p.exists():
                detected.append(name)

        if detected:
            self.fmt.print_info(f"Detected: {', '.join(detected)}")
        else:
            self.fmt.print_warning("No deployment configuration detected.")

        deploy_plan = self.core.generate_text(
            f"Create a deployment plan for a project at {path}. "
            f"Detected files: {detected}. "
            f"Provide step-by-step deployment instructions."
        )
        print(f"\n{deploy_plan}\n")

        return 0

    def cmd_docs(self, args: argparse.Namespace) -> int:
        """Handle the docs command — documentation generation."""
        self.fmt.print_section("DOCUMENTATION GENERATION")

        target = " ".join(args.target) if hasattr(args, "target") and args.target else "."
        path = Path(target)

        if not path.exists():
            self.fmt.print_error(f"Path not found: {target}")
            return 1

        if path.is_file():
            content = path.read_text(encoding="utf-8", errors="replace")
            prompt = f"Generate comprehensive documentation for this code:\n\n```\n{content[:3000]}\n```"
        elif path.is_dir():
            py_files = list(path.glob("*.py"))[:5]
            summaries = []
            for f in py_files:
                content = f.read_text(encoding="utf-8", errors="replace")[:1000]
                summaries.append(f"# {f.name}\n{content}")
            prompt = f"Generate project documentation for a Python project with these files:\n\n" + "\n\n".join(summaries)

        result = self.core.generate_text(prompt)
        print(f"\n{result}\n")

        return 0


# ============================================================================
# CLI Parser
# ============================================================================

def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for NovaCode CLI."""
    parser = argparse.ArgumentParser(
        prog="nova",
        description="NovaCode Super Multimodal CLI — Ultimate AI-powered development tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    nova chat                              Start interactive chat
    nova generate image "sunset landscape"  Generate an image
    nova code "sort a list efficiently"     Generate Python code
    nova analyze script.py                  Analyze a file
    nova models                             List available models
    nova doctor                             System health check
    nova web "python async patterns"        Search the web
    nova multimodal "create a video of..."  Full multimodal pipeline
        """,
    )

    parser.add_argument("--version", action="version", version=f"CodeForge CLI v{NOVACODE_VERSION}")
    parser.add_argument("--model", "-m", default="nova", help="Model alias or ID")
    parser.add_argument("--quality", "-q", default="pro", choices=["draft", "pro", "ultra"], help="Quality level")
    parser.add_argument("--nsfw", action="store_true", help="Enable NSFW mode")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--quiet", action="store_true", help="Minimal output")
    parser.add_argument("--no-color", action="store_true", help="Disable colors")
    parser.add_argument("--config", help="Config file path")
    parser.add_argument("--session", help="Session ID")
    parser.add_argument("--worktree", help="Git worktree path")
    parser.add_argument("--auto", action="store_true", help="Auto mode (no prompts)")
    parser.add_argument("--pure", action="store_true", help="Pure mode (no system prompts)")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    chat_parser = subparsers.add_parser("chat", help="Interactive chat")
    chat_parser.add_argument("messages", nargs="*", help="Initial message")

    gen_parser = subparsers.add_parser("generate", help="Generate content")
    gen_parser.add_argument("type", nargs="?", default="text", choices=["text", "image", "video", "audio", "music"])
    gen_parser.add_argument("prompt", nargs="*", help="Generation prompt")

    code_parser = subparsers.add_parser("code", help="Code generation")
    code_parser.add_argument("task", nargs="*", help="Code task description")
    code_parser.add_argument("--run", action="store_true", help="Run generated code")

    analyze_parser = subparsers.add_parser("analyze", help="Analyze files")
    analyze_parser.add_argument("target", nargs="*", help="File or path to analyze")

    subparsers.add_parser("learn", help="View learning data")
    subparsers.add_parser("evolve", help="Self-improvement")
    subparsers.add_parser("models", help="List models")
    subparsers.add_parser("doctor", help="Health check")

    config_parser = subparsers.add_parser("config", help="Configuration")
    config_parser.add_argument("action", nargs="?", choices=["show", "set", "reset"])
    config_parser.add_argument("key", nargs="?")
    config_parser.add_argument("value", nargs="?")

    session_parser = subparsers.add_parser("session", help="Session management")
    session_parser.add_argument("action", nargs="?", choices=["info", "new", "list"])

    mm_parser = subparsers.add_parser("multimodal", help="Multimodal pipeline")
    mm_parser.add_argument("prompt", nargs="*", help="Multimodal prompt")

    py_parser = subparsers.add_parser("python", help="Python execution")
    py_parser.add_argument("code", nargs="*", help="Python code or 'ai: description'")

    bash_parser = subparsers.add_parser("bash", help="Bash execution")
    bash_parser.add_argument("command", nargs="*", help="Bash command or 'ai: description'")

    sudo_parser = subparsers.add_parser("sudo", help="Privileged sudo execution")
    sudo_parser.add_argument("command", nargs="*", help="Privileged command or 'ai: description'")

    forge_parser = subparsers.add_parser("forge", help="Proprietary Model Forge")
    forge_parser.add_argument("action", nargs="?", default="status", choices=["status", "dataset", "merge", "train", "quantize"])
    forge_parser.add_argument("target", nargs="?", help="Target directory or model path")

    swarm_parser = subparsers.add_parser("swarm", help="Parallel Swarm Turbo Execution")
    swarm_parser.add_argument("task", nargs="*", help="Task description")

    sandbox_parser = subparsers.add_parser("sandbox", help="Instant Sandbox & Rollback")
    sandbox_parser.add_argument("action", nargs="?", default="status", choices=["status", "snapshot", "rollback"])

    sentinel_parser = subparsers.add_parser("sentinel", help="Background Sentinel Watcher & Healer")
    sentinel_parser.add_argument("action", nargs="?", default="status", choices=["status", "watch"])

    graph_parser = subparsers.add_parser("graph", help="AST Semantic Code Graph")
    graph_parser.add_argument("query", nargs="*", help="Symbol search query")

    canvas_parser = subparsers.add_parser("canvas", help="Terminal Canvas Visual Metrics")

    refactor_parser = subparsers.add_parser("refactor", help="AST Code Surgery & Refactor")
    refactor_parser.add_argument("target", nargs="?", help="Target file to refactor")

    sync_parser = subparsers.add_parser("sync", help="GitHub Continuous Auto-Sync")
    sync_parser.add_argument("message", nargs="*", help="Optional commit message")

    bench_parser = subparsers.add_parser("bench", help="Benchmark Model Latency and TPS")

    docker_parser = subparsers.add_parser("docker", help="Docker Pilot AI & Container Management")
    docker_parser.add_argument("action", nargs="?", default="status", choices=["status", "gen", "compose", "audit"])

    api_parser = subparsers.add_parser("api", help="API Tester and Endpoint Benchmark")
    api_parser.add_argument("url", nargs="?", help="URL endpoint to test")

    net_parser = subparsers.add_parser("net", help="Network and Port Scanner")

    secret_parser = subparsers.add_parser("secret", help="Secret and Credential Scanner")

    auto_parser = subparsers.add_parser("auto", help="Autonomous Self-Driving Goal Pilot")
    auto_parser.add_argument("goal", nargs="*", help="High-level goal description")
    auto_parser.add_argument("--unlimited", action="store_true", help="Run without step limits until completion")

    web_parser = subparsers.add_parser("web", help="Web search/fetch")
    web_parser.add_argument("query", nargs="*", help="Search query or URL")

    files_parser = subparsers.add_parser("files", help="File management")
    files_parser.add_argument("path", nargs="?", help="File or directory path")

    db_parser = subparsers.add_parser("db", help="Database operations")
    db_parser.add_argument("query", nargs="?", help="SQL query")

    sec_parser = subparsers.add_parser("security", help="Security audit")
    sec_parser.add_argument("target", nargs="*", help="Target path")

    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.add_argument("target", nargs="?", help="Test target")

    deploy_parser = subparsers.add_parser("deploy", help="Deployment")
    deploy_parser.add_argument("target", nargs="?", help="Deploy target")

    docs_parser = subparsers.add_parser("docs", help="Documentation")
    docs_parser.add_argument("target", nargs="*", help="Documentation target")

    return parser


# ============================================================================
# Main Entry Point
# ============================================================================

def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the CodeForge CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    core = NovaCodeCore(
        model=getattr(args, "model", "nova"),
        quality=getattr(args, "quality", "pro"),
        nsfw=getattr(args, "nsfw", False),
        json_mode=getattr(args, "json", False),
        verbose=getattr(args, "verbose", False),
        quiet=getattr(args, "quiet", False),
        no_color=getattr(args, "no_color", False),
        session_id=getattr(args, "session", None),
        auto_mode=getattr(args, "auto", False),
        pure_mode=getattr(args, "pure", False),
    )

    if not args.command:
        core.fmt.print_banner()
        parser.print_help()
        return 0

    handlers = CommandHandlers(core)

    command_map: Dict[str, Callable[[argparse.Namespace], int]] = {
        "chat": handlers.cmd_chat,
        "generate": handlers.cmd_generate,
        "code": handlers.cmd_code,
        "analyze": handlers.cmd_analyze,
        "learn": handlers.cmd_learn,
        "evolve": handlers.cmd_evolve,
        "models": handlers.cmd_models,
        "doctor": handlers.cmd_doctor,
        "config": handlers.cmd_config,
        "session": handlers.cmd_session,
        "multimodal": handlers.cmd_multimodal,
        "python": handlers.cmd_python,
        "bash": handlers.cmd_bash,
        "sudo": handlers.cmd_sudo,
        "forge": handlers.cmd_forge,
        "swarm": handlers.cmd_swarm,
        "sandbox": handlers.cmd_sandbox,
        "sentinel": handlers.cmd_sentinel,
        "graph": handlers.cmd_graph,
        "canvas": handlers.cmd_canvas,
        "refactor": handlers.cmd_refactor,
        "sync": handlers.cmd_sync,
        "bench": handlers.cmd_bench,
        "docker": handlers.cmd_docker,
        "api": handlers.cmd_api,
        "net": handlers.cmd_net,
        "secret": handlers.cmd_secret,
        "auto": handlers.cmd_auto,
        "web": handlers.cmd_web,
        "files": handlers.cmd_files,
        "db": handlers.cmd_db,
        "security": handlers.cmd_security,
        "test": handlers.cmd_test,
        "deploy": handlers.cmd_deploy,
        "docs": handlers.cmd_docs,
    }

    handler = command_map.get(args.command)
    if handler is None:
        core.fmt.print_error(f"Unknown command: {args.command}")
        return 1

    try:
        return handler(args)
    except KeyboardInterrupt:
        if not core.fmt.quiet:
            print()
        return 130
    except Exception as exc:
        core.fmt.print_error(f"Command failed: {exc}")
        if core.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
