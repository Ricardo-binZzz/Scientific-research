# WeChat Local Companion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the V1 local-first WeChat mini program companion: a phone-facing project dashboard and report center that connect to a computer-side Python service and reuse the existing research workflow actions.

**Architecture:** Add a `workflow.mobile_app` module that exposes a standard-library HTTP JSON API with pairing, token checks, project-root authorization, dashboard summaries, run actions, and report actions. Add a native WeChat mini program skeleton under `miniprogram/` with soft V2 visual styling, connection state, dashboard, run page, and report center, while preserving the existing desktop web app.

**Tech Stack:** Python standard library HTTP server, existing `workflow.web_actions` and workflow modules, `unittest`, native WeChat mini program with TypeScript, WXML, and WXSS.

---

## File Structure

- Create `workflow/mobile_responses.py`: pure helpers that convert existing Markdown workflow outputs into mobile JSON summaries and cards.
- Create `workflow/mobile_app.py`: local companion HTTP server, pairing token state, authorized project root checks, and mobile action dispatch.
- Modify `pyproject.toml`: add a `research-workflow-mobile` console script.
- Modify `tools/check_release_package.py`: include the new mobile server module and mini program skeleton in release package checks after implementation.
- Create `tests/test_mobile_responses.py`: unit tests for Markdown-to-card summary helpers.
- Create `tests/test_mobile_app.py`: HTTP/API, pairing, token, action dispatch, and project-root authorization tests.
- Create `miniprogram/app.json`, `miniprogram/app.ts`, `miniprogram/app.wxss`: mini program app shell.
- Create `miniprogram/utils/api.ts`: typed wrapper around local companion API calls.
- Create `miniprogram/pages/connect/*`: connection and pairing screen.
- Create `miniprogram/pages/dashboard/*`: soft project dashboard.
- Create `miniprogram/pages/run/*`: safe V1 action triggers.
- Create `miniprogram/pages/reports/*`: report center and report detail navigation.
- Modify `USER_GUIDE.md` and `WEB_GUIDE.md`: document the local companion command, V1 scope, and local testing caveats.
- Modify `PROJECT_MEMORY.md` and `handoff.md`: record implementation status when tasks land.

## Task 1: Mobile Response Summaries

**Files:**
- Create: `workflow/mobile_responses.py`
- Test: `tests/test_mobile_responses.py`

- [ ] **Step 1: Write failing tests for project-check, workflow-status, and report summaries**

Create `tests/test_mobile_responses.py`:

```python
import unittest

from workflow.mobile_responses import (
    build_mobile_cards,
    build_mobile_summary,
    mobile_response,
)


PROJECT_CHECK_MARKDOWN = """# Project Check Report

## Literature
- Missing PDFs: 1
- Missing notes: 2

## Simulation
- Simulation issues: 0

## Manuscript
- Manuscript issues: 1

## Next Actions
- Fill missing reading notes.
"""


WORKFLOW_STATUS_MARKDOWN = """# Workflow Status

## Current Gaps
- Missing PDFs: 1
- Missing notes: 2
- Simulation issues: 0
- Manuscript issues: 1

## Next recommended action
- Fill missing reading notes.
"""


class MobileResponsesTests(unittest.TestCase):
    def test_project_check_summary_uses_soft_next_action_language(self) -> None:
        summary = build_mobile_summary("project_check", PROJECT_CHECK_MARKDOWN)

        self.assertEqual(summary["title"], "Project check complete")
        self.assertEqual(summary["primaryMessage"], "4 items need attention")
        self.assertEqual(summary["nextAction"], "Fill missing reading notes.")

    def test_workflow_status_summary_uses_next_recommended_action(self) -> None:
        summary = build_mobile_summary("workflow_status", WORKFLOW_STATUS_MARKDOWN)

        self.assertEqual(summary["title"], "Workflow status updated")
        self.assertEqual(summary["primaryMessage"], "4 items need attention")
        self.assertEqual(summary["nextAction"], "Fill missing reading notes.")

    def test_build_mobile_cards_extracts_dashboard_cards(self) -> None:
        cards = build_mobile_cards("project_check", PROJECT_CHECK_MARKDOWN)

        self.assertIn(
            {"label": "Literature", "status": "needs_attention", "message": "1 PDF missing, 2 notes missing"},
            cards,
        )
        self.assertIn(
            {"label": "Simulation", "status": "ready", "message": "No simulation issues found"},
            cards,
        )
        self.assertIn(
            {"label": "Manuscript", "status": "needs_attention", "message": "1 manuscript issue found"},
            cards,
        )

    def test_mobile_response_includes_raw_markdown(self) -> None:
        response = mobile_response("project_check", PROJECT_CHECK_MARKDOWN)

        self.assertTrue(response["ok"])
        self.assertEqual(response["action"], "project_check")
        self.assertEqual(response["markdown"], PROJECT_CHECK_MARKDOWN)
        self.assertEqual(response["summary"]["primaryMessage"], "4 items need attention")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the failing tests**

Run:

```powershell
python -m unittest tests.test_mobile_responses -v
```

Expected: fail with `ModuleNotFoundError: No module named 'workflow.mobile_responses'`.

- [ ] **Step 3: Implement the mobile response helpers**

Create `workflow/mobile_responses.py`:

```python
from __future__ import annotations

