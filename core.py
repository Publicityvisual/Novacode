def is_connected() -> bool:
    """Simple network connectivity check."""
    try:
        import socket
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

def update_project() -> None:
    """Simulate checking for updates."""
    print("Checked for updates – no action taken.")

class NovaCodeCore:
    def __init__(self, offline: bool = False):
        self.offline = offline
        if not offline:
            self._ensure_network()

    def _ensure_network(self) -> None:
        if not is_connected():
            raise RuntimeError("Network is not available")