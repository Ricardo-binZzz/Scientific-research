from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from workflow.library import inspect_note_inventory, inspect_pdf_inventory, load_index
from workflow.manuscript import inspect_manuscript
from workflow.python.sim_result_loader import load_tabular_result
from workflow.simulation import check_dataset_ranges, collect_export_files, load_unit_metadata, validate_dataset_columns


@dataclass(frozen=True)
class ProjectReport:
    root: Path
    library_entries: int
    note_files: int
    figure_bundles: int
    simulation_exports: int
    manuscript_files: int


@dataclass(frozen=True)
class ProjectCheck:
    root: Path
    summary: ProjectReport
    library_entries: int
    missing_pdf_names: list[str]
    missing_note_paths: list[str]
    simulation_issues: list[str]
    manuscript_issues: list[str]


def build_project_report(root: Path) -> ProjectReport:
    literature = root / "literature"
    notes = root / "notes"
    figures = root / "figures"
    simulation = root / "simulation"
    manuscript = root / "manuscript"
    return ProjectReport(
        root=root,
        library_entries=len(load_index(literature).entries),
        note_files=_count_files(notes, {".md"}),
        figure_bundles=_count_figure_bundles(figures),
        simulation_exports=len(collect_export_files(simulation)) if simulation.exists() else 0,
        manuscript_files=_count_files(manuscript, {".md", ".txt", ".docx"}),
    )


def build_project_check(root: Path) -> ProjectCheck:
    config = _load_project_check_config(root)
    literature = root / "literature"
    library_index = load_index(literature)
    pdf_report = inspect_pdf_inventory(literature, library_index)
    note_report = inspect_note_inventory(literature, library_index)
    simulation_issues = _inspect_simulation(root, config.get("simulation", {}))
    manuscript_issues = _inspect_manuscripts(root, config.get("manuscript", {}), library_index)
    return ProjectCheck(
        root=root,
        summary=build_project_report(root),
        library_entries=len(library_index.entries),
        missing_pdf_names=pdf_report.missing_pdf_names,
        missing_note_paths=note_report.missing_note_paths,
        simulation_issues=simulation_issues,
        manuscript_issues=manuscript_issues,
    )


def render_project_report(report: ProjectReport) -> str:
    return "\n".join(
        [
            "# Project Status Report",
            "",
            f"- Root: {report.root}",
            f"- Library entries: {report.library_entries}",
            f"- Note files: {report.note_files}",
            f"- Figure bundles: {report.figure_bundles}",
            f"- Simulation exports: {report.simulation_exports}",
            f"- Manuscript files: {report.manuscript_files}",
            "",
        ]
    )


def render_project_check(check: ProjectCheck) -> str:
    lines = ["# Project Check Report", "", f"- Root: {check.root}", ""]
    lines.append("## Literature")
    lines.append(f"- Library entries: {check.library_entries}")
    lines.append(f"- Missing PDFs: {', '.join(check.missing_pdf_names) if check.missing_pdf_names else 'None'}")
    lines.append(f"- Missing notes: {', '.join(check.missing_note_paths) if check.missing_note_paths else 'None'}")
    lines.append("")
    lines.append("## Simulation")
    lines.extend([f"- {issue}" for issue in check.simulation_issues] or ["- None"])
    lines.append("")
    lines.append("## Manuscript")
    lines.extend([f"- {issue}" for issue in check.manuscript_issues] or ["- None"])
    lines.append("")
    lines.append("## Project Summary")
    lines.append(f"- Note files: {check.summary.note_files}")
    lines.append(f"- Figure bundles: {check.summary.figure_bundles}")
    lines.append(f"- Simulation exports: {check.summary.simulation_exports}")
    lines.append(f"- Manuscript files: {check.summary.manuscript_files}")
    lines.append("")
    lines.append("## Next Actions")
    lines.extend(f"- {action}" for action in _project_check_next_actions(check))
    lines.append("")
    return "\n".join(lines)


