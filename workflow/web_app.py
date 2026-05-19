from __future__ import annotations

import argparse
import html
import json
import socket
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

from workflow.bootstrap import bootstrap_workspace
from workflow.library import (
    LibraryEntry,
    LibraryIndex,
    add_entry,
    filter_library_by_source,
    filter_library_by_year,
    inspect_library_stats,
    inspect_note_inventory,
    inspect_pdf_inventory,
    import_csv_metadata,
    load_index,
    render_library_stats,
    render_note_inventory_report,
    render_pdf_inventory_report,
    render_search_results,
    search_library,
)
from workflow.literature_table import build_literature_table, render_literature_table
from workflow.manuscript import inspect_manuscript, render_report_from_inspection
from workflow.notes import PaperSummary, SearchLogEntry, create_note_file, render_paper_summary, render_search_log
from workflow.project_report import build_project_check, build_project_report, render_project_check, render_project_report
from workflow.python.figure_exporter import build_spec_from_dataset, export_figure_bundle
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
      <h2>新建课题</h2>
      <label for="baseDir">保存到哪个文件夹</label>
      <input id="baseDir" placeholder="例如 C:\\Users\\22676\\Documents">
      <label for="projectSlug">课题文件夹名</label>
      <input id="projectSlug" placeholder="fixture-study">
      <label for="projectName">课题显示名称</label>
      <input id="projectName" placeholder="夹具优化研究">
      <button data-action="init_project">创建课题</button>

      <h2>课题目录</h2>
      <label for="projectRoot">项目根目录</label>
      <input id="projectRoot" value="{escaped_root}" placeholder="例如 C:\\Users\\22676\\Documents\\fixture-study">
      <div>
        <button data-action="project_check">项目体检</button>
        <button data-action="project_report" class="secondary">项目状态</button>
        <button data-action="writing_pack" class="secondary">生成写作素材包</button>
        <button data-action="literature_table" class="secondary">生成文献对比表</button>
      </div>

      <h2 style="margin-top:20px">文献库</h2>
      <label for="libraryQuery">搜索关键词</label>
      <input id="libraryQuery" placeholder="题名、作者、期刊或 DOI">
      <label for="sinceYear">只看某年之后</label>
      <input id="sinceYear" placeholder="2020">
      <label for="sourceQuery">来源关键词</label>
      <input id="sourceQuery" placeholder="Manufacturing">
      <div>
        <button data-action="library_search">搜索文献</button>
        <button data-action="library_recent" class="secondary">按年份过滤</button>
        <button data-action="library_source" class="secondary">按来源过滤</button>
        <button data-action="library_stats" class="secondary">文献库统计</button>
        <button data-action="library_check_pdfs" class="secondary">检查缺 PDF</button>
        <button data-action="library_check_notes" class="secondary">检查缺笔记</button>
      </div>
      <label for="csvPath">CSV 元数据文件路径</label>
      <input id="csvPath" placeholder="例如 C:\\Users\\22676\\Documents\\fixture-study\\papers.csv">
      <button data-action="library_import_csv">导入 CSV 文献</button>

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

      <h2 style="margin-top:20px">论文摘要卡</h2>
      <label for="summaryTitle">论文题名</label>
      <input id="summaryTitle">
      <label for="summaryAuthors">作者，多个作者用分号隔开</label>
      <input id="summaryAuthors">
      <label for="summarySource">来源</label>
      <input id="summarySource">
      <label for="summaryYear">年份</label>
      <input id="summaryYear">
      <label for="summaryDoi">DOI</label>
      <input id="summaryDoi">
      <label for="summaryProblem">研究问题</label>
      <textarea id="summaryProblem"></textarea>
      <label for="summaryMethod">方法</label>
      <textarea id="summaryMethod"></textarea>
      <label for="summaryData">数据</label>
      <textarea id="summaryData"></textarea>
      <label for="summaryKeyFigures">关键图表</label>
      <textarea id="summaryKeyFigures"></textarea>
      <label for="summaryMainResult">主要结论</label>
      <textarea id="summaryMainResult"></textarea>
      <label for="summaryLimitation">局限性</label>
      <textarea id="summaryLimitation"></textarea>
      <label for="summaryReuseValue">可复用价值</label>
      <textarea id="summaryReuseValue"></textarea>
      <label for="summarySourcePages">来源页码</label>
      <input id="summarySourcePages" placeholder="pp. 1-5">
      <button data-action="note_paper_summary">生成摘要卡</button>

      <h2 style="margin-top:20px">文献检索记录</h2>
      <label for="searchQuestion">检索问题</label>
      <input id="searchQuestion">
      <label for="searchKeywords">关键词，多个用分号隔开</label>
      <input id="searchKeywords">
      <label for="searchQuery">检索式</label>
      <textarea id="searchQuery"></textarea>
      <label for="searchSource">检索平台</label>
      <input id="searchSource" placeholder="Google Scholar / Web of Science / Scopus">
      <label for="searchDate">日期</label>
      <input id="searchDate" placeholder="2026-05-19">
      <label for="searchFilters">筛选条件</label>
      <input id="searchFilters" placeholder="2020-2026">
      <label for="searchResultCount">结果数量</label>
      <input id="searchResultCount" placeholder="12">
      <label for="searchNotes">备注</label>
      <textarea id="searchNotes"></textarea>
      <button data-action="note_search_log">生成检索记录</button>

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

      <h2 style="margin-top:20px">生成图</h2>
      <label for="figureDataPath">数据文件路径</label>
      <input id="figureDataPath" placeholder="例如 C:\\Users\\22676\\Documents\\fixture-study\\simulation\\result.csv">
      <label for="figureOutDir">输出文件夹</label>
      <input id="figureOutDir" placeholder="例如 C:\\Users\\22676\\Documents\\fixture-study\\figures">
      <label for="figureStem">文件名前缀</label>
      <input id="figureStem" placeholder="stress-response">
      <label for="figureTitle">图题</label>
      <input id="figureTitle" placeholder="Stress response">
      <label for="figureType">图类型</label>
      <input id="figureType" placeholder="trend 或 bar">
      <label for="xColumn">X 列</label>
      <input id="xColumn" placeholder="time">
      <label for="yColumns">Y 列，多个用逗号隔开</label>
      <input id="yColumns" placeholder="stress">
      <label for="xLabel">X 轴标签</label>
      <input id="xLabel" placeholder="Time (s)">
      <label for="yLabel">Y 轴标签</label>
      <input id="yLabel" placeholder="Stress (MPa)">
      <button data-action="figure_from_data">生成 SVG 图</button>

      <h2 style="margin-top:20px">稿件检查</h2>
      <label for="manuscriptPath">稿件路径</label>
      <input id="manuscriptPath" placeholder="例如 C:\\Users\\22676\\Documents\\fixture-study\\manuscript\\chapter.md">
      <label for="requiredSections">必需章节，多个用逗号隔开</label>
      <input id="requiredSections" placeholder="Introduction,Method,Results">
      <label for="expectedFigures">预期图号，多个用逗号隔开</label>
      <input id="expectedFigures" placeholder="Figure 1,Figure 2">
      <button data-action="manuscript_check">检查稿件</button>
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
        base_dir: document.getElementById("baseDir").value,
        project_slug: document.getElementById("projectSlug").value,
        project_name: document.getElementById("projectName").value,
        project_root: document.getElementById("projectRoot").value,
        query: document.getElementById("libraryQuery").value,
        since_year: document.getElementById("sinceYear").value,
        source_query: document.getElementById("sourceQuery").value,
        csv_path: document.getElementById("csvPath").value,
        title: document.getElementById("title").value,
        authors: document.getElementById("authors").value,
        year: document.getElementById("year").value,
        source: document.getElementById("source").value,
        doi: document.getElementById("doi").value,
        pdf_name: document.getElementById("pdfName").value,
        note_path: document.getElementById("notePath").value,
        summary_title: document.getElementById("summaryTitle").value,
        summary_authors: document.getElementById("summaryAuthors").value,
        summary_source: document.getElementById("summarySource").value,
        summary_year: document.getElementById("summaryYear").value,
        summary_doi: document.getElementById("summaryDoi").value,
        summary_problem: document.getElementById("summaryProblem").value,
        summary_method: document.getElementById("summaryMethod").value,
        summary_data: document.getElementById("summaryData").value,
        summary_key_figures: document.getElementById("summaryKeyFigures").value,
        summary_main_result: document.getElementById("summaryMainResult").value,
        summary_limitation: document.getElementById("summaryLimitation").value,
        summary_reuse_value: document.getElementById("summaryReuseValue").value,
        summary_source_pages: document.getElementById("summarySourcePages").value,
        search_question: document.getElementById("searchQuestion").value,
        search_keywords: document.getElementById("searchKeywords").value,
        search_query: document.getElementById("searchQuery").value,
        search_source: document.getElementById("searchSource").value,
        search_date: document.getElementById("searchDate").value,
        search_filters: document.getElementById("searchFilters").value,
        search_result_count: document.getElementById("searchResultCount").value,
        search_notes: document.getElementById("searchNotes").value,
        data_path: document.getElementById("dataPath").value,
        required_columns: document.getElementById("requiredColumns").value,
        numeric_columns: document.getElementById("numericColumns").value,
        figure_data_path: document.getElementById("figureDataPath").value,
        figure_out_dir: document.getElementById("figureOutDir").value,
        figure_stem: document.getElementById("figureStem").value,
        figure_title: document.getElementById("figureTitle").value,
        figure_type: document.getElementById("figureType").value,
        x_column: document.getElementById("xColumn").value,
        y_columns: document.getElementById("yColumns").value,
        x_label: document.getElementById("xLabel").value,
        y_label: document.getElementById("yLabel").value,
        manuscript_path: document.getElementById("manuscriptPath").value,
        required_sections: document.getElementById("requiredSections").value,
        expected_figures: document.getElementById("expectedFigures").value
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
    if action not in {"init_project", "library_add"} and not str(project_root):
        return 400, "text/plain; charset=utf-8", "请先填写项目根目录。"

    try:
        if action == "init_project":
            created = bootstrap_workspace(
                Path(payload.get("base_dir", "").strip()),
                project_slug=payload.get("project_slug", "").strip(),
                project_name=payload.get("project_name", "").strip(),
            )
            return _text(f"已创建课题：{created}")
        if action == "project_check":
            return _text(render_project_check(build_project_check(project_root)))
        if action == "project_report":
            return _text(render_project_report(build_project_report(project_root)))
        if action == "writing_pack":
            return _text(render_writing_pack(build_writing_pack(project_root)))
        if action == "literature_table":
            return _text(render_literature_table(build_literature_table(project_root / "notes")))

        literature_root = project_root / "literature"
        if action == "library_stats":
            index = load_index(literature_root)
            return _text(render_library_stats(inspect_library_stats(literature_root, index)))
        if action == "library_search":
            index = load_index(literature_root)
            return _text(render_search_results(search_library(index, payload.get("query", ""))))
        if action == "library_recent":
            index = load_index(literature_root)
            return _text(render_search_results(filter_library_by_year(index, int(payload.get("since_year", "0").strip() or 0))))
        if action == "library_source":
            index = load_index(literature_root)
            return _text(render_search_results(filter_library_by_source(index, payload.get("source_query", ""))))
        if action == "library_import_csv":
            imported = import_csv_metadata(Path(payload.get("csv_path", "").strip()).read_text(encoding="utf-8-sig"))
            combined = LibraryIndex(entries=[])
            for entry in load_index(literature_root).entries + imported.entries:
                combined = add_entry(literature_root, combined, entry)
            combined.save(literature_root)
            return _text(f"已导入 {len(imported.entries)} 条，当前文献库共有 {len(load_index(literature_root).entries)} 条。")
        if action == "library_check_pdfs":
            return _text(render_pdf_inventory_report(inspect_pdf_inventory(literature_root, load_index(literature_root))))
        if action == "library_check_notes":
            return _text(render_note_inventory_report(inspect_note_inventory(literature_root, load_index(literature_root))))
        if action == "library_add":
            return _add_library_entry(project_root, payload)
        if action == "note_paper_summary":
            path = create_note_file(
                project_root / "notes",
                note_type="paper-summary",
                title=payload.get("summary_title", "").strip(),
                content=render_paper_summary(
                    PaperSummary(
                        title=payload.get("summary_title", "").strip(),
                        authors=[item.strip() for item in payload.get("summary_authors", "").split(";") if item.strip()],
                        source=payload.get("summary_source", "").strip(),
                        year=int(payload.get("summary_year", "0").strip() or 0),
                        doi=payload.get("summary_doi", "").strip(),
                        problem=payload.get("summary_problem", "").strip(),
                        method=payload.get("summary_method", "").strip(),
                        data=payload.get("summary_data", "").strip(),
                        key_figures=payload.get("summary_key_figures", "").strip(),
                        main_result=payload.get("summary_main_result", "").strip(),
                        limitation=payload.get("summary_limitation", "").strip(),
                        reuse_value=payload.get("summary_reuse_value", "").strip(),
                        source_pages=payload.get("summary_source_pages", "").strip(),
                    )
                ),
            )
            return _text(f"已生成摘要卡：{path}")
        if action == "note_search_log":
            path = create_note_file(
                project_root / "notes",
                note_type="search-log",
                title=payload.get("search_question", "").strip(),
                content=render_search_log(
                    SearchLogEntry(
                        question=payload.get("search_question", "").strip(),
                        keywords=[item.strip() for item in payload.get("search_keywords", "").split(";") if item.strip()],
                        query=payload.get("search_query", "").strip(),
                        source=payload.get("search_source", "").strip(),
                        date=payload.get("search_date", "").strip(),
                        filters=payload.get("search_filters", "").strip(),
                        result_count=int(payload.get("search_result_count", "0").strip() or 0),
                        notes=payload.get("search_notes", "").strip(),
                    )
                ),
            )
            return _text(f"已生成检索记录：{path}")
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
        if action == "figure_from_data":
            out_dir = Path(payload.get("figure_out_dir", "").strip())
            stem = payload.get("figure_stem", "").strip()
            spec = build_spec_from_dataset(
                load_tabular_result(Path(payload.get("figure_data_path", "").strip())),
                title=payload.get("figure_title", "").strip(),
                figure_type=payload.get("figure_type", "").strip() or "trend",
                x_column=payload.get("x_column", "").strip(),
                y_columns=_split_csv_input(payload.get("y_columns", "")),
                y_error_columns=[],
                x_label=payload.get("x_label", "").strip(),
                y_label=payload.get("y_label", "").strip(),
                width_mm=180,
                height_mm=120,
                dpi=300,
            )
            export_figure_bundle(spec, out_dir, stem=stem)
            return _text(f"已生成：{out_dir / f'{stem}.svg'}\n已生成：{out_dir / f'{stem}.json'}")
        if action == "manuscript_check":
            return _text(
                render_report_from_inspection(
                    inspect_manuscript(
                        Path(payload.get("manuscript_path", "").strip()),
                        required_sections=_split_csv_input(payload.get("required_sections", "")),
                        expected_figures=_split_csv_input(payload.get("expected_figures", "")),
                        library_index=load_index(project_root / "literature"),
                    )
                )
            )
    except Exception as exc:
        return 500, "text/plain; charset=utf-8", f"运行失败：{exc}"

    return 400, "text/plain; charset=utf-8", f"不支持的操作：{action}"


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


def _text(body: str) -> ContentResponse:
    return 200, "text/plain; charset=utf-8", body


def _split_csv_input(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


if __name__ == "__main__":
    raise SystemExit(main())
