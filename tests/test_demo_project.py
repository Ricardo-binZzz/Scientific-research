import unittest
from pathlib import Path

from workflow.library import load_index, search_library
from workflow.manuscript import inspect_manuscript
from workflow.project_report import build_project_check
from workflow.python.sim_result_loader import load_tabular_result
from workflow.simulation import summarize_dataset


class DemoProjectTests(unittest.TestCase):
    def test_demo_project_contains_runnable_assets(self) -> None:
        project = Path("examples/demo-project")

        self.assertTrue((project / "literature" / "library-index.json").exists())
        self.assertTrue((project / "notes" / "paper-summary-adaptive-clamping-fixture.md").exists())
        self.assertTrue((project / "simulation" / "fixture-stress.csv").exists())
        self.assertTrue((project / "manuscript" / "chapter.md").exists())
        self.assertTrue((project / "project-check.json").exists())
        self.assertTrue((project / "literature-tracker.json").exists())

    def test_demo_project_runs_through_core_reports(self) -> None:
        project = Path("examples/demo-project")
        index = load_index(project / "literature")
        dataset = load_tabular_result(project / "simulation" / "fixture-stress.csv")
        manuscript = inspect_manuscript(
            project / "manuscript" / "chapter.md",
            required_sections=["Introduction", "Method", "Results"],
            expected_figures=["Figure 1"],
            library_index=index,
        )
        check = build_project_check(project)

        self.assertEqual(len(index.entries), 2)
        self.assertEqual(len(search_library(index, "fixture")), 2)
        self.assertIn("stress", summarize_dataset(dataset).numeric_columns)
        self.assertEqual(manuscript.missing_sections, [])
        self.assertGreaterEqual(check.summary.library_entries, 2)
        self.assertEqual(check.missing_pdf_names, [])
        self.assertEqual(check.missing_note_paths, [])
        self.assertEqual(check.manuscript_issues, [])


if __name__ == "__main__":
    unittest.main()
