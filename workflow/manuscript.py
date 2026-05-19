from __future__ import annotations

import re
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from xml.etree import ElementTree

from workflow.library import LibraryIndex, make_citekey


SECTION_ALIASES = {
    "introduction": ["Introduction", "引言", "绪论", "研究背景"],
    "method": ["Method", "Methods", "方法", "研究方法", "材料与方法"],
    "results": ["Results", "Result", "结果", "结果与讨论", "实验结果"],
    "discussion": ["Discussion", "讨论", "结果与讨论"],
    "conclusion": ["Conclusion", "Conclusions", "结论", "总结"],
}


@dataclass(frozen=True)
class ManuscriptIssue:
    level: str
    message: str


@dataclass(frozen=True)
class ManuscriptReport:
    path: Path
    citations: list[str]
    figures: list[str]
    missing_sections: list[str] = field(default_factory=list)
    missing_figures: list[str] = field(default_factory=list)
    missing_citations: list[str] = field(default_factory=list)
    uncited_library_keys: list[str] = field(default_factory=list)
    issues: list[ManuscriptIssue] = field(default_factory=list)


def inspect_manuscript(
    path: Path,
    *,
    required_sections: list[str] | None = None,
    expected_figures: list[str] | None = None,
    library_index: LibraryIndex | None = None,
) -> ManuscriptReport:
    text = _read_manuscript_text(path)
    citations = _extract_citations(text)
    figure_mentions = _extract_figure_mentions(text)
    figures = _unique_in_order(figure_mentions)
    headings = _extract_headings(text)
    required = required_sections or []
    expected = expected_figures or []
    missing_sections = [section for section in required if not _has_required_section(section, headings)]
    missing_figures = [figure for figure in expected if figure not in figures]
    library_keys = {make_citekey(entry) for entry in library_index.entries} if library_index else set()
    missing_citations = [citation for citation in citations if library_keys and citation not in library_keys]
    uncited_library_keys = sorted(key for key in library_keys if key not in citations)
    issues = [
        ManuscriptIssue(level="warning", message=f"Missing section: {section}")
        for section in missing_sections
    ]
    issues.extend(
        ManuscriptIssue(level="warning", message=f"Missing figure marker: {figure}")
        for figure in missing_figures
    )
    issues.extend(_inspect_figure_marker_quality(figure_mentions))
    issues.extend(
        ManuscriptIssue(level="warning", message=f"Citation not found in library: {citation}")
        for citation in missing_citations
    )
    issues.extend(
        ManuscriptIssue(level="info", message=f"Library entry not cited in manuscript: {citation}")
        for citation in uncited_library_keys
    )
    if not citations:
        issues.append(ManuscriptIssue(level="warning", message="No citation markers found"))
    return ManuscriptReport(
        path=path,
        citations=citations,
        figures=figures,
        missing_sections=missing_sections,
        missing_figures=missing_figures,
        missing_citations=missing_citations,
        uncited_library_keys=uncited_library_keys,
        issues=issues,
    )


def render_manuscript_report(
    *,
    citations: list[str],
    figures: list[str],
    issues: list[ManuscriptIssue],
) -> str:
    lines = ["# Manuscript Check Report", ""]
    lines.append("## Citations")
    lines.extend([f"- {citation}" for citation in citations] or ["- None"])
    lines.append("")
    lines.append("## Figures")
    lines.extend([f"- {figure}" for figure in figures] or ["- None"])
    lines.append("")
    lines.append("## Issues")
    lines.extend([f"- {issue.level}: {issue.message}" for issue in issues] or ["- None"])
    lines.append("")
    return "\n".join(lines)


def render_report_from_inspection(report: ManuscriptReport) -> str:
    return render_manuscript_report(
        citations=report.citations,
        figures=report.figures,
        issues=report.issues,
    )


def _extract_citations(text: str) -> list[str]:
    citations: list[str] = []
    for match in re.finditer(r"\[@([A-Za-z0-9_:\-.]+)\]", text):
        citation = match.group(1)
        if citation not in citations:
            citations.append(citation)
    return citations


def _extract_figures(text: str) -> list[str]:
    return _unique_in_order(_extract_figure_mentions(text))


def _extract_figure_mentions(text: str) -> list[str]:
    return [match.group(0) for match in _iter_figure_matches(text)]


def _iter_figure_matches(text: str) -> list[re.Match[str]]:
    matches = list(re.finditer(r"\bFigure\s+\d+\b", text))
    matches.extend(re.finditer(r"图\s*\d+", text))
    matches.extend(re.finditer(r"ͼ\s*\d+", text))
    return sorted(matches, key=lambda match: match.start())


def _inspect_figure_marker_quality(figures: list[str]) -> list[ManuscriptIssue]:
    issues: list[ManuscriptIssue] = []
    seen: set[str] = set()
    duplicates: list[str] = []
    for figure in figures:
        if figure in seen and figure not in duplicates:
            duplicates.append(figure)
        seen.add(figure)
    issues.extend(
        ManuscriptIssue(level="warning", message=f"Duplicate figure marker: {figure}")
        for figure in duplicates
    )
    english_numbers = sorted({int(match.group(1)) for figure in figures if (match := re.match(r"Figure\s+(\d+)", figure))})
    if english_numbers:
        issues.extend(
            ManuscriptIssue(level="warning", message=f"Missing figure number in sequence: Figure {number}")
            for number in range(english_numbers[0], english_numbers[-1] + 1)
            if number not in english_numbers
        )
    return issues


def _unique_in_order(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if value not in result:
            result.append(value)
    return result


def _extract_headings(text: str) -> list[str]:
    headings: list[str] = []
    for line in text.splitlines():
        match = re.match(r"^#{1,6}\s+(.+?)\s*$", line)
        if match:
            headings.append(match.group(1).strip())
        elif line.strip() and len(line.strip()) <= 80:
            headings.append(line.strip())
    return headings


def _has_required_section(required: str, headings: list[str]) -> bool:
    heading_keys = {_normalize_heading(heading) for heading in headings}
    aliases = SECTION_ALIASES.get(_normalize_heading(required), [required])
    return any(_normalize_heading(alias) in heading_keys for alias in aliases)


def _normalize_heading(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def _read_manuscript_text(path: Path) -> str:
    if path.suffix.lower() == ".docx":
        return _read_docx_text(path)
    return path.read_text(encoding="utf-8-sig")


def _read_docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as package:
        xml = package.read("word/document.xml")
    root = ElementTree.fromstring(xml)
    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    paragraphs: list[str] = []
    for paragraph in root.findall(".//w:p", namespace):
        texts = [node.text or "" for node in paragraph.findall(".//w:t", namespace)]
        value = "".join(texts).strip()
        if value:
            paragraphs.append(value)
    return "\n".join(paragraphs)
