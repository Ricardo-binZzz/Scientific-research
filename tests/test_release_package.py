import tempfile
import unittest
import zipfile
from pathlib import Path

from tools.build_windows_release import build_release_package, collect_release_files, read_project_version, release_zip_name
from tools.check_release_package import check_release_package


class ReleasePackageTests(unittest.TestCase):
    def test_release_version_reader_avoids_python_311_only_tomllib_dependency(self) -> None:
        source = Path("tools") / "build_windows_release.py"
        self.assertNotIn("tomllib", source.read_text(encoding="utf-8"))

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "pyproject.toml").write_text(
                '[build-system]\nrequires = ["setuptools"]\n\n[project]\nname = "demo"\nversion = "1.2.3"\n',
                encoding="utf-8",
            )

            version = read_project_version(root)

        self.assertEqual(version, "1.2.3")

    def test_release_file_collection_includes_runtime_assets_and_excludes_local_state(self) -> None:
        root = Path.cwd()

        files = collect_release_files(root)
        names = {path.as_posix() for path in files}

        self.assertIn("install_windows.bat", names)
        self.assertIn("start_web.bat", names)
        self.assertIn("pyproject.toml", names)
        self.assertIn("workflow/web_app.py", names)
        self.assertIn("examples/demo-project/project-check.json", names)
        self.assertIn("docs/screenshots/project-check.png", names)
        self.assertIn("tools/check_release_package.py", names)

        self.assertNotIn("Research Workflow Web.bat", names)
        self.assertFalse(any(name.startswith(".git/") for name in names))
        self.assertFalse(any(name.startswith(".venv/") for name in names))
        self.assertFalse(any(name.startswith("dist/") for name in names))
        self.assertFalse(any("__pycache__" in name for name in names))
        self.assertFalse(any(name.endswith(".pyc") for name in names))

    def test_build_windows_release_zip_and_validate_manifest(self) -> None:
        root = Path.cwd()
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)

            package_path = build_release_package(root, output_dir=output_dir, version="9.9.9-test")

            self.assertEqual(package_path, output_dir / release_zip_name("9.9.9-test"))
            self.assertTrue(package_path.exists())

            errors = check_release_package(package_path)

            self.assertEqual(errors, [])
            with zipfile.ZipFile(package_path) as archive:
                names = set(archive.namelist())
                self.assertIn("research-workflow-workbench-9.9.9-test/install_windows.bat", names)
                self.assertIn("research-workflow-workbench-9.9.9-test/start_web.bat", names)
                self.assertIn("research-workflow-workbench-9.9.9-test/examples/demo-project/project-check.json", names)
                self.assertIn("research-workflow-workbench-9.9.9-test/RELEASE_MANIFEST.txt", names)
                manifest = archive.read("research-workflow-workbench-9.9.9-test/RELEASE_MANIFEST.txt").decode("utf-8")

        self.assertIn("Package: research-workflow-workbench", manifest)
        self.assertIn("Version: 9.9.9-test", manifest)
        self.assertIn("install_windows.bat", manifest)
        self.assertNotIn(".venv", manifest)


if __name__ == "__main__":
    unittest.main()
