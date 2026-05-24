import tempfile
import unittest
import zipfile
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from workflow.cli import main
from workflow.manuscript import ManuscriptIssue, inspect_manuscript, render_manuscript_report
from workflow.library import LibraryEntry, LibraryIndex


class ManuscriptTests(unittest.TestCase):
    def test_inspect_manuscript_extracts_citations_and_flags_missing_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "chapter.md"
            path.write_text(
                "# Method\n\n"
                "The fixture reduces deviation [@zhang2024].\n\n"
                "Figure 1 shows the stress response.\n",
                encoding="utf-8",
            )

            report = inspect_manuscript(path, required_sections=["Introduction", "Method"], expected_figures=["Figure 1"])

        self.assertEqual(report.citations, ["zhang2024"])
        self.assertEqual(report.figures, ["Figure 1"])
        self.assertIn("Introduction", report.missing_sections)
        self.assertEqual(report.missing_figures, [])

    def test_inspect_manuscript_extracts_multiple_citations_from_one_marker(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "chapter.md"
            path.write_text(
                "# Introduction\n\n"
                "Prior work supports this design [@zhang2024; @li2023fixture].\n",
                encoding="utf-8",
            )

            report = inspect_manuscript(path, required_sections=["Introduction"], expected_figures=[])

        self.assertEqual(report.citations, ["zhang2024", "li2023fixture"])

    def test_inspect_manuscript_handles_utf8_bom_heading(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "chapter.md"
            path.write_text(
                "\ufeff# Introduction\n\n"
                "Prior work [@zhang2024] motivates this design.\n",
                encoding="utf-8",
            )

            report = inspect_manuscript(path, required_sections=["Introduction"], expected_figures=[])

        self.assertEqual(report.missing_sections, [])

    def test_inspect_manuscript_extracts_chinese_figure_marker(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "chapter.md"
            path.write_text("# Introduction\n\n图 1 shows the fixture.\n", encoding="utf-8")

            report = inspect_manuscript(path, required_sections=["Introduction"], expected_figures=["图 1"])

        self.assertIn("图 1", report.figures)
        self.assertEqual(report.missing_figures, [])

    def test_inspect_manuscript_matches_common_chinese_section_aliases(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "chapter.md"
            path.write_text(
                "# 绪论\n\n"
                "研究背景。\n\n"
                "# 研究方法\n\n"
                "方法说明。\n\n"
                "# 结果与讨论\n\n"
                "结果说明。\n",
                encoding="utf-8",
            )

            report = inspect_manuscript(
                path,
                required_sections=["Introduction", "Method", "Results"],
                expected_figures=[],
            )

        self.assertEqual(report.missing_sections, [])

    def test_inspect_manuscript_flags_duplicate_figure_markers(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "chapter.md"
            path.write_text(
                "# Introduction\n\n"
                "Figure 1 shows the fixture.\n\n"
                "Figure 1 compares stress.\n",
                encoding="utf-8",
            )

            report = inspect_manuscript(path, required_sections=["Introduction"], expected_figures=[])

        self.assertTrue(any("Duplicate figure marker: Figure 1" in issue.message for issue in report.issues))

    def test_inspect_manuscript_flags_missing_figure_sequence_numbers(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "chapter.md"
            path.write_text(
                "# Introduction\n\n"
                "Figure 1 shows the fixture.\n\n"
                "Figure 3 compares stress.\n",
                encoding="utf-8",
            )

            report = inspect_manuscript(path, required_sections=["Introduction"], expected_figures=[])

        self.assertTrue(any("Missing figure number in sequence: Figure 2" in issue.message for issue in report.issues))

    def test_inspect_manuscript_flags_missing_chinese_figure_sequence_numbers(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "chapter.md"
            path.write_text(
                "# 绪论\n\n"
                "图 1 展示结构。\n\n"
                "图 3 对比应力。\n",
                encoding="utf-8",
            )

            report = inspect_manuscript(path, required_sections=["Introduction"], expected_figures=[])

        self.assertTrue(any("Missing figure number in sequence: 图 2" in issue.message for issue in report.issues))

    def test_inspect_manuscript_flags_skipped_markdown_heading_levels(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "chapter.md"
            path.write_text(
                "# Introduction\n\n"
                "### Results\n\n"
                "Prior work [@zhang2024fixture] supports the design.\n",
                encoding="utf-8",
            )

            report = inspect_manuscript(path, required_sections=["Introduction"], expected_figures=[])

        self.assertTrue(any("Skipped heading level: H1 to H3 at Results" in issue.message for issue in report.issues))

    def test_inspect_manuscript_flags_missing_references_section_when_cited(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "chapter.md"
            path.write_text(
                "# Introduction\n\n"
                "Prior work [@zhang2024fixture] supports the design.\n",
                encoding="utf-8",
            )

            report = inspect_manuscript(path)

        self.assertTrue(any("Citation markers found but no References section" in issue.message for issue in report.issues))

    def test_inspect_manuscript_flags_empty_markdown_headings(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "chapter.md"
            path.write_text("# Introduction\n\n##   \n\nText.\n", encoding="utf-8")

            report = inspect_manuscript(path)

        self.assertTrue(any("Empty heading: H2" in issue.message for issue in report.issues))

    def test_inspect_manuscript_flags_markdown_images_without_captions(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "chapter.md"
            path.write_text(
                "# Results\n\n"
                "![](stress.svg)\n\n"
                "The stress result is shown above.\n",
                encoding="utf-8",
            )

            report = inspect_manuscript(path)

        self.assertTrue(any("Figure image missing caption near line" in issue.message for issue in report.issues))

    def test_inspect_manuscript_accepts_markdown_image_with_nearby_caption(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "chapter.md"
            path.write_text(
                "# Results\n\n"
                "Figure 1. Stress response.\n\n"
                "![Stress response](stress.svg)\n",
                encoding="utf-8",
            )

            report = inspect_manuscript(path)

        self.assertFalse(any("Figure image missing caption near line" in issue.message for issue in report.issues))

    def test_inspect_manuscript_flags_markdown_tables_without_captions(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "chapter.md"
            path.write_text(
                "# Results\n\n"
                "| Case | Stress |\n"
                "| --- | --- |\n"
                "| A | 12 |\n",
                encoding="utf-8",
            )

            report = inspect_manuscript(path)

        self.assertTrue(any("Table missing caption near line" in issue.message for issue in report.issues))

    def test_inspect_manuscript_flags_short_references_section(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "chapter.md"
            path.write_text(
                "# Introduction\n\n"
                "Prior work [@zhang2024fixture] supports the design.\n\n"
                "# References\n\n"
                "- Zhang, 2024.\n",
                encoding="utf-8",
            )

            report = inspect_manuscript(path)

        self.assertTrue(any("References section looks too short" in issue.message for issue in report.issues))

    def test_inspect_manuscript_accepts_chinese_references_section(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "chapter.md"
            path.write_text(
                "# Introduction\n\n"
                "Prior work [@zhang2024fixture] supports the design.\n\n"
                "# 参考文献\n\n"
                "- Zhang, 2024.\n",
                encoding="utf-8",
            )

            report = inspect_manuscript(path)

        self.assertFalse(any("Citation markers found but no References section" in issue.message for issue in report.issues))

    def test_render_manuscript_report_lists_issues(self) -> None:
        issue = ManuscriptIssue(level="warning", message="Missing section: Introduction")
        text = render_manuscript_report(
            citations=["zhang2024"],
            figures=["Figure 1"],
            issues=[issue],
        )

        self.assertIn("# Manuscript Check Report", text)
        self.assertIn("zhang2024", text)
        self.assertIn("Figure 1", text)
        self.assertIn("Missing section: Introduction", text)

    def test_cli_manuscript_check_prints_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "chapter.md"
            path.write_text(
                "# Introduction\n\n"
                "Prior work [@zhang2024] motivates this design.\n\n"
                "Figure 2 compares the result.\n",
                encoding="utf-8",
            )
            output = StringIO()

            with redirect_stdout(output):
                exit_code = main(
                    [
                        "manuscript",
                        "check",
                        str(path),
                        "--required-section",
                        "Introduction",
                        "--required-section",
                        "Method",
                        "--expected-figure",
                        "Figure 2",
                    ]
                )

        self.assertEqual(exit_code, 0)
        report = output.getvalue()
        self.assertIn("zhang2024", report)
        self.assertIn("Missing section: Method", report)

    def test_inspect_manuscript_reads_docx_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "chapter.docx"
            _write_minimal_docx(
                path,
                [
                    "Introduction",
                    "Prior work [@zhang2024] motivates this design.",
                    "Figure 3 shows the fixture.",
                ],
            )

            report = inspect_manuscript(path, required_sections=["Introduction"], expected_figures=["Figure 3"])

        self.assertEqual(report.citations, ["zhang2024"])
        self.assertEqual(report.missing_sections, [])
        self.assertEqual(report.missing_figures, [])

    def test_inspect_manuscript_flags_docx_style_layout_and_reference_field_gaps(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "chapter.docx"
            _write_minimal_docx(
                path,
                [
                    "Introduction",
                    "Prior work [@zhang2024] motivates this design.",
                    "References",
                    "[1] Zhang. Adaptive fixture design.",
                ],
            )

            report = inspect_manuscript(path, required_sections=["Introduction"], expected_figures=[])

        messages = [issue.message for issue in report.issues]
        self.assertIn("DOCX styles.xml missing; cannot verify Word style definitions", messages)
        self.assertIn("DOCX page margin settings missing", messages)
        self.assertIn("No Word citation/reference fields detected", messages)
        self.assertIn("References section found but no Word bibliography field detected", messages)

    def test_inspect_manuscript_flags_docx_images_missing_alt_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "chapter.docx"
            _write_docx_with_image_docpr(path, name="Stress plot", descr="")

            report = inspect_manuscript(path, required_sections=["Introduction"], expected_figures=[])

        messages = [issue.message for issue in report.issues]
        self.assertIn("DOCX image/drawing missing alt text: Stress plot", messages)

    def test_inspect_manuscript_accepts_docx_images_with_alt_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "chapter.docx"
            _write_docx_with_image_docpr(path, name="Stress plot", descr="", title="Stress distribution under load")

            report = inspect_manuscript(path, required_sections=["Introduction"], expected_figures=[])

        messages = [issue.message for issue in report.issues]
        self.assertNotIn("DOCX image/drawing missing alt text: Stress plot", messages)

    def test_inspect_manuscript_flags_citations_missing_from_library(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "chapter.md"
            path.write_text(
                "# Introduction\n\n"
                "Prior work [@zhang2024adaptive] and [@missing2025paper] motivates this design.\n",
                encoding="utf-8",
            )
            library = LibraryIndex(
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

            report = inspect_manuscript(path, required_sections=["Introduction"], expected_figures=[], library_index=library)

        self.assertIn("missing2025paper", report.missing_citations)
        self.assertNotIn("zhang2024adaptive", report.missing_citations)

    def test_inspect_manuscript_flags_library_entries_not_cited(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "chapter.md"
            path.write_text("# Introduction\n\nPrior work [@zhang2024adaptive] motivates this design.\n", encoding="utf-8")
            library = LibraryIndex(
                entries=[
                    LibraryEntry(
                        title="Adaptive clamping fixture",
                        authors=["Zhang"],
                        year=2024,
                        source="Journal",
                        doi="10.1000/example",
                        pdf_name="paper.pdf",
                        note_path="notes/summary.md",
                    ),
                    LibraryEntry(
                        title="Unused fatigue model",
                        authors=["Wang"],
                        year=2022,
                        source="Journal",
                        doi="10.1000/unused",
                        pdf_name="unused.pdf",
                        note_path="notes/unused.md",
                    ),
                ]
            )

            report = inspect_manuscript(path, required_sections=["Introduction"], expected_figures=[], library_index=library)

        self.assertIn("wang2022unused", report.uncited_library_keys)


def _write_minimal_docx(path: Path, paragraphs: list[str]) -> None:
    body = "".join(
        f"<w:p><w:r><w:t>{text}</w:t></w:r></w:p>"
        for text in paragraphs
    )
    document_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f"<w:body>{body}</w:body>"
        "</w:document>"
    )
    with zipfile.ZipFile(path, "w") as package:
        package.writestr("[Content_Types].xml", '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
        package.writestr("word/document.xml", document_xml)


def _write_docx_with_image_docpr(path: Path, *, name: str, descr: str, title: str = "") -> None:
    document_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
        'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing">'
        "<w:body>"
        "<w:p><w:r><w:t>Introduction</w:t></w:r></w:p>"
        "<w:p><w:r><w:drawing><wp:inline>"
        f'<wp:docPr id="1" name="{name}" descr="{descr}" title="{title}"/>'
        "</wp:inline></w:drawing></w:r></w:p>"
        "</w:body>"
        "</w:document>"
    )
    with zipfile.ZipFile(path, "w") as package:
        package.writestr("[Content_Types].xml", '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
        package.writestr("word/document.xml", document_xml)


if __name__ == "__main__":
    unittest.main()
