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
        self.assertIn('class="app-shell"', html)
        self.assertIn('class="sidebar"', html)
        self.assertIn('class="workspace"', html)
        self.assertIn('class="result-panel"', html)
        self.assertIn('id="insightPanel"', html)
        self.assertIn('class="insight-panel"', html)
        self.assertIn("新建课题", html)
        self.assertIn("项目体检", html)
        self.assertIn("文献库统计", html)
        self.assertIn("仿真数据", html)
        self.assertIn("稿件检查", html)
        self.assertIn("生成图", html)
        self.assertIn("复制结果", html)
        self.assertIn("下载 .md", html)
        self.assertIn("保存常用报告", html)
        self.assertIn("value=\"heatmap\"", html)
        self.assertIn("id=\"valueColumn\"", html)
        self.assertIn("加载示例课题", html)
        self.assertIn("填充常用路径", html)
        self.assertIn("扫描可用文件", html)
        self.assertIn("流程状态", html)
        self.assertIn("id=\"figureWidthMm\"", html)
        self.assertIn("id=\"figureHeightMm\"", html)
        self.assertIn("id=\"xMin\"", html)
        self.assertIn("id=\"yMax\"", html)
        self.assertIn("id=\"showLegend\"", html)
        self.assertIn("id=\"showGrid\"", html)
        self.assertIn("id=\"palette\"", html)
        self.assertIn("id=\"tickCount\"", html)
        self.assertIn("literature_insights", html)
        self.assertIn(r"C:\Research\demo", html)
        self.assertNotIn("return f\"\"\"<!doctype html>", html)

    def test_frontend_assets_include_literature_insight_renderer(self) -> None:
        js_path = Path("workflow") / "web_assets" / "app.js"
        css_path = Path("workflow") / "web_assets" / "styles.css"
        html_path = Path("workflow") / "web_assets" / "index.html"
        js = js_path.read_text(encoding="utf-8")
        css = css_path.read_text(encoding="utf-8")
        html = html_path.read_text(encoding="utf-8")

        self.assertIn("renderLiteratureInsights", js)
        self.assertIn("parseMarkdownListSection", js)
        self.assertIn("renderProjectFileScan", js)
        self.assertIn("parseSuggestedPaths", js)
        self.assertIn("renderWorkflowStatus", js)
        self.assertIn("parseWorkflowSteps", js)
        self.assertIn("workflowTargetForStep", js)
        self.assertIn("workflow-jump-button", js)
        self.assertIn("renderProjectCheck", js)
        self.assertIn("parseProjectCheckCards", js)
        self.assertIn("renderManuscriptCheck", js)
        self.assertIn("parseManuscriptIssues", js)
        self.assertIn("renderSimulationReport", js)
        self.assertIn("parseSimulationReportRows", js)
        self.assertIn("renderFigureResult", js)
        self.assertIn("parseGeneratedPaths", js)
        self.assertIn("renderSavedReportResult", js)
        self.assertIn("savedReportPurpose", js)
        self.assertIn("renderNoteResult", js)
        self.assertIn("noteResultPurpose", js)
        self.assertIn("renderLibraryResult", js)
        self.assertIn("parseLibraryEntries", js)
        self.assertIn("renderLibraryAssetReport", js)
        self.assertIn("parseInventorySection", js)
        self.assertIn("renderPlanningReport", js)
        self.assertIn("planningReportSections", js)
        self.assertIn("renderProjectReport", js)
        self.assertIn("parseProjectReportMetrics", js)
        self.assertIn("renderProjectInitResult", js)
        self.assertIn("parseCreatedProjectPath", js)
        self.assertIn("renderResultFallback", js)
        self.assertIn("resultFallbackAdvice", js)
        self.assertIn("fallbackTargetForAction", js)
        self.assertIn("data-target-section", js)
        self.assertIn("highlightTargetSection", js)
        self.assertIn("section-highlight", js)
        self.assertIn("validateActionPayload", js)
        self.assertIn("actionNeedsProjectRoot", js)
        self.assertIn("actionPrimaryPath", js)
        self.assertIn("actionSecondaryRequiredField", js)
        self.assertIn("focusMissingField", js)
        self.assertIn("fieldLabelForId", js)
        self.assertIn("lastSuccessSummary", js)
        self.assertIn("updateLastSuccess", js)
        self.assertIn("successHistory", js)
        self.assertIn("setResultLoading", js)
        self.assertIn("insight-card", css)
        self.assertIn("keyword-pill", css)
        self.assertIn("path-card", css)
        self.assertIn("path-fill-button", css)
        self.assertIn("workflow-step-card", css)
        self.assertIn("next-action-card", css)
        self.assertIn("workflow-jump-button", css)
        self.assertIn("health-card", css)
        self.assertIn("manuscript-issue-card", css)
        self.assertIn("simulation-card", css)
        self.assertIn("figure-result-card", css)
        self.assertIn("saved-report-card", css)
        self.assertIn("note-result-card", css)
        self.assertIn("library-result-card", css)
        self.assertIn("library-asset-card", css)
        self.assertIn("planning-report-card", css)
        self.assertIn("project-report-card", css)
        self.assertIn("project-init-card", css)
        self.assertIn("result-fallback-card", css)
        self.assertIn("section-highlight", css)
        self.assertIn("required-field", html)
        self.assertIn("required-field", css)
        self.assertIn("last-success", css)
        self.assertIn("success-history", css)
        self.assertIn("result-loading", css)

    def test_handle_project_check_action_returns_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project = bootstrap_workspace(Path(tmpdir), project_slug="demo", project_name="Demo")

            status, content_type, body = handle_web_action({"action": "project_check", "project_root": str(project)})

        self.assertEqual(status, 200)
        self.assertEqual(content_type, "text/plain; charset=utf-8")
        self.assertIn("# Project Check Report", body)

    def test_handle_workflow_status_action_returns_next_steps(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project = bootstrap_workspace(Path(tmpdir), project_slug="demo", project_name="Demo")
            data_path = project / "simulation" / "result.csv"
            data_path.write_text("time,stress\n0,10\n", encoding="utf-8")

            status, content_type, body = handle_web_action({"action": "workflow_status", "project_root": str(project)})

        self.assertEqual(status, 200)
        self.assertEqual(content_type, "text/plain; charset=utf-8")
        self.assertIn("# Workflow Status", body)
        self.assertIn("Literature library", body)
        self.assertIn("Simulation data", body)
        self.assertIn("Next recommended action", body)

    def test_handle_scan_project_files_lists_common_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project = bootstrap_workspace(Path(tmpdir), project_slug="demo", project_name="Demo")
            (project / "simulation" / "result.csv").write_text("time,stress\n0,10\n", encoding="utf-8")
            (project / "manuscript" / "chapter.md").write_text("# Introduction\n", encoding="utf-8")

            status, content_type, body = handle_web_action({"action": "scan_project_files", "project_root": str(project)})

        self.assertEqual(status, 200)
        self.assertEqual(content_type, "text/plain; charset=utf-8")
        self.assertIn("# Available Project Files", body)
        self.assertIn("simulation/result.csv", body)
        self.assertIn("manuscript/chapter.md", body)

    def test_handle_scan_project_files_includes_suggested_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project = bootstrap_workspace(Path(tmpdir), project_slug="demo", project_name="Demo")
            (project / "simulation" / "result.csv").write_text("time,stress\n0,10\n", encoding="utf-8")
            (project / "manuscript" / "chapter.md").write_text("# Introduction\n", encoding="utf-8")
            (project / "papers.csv").write_text("Title,Authors\nFixture,Zhang\n", encoding="utf-8")

            status, _content_type, body = handle_web_action({"action": "scan_project_files", "project_root": str(project)})

        self.assertEqual(status, 200)
        self.assertIn("## Suggested Form Paths", body)
        self.assertIn(f"- data_path: {project / 'simulation' / 'result.csv'}", body)
        self.assertIn(f"- figure_data_path: {project / 'simulation' / 'result.csv'}", body)
        self.assertIn(f"- manuscript_path: {project / 'manuscript' / 'chapter.md'}", body)
        self.assertIn(f"- csv_path: {project / 'papers.csv'}", body)
        self.assertIn(f"- figure_out_dir: {project / 'figures'}", body)

    def test_handle_writing_pack_action_returns_enriched_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project = bootstrap_workspace(Path(tmpdir), project_slug="demo", project_name="Demo")
            (project / "manuscript" / "draft.md").write_text("# Introduction\n", encoding="utf-8")
            handle_web_action(
                {
                    "action": "library_add",
                    "project_root": str(project),
                    "title": "Recent adaptive fixture",
                    "authors": "Zhang",
                    "year": "2024",
                    "source": "Journal",
                    "doi": "10.1000/recent",
                    "pdf_name": "recent.pdf",
                    "note_path": "notes/recent.md",
                }
            )

            status, _content_type, body = handle_web_action({"action": "writing_pack", "project_root": str(project)})

        self.assertEqual(status, 200)
        self.assertIn("## Recent Literature", body)
        self.assertIn("Recent adaptive fixture", body)
        self.assertIn("## Library Gaps", body)
        self.assertIn("recent.pdf", body)
        self.assertIn("## Manuscript Drafts", body)
        self.assertIn("draft.md", body)

    def test_handle_save_standard_report_writes_known_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project = bootstrap_workspace(Path(tmpdir), project_slug="demo", project_name="Demo")
            handle_web_action(
                {
                    "action": "library_add",
                    "project_root": str(project),
                    "title": "Recent adaptive fixture",
                    "authors": "Zhang",
                    "year": "2024",
                    "source": "Journal",
                    "doi": "10.1000/recent",
                    "pdf_name": "recent.pdf",
                    "note_path": "notes/recent.md",
                }
            )

            status, _content_type, body = handle_web_action(
                {
                    "action": "save_standard_report",
                    "project_root": str(project),
                    "report_kind": "writing_pack",
                }
            )
            out_path = project / "manuscript" / "writing-pack.md"
            out_exists = out_path.exists()
            out_text = out_path.read_text(encoding="utf-8")

        self.assertEqual(status, 200)
        self.assertIn("已保存标准报告", body)
        self.assertIn("writing-pack.md", body)
        self.assertTrue(out_exists)
        self.assertIn("# Writing Pack", out_text)

    def test_handle_save_standard_report_rejects_unknown_kind(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project = bootstrap_workspace(Path(tmpdir), project_slug="demo", project_name="Demo")

            status, _content_type, body = handle_web_action(
                {
                    "action": "save_standard_report",
                    "project_root": str(project),
                    "report_kind": "unknown",
                }
            )

        self.assertEqual(status, 400)
        self.assertIn("不支持的标准报告", body)

    def test_handle_literature_table_action_returns_comparison(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project = bootstrap_workspace(Path(tmpdir), project_slug="demo", project_name="Demo")
            handle_web_action(
                {
                    "action": "note_paper_summary",
                    "project_root": str(project),
                    "summary_title": "Adaptive clamping fixture",
                    "summary_authors": "Zhang",
                    "summary_source": "Journal A",
                    "summary_year": "2024",
                    "summary_doi": "10.1000/a",
                    "summary_problem": "Fixture deformation",
                    "summary_method": "Finite element analysis",
                    "summary_data": "Stress",
                    "summary_key_figures": "Fig. 3",
                    "summary_main_result": "Lower deformation",
                    "summary_limitation": "Small sample",
                    "summary_reuse_value": "Metric reference",
                    "summary_source_pages": "pp. 1-5",
                }
            )

            status, _content_type, body = handle_web_action({"action": "literature_table", "project_root": str(project)})

        self.assertEqual(status, 200)
        self.assertIn("# Literature Comparison Table", body)
        self.assertIn("Adaptive clamping fixture", body)
        self.assertIn("Finite element analysis", body)

    def test_handle_new_planning_actions_return_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project = bootstrap_workspace(Path(tmpdir), project_slug="demo", project_name="Demo")
            handle_web_action(
                {
                    "action": "library_add",
                    "project_root": str(project),
                    "title": "Adaptive clamping fixture",
                    "authors": "Zhang",
                    "year": "2024",
                    "source": "Journal A",
                    "doi": "10.1000/a",
                    "pdf_name": "a.pdf",
                    "note_path": "notes/a.md",
                }
            )

            dashboard_status, _content_type, dashboard_body = handle_web_action(
                {"action": "writing_dashboard", "project_root": str(project)}
            )
            map_status, _content_type, map_body = handle_web_action({"action": "literature_map", "project_root": str(project)})
            tracker_status, _content_type, tracker_body = handle_web_action(
                {"action": "literature_tracker", "project_root": str(project)}
            )

        self.assertEqual(dashboard_status, 200)
        self.assertIn("# Writing Dashboard", dashboard_body)
        self.assertEqual(map_status, 200)
        self.assertIn("# Literature Map", map_body)
        self.assertEqual(tracker_status, 200)
        self.assertIn("# Literature Tracking Plan", tracker_body)

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

    def test_handle_library_recent_and_source_actions_return_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project = bootstrap_workspace(Path(tmpdir), project_slug="demo", project_name="Demo")
            csv_path = project / "papers.csv"
            csv_path.write_text(
                "Title,Authors,Year,Journal,DOI,File,Note\n"
                "Old fixture,Zhang,2018,Old Journal,10.1000/old,old.pdf,notes/old.md\n"
                "Recent fixture,Li,2024,Journal of Manufacturing Systems,10.1000/recent,recent.pdf,notes/recent.md\n",
                encoding="utf-8",
            )
            handle_web_action({"action": "library_import_csv", "project_root": str(project), "csv_path": str(csv_path)})

            recent_status, _content_type, recent_body = handle_web_action(
                {"action": "library_recent", "project_root": str(project), "since_year": "2020"}
            )
            source_status, _content_type, source_body = handle_web_action(
                {"action": "library_source", "project_root": str(project), "source_query": "manufacturing"}
            )

        self.assertEqual(recent_status, 200)
        self.assertIn("Recent fixture", recent_body)
        self.assertNotIn("Old fixture", recent_body)
        self.assertEqual(source_status, 200)
        self.assertIn("Recent fixture", source_body)

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

    def test_handle_library_add_action_preserves_rich_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project = bootstrap_workspace(Path(tmpdir), project_slug="demo", project_name="Demo")

            status, _content_type, _body = handle_web_action(
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
                    "abstract": "Fixture abstract",
                    "keywords": "fixture; clamping",
                    "url": "https://example.com",
                    "database_source": "Scopus",
                    "citation_count": "12",
                }
            )
            search_status, _content_type, search_body = handle_web_action(
                {"action": "library_search", "project_root": str(project), "query": "Scopus"}
            )

        self.assertEqual(status, 200)
        self.assertEqual(search_status, 200)
        self.assertIn("Adaptive clamping fixture", search_body)
        self.assertIn("Citation count: 12", search_body)

    def test_handle_literature_insights_action_returns_rich_metadata_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project = bootstrap_workspace(Path(tmpdir), project_slug="demo", project_name="Demo")
            handle_web_action(
                {
                    "action": "library_add",
                    "project_root": str(project),
                    "title": "Highly cited fixture review",
                    "authors": "Zhang",
                    "year": "2024",
                    "source": "Journal A",
                    "doi": "10.1000/rich-a",
                    "pdf_name": "a.pdf",
                    "note_path": "notes/a.md",
                    "abstract": "Reviews adaptive fixture methods.",
                    "keywords": "fixture; adaptive",
                    "database_source": "Scopus",
                    "citation_count": "42",
                }
            )
            handle_web_action(
                {
                    "action": "library_add",
                    "project_root": str(project),
                    "title": "Fixture case study",
                    "authors": "Li",
                    "year": "2023",
                    "source": "Journal B",
                    "doi": "10.1000/rich-b",
                    "pdf_name": "b.pdf",
                    "note_path": "notes/b.md",
                    "keywords": "fixture",
                    "database_source": "Web of Science",
                    "citation_count": "7",
                }
            )

            status, content_type, body = handle_web_action({"action": "literature_insights", "project_root": str(project)})

        self.assertEqual(status, 200)
        self.assertEqual(content_type, "text/plain; charset=utf-8")
        self.assertIn("# Literature Insights", body)
        self.assertIn("- Total entries: 2", body)
        self.assertIn("- Abstract-ready entries: 1", body)
        self.assertIn("- High-citation candidates: 2", body)
        self.assertIn("- fixture: 2", body)
        self.assertIn("- Scopus: 1", body)
        self.assertIn("- Highly cited fixture review (42 citations)", body)

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
                    "x_min": "0",
                    "x_max": "2",
                    "y_min": "0",
                    "y_max": "30",
                    "show_legend": "false",
                    "show_grid": "false",
                    "palette": "mono",
                    "title_font_size": "20",
                    "label_font_size": "16",
                    "tick_font_size": "11",
                    "line_width": "3.5",
                    "tick_count": "7",
                }
            )
            svg_exists = (out_dir / "stress-response.svg").exists()
            json_exists = (out_dir / "stress-response.json").exists()
            payload = (out_dir / "stress-response.json").read_text(encoding="utf-8")
            svg_text = (out_dir / "stress-response.svg").read_text(encoding="utf-8")

        self.assertEqual(status, 200)
        self.assertIn("stress-response.svg", body)
        self.assertTrue(svg_exists)
        self.assertTrue(json_exists)
        self.assertIn('"x_min": 0.0', payload)
        self.assertIn('"y_max": 30.0', payload)
        self.assertIn('"show_legend": false', payload)
        self.assertIn('"palette": "mono"', payload)
        self.assertIn(".title{font-size:20px", svg_text)
        self.assertNotIn('class="grid"', svg_text)

    def test_handle_figure_from_data_action_writes_heatmap_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project = bootstrap_workspace(Path(tmpdir), project_slug="demo", project_name="Demo")
            data_path = project / "simulation" / "grid.csv"
            data_path.write_text("x,y,temp\n0,0,10\n0,1,20\n1,0,30\n1,1,40\n", encoding="utf-8")
            out_dir = project / "figures"

            status, _content_type, body = handle_web_action(
                {
                    "action": "figure_from_data",
                    "project_root": str(project),
                    "figure_data_path": str(data_path),
                    "figure_out_dir": str(out_dir),
                    "figure_stem": "temperature-map",
                    "figure_title": "Temperature map",
                    "figure_type": "heatmap",
                    "x_column": "x",
                    "y_columns": "y",
                    "value_column": "temp",
                    "x_label": "X",
                    "y_label": "Y",
                    "figure_width_mm": "120",
                    "figure_height_mm": "90",
                }
            )
            svg_text = (out_dir / "temperature-map.svg").read_text(encoding="utf-8")
            json_text = (out_dir / "temperature-map.json").read_text(encoding="utf-8")

        self.assertEqual(status, 200)
        self.assertIn("temperature-map.svg", body)
        self.assertIn("<rect", svg_text)
        self.assertIn('"width_mm": 120', json_text)
        self.assertIn('"height_mm": 90', json_text)

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
