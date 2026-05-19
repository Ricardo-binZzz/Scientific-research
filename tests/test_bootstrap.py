import tempfile
import unittest
from pathlib import Path

from workflow.bootstrap import bootstrap_workspace
from workflow.cli import main


class BootstrapTests(unittest.TestCase):
    def test_bootstrap_workspace_creates_workspace_and_copies_templates(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = bootstrap_workspace(Path(tmpdir), project_slug="demo-lab", project_name="Demo Lab")

            self.assertEqual(root.name, "demo-lab")
            for name in [
                "data",
                "exports",
                "figures",
                "literature",
                "manuscript",
                "notes",
                "simulation",
                "templates",
            ]:
                self.assertTrue((root / name).is_dir(), name)

            for name in [
                "search-log.md",
                "paper-summary.md",
                "outline.md",
                "literature-review.md",
                "figure-spec.md",
                "sim-runbook.md",
                "simulation-metadata.json",
            ]:
                self.assertTrue((root / "templates" / name).is_file(), name)

            readme = (root / "README.md").read_text(encoding="utf-8")
            self.assertIn("Demo Lab", readme)
            self.assertIn("literature", readme)
            check_config = root / "project-check.json"
            self.assertTrue(check_config.is_file())
            self.assertIn("required_sections", check_config.read_text(encoding="utf-8"))

    def test_cli_init_returns_success(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            exit_code = main(["init", tmpdir, "--slug", "cli-demo", "--name", "CLI Demo"])

        self.assertEqual(exit_code, 0)

    def test_cli_module_entrypoint_is_importable(self) -> None:
        from workflow import cli  # noqa: F401

        self.assertTrue(hasattr(cli, "main"))


if __name__ == "__main__":
    unittest.main()
