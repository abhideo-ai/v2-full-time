#!/usr/bin/env python3
"""Static server for the workspace, plus the daily log's state API.

    automation/.venv/bin/python automation/serve.py            # port 8006
    automation/.venv/bin/python automation/serve.py --port N

This REPLACES `python3 -m http.server 8006`. Same port, same URLs, so a pinned
tab keeps working. What it adds:

  GET  /__daily_api        {"ok": true, "store": "postgresql"} — capability probe
  GET  /api/state          current task state
  POST /api/ops            apply operations, return the new state
  GET  /api/history?limit  recent task events, newest first

  no-store on HTML/JSON/JS/CSS, so a pinned tab's refresh really does refresh.

Binds 127.0.0.1, NOT 0.0.0.0 the way `python -m http.server` does. This process
writes to a database, so it must not be reachable from the network.

If PostgreSQL is unreachable the API answers 503 and the page falls back to
localStorage, telling you on the page that it is not saving. Read-only browsing
of the workspace keeps working either way.
"""
import argparse
import json
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))

import db  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MAX_BODY = 1 << 20  # 1 MB; a realistic batch is a few hundred bytes
NO_STORE = (".html", ".json", ".js", ".css")


class Handler(SimpleHTTPRequestHandler):
    # ---- helpers ---------------------------------------------------------
    def _json(self, code: int, payload) -> None:
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _body(self) -> dict:
        try:
            length = int(self.headers.get("Content-Length", 0))
        except ValueError as exc:
            raise db.OpError("bad Content-Length") from exc
        if length <= 0 or length > MAX_BODY:
            raise db.OpError(f"body must be 1..{MAX_BODY} bytes")
        try:
            return json.loads(self.rfile.read(length))
        except json.JSONDecodeError as exc:
            raise db.OpError(f"invalid JSON: {exc}") from exc

    def end_headers(self) -> None:
        # A pinned tab is refreshed to see what changed; a cached page defeats
        # the whole point. These files are small, so no-store costs nothing.
        path = urlparse(self.path).path
        if path.endswith(NO_STORE) or path.endswith("/"):
            self.send_header("Cache-Control", "no-store")
        super().end_headers()

    # ---- routes ----------------------------------------------------------
    def do_GET(self) -> None:                                   # noqa: N802
        url = urlparse(self.path)
        if url.path == "/__daily_api":
            try:
                db.get_state()
            except Exception as exc:                            # noqa: BLE001
                return self._json(503, {"ok": False, "error": str(exc)})
            return self._json(200, {"ok": True, "store": "postgresql"})
        if url.path == "/api/state":
            try:
                return self._json(200, db.get_state())
            except Exception as exc:                            # noqa: BLE001
                return self._json(503, {"error": f"database unreachable: {exc}"})
        if url.path == "/api/history":
            try:
                limit = min(int(parse_qs(url.query).get("limit", ["100"])[0]), 1000)
            except ValueError:
                limit = 100
            try:
                return self._json(200, {"events": db.history(limit)})
            except Exception as exc:                            # noqa: BLE001
                return self._json(503, {"error": f"database unreachable: {exc}"})
        return super().do_GET()

    def do_POST(self) -> None:                                  # noqa: N802
        if urlparse(self.path).path != "/api/ops":
            return self._json(404, {"error": "no such endpoint"})
        try:
            payload = self._body()
            return self._json(200, db.apply_ops(payload.get("ops")))
        except db.OpError as exc:
            return self._json(400, {"error": str(exc)})
        except Exception as exc:                                # noqa: BLE001
            return self._json(503, {"error": f"database unreachable: {exc}"})

    def log_message(self, fmt: str, *args) -> None:
        path = urlparse(self.path).path
        if self.command != "GET" or not path.startswith(("/static", "/style")):
            sys.stderr.write(f"[serve] {self.command} {path} -> {args[1]}\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8006)
    ap.add_argument("--host", default="127.0.0.1")
    args = ap.parse_args()
    try:
        state = db.get_state()
        print(f"[serve] postgresql ok — {len(state['tasks'])} task(s) stored", file=sys.stderr)
    except Exception as exc:                                    # noqa: BLE001
        print(f"[serve] WARNING: database unreachable ({exc})", file=sys.stderr)
        print("[serve] the page will fall back to localStorage and say so", file=sys.stderr)
    handler = partial(Handler, directory=str(ROOT))
    with ThreadingHTTPServer((args.host, args.port), handler) as httpd:
        print(f"[serve] http://{args.host}:{args.port}/daily/", file=sys.stderr)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[serve] stopped", file=sys.stderr)


if __name__ == "__main__":
    main()
