from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from workflow.library import inspect_library_stats, inspect_note_inventory, inspect_pdf_inventory, load_index
from workflow.simulation import collect_export_files


RECENT_LITERATURE_YEAR = 2020


@dataclass(frozen=True)
class WritingPack:
    root: Path
    library_total_entries: int
    library_year_range: str
    library_missing_pdf_count: int
    recent_library_titles: list[str]
    missing_pdf_names: list[str]
    missing_note_paths: list[str]
    library_titles: list[str]
    note_files: list[str]
    figure_bundles: list[str]
    simulation_exports: list[str]
    manuscript_files: list[str]


def build_writing_pack(root: Path) -> WritingPack:
    library_root = root / "literature"
    library_index = load_index(library_root)
    library_stats = inspect_library_stats(library_root, library_index)
    pdf_report = inspect_pdf_inventory(library_root, library_index)
    note_report = inspect_note_inventory(library_root, library_index)
    return WritingPack(
        root=root,
        library_total_entries=library_stats.total_entries,
        library_year_range=_year_range(library_stats.year_min, library_stats.year_max),
        library_missing_pdf_count=library_stats.missing_pdf_count,
        recent_library_titles=[entry.title for entry in library_index.entries if entry.year >= RECENT_LITERATURE_YEAR],
        missing_pdf_names=pdf_report.missing_pdf_names,
        missing_note_paths=note_report.missing_note_paths,
        library_titles=[entry.title for entry in library_index.entries],
        note_files=_names(root / "notes", {".md"}),
        figure_bundles=_figure_bundle_stems(root / "figures"),
        simulation_exports=[path.name for path in collect_export_files(root / "simulation")] if (root / "simulation").exists() else [],
        manuscript_files=_names(root / "manuscript", {".md", ".txt", ".docx"}),
    )


def render_writing_pack(pack: WritingPack) -> str:
    lines = ["# Writing Pack", "", f"- Root: {pack.root}", ""]
    lines.append("## Library Overview")
    lines.append(f"- Total entries: {pack.library_total_entries}")
    lines.append(f"- Year range: {pack.library_year_range}")
    lines.append(f"- Missing PDFs: {pack.library_missing_pdf_count}")
    lines.append("")
    lines.append(f"## Recent Literature (since {RECENT_LITERATURE_YEAR})")
    lines.extend([f"- {title}" for title in pack.recent_library_titles] or ["- None"])
    lines.append("")
    lines.append("## Library Gaps")
    lines.append(f"- Missing PDFs: {', '.join(pack.missing_pdf_names) if pack.missing_pdf_names else 'None'}")
    lines.append(f"- Missing notes: {', '.join(pack.missing_note_paths) if pack.missing_note_paths else 'None'}")
    lines.append("")
    lines.append("## Literature")
    lines.extend([f"- {title}" for title in pack.library_titles] or ["- None"])
    lines.append("")
    lines.append("## Notes")
    lines.extend([f"- {name}" for name in pack.note_files] or ["- None"])
    lines.append("")
    lines.append("## Figures")
    lines.extend([f"- {stem}" for stem in pack.figure_bundles] or ["- None"])
    lines.append("")
    lines.append("## Simulation Data")
    lines.extend([f"- {name}" for name in pack.simulation_exports] or ["- None"])
    lines.append("")
    lines.append("## Manuscript Drafts")
    lines.extend([f"- {name}" for name in pack.manuscript_files] or ["- None"])
    lines.append("")
    return "\n".join(lines)


def _names(root: Path, suffixes: set[str]) -> list[str]:
    if not root.exists():
        return []
    return sorted(path.name for path in root.iterdir() if path.is_file() and path.suffix.lower() in suffixes)


def _figure_bundle_stems(root: Path) -> list[str]:
    if not root.exists():
        return []
    stems = sorted(path.stem for path in root.iterdir() if path.is_file() and path.suffix.lower() == ".svg")
    return [stem for stem in stems if (root / f"{stem}.json").exists()]


def _year_range(year_min: int | None, year_max: int | None) -> str:
    if year_min is None or year_max is None:
        return "None"
    return f"{year_min}-{year_max}"
