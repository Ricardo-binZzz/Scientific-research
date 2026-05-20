from __future__ import annotations

import json
import re
from html import unescape
from pathlib import Path
from urllib.parse import quote_plus, urlparse
from urllib.request import Request, urlopen

from workflow.library import LibraryEntry, LibraryIndex


def discover_crossref(query: str, limit: int = 10, opener=urlopen) -> LibraryIndex:
    """Search Crossref open metadata and map results into local library entries."""
    safe_limit = max(1, min(limit, 50))
    url = f"https://api.crossref.org/works?query={quote_plus(query)}&rows={safe_limit}"
    request = Request(url, headers={"User-Agent": "research-workflow/0.1 (mailto:local@example.com)"})
    with opener(request, timeout=20) as response:
        payload = json.loads(response.read().decode("utf-8"))
    entries = [_crossref_item_to_entry(item) for item in payload.get("message", {}).get("items", [])]
    return LibraryIndex(entries=[entry for entry in entries if entry is not None])


def download_pdf_from_url(url: str, out_dir: Path, filename: str = "", opener=urlopen) -> Path:
    """Download a direct/open PDF URL without bypassing paywalls or access controls."""
    if not url.lower().startswith(("http://", "https://")):
        raise ValueError("PDF URL must start with http:// or https://")
    request = Request(url, headers={"User-Agent": "research-workflow/0.1"})
    with opener(request, timeout=30) as response:
        body = response.read()
        content_type = response.headers.get("Content-Type", "").lower()
    if "pdf" not in content_type and not body.startswith(b"%PDF"):
        raise ValueError("URL did not return a PDF response")
    out_dir.mkdir(parents=True, exist_ok=True)
    safe_name = _safe_pdf_filename(filename or Path(urlparse(url).path).name or "downloaded-paper.pdf")
    path = out_dir / safe_name
    path.write_bytes(body)
    return path


def render_discovery_results(index: LibraryIndex) -> str:
    lines = ["# Literature Discovery Results", ""]
    if not index.entries:
        return "# Literature Discovery Results\n\n- None"
    for entry in index.entries:
        lines.extend(
            [
                f"- Title: {entry.title}",
                f"  - Authors: {'; '.join(entry.authors)}",
                f"  - Year: {entry.year}",
                f"  - Source: {entry.source}",
                f"  - DOI: {entry.doi}",
                f"  - URL: {entry.url}",
                f"  - Database: {entry.database_source}",
                "",
            ]
        )
    return "\n".join(lines).rstrip()


def _crossref_item_to_entry(item: dict) -> LibraryEntry | None:
    title = _first(item.get("title"))
    doi = str(item.get("DOI", "")).strip()
    if not title or not doi:
        return None
    authors = [
        " ".join(part for part in [author.get("given", ""), author.get("family", "")] if part).strip()
        for author in item.get("author", [])
    ]
    authors = [author for author in authors if author]
    year = _published_year(item)
    source = _first(item.get("container-title")) or _first(item.get("publisher")) or "Unknown source"
    abstract = _strip_tags(str(item.get("abstract", "")))
    return LibraryEntry(
        title=title,
        authors=authors,
        year=year,
        source=source,
        doi=doi,
        pdf_name="",
        note_path="",
        abstract=abstract,
        url=str(item.get("URL", "")).strip(),
        database_source="Crossref",
    )


def _published_year(item: dict) -> int:
    for key in ("published-print", "published-online", "published", "issued"):
        parts = item.get(key, {}).get("date-parts", [])
        if parts and parts[0]:
            return int(parts[0][0])
    return 0


def _first(value) -> str:
    if isinstance(value, list) and value:
        return str(value[0]).strip()
    return str(value or "").strip()


def _strip_tags(value: str) -> str:
    return unescape(re.sub(r"<[^>]+>", "", value)).strip()


def _safe_pdf_filename(value: str) -> str:
    name = Path(value).name
    if not name.lower().endswith(".pdf"):
        name += ".pdf"
    return re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-") or "downloaded-paper.pdf"
