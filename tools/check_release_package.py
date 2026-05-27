from __future__ import annotations

import argparse
import zipfile
from pathlib import Path


REQUIRED_SUFFIXES = {
    "install_windows.bat",
    "start_web.bat",
    "pyproject.toml",
    "README.md",
    "README.zh-CN.md",
    "workflow/web_app.py",
    "workflow/mobile_app.py",
    "workflow/mobile_responses.py",
    "workflow/cli.py",
    "miniprogram/app.json",
    "miniprogram/project.config.json",
    "miniprogram/utils/api.ts",
    "miniprogram/pages/connect/connect.json",
    "miniprogram/pages/connect/connect.wxml",
    "miniprogram/pages/connect/connect.ts",
    "miniprogram/pages/connect/connect.wxss",
    "miniprogram/pages/dashboard/dashboard.json",
    "miniprogram/pages/dashboard/dashboard.wxml",
    "miniprogram/pages/dashboard/dashboard.ts",
    "miniprogram/pages/dashboard/dashboard.wxss",
    "miniprogram/pages/run/run.json",
    "miniprogram/pages/run/run.wxml",
    "miniprogram/pages/run/run.ts",
    "miniprogram/pages/run/run.wxss",
    "miniprogram/pages/reports/reports.json",
    "miniprogram/pages/reports/reports.wxml",
    "miniprogram/pages/reports/reports.ts",
    "miniprogram/pages/reports/reports.wxss",
    "examples/demo-project/project-check.json",
    "docs/screenshots/project-check.png",
    "tools/check_release_package.py",
    "tools/check_release_readiness.py",
    "tools/smoke_test_windows_release.py",
    "RELEASE_MANIFEST.txt",
}
FORBIDDEN_PARTS = {".git", ".venv", "__pycache__", ".pytest_cache", ".mypy_cache", "dist"}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo", ".tmp"}


def check_release_package(package_path: Path) -> list[str]:
    errors: list[str] = []
    if not package_path.exists():
        return [f"Release package not found: {package_path}"]

    with zipfile.ZipFile(package_path) as archive:
        names = archive.namelist()
        if not names:
            return ["Release package is empty"]

        top_level = {name.split("/", 1)[0] for name in names if "/" in name}
        if len(top_level) != 1:
            errors.append("Release package must contain exactly one top-level folder")

        for required in sorted(REQUIRED_SUFFIXES):
            if not any(name.endswith(f"/{required}") for name in names):
                errors.append(f"Missing required release file: {required}")

        for name in names:
            parts = set(Path(name).parts)
            if parts & FORBIDDEN_PARTS:
                errors.append(f"Forbidden local/development path in release package: {name}")
            if Path(name).suffix in FORBIDDEN_SUFFIXES:
                errors.append(f"Forbidden generated file in release package: {name}")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check a Windows release zip package.")
    parser.add_argument("package", help="Path to the release zip.")
    args = parser.parse_args(argv)

    errors = check_release_package(Path(args.package))
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("release package OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
