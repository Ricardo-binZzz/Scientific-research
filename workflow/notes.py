from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class SearchLogEntry:
    question: str
    keywords: list[str]
    query: str
    source: str
    date: str
    filters: str
    result_count: int
    notes: str


@dataclass(frozen=True)
class PaperSummary:
    title: str
    authors: list[str]
    source: str
    year: int
    doi: str
    problem: str
    method: str
    data: str
    key_figures: str
    main_result: str
    limitation: str
    reuse_value: str
    source_pages: str


@dataclass(frozen=True)
class OutlineSection:
    heading: str
    bullets: list[str]


@dataclass(frozen=True)
class OutlineDraft:
    topic: str
    problem_statement: str
    sections: list[OutlineSection]
    conclusion: str


@dataclass(frozen=True)
class LiteratureReviewParagraph:
    paper: str
    claim: str
    evidence: str
    connection_to_current_work: str
    limit: str


def render_search_log(entry: SearchLogEntry) -> str:
    return "\n".join(
        [
            "# Search Log",
            "",
            f"- Question: {entry.question}",
            f"- Keywords: {', '.join(entry.keywords)}",
            f"- Query: {entry.query}",
            f"- Source: {entry.source}",
            f"- Date: {entry.date}",
            f"- Filters: {entry.filters}",
            f"- Result count: {entry.result_count}",
            f"- Notes: {entry.notes}",
            "",
        ]
    )


def render_paper_summary(summary: PaperSummary) -> str:
    return "\n".join(
        [
            "# Paper Summary",
            "",
            f"- Title: {summary.title}",
            f"- Authors: {'; '.join(summary.authors)}",
            f"- Source: {summary.source}",
            f"- Year: {summary.year}",
            f"- DOI: {summary.doi}",
            f"- Problem: {summary.problem}",
            f"- Method: {summary.method}",
            f"- Data: {summary.data}",
            f"- Key figures: {summary.key_figures}",
            f"- Main result: {summary.main_result}",
            f"- Limitation: {summary.limitation}",
            f"- Reuse value: {summary.reuse_value}",
            f"- Source pages: {summary.source_pages}",
            "",
        ]
    )


def render_outline(draft: OutlineDraft) -> str:
    lines = ["# Outline", "", f"- Topic: {draft.topic}", f"- Problem statement: {draft.problem_statement}", ""]
    for section in draft.sections:
        lines.append(f"## {section.heading}")
        for bullet in section.bullets:
            lines.append(f"- {bullet}")
        lines.append("")
    lines.extend([f"- Conclusion: {draft.conclusion}", ""])
    return "\n".join(lines)


def render_literature_review(paragraph: LiteratureReviewParagraph) -> str:
    return "\n".join(
        [
            "# Literature Review Paragraph",
            "",
            f"- Paper: {paragraph.paper}",
            f"- Claim: {paragraph.claim}",
            f"- Evidence: {paragraph.evidence}",
            f"- Connection to current work: {paragraph.connection_to_current_work}",
            f"- Limit: {paragraph.limit}",
            "",
        ]
    )


def create_note_file(
    notes_dir: Path,
    *,
    note_type: str,
    title: str,
    content: str,
    timestamp: str | None = None,
) -> Path:
    notes_dir.mkdir(parents=True, exist_ok=True)
    safe_title = _slugify(title)
    stamp = timestamp or datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{stamp}-{safe_title}.md"
    path = notes_dir / filename
    path.write_text(content, encoding="utf-8")
    return path


def _slugify(text: str) -> str:
    value = text.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "note"
