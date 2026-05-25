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
