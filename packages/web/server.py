"""
NovaCode Web Dashboard Server
Serves the interactive NovaCode Web UI and connects to the local NovaCode proxy.
"""
import http.server
import socketserver
import os
import sys
import webbrowser
from pathlib import Path

WEB_DIR = Path(__file__).resolve().parent
PORT = int(os.environ.get("NOVACODE_WEB_PORT", "18795"))

class NovaCodeWebHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def log_message(self, format, *args):
        # Silence default request spam
        pass

def start_server(port: int = PORT, open_browser: bool = True) -> int:
    os.chdir(WEB_DIR)
    print(f"\033[1;36m[NovaCode Web]\033[0m Starting Dashboard at http://localhost:{port}")
    if open_browser:
        try:
            webbrowser.open(f"http://localhost:{port}")
        except Exception:
            pass

    with socketserver.TCPServer(("", port), NovaCodeWebHandler) as httpd:
        try:
            print(f"\033[32m✓ [NovaCode Web]\033[0m Running on http://127.0.0.1:{port} (Press Ctrl+C to stop)")
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\033[90m[NovaCode Web] Dashboard stopped.\033[0m")
            return 0
    return 0

if __name__ == "__main__":
    sys.exit(start_server())
