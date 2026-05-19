import tempfile
import unittest
from pathlib import Path

from workflow.cli import main
from workflow.literature_table import build_literature_table, render_literature_table
from workflow.notes import PaperSummary, create_note_file, render_paper_summary


class LiteratureTableTests(unittest.TestCase):
    def test_build_literature_table_reads_paper_summary_notes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            notes_dir = Path(tmpdir) / "notes"
            create_note_file(
                notes_dir,
                note_type="paper-summary",
                title="Adaptive clamping fixture",
                timestamp="20260519-120000",
                content=render_paper_summary(
                    PaperSummary(
                        title="Adaptive clamping fixture",
                        authors=["Zhang", "Li"],
                        source="Journal A",
                        year=2024,
                        doi="10.1000/a",
                        problem="Fixture deformation",
                        method="Finite element analysis",
                        data="Stress and displacement",
                        key_figures="Fig. 3",
                        main_result="Lower deformation",
                        limitation="Small sample",
                        reuse_value="Metric reference",
                        source_pages="pp. 1-5",
                    )
                ),
            )
            create_note_file(
                notes_dir,
                note_type="search-log",
                title="Fixture search",
                timestamp="20260519-121000",
                content="# Search Log\n\n- Question: fixture\n",
            )

            table = build_literature_table(notes_dir)

        self.assertEqual(len(table.rows), 1)
        self.assertEqual(table.rows[0].title, "Adaptive clamping fixture")
        self.assertEqual(table.rows[0].authors, "Zhang; Li")
        self.assertEqual(table.rows[0].method, "Finite element analysis")
        self.assertEqual(table.rows[0].reuse_value, "Metric reference")

    def test_render_literature_table_outputs_markdown_comparison(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            notes_dir = Path(tmpdir) / "notes"
            create_note_file(
                notes_dir,
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

            text = render_literature_table(build_literature_table(notes_dir))

        self.assertIn("# Literature Comparison Table", text)
        self.assertIn("| Title | Authors | Year | Source | Problem | Method | Data | Main result | Limitation | Reuse value | Source pages |", text)
        self.assertIn("| Adaptive clamping fixture | Zhang | 2024 | Journal A | Fixture deformation | Finite element analysis | Stress | Lower deformation | Small sample | Metric reference | pp. 1-5 |", text)

    def test_cli_project_literature_table_writes_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            self.assertEqual(main(["init", tmpdir, "--slug", "demo", "--name", "Demo"]), 0)
            root = Path(tmpdir) / "demo"
            create_note_file(
                root / "notes",
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
            out_path = root / "literature-table.md"

            exit_code = main(["project", "literature-table", str(root), "--out", str(out_path)])

            self.assertEqual(exit_code, 0)
            self.assertTrue(out_path.exists())
            self.assertIn("Adaptive clamping fixture", out_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
