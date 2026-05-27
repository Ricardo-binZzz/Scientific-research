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

    def test_project_config_supports_wechat_developer_tools_local_debug(self) -> None:
        project_config = json.loads(Path("miniprogram/project.config.json").read_text(encoding="utf-8"))

        self.assertEqual(project_config["compileType"], "miniprogram")
        self.assertEqual(project_config["miniprogramRoot"], "./")
        self.assertEqual(project_config["appid"], "touristappid")
        self.assertFalse(project_config["setting"]["urlCheck"])

    def test_api_wrapper_contains_pair_dashboard_run_and_report_calls(self) -> None:
        api_ts = Path("miniprogram/utils/api.ts").read_text(encoding="utf-8")

        self.assertIn("export interface MobileSummary", api_ts)
        self.assertIn("export function pairWithWorkbench", api_ts)
        self.assertIn("export function fetchDashboard", api_ts)
        self.assertIn("export function runWorkflowAction", api_ts)
        self.assertIn("export function updateReport", api_ts)
        self.assertIn("authorizedProjects?: string[]", api_ts)
        self.assertIn("Authorization", api_ts)

    def test_connect_page_verifies_project_before_switching_tabs(self) -> None:
        connect_ts = Path("miniprogram/pages/connect/connect.ts").read_text(encoding="utf-8")

        self.assertIn("fetchDashboard", connect_ts)
        self.assertIn('!baseUrl || !pin', connect_ts)
        self.assertIn("authorizedProjects", connect_ts)
        self.assertIn("selectedProjectRoot", connect_ts)
        self.assertIn("wx.setStorageSync", connect_ts)
        self.assertLess(connect_ts.index("fetchDashboard"), connect_ts.index('wx.setStorageSync("token"'))
        self.assertIn("项目路径", connect_ts)

    def test_pages_use_soft_research_assistant_language(self) -> None:
        dashboard = Path("miniprogram/pages/dashboard/dashboard.wxml").read_text(encoding="utf-8")
        reports = Path("miniprogram/pages/reports/reports.wxml").read_text(encoding="utf-8")
        run = Path("miniprogram/pages/run/run.wxml").read_text(encoding="utf-8")

        self.assertIn("今天的研究进度", dashboard)
        self.assertIn("开始一次体检", dashboard)
        self.assertIn("整理好的材料", reports)
        self.assertIn("先处理这些", run)
        self.assertNotIn("project check", dashboard.lower())

    def test_report_center_exposes_all_v1_standard_reports(self) -> None:
        reports_ts = Path("miniprogram/pages/reports/reports.ts").read_text(encoding="utf-8")

        for report_kind in (
            "writing_pack",
            "writing_dashboard",
            "literature_table",
            "literature_map",
            "literature_tracker",
        ):
            self.assertIn(f'kind: "{report_kind}"', reports_ts)
        self.assertIn("写作看板", reports_ts)
        self.assertIn("追踪清单", reports_ts)

    def test_report_center_can_open_project_health_report(self) -> None:
        reports_ts = Path("miniprogram/pages/reports/reports.ts").read_text(encoding="utf-8")

        self.assertIn('kind: "project_check"', reports_ts)
        self.assertIn("项目体检报告", reports_ts)
        self.assertIn("runWorkflowAction", reports_ts)

    def test_mobile_pages_surface_connection_and_action_errors(self) -> None:
        for page in ("dashboard", "run", "reports"):
            page_ts = Path(f"miniprogram/pages/{page}/{page}.ts").read_text(encoding="utf-8")
            page_wxml = Path(f"miniprogram/pages/{page}/{page}.wxml").read_text(encoding="utf-8")

            self.assertIn("message", page_ts)
            self.assertIn(".catch", page_ts)
            self.assertIn("response.ok", page_ts)
            self.assertIn("{{message}}", page_wxml)

    def test_tab_pages_offer_reconnect_navigation(self) -> None:
        for page in ("dashboard", "run", "reports"):
            page_ts = Path(f"miniprogram/pages/{page}/{page}.ts").read_text(encoding="utf-8")
            page_wxml = Path(f"miniprogram/pages/{page}/{page}.wxml").read_text(encoding="utf-8")

            self.assertIn("openConnect", page_ts)
            self.assertIn('url: "/pages/connect/connect"', page_ts)
            self.assertIn('bindtap="openConnect"', page_wxml)
            self.assertIn("重新连接工作台", page_wxml)

    def test_shared_styles_use_soft_tokens(self) -> None:
        app_wxss = Path("miniprogram/app.wxss").read_text(encoding="utf-8")

        self.assertIn("--green-soft", app_wxss)
        self.assertIn("--blue-soft", app_wxss)
        self.assertIn("border-radius: 8px", app_wxss)
        self.assertIn("box-shadow", app_wxss)


if __name__ == "__main__":
    unittest.main()
