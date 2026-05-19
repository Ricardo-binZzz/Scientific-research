import tempfile
import unittest
from pathlib import Path

from workflow.bootstrap import bootstrap_workspace
from workflow.web_app import handle_web_action, render_home_page


class WebAppTests(unittest.TestCase):
    def test_render_home_page_contains_core_controls(self) -> None:
        html = render_home_page(default_project_root=r"C:\Research\demo")

        self.assertIn("科研工作流控制台", html)
        self.assertIn("项目体检", html)
        self.assertIn("文献库统计", html)
        self.assertIn("仿真数据", html)
        self.assertIn(r"C:\Research\demo", html)

    def test_handle_project_check_action_returns_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project = bootstrap_workspace(Path(tmpdir), project_slug="demo", project_name="Demo")

            status, content_type, body = handle_web_action({"action": "project_check", "project_root": str(project)})

        self.assertEqual(status, 200)
        self.assertEqual(content_type, "text/plain; charset=utf-8")
        self.assertIn("# Project Check Report", body)

    def test_handle_library_search_action_returns_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project = bootstrap_workspace(Path(tmpdir), project_slug="demo", project_name="Demo")
            handle_web_action(
                {
                    "action": "library_add",
                    "project_root": str(project),
                    "title": "Adaptive clamping fixture",
                    "authors": "Zhang; Li",
                    "year": "2024",
                    "source": "Journal",
                    "doi": "10.1000/example",
                    "pdf_name": "paper.pdf",
                    "note_path": "notes/summary.md",
                }
            )

            status, _content_type, body = handle_web_action(
                {"action": "library_search", "project_root": str(project), "query": "clamping"}
            )

        self.assertEqual(status, 200)
        self.assertIn("Adaptive clamping fixture", body)

    def test_handle_simulation_actions_return_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project = bootstrap_workspace(Path(tmpdir), project_slug="demo", project_name="Demo")
            data_path = project / "simulation" / "result.csv"
            data_path.write_text("time,stress\n0,10\n1,20\n", encoding="utf-8")

            inspect_status, _content_type, inspect_body = handle_web_action(
                {"action": "simulation_inspect", "project_root": str(project), "data_path": str(data_path)}
            )
            summarize_status, _content_type, summarize_body = handle_web_action(
                {"action": "simulation_summarize", "project_root": str(project), "data_path": str(data_path)}
            )
            validate_status, _content_type, validate_body = handle_web_action(
                {
                    "action": "simulation_validate",
                    "project_root": str(project),
                    "data_path": str(data_path),
                    "required_columns": "time,stress",
                    "numeric_columns": "time,stress",
                }
            )

        self.assertEqual(inspect_status, 200)
        self.assertIn("Columns", inspect_body)
        self.assertEqual(summarize_status, 200)
        self.assertIn("stress", summarize_body)
        self.assertEqual(validate_status, 200)
        self.assertIn("# Dataset Validation Report", validate_body)


if __name__ == "__main__":
    unittest.main()
