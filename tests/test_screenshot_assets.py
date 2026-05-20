import unittest
from pathlib import Path


class ScreenshotAssetTests(unittest.TestCase):
    def test_real_web_screenshots_are_documented_and_reproducible(self) -> None:
        script = Path("tools") / "capture_web_screenshots.js"
        screenshots_dir = Path("docs") / "screenshots"
        readme = Path("README.md").read_text(encoding="utf-8")
        readme_zh = Path("README.zh-CN.md").read_text(encoding="utf-8")
        screenshot_readme = (screenshots_dir / "README.md").read_text(encoding="utf-8")

        self.assertTrue(script.exists())
        script_text = script.read_text(encoding="utf-8")
        self.assertIn("workflow.web_app", script_text)
        self.assertIn("playwright", script_text)
        self.assertIn("redactDemoPath", script_text)
        self.assertIn("workflow-status.png", script_text)
        self.assertIn("project-check.png", script_text)

        for name in ("web-workbench-home.png", "workflow-status.png", "project-check.png"):
            path = screenshots_dir / name
            self.assertTrue(path.exists(), name)
            self.assertGreater(path.stat().st_size, 10_000, name)
            self.assertIn(name, readme)
            self.assertIn(name, readme_zh)
            self.assertIn(name, screenshot_readme)


if __name__ == "__main__":
    unittest.main()
