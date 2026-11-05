"""
server_helper.py - Robust Local HTTP Server Daemon for art-web E2E Tests.

Features:
- Dynamically allocates a free local port (or binds to a requested port).
- Runs a multithreaded HTTP server daemon serving the project root directory.
- Guarantees correct MIME types for ES Modules (.js as application/javascript),
  fonts (.woff2, .woff), images (.webp, .jpg, .svg), and stylesheets (.css).
- Provides clean thread-safe startup, health checking, and graceful shutdown.
- Provides context manager support for safe resource management in tests.
"""

import http.server
import mimetypes
import os
import socket
import socketserver
import threading
import time
import urllib.request
from pathlib import Path
from typing import Optional

# Ensure standard MIME types are recognized
mimetypes.init()
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("application/javascript", ".mjs")
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("application/json", ".json")
mimetypes.add_type("image/webp", ".webp")
mimetypes.add_type("image/jpeg", ".jpg")
mimetypes.add_type("image/jpeg", ".jpeg")
mimetypes.add_type("image/png", ".png")
mimetypes.add_type("image/svg+xml", ".svg")
mimetypes.add_type("font/woff2", ".woff2")
mimetypes.add_type("font/woff", ".woff")
mimetypes.add_type("font/ttf", ".ttf")

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """Threaded TCP server allowing non-blocking concurrent requests."""
    allow_reuse_address = True
    daemon_threads = True


class ArtWebHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom request handler with strict MIME types and quiet logging."""

    def __init__(self, *args, **kwargs):
        # Serve directly from project root
        super().__init__(*args, directory=str(PROJECT_ROOT), **kwargs)

    def guess_type(self, path):
        """Override MIME type detection to guarantee ES Module compatibility."""
        path_str = str(path).lower()
        if path_str.endswith(".js") or path_str.endswith(".mjs"):
            return "application/javascript"
        if path_str.endswith(".css"):
            return "text/css"
        if path_str.endswith(".json"):
            return "application/json"
        if path_str.endswith(".webp"):
            return "image/webp"
        if path_str.endswith(".woff2"):
            return "font/woff2"
        if path_str.endswith(".woff"):
            return "font/woff"
        if path_str.endswith(".ttf"):
            return "font/ttf"
        return super().guess_type(path)

    def end_headers(self):
        """Add permissive CORS and caching headers for local test execution."""
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, HEAD, OPTIONS")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

    def log_message(self, format, *args):
        """Suppress standard HTTP request logging noise in tests."""
        pass


def find_free_port(start_port: int = 8900, max_port: int = 9999) -> int:
    """Find an available port on localhost."""
    for port in range(start_port, max_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    # Fallback to ephemeral port assigned by OS
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class LocalServer:
    """Daemon HTTP server manager for running E2E tests."""

    def __init__(self, port: Optional[int] = None, host: str = "127.0.0.1"):
        self.host = host
        self.port = port or find_free_port()
        self.httpd: Optional[ThreadedTCPServer] = None
        self.thread: Optional[threading.Thread] = None
        self._running = False

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    def start(self, timeout: float = 8.0) -> "LocalServer":
        """Start the HTTP server daemon in a background thread."""
        if self._running:
            return self

        # Initialize server
        self.httpd = ThreadedTCPServer((self.host, self.port), ArtWebHTTPRequestHandler)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        self._running = True

        # Health check poll
        health_url = f"{self.base_url}/index.html"
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                with urllib.request.urlopen(health_url, timeout=1.0) as resp:
                    if resp.status == 200:
                        return self
            except Exception:
                time.sleep(0.05)

        self.stop()
        raise TimeoutError(f"Local server failed to respond at {health_url} within {timeout}s")

    def stop(self):
        """Stop and clean up the server."""
        if not self._running:
            return
        self._running = False
        if self.httpd:
            try:
                self.httpd.shutdown()
                self.httpd.server_close()
            except Exception:
                pass
            self.httpd = None
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
            self.thread = None

    def __enter__(self) -> "LocalServer":
        return self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


if __name__ == "__main__":
    print(f"Testing server_helper from {PROJECT_ROOT}...")
    with LocalServer() as srv:
        print(f"Server started at {srv.base_url}")
        req = urllib.request.urlopen(f"{srv.base_url}/index.html")
        print(f"Response status: {req.status}")
        assert req.status == 200
        print("Server helper test passed successfully!")
