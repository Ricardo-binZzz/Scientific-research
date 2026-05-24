from __future__ import annotations

import argparse
import html
import json
import socket
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

from workflow.web_actions import handle_web_action


def render_home_page(default_project_root: str = "") -> str:
    index_path = Path(__file__).with_name("web_assets") / "index.html"
    content = index_path.read_text(encoding="utf-8")
    return (
        content.replace("__DEFAULT_PROJECT_ROOT__", html.escape(default_project_root, quote=True))
    )


def run_server(host: str = "127.0.0.1", port: int = 8000, default_project_root: str = "", open_browser: bool = False) -> None:
    handler = _make_handler(default_project_root)
    server = _create_server(host, port, handler)
    actual_port = server.server_address[1]
    url = f"http://{host}:{actual_port}"
    print(f"Open {url}", flush=True)
    if open_browser:
        webbrowser.open(url)
    server.serve_forever()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="research-workflow-web")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8000, type=int)
    parser.add_argument("--project-root", default="")
    parser.add_argument("--open-browser", action="store_true")
    args = parser.parse_args(argv)
    run_server(host=args.host, port=args.port, default_project_root=args.project_root, open_browser=args.open_browser)
    return 0


def _make_handler(default_project_root: str):
    class WorkflowRequestHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            if self.path.startswith("/assets/"):
                self._send_asset(self.path.removeprefix("/assets/"))
                return
            if self.path not in {"/", "/index.html"}:
                self._send(404, "text/plain; charset=utf-8", "Not Found")
                return
            self._send(200, "text/html; charset=utf-8", render_home_page(default_project_root))

        def do_POST(self) -> None:
            if self.path != "/action":
                self._send(404, "text/plain; charset=utf-8", "Not Found")
                return
            length = int(self.headers.get("Content-Length", "0") or "0")
            raw_body = self.rfile.read(length).decode("utf-8")
            if self.headers.get("Content-Type", "").startswith("application/json"):
                payload = json.loads(raw_body or "{}")
            else:
                payload = {key: values[0] for key, values in parse_qs(raw_body).items()}
            status, content_type, body = handle_web_action(payload)
            self._send(status, content_type, body)

        def log_message(self, format: str, *args) -> None:
            return

        def _send(self, status: int, content_type: str, body: str) -> None:
            data = body.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _send_asset(self, name: str) -> None:
            if name not in {"styles.css", "actions.js", "app.js", "renderers.js"}:
                self._send(404, "text/plain; charset=utf-8", "Not Found")
                return
            path = Path(__file__).with_name("web_assets") / name
            content_type = "text/css; charset=utf-8" if name.endswith(".css") else "application/javascript; charset=utf-8"
            text = path.read_text(encoding="utf-8")
            if name == "app.js":
                demo_project_root = Path(__file__).resolve().parent.parent / "examples" / "demo-project"
                text = text.replace("__DEMO_PROJECT_ROOT_JSON__", json.dumps(str(demo_project_root)))
            self._send(200, content_type, text)

    return WorkflowRequestHandler


def _create_server(host: str, port: int, handler) -> ThreadingHTTPServer:
    last_error: OSError | None = None
    for candidate in range(port, port + 10):
        if _port_is_listening(host, candidate):
            continue
        try:
            return ThreadingHTTPServer((host, candidate), handler)
        except OSError as exc:
            last_error = exc
    raise OSError(f"No available port from {port} to {port + 9}") from last_error


def _port_is_listening(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.settimeout(0.2)
        return probe.connect_ex((host, port)) == 0



if __name__ == "__main__":
    raise SystemExit(main())
