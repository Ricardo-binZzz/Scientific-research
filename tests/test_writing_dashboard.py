import tempfile
import unittest
from pathlib import Path

from workflow.bootstrap import bootstrap_workspace
from argparse import Namespace

from workflow.cli import main
from workflow.library import LibraryEntry, add_entry, load_index
from workflow.notes import PaperSummary, create_note_file, render_paper_summary
from workflow.writing_dashboard import build_writing_dashboard, render_writing_dashboard


class WritingDashboardTests(unittest.TestCase):
    def test_build_writing_dashboard_groups_ready_assets_and_gaps(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project = bootstrap_workspace(Path(tmpdir), project_slug="demo", project_name="Demo")
            (project / "figures" / "stress.svg").write_text("<svg></svg>", encoding="utf-8")
            (project / "figures" / "stress.json").write_text("{}", encoding="utf-8")
            (project / "simulation" / "result.csv").write_text("time,stress\n0,10\n", encoding="utf-8")
            (project / "manuscript" / "chapter.md").write_text("# Introduction\n\nFigure 1\n", encoding="utf-8")
            create_note_file(
                project / "notes",
                note_type="paper-summary",
                title="Adaptive clamping fixture",
                timestamp="20260519-120000",
                content=render_paper_summary(
                    PaperSummary(
                        title="Adaptive clamping fixture",
                        authors=["Zhang"],
                        source="Journal A",
                        year=2024,
                        doi="10.1000/a",
                        problem="Fixture deformation",
                        method="Finite element analysis",
                        data="Stress",
                        key_figures="Fig. 3",
                        main_result="Lower deformation",
                        limitation="Small sample",
                        reuse_value="Metric reference",
                        source_pages="pp. 1-5",
                    )
                ),
            )
            add_entry(
                project / "literature",
                load_index(project / "literature"),
                LibraryEntry(
                    title="Adaptive clamping fixture",
                    authors=["Zhang"],
                    year=2024,
                    source="Journal A",
                    doi="10.1000/a",
                    pdf_name="missing.pdf",
                    note_path="notes/missing.md",
                ),
            )

            dashboard = build_writing_dashboard(project)

        self.assertEqual(dashboard.recent_literature_count, 1)
        self.assertEqual(dashboard.summary_note_count, 1)
        self.assertEqual(dashboard.figure_bundles, ["stress"])
        self.assertEqual(dashboard.simulation_exports, ["result.csv"])
        self.assertEqual(dashboard.manuscript_files, ["chapter.md"])
        self.assertEqual(dashboard.gaps, ["Missing PDFs: missing.pdf", "Missing notes: notes/missing.md"])

    def test_render_writing_dashboard_outputs_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project = bootstrap_workspace(Path(tmpdir), project_slug="demo", project_name="Demo")
            dashboard = build_writing_dashboard(project)

            text = render_writing_dashboard(dashboard)

        self.assertIn("# Writing Dashboard", text)
        self.assertIn("## Ready for Background", text)
        self.assertIn("## Ready for Methods", text)
        self.assertIn("## Ready for Results", text)
        self.assertIn("## Gaps to Fix", text)

    def test_writing_dashboard_includes_rich_literature_signals(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project = bootstrap_workspace(Path(tmpdir), project_slug="demo", project_name="Demo")
            add_entry(
                project / "literature",
                load_index(project / "literature"),
                LibraryEntry(
                    title="Highly cited fixture review",
                    authors=["Zhang"],
                    year=2024,
                    source="Journal A",
                    doi="10.1000/rich-a",
                    pdf_name="a.pdf",
                    note_path="notes/a.md",
                    abstract="Reviews adaptive fixture methods.",
                    keywords=["fixture", "adaptive"],
                    citation_count=42,
                ),
            )
            add_entry(
                project / "literature",
                load_index(project / "literature"),
                LibraryEntry(
                    title="Fixture case study",
                    authors=["Li"],
                    year=2023,
                    source="Journal B",
                    doi="10.1000/rich-b",
                    pdf_name="b.pdf",
                    note_path="notes/b.md",
                    keywords=["fixture"],
                    citation_count=7,
                ),
            )

            dashboard = build_writing_dashboard(project)
            text = render_writing_dashboard(dashboard)

        self.assertEqual(dashboard.abstract_ready_count, 1)
        self.assertEqual(dashboard.top_keywords, ["fixture (2)", "adaptive (1)"])
        self.assertEqual(dashboard.high_citation_count, 2)
        self.assertIn("- Abstract-ready literature: 1", text)
        self.assertIn("- High-citation candidates: 2", text)
        self.assertIn("- Top keywords: fixture (2), adaptive (1)", text)

    def test_cli_project_writing_dashboard_writes_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project = bootstrap_workspace(Path(tmpdir), project_slug="demo", project_name="Demo")
            out_path = project / "writing-dashboard.md"

            exit_code = main(["project", "writing-dashboard", str(project), "--out", str(out_path)])

            self.assertEqual(exit_code, 0)
            self.assertTrue(out_path.exists())
            self.assertIn("# Writing Dashboard", out_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