def _project_check_next_actions(check: ProjectCheck) -> list[str]:
    actions: list[str] = []
    if check.missing_pdf_names:
        actions.append("Run `library check-pdfs` and add the missing PDF files to the literature folder.")
    if check.missing_note_paths:
        actions.append("Run `library check-notes` and create paper-summary notes for missing note paths.")
    if check.simulation_issues:
        actions.append("Review simulation issues, then run `simulation inspect-data`, `simulation validate-data`, or `simulation check-ranges` on the affected files.")
    if check.manuscript_issues:
        actions.append("Review manuscript issues, then run `manuscript check` after fixing citations, sections, figures, captions, or references.")
    if not actions:
        actions.append("No immediate fixes needed; continue with writing packs, dashboards, figures, or the next review cycle.")
    return actions


def _load_project_check_config(root: Path) -> dict:
    path = root / "project-check.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _inspect_simulation(root: Path, config: dict) -> list[str]:
    simulation_root = root / "simulation"
    if not simulation_root.exists():
        return ["Simulation directory missing"]
    files = collect_export_files(simulation_root)
    if not files:
        return ["No simulation CSV/JSON exports found"]
    issues: list[str] = []
    required_columns = list(config.get("required_columns", []))
    numeric_columns = list(config.get("numeric_columns", []))
    metadata_path = root / config["metadata"] if config.get("metadata") else None
    unit_metadata = load_unit_metadata(metadata_path) if metadata_path and metadata_path.exists() else None
    for path in files:
        try:
            dataset = load_tabular_result(path)
            report = validate_dataset_columns(
                dataset,
                required_columns=required_columns,
                numeric_columns=numeric_columns,
                unit_metadata=unit_metadata,
            )
        except ValueError as exc:
            issues.append(f"{path.name}: {exc}")
            continue
        if report.missing_columns:
            issues.append(f"{path.name}: missing columns {', '.join(report.missing_columns)}")
        if report.non_numeric_columns:
            issues.append(f"{path.name}: non-numeric columns {', '.join(report.non_numeric_columns)}")
        if report.missing_unit_columns:
            issues.append(f"{path.name}: missing unit metadata {', '.join(report.missing_unit_columns)}")
        if report.empty_unit_columns:
            issues.append(f"{path.name}: empty unit metadata {', '.join(report.empty_unit_columns)}")
        if report.extra_unit_columns:
            issues.append(f"{path.name}: extra unit metadata {', '.join(report.extra_unit_columns)}")
        range_report = check_dataset_ranges(dataset, _parse_range_config(config.get("ranges", {})))
        for column, finding in range_report.findings.items():
            if finding.out_of_range_count:
                issues.append(f"{path.name}: {column} out of range {finding.out_of_range_count}")
            if finding.non_numeric_count:
                issues.append(f"{path.name}: {column} range check non-numeric {finding.non_numeric_count}")
        if range_report.missing_columns:
            issues.append(f"{path.name}: range check missing columns {', '.join(range_report.missing_columns)}")
    return issues


def _inspect_manuscripts(root: Path, config: dict, library_index) -> list[str]:
    manuscript_root = root / "manuscript"
    if not manuscript_root.exists():
        return ["Manuscript directory missing"]
    files = sorted(path for path in manuscript_root.iterdir() if path.suffix.lower() in {".md", ".txt", ".docx"})
    if not files:
        return ["No manuscript drafts found"]
    issues: list[str] = []
    for path in files:
        report = inspect_manuscript(
            path,
            required_sections=list(config.get("required_sections", [])),
            expected_figures=list(config.get("expected_figures", [])),
            library_index=library_index,
        )
        issues.extend(f"{path.name}: {issue.message}" for issue in report.issues)
    return issues


def _count_files(root: Path, suffixes: set[str]) -> int:
    if not root.exists():
        return 0
    return sum(1 for path in root.iterdir() if path.is_file() and path.suffix.lower() in suffixes)


def _count_figure_bundles(root: Path) -> int:
    if not root.exists():
        return 0
    stems = {path.stem for path in root.iterdir() if path.is_file() and path.suffix.lower() == ".svg"}
    return sum(1 for stem in stems if (root / f"{stem}.json").exists())


def _parse_range_config(payload: dict) -> dict[str, tuple[float, float]]:
    ranges: dict[str, tuple[float, float]] = {}
    for column, limits in payload.items():
        if isinstance(limits, (list, tuple)) and len(limits) == 2:
            ranges[column] = (float(limits[0]), float(limits[1]))
    return ranges
