from __future__ import annotations

import argparse
import os
import zipfile
from pathlib import Path


PACKAGE_NAME = "research-workflow-workbench"
EXCLUDED_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache", ".mypy_cache", "dist"}
EXCLUDED_FILES = {"Research Workflow Web.bat"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".tmp"}
FIXED_ZIP_TIMESTAMP = (2026, 1, 1, 0, 0, 0)


def release_zip_name(version: str) -> str:
    return f"{PACKAGE_NAME}-{version}-windows.zip"


def read_project_version(root: Path) -> str:
    in_project_section = False
    for line in (root / "pyproject.toml").read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            in_project_section = stripped == "[project]"
            continue
        if in_project_section and stripped.startswith("version"):
            key, _, value = stripped.partition("=")
            if key.strip() == "version" and value.strip():
                return value.strip().strip('"').strip("'")
    raise ValueError("Could not read project version from pyproject.toml")


def collect_release_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for current_root, dirnames, filenames in os.walk(root):
        current_path = Path(current_root)
        dirnames[:] = sorted(name for name in dirnames if name not in EXCLUDED_DIRS)
        for filename in sorted(filenames):
            path = current_path / filename
            relative_path = path.relative_to(root)
            if filename in EXCLUDED_FILES:
                continue
            if path.suffix in EXCLUDED_SUFFIXES:
                continue
            if any(part in EXCLUDED_DIRS for part in relative_path.parts):
                continue
            files.append(relative_path)
    return sorted(files, key=lambda path: path.as_posix())


def build_manifest(version: str, files: list[Path]) -> str:
    lines = [
        f"Package: {PACKAGE_NAME}",
        f"Version: {version}",
        "Target: Windows local zip release",
        "",
        "Install:",
        "1. Extract this zip.",
        "2. Double-click install_windows.bat.",
        "3. Double-click Research Workflow Web.bat after installation.",
        "",
        "Files:",
    ]
    lines.extend(f"- {path.as_posix()}" for path in files)
    return "\n".join(lines) + "\n"


def _write_file_to_zip(archive: zipfile.ZipFile, source: Path, arcname: str) -> None:
    info = zipfile.ZipInfo(arcname, FIXED_ZIP_TIMESTAMP)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    archive.writestr(info, source.read_bytes())


def build_release_package(root: Path, output_dir: Path | None = None, version: str | None = None) -> Path:
    root = root.resolve()
    output_dir = (output_dir or root / "dist").resolve()
    version = version or read_project_version(root)
    files = collect_release_files(root)
    package_path = output_dir / release_zip_name(version)
    package_root = f"{PACKAGE_NAME}-{version}"

    output_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(package_path, "w") as archive:
        for relative_path in files:
            _write_file_to_zip(
                archive,
                root / relative_path,
                f"{package_root}/{relative_path.as_posix()}",
            )
        manifest_info = zipfile.ZipInfo(f"{package_root}/RELEASE_MANIFEST.txt", FIXED_ZIP_TIMESTAMP)
        manifest_info.compress_type = zipfile.ZIP_DEFLATED
        manifest_info.external_attr = 0o644 << 16
        archive.writestr(manifest_info, build_manifest(version, files))

    return package_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the Windows release zip package.")
    parser.add_argument("--root", default=".", help="Project root to package.")
    parser.add_argument("--out", default="dist", help="Output directory for the release zip.")
    parser.add_argument("--version", default=None, help="Override the version from pyproject.toml.")
    args = parser.parse_args(argv)

    package_path = build_release_package(Path(args.root), output_dir=Path(args.out), version=args.version)
    print(package_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
