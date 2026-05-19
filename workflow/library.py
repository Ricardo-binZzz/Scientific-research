from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass, asdict
from io import StringIO
from pathlib import Path


INDEX_FILENAME = "library-index.json"


@dataclass(frozen=True)
class LibraryEntry:
    title: str
    authors: list[str]
    year: int
    source: str
    doi: str
    pdf_name: str
    note_path: str


@dataclass(frozen=True)
class LibraryIndex:
    entries: list[LibraryEntry]

    def save(self, root: Path) -> Path:
        root.mkdir(parents=True, exist_ok=True)
        path = root / INDEX_FILENAME
        payload = {"entries": [asdict(entry) for entry in self.entries]}
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return path


@dataclass(frozen=True)
class PdfInventoryReport:
    present_pdf_names: list[str]
    missing_pdf_names: list[str]


@dataclass(frozen=True)
class NoteInventoryReport:
    present_note_paths: list[str]
    missing_note_paths: list[str]


@dataclass(frozen=True)
class LibraryStats:
    total_entries: int
    year_min: int | None
    year_max: int | None
    missing_pdf_count: int
    source_counts: dict[str, int]
    author_counts: dict[str, int]


def load_index(root: Path) -> LibraryIndex:
    path = root / INDEX_FILENAME
    if not path.exists():
        return LibraryIndex(entries=[])
    payload = json.loads(path.read_text(encoding="utf-8"))
    entries = [
        LibraryEntry(
            title=item["title"],
            authors=list(item.get("authors", [])),
            year=int(item["year"]),
            source=item["source"],
            doi=item["doi"],
            pdf_name=item["pdf_name"],
            note_path=item["note_path"],
        )
        for item in payload.get("entries", [])
    ]
    return LibraryIndex(entries=entries)


def add_entry(root: Path, index: LibraryIndex, entry: LibraryEntry) -> LibraryIndex:
    entries = _merge_existing_entries(load_index(root).entries, index.entries)
    if any(_same_entry(item, entry) for item in entries):
        updated = LibraryIndex(entries=entries)
        updated.save(root)
        return updated
    entries.append(entry)
    updated = LibraryIndex(entries=entries)
    updated.save(root)
    return updated


def render_index(index: LibraryIndex) -> str:
    lines = ["# Literature Library", ""]
    for entry in index.entries:
        lines.extend(
            [
                f"- Title: {entry.title}",
                f"  - Authors: {'; '.join(entry.authors)}",
                f"  - Year: {entry.year}",
                f"  - Source: {entry.source}",
                f"  - DOI: {entry.doi}",
                f"  - PDF: {entry.pdf_name}",
                f"  - Note: {entry.note_path}",
                "",
            ]
        )
    return "\n".join(lines)


def inspect_pdf_inventory(root: Path, index: LibraryIndex) -> PdfInventoryReport:
    present: list[str] = []
    missing: list[str] = []
    for entry in index.entries:
        if not entry.pdf_name:
            missing.append(entry.pdf_name)
            continue
        if (root / entry.pdf_name).exists():
            present.append(entry.pdf_name)
        else:
            missing.append(entry.pdf_name)
    return PdfInventoryReport(present_pdf_names=present, missing_pdf_names=missing)


def render_pdf_inventory_report(report: PdfInventoryReport) -> str:
    lines = ["# PDF Inventory Report", ""]
    lines.append("## Present")
    lines.extend([f"- {name}" for name in report.present_pdf_names] or ["- None"])
    lines.append("")
    lines.append("## Missing")
    lines.extend([f"- {name}" for name in report.missing_pdf_names] or ["- None"])
    lines.append("")
    return "\n".join(lines)


def inspect_note_inventory(root: Path, index: LibraryIndex) -> NoteInventoryReport:
    present: list[str] = []
    missing: list[str] = []
    for entry in index.entries:
        if not entry.note_path:
            missing.append(entry.note_path)
            continue
        if _resolve_note_path(root, entry.note_path).exists():
            present.append(entry.note_path)
        else:
            missing.append(entry.note_path)
    return NoteInventoryReport(present_note_paths=present, missing_note_paths=missing)


