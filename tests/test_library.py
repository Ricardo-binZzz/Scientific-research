import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from workflow.cli import main
from workflow.library import (
    LibraryEntry,
    LibraryIndex,
    add_entry,
    export_bibtex,
    import_csv_metadata,
    import_bibtex,
    inspect_pdf_inventory,
    inspect_library_stats,
    load_index,
    make_citekey,
    render_index,
    render_library_stats,
)


class LibraryTests(unittest.TestCase):
    def test_add_entry_deduplicates_by_doi(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            index = LibraryIndex(entries=[])

            first = LibraryEntry(
                title="Adaptive clamping fixture",
                authors=["Zhang", "Li"],
                year=2024,
                source="Journal of Manufacturing Systems",
                doi="10.1000/example",
                pdf_name="2024-zhang-adaptive-clamping.pdf",
                note_path="notes/20240518-summary.md",
            )
            second = LibraryEntry(
                title="Adaptive clamping fixture",
                authors=["Zhang", "Li"],
                year=2024,
                source="Journal of Manufacturing Systems",
                doi="10.1000/example",
                pdf_name="2024-zhang-adaptive-clamping-v2.pdf",
                note_path="notes/20240518-summary-v2.md",
            )

            add_entry(root, index, first)
            add_entry(root, index, second)

            loaded = load_index(root)

        self.assertEqual(len(loaded.entries), 1)
        self.assertEqual(loaded.entries[0].pdf_name, "2024-zhang-adaptive-clamping.pdf")

    def test_render_index_lists_entries(self) -> None:
        index = LibraryIndex(
            entries=[
                LibraryEntry(
                    title="Adaptive clamping fixture",
                    authors=["Zhang", "Li"],
                    year=2024,
                    source="Journal of Manufacturing Systems",
                    doi="10.1000/example",
                    pdf_name="2024-zhang-adaptive-clamping.pdf",
                    note_path="notes/20240518-summary.md",
                )
            ]
        )

        text = render_index(index)

        self.assertIn("# Literature Library", text)
        self.assertIn("Adaptive clamping fixture", text)
        self.assertIn("10.1000/example", text)

    def test_make_citekey_uses_first_author_year_and_title_word(self) -> None:
        entry = LibraryEntry(
            title="Adaptive clamping fixture",
            authors=["Zhang", "Li"],
            year=2024,
            source="Journal of Manufacturing Systems",
            doi="10.1000/example",
            pdf_name="2024-zhang-adaptive-clamping.pdf",
            note_path="notes/20240518-summary.md",
        )

        self.assertEqual(make_citekey(entry), "zhang2024adaptive")

    def test_export_bibtex_writes_article_entries(self) -> None:
        index = LibraryIndex(
            entries=[
                LibraryEntry(
                    title="Adaptive clamping fixture",
                    authors=["Zhang", "Li"],
                    year=2024,
                    source="Journal of Manufacturing Systems",
                    doi="10.1000/example",
                    pdf_name="2024-zhang-adaptive-clamping.pdf",
                    note_path="notes/20240518-summary.md",
                )
            ]
        )

        text = export_bibtex(index)

        self.assertIn("@article{zhang2024adaptive", text)
        self.assertIn("author = {Zhang and Li}", text)
        self.assertIn("journal = {Journal of Manufacturing Systems}", text)
        self.assertIn("doi = {10.1000/example}", text)

    def test_import_bibtex_reads_article_entries(self) -> None:
        text = (
            "@article{zhang2024adaptive,\n"
            "  title = {Adaptive clamping fixture},\n"
            "  author = {Zhang and Li},\n"
            "  journal = {Journal of Manufacturing Systems},\n"
            "  year = {2024},\n"
            "  doi = {10.1000/example},\n"
            "  file = {paper.pdf},\n"
            "  note = {notes/summary.md}\n"
            "}\n"
        )

        index = import_bibtex(text)

        self.assertEqual(len(index.entries), 1)
        self.assertEqual(index.entries[0].title, "Adaptive clamping fixture")
        self.assertEqual(index.entries[0].authors, ["Zhang", "Li"])
        self.assertEqual(index.entries[0].source, "Journal of Manufacturing Systems")

    def test_import_csv_metadata_reads_common_export_columns(self) -> None:
        text = (
            "Title,Authors,Year,Source title,DOI,PDF,Notes\n"
            '"Adaptive clamping fixture","Zhang; Li",2024,Journal of Manufacturing Systems,10.1000/example,paper.pdf,notes/summary.md\n'
        )

        index = import_csv_metadata(text)

        self.assertEqual(len(index.entries), 1)
        self.assertEqual(index.entries[0].title, "Adaptive clamping fixture")
        self.assertEqual(index.entries[0].authors, ["Zhang", "Li"])
        self.assertEqual(index.entries[0].year, 2024)
        self.assertEqual(index.entries[0].source, "Journal of Manufacturing Systems")
        self.assertEqual(index.entries[0].doi, "10.1000/example")
        self.assertEqual(index.entries[0].pdf_name, "paper.pdf")
        self.assertEqual(index.entries[0].note_path, "notes/summary.md")

    def test_import_csv_metadata_reads_scopus_full_name_export_columns(self) -> None:
        text = (
            "Title,Author full names,Year,Source title,DOI,Link,Abstract,Author Keywords\n"
            '"Adaptive fixture design","Zhang, Wei; Li, Ming",2024,Journal of Manufacturing Systems,10.1000/scopus,https://example.com,"Abstract text","fixture; clamping"\n'
        )

        index = import_csv_metadata(text)

        self.assertEqual(len(index.entries), 1)
        self.assertEqual(index.entries[0].title, "Adaptive fixture design")
        self.assertEqual(index.entries[0].authors, ["Zhang, Wei", "Li, Ming"])
        self.assertEqual(index.entries[0].year, 2024)
        self.assertEqual(index.entries[0].source, "Journal of Manufacturing Systems")
        self.assertEqual(index.entries[0].doi, "10.1000/scopus")
        self.assertEqual(index.entries[0].pdf_name, "")
        self.assertEqual(index.entries[0].note_path, "")

    def test_import_csv_metadata_reads_web_of_science_publication_name_columns(self) -> None:
        text = (
            "Article Title,Authors,Publication Year,Publication Name,DOI,Web of Science Categories\n"
            '"Fixture stiffness optimization","Chen, Q.; Wang, Y.",2023,International Journal of Advanced Manufacturing Technology,10.1000/wos,Engineering\n'
        )

        index = import_csv_metadata(text)

        self.assertEqual(len(index.entries), 1)
        self.assertEqual(index.entries[0].title, "Fixture stiffness optimization")
        self.assertEqual(index.entries[0].authors, ["Chen, Q.", "Wang, Y."])
        self.assertEqual(index.entries[0].year, 2023)
        self.assertEqual(index.entries[0].source, "International Journal of Advanced Manufacturing Technology")
        self.assertEqual(index.entries[0].doi, "10.1000/wos")

    def test_inspect_pdf_inventory_reports_missing_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "paper.pdf").write_bytes(b"%PDF-1.4")
            index = LibraryIndex(
                entries=[
                    LibraryEntry(
                        title="Present paper",
                        authors=["Zhang"],
                        year=2024,
                        source="Journal",
                        doi="10.1000/present",
                        pdf_name="paper.pdf",
                        note_path="notes/present.md",
                    ),
                    LibraryEntry(
                        title="Missing paper",
                        authors=["Li"],
                        year=2023,
                        source="Journal",
                        doi="10.1000/missing",
                        pdf_name="missing.pdf",
                        note_path="notes/missing.md",
                    ),
                ]
            )

            report = inspect_pdf_inventory(root, index)

        self.assertEqual(report.present_pdf_names, ["paper.pdf"])
        self.assertEqual(report.missing_pdf_names, ["missing.pdf"])

    def test_cli_library_add_writes_index(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            pdf = root / "paper.pdf"
            pdf.write_bytes(b"%PDF-1.4")

            exit_code = main(
                [
                    "library",
                    "add",
                    tmpdir,
                    "--title",
                    "Adaptive clamping fixture",
                    "--author",
                    "Zhang",
                    "--author",
                    "Li",
                    "--year",
                    "2024",
                    "--source",
                    "Journal of Manufacturing Systems",
                    "--doi",
                    "10.1000/example",
                    "--pdf-name",
                    "paper.pdf",
                    "--note-path",
                    "notes/20240518-summary.md",
                ]
            )

            self.assertEqual(exit_code, 0)
            loaded = load_index(root)
            self.assertEqual(len(loaded.entries), 1)

    def test_cli_library_list_prints_entries(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            index = LibraryIndex(
                entries=[
                    LibraryEntry(
                        title="Adaptive clamping fixture",
                        authors=["Zhang", "Li"],
                        year=2024,
                        source="Journal of Manufacturing Systems",
                        doi="10.1000/example",
                        pdf_name="paper.pdf",
                        note_path="notes/summary.md",
                    )
                ]
            )
            index.save(root)

            output = StringIO()
            with redirect_stdout(output):
                exit_code = main(["library", "list", tmpdir])

            self.assertEqual(exit_code, 0)
            self.assertIn("Adaptive clamping fixture", output.getvalue())

    def test_cli_library_export_bibtex_writes_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            index = LibraryIndex(
                entries=[
                    LibraryEntry(
                        title="Adaptive clamping fixture",
                        authors=["Zhang", "Li"],
                        year=2024,
                        source="Journal of Manufacturing Systems",
                        doi="10.1000/example",
                        pdf_name="paper.pdf",
                        note_path="notes/summary.md",
                    )
                ]
            )
            index.save(root)
            out_path = root / "export.bib"

            exit_code = main(["library", "export-bibtex", tmpdir, str(out_path)])

            self.assertEqual(exit_code, 0)
            self.assertIn("@article{zhang2024adaptive", out_path.read_text(encoding="utf-8"))

    def test_cli_library_import_bibtex_merges_index(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            bib_path = root / "import.bib"
            bib_path.write_text(
                "@article{zhang2024adaptive,\n"
                "  title = {Adaptive clamping fixture},\n"
                "  author = {Zhang and Li},\n"
                "  journal = {Journal of Manufacturing Systems},\n"
                "  year = {2024},\n"
                "  doi = {10.1000/example},\n"
                "  file = {paper.pdf},\n"
                "  note = {notes/summary.md}\n"
                "}\n",
                encoding="utf-8",
            )

            exit_code = main(["library", "import-bibtex", tmpdir, str(bib_path)])

            self.assertEqual(exit_code, 0)
            loaded = load_index(root)
            self.assertEqual(len(loaded.entries), 1)
            self.assertEqual(loaded.entries[0].doi, "10.1000/example")

    def test_cli_library_import_csv_merges_and_deduplicates_index(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            LibraryIndex(
                entries=[
                    LibraryEntry(
                        title="Existing paper",
                        authors=["Existing"],
                        year=2022,
                        source="Journal",
                        doi="10.1000/existing",
                        pdf_name="existing.pdf",
                        note_path="notes/existing.md",
                    )
                ]
            ).save(root)
            csv_path = root / "import.csv"
            csv_path.write_text(
                "Title,Authors,Year,Journal,DOI,File,Note\n"
                "Existing paper,Existing,2022,Journal,10.1000/existing,duplicate.pdf,notes/duplicate.md\n"
                '"New paper","Chen and Wang",2025,Manufacturing Letters,10.1000/new,new.pdf,notes/new.md\n',
                encoding="utf-8",
            )

            exit_code = main(["library", "import-csv", tmpdir, str(csv_path)])

            self.assertEqual(exit_code, 0)
            loaded = load_index(root)
            self.assertEqual(len(loaded.entries), 2)
            self.assertEqual(loaded.entries[0].pdf_name, "existing.pdf")
            self.assertEqual(loaded.entries[1].title, "New paper")
            self.assertEqual(loaded.entries[1].authors, ["Chen", "Wang"])

    def test_cli_library_check_pdfs_prints_missing_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            LibraryIndex(
                entries=[
                    LibraryEntry(
                        title="Missing paper",
                        authors=["Li"],
                        year=2023,
                        source="Journal",
                        doi="10.1000/missing",
                        pdf_name="missing.pdf",
                        note_path="notes/missing.md",
                    )
                ]
            ).save(root)
            output = StringIO()

            with redirect_stdout(output):
                exit_code = main(["library", "check-pdfs", tmpdir])

        self.assertEqual(exit_code, 0)
        self.assertIn("missing.pdf", output.getvalue())

    def test_inspect_library_stats_counts_years_sources_and_missing_pdfs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "present.pdf").write_bytes(b"%PDF-1.4")
            index = LibraryIndex(
                entries=[
                    LibraryEntry(
                        title="Paper A",
                        authors=["Zhang"],
                        year=2022,
                        source="Journal A",
                        doi="10.1000/a",
                        pdf_name="present.pdf",
                        note_path="notes/a.md",
                    ),
                    LibraryEntry(
                        title="Paper B",
                        authors=["Li"],
                        year=2024,
                        source="Journal A",
                        doi="10.1000/b",
                        pdf_name="missing.pdf",
                        note_path="notes/b.md",
                    ),
                    LibraryEntry(
                        title="Paper C",
                        authors=["Wang"],
                        year=2023,
                        source="Journal B",
                        doi="10.1000/c",
                        pdf_name="",
                        note_path="notes/c.md",
                    ),
                ]
            )

            stats = inspect_library_stats(root, index)
            text = render_library_stats(stats)

        self.assertEqual(stats.total_entries, 3)
        self.assertEqual(stats.year_min, 2022)
        self.assertEqual(stats.year_max, 2024)
        self.assertEqual(stats.missing_pdf_count, 2)
        self.assertEqual(stats.source_counts["Journal A"], 2)
        self.assertIn("Year range: 2022-2024", text)
        self.assertIn("Missing PDFs: 2", text)
        self.assertIn("Journal A: 2", text)

    def test_cli_library_stats_prints_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            LibraryIndex(
                entries=[
                    LibraryEntry(
                        title="Paper A",
                        authors=["Zhang"],
                        year=2024,
                        source="Journal A",
                        doi="10.1000/a",
                        pdf_name="paper.pdf",
                        note_path="notes/a.md",
                    )
                ]
            ).save(root)
            output = StringIO()

            with redirect_stdout(output):
                exit_code = main(["library", "stats", tmpdir])

        self.assertEqual(exit_code, 0)
        self.assertIn("Total entries: 1", output.getvalue())


if __name__ == "__main__":
    unittest.main()