import re
from typing import Any


MobileResponse = dict[str, Any]


def mobile_response(action: str, markdown: str) -> MobileResponse:
    return {
        "ok": True,
        "action": action,
        "summary": build_mobile_summary(action, markdown),
        "cards": build_mobile_cards(action, markdown),
        "markdown": markdown,
    }


def build_mobile_summary(action: str, markdown: str) -> dict[str, str]:
    counts = _issue_counts(markdown)
    total = sum(counts.values())
    next_action = _first_bullet_after_heading(markdown, "Next Actions") or _first_bullet_after_heading(
        markdown, "Next recommended action"
    )
    if not next_action:
        next_action = "Review the generated report details."
    titles = {
        "project_check": "Project check complete",
        "workflow_status": "Workflow status updated",
        "project_report": "Project overview updated",
        "save_standard_report": "Reports updated",
    }
    return {
        "title": titles.get(action, "Workflow action complete"),
        "primaryMessage": f"{total} items need attention" if total else "No urgent gaps found",
        "nextAction": next_action,
    }


def build_mobile_cards(action: str, markdown: str) -> list[dict[str, str]]:
    counts = _issue_counts(markdown)
    cards = [
        _card(
            "Literature",
            counts["missing_pdfs"] + counts["missing_notes"],
            _literature_message(counts["missing_pdfs"], counts["missing_notes"]),
        ),
        _card(
            "Simulation",
            counts["simulation_issues"],
            f"{counts['simulation_issues']} simulation issue found"
            if counts["simulation_issues"] == 1
            else f"{counts['simulation_issues']} simulation issues found",
            ready_message="No simulation issues found",
        ),
        _card(
            "Manuscript",
            counts["manuscript_issues"],
            f"{counts['manuscript_issues']} manuscript issue found"
            if counts["manuscript_issues"] == 1
            else f"{counts['manuscript_issues']} manuscript issues found",
            ready_message="No manuscript issues found",
        ),
    ]
    return cards


def error_response(action: str, message: str, status: int = 400) -> MobileResponse:
    return {
        "ok": False,
        "action": action,
        "status": status,
        "summary": {
            "title": "Action needs attention",
            "primaryMessage": message,
            "nextAction": "Check the connection, project root, and local service window.",
        },
        "cards": [],
        "markdown": message,
    }


def _card(label: str, count: int, message: str, ready_message: str = "No gaps found") -> dict[str, str]:
    return {
        "label": label,
        "status": "needs_attention" if count else "ready",
        "message": message if count else ready_message,
    }


def _literature_message(missing_pdfs: int, missing_notes: int) -> str:
    parts: list[str] = []
    if missing_pdfs:
        noun = "PDF" if missing_pdfs == 1 else "PDFs"
        parts.append(f"{missing_pdfs} {noun} missing")
    if missing_notes:
        noun = "note" if missing_notes == 1 else "notes"
        parts.append(f"{missing_notes} {noun} missing")
    return ", ".join(parts) if parts else "No literature asset gaps found"


def _issue_counts(markdown: str) -> dict[str, int]:
    return {
        "missing_pdfs": _extract_count(markdown, "Missing PDFs"),
        "missing_notes": _extract_count(markdown, "Missing notes"),
        "simulation_issues": _extract_count(markdown, "Simulation issues"),
        "manuscript_issues": _extract_count(markdown, "Manuscript issues"),
    }


def _extract_count(markdown: str, label: str) -> int:
    match = re.search(rf"{re.escape(label)}:\s*(\d+)", markdown, flags=re.IGNORECASE)
    return int(match.group(1)) if match else 0


def _first_bullet_after_heading(markdown: str, heading: str) -> str:
    lines = markdown.splitlines()
    in_section = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            in_section = stripped.lstrip("#").strip().lower() == heading.lower()
            continue
        if in_section and stripped.startswith("- "):
            return stripped[2:].strip()
    return ""
```

- [ ] **Step 4: Run the tests until they pass**

Run:

```powershell
python -m unittest tests.test_mobile_responses -v
```

Expected: 4 tests pass.

- [ ] **Step 5: Commit Task 1**

```powershell
git add workflow/mobile_responses.py tests/test_mobile_responses.py
git commit -m "Add mobile response summaries"
```

## Task 2: Local Mobile API Dispatch and Authorization

**Files:**
- Create: `workflow/mobile_app.py`
- Test: `tests/test_mobile_app.py`

- [ ] **Step 1: Write failing tests for token pairing, root authorization, dashboard, and action dispatch**

Create `tests/test_mobile_app.py`:

```python
import json
import tempfile
import unittest
from pathlib import Path

