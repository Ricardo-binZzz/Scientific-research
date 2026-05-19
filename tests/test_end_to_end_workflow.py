import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from workflow.cli import main


class EndToEndWorkflowTests(unittest.TestCase):
    def test_project_workflow_runs_from_library_to_figure(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            self.assertEqual(main(["init", tmpdir, "--slug", "demo", "--name", "Demo"]), 0)
            project = base / "demo"

            literature = project / "literature"
            notes = project / "notes"
            manuscript = project / "manuscript"
            simulation = project / "simulation"
            figures = project / "figures"

            self.assertEqual(
                main(
                    [
                        "library",
                        "add",
                        str(literature),
                        "--title",
                        "Adaptive clamping fixture",
                        "--author",
                        "Zhang",
                        "--year",
                        "2024",
                        "--source",
                        "Journal of Manufacturing Systems",
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
            self.assertEqual(
                main(
                    [
                        "note",
                        "paper-summary",
                        str(notes),
                        "--title",
                        "Adaptive clamping fixture",
                        "--author",
                        "Zhang",
                        "--source",
                        "Journal of Manufacturing Systems",
                        "--year",
                        "2024",
                        "--doi",
                        "10.1000/example",
                        "--problem",
                        "Deviation",
                        "--method",
                        "Fixture",
                        "--data",
                        "Experiment",
                        "--key-figures",
                        "Figure 3",
                        "--main-result",
                        "Improved stability",
                        "--limitation",
                        "Manual setup",
                        "--reuse-value",
                        "Mechanism comparison",
                        "--source-pages",
                        "pp. 1-8",
                        "--timestamp",
                        "20260518-100000",
                    ]
                ),
                0,
            )

            draft = manuscript / "chapter.md"
            draft.write_text("# Introduction\n\nText [@zhang2024adaptive].\n\nFigure 1 shows the result.\n", encoding="utf-8")
            output = StringIO()
            with redirect_stdout(output):
                self.assertEqual(
                    main(
                        [
                            "manuscript",
                            "check",
                            str(draft),
                            "--required-section",
                            "Introduction",
                            "--expected-figure",
                            "Figure 1",
                            "--library-root",
                            str(literature),
                        ]
                    ),
                    0,
                )
            self.assertIn("- None", output.getvalue())

            data_path = simulation / "result.csv"
            data_path.write_text("time,stress\n0,0\n1,2\n", encoding="utf-8")
            output = StringIO()
            with redirect_stdout(output):
                self.assertEqual(
                    main(
                        [
                            "simulation",
                            "validate-data",
                            str(data_path),
                            "--required-column",
                            "time",
                            "--required-column",
                            "stress",
                            "--numeric-column",
                            "stress",
                        ]
                    ),
                    0,
                )
            self.assertIn("OK: True", output.getvalue())

            self.assertEqual(
                main(
                    [
                        "figure",
                        "from-data",
                        str(data_path),
                        str(figures),
                        "--stem",
                        "stress-response",
                        "--title",
                        "Stress response",
                        "--figure-type",
                        "trend",
                        "--x-column",
                        "time",
                        "--y-column",
                        "stress",
                        "--x-label",
                        "Time (s)",
                        "--y-label",
                        "Stress (MPa)",
                    ]
                ),
                0,
            )
            self.assertTrue((figures / "stress-response.svg").exists())
            self.assertTrue((figures / "stress-response.json").exists())


if __name__ == "__main__":
    unittest.main()
