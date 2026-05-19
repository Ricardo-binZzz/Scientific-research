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
from workflow.literature_map import build_literature_map, render_literature_map
from workflow.literature_table import build_literature_table, render_literature_table
from workflow.literature_tracker import build_literature_tracker, render_literature_tracker
from workflow.manuscript import inspect_manuscript, render_report_from_inspection
from workflow.notes import PaperSummary, SearchLogEntry, create_note_file, render_paper_summary, render_search_log
from workflow.project_report import build_project_check, build_project_report, render_project_check, render_project_report
from workflow.python.figure_exporter import (
    build_contour_spec_from_dataset,
    build_heatmap_spec_from_dataset,
    build_spec_from_dataset,
    export_figure_bundle,
)
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
from workflow.writing_dashboard import build_writing_dashboard, render_writing_dashboard


ContentResponse = tuple[int, str, str]


def render_home_page(default_project_root: str = "") -> str:
    index_path = Path(__file__).with_name("web_assets") / "index.html"
    content = index_path.read_text(encoding="utf-8")
    return content.replace("__DEFAULT_PROJECT_ROOT__", html.escape(default_project_root, quote=True))


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
        if action == "workflow_status":
            return _text(_render_workflow_status(project_root))
        if action == "project_report":
            return _text(render_project_report(build_project_report(project_root)))
        if action == "writing_pack":
            return _text(render_writing_pack(build_writing_pack(project_root)))
        if action == "literature_table":
            return _text(render_literature_table(build_literature_table(project_root / "notes")))
        if action == "writing_dashboard":
            return _text(render_writing_dashboard(build_writing_dashboard(project_root)))
        if action == "literature_tracker":
            return _text(render_literature_tracker(build_literature_tracker(project_root)))
        if action == "save_standard_report":
            return _save_standard_report(project_root, payload.get("report_kind", "").strip())

        literature_root = project_root / "literature"
        if action == "literature_map":
            return _text(render_literature_map(build_literature_map(literature_root)))
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
            dataset = load_tabular_result(Path(payload.get("figure_data_path", "").strip()))
            figure_type = payload.get("figure_type", "").strip() or "trend"
            if figure_type == "heatmap":
                spec = build_heatmap_spec_from_dataset(
                    dataset,
                    title=payload.get("figure_title", "").strip(),
                    x_column=payload.get("x_column", "").strip(),
                    y_column=_first_value(payload.get("y_columns", "")),
                    value_column=payload.get("value_column", "").strip(),
                    x_label=payload.get("x_label", "").strip(),
                    y_label=payload.get("y_label", "").strip(),
                    width_mm=_int_or_default(payload.get("figure_width_mm", ""), 180),
                    height_mm=_int_or_default(payload.get("figure_height_mm", ""), 120),
                    dpi=300,
                )
            elif figure_type == "contour":
                spec = build_contour_spec_from_dataset(
                    dataset,
                    title=payload.get("figure_title", "").strip(),
                    x_column=payload.get("x_column", "").strip(),
                    y_column=_first_value(payload.get("y_columns", "")),
                    value_column=payload.get("value_column", "").strip(),
                    x_label=payload.get("x_label", "").strip(),
                    y_label=payload.get("y_label", "").strip(),
                    width_mm=_int_or_default(payload.get("figure_width_mm", ""), 180),
                    height_mm=_int_or_default(payload.get("figure_height_mm", ""), 120),
                    dpi=300,
                )
            else:
                spec = build_spec_from_dataset(
                    dataset,
                    title=payload.get("figure_title", "").strip(),
                    figure_type=figure_type,
                    x_column=payload.get("x_column", "").strip(),
                    y_columns=_split_csv_input(payload.get("y_columns", "")),
                    y_error_columns=_split_csv_input(payload.get("y_error_columns", "")),
                    x_label=payload.get("x_label", "").strip(),
                    y_label=payload.get("y_label", "").strip(),
                    width_mm=_int_or_default(payload.get("figure_width_mm", ""), 180),
                    height_mm=_int_or_default(payload.get("figure_height_mm", ""), 120),
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


def _save_standard_report(project_root: Path, report_kind: str) -> ContentResponse:
    reports = {
        "writing_pack": (
            project_root / "manuscript" / "writing-pack.md",
            lambda: render_writing_pack(build_writing_pack(project_root)),
        ),
        "writing_dashboard": (
            project_root / "manuscript" / "writing-dashboard.md",
            lambda: render_writing_dashboard(build_writing_dashboard(project_root)),
        ),
        "literature_table": (
            project_root / "notes" / "literature-table.md",
            lambda: render_literature_table(build_literature_table(project_root / "notes")),
        ),
        "literature_map": (
            project_root / "notes" / "literature-map.md",
            lambda: render_literature_map(build_literature_map(project_root / "literature")),
        ),
        "literature_tracker": (
            project_root / "notes" / "literature-tracker.md",
            lambda: render_literature_tracker(build_literature_tracker(project_root)),
        ),
    }
    if report_kind not in reports:
        return 400, "text/plain; charset=utf-8", f"不支持的标准报告：{report_kind}"
    out_path, build_content = reports[report_kind]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(build_content(), encoding="utf-8")
    return _text(f"已保存标准报告：{out_path}")


def _render_workflow_status(project_root: Path) -> str:
    report = build_project_report(project_root)
    check = build_project_check(project_root)
    steps = [
        ("Project structure", project_root.exists(), "Create or select a project directory."),
        ("Literature library", report.library_entries > 0, "Add or import literature entries."),
        ("Paper summaries", report.note_files > 0, "Create paper-summary notes for useful papers."),
        ("Simulation data", report.simulation_exports > 0, "Add exported CSV/JSON simulation data."),
        ("Figures", report.figure_bundles > 0, "Generate SVG figures from validated data."),
        ("Manuscript draft", report.manuscript_files > 0, "Add a manuscript draft for checking."),
    ]
    next_action = next((advice for _name, ready, advice in steps if not ready), "Run project check and fix reported gaps.")
    lines = ["# Workflow Status", "", f"- Root: {project_root}", ""]
    lines.append("## Steps")
    for name, ready, advice in steps:
        marker = "ready" if ready else "todo"
        lines.append(f"- {name}: {marker} - {advice if not ready else 'OK'}")
    lines.append("")
    lines.append("## Current Gaps")
    lines.append(f"- Missing PDFs: {len(check.missing_pdf_names)}")
    lines.append(f"- Missing notes: {len(check.missing_note_paths)}")
    lines.append(f"- Simulation issues: {len(check.simulation_issues)}")
    lines.append(f"- Manuscript issues: {len(check.manuscript_issues)}")
    lines.append("")
    lines.append(f"## Next recommended action\n- {next_action}")
    lines.append("")
    return "\n".join(lines)


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
            if name not in {"styles.css", "app.js"}:
                self._send(404, "text/plain; charset=utf-8", "Not Found")
                return
            path = Path(__file__).with_name("web_assets") / name
            content_type = "text/css; charset=utf-8" if name.endswith(".css") else "application/javascript; charset=utf-8"
            self._send(200, content_type, path.read_text(encoding="utf-8"))

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


def _first_value(value: str) -> str:
    values = _split_csv_input(value)
    return values[0] if values else ""


def _int_or_default(value: str, default: int) -> int:
    text = value.strip()
    if not text:
        return default
    parsed = int(text)
    if parsed <= 0:
        raise ValueError("figure size must be greater than 0")
    return parsed


if __name__ == "__main__":
    raise SystemExit(main())
