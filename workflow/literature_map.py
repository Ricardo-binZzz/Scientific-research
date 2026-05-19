from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from workflow.library import load_index


@dataclass(frozen=True)
class LiteratureMap:
    root: Path
    year_counts: dict[int, int]
    source_counts: dict[str, int]
    author_counts: dict[str, int]
    author_links: dict[str, list[str]]


def build_literature_map(root: Path) -> LiteratureMap:
    index = load_index(root)
    year_counts: dict[int, int] = {}
    source_counts: dict[str, int] = {}
    author_counts: dict[str, int] = {}
    author_links: dict[str, list[str]] = {}
    for entry in index.entries:
        if entry.year > 0:
            year_counts[entry.year] = year_counts.get(entry.year, 0) + 1
        source = entry.source or "Unknown"
        source_counts[source] = source_counts.get(source, 0) + 1
        for author in entry.authors:
            author_counts[author] = author_counts.get(author, 0) + 1
            author_links.setdefault(author, []).append(entry.title)
    return LiteratureMap(
        root=root,
        year_counts=dict(sorted(year_counts.items(), reverse=True)),
        source_counts=dict(sorted(source_counts.items(), key=lambda item: (-item[1], item[0]))),
        author_counts=dict(sorted(author_counts.items(), key=lambda item: (-item[1], item[0]))),
        author_links=dict(sorted(author_links.items())),
    )


def render_literature_map(literature_map: LiteratureMap) -> str:
    lines = ["# Literature Map", "", f"- Library root: {literature_map.root}", ""]
    lines.append("## Years")
    lines.extend([f"- {year}: {count}" for year, count in literature_map.year_counts.items()] or ["- None"])
    lines.append("")
    lines.append("## Sources")
    lines.extend([f"- {source}: {count}" for source, count in literature_map.source_counts.items()] or ["- None"])
    lines.append("")
    lines.append("## Authors")
    lines.extend([f"- {author}: {count}" for author, count in literature_map.author_counts.items()] or ["- None"])
    lines.append("")
    lines.append("## Author Links")
    lines.extend([f"- {author}: {', '.join(titles)}" for author, titles in literature_map.author_links.items()] or ["- None"])
    lines.append("")
    return "\n".join(lines)
