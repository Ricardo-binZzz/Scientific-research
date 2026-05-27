from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.build_windows_release import read_project_version, release_zip_name
from tools.check_release_package import check_release_package


@dataclass(frozen=True)
class ReleaseReadinessCheck:
    level: str
    name: str
    message: str


def _git_commit(root: Path, ref: str) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "--verify", ref],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def check_release_readiness(
    root: Path,
    *,
    package_path: Path | None = None,
    release_tag: str = "v0.1.0",
    head_commit: str | None = None,
    tag_commit: str | None = None,
) -> list[ReleaseReadinessCheck]:
    root = root.resolve()
    version = read_project_version(root)
    package_path = package_path or root / "dist" / release_zip_name(version)
    package_errors = check_release_package(package_path)

    checks: list[ReleaseReadinessCheck] = []
    if package_errors:
        checks.append(
            ReleaseReadinessCheck(
                "error",
                "release package",
                "; ".join(package_errors),
            )
        )
    else:
        checks.append(ReleaseReadinessCheck("ok", "release package", f"Release package valid: {package_path}"))

    smoke_script = root / "tools" / "smoke_test_windows_release.py"
    if smoke_script.exists():
        checks.append(ReleaseReadinessCheck("ok", "release smoke", "Release smoke-test script is present."))
    else:
        checks.append(ReleaseReadinessCheck("error", "release smoke", "Missing tools/smoke_test_windows_release.py"))

    head_commit = head_commit if head_commit is not None else _git_commit(root, "HEAD")
    tag_commit = tag_commit if tag_commit is not None else _git_commit(root, release_tag)
    if head_commit and tag_commit:
        if head_commit == tag_commit:
            checks.append(ReleaseReadinessCheck("ok", "release tag", f"Release tag {release_tag} points to HEAD."))
        else:
            checks.append(
                ReleaseReadinessCheck(
                    "warn",
                    "release tag",
                    f"Release tag {release_tag} points to {tag_commit}, current HEAD is {head_commit}; do not move it without explicit confirmation.",
                )
            )
    elif head_commit and not tag_commit:
        checks.append(ReleaseReadinessCheck("warn", "release tag", f"Release tag {release_tag} does not exist locally."))
    else:
        checks.append(ReleaseReadinessCheck("warn", "release tag", "Could not inspect git release tag state."))

    return checks


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check whether the local Windows release package is ready to publish.")
    parser.add_argument("--root", default=".", help="Project root to inspect.")
    parser.add_argument("--package", default=None, help="Release zip path. Defaults to dist/<versioned zip>.")
    parser.add_argument("--tag", default="v0.1.0", help="Release tag to compare with HEAD.")
    args = parser.parse_args(argv)

    package_path = Path(args.package) if args.package else None
    checks = check_release_readiness(Path(args.root), package_path=package_path, release_tag=args.tag)
    for check in checks:
        print(f"{check.level.upper()}: {check.name}: {check.message}")
    return 1 if any(check.level == "error" for check in checks) else 0


if __name__ == "__main__":
    raise SystemExit(main())
