"""Local dev server that mimics Vercel: static files from ./public + /api/* routes.

    python dev_server.py            # http://localhost:8000
"""
import json
import mimetypes
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from careerlens.service import MAX_CHARS, handle_analyze, health, roles

PUBLIC = Path(__file__).parent / "public"


class Dev(BaseHTTPRequestHandler):
    def _json(self, status, body):
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path.startswith("/api/health"):
            return self._json(200, {**health(), "target_roles": roles()})
        rel = "index.html" if self.path in ("/", "") else self.path.lstrip("/").split("?")[0]
        f = (PUBLIC / rel).resolve()
        if PUBLIC.resolve() not in f.parents and f != PUBLIC.resolve() or not f.is_file():
            return self._json(404, {"error": "Not found"})
        data = f.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mimetypes.guess_type(f.name)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if not self.path.startswith("/api/analyze"):
            return self._json(404, {"error": "Not found"})
        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_CHARS * 4:
            return self._json(413, {"error": "Request body too large."})
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except ValueError:
            return self._json(400, {"error": "Body must be valid JSON."})
        self._json(*handle_analyze(payload))


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f"CareerLens dev server on http://localhost:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), Dev).serve_forever()
