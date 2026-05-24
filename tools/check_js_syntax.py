"""Run `node --check` for repository JavaScript assets."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


DEFAULT_TARGETS = [
    "workflow/web_assets/actions.js",
    "workflow/web_assets/app.js",
    "workflow/web_assets/renderers.js",
    "tools/capture_web_screenshots.js",
]


def candidate_node_paths() -> list[Path]:
    paths: list[Path] = []
    configured = os.environ.get("NODE")
    if configured:
        paths.append(Path(configured))

    paths.append(
        Path.home()
        / ".cache"
        / "codex-runtimes"
        / "codex-primary-runtime"
        / "dependencies"
        / "node"
        / "bin"
        / "node.exe"
    )

    discovered = shutil.which("node")
    if discovered:
        paths.append(Path(discovered))

    return paths


def find_node() -> Path | None:
    for path in candidate_node_paths():
        if path.exists():
            return path
    return None


def main(argv: list[str]) -> int:
    node = find_node()
    if node is None:
        print("Cannot find Node.js. Set NODE or install node on PATH.", file=sys.stderr)
        return 2

    targets = argv or DEFAULT_TARGETS
    failed = False
    for target in targets:
        path = Path(target)
        result = subprocess.run([str(node), "--check", str(path)], text=True, capture_output=True)
        if result.returncode == 0:
            print(f"OK {path.as_posix()}")
            continue
        failed = True
        print(f"FAIL {path.as_posix()}", file=sys.stderr)
        if result.stdout:
            print(result.stdout, file=sys.stderr, end="")
        if result.stderr:
            print(result.stderr, file=sys.stderr, end="")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
