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
        self.assertEqual(pack.note_files, ["summary.md"])
        self.assertEqual(pack.figure_bundles, ["stress"])
        self.assertEqual(pack.simulation_exports, ["result.csv"])

    def test_render_writing_pack_contains_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            self.assertEqual(main(["init", tmpdir, "--slug", "demo", "--name", "Demo"]), 0)
            pack = build_writing_pack(Path(tmpdir) / "demo")

            text = render_writing_pack(pack)

        self.assertIn("# Writing Pack", text)
        self.assertIn("## Literature", text)
        self.assertIn("## Figures", text)

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
