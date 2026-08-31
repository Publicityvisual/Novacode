def is_connected() -> bool:
    """Simple network connectivity check."""
    try:
        import socket
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False


def check_host(host: str) -> bool:
    """Check if a host is reachable via HTTP."""
    import urllib.request, urllib.error
    try:
        urllib.request.urlopen(f"https://{host}", timeout=5)
        return True
    except urllib.error.URLError:
        return False


def update_project(host: str = "github.com") -> None:
    """Simulate checking for updates with graceful error handling."""
    print(f"Checked for updates on {host} – no action taken.")


class NovaCodeCore:
    def __init__(self, offline: bool = False):
        self.offline = offline
        if not offline:
            self._ensure_network()

    def _ensure_network(self) -> None:
        if not is_connected():
            raise RuntimeError("Network is not available")