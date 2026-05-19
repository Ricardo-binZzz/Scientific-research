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
    inspect_note_inventory,
    inspect_pdf_inventory,
    inspect_library_stats,
    load_index,
    make_citekey,
    render_index,
    render_library_stats,
    render_note_inventory_report,
    render_search_results,
    search_library,
    filter_library_by_year,
    filter_library_by_source,
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

    def test_inspect_note_inventory_reports_missing_notes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "literature"
            notes_dir = Path(tmpdir) / "notes"
            notes_dir.mkdir(parents=True)
            (notes_dir / "present.md").write_text("# Present", encoding="utf-8")
            index = LibraryIndex(
                entries=[
                    LibraryEntry(
                        title="Present note paper",
                        authors=["Zhang"],
                        year=2024,
                        source="Journal",
                        doi="10.1000/present-note",
                        pdf_name="present.pdf",
                        note_path="notes/present.md",
                    ),
                    LibraryEntry(
                        title="Missing note paper",
                        authors=["Li"],
                        year=2023,
                        source="Journal",
                        doi="10.1000/missing-note",
                        pdf_name="missing.pdf",
                        note_path="notes/missing.md",
                    ),
                    LibraryEntry(
                        title="Blank note paper",
                        authors=["Wang"],
                        year=2022,
                        source="Journal",
                        doi="10.1000/blank-note",
                        pdf_name="blank.pdf",
                        note_path="",
                    ),
                ]
            )

            report = inspect_note_inventory(root, index)
            text = render_note_inventory_report(report)

        self.assertEqual(report.present_note_paths, ["notes/present.md"])
        self.assertEqual(report.missing_note_paths, ["notes/missing.md", ""])
        self.assertIn("notes/present.md", text)
        self.assertIn("notes/missing.md", text)

    def test_cli_library_check_notes_prints_missing_notes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "literature"
            root.mkdir()
            LibraryIndex(
                entries=[
                    LibraryEntry(
                        title="Missing note paper",
                        authors=["Li"],
                        year=2023,
                        source="Journal",
                        doi="10.1000/missing-note",
                        pdf_name="missing.pdf",
                        note_path="notes/missing.md",
                    )
                ]
            ).save(root)
            output = StringIO()

            with redirect_stdout(output):
                exit_code = main(["library", "check-notes", str(root)])

        self.assertEqual(exit_code, 0)
        self.assertIn("notes/missing.md", output.getvalue())

    def test_inspect_library_stats_counts_years_sources_and_missing_pdfs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "present.pdf").write_bytes(b"%PDF-1.4")
            notes_dir = Path(tmpdir) / "notes"
            notes_dir.mkdir()
            (notes_dir / "a.md").write_text("# A", encoding="utf-8")
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
        self.assertEqual(stats.missing_note_count, 2)
        self.assertEqual(stats.source_counts["Journal A"], 2)
        self.assertEqual(stats.author_counts["Zhang"], 1)
        self.assertEqual(stats.author_counts["Li"], 1)
        self.assertIn("Year range: 2022-2024", text)
        self.assertIn("Missing PDFs: 2", text)
        self.assertIn("Missing notes: 2", text)
        self.assertIn("Journal A: 2", text)
        self.assertIn("## Authors", text)
        self.assertIn("Zhang: 1", text)

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
        self.assertIn("Missing notes: 1", output.getvalue())

    def test_search_library_matches_title_author_source_and_doi(self) -> None:
        index = LibraryIndex(
            entries=[
                LibraryEntry(
                    title="Adaptive clamping fixture",
                    authors=["Zhang", "Li"],
                    year=2024,
                    source="Journal of Manufacturing Systems",
                    doi="10.1000/fixture",
                    pdf_name="fixture.pdf",
                    note_path="notes/fixture.md",
                ),
                LibraryEntry(
                    title="Heat treatment simulation",
                    authors=["Wang"],
                    year=2023,
                    source="Materials Letters",
                    doi="10.1000/heat",
                    pdf_name="heat.pdf",
                    note_path="notes/heat.md",
                ),
            ]
        )

        title_matches = search_library(index, "clamping")
        author_matches = search_library(index, "wang")
        source_matches = search_library(index, "manufacturing")
        doi_matches = search_library(index, "10.1000/heat")

        self.assertEqual([entry.title for entry in title_matches], ["Adaptive clamping fixture"])
        self.assertEqual([entry.title for entry in author_matches], ["Heat treatment simulation"])
        self.assertEqual([entry.title for entry in source_matches], ["Adaptive clamping fixture"])
        self.assertEqual([entry.title for entry in doi_matches], ["Heat treatment simulation"])

    def test_filter_library_by_year_keeps_entries_since_year(self) -> None:
        index = LibraryIndex(
            entries=[
                LibraryEntry(
                    title="Older paper",
                    authors=["Zhang"],
                    year=2019,
                    source="Journal",
                    doi="10.1000/old",
                    pdf_name="old.pdf",
                    note_path="notes/old.md",
                ),
                LibraryEntry(
                    title="Recent paper",
                    authors=["Li"],
                    year=2024,
                    source="Journal",
                    doi="10.1000/recent",
                    pdf_name="recent.pdf",
                    note_path="notes/recent.md",
                ),
            ]
        )

        matches = filter_library_by_year(index, since_year=2020)

        self.assertEqual([entry.title for entry in matches], ["Recent paper"])

    def test_filter_library_by_source_matches_source_keyword(self) -> None:
        index = LibraryIndex(
            entries=[
                LibraryEntry(
                    title="Journal paper",
                    authors=["Zhang"],
                    year=2024,
                    source="Journal of Manufacturing Systems",
                    doi="10.1000/journal",
                    pdf_name="journal.pdf",
                    note_path="notes/journal.md",
                ),
                LibraryEntry(
                    title="Conference paper",
                    authors=["Li"],
                    year=2024,
                    source="CIRP Conference",
                    doi="10.1000/conference",
                    pdf_name="conference.pdf",
                    note_path="notes/conference.md",
                ),
            ]
        )

        matches = filter_library_by_source(index, "manufacturing")

        self.assertEqual([entry.title for entry in matches], ["Journal paper"])

    def test_cli_library_search_prints_matching_entries(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            LibraryIndex(
                entries=[
                    LibraryEntry(
                        title="Adaptive clamping fixture",
                        authors=["Zhang", "Li"],
                        year=2024,
                        source="Journal of Manufacturing Systems",
                        doi="10.1000/fixture",
                        pdf_name="fixture.pdf",
                        note_path="notes/fixture.md",
                    ),
                    LibraryEntry(
                        title="Heat treatment simulation",
                        authors=["Wang"],
                        year=2023,
                        source="Materials Letters",
                        doi="10.1000/heat",
                        pdf_name="heat.pdf",
                        note_path="notes/heat.md",
                    ),
                ]
            ).save(root)
            output = StringIO()

            with redirect_stdout(output):
                exit_code = main(["library", "search", tmpdir, "fixture"])

        self.assertEqual(exit_code, 0)
        text = output.getvalue()
        self.assertIn("# Library Search Results", text)
        self.assertIn("Adaptive clamping fixture", text)
        self.assertNotIn("Heat treatment simulation", text)
        self.assertIn("10.1000/fixture", text)

    def test_cli_library_recent_prints_entries_since_year(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            LibraryIndex(
                entries=[
                    LibraryEntry(
                        title="Older paper",
                        authors=["Zhang"],
                        year=2019,
                        source="Journal",
                        doi="10.1000/old",
                        pdf_name="old.pdf",
                        note_path="notes/old.md",
                    ),
                    LibraryEntry(
                        title="Recent paper",
                        authors=["Li"],
                        year=2024,
                        source="Journal",
                        doi="10.1000/recent",
                        pdf_name="recent.pdf",
                        note_path="notes/recent.md",
                    ),
                ]
            ).save(root)
            output = StringIO()

            with redirect_stdout(output):
                exit_code = main(["library", "recent", tmpdir, "--since", "2020"])

        self.assertEqual(exit_code, 0)
        self.assertIn("Recent paper", output.getvalue())
        self.assertNotIn("Older paper", output.getvalue())

    def test_cli_library_source_prints_entries_matching_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            LibraryIndex(
                entries=[
                    LibraryEntry(
                        title="Journal paper",
                        authors=["Zhang"],
                        year=2024,
                        source="Journal of Manufacturing Systems",
                        doi="10.1000/journal",
                        pdf_name="journal.pdf",
                        note_path="notes/journal.md",
                    ),
                    LibraryEntry(
                        title="Conference paper",
                        authors=["Li"],
                        year=2024,
                        source="CIRP Conference",
                        doi="10.1000/conference",
                        pdf_name="conference.pdf",
                        note_path="notes/conference.md",
                    ),
                ]
            ).save(root)
            output = StringIO()

            with redirect_stdout(output):
                exit_code = main(["library", "source", tmpdir, "manufacturing"])

        self.assertEqual(exit_code, 0)
        self.assertIn("Journal paper", output.getvalue())
        self.assertNotIn("Conference paper", output.getvalue())


if __name__ == "__main__":
    unittest.main()
