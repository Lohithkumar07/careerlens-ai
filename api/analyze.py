"""POST /api/analyze  ->  role prediction, skills, JD match."""
import json
import os
import sys
from http.server import BaseHTTPRequestHandler

_HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (_HERE, os.path.dirname(_HERE)):  # api/ (for _common) and project root (for careerlens)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from _common import HEADERS  # noqa: E402  (also fixes sys.path)
from careerlens.service import MAX_CHARS, handle_analyze  # noqa: E402


class handler(BaseHTTPRequestHandler):
    def _send(self, status, body):
        data = json.dumps(body).encode("utf-8")
        self.send_response(status)
        for k, v in HEADERS.items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self._send(204, {})

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            return self._send(400, {"error": "Invalid Content-Length."})
        if length > MAX_CHARS * 4:
            return self._send(413, {"error": "Request body too large."})
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except (json.JSONDecodeError, UnicodeDecodeError):
            return self._send(400, {"error": "Body must be valid JSON."})
        status, body = handle_analyze(payload)
        self._send(status, body)

    def do_GET(self):
        self._send(405, {"error": "Use POST."})
