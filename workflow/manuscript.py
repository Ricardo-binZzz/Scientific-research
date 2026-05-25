from __future__ import annotations

import posixpath
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

REFERENCE_HEADINGS = {"references", "reference", "bibliography", "参考文献", "参考资料"}


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
    issues.extend(_inspect_heading_quality(text))
    issues.extend(_inspect_caption_quality(text))
    if citations and not _has_references_section(headings):
        issues.append(ManuscriptIssue(level="warning", message="Citation markers found but no References section"))
    if _has_references_section(headings):
        issues.extend(_inspect_references_quality(text))
    if not citations:
        issues.append(ManuscriptIssue(level="warning", message="No citation markers found"))
    if path.suffix.lower() == ".docx":
        issues.extend(_inspect_docx_package_quality(path, headings))
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
    for block in re.finditer(r"\[([^\]]*@[^]]+)\]", text):
        for match in re.finditer(r"@([A-Za-z0-9_:\-.]+)", block.group(1)):
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
    chinese_numbers = sorted({int(match.group(1)) for figure in figures if (match := re.match(r"图\s*(\d+)", figure))})
    if chinese_numbers:
        issues.extend(
            ManuscriptIssue(level="warning", message=f"Missing figure number in sequence: 图 {number}")
            for number in range(chinese_numbers[0], chinese_numbers[-1] + 1)
            if number not in chinese_numbers
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


def _inspect_heading_quality(text: str) -> list[ManuscriptIssue]:
    issues: list[ManuscriptIssue] = []
    previous_level = 0
    for line in text.splitlines():
        empty_match = re.match(r"^(#{1,6})\s*$", line)
        if empty_match:
            issues.append(ManuscriptIssue(level="warning", message=f"Empty heading: H{len(empty_match.group(1))}"))
            continue
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if not match:
            continue
        level = len(match.group(1))
        title = match.group(2).strip()
        if previous_level and level > previous_level + 1:
            issues.append(
                ManuscriptIssue(
                    level="warning",
                    message=f"Skipped heading level: H{previous_level} to H{level} at {title}",
                )
            )
        previous_level = level
    return issues


def _inspect_caption_quality(text: str) -> list[ManuscriptIssue]:
    issues: list[ManuscriptIssue] = []
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if re.search(r"!\[[^\]]*\]\([^)]+\)", line) and not _nearby_caption(lines, index, kind="figure"):
            issues.append(ManuscriptIssue(level="warning", message=f"Figure image missing caption near line {index + 1}"))
        if _is_markdown_table_start(lines, index) and not _nearby_caption(lines, index, kind="table"):
            issues.append(ManuscriptIssue(level="warning", message=f"Table missing caption near line {index + 1}"))
    return issues


def _nearby_caption(lines: list[str], index: int, *, kind: str) -> bool:
    start = max(0, index - 2)
    end = min(len(lines), index + 3)
    nearby = "\n".join(lines[start:end])
    if kind == "figure":
        return bool(re.search(r"\b(Figure|Fig\.)\s+\d+|图\s*\d+|鍥綷s*\d+", nearby, flags=re.IGNORECASE))
    return bool(re.search(r"\b(Table|Tab\.)\s+\d+|表\s*\d+", nearby, flags=re.IGNORECASE))


def _is_markdown_table_start(lines: list[str], index: int) -> bool:
    if index + 1 >= len(lines):
        return False
    header = lines[index].strip()
    separator = lines[index + 1].strip()
    if not (header.startswith("|") and header.endswith("|")):
        return False
    return bool(re.match(r"^\|[\s:\-|]+\|$", separator))


def _inspect_references_quality(text: str) -> list[ManuscriptIssue]:
    entries = _reference_entries(text)
    if entries and len(entries) < 3:
        return [ManuscriptIssue(level="warning", message=f"References section looks too short: {len(entries)} entries")]
    return []


def _reference_entries(text: str) -> list[str]:
    lines = text.splitlines()
    entries: list[str] = []
    in_references = False
    for line in lines:
        stripped = line.strip()
        heading_match = re.match(r"^#{1,6}\s+(.+?)\s*$", stripped)
        plain_heading = stripped if stripped and len(stripped) <= 80 else ""
        if heading_match or plain_heading:
            heading = heading_match.group(1).strip() if heading_match else plain_heading
            if _normalize_heading(heading) in REFERENCE_HEADINGS:
                in_references = True
                continue
            if in_references and heading_match:
                break
        if not in_references or not stripped:
            continue
        if stripped.startswith(("-", "*")) or re.match(r"^\[\d+\]|\d+\.", stripped):
            entries.append(stripped)
    return entries


def _has_required_section(required: str, headings: list[str]) -> bool:
    heading_keys = {_normalize_heading(heading) for heading in headings}
    aliases = SECTION_ALIASES.get(_normalize_heading(required), [required])
    return any(_normalize_heading(alias) in heading_keys for alias in aliases)


def _has_references_section(headings: list[str]) -> bool:
    heading_keys = {_normalize_heading(heading) for heading in headings}
    return any(_normalize_heading(heading) in REFERENCE_HEADINGS for heading in heading_keys)


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


def _inspect_docx_package_quality(path: Path, headings: list[str]) -> list[ManuscriptIssue]:
    issues: list[ManuscriptIssue] = []
    with zipfile.ZipFile(path) as package:
        names = set(package.namelist())
        document_xml = package.read("word/document.xml")
        styles_xml = package.read("word/styles.xml") if "word/styles.xml" in names else b""
        relationships_xml = package.read("word/_rels/document.xml.rels") if "word/_rels/document.xml.rels" in names else b""
        footnotes_xml = package.read("word/footnotes.xml") if "word/footnotes.xml" in names else b""
        endnotes_xml = package.read("word/endnotes.xml") if "word/endnotes.xml" in names else b""
        comments_xml = package.read("word/comments.xml") if "word/comments.xml" in names else b""
    if not styles_xml:
        issues.append(ManuscriptIssue(level="warning", message="DOCX styles.xml missing; cannot verify Word style definitions"))
    else:
        issues.extend(_inspect_docx_styles(document_xml, styles_xml))
    root = ElementTree.fromstring(document_xml)
    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    if root.find(".//w:sectPr/w:pgMar", namespace) is None:
        issues.append(ManuscriptIssue(level="warning", message="DOCX page margin settings missing"))
    page_size = root.find(".//w:sectPr/w:pgSz", namespace)
    if page_size is None:
        issues.append(ManuscriptIssue(level="warning", message="DOCX page size settings missing"))
    elif not page_size.attrib.get(f"{{{namespace['w']}}}w") or not page_size.attrib.get(f"{{{namespace['w']}}}h"):
        issues.append(ManuscriptIssue(level="warning", message="DOCX page size dimensions incomplete"))
    field_text = _docx_field_instruction_text(root)
    has_field_char = root.find(".//w:fldChar", namespace) is not None
    if not field_text and not has_field_char:
        issues.append(ManuscriptIssue(level="warning", message="No Word citation/reference fields detected"))
    if _has_references_section(headings) and "BIBLIOGRAPHY" not in field_text.upper():
        issues.append(ManuscriptIssue(level="warning", message="References section found but no Word bibliography field detected"))
    issues.extend(_inspect_docx_complex_fields(root))
    issues.extend(_inspect_docx_drawing_alt_text(root))
    issues.extend(_inspect_docx_image_targets(root, names, relationships_xml))
    issues.extend(_inspect_docx_review_marks(root, names))
    issues.extend(_inspect_docx_comment_references(root, comments_xml))
    issues.extend(_inspect_docx_header_footer_references(root, names, relationships_xml))
    issues.extend(_inspect_docx_note_references(root, footnotes_xml, endnotes_xml))
    issues.extend(_inspect_docx_hyperlink_references(root, relationships_xml))
    return issues


def _docx_field_instruction_text(root: ElementTree.Element) -> str:
    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    instructions = [node.text or "" for node in root.findall(".//w:instrText", namespace)]
    instructions.extend(
        node.attrib.get(f"{{{namespace['w']}}}instr", "")
        for node in root.findall(".//w:fldSimple", namespace)
    )
    return " ".join(instruction for instruction in instructions if instruction)


def _inspect_docx_complex_fields(root: ElementTree.Element) -> list[ManuscriptIssue]:
    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    field_characters = root.findall(".//w:fldChar", namespace)
    begin_count = sum(
        1
        for node in field_characters
        if node.attrib.get(f"{{{namespace['w']}}}fldCharType", "") == "begin"
    )
    end_count = sum(
        1
        for node in field_characters
        if node.attrib.get(f"{{{namespace['w']}}}fldCharType", "") == "end"
    )
    if begin_count != end_count:
        return [
            ManuscriptIssue(
                level="warning",
                message=f"DOCX complex field characters unbalanced: begin={begin_count}, end={end_count}",
            )
        ]
    return []


def _inspect_docx_hyperlink_references(root: ElementTree.Element, relationships_xml: bytes) -> list[ManuscriptIssue]:
    namespace = {
        "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
        "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    }
    relationships = _docx_relationship_targets(relationships_xml)
    bookmark_names = {
        node.attrib.get(f"{{{namespace['w']}}}name", "")
        for node in root.findall(".//w:bookmarkStart", namespace)
    }
    issues: list[ManuscriptIssue] = []
    for hyperlink in root.findall(".//w:hyperlink", namespace):
        relationship_id = hyperlink.attrib.get(f"{{{namespace['r']}}}id", "")
        anchor = hyperlink.attrib.get(f"{{{namespace['w']}}}anchor", "")
        if not relationship_id:
            if anchor and anchor not in bookmark_names:
                issues.append(ManuscriptIssue(level="warning", message=f"DOCX hyperlink anchor target missing: {anchor}"))
            continue
        target = relationships.get(relationship_id)
        if target is None:
            issues.append(ManuscriptIssue(level="warning", message=f"DOCX hyperlink relationship unresolved: {relationship_id}"))
        elif not target.strip():
            issues.append(ManuscriptIssue(level="warning", message=f"DOCX hyperlink target missing: {relationship_id}"))
    return issues


def _inspect_docx_note_references(
    root: ElementTree.Element,
    footnotes_xml: bytes,
    endnotes_xml: bytes,
) -> list[ManuscriptIssue]:
    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    issues: list[ManuscriptIssue] = []
    issues.extend(_inspect_docx_note_kind(root, footnotes_xml, "footnote", "footnoteReference", "footnote", namespace))
    issues.extend(_inspect_docx_note_kind(root, endnotes_xml, "endnote", "endnoteReference", "endnote", namespace))
    return issues


def _inspect_docx_note_kind(
    document_root: ElementTree.Element,
    notes_xml: bytes,
    note_label: str,
    reference_tag: str,
    target_tag: str,
    namespace: dict[str, str],
) -> list[ManuscriptIssue]:
    references = [
        node.attrib.get(f"{{{namespace['w']}}}id", "")
        for node in document_root.findall(f".//w:{reference_tag}", namespace)
    ]
    references = [note_id for note_id in references if note_id not in {"", "-1", "0"}]
    if not references:
        return []
    if not notes_xml:
        return [
            ManuscriptIssue(level="warning", message=f"DOCX {note_label} target missing: {note_id}")
            for note_id in sorted(set(references), key=int)
        ]
    notes_root = ElementTree.fromstring(notes_xml)
    target_ids = {
        node.attrib.get(f"{{{namespace['w']}}}id", "")
        for node in notes_root.findall(f".//w:{target_tag}", namespace)
    }
    return [
        ManuscriptIssue(level="warning", message=f"DOCX {note_label} target missing: {note_id}")
        for note_id in sorted(set(references), key=int)
        if note_id not in target_ids
    ]


def _inspect_docx_image_targets(
    root: ElementTree.Element,
    package_names: set[str],
    relationships_xml: bytes,
) -> list[ManuscriptIssue]:
    namespace = {
        "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
        "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    }
    relationships = _docx_relationship_targets(relationships_xml)
    issues: list[ManuscriptIssue] = []
    for blip in root.findall(".//a:blip", namespace):
        relationship_id = blip.attrib.get(f"{{{namespace['r']}}}embed", "")
        if not relationship_id:
            continue
        target = relationships.get(relationship_id)
        if not target:
            issues.append(ManuscriptIssue(level="warning", message=f"DOCX image relationship unresolved: {relationship_id}"))
            continue
        target_part = posixpath.normpath(posixpath.join("word", target))
        if target_part not in package_names:
            issues.append(ManuscriptIssue(level="warning", message=f"DOCX image target missing: {target_part}"))
    return issues


def _inspect_docx_header_footer_references(
    root: ElementTree.Element,
    package_names: set[str],
    relationships_xml: bytes,
) -> list[ManuscriptIssue]:
    namespace = {
        "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
        "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    }
    references = root.findall(".//w:headerReference", namespace) + root.findall(".//w:footerReference", namespace)
    if not references:
        return []
    relationships = _docx_relationship_targets(relationships_xml)
    issues: list[ManuscriptIssue] = []
    for reference in references:
        relationship_id = reference.attrib.get(f"{{{namespace['r']}}}id", "")
        if not relationship_id:
            issues.append(ManuscriptIssue(level="warning", message="DOCX header/footer reference missing relationship id"))
            continue
        target = relationships.get(relationship_id)
        if not target:
            issues.append(ManuscriptIssue(level="warning", message=f"DOCX header/footer relationship unresolved: {relationship_id}"))
            continue
        target_part = posixpath.normpath(posixpath.join("word", target))
        if target_part not in package_names:
            issues.append(ManuscriptIssue(level="warning", message=f"DOCX header/footer target missing: {target_part}"))
    return issues


def _docx_relationship_targets(relationships_xml: bytes) -> dict[str, str]:
    if not relationships_xml:
        return {}
    namespace = {"rel": "http://schemas.openxmlformats.org/package/2006/relationships"}
    root = ElementTree.fromstring(relationships_xml)
    return {
        relationship.attrib.get("Id", ""): relationship.attrib.get("Target", "")
        for relationship in root.findall(".//rel:Relationship", namespace)
    }


def _inspect_docx_drawing_alt_text(root: ElementTree.Element) -> list[ManuscriptIssue]:
    namespace = {"wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"}
    issues: list[ManuscriptIssue] = []
    for index, docpr in enumerate(root.findall(".//wp:docPr", namespace), start=1):
        description = docpr.attrib.get("descr", "").strip()
        title = docpr.attrib.get("title", "").strip()
        if description or title:
            continue
        name = docpr.attrib.get("name", "").strip() or f"drawing {index}"
        issues.append(ManuscriptIssue(level="warning", message=f"DOCX image/drawing missing alt text: {name}"))
    return issues


def _inspect_docx_review_marks(root: ElementTree.Element, package_names: set[str]) -> list[ManuscriptIssue]:
    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    insertions = len(root.findall(".//w:ins", namespace))
    deletions = len(root.findall(".//w:del", namespace))
    comment_markers = len(root.findall(".//w:commentRangeStart", namespace))
    if not comment_markers and "word/comments.xml" in package_names:
        comment_markers = len(root.findall(".//w:commentReference", namespace))

    issues: list[ManuscriptIssue] = []
    if insertions or deletions:
        issues.append(
            ManuscriptIssue(
                level="warning",
                message=f"DOCX tracked changes detected: insertions={insertions}, deletions={deletions}",
            )
        )
    if comment_markers:
        suffix = "marker" if comment_markers == 1 else "markers"
        issues.append(ManuscriptIssue(level="warning", message=f"DOCX comments detected: {comment_markers} comment {suffix}"))
    return issues


def _inspect_docx_comment_references(root: ElementTree.Element, comments_xml: bytes) -> list[ManuscriptIssue]:
    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    references = {
        node.attrib.get(f"{{{namespace['w']}}}id", "")
        for node in root.findall(".//w:commentRangeStart", namespace) + root.findall(".//w:commentReference", namespace)
    }
    references.discard("")
    if not references:
        return []
    if not comments_xml:
        target_ids: set[str] = set()
    else:
        comments_root = ElementTree.fromstring(comments_xml)
        target_ids = {
            node.attrib.get(f"{{{namespace['w']}}}id", "")
            for node in comments_root.findall(".//w:comment", namespace)
        }
    missing = sorted(references - target_ids, key=_docx_id_sort_key)
    return [
        ManuscriptIssue(level="warning", message=f"DOCX comment target missing: {comment_id}")
        for comment_id in missing
    ]


def _docx_id_sort_key(value: str) -> tuple[int, int | str]:
    return (0, int(value)) if value.lstrip("-").isdigit() else (1, value)


def _inspect_docx_styles(document_xml: bytes, styles_xml: bytes) -> list[ManuscriptIssue]:
    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    document_root = ElementTree.fromstring(document_xml)
    styles_root = ElementTree.fromstring(styles_xml)
    style_ids = {
        node.attrib.get(f"{{{namespace['w']}}}styleId", "")
        for node in styles_root.findall(".//w:style", namespace)
    }
    used_styles = {
        node.attrib.get(f"{{{namespace['w']}}}val", "")
        for node in document_root.findall(".//w:pStyle", namespace)
    }
    missing = sorted(style for style in used_styles if style and style not in style_ids)
    return [
        ManuscriptIssue(level="warning", message=f"DOCX paragraph style is used but not defined: {style}")
        for style in missing
    ]