from workflow.bootstrap import bootstrap_workspace
from workflow.mobile_app import MobileCompanionState, dispatch_mobile_request


class MobileAppDispatchTests(unittest.TestCase):
    def test_pair_returns_token_and_dashboard_accepts_authorized_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project = bootstrap_workspace(Path(tmpdir), project_slug="demo", project_name="Demo")
            state = MobileCompanionState(allowed_roots=[project], pairing_pin="123456")

            pair = dispatch_mobile_request(state, "/api/pair", {"pin": "123456"}, token="")
            token = pair["token"]
            dashboard = dispatch_mobile_request(
                state,
                "/api/dashboard",
                {"project_root": str(project)},
                token=token,
            )

        self.assertTrue(pair["ok"])
        self.assertEqual(dashboard["action"], "dashboard")
        self.assertEqual(dashboard["project"]["name"], "demo")
        self.assertIn("summary", dashboard)

    def test_wrong_pin_is_rejected(self) -> None:
        state = MobileCompanionState(allowed_roots=[], pairing_pin="123456")

        response = dispatch_mobile_request(state, "/api/pair", {"pin": "000000"}, token="")

        self.assertFalse(response["ok"])
        self.assertEqual(response["status"], 403)

    def test_unauthorized_project_root_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            allowed = Path(tmpdir) / "allowed"
            outside = Path(tmpdir) / "outside"
            allowed.mkdir()
            outside.mkdir()
            state = MobileCompanionState(allowed_roots=[allowed], pairing_pin="123456")
            token = dispatch_mobile_request(state, "/api/pair", {"pin": "123456"}, token="")["token"]

            response = dispatch_mobile_request(
                state,
                "/api/run",
                {"action": "project_check", "project_root": str(outside)},
                token=token,
            )

        self.assertFalse(response["ok"])
        self.assertEqual(response["status"], 403)
        self.assertIn("authorized project", response["summary"]["primaryMessage"])

    def test_project_check_run_returns_mobile_cards(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project = bootstrap_workspace(Path(tmpdir), project_slug="demo", project_name="Demo")
            state = MobileCompanionState(allowed_roots=[project], pairing_pin="123456")
            token = dispatch_mobile_request(state, "/api/pair", {"pin": "123456"}, token="")["token"]

            response = dispatch_mobile_request(
                state,
                "/api/run",
                {"action": "project_check", "project_root": str(project)},
                token=token,
            )

        self.assertTrue(response["ok"])
        self.assertEqual(response["action"], "project_check")
        self.assertEqual(response["summary"]["title"], "Project check complete")
        self.assertIn("# Project Check Report", response["markdown"])
        self.assertTrue(response["cards"])

    def test_save_standard_report_dispatch_returns_report_result(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project = bootstrap_workspace(Path(tmpdir), project_slug="demo", project_name="Demo")
            state = MobileCompanionState(allowed_roots=[project], pairing_pin="123456")
            token = dispatch_mobile_request(state, "/api/pair", {"pin": "123456"}, token="")["token"]

            response = dispatch_mobile_request(
                state,
                "/api/report",
                {"report_kind": "writing_pack", "project_root": str(project)},
                token=token,
            )

        self.assertTrue(response["ok"])
        self.assertEqual(response["action"], "save_standard_report")
        self.assertIn("writing-pack.md", response["markdown"])

    def test_response_can_be_serialized_to_json(self) -> None:
        state = MobileCompanionState(allowed_roots=[], pairing_pin="123456")
        response = dispatch_mobile_request(state, "/api/pair", {"pin": "123456"}, token="")

        encoded = json.dumps(response, ensure_ascii=False)

        self.assertIn("token", encoded)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the failing tests**

Run:

```powershell
python -m unittest tests.test_mobile_app -v
```

Expected: fail with `ModuleNotFoundError: No module named 'workflow.mobile_app'`.

- [ ] **Step 3: Implement dispatch, token state, and authorized-root checks**

Create `workflow/mobile_app.py` with these imports and core functions:

```python
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
        if not expires_at:
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
        if str(payload.get("pin", "")) != state.pairing_pin:
            return error_response("pair", "Pairing code is incorrect or expired.", status=403)
        issued = state.issue_token()
        return {"ok": True, "token": issued, "expiresInSeconds": state.token_ttl_seconds}

    if not state.token_is_valid(token):
        return error_response("auth", "Phone is not connected to the local workbench.", status=401)

    if path == "/api/dashboard":
        return _dashboard_response(state, payload)
    if path == "/api/run":
        return _run_response(state, payload)
    if path == "/api/report":
        return _report_response(state, payload)
    return error_response("unknown", f"Unsupported mobile API path: {path}", status=404)


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
```

- [ ] **Step 4: Run dispatch tests until they pass**

Run:

```powershell
python -m unittest tests.test_mobile_app -v
```

Expected: 6 tests pass.

- [ ] **Step 5: Commit Task 2**

```powershell
git add workflow/mobile_app.py tests/test_mobile_app.py
git commit -m "Add mobile companion API dispatch"
```

## Task 3: Local HTTP Server and CLI Entry Point

**Files:**
- Modify: `workflow/mobile_app.py`
- Modify: `pyproject.toml`
- Test: `tests/test_mobile_app.py`

- [ ] **Step 1: Add failing HTTP server tests**

Append to `tests/test_mobile_app.py`:

```python
import threading
import urllib.error
import urllib.request


class MobileAppHttpTests(unittest.TestCase):
    def test_http_pair_and_dashboard_round_trip(self) -> None:
        from workflow.mobile_app import _create_mobile_server, _make_mobile_handler

        with tempfile.TemporaryDirectory() as tmpdir:
            project = bootstrap_workspace(Path(tmpdir), project_slug="demo", project_name="Demo")
            state = MobileCompanionState(allowed_roots=[project], pairing_pin="123456")
            server = _create_mobile_server("127.0.0.1", 9100, _make_mobile_handler(state))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                base = f"http://127.0.0.1:{server.server_address[1]}"
                pair = _post_json(f"{base}/api/pair", {"pin": "123456"})
                dashboard = _post_json(
                    f"{base}/api/dashboard",
                    {"project_root": str(project)},
                    token=pair["token"],
                )
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

        self.assertTrue(pair["ok"])
        self.assertEqual(dashboard["action"], "dashboard")
        self.assertEqual(dashboard["project"]["name"], "demo")

    def test_http_rejects_missing_token(self) -> None:
        from workflow.mobile_app import _create_mobile_server, _make_mobile_handler

        state = MobileCompanionState(allowed_roots=[], pairing_pin="123456")
        server = _create_mobile_server("127.0.0.1", 9100, _make_mobile_handler(state))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            base = f"http://127.0.0.1:{server.server_address[1]}"
            response = _post_json(f"{base}/api/dashboard", {"project_root": ""})
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

        self.assertFalse(response["ok"])
        self.assertEqual(response["status"], 401)


def _post_json(url: str, payload: dict[str, object], token: str = "") -> dict[str, object]:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=body, method="POST")
    request.add_header("Content-Type", "application/json")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return json.loads(exc.read().decode("utf-8"))
```

- [ ] **Step 2: Run tests to verify missing HTTP helpers**

Run:

```powershell
python -m unittest tests.test_mobile_app -v
```

Expected: fail with missing `_create_mobile_server` or `_make_mobile_handler`.

- [ ] **Step 3: Implement HTTP server helpers and CLI**

Append to `workflow/mobile_app.py`:

```python
def run_server(
    host: str = "127.0.0.1",
    port: int = 8765,
    project_roots: list[str] | None = None,
    pairing_pin: str = "123456",
) -> None:
    allowed_roots = [Path(root).expanduser().resolve() for root in (project_roots or [])]
    state = MobileCompanionState(allowed_roots=allowed_roots, pairing_pin=pairing_pin)
    server = _create_mobile_server(host, port, _make_mobile_handler(state))
    actual_port = server.server_address[1]
    print(f"Mobile companion listening on http://{host}:{actual_port}", flush=True)
    print(f"Pairing PIN: {pairing_pin}", flush=True)
    for root in allowed_roots:
        print(f"Authorized project: {root}", flush=True)
    server.serve_forever()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="research-workflow-mobile")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8765, type=int)
    parser.add_argument("--project-root", action="append", default=[])
    parser.add_argument("--pin", default="")
    args = parser.parse_args(argv)
    pairing_pin = args.pin.strip() or f"{secrets.randbelow(900000) + 100000}"
    run_server(host=args.host, port=args.port, project_roots=args.project_root, pairing_pin=pairing_pin)
    return 0


def _make_mobile_handler(state: MobileCompanionState):
    class MobileRequestHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            if self.path != "/api/health":
                self._send_json(404, error_response("health", "Not found", status=404))
                return
            self._send_json(200, {"ok": True, "service": "research-workflow-mobile"})

        def do_POST(self) -> None:
            length = int(self.headers.get("Content-Length", "0") or "0")
            raw_body = self.rfile.read(length).decode("utf-8")
            payload = json.loads(raw_body or "{}")
            token = _bearer_token(self.headers.get("Authorization", ""))
            response = dispatch_mobile_request(state, self.path, payload, token=token)
            status = int(response.get("status", 200 if response.get("ok") else 400))
            self._send_json(status, response)

        def log_message(self, format: str, *args: object) -> None:
            return

        def _send_json(self, status: int, body: dict[str, Any]) -> None:
            data = json.dumps(body, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    return MobileRequestHandler


def _create_mobile_server(host: str, port: int, handler) -> ThreadingHTTPServer:
    last_error: OSError | None = None
    for candidate in range(port, port + 10):
        if _port_is_listening(host, candidate):
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
```

Modify `pyproject.toml`:

```toml
[project.scripts]
research-workflow = "workflow.cli:main"
research-workflow-web = "workflow.web_app:main"
research-workflow-mobile = "workflow.mobile_app:main"
```

- [ ] **Step 4: Run focused mobile API tests**

Run:

```powershell
python -m unittest tests.test_mobile_app -v
```

Expected: mobile API tests pass.

- [ ] **Step 5: Run project metadata test subset**

Run:

```powershell
python -m unittest tests.test_web_app tests.test_release_package -v
```

Expected: tests pass. If release-package tests fail because the new mobile file is not in the package list, update `tools/check_release_package.py` in Task 6.

- [ ] **Step 6: Commit Task 3**

```powershell
git add workflow/mobile_app.py pyproject.toml tests/test_mobile_app.py
git commit -m "Add mobile companion HTTP server"
```

## Task 4: WeChat Mini Program Skeleton

**Files:**
- Create: `miniprogram/app.json`
- Create: `miniprogram/app.ts`
- Create: `miniprogram/app.wxss`
- Create: `miniprogram/utils/api.ts`
- Create: `miniprogram/pages/connect/connect.json`
- Create: `miniprogram/pages/connect/connect.wxml`
- Create: `miniprogram/pages/connect/connect.ts`
- Create: `miniprogram/pages/connect/connect.wxss`
- Create: `miniprogram/pages/dashboard/dashboard.json`
- Create: `miniprogram/pages/dashboard/dashboard.wxml`
- Create: `miniprogram/pages/dashboard/dashboard.ts`
- Create: `miniprogram/pages/dashboard/dashboard.wxss`
- Create: `miniprogram/pages/run/run.json`
- Create: `miniprogram/pages/run/run.wxml`
- Create: `miniprogram/pages/run/run.ts`
- Create: `miniprogram/pages/run/run.wxss`
- Create: `miniprogram/pages/reports/reports.json`
- Create: `miniprogram/pages/reports/reports.wxml`
- Create: `miniprogram/pages/reports/reports.ts`
- Create: `miniprogram/pages/reports/reports.wxss`
- Test: `tests/test_miniprogram_assets.py`

- [ ] **Step 1: Write failing asset tests**

Create `tests/test_miniprogram_assets.py`:

```python
import json
import unittest
from pathlib import Path


class MiniProgramAssetsTests(unittest.TestCase):
    def test_app_json_declares_v1_pages_and_soft_navigation(self) -> None:
        app_json = json.loads(Path("miniprogram/app.json").read_text(encoding="utf-8"))

        self.assertEqual(
            app_json["pages"],
            [
                "pages/connect/connect",
                "pages/dashboard/dashboard",
                "pages/run/run",
                "pages/reports/reports",
            ],
        )
        self.assertEqual(app_json["window"]["navigationBarTitleText"], "科研工作台")
        self.assertEqual(app_json["tabBar"]["list"][0]["text"], "首页")
        self.assertEqual(app_json["tabBar"]["list"][1]["text"], "运行")
        self.assertEqual(app_json["tabBar"]["list"][2]["text"], "报告")

    def test_api_wrapper_contains_pair_dashboard_run_and_report_calls(self) -> None:
        api_ts = Path("miniprogram/utils/api.ts").read_text(encoding="utf-8")

        self.assertIn("export interface MobileSummary", api_ts)
        self.assertIn("export function pairWithWorkbench", api_ts)
        self.assertIn("export function fetchDashboard", api_ts)
        self.assertIn("export function runWorkflowAction", api_ts)
        self.assertIn("export function updateReport", api_ts)
        self.assertIn("Authorization", api_ts)

    def test_pages_use_soft_research_assistant_language(self) -> None:
        dashboard = Path("miniprogram/pages/dashboard/dashboard.wxml").read_text(encoding="utf-8")
        reports = Path("miniprogram/pages/reports/reports.wxml").read_text(encoding="utf-8")
        run = Path("miniprogram/pages/run/run.wxml").read_text(encoding="utf-8")

        self.assertIn("今天的研究进度", dashboard)
        self.assertIn("开始一次体检", dashboard)
        self.assertIn("整理好的材料", reports)
        self.assertIn("先处理这些", run)
        self.assertNotIn("project check", dashboard.lower())

    def test_shared_styles_use_soft_tokens(self) -> None:
        app_wxss = Path("miniprogram/app.wxss").read_text(encoding="utf-8")

        self.assertIn("--green-soft", app_wxss)
        self.assertIn("--blue-soft", app_wxss)
        self.assertIn("border-radius: 8px", app_wxss)
        self.assertIn("box-shadow", app_wxss)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify missing assets**

Run:

```powershell
python -m unittest tests.test_miniprogram_assets -v
```

Expected: fail because `miniprogram/app.json` does not exist.

- [ ] **Step 3: Create the mini program app shell**

Create `miniprogram/app.json`:

```json
{
  "pages": [
    "pages/connect/connect",
    "pages/dashboard/dashboard",
    "pages/run/run",
    "pages/reports/reports"
  ],
  "window": {
    "navigationBarTitleText": "科研工作台",
    "navigationBarBackgroundColor": "#f8fafb",
    "navigationBarTextStyle": "black",
    "backgroundColor": "#f8fafb"
  },
  "tabBar": {
    "color": "#8a95a3",
    "selectedColor": "#3f8b63",
    "backgroundColor": "#ffffff",
    "borderStyle": "white",
    "list": [
      {"pagePath": "pages/dashboard/dashboard", "text": "首页"},
      {"pagePath": "pages/run/run", "text": "运行"},
      {"pagePath": "pages/reports/reports", "text": "报告"}
    ]
  }
}
```

Create `miniprogram/app.ts`:

```typescript
App({
  globalData: {
    baseUrl: "",
    token: "",
    projectRoot: ""
  }
})
```

Create `miniprogram/app.wxss`:

```css
page {
  --ink: #202734;
  --muted: #6e7a89;
  --quiet: #8a95a3;
  --paper: #f8fafb;
  --panel: #ffffff;
  --line-soft: #edf1f5;
  --green: #3f8b63;
  --blue: #557fae;
  --green-soft: #eef7f2;
  --blue-soft: #f0f5fa;
  --warm-soft: #fbf6ed;
  --rose-soft: #fbf1f0;
  background: var(--paper);
  color: var(--ink);
  font-family: system-ui, sans-serif;
}

.screen {
  padding: 28rpx;
}

.eyebrow {
  color: var(--quiet);
  font-size: 24rpx;
  margin-bottom: 8rpx;
}

.title {
  color: var(--ink);
  font-size: 36rpx;
  font-weight: 700;
  line-height: 1.3;
  margin-bottom: 24rpx;
}

.soft-card {
  background: var(--panel);
  border: 1rpx solid var(--line-soft);
  border-radius: 8px;
  box-shadow: 0 10rpx 24rpx rgba(32, 39, 52, 0.07);
  margin-bottom: 16rpx;
  padding: 22rpx;
}

.soft-card-title {
  color: var(--ink);
  display: block;
  font-size: 28rpx;
  font-weight: 700;
  margin-bottom: 8rpx;
}

.soft-card-text {
  color: var(--muted);
  display: block;
  font-size: 26rpx;
  line-height: 1.55;
}

.action-row {
  align-items: center;
  background: var(--panel);
  border: 1rpx solid #dce8df;
  border-radius: 8px;
  color: var(--green);
  display: flex;
  font-size: 28rpx;
  font-weight: 700;
  justify-content: space-between;
  margin: 18rpx 0;
  min-height: 76rpx;
  padding: 0 22rpx;
}
```

- [ ] **Step 4: Create API wrapper**

Create `miniprogram/utils/api.ts`:

```typescript
export interface MobileSummary {
  title: string
  primaryMessage: string
  nextAction: string
}

export interface MobileCard {
  label: string
  status: "ready" | "needs_attention"
  message: string
}

export interface MobileResponse {
  ok: boolean
  action: string
  summary: MobileSummary
  cards: MobileCard[]
  markdown: string
  project?: { name: string; root: string }
  token?: string
  expiresInSeconds?: number
}

function request<T>(baseUrl: string, path: string, payload: object, token = ""): Promise<T> {
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${baseUrl}${path}`,
      method: "POST",
      data: payload,
      header: token ? { Authorization: `Bearer ${token}` } : {},
      success: (result) => resolve(result.data as T),
      fail: reject
    })
  })
}

export function pairWithWorkbench(baseUrl: string, pin: string): Promise<MobileResponse> {
  return request<MobileResponse>(baseUrl, "/api/pair", { pin })
}

export function fetchDashboard(baseUrl: string, token: string, projectRoot: string): Promise<MobileResponse> {
  return request<MobileResponse>(baseUrl, "/api/dashboard", { project_root: projectRoot }, token)
}

export function runWorkflowAction(
  baseUrl: string,
  token: string,
  projectRoot: string,
  action: "workflow_status" | "project_report" | "project_check"
): Promise<MobileResponse> {
  return request<MobileResponse>(baseUrl, "/api/run", { action, project_root: projectRoot }, token)
}

export function updateReport(
  baseUrl: string,
  token: string,
  projectRoot: string,
  reportKind: string
): Promise<MobileResponse> {
  return request<MobileResponse>(baseUrl, "/api/report", { project_root: projectRoot, report_kind: reportKind }, token)
}
```

- [ ] **Step 5: Create pages with soft V2 language**

Create the four page `.json` files with `{ "navigationBarTitleText": "科研工作台" }`, changing the title to `"连接工作台"`, `"运行检查"`, and `"报告中心"` for the connect, run, and reports pages.

Create `miniprogram/pages/dashboard/dashboard.wxml`:

```xml
<view class="screen">
  <view class="eyebrow">本地工作台已连接</view>
  <view class="title">今天的研究进度</view>
  <view class="soft-card summary">
    <text class="soft-card-title">{{summary.primaryMessage || "还没有体检结果"}}</text>
    <text class="soft-card-text">{{summary.nextAction || "连接电脑后开始一次体检。"}}</text>
  </view>
  <view class="soft-card" wx:for="{{cards}}" wx:key="label">
    <text class="soft-card-title">{{item.label}}</text>
    <text class="soft-card-text">{{item.message}}</text>
  </view>
  <view class="action-row" bindtap="startProjectCheck">
    <text>开始一次体检</text>
    <text>约 10 秒</text>
  </view>
</view>
```

Create `miniprogram/pages/run/run.wxml`:

```xml
<view class="screen">
  <view class="eyebrow">运行结果</view>
  <view class="title">先处理这些</view>
  <view class="action-row" bindtap="runWorkflowStatus"><text>更新流程状态</text><text>查看建议</text></view>
  <view class="action-row" bindtap="runProjectReport"><text>更新项目概览</text><text>整理数字</text></view>
  <view class="action-row" bindtap="runProjectCheck"><text>开始一次体检</text><text>查缺口</text></view>
  <view class="soft-card" wx:for="{{cards}}" wx:key="label">
    <text class="soft-card-title">{{item.label}}</text>
    <text class="soft-card-text">{{item.message}}</text>
  </view>
</view>
```

Create `miniprogram/pages/reports/reports.wxml`:

```xml
<view class="screen">
  <view class="eyebrow">报告中心</view>
  <view class="title">整理好的材料</view>
  <view class="soft-card" wx:for="{{reports}}" wx:key="kind" bindtap="updateReport" data-kind="{{item.kind}}">
    <text class="soft-card-title">{{item.title}}</text>
    <text class="soft-card-text">{{item.description}}</text>
  </view>
  <view class="soft-card" wx:if="{{markdown}}">
    <text class="soft-card-title">完整报告</text>
    <text class="soft-card-text">{{markdown}}</text>
  </view>
</view>
```

Create `miniprogram/pages/connect/connect.wxml`:

```xml
<view class="screen">
  <view class="eyebrow">连接电脑</view>
  <view class="title">连接本地研究工作台</view>
  <view class="soft-card">
    <text class="soft-card-title">电脑端服务</text>
    <text class="soft-card-text">先在电脑启动 research-workflow-mobile，再输入地址和配对码。</text>
  </view>
  <view class="soft-card-text">电脑服务地址</view>
  <input value="{{baseUrl}}" bindinput="onBaseUrlInput" />
  <view class="soft-card-text">配对码</view>
  <input value="{{pin}}" bindinput="onPinInput" />
  <view class="soft-card-text">电脑上的项目路径</view>
  <input value="{{projectRoot}}" bindinput="onProjectRootInput" />
  <view class="action-row" bindtap="connect"><text>连接工作台</text><text>本地优先</text></view>
</view>
```

For each page `.ts`, create page state and call functions from `miniprogram/utils/api.ts`. Keep the first pass direct: read and write `baseUrl`, `token`, and `projectRoot` through `wx.getStorageSync` and `wx.setStorageSync`.

- [ ] **Step 6: Run mini program asset tests**

Run:

```powershell
python -m unittest tests.test_miniprogram_assets -v
```

Expected: 4 tests pass.

- [ ] **Step 7: Commit Task 4**

```powershell
git add miniprogram tests/test_miniprogram_assets.py
git commit -m "Add WeChat mini program V1 shell"
```

## Task 5: Documentation and Release Packaging Alignment

**Files:**
- Modify: `USER_GUIDE.md`
- Modify: `WEB_GUIDE.md`
- Modify: `tools/check_release_package.py`
- Modify: `PROJECT_MEMORY.md`
- Modify: `handoff.md`
- Test: `tests/test_release_package.py`

- [ ] **Step 1: Add release-package expectations for mobile assets**

Modify `tools/check_release_package.py` so `REQUIRED_SUFFIXES` includes:

```python
    "workflow/mobile_app.py",
    "workflow/mobile_responses.py",
    "miniprogram/app.json",
    "miniprogram/utils/api.ts",
```

- [ ] **Step 2: Update user-facing documentation**

Add a concise V1 section to `USER_GUIDE.md` under the local web interface or workflow entry area:

```markdown
## 微信小程序本地伴随服务（规划中的 V1）

V1 小程序定位为手机端研究助手：连接电脑上的本地伴随服务后，用手机查看项目驾驶舱、开始一次项目体检、更新常用报告，并在手机上阅读柔和摘要和完整 Markdown 报告。

电脑端命令计划为：

```powershell
research-workflow-mobile --project-root C:\path\to\workspace --host 127.0.0.1 --port 8765
```

第一版聚焦“项目驾驶舱 + 报告中心”，不在手机上编辑文献、上传仿真数据、配置图表或修改稿件。微信小程序正式发布会受到 HTTPS 和合法域名限制；本地伴随服务 V1 先面向开发和小范围测试。
```

Add a matching short note to `WEB_GUIDE.md` explaining that the desktop browser workbench remains the full local UI, while the mini program is a mobile companion for dashboard and reports.

- [ ] **Step 3: Record stable implementation facts**

Append to `PROJECT_MEMORY.md`:

```markdown
- WeChat mini program V1 implementation uses `workflow.mobile_app` and `workflow.mobile_responses`, a Python standard-library HTTP server, and a native WeChat mini program skeleton under `miniprogram/`.
```

Append to `handoff.md` under `## Status`:

```markdown
- WeChat local companion V1 implementation added the mobile JSON API, pairing/token checks, soft mini program shell, and user-facing docs. Run `python -m unittest tests.test_mobile_responses tests.test_mobile_app tests.test_miniprogram_assets tests.test_release_package -v` after edits.
```

- [ ] **Step 4: Run focused verification**

Run:

```powershell
python -m unittest tests.test_mobile_responses tests.test_mobile_app tests.test_miniprogram_assets tests.test_release_package -v
```

Expected: focused mobile and release-package tests pass.

- [ ] **Step 5: Run full verification**

Run:

```powershell
python -m unittest discover -v
```

Expected: full suite passes.

- [ ] **Step 6: Commit Task 5**

```powershell
git add USER_GUIDE.md WEB_GUIDE.md PROJECT_MEMORY.md handoff.md tools/check_release_package.py tests/test_release_package.py
git commit -m "Document mobile companion workflow"
```

## Task 6: Manual WeChat Developer Tools Check

**Files:**
- Modify only if manual testing finds a concrete issue: `miniprogram/**`

- [ ] **Step 1: Start the local companion service**

Run:

```powershell
research-workflow-mobile --project-root C:\Users\22676\Documents\科研\examples\demo-project --host 127.0.0.1 --port 8765 --pin 123456
```

Expected output includes:

```text
Mobile companion listening on http://127.0.0.1:8765
Pairing PIN: 123456
Authorized project: C:\Users\22676\Documents\科研\examples\demo-project
```

- [ ] **Step 2: Open `miniprogram/` in WeChat Developer Tools**

Use a test AppID or mini program test mode. Configure the local request domain according to WeChat Developer Tools local-debug settings. Enter:

```text
Base URL: http://127.0.0.1:8765
PIN: 123456
Project root: C:\Users\22676\Documents\科研\examples\demo-project
```

- [ ] **Step 3: Verify the V1 user journey manually**

Expected:

- Connect page accepts the PIN and stores a token.
- Dashboard shows "今天的研究进度".
- "开始一次体检" returns project-check cards.
- Run page can update workflow status, project overview, and project check.
- Report center can update writing pack and literature reports.
- Full Markdown appears in the report detail area.

- [ ] **Step 4: Fix concrete manual-test issues with focused tests**

For each issue, add or adjust a Python asset test in `tests/test_miniprogram_assets.py` or an API test in `tests/test_mobile_app.py`, run the focused test, then patch the affected mini program or API file.

- [ ] **Step 5: Final verification**

Run:

```powershell
python -m unittest discover -v
```

Expected: full suite passes.

- [ ] **Step 6: Commit manual-test fixes**

```powershell
git add miniprogram workflow tests USER_GUIDE.md WEB_GUIDE.md PROJECT_MEMORY.md handoff.md
git commit -m "Polish mobile companion manual flow"
```

## Self-Review

- Spec coverage: product type, target users, softer visual direction, local-first architecture, project dashboard, run page, report center, pairing, authorized project roots, JSON summaries, raw Markdown details, testing, docs, and non-goals are covered by Tasks 1-6.
- Red-flag scan: this plan contains no unfinished-marker terms or unspecified "add tests" steps.
- Type consistency: the plan uses `MobileSummary`, `MobileCard`, `MobileResponse`, `MobileCompanionState`, `dispatch_mobile_request`, `mobile_response`, and the same action names across tests, implementation snippets, and mini program API wrappers.
