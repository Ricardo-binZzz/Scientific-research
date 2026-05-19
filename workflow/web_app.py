from __future__ import annotations

import argparse
import html
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

from workflow.library import (
    LibraryEntry,
    add_entry,
    inspect_library_stats,
    inspect_note_inventory,
    inspect_pdf_inventory,
    load_index,
    render_library_stats,
    render_note_inventory_report,
    render_pdf_inventory_report,
    render_search_results,
    search_library,
)
from workflow.project_report import build_project_check, build_project_report, render_project_check, render_project_report
from workflow.python.sim_result_loader import load_tabular_result
from workflow.simulation import (
    inspect_dataset,
    render_dataset_inspection,
    render_dataset_summary,
    render_dataset_validation_report,
    summarize_dataset,
    validate_dataset_columns,
)
from workflow.writing_pack import build_writing_pack, render_writing_pack


ContentResponse = tuple[int, str, str]


def render_home_page(default_project_root: str = "") -> str:
    escaped_root = html.escape(default_project_root, quote=True)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>科研工作流控制台</title>
  <style>
    :root {{
      color-scheme: light;
      font-family: "Microsoft YaHei", "Segoe UI", Arial, sans-serif;
      background: #f4f5f7;
      color: #1f2933;
    }}
    body {{ margin: 0; }}
    header {{
      background: #1f4f5f;
      color: white;
      padding: 22px 28px;
    }}
    main {{
      display: grid;
      grid-template-columns: minmax(280px, 380px) minmax(360px, 1fr);
      gap: 18px;
      padding: 18px;
    }}
    section {{
      background: white;
      border: 1px solid #d9dee5;
      border-radius: 8px;
      padding: 16px;
    }}
    h1 {{ margin: 0; font-size: 26px; }}
    h2 {{ margin: 0 0 12px; font-size: 18px; }}
    label {{ display: block; font-size: 13px; font-weight: 600; margin-top: 10px; }}
    input, textarea {{
      box-sizing: border-box;
      width: 100%;
      margin-top: 5px;
      padding: 9px 10px;
      border: 1px solid #c8d0d9;
      border-radius: 6px;
      font: inherit;
    }}
    textarea {{ min-height: 68px; resize: vertical; }}
    button {{
      border: 0;
      border-radius: 6px;
      background: #236477;
      color: white;
      cursor: pointer;
      font: inherit;
      font-weight: 600;
      margin: 8px 6px 0 0;
      padding: 9px 12px;
    }}
    button.secondary {{ background: #52616d; }}
    pre {{
      background: #111827;
      border-radius: 8px;
      color: #e5e7eb;
      min-height: 420px;
      overflow: auto;
      padding: 14px;
      white-space: pre-wrap;
    }}
    .hint {{ color: #5d6875; font-size: 13px; line-height: 1.6; }}
    @media (max-width: 860px) {{
      main {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>科研工作流控制台</h1>
    <div class="hint" style="color:#dce8ec">填写课题目录后，点击按钮运行常用检查。结果会显示在右侧。</div>
  </header>
  <main>
    <section>
      <h2>课题目录</h2>
      <label for="projectRoot">项目根目录</label>
      <input id="projectRoot" value="{escaped_root}" placeholder="例如 C:\\Users\\22676\\Documents\\fixture-study">
      <div>
        <button data-action="project_check">项目体检</button>
        <button data-action="project_report" class="secondary">项目状态</button>
        <button data-action="writing_pack" class="secondary">生成写作素材包</button>
      </div>

      <h2 style="margin-top:20px">文献库</h2>
      <label for="libraryQuery">搜索关键词</label>
      <input id="libraryQuery" placeholder="题名、作者、期刊或 DOI">
      <div>
        <button data-action="library_search">搜索文献</button>
        <button data-action="library_stats" class="secondary">文献库统计</button>
        <button data-action="library_check_pdfs" class="secondary">检查缺 PDF</button>
        <button data-action="library_check_notes" class="secondary">检查缺笔记</button>
      </div>

      <h2 style="margin-top:20px">添加文献</h2>
      <label for="title">题名</label>
      <input id="title">
      <label for="authors">作者，多个作者用分号隔开</label>
      <input id="authors">
      <label for="year">年份</label>
      <input id="year">
      <label for="source">来源期刊或会议</label>
      <input id="source">
      <label for="doi">DOI</label>
      <input id="doi">
      <label for="pdfName">PDF 文件名</label>
      <input id="pdfName">
      <label for="notePath">笔记路径</label>
      <input id="notePath" placeholder="notes/summary.md">
      <button data-action="library_add">添加到文献库</button>

      <h2 style="margin-top:20px">仿真数据</h2>
      <label for="dataPath">CSV/JSON 数据文件路径</label>
      <input id="dataPath" placeholder="例如 C:\\Users\\22676\\Documents\\fixture-study\\simulation\\result.csv">
      <label for="requiredColumns">必须存在的列，多个用逗号隔开</label>
      <input id="requiredColumns" placeholder="time,stress">
      <label for="numericColumns">必须是数字的列，多个用逗号隔开</label>
      <input id="numericColumns" placeholder="time,stress">
      <div>
        <button data-action="simulation_inspect">预览数据</button>
        <button data-action="simulation_summarize" class="secondary">汇总数值范围</button>
        <button data-action="simulation_validate" class="secondary">校验数据</button>
      </div>
    </section>
    <section>
      <h2>运行结果</h2>
      <pre id="output">网页已打开。先填写项目根目录，然后点击左侧按钮。</pre>
    </section>
  </main>
  <script>
    async function runAction(action) {{
      const payload = {{
        action,
        project_root: document.getElementById("projectRoot").value,
        query: document.getElementById("libraryQuery").value,
        title: document.getElementById("title").value,
        authors: document.getElementById("authors").value,
        year: document.getElementById("year").value,
        source: document.getElementById("source").value,
        doi: document.getElementById("doi").value,
        pdf_name: document.getElementById("pdfName").value,
        note_path: document.getElementById("notePath").value,
        data_path: document.getElementById("dataPath").value,
        required_columns: document.getElementById("requiredColumns").value,
        numeric_columns: document.getElementById("numericColumns").value
      }};
      const output = document.getElementById("output");
      output.textContent = "运行中...";
      try {{
        const response = await fetch("/action", {{
          method: "POST",
          headers: {{ "Content-Type": "application/json" }},
          body: JSON.stringify(payload)
        }});
        output.textContent = await response.text();
      }} catch (error) {{
        output.textContent = "请求失败：" + error;
      }}
    }}
    document.querySelectorAll("button[data-action]").forEach((button) => {{
      button.addEventListener("click", () => runAction(button.dataset.action));
    }});
  </script>
</body>
</html>"""


def handle_web_action(payload: dict[str, str]) -> ContentResponse:
    action = payload.get("action", "")
    project_root = Path(payload.get("project_root", "").strip())
    if action != "library_add" and not str(project_root):
        return 400, "text/plain; charset=utf-8", "请先填写项目根目录。"

    try:
        if action == "project_check":
            return _text(render_project_check(build_project_check(project_root)))
        if action == "project_report":
            return _text(render_project_report(build_project_report(project_root)))
        if action == "writing_pack":
            return _text(render_writing_pack(build_writing_pack(project_root)))

        literature_root = project_root / "literature"
        if action == "library_stats":
            index = load_index(literature_root)
            return _text(render_library_stats(inspect_library_stats(literature_root, index)))
        if action == "library_search":
            index = load_index(literature_root)
            return _text(render_search_results(search_library(index, payload.get("query", ""))))
        if action == "library_check_pdfs":
            return _text(render_pdf_inventory_report(inspect_pdf_inventory(literature_root, load_index(literature_root))))
        if action == "library_check_notes":
            return _text(render_note_inventory_report(inspect_note_inventory(literature_root, load_index(literature_root))))
        if action == "library_add":
            return _add_library_entry(project_root, payload)
        if action == "simulation_inspect":
            dataset = load_tabular_result(Path(payload.get("data_path", "").strip()))
            return _text(render_dataset_inspection(inspect_dataset(dataset)))
        if action == "simulation_summarize":
            dataset = load_tabular_result(Path(payload.get("data_path", "").strip()))
            return _text(render_dataset_summary(summarize_dataset(dataset)))
        if action == "simulation_validate":
            dataset = load_tabular_result(Path(payload.get("data_path", "").strip()))
            return _text(
                render_dataset_validation_report(
                    validate_dataset_columns(
                        dataset,
                        required_columns=_split_csv_input(payload.get("required_columns", "")),
                        numeric_columns=_split_csv_input(payload.get("numeric_columns", "")),
                    )
                )
            )
    except Exception as exc:
        return 500, "text/plain; charset=utf-8", f"运行失败：{exc}"

    return 400, "text/plain; charset=utf-8", f"不支持的操作：{action}"


def run_server(host: str = "127.0.0.1", port: int = 8000, default_project_root: str = "") -> None:
    handler = _make_handler(default_project_root)
    server = ThreadingHTTPServer((host, port), handler)
    print(f"Open http://{host}:{port}")
    server.serve_forever()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="research-workflow-web")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8000, type=int)
    parser.add_argument("--project-root", default="")
    args = parser.parse_args(argv)
    run_server(host=args.host, port=args.port, default_project_root=args.project_root)
    return 0


def _add_library_entry(project_root: Path, payload: dict[str, str]) -> ContentResponse:
    year_text = payload.get("year", "").strip()
    year = int(year_text) if year_text else 0
    authors = [item.strip() for item in payload.get("authors", "").split(";") if item.strip()]
    literature_root = project_root / "literature"
    index = load_index(literature_root)
    updated = add_entry(
        literature_root,
        index,
        LibraryEntry(
            title=payload.get("title", "").strip(),
            authors=authors,
            year=year,
            source=payload.get("source", "").strip(),
            doi=payload.get("doi", "").strip(),
            pdf_name=payload.get("pdf_name", "").strip(),
            note_path=payload.get("note_path", "").strip(),
        ),
    )
    return _text(f"已添加。当前文献库共有 {len(updated.entries)} 条。")


def _make_handler(default_project_root: str):
    class WorkflowRequestHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
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

    return WorkflowRequestHandler


def _text(body: str) -> ContentResponse:
    return 200, "text/plain; charset=utf-8", body


def _split_csv_input(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


if __name__ == "__main__":
    raise SystemExit(main())
