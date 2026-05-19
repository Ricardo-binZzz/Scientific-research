import tempfile
import unittest
from pathlib import Path

from workflow.cli import main
from workflow.writing_pack import build_writing_pack, render_writing_pack


class WritingPackTests(unittest.TestCase):
    def test_build_writing_pack_collects_project_assets(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            self.assertEqual(main(["init", tmpdir, "--slug", "demo", "--name", "Demo"]), 0)
            root = Path(tmpdir) / "demo"
            (root / "notes" / "summary.md").write_text("# Paper Summary\n\n- Main result: Stable\n", encoding="utf-8")
            (root / "figures" / "stress.svg").write_text("<svg></svg>", encoding="utf-8")
            (root / "figures" / "stress.json").write_text("{}", encoding="utf-8")
            (root / "simulation" / "result.csv").write_text("time,stress\n0,1\n", encoding="utf-8")
            (root / "manuscript" / "draft.md").write_text("# Introduction\n", encoding="utf-8")
            self.assertEqual(
                main(
                    [
                        "library",
                        "add",
                        str(root / "literature"),
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

            pack = build_writing_pack(root)

        self.assertEqual(pack.library_titles, ["Adaptive clamping fixture"])
        self.assertEqual(pack.library_total_entries, 1)
        self.assertEqual(pack.library_year_range, "2024-2024")
        self.assertEqual(pack.library_missing_pdf_count, 1)
        self.assertEqual(pack.note_files, ["summary.md"])
        self.assertEqual(pack.figure_bundles, ["stress"])
        self.assertEqual(pack.simulation_exports, ["result.csv"])
        self.assertEqual(pack.manuscript_files, ["draft.md"])

    def test_writing_pack_tracks_recent_literature(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            self.assertEqual(main(["init", tmpdir, "--slug", "demo", "--name", "Demo"]), 0)
            root = Path(tmpdir) / "demo"
            for title, year in [("Classic fixture review", "2015"), ("Recent adaptive fixture", "2024")]:
                self.assertEqual(
                    main(
                        [
                            "library",
                            "add",
                            str(root / "literature"),
                            "--title",
                            title,
                            "--author",
                            "Zhang",
                            "--year",
                            year,
                            "--source",
                            "Journal",
                            "--doi",
                            f"10.1000/{year}",
                            "--pdf-name",
                            f"{year}.pdf",
                            "--note-path",
                            f"notes/{year}.md",
                        ]
                    ),
                    0,
                )

            pack = build_writing_pack(root)
            text = render_writing_pack(pack)

        self.assertEqual(pack.recent_library_titles, ["Recent adaptive fixture"])
        self.assertIn("## Recent Literature", text)
        recent_section = text.split("## Recent Literature", 1)[1].split("## Literature", 1)[0]
        self.assertIn("Recent adaptive fixture", recent_section)
        self.assertNotIn("Classic fixture review", recent_section)

    def test_writing_pack_lists_missing_library_assets(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            self.assertEqual(main(["init", tmpdir, "--slug", "demo", "--name", "Demo"]), 0)
            root = Path(tmpdir) / "demo"
            self.assertEqual(
                main(
                    [
                        "library",
                        "add",
                        str(root / "literature"),
                        "--title",
                        "Missing assets paper",
                        "--author",
                        "Li",
                        "--year",
                        "2023",
                        "--source",
                        "Journal",
                        "--doi",
                        "10.1000/missing",
                        "--pdf-name",
                        "missing.pdf",
                        "--note-path",
                        "notes/missing.md",
                    ]
                ),
                0,
            )

            pack = build_writing_pack(root)
            text = render_writing_pack(pack)

        self.assertEqual(pack.missing_pdf_names, ["missing.pdf"])
        self.assertEqual(pack.missing_note_paths, ["notes/missing.md"])
        self.assertIn("## Library Gaps", text)
        self.assertIn("- Missing PDFs: missing.pdf", text)
        self.assertIn("- Missing notes: notes/missing.md", text)

    def test_render_writing_pack_contains_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            self.assertEqual(main(["init", tmpdir, "--slug", "demo", "--name", "Demo"]), 0)
            root = Path(tmpdir) / "demo"
            (root / "manuscript" / "draft.md").write_text("# Introduction\n", encoding="utf-8")
            pack = build_writing_pack(root)

            text = render_writing_pack(pack)

        self.assertIn("# Writing Pack", text)
        self.assertIn("## Library Overview", text)
        self.assertIn("Total entries", text)
        self.assertIn("## Literature", text)
        self.assertIn("## Figures", text)
        self.assertIn("## Manuscript Drafts", text)
        self.assertIn("draft.md", text)

    def test_cli_project_writing_pack_writes_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            self.assertEqual(main(["init", tmpdir, "--slug", "demo", "--name", "Demo"]), 0)
            root = Path(tmpdir) / "demo"
            out_path = root / "writing-pack.md"

            exit_code = main(["project", "writing-pack", str(root), "--out", str(out_path)])

            self.assertEqual(exit_code, 0)
            self.assertTrue(out_path.exists())
            self.assertIn("# Writing Pack", out_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
