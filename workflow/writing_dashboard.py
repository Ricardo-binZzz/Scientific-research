from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from workflow.literature_table import build_literature_table
from workflow.writing_pack import build_writing_pack


@dataclass(frozen=True)
class WritingDashboard:
    root: Path
    recent_literature_count: int
    summary_note_count: int
    figure_bundles: list[str]
    simulation_exports: list[str]
    manuscript_files: list[str]
    gaps: list[str]
    abstract_ready_count: int
    top_keywords: list[str]
    high_citation_count: int


def build_writing_dashboard(root: Path) -> WritingDashboard:
    pack = build_writing_pack(root)
    literature_table = build_literature_table(root / "notes")
    gaps: list[str] = []
    if pack.missing_pdf_names:
        gaps.append(f"Missing PDFs: {', '.join(pack.missing_pdf_names)}")
    if pack.missing_note_paths:
        gaps.append(f"Missing notes: {', '.join(pack.missing_note_paths)}")
    if not pack.manuscript_files:
        gaps.append("No manuscript drafts found")
    return WritingDashboard(
        root=root,
        recent_literature_count=len(pack.recent_library_titles),
        summary_note_count=len(literature_table.rows),
        figure_bundles=pack.figure_bundles,
        simulation_exports=pack.simulation_exports,
        manuscript_files=pack.manuscript_files,
        gaps=gaps,
        abstract_ready_count=len(pack.abstract_ready_titles),
        top_keywords=[f"{keyword} ({count})" for keyword, count in list(pack.keyword_counts.items())[:5]],
        high_citation_count=len(pack.top_cited_literature),
    )


def render_writing_dashboard(dashboard: WritingDashboard) -> str:
    lines = ["# Writing Dashboard", "", f"- Root: {dashboard.root}", ""]
    lines.append("## Ready for Background")
    lines.append(f"- Recent literature items: {dashboard.recent_literature_count}")
    lines.append(f"- Paper summary notes: {dashboard.summary_note_count}")
    lines.append(f"- Abstract-ready literature: {dashboard.abstract_ready_count}")
    lines.append(f"- High-citation candidates: {dashboard.high_citation_count}")
    lines.append(f"- Top keywords: {', '.join(dashboard.top_keywords) if dashboard.top_keywords else 'None'}")
    lines.append("")
    lines.append("## Ready for Methods")
    lines.extend([f"- Simulation export: {name}" for name in dashboard.simulation_exports] or ["- No simulation exports"])
    lines.append("")
    lines.append("## Ready for Results")
    lines.extend([f"- Figure bundle: {name}" for name in dashboard.figure_bundles] or ["- No figure bundles"])
    lines.append("")
    lines.append("## Manuscript Drafts")
    lines.extend([f"- {name}" for name in dashboard.manuscript_files] or ["- None"])
    lines.append("")
    lines.append("## Gaps to Fix")
    lines.extend([f"- {gap}" for gap in dashboard.gaps] or ["- None"])
    lines.append("")
    return "\n".join(lines)
