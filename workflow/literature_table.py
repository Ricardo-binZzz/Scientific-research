from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LiteratureTableRow:
    title: str
    authors: str
    year: str
    source: str
    problem: str
    method: str
    data: str
    main_result: str
    limitation: str
    reuse_value: str
    source_pages: str


@dataclass(frozen=True)
class LiteratureTable:
    notes_dir: Path
    rows: list[LiteratureTableRow]


def build_literature_table(notes_dir: Path) -> LiteratureTable:
    rows: list[LiteratureTableRow] = []
    if notes_dir.exists():
        for path in sorted(notes_dir.glob("*.md")):
            fields = _read_paper_summary_fields(path)
            if fields:
                rows.append(_row_from_fields(fields))
    return LiteratureTable(notes_dir=notes_dir, rows=rows)


def render_literature_table(table: LiteratureTable) -> str:
    lines = [
        "# Literature Comparison Table",
        "",
        f"- Notes directory: {table.notes_dir}",
        f"- Paper summaries: {len(table.rows)}",
        "",
    ]
    if not table.rows:
        lines.append("No paper summary notes found.")
        lines.append("")
        return "\n".join(lines)
    lines.append(
        "| Title | Authors | Year | Source | Problem | Method | Data | Main result | Limitation | Reuse value | Source pages |"
    )
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for row in table.rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    _escape_cell(row.title),
                    _escape_cell(row.authors),
                    _escape_cell(row.year),
                    _escape_cell(row.source),
                    _escape_cell(row.problem),
                    _escape_cell(row.method),
                    _escape_cell(row.data),
                    _escape_cell(row.main_result),
                    _escape_cell(row.limitation),
                    _escape_cell(row.reuse_value),
                    _escape_cell(row.source_pages),
                ]
            )
            + " |"
        )
    lines.append("")
    return "\n".join(lines)


def _read_paper_summary_fields(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8-sig")
    if not text.startswith("# Paper Summary"):
        return {}
    fields: dict[str, str] = {}
    for line in text.splitlines():
        if not line.startswith("- ") or ": " not in line:
            continue
        key, value = line[2:].split(": ", 1)
        fields[key.lower()] = value.strip()
    return fields


def _row_from_fields(fields: dict[str, str]) -> LiteratureTableRow:
    return LiteratureTableRow(
        title=fields.get("title", ""),
        authors=fields.get("authors", ""),
        year=fields.get("year", ""),
        source=fields.get("source", ""),
        problem=fields.get("problem", ""),
        method=fields.get("method", ""),
        data=fields.get("data", ""),
        main_result=fields.get("main result", ""),
        limitation=fields.get("limitation", ""),
        reuse_value=fields.get("reuse value", ""),
        source_pages=fields.get("source pages", ""),
    )


def _escape_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()
