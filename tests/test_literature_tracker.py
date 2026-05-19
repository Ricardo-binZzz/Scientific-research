import tempfile
import unittest
from pathlib import Path

from workflow.bootstrap import bootstrap_workspace
from workflow.cli import main
from workflow.literature_tracker import build_literature_tracker, render_literature_tracker


class LiteratureTrackerTests(unittest.TestCase):
    def test_bootstrap_workspace_creates_literature_tracking_template(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project = bootstrap_workspace(Path(tmpdir), project_slug="demo", project_name="Demo")

            self.assertTrue((project / "literature-tracker.json").exists())

    def test_build_literature_tracker_reads_topics(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / "literature-tracker.json").write_text(
                '{\n'
                '  "topics": [\n'
                '    {"name": "Adaptive fixtures", "keywords": ["adaptive fixture", "clamping"], "sources": ["Google Scholar"], "last_checked": "2026-05-01"}\n'
                "  ]\n"
                "}\n",
                encoding="utf-8",
            )

            tracker = build_literature_tracker(project)

        self.assertEqual(len(tracker.topics), 1)
        self.assertEqual(tracker.topics[0].name, "Adaptive fixtures")
        self.assertEqual(tracker.topics[0].keywords, ["adaptive fixture", "clamping"])
        self.assertEqual(tracker.topics[0].search_query, '"adaptive fixture" OR clamping')

    def test_render_literature_tracker_outputs_next_searches(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / "literature-tracker.json").write_text(
                '{\n'
                '  "topics": [\n'
                '    {"name": "Adaptive fixtures", "keywords": ["adaptive fixture", "clamping"], "sources": ["Google Scholar"], "last_checked": "2026-05-01"}\n'
                "  ]\n"
                "}\n",
                encoding="utf-8",
            )

            text = render_literature_tracker(build_literature_tracker(project))

        self.assertIn("# Literature Tracking Plan", text)
        self.assertIn("## Adaptive fixtures", text)
        self.assertIn('- Query: "adaptive fixture" OR clamping', text)
        self.assertIn("- Sources: Google Scholar", text)
        self.assertIn("- Last checked: 2026-05-01", text)

    def test_cli_project_literature_tracker_writes_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project = bootstrap_workspace(Path(tmpdir), project_slug="demo", project_name="Demo")
            out_path = project / "literature-tracking-plan.md"

            exit_code = main(["project", "literature-tracker", str(project), "--out", str(out_path)])

            self.assertEqual(exit_code, 0)
            self.assertTrue(out_path.exists())
            self.assertIn("# Literature Tracking Plan", out_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
