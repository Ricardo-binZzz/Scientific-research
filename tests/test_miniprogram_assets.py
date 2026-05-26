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
