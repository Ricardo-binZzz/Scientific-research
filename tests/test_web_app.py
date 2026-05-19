import tempfile
import unittest
from pathlib import Path
from http.server import BaseHTTPRequestHandler

from workflow.bootstrap import bootstrap_workspace
from workflow.web_app import _create_server, handle_web_action, render_home_page


class WebAppTests(unittest.TestCase):
    def test_render_home_page_contains_core_controls(self) -> None:
        html = render_home_page(default_project_root=r"C:\Research\demo")

        self.assertIn("科研工作流控制台", html)
        self.assertIn("新建课题", html)
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

    def test_handle_init_project_action_creates_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            status, _content_type, body = handle_web_action(
                {
                    "action": "init_project",
                    "base_dir": tmpdir,
                    "project_slug": "demo",
                    "project_name": "Demo",
                }
            )

            project = Path(tmpdir) / "demo"
            exists = project.exists()

        self.assertEqual(status, 200)
        self.assertIn("已创建课题", body)
        self.assertTrue(exists)

    def test_handle_library_import_csv_action_imports_entries(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project = bootstrap_workspace(Path(tmpdir), project_slug="demo", project_name="Demo")
            csv_path = project / "papers.csv"
            csv_path.write_text(
                "Title,Authors,Year,Journal,DOI,File,Note\n"
                "Fixture stiffness,Zhang,2024,Journal A,10.1000/a,a.pdf,notes/a.md\n",
                encoding="utf-8",
            )

            status, _content_type, body = handle_web_action(
                {"action": "library_import_csv", "project_root": str(project), "csv_path": str(csv_path)}
            )

            search_status, _content_type, search_body = handle_web_action(
                {"action": "library_search", "project_root": str(project), "query": "Fixture"}
            )

        self.assertEqual(status, 200)
        self.assertIn("已导入", body)
        self.assertEqual(search_status, 200)
        self.assertIn("Fixture stiffness", search_body)

    def test_handle_paper_summary_action_writes_note(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project = bootstrap_workspace(Path(tmpdir), project_slug="demo", project_name="Demo")

            status, _content_type, body = handle_web_action(
                {
                    "action": "note_paper_summary",
                    "project_root": str(project),
                    "summary_title": "Adaptive clamping fixture",
                    "summary_authors": "Zhang; Li",
                    "summary_source": "Journal A",
                    "summary_year": "2024",
                    "summary_doi": "10.1000/a",
                    "summary_problem": "Fixture deformation",
                    "summary_method": "Finite element analysis",
                    "summary_data": "Stress and displacement",
                    "summary_key_figures": "Fig. 3",
                    "summary_main_result": "Lower deformation",
                    "summary_limitation": "Small sample",
                    "summary_reuse_value": "Metric reference",
                    "summary_source_pages": "pp. 1-5",
                }
            )
            note_files = list((project / "notes").glob("*adaptive-clamping-fixture.md"))

        self.assertEqual(status, 200)
        self.assertIn("已生成摘要卡", body)
        self.assertEqual(len(note_files), 1)

    def test_handle_search_log_action_writes_note(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project = bootstrap_workspace(Path(tmpdir), project_slug="demo", project_name="Demo")

            status, _content_type, body = handle_web_action(
                {
                    "action": "note_search_log",
                    "project_root": str(project),
                    "search_question": "Fixture optimization",
                    "search_keywords": "fixture; clamping",
                    "search_query": "fixture clamping optimization",
                    "search_source": "Google Scholar",
                    "search_date": "2026-05-19",
                    "search_filters": "2020-2026",
                    "search_result_count": "12",
                    "search_notes": "Focus on FEM papers",
                }
            )
            note_files = list((project / "notes").glob("*fixture-optimization.md"))

        self.assertEqual(status, 200)
        self.assertIn("已生成检索记录", body)
        self.assertEqual(len(note_files), 1)

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

    def test_create_server_uses_next_port_when_requested_port_is_busy(self) -> None:
        probe = _create_server("127.0.0.1", 8000, _QuietHandler)
        busy_port = probe.server_address[1]
        probe.server_close()
        first_server = _create_server("127.0.0.1", busy_port, _QuietHandler)
        try:
            second_server = _create_server("127.0.0.1", busy_port, _QuietHandler)
            try:
                self.assertEqual(second_server.server_address[1], busy_port + 1)
            finally:
                second_server.server_close()
        finally:
            first_server.server_close()


class _QuietHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:
        return


if __name__ == "__main__":
    unittest.main()