def render_note_inventory_report(report: NoteInventoryReport) -> str:
    lines = ["# Note Inventory Report", ""]
    lines.append("## Present")
    lines.extend([f"- {path}" for path in report.present_note_paths] or ["- None"])
    lines.append("")
    lines.append("## Missing")
    lines.extend([f"- {path}" for path in report.missing_note_paths] or ["- None"])
    lines.append("")
    return "\n".join(lines)


def inspect_library_stats(root: Path, index: LibraryIndex) -> LibraryStats:
    years = [entry.year for entry in index.entries if entry.year > 0]
    source_counts: dict[str, int] = {}
    author_counts: dict[str, int] = {}
    for entry in index.entries:
        source = entry.source or "Unknown"
        source_counts[source] = source_counts.get(source, 0) + 1
        for author in entry.authors:
            author_counts[author] = author_counts.get(author, 0) + 1
    pdf_report = inspect_pdf_inventory(root, index)
    return LibraryStats(
        total_entries=len(index.entries),
        year_min=min(years) if years else None,
        year_max=max(years) if years else None,
        missing_pdf_count=len(pdf_report.missing_pdf_names),
        source_counts=dict(sorted(source_counts.items(), key=lambda item: (-item[1], item[0]))),
        author_counts=dict(sorted(author_counts.items(), key=lambda item: (-item[1], item[0]))),
    )


def render_library_stats(stats: LibraryStats) -> str:
    year_range = f"{stats.year_min}-{stats.year_max}" if stats.year_min is not None and stats.year_max is not None else "None"
    lines = ["# Library Stats", ""]
    lines.append(f"- Total entries: {stats.total_entries}")
    lines.append(f"- Year range: {year_range}")
    lines.append(f"- Missing PDFs: {stats.missing_pdf_count}")
    lines.append("")
    lines.append("## Sources")
    if not stats.source_counts:
        lines.append("- None")
    else:
        lines.extend(f"- {source}: {count}" for source, count in stats.source_counts.items())
    lines.append("")
    lines.append("## Authors")
    if not stats.author_counts:
        lines.append("- None")
    else:
        lines.extend(f"- {author}: {count}" for author, count in stats.author_counts.items())
    lines.append("")
    return "\n".join(lines)


def search_library(index: LibraryIndex, query: str) -> list[LibraryEntry]:
    needle = query.strip().lower()
    if not needle:
        return []
    return [entry for entry in index.entries if _entry_matches_query(entry, needle)]


def render_search_results(entries: list[LibraryEntry]) -> str:
    lines = ["# Library Search Results", ""]
    if not entries:
        lines.append("- No matching entries")
        lines.append("")
        return "\n".join(lines)
    for entry in entries:
        lines.extend(
            [
                f"- Title: {entry.title}",
                f"  - Authors: {'; '.join(entry.authors)}",
                f"  - Year: {entry.year}",
                f"  - Source: {entry.source}",
                f"  - DOI: {entry.doi}",
                f"  - PDF: {entry.pdf_name}",
                f"  - Note: {entry.note_path}",
                "",
            ]
        )
    return "\n".join(lines)


def export_bibtex(index: LibraryIndex) -> str:
    entries: list[str] = []
    used_keys: set[str] = set()
    for entry in index.entries:
        citekey = make_citekey(entry)
        unique_key = _unique_citekey(citekey, used_keys)
        used_keys.add(unique_key)
        entries.append(
            "\n".join(
                [
                    f"@article{{{unique_key},",
                    f"  title = {{{_escape_bibtex(entry.title)}}},",
                    f"  author = {{{_escape_bibtex(' and '.join(entry.authors))}}},",
                    f"  journal = {{{_escape_bibtex(entry.source)}}},",
                    f"  year = {{{entry.year}}},",
                    f"  doi = {{{_escape_bibtex(entry.doi)}}},",
                    f"  file = {{{_escape_bibtex(entry.pdf_name)}}},",
                    f"  note = {{{_escape_bibtex(entry.note_path)}}}",
                    "}",
                ]
            )
        )
    return "\n\n".join(entries) + ("\n" if entries else "")


