"""GET /api/health  ->  model status and the list of target roles."""
import json
import os
import sys
from http.server import BaseHTTPRequestHandler

_HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (_HERE, os.path.dirname(_HERE)):  # api/ (for _common) and project root (for careerlens)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from _common import HEADERS  # noqa: E402
from careerlens.service import health, roles  # noqa: E402


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        data = json.dumps({**health(), "target_roles": roles()}).encode("utf-8")
        self.send_response(200)
        for k, v in HEADERS.items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
