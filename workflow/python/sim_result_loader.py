from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from workflow.python.plot_contract import PlotSeries


@dataclass(frozen=True)
class SimulationDataset:
    source: Path
    columns: list[str]
    rows: list[dict[str, Any]]


def load_tabular_result(path: Path) -> SimulationDataset:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return _load_csv(path)
    if suffix == ".json":
        return _load_json(path)
    raise ValueError(f"Unsupported result format: {path.suffix}")


def dataset_to_plot_series(
    dataset: SimulationDataset,
    *,
    x_column: str,
    y_columns: list[str],
) -> list[PlotSeries]:
    x_values = [float(row[x_column]) for row in dataset.rows]
    series: list[PlotSeries] = []
    for column in y_columns:
        series.append(
            PlotSeries(
                label=column,
                x=x_values,
                y=[float(row[column]) for row in dataset.rows],
            )
        )
    return series


def _load_csv(path: Path) -> SimulationDataset:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        columns = _normalize_result_columns(fieldnames)
        rows = [
            {normalized: row.get(original) for original, normalized in zip(fieldnames, columns)}
            for row in reader
        ]
        return SimulationDataset(source=path, columns=columns, rows=rows)


def _load_json(path: Path) -> SimulationDataset:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if isinstance(payload, list):
        rows = [dict(item) for item in payload]
    elif isinstance(payload, dict) and isinstance(payload.get("rows"), list):
        rows = [dict(item) for item in payload["rows"]]
    else:
        raise ValueError("JSON result must contain a list of records or a {rows: [...]} object")
    columns = list(rows[0].keys()) if rows else []
    return SimulationDataset(source=path, columns=columns, rows=rows)


def _normalize_result_columns(fieldnames: list[str]) -> list[str]:
    columns: list[str] = []
    used: set[str] = set()
    for fieldname in fieldnames:
        base = _standard_result_column(fieldname)
        column = base
        counter = 2
        while column in used:
            column = f"{base}_{counter}"
            counter += 1
        used.add(column)
        columns.append(column)
    return columns


def _standard_result_column(fieldname: str) -> str:
    normalized = _normalize_header_text(fieldname)
    if normalized in {"time", "t", "t s", "step time"} or normalized.startswith("time "):
        return "time"
    if normalized in {"stress", "stress mpa", "equivalent stress", "equivalent stress mpa"} or "mises" in normalized:
        return "stress"
    if "strain" in normalized or normalized in {"e", "peeq"}:
        return "strain"
    if "deformation" in normalized or "displacement" in normalized or normalized in {"u magnitude", "solid disp", "solid disp mm"}:
        return "displacement"
    if "force" in normalized or normalized in {"rf magnitude", "reaction force"}:
        return "force"
    if normalized in {"t k", "temperature"} or "temperature" in normalized:
        return "temperature"
    return fieldname.strip()


def _normalize_header_text(fieldname: str) -> str:
    text = fieldname.strip().lower()
    text = text.replace(":", " ")
    text = re.sub(r"[\[\]\(\),/.]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _safe_column_name(fieldname: str) -> str:
    text = _normalize_header_text(fieldname)
    text = re.sub(r"[^a-z0-9]+", "_", text).strip("_")
    return text or "column"