def import_bibtex(text: str) -> LibraryIndex:
    entries: list[LibraryEntry] = []
    for match in re.finditer(r"@article\s*\{[^,]+,(.*?)\n\}", text, flags=re.IGNORECASE | re.DOTALL):
        fields = _parse_bibtex_fields(match.group(1))
        title = fields.get("title", "")
        authors = [item.strip() for item in fields.get("author", "").split(" and ") if item.strip()]
        source = fields.get("journal", fields.get("booktitle", ""))
        year = int(fields.get("year", "0") or 0)
        doi = fields.get("doi", "")
        pdf_name = fields.get("file", "")
        note_path = fields.get("note", "")
        entries.append(
            LibraryEntry(
                title=title,
                authors=authors,
                year=year,
                source=source,
                doi=doi,
                pdf_name=pdf_name,
                note_path=note_path,
            )
        )
    return LibraryIndex(entries=_merge_existing_entries(entries))


def import_csv_metadata(text: str) -> LibraryIndex:
    reader = csv.DictReader(StringIO(text.lstrip("\ufeff")))
    entries: list[LibraryEntry] = []
    for row in reader:
        title = _first_csv_value(row, "title", "document title", "article title")
        if not title:
            continue
        entries.append(
            LibraryEntry(
                title=title,
                authors=_parse_csv_authors(
                    _first_csv_value(row, "authors", "author full names", "author names", "author")
                ),
                year=_parse_year(_first_csv_value(row, "year", "publication year", "pubyear")),
                source=_first_csv_value(
                    row, "source title", "publication name", "journal title", "journal", "publication title", "source"
                ),
                doi=_first_csv_value(row, "doi"),
                pdf_name=_first_csv_value(row, "pdf", "file", "pdf name", "pdf_name"),
                note_path=_first_csv_value(row, "notes", "note", "note path", "note_path"),
            )
        )
    return LibraryIndex(entries=_merge_existing_entries(entries))


def make_citekey(entry: LibraryEntry) -> str:
    author = entry.authors[0] if entry.authors else "unknown"
    author_key = re.sub(r"[^a-z0-9]", "", author.lower()) or "unknown"
    title_words = re.findall(r"[A-Za-z0-9]+", entry.title.lower())
    title_word = title_words[0] if title_words else "entry"
    return f"{author_key}{entry.year}{title_word}"


def _same_entry(left: LibraryEntry, right: LibraryEntry) -> bool:
    if left.doi and right.doi:
        return left.doi == right.doi
    return _normalize_title(left.title) == _normalize_title(right.title)


def _entry_matches_query(entry: LibraryEntry, needle: str) -> bool:
    haystack = " ".join([entry.title, *entry.authors, entry.source, entry.doi]).lower()
    return needle in haystack


def _resolve_note_path(root: Path, note_path: str) -> Path:
    path = Path(note_path)
    if path.is_absolute():
        return path
    project_root = root.parent if root.name == "literature" else root
    return project_root / path


def _normalize_title(title: str) -> str:
    return re.sub(r"\s+", " ", title.strip().lower())


def _merge_existing_entries(*entry_groups: list[LibraryEntry]) -> list[LibraryEntry]:
    merged: list[LibraryEntry] = []
    for entries in entry_groups:
        for entry in entries:
            if not any(_same_entry(existing, entry) for existing in merged):
                merged.append(entry)
    return merged


def _unique_citekey(base: str, used_keys: set[str]) -> str:
    if base not in used_keys:
        return base
    counter = 2
    while f"{base}{counter}" in used_keys:
        counter += 1
    return f"{base}{counter}"


def _escape_bibtex(value: str) -> str:
    return value.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")


def _parse_bibtex_fields(body: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for match in re.finditer(r"([A-Za-z]+)\s*=\s*\{([^{}]*)\}\s*,?", body):
        fields[match.group(1).lower()] = match.group(2).strip()
    return fields


def _first_csv_value(row: dict[str, str], *names: str) -> str:
    normalized = {_normalize_csv_header(key): value for key, value in row.items() if key is not None}
    for name in names:
        value = normalized.get(_normalize_csv_header(name), "")
        if value:
            return value.strip()
    return ""


def _normalize_csv_header(header: str) -> str:
    return re.sub(r"[\s_-]+", " ", header.strip().lower())


def _parse_csv_authors(value: str) -> list[str]:
    if not value:
        return []
    parts = re.split(r"\s*(?:;|\band\b)\s*", value)
    return [part.strip() for part in parts if part.strip()]


def _parse_year(value: str) -> int:
    match = re.search(r"\d{4}", value)
    return int(match.group(0)) if match else 0
