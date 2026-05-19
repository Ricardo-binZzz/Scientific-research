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
        self.assertIn("稿件检查", html)
        self.assertIn("生成图", html)
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

    def test_handle_manuscript_check_action_returns_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project = bootstrap_workspace(Path(tmpdir), project_slug="demo", project_name="Demo")
            manuscript_path = project / "manuscript" / "chapter.md"
            manuscript_path.write_text("# Introduction\n\nFigure 1.\n", encoding="utf-8")

            status, _content_type, body = handle_web_action(
                {
                    "action": "manuscript_check",
                    "project_root": str(project),
                    "manuscript_path": str(manuscript_path),
                    "required_sections": "Introduction,Method",
                    "expected_figures": "Figure 1",
                }
            )

        self.assertEqual(status, 200)
        self.assertIn("# Manuscript Check Report", body)
        self.assertIn("Missing section: Method", body)

    def test_handle_figure_from_data_action_writes_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project = bootstrap_workspace(Path(tmpdir), project_slug="demo", project_name="Demo")
            data_path = project / "simulation" / "result.csv"
            data_path.write_text("time,stress\n0,10\n1,20\n", encoding="utf-8")
            out_dir = project / "figures"

            status, _content_type, body = handle_web_action(
                {
                    "action": "figure_from_data",
                    "project_root": str(project),
                    "figure_data_path": str(data_path),
                    "figure_out_dir": str(out_dir),
                    "figure_stem": "stress-response",
                    "figure_title": "Stress response",
                    "figure_type": "trend",
                    "x_column": "time",
                    "y_columns": "stress",
                    "x_label": "Time (s)",
                    "y_label": "Stress (MPa)",
                }
            )
            svg_exists = (out_dir / "stress-response.svg").exists()
            json_exists = (out_dir / "stress-response.json").exists()

        self.assertEqual(status, 200)
        self.assertIn("stress-response.svg", body)
        self.assertTrue(svg_exists)
        self.assertTrue(json_exists)


if __name__ == "__main__":
    unittest.main()
