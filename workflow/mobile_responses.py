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
        "primaryMessage": _attention_message(total),
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


def _attention_message(total: int) -> str:
    if not total:
        return "No urgent gaps found"
    if total == 1:
        return "1 item needs attention"
    return f"{total} items need attention"


def _issue_counts(markdown: str) -> dict[str, int]:
    simulation_issues = _extract_count(markdown, "Simulation issues")
    if simulation_issues is None:
        simulation_issues = _section_bullet_count(markdown, "Simulation")

    manuscript_issues = _extract_count(markdown, "Manuscript issues")
    if manuscript_issues is None:
        manuscript_issues = _section_bullet_count(markdown, "Manuscript")

    return {
        "missing_pdfs": _extract_count(markdown, "Missing PDFs") or 0,
        "missing_notes": _extract_count(markdown, "Missing notes") or 0,
        "simulation_issues": simulation_issues,
        "manuscript_issues": manuscript_issues,
    }


def _extract_count(markdown: str, label: str) -> int | None:
    matches = re.findall(rf"^\s*-?\s*{re.escape(label)}:\s*(.+?)\s*$", markdown, flags=re.IGNORECASE | re.MULTILINE)
    if not matches:
        return None

    total = 0
    for value in matches:
        digit_match = re.match(r"(\d+)\b", value)
        if digit_match:
            total += int(digit_match.group(1))
        elif not re.match(r"(?i)none|no\b|n/a\b", value.strip()):
            total += 1
    return total


def _section_bullet_count(markdown: str, heading: str) -> int:
    count = 0
    in_section = False
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            in_section = stripped.lstrip("#").strip().lower() == heading.lower()
            continue
        if in_section and stripped.startswith("- ") and not _is_empty_bullet(stripped[2:].strip()):
            count += 1
    return count


def _is_empty_bullet(text: str) -> bool:
    return bool(re.match(r"(?i)none|no\b|n/a\b", text.strip()))


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
