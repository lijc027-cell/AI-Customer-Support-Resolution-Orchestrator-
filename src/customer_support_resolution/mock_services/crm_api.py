"""Local CRM HTTP mock used by integration tests."""

from __future__ import annotations

import json
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread


def _build_handler(accounts: dict[str, dict], required_token: str | None):
    class CRMHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            if not self._is_authorized():
                self._write_json(401, {"error": "Unauthorized"})
                return
            account_id = self._read_account_id()
            if account_id is None:
                self._write_json(404, {"error": "Not found"})
                return

            payload = accounts.get(account_id)
            if payload is None:
                self._write_json(404, {"error": "Account not found"})
                return

            self._write_json(200, payload)

        def log_message(self, format: str, *args) -> None:  # noqa: A003
            return

        def _read_account_id(self) -> str | None:
            prefix = "/accounts/"
            if not self.path.startswith(prefix):
                return None
            account_id = self.path.removeprefix(prefix).strip("/")
            return account_id or None

        def _is_authorized(self) -> bool:
            if required_token is None:
                return True
            return self.headers.get("Authorization") == f"Bearer {required_token}"

        def _write_json(self, status_code: int, payload: dict) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return CRMHandler


@contextmanager
def run_mock_crm_server(accounts: dict[str, dict], required_token: str | None = None):
    server = ThreadingHTTPServer(("127.0.0.1", 0), _build_handler(accounts, required_token))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        yield f"http://{host}:{port}"
    finally:
        server.shutdown()
        thread.join(timeout=2)
        server.server_close()
