from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

from workflow.python.sim_result_loader import SimulationDataset


@dataclass(frozen=True)
class SimulationCase:
    name: str
    software: str
    version: str
    geometry_source: str
    material_set: str
    boundary_conditions: str
    mesh_summary: str
    solve_settings: str
    export_format: str
    validation_notes: str


@dataclass(frozen=True)
class DatasetValidationReport:
    missing_columns: list[str]
    non_numeric_columns: list[str]
    missing_unit_columns: list[str] | None = None
    empty_unit_columns: list[str] | None = None
    extra_unit_columns: list[str] | None = None

    @property
    def ok(self) -> bool:
        return (
            not self.missing_columns
            and not self.non_numeric_columns
            and not (self.missing_unit_columns or [])
            and not (self.empty_unit_columns or [])
            and not (self.extra_unit_columns or [])
        )


@dataclass(frozen=True)
class DatasetInspection:
    source_name: str
    columns: list[str]
    row_count: int
    sample_rows: list[dict[str, object]]


@dataclass(frozen=True)
class NumericColumnSummary:
    count: int
    minimum: float
    maximum: float


@dataclass(frozen=True)
class DatasetSummary:
    source_name: str
    row_count: int
    numeric_columns: dict[str, NumericColumnSummary]
    non_numeric_columns: list[str]


@dataclass(frozen=True)
class RangeFinding:
    minimum: float
    maximum: float
    out_of_range_count: int
    non_numeric_count: int


@dataclass(frozen=True)
class RangeCheckReport:
    source_name: str
    row_count: int
    findings: dict[str, RangeFinding]
    missing_columns: list[str]

    @property
    def ok(self) -> bool:
        return (
            not self.missing_columns
            and all(item.out_of_range_count == 0 and item.non_numeric_count == 0 for item in self.findings.values())
        )


@dataclass(frozen=True)
class ExternalSimulationRun:
    command: list[str]
    work_dir: Path
    log_path: Path
    exit_code: int


def build_case_manifest(case: SimulationCase) -> str:
    return render_case_manifest(case)


