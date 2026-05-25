from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field
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
