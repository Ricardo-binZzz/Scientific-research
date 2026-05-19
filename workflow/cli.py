from __future__ import annotations

import argparse
import sys

from workflow.commands import handle_args


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="research-workflow")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="bootstrap a new research workspace")
    init_parser.add_argument("base_dir", help="directory where the workspace should be created")
    init_parser.add_argument("--slug", required=True, help="workspace folder name")
    init_parser.add_argument("--name", required=True, help="human-readable project name")
    note_parser = subparsers.add_parser("note", help="create a research note")
    note_subparsers = note_parser.add_subparsers(dest="note_type", required=True)

    search_parser = note_subparsers.add_parser("search-log", help="write a search log entry")
    search_parser.add_argument("notes_dir", help="directory where notes should be written")
    search_parser.add_argument("--question", required=True)
    search_parser.add_argument("--keyword", action="append", default=[], dest="keywords")
    search_parser.add_argument("--query", required=True)
    search_parser.add_argument("--source", required=True)
    search_parser.add_argument("--date", required=True)
    search_parser.add_argument("--filters", required=True)
    search_parser.add_argument("--result-count", required=True, type=int)
    search_parser.add_argument("--notes", required=True)
    search_parser.add_argument("--timestamp")

    summary_parser = note_subparsers.add_parser("paper-summary", help="write a paper summary card")
    summary_parser.add_argument("notes_dir", help="directory where notes should be written")
    summary_parser.add_argument("--title", required=True)
    summary_parser.add_argument("--author", action="append", default=[], dest="authors")
    summary_parser.add_argument("--source", required=True)
    summary_parser.add_argument("--year", required=True, type=int)
    summary_parser.add_argument("--doi", required=True)
    summary_parser.add_argument("--problem", required=True)
    summary_parser.add_argument("--method", required=True)
    summary_parser.add_argument("--data", required=True)
    summary_parser.add_argument("--key-figures", required=True)
    summary_parser.add_argument("--main-result", required=True)
    summary_parser.add_argument("--limitation", required=True)
    summary_parser.add_argument("--reuse-value", required=True)
    summary_parser.add_argument("--source-pages", required=True)
    summary_parser.add_argument("--timestamp")

    outline_parser = note_subparsers.add_parser("outline", help="write an outline draft")
    outline_parser.add_argument("notes_dir", help="directory where notes should be written")
    outline_parser.add_argument("--topic", required=True)
    outline_parser.add_argument("--problem-statement", required=True)
    outline_parser.add_argument("--section", action="append", default=[], dest="sections")
    outline_parser.add_argument("--conclusion", required=True)
    outline_parser.add_argument("--timestamp")

    review_parser = note_subparsers.add_parser("literature-review", help="write a literature review paragraph")
    review_parser.add_argument("notes_dir", help="directory where notes should be written")
    review_parser.add_argument("--paper", required=True)
    review_parser.add_argument("--claim", required=True)
    review_parser.add_argument("--evidence", required=True)
    review_parser.add_argument("--connection", required=True)
    review_parser.add_argument("--limit", required=True)
    review_parser.add_argument("--timestamp")

    sim_parser = subparsers.add_parser("simulation", help="create a simulation runbook or inspect exports")
    sim_subparsers = sim_parser.add_subparsers(dest="sim_command", required=True)

    runbook_parser = sim_subparsers.add_parser("runbook", help="write a simulation runbook")
    runbook_parser.add_argument("notes_dir", help="directory where notes should be written")
    runbook_parser.add_argument("--name", required=True)
    runbook_parser.add_argument("--software", required=True)
    runbook_parser.add_argument("--version", required=True)
    runbook_parser.add_argument("--geometry-source", required=True)
    runbook_parser.add_argument("--material-set", required=True)
    runbook_parser.add_argument("--boundary-conditions", required=True)
    runbook_parser.add_argument("--mesh-summary", required=True)
    runbook_parser.add_argument("--solve-settings", required=True)
    runbook_parser.add_argument("--export-format", required=True)
    runbook_parser.add_argument("--validation-notes", required=True)
    runbook_parser.add_argument("--timestamp")

    list_parser = sim_subparsers.add_parser("list-exports", help="list simulation export files")
    list_parser.add_argument("root_dir", help="directory to scan for exports")

    inspect_parser = sim_subparsers.add_parser("inspect-data", help="print normalized columns and sample rows")
    inspect_parser.add_argument("data_path", help="csv or json data path")
    inspect_parser.add_argument("--rows", type=int, default=5, help="number of sample rows to print")

    summarize_parser = sim_subparsers.add_parser("summarize-data", help="print numeric column ranges")
    summarize_parser.add_argument("data_path", help="csv or json data path")

    range_parser = sim_subparsers.add_parser("check-ranges", help="check numeric columns against expected ranges")
    range_parser.add_argument("data_path", help="csv or json data path")
    range_parser.add_argument("--range", action="append", default=[], dest="ranges", help="column:min:max")

    validate_parser = sim_subparsers.add_parser("validate-data", help="validate exported tabular data")
    validate_parser.add_argument("data_path", help="csv or json data path")
    validate_parser.add_argument("--required-column", action="append", default=[], dest="required_columns")
    validate_parser.add_argument("--numeric-column", action="append", default=[], dest="numeric_columns")
    validate_parser.add_argument("--metadata", help="optional simulation metadata JSON with column units")

    library_parser = subparsers.add_parser("library", help="manage the literature library")
    library_subparsers = library_parser.add_subparsers(dest="library_command", required=True)

    add_parser = library_subparsers.add_parser("add", help="add a literature entry")
    add_parser.add_argument("root_dir", help="library root directory")
    add_parser.add_argument("--title", required=True)
    add_parser.add_argument("--author", action="append", default=[], dest="authors")
    add_parser.add_argument("--year", required=True, type=int)
    add_parser.add_argument("--source", required=True)
    add_parser.add_argument("--doi", required=True)
    add_parser.add_argument("--pdf-name", required=True)
    add_parser.add_argument("--note-path", required=True)

    list_library_parser = library_subparsers.add_parser("list", help="list literature entries")
    list_library_parser.add_argument("root_dir", help="library root directory")

    export_bibtex_parser = library_subparsers.add_parser("export-bibtex", help="export library entries as BibTeX")
    export_bibtex_parser.add_argument("root_dir", help="library root directory")
    export_bibtex_parser.add_argument("out_path", help="output .bib path")

    import_bibtex_parser = library_subparsers.add_parser("import-bibtex", help="import BibTeX entries into the local index")
    import_bibtex_parser.add_argument("root_dir", help="library root directory")
    import_bibtex_parser.add_argument("bib_path", help="input .bib path")

    import_csv_parser = library_subparsers.add_parser("import-csv", help="import CSV metadata entries into the local index")
    import_csv_parser.add_argument("root_dir", help="library root directory")
    import_csv_parser.add_argument("csv_path", help="input .csv path")

    check_pdfs_parser = library_subparsers.add_parser("check-pdfs", help="check whether indexed PDFs exist")
    check_pdfs_parser.add_argument("root_dir", help="library root directory")

    stats_parser = library_subparsers.add_parser("stats", help="print literature library statistics")
    stats_parser.add_argument("root_dir", help="library root directory")

    figure_parser = subparsers.add_parser("figure", help="generate figure assets")
    figure_subparsers = figure_parser.add_subparsers(dest="figure_command", required=True)

    from_data_parser = figure_subparsers.add_parser("from-data", help="generate a figure bundle from csv/json data")
    from_data_parser.add_argument("data_path", help="csv or json data path")
    from_data_parser.add_argument("out_dir", help="directory where figure assets should be written")
    from_data_parser.add_argument("--stem", required=True)
    from_data_parser.add_argument("--title", required=True)
    from_data_parser.add_argument("--figure-type", required=True)
    from_data_parser.add_argument("--x-column", required=True)
    from_data_parser.add_argument("--y-column", action="append", default=[], dest="y_columns")
    from_data_parser.add_argument("--y-error-column", action="append", default=[], dest="y_error_columns")
    from_data_parser.add_argument("--value-column")
    from_data_parser.add_argument("--x-label", required=True)
    from_data_parser.add_argument("--y-label", required=True)
    from_data_parser.add_argument("--width-mm", type=int, default=180)
    from_data_parser.add_argument("--height-mm", type=int, default=120)
    from_data_parser.add_argument("--dpi", type=int, default=300)

    manuscript_parser = subparsers.add_parser("manuscript", help="inspect manuscript drafts")
    manuscript_subparsers = manuscript_parser.add_subparsers(dest="manuscript_command", required=True)

    check_parser = manuscript_subparsers.add_parser("check", help="check a markdown/plain-text manuscript draft")
    check_parser.add_argument("path", help="manuscript path")
    check_parser.add_argument("--required-section", action="append", default=[], dest="required_sections")
    check_parser.add_argument("--expected-figure", action="append", default=[], dest="expected_figures")
    check_parser.add_argument("--library-root", help="library root directory for citation coverage checks")

    project_parser = subparsers.add_parser("project", help="inspect research project status")
    project_subparsers = project_parser.add_subparsers(dest="project_command", required=True)
    report_parser = project_subparsers.add_parser("report", help="print a project status report")
    report_parser.add_argument("root_dir", help="project root directory")
    check_project_parser = project_subparsers.add_parser("check", help="print a project health check")
    check_project_parser.add_argument("root_dir", help="project root directory")
    writing_pack_parser = project_subparsers.add_parser("writing-pack", help="print or write a manuscript writing pack")
    writing_pack_parser.add_argument("root_dir", help="project root directory")
    writing_pack_parser.add_argument("--out", help="optional output Markdown path")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return handle_args(args)
    except ValueError as exc:
        parser.error(str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
