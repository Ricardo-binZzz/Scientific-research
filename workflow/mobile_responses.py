from __future__ import annotations

import re
from typing import Any


MobileResponse = dict[str, Any]


def mobile_response(action: str, markdown: str) -> MobileResponse:
    return {
        "ok": True,
        "action": action,
        "summary": build_mobile_summary(action, markdown),
        "cards": build_mobile_cards(action, markdown),
        "markdown": markdown,
    }


def build_mobile_summary(action: str, markdown: str) -> dict[str, str]:
    counts = _issue_counts(markdown)
    total = sum(counts.values())
    next_action = _first_bullet_after_heading(markdown, "Next Actions")
    if not next_action:
        next_action = _first_bullet_after_heading(markdown, "Next recommended action")
    if not next_action:
        next_action = "Review the generated report details."

    titles = {
        "project_check": "Project check complete",
        "workflow_status": "Workflow status updated",
        "project_report": "Project overview updated",
        "save_standard_report": "Reports updated",
    }
    return {
        "title": titles.get(action, "Workflow action complete"),
        "primaryMessage": f"{total} items need attention" if total else "No urgent gaps found",
        "nextAction": next_action,
    }


def build_mobile_cards(action: str, markdown: str) -> list[dict[str, str]]:
    counts = _issue_counts(markdown)
    return [
        _card(
            "Literature",
            counts["missing_pdfs"] + counts["missing_notes"],
            _literature_message(counts["missing_pdfs"], counts["missing_notes"]),
            ready_message="No literature asset gaps found",
        ),
        _card(
            "Simulation",
            counts["simulation_issues"],
            _issue_message(counts["simulation_issues"], "simulation issue"),
            ready_message="No simulation issues found",
        ),
        _card(
            "Manuscript",
            counts["manuscript_issues"],
            _issue_message(counts["manuscript_issues"], "manuscript issue"),
            ready_message="No manuscript issues found",
        ),
    ]


def error_response(action: str, message: str, status: int = 400) -> MobileResponse:
    return {
        "ok": False,
        "action": action,
        "status": status,
        "summary": {
            "title": "Action needs attention",
            "primaryMessage": message,
            "nextAction": "Check the connection, project root, and local service window.",
        },
        "cards": [],
        "markdown": message,
    }


def _card(
    label: str,
    count: int,
    message: str,
    ready_message: str,
) -> dict[str, str]:
    return {
        "label": label,
        "status": "needs_attention" if count else "ready",
        "message": message if count else ready_message,
    }


def _literature_message(missing_pdfs: int, missing_notes: int) -> str:
    parts: list[str] = []
    if missing_pdfs:
        pdf_noun = "PDF" if missing_pdfs == 1 else "PDFs"
        parts.append(f"{missing_pdfs} {pdf_noun} missing")
    if missing_notes:
        note_noun = "note" if missing_notes == 1 else "notes"
        parts.append(f"{missing_notes} {note_noun} missing")
    return ", ".join(parts) if parts else "No literature asset gaps found"


def _issue_message(count: int, singular_label: str) -> str:
    suffix = "" if count == 1 else "s"
    return f"{count} {singular_label}{suffix} found"


def _issue_counts(markdown: str) -> dict[str, int]:
    return {
        "missing_pdfs": _extract_count(markdown, "Missing PDFs"),
        "missing_notes": _extract_count(markdown, "Missing notes"),
        "simulation_issues": _extract_count(markdown, "Simulation issues"),
        "manuscript_issues": _extract_count(markdown, "Manuscript issues"),
    }


def _extract_count(markdown: str, label: str) -> int:
    match = re.search(rf"{re.escape(label)}:\s*(\d+)", markdown, flags=re.IGNORECASE)
    return int(match.group(1)) if match else 0


def _first_bullet_after_heading(markdown: str, heading: str) -> str:
    in_section = False
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            in_section = stripped.lstrip("#").strip().lower() == heading.lower()
            continue
        if in_section and stripped.startswith("- "):
            return stripped[2:].strip()
    return ""
