import json
import socket
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from workflow.bootstrap import bootstrap_workspace
from workflow.mobile_app import (
    MobileCompanionState,
    _create_mobile_server,
    _make_mobile_handler,
    dispatch_mobile_request,
)


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


class MobileAppHttpServerTests(unittest.TestCase):
    def test_http_server_pairs_then_accepts_dashboard_with_bearer_token(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project = bootstrap_workspace(Path(tmpdir), project_slug="demo", project_name="Demo")
            state = MobileCompanionState(allowed_roots=[project], pairing_pin="123456")
            server = _create_mobile_server("127.0.0.1", 0, _make_mobile_handler(state))
            thread = self._serve_in_thread(server)
            try:
                base_url = f"http://127.0.0.1:{server.server_address[1]}"
                pair = self._post_json(base_url, "/api/pair", {"pin": "123456"})
                dashboard = self._post_json(
                    base_url,
                    "/api/dashboard",
                    {"project_root": str(project)},
                    token=pair["token"],
                )
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

        self.assertTrue(pair["ok"])
        self.assertTrue(dashboard["ok"])
        self.assertEqual(dashboard["action"], "dashboard")
        self.assertEqual(dashboard["project"]["name"], "demo")

    def test_http_server_rejects_missing_token_with_json_401(self) -> None:
        state = MobileCompanionState(allowed_roots=[], pairing_pin="123456")
        server = _create_mobile_server("127.0.0.1", 0, _make_mobile_handler(state))
        thread = self._serve_in_thread(server)
        try:
            base_url = f"http://127.0.0.1:{server.server_address[1]}"
            with self.assertRaises(urllib.error.HTTPError) as raised:
                self._post_json(base_url, "/api/dashboard", {"project_root": ""})
            body = json.loads(raised.exception.read().decode("utf-8"))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

        self.assertEqual(raised.exception.code, 401)
        self.assertFalse(body["ok"])
        self.assertEqual(body["status"], 401)
        self.assertEqual(body["action"], "auth")

    def test_http_server_rejects_invalid_utf8_body_with_json_400(self) -> None:
        state = MobileCompanionState(allowed_roots=[], pairing_pin="123456")
        server = _create_mobile_server("127.0.0.1", 0, _make_mobile_handler(state))
        thread = self._serve_in_thread(server)
        try:
            response = self._raw_http_request(
                server,
                b"POST /api/pair HTTP/1.1\r\n"
                b"Host: 127.0.0.1\r\n"
                b"Content-Type: application/json\r\n"
                b"Content-Length: 1\r\n"
                b"\r\n"
                b"\xff",
            )
            status, body = self._parse_raw_json_response(response)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

        self.assertEqual(status, 400)
        self.assertFalse(body["ok"])
        self.assertEqual(body["status"], 400)

    def test_http_server_rejects_malformed_content_length_with_json_400(self) -> None:
        state = MobileCompanionState(allowed_roots=[], pairing_pin="123456")
        server = _create_mobile_server("127.0.0.1", 0, _make_mobile_handler(state))
        thread = self._serve_in_thread(server)
        try:
            response = self._raw_http_request(
                server,
                b"POST /api/pair HTTP/1.1\r\n"
                b"Host: 127.0.0.1\r\n"
                b"Content-Type: application/json\r\n"
                b"Content-Length: nope\r\n"
                b"\r\n"
                b'{"pin":"123456"}',
            )
            status, body = self._parse_raw_json_response(response)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

        self.assertEqual(status, 400)
        self.assertFalse(body["ok"])
        self.assertEqual(body["status"], 400)

    def _post_json(self, base_url: str, path: str, payload: dict[str, str], token: str = "") -> dict[str, object]:
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        request = urllib.request.Request(
            f"{base_url}{path}",
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            return json.loads(response.read().decode("utf-8"))

    def _serve_in_thread(self, server) -> threading.Thread:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        return thread

    def _raw_http_request(self, server, request: bytes) -> bytes:
        with socket.create_connection(server.server_address, timeout=5) as client:
            client.settimeout(5)
            client.sendall(request)
            chunks = []
            while True:
                try:
                    chunk = client.recv(4096)
                except TimeoutError:
                    break
                if not chunk:
                    break
                chunks.append(chunk)
        return b"".join(chunks)

    def _parse_raw_json_response(self, response: bytes) -> tuple[int, dict[str, object]]:
        header_bytes, body_bytes = response.split(b"\r\n\r\n", 1)
        status_line = header_bytes.splitlines()[0].decode("ascii")
        status = int(status_line.split()[1])
        return status, json.loads(body_bytes.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
