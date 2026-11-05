import http.server
import socketserver
import mimetypes
import sys
from pathlib import Path

# Fix Windows registry MIME issues for ES modules
mimetypes.init()
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("application/javascript", ".mjs")
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("application/json", ".json")
mimetypes.add_type("image/webp", ".webp")
mimetypes.add_type("font/woff2", ".woff2")

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
DIRECTORY = Path(__file__).resolve().parent

class ArtWebHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)

class ThreadedServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True

if __name__ == "__main__":
    for port in [PORT, 8081, 8082, 8888, 5000]:
        try:
            with ThreadedServer(("127.0.0.1", port), ArtWebHandler) as httpd:
                print(f"ART_WEB_SERVER_READY:http://127.0.0.1:{port}/")
                sys.stdout.flush()
                httpd.serve_forever()
        except OSError:
            continue
