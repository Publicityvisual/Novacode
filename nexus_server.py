#!/usr/bin/env python3
"""
NOVACODE HTTP SERVER — Backend local para clientes externos.
Expone la API de NovaCode por HTTP + SSE para integración con editores, TUI web, etc.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

try:
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from socketserver import ThreadingMixIn
except ImportError:
    print("❌ HTTP server no disponible en esta versión de Python")
    raise SystemExit(1)


class NovaCodeHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def _send_json(self, status: int, data: dict):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self._send_json(200, {"status": "ok", "service": "novacode"})
        elif self.path == "/models":
            try:
                sys_path = str(Path.home() / ".novacode/memory")
                if sys_path not in sys.path:
                    sys.path.insert(0, sys_path)
                from nexus_router import NexusRouter
                router = NexusRouter()
                routes = {
                    t.value: {"model": r.model_id, "fallback": r.fallback}
                    for t, r in router.routes.items()
                }
                self._send_json(200, {"models": routes})
            except Exception as e:
                self._send_json(500, {"error": str(e)})
        else:
            self._send_json(404, {"error": "Not found"})

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self._send_json(400, {"error": "Invalid JSON"})
            return

        if self.path == "/run":
            query = data.get("query", "")
            model = data.get("model")
            task = data.get("task")
            if not query:
                self._send_json(400, {"error": "Missing 'query'"})
                return
            try:
                sys_path = str(Path.home() / ".novacode/memory")
                if sys_path not in sys.path:
                    sys.path.insert(0, sys_path)
                import asyncio
                from nexus_orchestrator import get_orchestrator
                from nexus_router import TaskType
                orchestrator = get_orchestrator()
                if task and not model:
                    try:
                        task_type = TaskType(task.lower())
                        model = orchestrator.router.get_optimal_model(task_type)
                    except ValueError:
                        pass
                response = asyncio.run(
                    orchestrator.process_request(
                        query,
                        force_model=model,
                        has_image=False,
                        stream=False,
                    )
                )
                self._send_json(200, {
                    "content": response.content,
                    "model": response.model_used,
                    "task": response.task_type,
                    "latency_ms": response.latency_ms,
                    "tokens": response.tokens_used,
                })
            except Exception as e:
                self._send_json(500, {"error": str(e)})
        else:
            self._send_json(404, {"error": "Not found"})


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


def serve(host: str = "127.0.0.1", port: int = 0) -> None:
    server = ThreadedHTTPServer((host, port), NovaCodeHandler)
    actual_port = server.server_address[1]
    print(f"🚀 NovaCode HTTP server running on http://{host}:{actual_port}")
    print("   Endpoints:")
    print("     GET  /health")
    print("     GET  /models")
    print("     POST /run")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        server.shutdown()
