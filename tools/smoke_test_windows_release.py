from __future__ import annotations

import argparse
import os
import queue
import shutil
import subprocess
import sys
import threading
import time
import urllib.request
import zipfile
from pathlib import Path


def extract_release(package_path: Path, work_dir: Path) -> Path:
    if work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True)

    with zipfile.ZipFile(package_path) as archive:
        archive.extractall(work_dir)

    roots = [path for path in work_dir.iterdir() if path.is_dir()]
    if len(roots) != 1:
        raise RuntimeError(f"Expected one extracted release root, found {len(roots)}")
    return roots[0]


def run_command(command: list[str], cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed in {cwd}: {' '.join(command)}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return result


def run_installer(release_root: Path) -> None:
    env = os.environ.copy()
    env["RW_NO_PAUSE"] = "1"
    env["RW_BOOTSTRAP_PY"] = sys.executable
    result = run_command(["cmd", "/c", "install_windows.bat"], cwd=release_root, env=env)
    if "Skipping pause because RW_NO_PAUSE=1" not in result.stdout:
        raise RuntimeError("Installer did not run in noninteractive smoke-test mode")


def run_web_smoke(release_root: Path, python_path: Path) -> None:
    lines: queue.Queue[str] = queue.Queue()
    process = subprocess.Popen(
        [
            str(python_path),
            "-m",
            "workflow.web_app",
            "--host",
            "127.0.0.1",
            "--port",
            "8765",
            "--project-root",
            str(release_root / "examples" / "demo-project"),
        ],
        cwd=release_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if process.stdout:
        threading.Thread(target=_read_process_lines, args=(process.stdout, lines), daemon=True).start()
    try:
        url = _wait_for_startup_url(process, lines)
        deadline = time.monotonic() + 20
        last_error: Exception | None = None
        while time.monotonic() < deadline:
            if process.poll() is not None:
                stderr = process.stderr.read() if process.stderr else ""
                raise RuntimeError(f"Web app exited before startup.\nstderr:\n{stderr}")
            try:
                with urllib.request.urlopen(url, timeout=2) as response:
                    body = response.read().decode("utf-8")
                if response.status == 200 and "<!doctype html>" in body and "projectRoot" in body:
                    return
            except Exception as exc:
                last_error = exc
            time.sleep(0.2)
        raise RuntimeError(f"Timed out waiting for web app home page: {last_error}")
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)


def _read_process_lines(stream, lines: queue.Queue[str]) -> None:
    for line in stream:
        lines.put(line)


def _wait_for_startup_url(process: subprocess.Popen[str], lines: queue.Queue[str]) -> str:
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        if process.poll() is not None:
            stderr = process.stderr.read() if process.stderr else ""
            raise RuntimeError(f"Web app exited before printing startup URL.\nstderr:\n{stderr}")
        try:
            line = lines.get(timeout=0.2)
        except queue.Empty:
            continue
        if line.startswith("Open http://"):
            return line.removeprefix("Open ").strip()
    raise RuntimeError("Timed out waiting for web app startup URL")


def run_demo_project_check(release_root: Path, python_path: Path) -> None:
    result = run_command(
        [
            str(python_path),
            "-m",
            "workflow.cli",
            "project",
            "check",
            str(release_root / "examples" / "demo-project"),
        ],
        cwd=release_root,
    )
    required_lines = [
        "Missing PDFs: None",
        "Missing notes: None",
        "## Manuscript",
        "No immediate fixes needed",
    ]
    missing = [line for line in required_lines if line not in result.stdout]
    if missing:
        raise RuntimeError(f"Demo project check output missed expected lines: {missing}\n{result.stdout}")


def smoke_test_release(package_path: Path, work_dir: Path) -> Path:
    package_path = package_path.resolve()
    work_dir = work_dir.resolve()
    release_root = extract_release(package_path, work_dir)
    run_installer(release_root)

    python_path = release_root / ".venv" / "Scripts" / "python.exe"
    launcher = release_root / "Research Workflow Web.bat"
    if not python_path.exists():
        raise RuntimeError(f"Installer did not create expected Python: {python_path}")
    if not launcher.exists():
        raise RuntimeError(f"Installer did not create expected launcher: {launcher}")

    run_web_smoke(release_root, python_path)
    run_demo_project_check(release_root, python_path)
    return release_root


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run an end-to-end smoke test for a Windows release zip.")
    parser.add_argument("package", help="Path to the release zip.")
    parser.add_argument("--work-dir", default="dist/release-smoke", help="Temporary extraction directory.")
    args = parser.parse_args(argv)

    release_root = smoke_test_release(Path(args.package), Path(args.work_dir))
    print(f"release smoke OK: {release_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
