import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from tools.build_windows_release import build_release_package, collect_release_files, read_project_version, release_zip_name
from tools.check_release_package import REQUIRED_SUFFIXES, check_release_package
from tools.check_release_readiness import check_release_readiness


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
        self.assertIn("workflow/mobile_app.py", names)
        self.assertIn("workflow/mobile_responses.py", names)
        self.assertIn("miniprogram/app.json", names)
        self.assertIn("miniprogram/project.config.json", names)
        self.assertIn("miniprogram/utils/api.ts", names)
        self.assertIn("miniprogram/pages/connect/connect.wxml", names)
        self.assertIn("miniprogram/pages/dashboard/dashboard.ts", names)
        self.assertIn("miniprogram/pages/run/run.wxss", names)
        self.assertIn("miniprogram/pages/reports/reports.json", names)
        self.assertIn("examples/demo-project/project-check.json", names)
        self.assertIn("docs/screenshots/project-check.png", names)
        self.assertIn("tools/check_release_package.py", names)
        self.assertIn("tools/smoke_test_windows_release.py", names)

        self.assertNotIn("Research Workflow Web.bat", names)
        self.assertFalse(any(name.startswith(".git/") for name in names))
        self.assertFalse(any(name.startswith(".venv/") for name in names))
        self.assertFalse(any(name.startswith("dist/") for name in names))
        self.assertFalse(any("__pycache__" in name for name in names))
        self.assertFalse(any(name.endswith(".pyc") for name in names))

    def test_release_checker_requires_mobile_companion_assets(self) -> None:
        self.assertIn("workflow/mobile_app.py", REQUIRED_SUFFIXES)
        self.assertIn("workflow/mobile_responses.py", REQUIRED_SUFFIXES)
        self.assertIn("miniprogram/app.json", REQUIRED_SUFFIXES)
        self.assertIn("miniprogram/project.config.json", REQUIRED_SUFFIXES)
        self.assertIn("tools/check_release_readiness.py", REQUIRED_SUFFIXES)
        self.assertIn("miniprogram/utils/api.ts", REQUIRED_SUFFIXES)
        for page in ("connect", "dashboard", "run", "reports"):
            for suffix in ("json", "wxml", "ts", "wxss"):
                self.assertIn(f"miniprogram/pages/{page}/{page}.{suffix}", REQUIRED_SUFFIXES)

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

    def test_windows_installer_supports_noninteractive_release_smoke(self) -> None:
        installer = Path("install_windows.bat").read_text(encoding="utf-8")

        self.assertIn("RW_NO_PAUSE", installer)
        self.assertIn("RW_BOOTSTRAP_PY", installer)
        self.assertIn("Skipping pause because RW_NO_PAUSE=1", installer)

    def test_release_smoke_script_runs_installer_and_demo_check(self) -> None:
        script = Path("tools") / "smoke_test_windows_release.py"

        self.assertTrue(script.exists())
        source = script.read_text(encoding="utf-8")
        self.assertIn("install_windows.bat", source)
        self.assertIn("RW_NO_PAUSE", source)
        self.assertIn("RW_BOOTSTRAP_PY", source)
        self.assertIn("Research Workflow Web.bat", source)
        self.assertIn("workflow.cli", source)
        self.assertIn("projectRoot", source)
        self.assertIn("project", source)
        self.assertIn("check", source)

    def test_release_readiness_accepts_valid_package_and_warns_for_stale_tag(self) -> None:
        root = Path.cwd()
        with tempfile.TemporaryDirectory() as tmpdir:
            package_path = build_release_package(root, output_dir=Path(tmpdir), version="9.9.9-test")

            checks = check_release_readiness(
                root,
                package_path=package_path,
                head_commit="new-head",
                tag_commit="old-tag",
            )

        statuses = {(check.name, check.level) for check in checks}
        self.assertIn(("release package", "ok"), statuses)
        self.assertIn(("release tag", "warn"), statuses)
        self.assertTrue(any("v0.1.0 points to old-tag" in check.message for check in checks))

    def test_release_readiness_reports_missing_package_as_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            checks = check_release_readiness(
                Path.cwd(),
                package_path=Path(tmpdir) / "missing.zip",
                head_commit="same",
                tag_commit="same",
            )

        self.assertTrue(any(check.name == "release package" and check.level == "error" for check in checks))

    def test_release_readiness_script_runs_directly(self) -> None:
        root = Path.cwd()
        with tempfile.TemporaryDirectory() as tmpdir:
            package_path = build_release_package(root, output_dir=Path(tmpdir), version="9.9.9-test")

            result = subprocess.run(
                [
                    sys.executable,
                    "tools/check_release_readiness.py",
                    "--package",
                    str(package_path),
                    "--tag",
                    "missing-test-tag",
                ],
                cwd=root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("OK: release package", result.stdout)
        self.assertIn("WARN: release tag", result.stdout)


if __name__ == "__main__":
    unittest.main()
