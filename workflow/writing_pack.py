from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from workflow.library import load_index
from workflow.simulation import collect_export_files


@dataclass(frozen=True)
class WritingPack:
    root: Path
    library_titles: list[str]
    note_files: list[str]
    figure_bundles: list[str]
    simulation_exports: list[str]


def build_writing_pack(root: Path) -> WritingPack:
    return WritingPack(
        root=root,
        library_titles=[entry.title for entry in load_index(root / "literature").entries],
        note_files=_names(root / "notes", {".md"}),
        figure_bundles=_figure_bundle_stems(root / "figures"),
        simulation_exports=[path.name for path in collect_export_files(root / "simulation")] if (root / "simulation").exists() else [],
    )


def render_writing_pack(pack: WritingPack) -> str:
    lines = ["# Writing Pack", "", f"- Root: {pack.root}", ""]
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
