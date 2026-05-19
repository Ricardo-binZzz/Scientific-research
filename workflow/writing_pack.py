from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from workflow.library import inspect_library_stats, load_index
from workflow.simulation import collect_export_files


@dataclass(frozen=True)
class WritingPack:
    root: Path
    library_total_entries: int
    library_year_range: str
    library_missing_pdf_count: int
    library_titles: list[str]
    note_files: list[str]
    figure_bundles: list[str]
    simulation_exports: list[str]


def build_writing_pack(root: Path) -> WritingPack:
    library_root = root / "literature"
    library_index = load_index(library_root)
    library_stats = inspect_library_stats(library_root, library_index)
    return WritingPack(
        root=root,
        library_total_entries=library_stats.total_entries,
        library_year_range=_year_range(library_stats.year_min, library_stats.year_max),
        library_missing_pdf_count=library_stats.missing_pdf_count,
        library_titles=[entry.title for entry in library_index.entries],
        note_files=_names(root / "notes", {".md"}),
        figure_bundles=_figure_bundle_stems(root / "figures"),
        simulation_exports=[path.name for path in collect_export_files(root / "simulation")] if (root / "simulation").exists() else [],
    )


def render_writing_pack(pack: WritingPack) -> str:
    lines = ["# Writing Pack", "", f"- Root: {pack.root}", ""]
    lines.append("## Library Overview")
    lines.append(f"- Total entries: {pack.library_total_entries}")
    lines.append(f"- Year range: {pack.library_year_range}")
    lines.append(f"- Missing PDFs: {pack.library_missing_pdf_count}")
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
