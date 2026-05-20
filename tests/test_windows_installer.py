import unittest
from pathlib import Path


class WindowsInstallerTests(unittest.TestCase):
    def test_windows_installer_and_launcher_are_documented(self) -> None:
        installer = Path("install_windows.bat")
        launcher = Path("start_web.bat")
        readme = Path("README.md").read_text(encoding="utf-8")
        readme_zh = Path("README.zh-CN.md").read_text(encoding="utf-8")
        guide = Path("USER_GUIDE.md").read_text(encoding="utf-8")

        self.assertTrue(installer.exists())
        installer_text = installer.read_text(encoding="utf-8")
        self.assertIn("python -m venv .venv", installer_text)
        self.assertIn("workflow.web_app", installer_text)
        self.assertIn("Research Workflow Web.bat", installer_text)
        self.assertIn("Desktop", installer_text)
        self.assertIn("workflow.web_app", launcher.read_text(encoding="utf-8"))

        self.assertIn("install_windows.bat", readme)
        self.assertIn("install_windows.bat", readme_zh)
        self.assertIn("install_windows.bat", guide)


if __name__ == "__main__":
    unittest.main()