def run_external_simulation_command(command: list[str], work_dir: Path, log_path: Path) -> ExternalSimulationRun:
    if not command:
        raise ValueError("external simulation command is required")
    work_dir.mkdir(parents=True, exist_ok=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(command, cwd=work_dir, text=True, capture_output=True, check=False)
    log_path.write_text((completed.stdout or "") + (completed.stderr or ""), encoding="utf-8")
    return ExternalSimulationRun(command=command, work_dir=work_dir, log_path=log_path, exit_code=completed.returncode)


def render_external_simulation_run(run: ExternalSimulationRun) -> str:
    return "\n".join(
        [
            "# External Simulation Command",
            "",
            f"- Command: {' '.join(run.command)}",
            f"- Work directory: {run.work_dir}",
            f"- Log path: {run.log_path}",
            f"- Exit code: {run.exit_code}",
            "",
        ]
    )


def render_case_manifest(case: SimulationCase) -> str:
    return "\n".join(
        [
            "# Simulation Runbook",
            "",
            f"- Case name: {case.name}",
            f"- Software: {case.software}",
            f"- Version: {case.version}",
            f"- Geometry source: {case.geometry_source}",
            f"- Material set: {case.material_set}",
            f"- Boundary conditions: {case.boundary_conditions}",
            f"- Mesh summary: {case.mesh_summary}",
            f"- Solve settings: {case.solve_settings}",
            f"- Export format: {case.export_format}",
            f"- Validation notes: {case.validation_notes}",
            "",
        ]
    )


def collect_export_files(root: Path) -> list[Path]:
    files = [path for path in root.iterdir() if path.suffix.lower() in {".csv", ".json"}]
    return sorted(files, key=lambda item: item.name)


def validate_dataset_columns(
    dataset: SimulationDataset,
    *,
    required_columns: list[str],
    numeric_columns: list[str],
    unit_metadata: dict[str, str] | None = None,
) -> DatasetValidationReport:
    missing = [column for column in required_columns if column not in dataset.columns]
    non_numeric: list[str] = []
    for column in numeric_columns:
        if column in missing:
            continue
        if any(not _is_number(row.get(column)) for row in dataset.rows):
            non_numeric.append(column)
    missing_units = []
    empty_units = []
    extra_units = []
    if unit_metadata is not None:
        missing_units = [column for column in numeric_columns if column not in unit_metadata]
        empty_units = [column for column in numeric_columns if column in unit_metadata and not unit_metadata[column].strip()]
        extra_units = [column for column in unit_metadata if column not in dataset.columns]
    return DatasetValidationReport(
        missing_columns=missing,
        non_numeric_columns=non_numeric,
        missing_unit_columns=missing_units,
        empty_unit_columns=empty_units,
        extra_unit_columns=extra_units,
    )


def inspect_dataset(dataset: SimulationDataset, *, sample_size: int = 5) -> DatasetInspection:
    return DatasetInspection(
        source_name=dataset.source.name,
        columns=dataset.columns,
        row_count=len(dataset.rows),
        sample_rows=dataset.rows[: max(0, sample_size)],
    )


def render_dataset_inspection(inspection: DatasetInspection) -> str:
    lines = ["# Dataset Inspection", ""]
    lines.append(f"- Source: {inspection.source_name}")
    lines.append(f"- Rows: {inspection.row_count}")
    lines.append(f"- Columns: {', '.join(inspection.columns) if inspection.columns else 'None'}")
    lines.append("")
    lines.append("## Sample Rows")
    if not inspection.sample_rows:
        lines.append("- None")
        lines.append("")
        return "\n".join(lines)
    lines.append(" | ".join(inspection.columns))
    for row in inspection.sample_rows:
        lines.append(" | ".join(str(row.get(column, "")) for column in inspection.columns))
    lines.append("")
    return "\n".join(lines)


def summarize_dataset(dataset: SimulationDataset) -> DatasetSummary:
    numeric_columns: dict[str, NumericColumnSummary] = {}
    non_numeric_columns: list[str] = []
    for column in dataset.columns:
        values = [_try_float(row.get(column)) for row in dataset.rows]
        numbers = [value for value in values if value is not None]
        if numbers:
            numeric_columns[column] = NumericColumnSummary(
                count=len(numbers),
                minimum=min(numbers),
                maximum=max(numbers),
            )
        if len(numbers) < len(dataset.rows):
            non_numeric_columns.append(column)
    return DatasetSummary(
        source_name=dataset.source.name,
        row_count=len(dataset.rows),
        numeric_columns=numeric_columns,
        non_numeric_columns=non_numeric_columns,
    )


def render_dataset_summary(summary: DatasetSummary) -> str:
    lines = ["# Dataset Summary", ""]
    lines.append(f"- Source: {summary.source_name}")
    lines.append(f"- Rows: {summary.row_count}")
    lines.append(
        f"- Non-numeric columns: {', '.join(summary.non_numeric_columns) if summary.non_numeric_columns else 'None'}"
    )
    lines.append("")
    lines.append("## Numeric Columns")
    if not summary.numeric_columns:
        lines.append("- None")
        lines.append("")
        return "\n".join(lines)
    lines.append("Column | Count | Min | Max")
    for column, item in summary.numeric_columns.items():
        lines.append(f"{column} | {item.count} | {_format_number(item.minimum)} | {_format_number(item.maximum)}")
    lines.append("")
    return "\n".join(lines)


def check_dataset_ranges(dataset: SimulationDataset, ranges: dict[str, tuple[float, float]]) -> RangeCheckReport:
    findings: dict[str, RangeFinding] = {}
    missing_columns: list[str] = []
    for column, (minimum, maximum) in ranges.items():
        if column not in dataset.columns:
            missing_columns.append(column)
            continue
        out_of_range = 0
        non_numeric = 0
        for row in dataset.rows:
            value = _try_float(row.get(column))
            if value is None:
                non_numeric += 1
                continue
            if value < minimum or value > maximum:
                out_of_range += 1
        findings[column] = RangeFinding(
            minimum=minimum,
            maximum=maximum,
            out_of_range_count=out_of_range,
            non_numeric_count=non_numeric,
        )
    return RangeCheckReport(
        source_name=dataset.source.name,
        row_count=len(dataset.rows),
        findings=findings,
        missing_columns=missing_columns,
    )


def render_range_check_report(report: RangeCheckReport) -> str:
    lines = ["# Range Check Report", ""]
    lines.append(f"- Source: {report.source_name}")
    lines.append(f"- Rows: {report.row_count}")
    lines.append(f"- OK: {report.ok}")
    lines.append(f"- Missing columns: {', '.join(report.missing_columns) if report.missing_columns else 'None'}")
    lines.append("")
    lines.append("Column | Min | Max | Out-of-range | Non-numeric")
    if not report.findings:
        lines.append("- None")
    for column, finding in report.findings.items():
        lines.append(
            f"{column} | {_format_number(finding.minimum)} | {_format_number(finding.maximum)} | "
            f"{finding.out_of_range_count} | {finding.non_numeric_count}"
        )
    lines.append("")
    return "\n".join(lines)


def render_dataset_validation_report(report: DatasetValidationReport) -> str:
    lines = ["# Dataset Validation Report", ""]
    lines.append(f"- OK: {report.ok}")
    lines.append(f"- Missing columns: {', '.join(report.missing_columns) if report.missing_columns else 'None'}")
    lines.append(f"- Non-numeric columns: {', '.join(report.non_numeric_columns) if report.non_numeric_columns else 'None'}")
    lines.append(f"- Missing unit metadata: {', '.join(report.missing_unit_columns or []) if report.missing_unit_columns else 'None'}")
    lines.append(f"- Empty unit metadata: {', '.join(report.empty_unit_columns or []) if report.empty_unit_columns else 'None'}")
    lines.append(f"- Extra unit metadata: {', '.join(report.extra_unit_columns or []) if report.extra_unit_columns else 'None'}")
    lines.append("")
    return "\n".join(lines)


def load_unit_metadata(path: Path) -> dict[str, str]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    columns = payload.get("columns", {})
    return {str(key): str(value) for key, value in columns.items()}


def _is_number(value: object) -> bool:
    return _try_float(value) is not None


def _try_float(value: object) -> float | None:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def _format_number(value: float) -> str:
    return f"{value:.6g}"
