import tempfile
import unittest
from pathlib import Path

from workflow.cli import main
from workflow.library import LibraryEntry, LibraryIndex
from workflow.literature_map import build_literature_map, render_literature_map


class LiteratureMapTests(unittest.TestCase):
    def test_build_literature_map_groups_years_sources_and_authors(self) -> None:
        index = LibraryIndex(
            entries=[
                LibraryEntry(
                    title="Adaptive fixture",
                    authors=["Zhang", "Li"],
                    year=2024,
                    source="Journal A",
                    doi="10.1000/a",
                    pdf_name="a.pdf",
                    note_path="notes/a.md",
                ),
                LibraryEntry(
                    title="Fixture review",
                    authors=["Zhang"],
                    year=2020,
                    source="Journal B",
                    doi="10.1000/b",
                    pdf_name="b.pdf",
                    note_path="notes/b.md",
                ),
            ]
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            index.save(root)

            literature_map = build_literature_map(root)

        self.assertEqual(literature_map.year_counts, {2024: 1, 2020: 1})
        self.assertEqual(literature_map.source_counts, {"Journal A": 1, "Journal B": 1})
        self.assertEqual(literature_map.author_counts, {"Zhang": 2, "Li": 1})
        self.assertEqual(literature_map.author_links["Zhang"], ["Adaptive fixture", "Fixture review"])

    def test_render_literature_map_outputs_markdown(self) -> None:
        index = LibraryIndex(
            entries=[
                LibraryEntry(
                    title="Adaptive fixture",
                    authors=["Zhang"],
                    year=2024,
                    source="Journal A",
                    doi="10.1000/a",
                    pdf_name="a.pdf",
                    note_path="notes/a.md",
                )
            ]
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            index.save(root)

            text = render_literature_map(build_literature_map(root))

        self.assertIn("# Literature Map", text)
        self.assertIn("## Years", text)
        self.assertIn("- 2024: 1", text)
        self.assertIn("## Authors", text)
        self.assertIn("- Zhang: 1", text)
        self.assertIn("## Author Links", text)
        self.assertIn("- Zhang: Adaptive fixture", text)

    def test_cli_library_map_writes_file(self) -> None:
        index = LibraryIndex(
            entries=[
                LibraryEntry(
                    title="Adaptive fixture",
                    authors=["Zhang"],
                    year=2024,
                    source="Journal A",
                    doi="10.1000/a",
                    pdf_name="a.pdf",
                    note_path="notes/a.md",
                )
            ]
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            index.save(root)
            out_path = root / "literature-map.md"

            exit_code = main(["library", "map", str(root), "--out", str(out_path)])

            self.assertEqual(exit_code, 0)
            self.assertTrue(out_path.exists())
            self.assertIn("# Literature Map", out_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
