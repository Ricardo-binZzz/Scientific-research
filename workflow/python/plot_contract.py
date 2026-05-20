from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Iterable


@dataclass(frozen=True)
class PlotSeries:
    label: str
    x: list[float]
    y: list[float]
    y_error: list[float] = field(default_factory=list)


@dataclass(frozen=True)
class FigureSpec:
    title: str
    figure_type: str
    x_label: str
    y_label: str
    series: list[PlotSeries] = field(default_factory=list)
    heatmap_points: list[dict[str, float]] = field(default_factory=list)
    contour_points: list[dict[str, float]] = field(default_factory=list)
    contour_levels: list[float] = field(default_factory=list)
    width_mm: int = 180
    height_mm: int = 120
    dpi: int = 300
    x_min: float | None = None
    x_max: float | None = None
    y_min: float | None = None
    y_max: float | None = None
    show_legend: bool = True
    show_grid: bool = True
    palette: str = "default"
    title_font_size: int = 18
    label_font_size: int = 15
    tick_font_size: int = 14
    line_width: float = 2.0
    tick_count: int = 5


def build_figure_spec(
    *,
    title: str,
    figure_type: str,
    x_label: str,
    y_label: str,
    series: Iterable[PlotSeries],
    width_mm: int = 180,
    height_mm: int = 120,
    dpi: int = 300,
    x_min: float | None = None,
    x_max: float | None = None,
    y_min: float | None = None,
    y_max: float | None = None,
    show_legend: bool = True,
    show_grid: bool = True,
    palette: str = "default",
    title_font_size: int = 18,
    label_font_size: int = 15,
    tick_font_size: int = 14,
    line_width: float = 2.0,
    tick_count: int = 5,
) -> FigureSpec:
    return FigureSpec(
        title=title,
        figure_type=figure_type,
        x_label=x_label,
        y_label=y_label,
        series=list(series),
        width_mm=width_mm,
        height_mm=height_mm,
        dpi=dpi,
        x_min=x_min,
        x_max=x_max,
        y_min=y_min,
        y_max=y_max,
        show_legend=show_legend,
        show_grid=show_grid,
        palette=palette,
        title_font_size=title_font_size,
        label_font_size=label_font_size,
        tick_font_size=tick_font_size,
        line_width=line_width,
        tick_count=tick_count,
    )


def figure_spec_to_dict(spec: FigureSpec) -> dict[str, Any]:
    payload = asdict(spec)
    payload["series"] = [asdict(item) for item in spec.series]
    return payload


def figure_spec_from_dict(payload: dict[str, Any]) -> FigureSpec:
    series = [
        PlotSeries(
            label=item["label"],
            x=[float(value) for value in item["x"]],
            y=[float(value) for value in item["y"]],
            y_error=[float(value) for value in item.get("y_error", [])],
        )
        for item in payload.get("series", [])
    ]
    return FigureSpec(
        title=str(payload["title"]),
        figure_type=str(payload["figure_type"]),
        x_label=str(payload["x_label"]),
        y_label=str(payload["y_label"]),
        series=series,
        heatmap_points=[{"x": float(item["x"]), "y": float(item["y"]), "value": float(item["value"])} for item in payload.get("heatmap_points", [])],
        contour_points=[{"x": float(item["x"]), "y": float(item["y"]), "value": float(item["value"])} for item in payload.get("contour_points", [])],
        contour_levels=[float(value) for value in payload.get("contour_levels", [])],
        width_mm=int(payload.get("width_mm", 180)),
        height_mm=int(payload.get("height_mm", 120)),
        dpi=int(payload.get("dpi", 300)),
        x_min=_optional_float(payload.get("x_min")),
        x_max=_optional_float(payload.get("x_max")),
        y_min=_optional_float(payload.get("y_min")),
        y_max=_optional_float(payload.get("y_max")),
        show_legend=bool(payload.get("show_legend", True)),
        show_grid=bool(payload.get("show_grid", True)),
        palette=str(payload.get("palette", "default")),
        title_font_size=int(payload.get("title_font_size", 18)),
        label_font_size=int(payload.get("label_font_size", 15)),
        tick_font_size=int(payload.get("tick_font_size", 14)),
        line_width=float(payload.get("line_width", 2.0)),
        tick_count=int(payload.get("tick_count", 5)),
    )


def _optional_float(value: Any) -> float | None:
    return None if value is None else float(value)
