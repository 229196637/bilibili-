from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, List

from ..core import PicGoCore


class PypicgoHandler(BaseHTTPRequestHandler):
    server_version = "pypicgo/0.1"
    core = PicGoCore()

    def _json(self, status: int, payload: Dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/health":
            self._json(200, {"status": "ok"})
            return
        if self.path == "/history":
            self._json(200, {"history": self.core.history.list()})
            return
        self._json(404, {"error": "not_found"})

    def do_POST(self) -> None:
        path, _, query = self.path.partition("?")
        if path != "/upload":
            self._json(404, {"error": "not_found"})
            return
        length = int(self.headers.get("Content-Length", "0"))
        data = self.rfile.read(length)
        try:
            payload = json.loads(data.decode("utf-8"))
        except Exception:
            self._json(400, {"error": "invalid_json"})
            return
        files: List[str] = payload.get("files") or []
        # parse query string
        from urllib.parse import parse_qs
        qs = parse_qs(query)
        host = qs.get("host", [None])[0] or payload.get("host")
        fmt = qs.get("format", [None])[0] or payload.get("format")
        try:
            text = self.core.run(files, host=host, fmt=fmt)
            self._json(200, {"text": text})
        except Exception as e:
            self._json(500, {"error": str(e)})


def run_server(host: str = "127.0.0.1", port: int = 8765) -> None:
    server = HTTPServer((host, port), PypicgoHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    run_server()

