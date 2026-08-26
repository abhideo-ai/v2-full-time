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
  GET  /api/jobs           every application, its launcher tab and both scores

  no-store on HTML/JSON/JS/CSS, so a pinned tab's refresh really does refresh.

Binds 127.0.0.1, NOT 0.0.0.0 the way `python -m http.server` does. This process
writes to a database, so it must not be reachable from the network.

If PostgreSQL is unreachable the API answers 503 and the page falls back to
localStorage, telling you on the page that it is not saving. Read-only browsing
of the workspace keeps working either way. `/api/jobs` answers 503 the same way
and the launcher says the list is unavailable rather than rendering nothing,
which would read as "no applications".

Two databases, never one connection: `db` is `v2_daily` (read-write, the daily
log), `jobs_db` is `jobs_tracker_v2` (read-only, the launcher). v1's
`jobs_tracker` is a third database and nothing here opens it.
"""
import argparse
import json
import socket
import sys
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))

import db  # noqa: E402
import jobs_db  # noqa: E402

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
        if url.path == "/api/jobs":
            try:
                return self._json(200, jobs_db.launcher())
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
        print(f"[serve] WARNING: v2_daily unreachable ({exc})", file=sys.stderr)
        print("[serve] the daily log will fall back to localStorage and say so", file=sys.stderr)
    try:
        rows = jobs_db.applications()
        print(f"[serve] jobs_tracker_v2 ok — {len(rows)} application(s)", file=sys.stderr)
    except Exception as exc:                                    # noqa: BLE001
        print(f"[serve] WARNING: jobs_tracker_v2 unreachable ({exc})", file=sys.stderr)
        print("[serve] the launcher will say the list is unavailable", file=sys.stderr)
    handler = partial(Handler, directory=str(ROOT))

    # Bind BOTH loopback families, not just 127.0.0.1.
    #
    # macOS resolves "localhost" to ::1 before 127.0.0.1. Binding only the IPv4
    # loopback left ::1 free, so a stray `python3 -m http.server 8006` could take
    # it and silently shadow this server for anyone browsing to localhost:8006 --
    # the page then reports "the server answered 404" while curl against
    # 127.0.0.1 says everything is fine. That happened twice in one night.
    #
    # Holding both means a competing server fails loudly with EADDRINUSE instead.
    # Still loopback-only: neither :: nor 0.0.0.0, because this process writes to
    # a database and must not be reachable from the network.
    servers = []
    for family, host in ((socket.AF_INET, args.host), (socket.AF_INET6, "::1")):
        if family is socket.AF_INET6 and args.host != "127.0.0.1":
            continue                       # explicit --host: honour it exactly
        klass = type("Srv", (ThreadingHTTPServer,), {"address_family": family})
        try:
            servers.append(klass((host, args.port), handler))
        except OSError as exc:
            if family is socket.AF_INET6:
                print(f"[serve] note: no IPv6 loopback ({exc}); IPv4 only", file=sys.stderr)
                continue
            raise
    if not servers:
        raise SystemExit(f"[serve] could not bind port {args.port}")

    for srv in servers[1:]:
        threading.Thread(target=srv.serve_forever, daemon=True).start()
    bound = ", ".join(f"{s.server_address[0]}" for s in servers)
    print(f"[serve] http://localhost:{args.port}/daily/  (bound: {bound})", file=sys.stderr)
    try:
        servers[0].serve_forever()
    except KeyboardInterrupt:
        print("\n[serve] stopped", file=sys.stderr)
    finally:
        for s in servers:
            s.server_close()


if __name__ == "__main__":
    main()
