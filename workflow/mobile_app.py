from __future__ import annotations

import argparse
import json
import secrets
import socket
import time
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from workflow.mobile_responses import error_response, mobile_response
from workflow.web_actions import handle_web_action


SAFE_RUN_ACTIONS = {"workflow_status", "project_report", "project_check"}
REPORT_KINDS = {
    "writing_pack",
    "writing_dashboard",
    "literature_table",
    "literature_map",
    "literature_tracker",
}


@dataclass
class MobileCompanionState:
    allowed_roots: list[Path]
    pairing_pin: str
    token_ttl_seconds: int = 3600
    sessions: dict[str, float] = field(default_factory=dict)

    def issue_token(self) -> str:
        token = secrets.token_urlsafe(24)
        self.sessions[token] = time.time() + self.token_ttl_seconds
        return token

    def token_is_valid(self, token: str) -> bool:
        expires_at = self.sessions.get(token)
        if expires_at is None:
            return False
        if expires_at < time.time():
            self.sessions.pop(token, None)
            return False
        return True

    def authorize_root(self, raw_root: str) -> Path:
        candidate = Path(raw_root).expanduser().resolve()
        for root in self.allowed_roots:
            allowed = root.expanduser().resolve()
            if candidate == allowed or allowed in candidate.parents:
                return candidate
        raise PermissionError(f"Project root is not inside an authorized project: {candidate}")


def dispatch_mobile_request(state: MobileCompanionState, path: str, payload: dict[str, Any], token: str) -> dict[str, Any]:
    if path == "/api/pair":
        return _pair_response(state, payload)

    if not state.token_is_valid(token):
        return error_response("auth", "Phone is not connected to the local workbench.", status=401)

    if path == "/api/dashboard":
        return _dashboard_response(state, payload)
    if path == "/api/run":
        return _run_response(state, payload)
    if path == "/api/report":
        return _report_response(state, payload)
    return error_response("unknown", f"Unsupported mobile API path: {path}", status=404)


def run_server(
    host: str = "127.0.0.1",
    port: int = 8765,
    project_roots: list[str | Path] | None = None,
    pairing_pin: str = "123456",
) -> None:
    roots = [Path(root).expanduser().resolve() for root in (project_roots or [])]
    state = MobileCompanionState(allowed_roots=roots, pairing_pin=pairing_pin)
    server = _create_mobile_server(host, port, _make_mobile_handler(state))
    actual_port = server.server_address[1]

    print(f"Mobile companion listening on http://{host}:{actual_port}", flush=True)
    print(f"Pairing PIN: {pairing_pin}", flush=True)
    if roots:
        for root in roots:
            print(f"Authorized project: {root}", flush=True)
    else:
        print("Authorized projects: none", flush=True)

    server.serve_forever()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="research-workflow-mobile")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8765, type=int)
    parser.add_argument("--project-root", action="append", default=[])
    parser.add_argument("--pin", default="")
    args = parser.parse_args(argv)

    pairing_pin = args.pin or f"{secrets.randbelow(1_000_000):06d}"
    run_server(
        host=args.host,
        port=args.port,
        project_roots=args.project_root,
        pairing_pin=pairing_pin,
    )
    return 0


def _pair_response(state: MobileCompanionState, payload: dict[str, Any]) -> dict[str, Any]:
    if str(payload.get("pin", "")) != state.pairing_pin:
        return error_response("pair", "Pairing code is incorrect or expired.", status=403)
    return {
        "ok": True,
        "token": state.issue_token(),
        "expiresInSeconds": state.token_ttl_seconds,
    }


def _dashboard_response(state: MobileCompanionState, payload: dict[str, Any]) -> dict[str, Any]:
    try:
        project_root = state.authorize_root(str(payload.get("project_root", "")))
    except PermissionError as exc:
        return error_response("dashboard", str(exc), status=403)

    status, _content_type, markdown = handle_web_action({"action": "workflow_status", "project_root": str(project_root)})
    if status != 200:
        return error_response("dashboard", markdown, status=status)

    response = mobile_response("dashboard", markdown)
    response["project"] = {"name": project_root.name, "root": str(project_root)}
    return response


def _run_response(state: MobileCompanionState, payload: dict[str, Any]) -> dict[str, Any]:
    action = str(payload.get("action", ""))
    if action not in SAFE_RUN_ACTIONS:
        return error_response(action or "run", f"Unsupported run action: {action}", status=400)

    try:
        project_root = state.authorize_root(str(payload.get("project_root", "")))
    except PermissionError as exc:
        return error_response(action, str(exc), status=403)

    status, _content_type, markdown = handle_web_action({"action": action, "project_root": str(project_root)})
    if status != 200:
        return error_response(action, markdown, status=status)
    return mobile_response(action, markdown)


def _report_response(state: MobileCompanionState, payload: dict[str, Any]) -> dict[str, Any]:
    report_kind = str(payload.get("report_kind", ""))
    if report_kind not in REPORT_KINDS:
        return error_response("save_standard_report", f"Unsupported report kind: {report_kind}", status=400)

    try:
        project_root = state.authorize_root(str(payload.get("project_root", "")))
    except PermissionError as exc:
        return error_response("save_standard_report", str(exc), status=403)

    status, _content_type, markdown = handle_web_action(
        {
            "action": "save_standard_report",
            "project_root": str(project_root),
            "report_kind": report_kind,
        }
    )
    if status != 200:
        return error_response("save_standard_report", markdown, status=status)
    return mobile_response("save_standard_report", markdown)


def _make_mobile_handler(state: MobileCompanionState):
    class MobileRequestHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            if self.path != "/api/health":
                self._send_json(error_response("unknown", f"Unsupported mobile API path: {self.path}", status=404))
                return
            self._send_json({"ok": True, "status": 200})

        def do_POST(self) -> None:
            payload = self._read_json_payload()
            if payload is None:
                self._send_json(error_response("json", "Request body must be valid JSON.", status=400))
                return
            token = _bearer_token(self.headers.get("Authorization", ""))
            self._send_json(dispatch_mobile_request(state, self.path, payload, token))

        def log_message(self, format: str, *args) -> None:
            return

        def _read_json_payload(self) -> dict[str, Any] | None:
            try:
                length = int(self.headers.get("Content-Length", "0") or "0")
                if length < 0:
                    return None
                raw_body = self.rfile.read(length).decode("utf-8")
                decoded = json.loads(raw_body or "{}")
            except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
                return None
            return decoded if isinstance(decoded, dict) else None

        def _send_json(self, response: dict[str, Any]) -> None:
            status = int(response.get("status", 200))
            data = json.dumps(response, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    return MobileRequestHandler


def _create_mobile_server(host: str, port: int, handler) -> ThreadingHTTPServer:
    last_error: OSError | None = None
    for candidate in range(port, port + 10):
        if candidate != 0 and _port_is_listening(host, candidate):
            continue
        try:
            return ThreadingHTTPServer((host, candidate), handler)
        except OSError as exc:
            last_error = exc
    raise OSError(f"No available port from {port} to {port + 9}") from last_error


def _port_is_listening(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.settimeout(0.2)
        return probe.connect_ex((host, port)) == 0


def _bearer_token(header: str) -> str:
    prefix = "Bearer "
    return header[len(prefix):].strip() if header.startswith(prefix) else ""


if __name__ == "__main__":
    raise SystemExit(main())
