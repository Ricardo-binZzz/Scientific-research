from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


TRACKER_FILENAME = "literature-tracker.json"


@dataclass(frozen=True)
class LiteratureTopic:
    name: str
    keywords: list[str]
    sources: list[str]
    last_checked: str
    search_query: str


@dataclass(frozen=True)
class LiteratureTracker:
    root: Path
    topics: list[LiteratureTopic]


def build_literature_tracker(root: Path) -> LiteratureTracker:
    path = root / TRACKER_FILENAME
    if not path.exists():
        return LiteratureTracker(root=root, topics=[])
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    topics = [
        LiteratureTopic(
            name=str(item.get("name", "")),
            keywords=[str(keyword) for keyword in item.get("keywords", [])],
            sources=[str(source) for source in item.get("sources", [])],
            last_checked=str(item.get("last_checked", "")),
            search_query=_build_query([str(keyword) for keyword in item.get("keywords", [])]),
        )
        for item in payload.get("topics", [])
    ]
    return LiteratureTracker(root=root, topics=topics)


def render_literature_tracker(tracker: LiteratureTracker) -> str:
    lines = ["# Literature Tracking Plan", "", f"- Root: {tracker.root}", ""]
    if not tracker.topics:
        lines.append("No tracked topics. Edit literature-tracker.json to add topics.")
        lines.append("")
        return "\n".join(lines)
    for topic in tracker.topics:
        lines.append(f"## {topic.name}")
        lines.append(f"- Query: {topic.search_query}")
        lines.append(f"- Keywords: {', '.join(topic.keywords) if topic.keywords else 'None'}")
        lines.append(f"- Sources: {', '.join(topic.sources) if topic.sources else 'None'}")
        lines.append(f"- Last checked: {topic.last_checked or 'Never'}")
        lines.append("- Next action: rerun this query, save the search-log note, then add useful papers to the library.")
        lines.append("")
    return "\n".join(lines)


def _build_query(keywords: list[str]) -> str:
    parts = []
    for keyword in keywords:
        value = keyword.strip()
        if not value:
            continue
        parts.append(f'"{value}"' if " " in value else value)
    return " OR ".join(parts)
