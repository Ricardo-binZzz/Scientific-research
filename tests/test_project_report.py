import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from workflow.cli import main
from workflow.project_report import build_project_check, build_project_report, render_project_check, render_project_report


class ProjectReportTests(unittest.TestCase):
    def test_build_project_report_counts_core_assets(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.assertEqual(main(["init", tmpdir, "--slug", "demo", "--name", "Demo"]), 0)
            project = root / "demo"
            (project / "notes" / "summary.md").write_text("# Paper Summary\n", encoding="utf-8")
            (project / "figures" / "plot.svg").write_text("<svg></svg>", encoding="utf-8")
            (project / "figures" / "plot.json").write_text("{}", encoding="utf-8")
            (project / "simulation" / "result.csv").write_text("x,y\n0,1\n", encoding="utf-8")
            self.assertEqual(
                main(
                    [
                        "library",
                        "add",
                        str(project / "literature"),
                        "--title",
                        "Adaptive clamping fixture",
                        "--author",
                        "Zhang",
                        "--year",
                        "2024",
                        "--source",
                        "Journal",
                        "--doi",
                        "10.1000/example",
                        "--pdf-name",
                        "paper.pdf",
                        "--note-path",
                        "notes/summary.md",
                    ]
                ),
                0,
            )

            report = build_project_report(project)

        self.assertEqual(report.library_entries, 1)
        self.assertEqual(report.note_files, 1)
        self.assertEqual(report.figure_bundles, 1)
        self.assertEqual(report.simulation_exports, 1)

    def test_render_project_report_lists_counts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.assertEqual(main(["init", tmpdir, "--slug", "demo", "--name", "Demo"]), 0)
            report = build_project_report(root / "demo")

            text = render_project_report(report)

        self.assertIn("# Project Status Report", text)
        self.assertIn("Library entries", text)

    def test_cli_project_report_prints_counts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.assertEqual(main(["init", tmpdir, "--slug", "demo", "--name", "Demo"]), 0)
            output = StringIO()

            with redirect_stdout(output):
                exit_code = main(["project", "report", str(root / "demo")])

        self.assertEqual(exit_code, 0)
        self.assertIn("# Project Status Report", output.getvalue())

    def test_build_project_check_reports_library_pdfs_simulation_and_manuscript(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.assertEqual(main(["init", tmpdir, "--slug", "demo", "--name", "Demo"]), 0)
            project = root / "demo"
            (project / "simulation" / "result.csv").write_text("time,stress\n0,1\n1,bad\n", encoding="utf-8")
            (project / "manuscript" / "chapter.md").write_text("# Introduction\n\nFigure 1.\n", encoding="utf-8")
            self.assertEqual(
                main(
                    [
                        "library",
                        "add",
                        str(project / "literature"),
                        "--title",
                        "Adaptive clamping fixture",
                        "--author",
                        "Zhang",
                        "--year",
                        "2024",
                        "--source",
                        "Journal",
                        "--doi",
                        "10.1000/example",
                        "--pdf-name",
                        "missing.pdf",
                        "--note-path",
                        "notes/summary.md",
                    ]
                ),
                0,
            )

            check = build_project_check(project)

        self.assertIn("missing.pdf", check.missing_pdf_names)
        self.assertTrue(any("stress" in issue for issue in check.simulation_issues))
        self.assertTrue(any("No citation markers found" in issue for issue in check.manuscript_issues))

    def test_build_project_check_reports_simulation_range_issues(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.assertEqual(main(["init", tmpdir, "--slug", "demo", "--name", "Demo"]), 0)
            project = root / "demo"
            (project / "simulation" / "result.csv").write_text("time,stress\n0,50\n1,120\n", encoding="utf-8")
            (project / "project-check.json").write_text(
                '{\n'
                '  "simulation": {\n'
                '    "required_columns": ["time", "stress"],\n'
                '    "numeric_columns": ["time", "stress"],\n'
                '    "ranges": {"stress": [0, 100]}\n'
                '  },\n'
                '  "manuscript": {}\n'
                '}\n',
                encoding="utf-8",
            )

            check = build_project_check(project)
            text = render_project_check(check)

        self.assertTrue(any("stress out of range 1" in issue for issue in check.simulation_issues))
        self.assertIn("result.csv: stress out of range 1", text)

    def test_render_project_check_lists_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.assertEqual(main(["init", tmpdir, "--slug", "demo", "--name", "Demo"]), 0)
            check = build_project_check(root / "demo")

            text = render_project_check(check)

        self.assertIn("# Project Check Report", text)
        self.assertIn("## Literature", text)
        self.assertIn("## Simulation", text)
        self.assertIn("## Manuscript", text)
        self.assertIn("## Project Summary", text)

    def test_cli_project_check_prints_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.assertEqual(main(["init", tmpdir, "--slug", "demo", "--name", "Demo"]), 0)
            output = StringIO()

            with redirect_stdout(output):
                exit_code = main(["project", "check", str(root / "demo")])

        self.assertEqual(exit_code, 0)
        self.assertIn("# Project Check Report", output.getvalue())


if __name__ == "__main__":
    unittest.main()
