import tempfile
import unittest
from pathlib import Path

from workflow.cli import main
from workflow.notes import PaperSummary, SearchLogEntry, create_note_file, render_paper_summary, render_search_log


class NoteRenderingTests(unittest.TestCase):
    def test_render_search_log_includes_query_metadata(self) -> None:
        entry = SearchLogEntry(
            question="How to improve adaptive clamping?",
            keywords=["adaptive clamping", "mechanical design"],
            query='("adaptive clamping" OR fixture) AND manufacturing',
            source="Web of Science",
            date="2026-05-18",
            filters="English, 2020-2026",
            result_count=24,
            notes="Need papers with comparable fixtures.",
        )

        text = render_search_log(entry)

        self.assertIn("# Search Log", text)
        self.assertIn("How to improve adaptive clamping?", text)
        self.assertIn("adaptive clamping, mechanical design", text)
        self.assertIn("Web of Science", text)
        self.assertIn("24", text)

    def test_render_paper_summary_includes_key_sections(self) -> None:
        summary = PaperSummary(
            title="Adaptive clamping fixture for roll-to-roll processing",
            authors=["Zhang", "Li"],
            source="Journal of Manufacturing Systems",
            year=2024,
            doi="10.1000/example",
            problem="Fix position deviation",
            method="Bidirectional screw clamping mechanism",
            data="Experimental force response",
            key_figures="Figure 3 and Figure 6",
            main_result="Improved alignment stability",
            limitation="Needs manual calibration",
            reuse_value="Useful for mechanism comparison",
            source_pages="pp. 2-8",
        )

        text = render_paper_summary(summary)

        self.assertIn("# Paper Summary", text)
        self.assertIn("Adaptive clamping fixture", text)
        self.assertIn("Zhang; Li", text)
        self.assertIn("Improved alignment stability", text)
        self.assertIn("pp. 2-8", text)

    def test_create_note_file_uses_slug_and_timestamp(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = create_note_file(
                Path(tmpdir),
                note_type="search-log",
                title="Adaptive clamping",
                content="# Search Log\n",
                timestamp="20260518-090000",
            )

            self.assertTrue(path.name.startswith("20260518-090000-adaptive-clamping"))
            self.assertEqual(path.read_text(encoding="utf-8"), "# Search Log\n")


class NoteCliTests(unittest.TestCase):
    def test_cli_search_log_writes_note_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            exit_code = main(
                [
                    "note",
                    "search-log",
                    tmpdir,
                    "--question",
                    "Adaptive clamping papers",
                    "--keyword",
                    "adaptive clamping",
                    "--keyword",
                    "fixture",
                    "--query",
                    "adaptive clamping fixture",
                    "--source",
                    "Scopus",
                    "--date",
                    "2026-05-18",
                    "--filters",
                    "2020-2026",
                    "--result-count",
                    "12",
                    "--notes",
                    "Focus on mechanism design.",
                    "--timestamp",
                    "20260518-090100",
                ]
            )

            self.assertEqual(exit_code, 0)
            root = Path(tmpdir)
            files = list(root.glob("20260518-090100-adaptive-clamping-papers*.md"))
            self.assertEqual(len(files), 1)
            content = files[0].read_text(encoding="utf-8")
            self.assertIn("Focus on mechanism design.", content)

    def test_cli_outline_writes_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            exit_code = main(
                [
                    "note",
                    "outline",
                    tmpdir,
                    "--topic",
                    "Adaptive clamping system",
                    "--problem-statement",
                    "Reduce setup deviation",
                    "--section",
                    "Introduction:Background|Gap",
                    "--section",
                    "Method:Fixture|Control",
                    "--conclusion",
                    "Conclude with practical impact.",
                    "--timestamp",
                    "20260518-090200",
                ]
            )

            self.assertEqual(exit_code, 0)
            files = list(Path(tmpdir).glob("20260518-090200-adaptive-clamping-system*.md"))
            self.assertEqual(len(files), 1)
            content = files[0].read_text(encoding="utf-8")
            self.assertIn("## Introduction", content)
            self.assertIn("- Background", content)
            self.assertIn("## Method", content)

    def test_cli_literature_review_writes_paragraph(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            exit_code = main(
                [
                    "note",
                    "literature-review",
                    tmpdir,
                    "--paper",
                    "Adaptive clamping fixture paper",
                    "--claim",
                    "The paper reduces deviation.",
                    "--evidence",
                    "Measured alignment error falls in tests.",
                    "--connection",
                    "Useful for our mechanism comparison section.",
                    "--limit",
                    "Needs more validation on heavier loads.",
                    "--timestamp",
                    "20260518-090300",
                ]
            )

            self.assertEqual(exit_code, 0)
            files = list(Path(tmpdir).glob("20260518-090300-adaptive-clamping-fixture-paper*.md"))
            self.assertEqual(len(files), 1)
            content = files[0].read_text(encoding="utf-8")
            self.assertIn("Useful for our mechanism comparison section.", content)
            self.assertIn("Needs more validation on heavier loads.", content)


if __name__ == "__main__":
    unittest.main()
