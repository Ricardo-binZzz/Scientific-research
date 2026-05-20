from __future__ import annotations

import html
import json
from dataclasses import dataclass
from pathlib import Path

from workflow.python.plot_contract import FigureSpec, build_figure_spec, figure_spec_to_dict
from workflow.python.plot_contract import PlotSeries
from workflow.python.sim_result_loader import SimulationDataset, dataset_to_plot_series


@dataclass(frozen=True)
class FigureBundle:
    svg_path: Path
    json_path: Path


@dataclass(frozen=True)
class HeatmapPoint:
    x: float
    y: float
    value: float


def build_spec_from_dataset(
    dataset: SimulationDataset,
    *,
    title: str,
    figure_type: str,
    x_column: str,
    y_columns: list[str],
    y_error_columns: list[str] | None = None,
    x_label: str,
    y_label: str,
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
    series = dataset_to_plot_series(dataset, x_column=x_column, y_columns=y_columns)
    if y_error_columns:
        if len(y_error_columns) != len(series):
            raise ValueError("y_error_columns must match y_columns")
        series = [
            PlotSeries(
                label=item.label,
                x=item.x,
                y=item.y,
                y_error=[float(row[column]) for row in dataset.rows],
            )
            for item, column in zip(series, y_error_columns)
        ]
    return build_figure_spec(
        title=title,
        figure_type=figure_type,
        x_label=x_label,
        y_label=y_label,
        series=series,
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


def build_heatmap_spec_from_dataset(
    dataset: SimulationDataset,
    *,
    title: str,
    x_column: str,
    y_column: str,
    value_column: str,
    x_label: str,
    y_label: str,
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
    points = [
        HeatmapPoint(
            x=float(row[x_column]),
            y=float(row[y_column]),
            value=float(row[value_column]),
        )
        for row in dataset.rows
    ]
    return FigureSpec(
        title=title,
        figure_type="heatmap",
        x_label=x_label,
        y_label=y_label,
        heatmap_points=[{"x": point.x, "y": point.y, "value": point.value} for point in points],
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


def build_contour_spec_from_dataset(
    dataset: SimulationDataset,
    *,
    title: str,
    x_column: str,
    y_column: str,
    value_column: str,
    x_label: str,
    y_label: str,
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
    points = [
        HeatmapPoint(
            x=float(row[x_column]),
            y=float(row[y_column]),
            value=float(row[value_column]),
        )
        for row in dataset.rows
    ]
    x_values = sorted({point.x for point in points})
    y_values = sorted({point.y for point in points})
    if len(x_values) * len(y_values) != len(points):
        raise ValueError("Contour data must form a complete rectangular grid")
    grid = {(point.x, point.y): point.value for point in points}
    values = [point.value for point in points]
    low, high = _range(values)
    levels = _contour_levels(low, high)
    return FigureSpec(
        title=title,
        figure_type="contour",
        x_label=x_label,
        y_label=y_label,
        contour_points=[{"x": point.x, "y": point.y, "value": point.value} for point in points],
        contour_levels=levels,
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


def export_figure_bundle(spec: FigureSpec, out_dir: Path, *, stem: str) -> FigureBundle:
    out_dir.mkdir(parents=True, exist_ok=True)
    svg_path = out_dir / f"{stem}.svg"
    json_path = out_dir / f"{stem}.json"
    svg_path.write_text(render_svg(spec), encoding="utf-8")
    json_path.write_text(json.dumps(figure_spec_to_dict(spec), ensure_ascii=False, indent=2), encoding="utf-8")
    return FigureBundle(svg_path=svg_path, json_path=json_path)


def render_svg(spec: FigureSpec) -> str:
    if spec.figure_type == "bar":
        return render_svg_bar_chart(spec)
    if spec.figure_type == "errorbar":
        return render_svg_errorbar_plot(spec)
    if spec.figure_type == "heatmap":
        return render_svg_heatmap_plot(spec)
    if spec.figure_type == "contour":
        return render_svg_contour_plot(spec)
    return render_svg_line_plot(spec)


def render_svg_line_plot(spec: FigureSpec) -> str:
    width = int(spec.width_mm * 3.78)
    height = int(spec.height_mm * 3.78)
    margin_left = 70
    margin_right = 30
    margin_top = 50
    margin_bottom = 65
    plot_width = max(10, width - margin_left - margin_right)
    plot_height = max(10, height - margin_top - margin_bottom)
    x_values = [value for item in spec.series for value in item.x]
    y_values = [value for item in spec.series for value in item.y]
    min_x, max_x = _spec_range(spec.x_min, spec.x_max, x_values)
    min_y, max_y = _spec_range(spec.y_min, spec.y_max, y_values)
    colors = _palette_colors(spec.palette)
    tick_count = _tick_count(spec.tick_count)

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        _svg_style(spec),
        f'<text class="title" x="{width / 2:.1f}" y="28" text-anchor="middle">{html.escape(spec.title)}</text>',
        f'<line class="axis" x1="{margin_left}" y1="{height - margin_bottom}" x2="{width - margin_right}" y2="{height - margin_bottom}" />',
        f'<line class="axis" x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{height - margin_bottom}" />',
        f'<text class="label" x="{width / 2:.1f}" y="{height - 18}" text-anchor="middle">{html.escape(spec.x_label)}</text>',
        f'<text class="label" x="18" y="{height / 2:.1f}" text-anchor="middle" transform="rotate(-90 18 {height / 2:.1f})">{html.escape(spec.y_label)}</text>',
    ]
    for tick in range(tick_count):
        ratio = _tick_ratio(tick, tick_count)
        x = margin_left + ratio * plot_width
        y = height - margin_bottom - ratio * plot_height
        if spec.show_grid:
            lines.append(f'<line class="grid" x1="{x:.1f}" y1="{margin_top}" x2="{x:.1f}" y2="{height - margin_bottom}" />')
            lines.append(f'<line class="grid" x1="{margin_left}" y1="{y:.1f}" x2="{width - margin_right}" y2="{y:.1f}" />')
        lines.append(f'<text x="{x:.1f}" y="{height - margin_bottom + 22}" text-anchor="middle" class="tick">{_format_value(min_x + ratio * (max_x - min_x))}</text>')
        lines.append(f'<text class="tick" x="{margin_left - 8}" y="{y + 5:.1f}" text-anchor="end">{_format_value(min_y + ratio * (max_y - min_y))}</text>')
    for idx, item in enumerate(spec.series):
        points = [
            f"{_scale(x, min_x, max_x, margin_left, margin_left + plot_width):.1f},{_scale(y, min_y, max_y, height - margin_bottom, margin_top):.1f}"
            for x, y in zip(item.x, item.y)
        ]
        color = colors[idx % len(colors)]
        lines.append(f'<polyline fill="none" stroke="{color}" stroke-width="{spec.line_width:g}" points="{" ".join(points)}" />')
        if spec.show_legend:
            legend_y = margin_top + idx * 22
            lines.append(f'<line x1="{width - 160}" y1="{legend_y}" x2="{width - 130}" y2="{legend_y}" stroke="{color}" stroke-width="{spec.line_width:g}" />')
            lines.append(f'<text x="{width - 124}" y="{legend_y + 5}">{html.escape(item.label)}</text>')
    lines.append("</svg>")
    return "\n".join(lines)


def render_svg_bar_chart(spec: FigureSpec) -> str:
    width = int(spec.width_mm * 3.78)
    height = int(spec.height_mm * 3.78)
    margin_left = 70
    margin_right = 30
    margin_top = 50
    margin_bottom = 65
    plot_width = max(10, width - margin_left - margin_right)
    plot_height = max(10, height - margin_top - margin_bottom)
    y_values = [value for item in spec.series for value in item.y]
    min_y, max_y = _spec_range(spec.y_min, spec.y_max, [0.0] + y_values)
    colors = _palette_colors(spec.palette)
    tick_count = _tick_count(spec.tick_count)
    first_series = spec.series[0] if spec.series else None
    category_count = len(first_series.x) if first_series else 0
    group_width = plot_width / max(1, category_count)
    bar_width = group_width / max(2, len(spec.series) + 1)

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        _svg_style(spec),
        f'<text class="title" x="{width / 2:.1f}" y="28" text-anchor="middle">{html.escape(spec.title)}</text>',
        f'<line class="axis" x1="{margin_left}" y1="{height - margin_bottom}" x2="{width - margin_right}" y2="{height - margin_bottom}" />',
        f'<line class="axis" x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{height - margin_bottom}" />',
        f'<text class="label" x="{width / 2:.1f}" y="{height - 18}" text-anchor="middle">{html.escape(spec.x_label)}</text>',
        f'<text class="label" x="18" y="{height / 2:.1f}" text-anchor="middle" transform="rotate(-90 18 {height / 2:.1f})">{html.escape(spec.y_label)}</text>',
    ]
    for tick in range(tick_count):
        ratio = _tick_ratio(tick, tick_count)
        y = height - margin_bottom - ratio * plot_height
        if spec.show_grid:
            lines.append(f'<line class="grid" x1="{margin_left}" y1="{y:.1f}" x2="{width - margin_right}" y2="{y:.1f}" />')
        lines.append(f'<text class="tick" x="{margin_left - 8}" y="{y + 5:.1f}" text-anchor="end">{_format_value(min_y + ratio * (max_y - min_y))}</text>')
    for series_idx, item in enumerate(spec.series):
        color = colors[series_idx % len(colors)]
        for point_idx, (x_value, y_value) in enumerate(zip(item.x, item.y)):
            group_start = margin_left + point_idx * group_width
            x = group_start + (series_idx + 0.5) * bar_width
            y = _scale(y_value, min_y, max_y, height - margin_bottom, margin_top)
            zero_y = _scale(0.0, min_y, max_y, height - margin_bottom, margin_top)
            bar_height = abs(zero_y - y)
            top = min(y, zero_y)
            lines.append(f'<rect x="{x:.1f}" y="{top:.1f}" width="{bar_width * 0.8:.1f}" height="{bar_height:.1f}" fill="{color}" />')
            if series_idx == 0:
                label_x = group_start + group_width / 2
                lines.append(f'<text class="tick" x="{label_x:.1f}" y="{height - margin_bottom + 22}" text-anchor="middle">{_format_value(x_value)}</text>')
        if spec.show_legend:
            legend_y = margin_top + series_idx * 22
            lines.append(f'<rect x="{width - 160}" y="{legend_y - 10}" width="22" height="12" fill="{color}" />')
            lines.append(f'<text x="{width - 130}" y="{legend_y + 1}">{html.escape(item.label)}</text>')
    lines.append("</svg>")
    return "\n".join(lines)


def render_svg_errorbar_plot(spec: FigureSpec) -> str:
    width = int(spec.width_mm * 3.78)
    height = int(spec.height_mm * 3.78)
    margin_left = 70
    margin_right = 30
    margin_top = 50
    margin_bottom = 65
    plot_width = max(10, width - margin_left - margin_right)
    plot_height = max(10, height - margin_top - margin_bottom)
    x_values = [value for item in spec.series for value in item.x]
    y_values = []
    for item in spec.series:
        if item.y_error:
            y_values.extend([value + error for value, error in zip(item.y, item.y_error)])
            y_values.extend([value - error for value, error in zip(item.y, item.y_error)])
        else:
            y_values.extend(item.y)
    min_x, max_x = _spec_range(spec.x_min, spec.x_max, x_values)
    min_y, max_y = _spec_range(spec.y_min, spec.y_max, y_values)
    colors = _palette_colors(spec.palette)
    tick_count = _tick_count(spec.tick_count)

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        _svg_style(spec, extra=".errorbar{stroke-width:1.4;}"),
        f'<text class="title" x="{width / 2:.1f}" y="28" text-anchor="middle">{html.escape(spec.title)}</text>',
        f'<line class="axis" x1="{margin_left}" y1="{height - margin_bottom}" x2="{width - margin_right}" y2="{height - margin_bottom}" />',
        f'<line class="axis" x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{height - margin_bottom}" />',
        f'<text class="label" x="{width / 2:.1f}" y="{height - 18}" text-anchor="middle">{html.escape(spec.x_label)}</text>',
        f'<text class="label" x="18" y="{height / 2:.1f}" text-anchor="middle" transform="rotate(-90 18 {height / 2:.1f})">{html.escape(spec.y_label)}</text>',
    ]
    for tick in range(tick_count):
        ratio = _tick_ratio(tick, tick_count)
        x = margin_left + ratio * plot_width
        y = height - margin_bottom - ratio * plot_height
        if spec.show_grid:
            lines.append(f'<line class="grid" x1="{x:.1f}" y1="{margin_top}" x2="{x:.1f}" y2="{height - margin_bottom}" />')
            lines.append(f'<line class="grid" x1="{margin_left}" y1="{y:.1f}" x2="{width - margin_right}" y2="{y:.1f}" />')
        lines.append(f'<text class="tick" x="{x:.1f}" y="{height - margin_bottom + 22}" text-anchor="middle">{_format_value(min_x + ratio * (max_x - min_x))}</text>')
        lines.append(f'<text class="tick" x="{margin_left - 8}" y="{y + 5:.1f}" text-anchor="end">{_format_value(min_y + ratio * (max_y - min_y))}</text>')
    for idx, item in enumerate(spec.series):
        color = colors[idx % len(colors)]
        points = []
        for x_value, y_value, error in _iter_error_points(item):
            x = _scale(x_value, min_x, max_x, margin_left, margin_left + plot_width)
            y = _scale(y_value, min_y, max_y, height - margin_bottom, margin_top)
            points.append(f"{x:.1f},{y:.1f}")
            if error > 0:
                y_low = _scale(y_value - error, min_y, max_y, height - margin_bottom, margin_top)
                y_high = _scale(y_value + error, min_y, max_y, height - margin_bottom, margin_top)
                lines.append(f'<line class="errorbar" x1="{x:.1f}" y1="{y_low:.1f}" x2="{x:.1f}" y2="{y_high:.1f}" stroke="{color}" />')
                lines.append(f'<line class="errorbar" x1="{x - 5:.1f}" y1="{y_low:.1f}" x2="{x + 5:.1f}" y2="{y_low:.1f}" stroke="{color}" />')
                lines.append(f'<line class="errorbar" x1="{x - 5:.1f}" y1="{y_high:.1f}" x2="{x + 5:.1f}" y2="{y_high:.1f}" stroke="{color}" />')
        lines.append(f'<polyline fill="none" stroke="{color}" stroke-width="{spec.line_width:g}" points="{" ".join(points)}" />')
        if spec.show_legend:
            legend_y = margin_top + idx * 22
            lines.append(f'<line x1="{width - 160}" y1="{legend_y}" x2="{width - 130}" y2="{legend_y}" stroke="{color}" stroke-width="{spec.line_width:g}" />')
            lines.append(f'<text x="{width - 124}" y="{legend_y + 5}">{html.escape(item.label)}</text>')
    lines.append("</svg>")
    return "\n".join(lines)


def render_svg_heatmap_plot(spec: FigureSpec) -> str:
    width = int(spec.width_mm * 3.78)
    height = int(spec.height_mm * 3.78)
    margin_left = 70
    margin_right = 30
    margin_top = 50
    margin_bottom = 65
    plot_width = max(10, width - margin_left - margin_right)
    plot_height = max(10, height - margin_top - margin_bottom)
    points = spec.heatmap_points
    x_values = [point["x"] for point in points]
    y_values = [point["y"] for point in points]
    values = [point["value"] for point in points]
    min_x, max_x = _spec_range(spec.x_min, spec.x_max, x_values)
    min_y, max_y = _spec_range(spec.y_min, spec.y_max, y_values)
    min_v, max_v = _range(values)
    tick_count = _tick_count(spec.tick_count)

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        _svg_style(spec, extra=".cell{stroke:#fff;stroke-width:1;}"),
        f'<text class="title" x="{width / 2:.1f}" y="28" text-anchor="middle">{html.escape(spec.title)}</text>',
        f'<line class="axis" x1="{margin_left}" y1="{height - margin_bottom}" x2="{width - margin_right}" y2="{height - margin_bottom}" />',
        f'<line class="axis" x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{height - margin_bottom}" />',
        f'<text class="label" x="{width / 2:.1f}" y="{height - 18}" text-anchor="middle">{html.escape(spec.x_label)}</text>',
        f'<text class="label" x="18" y="{height / 2:.1f}" text-anchor="middle" transform="rotate(-90 18 {height / 2:.1f})">{html.escape(spec.y_label)}</text>',
    ]
    for tick in range(tick_count):
        ratio = _tick_ratio(tick, tick_count)
        x = margin_left + ratio * plot_width
        y = height - margin_bottom - ratio * plot_height
        if spec.show_grid:
            lines.append(f'<line class="grid" x1="{x:.1f}" y1="{margin_top}" x2="{x:.1f}" y2="{height - margin_bottom}" />')
            lines.append(f'<line class="grid" x1="{margin_left}" y1="{y:.1f}" x2="{width - margin_right}" y2="{y:.1f}" />')
        lines.append(f'<text class="tick" x="{x:.1f}" y="{height - margin_bottom + 22}" text-anchor="middle">{_format_value(min_x + ratio * (max_x - min_x))}</text>')
        lines.append(f'<text class="tick" x="{margin_left - 8}" y="{y + 5:.1f}" text-anchor="end">{_format_value(min_y + ratio * (max_y - min_y))}</text>')
    for point in points:
        x = _scale(point["x"], min_x, max_x, margin_left, margin_left + plot_width)
        y = _scale(point["y"], min_y, max_y, height - margin_bottom, margin_top)
        color = _heatmap_color(point["value"], min_v, max_v)
        lines.append(
            f'<rect class="cell" x="{x - 20:.1f}" y="{y - 20:.1f}" width="40" height="40" fill="{color}"><title>{point["value"]:.3g}</title></rect>'
        )
    lines.append("</svg>")
    return "\n".join(lines)


def render_svg_contour_plot(spec: FigureSpec) -> str:
    width = int(spec.width_mm * 3.78)
    height = int(spec.height_mm * 3.78)
    margin_left = 70
    margin_right = 30
    margin_top = 50
    margin_bottom = 65
    plot_width = max(10, width - margin_left - margin_right)
    plot_height = max(10, height - margin_top - margin_bottom)
    points = spec.contour_points
    x_values = [point["x"] for point in points]
    y_values = [point["y"] for point in points]
    values = [point["value"] for point in points]
    min_x, max_x = _spec_range(spec.x_min, spec.x_max, x_values)
    min_y, max_y = _spec_range(spec.y_min, spec.y_max, y_values)
    min_v, max_v = _range(values)
    grid = {(point["x"], point["y"]): point["value"] for point in points}
    x_levels = sorted(set(x_values))
    y_levels = sorted(set(y_values))
    tick_count = _tick_count(spec.tick_count)

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        _svg_style(spec, extra=f".contour{{fill:none;stroke:{_palette_colors(spec.palette)[0]};stroke-width:{max(1.0, spec.line_width * 0.8):g};}}"),
        f'<text class="title" x="{width / 2:.1f}" y="28" text-anchor="middle">{html.escape(spec.title)}</text>',
        f'<line class="axis" x1="{margin_left}" y1="{height - margin_bottom}" x2="{width - margin_right}" y2="{height - margin_bottom}" />',
        f'<line class="axis" x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{height - margin_bottom}" />',
        f'<text class="label" x="{width / 2:.1f}" y="{height - 18}" text-anchor="middle">{html.escape(spec.x_label)}</text>',
        f'<text class="label" x="18" y="{height / 2:.1f}" text-anchor="middle" transform="rotate(-90 18 {height / 2:.1f})">{html.escape(spec.y_label)}</text>',
    ]
    for tick in range(tick_count):
        ratio = _tick_ratio(tick, tick_count)
        x = margin_left + ratio * plot_width
        y = height - margin_bottom - ratio * plot_height
        if spec.show_grid:
            lines.append(f'<line class="grid" x1="{x:.1f}" y1="{margin_top}" x2="{x:.1f}" y2="{height - margin_bottom}" />')
            lines.append(f'<line class="grid" x1="{margin_left}" y1="{y:.1f}" x2="{width - margin_right}" y2="{y:.1f}" />')
        lines.append(f'<text class="tick" x="{x:.1f}" y="{height - margin_bottom + 22}" text-anchor="middle">{_format_value(min_x + ratio * (max_x - min_x))}</text>')
        lines.append(f'<text class="tick" x="{margin_left - 8}" y="{y + 5:.1f}" text-anchor="end">{_format_value(min_y + ratio * (max_y - min_y))}</text>')

    if len(x_levels) >= 2 and len(y_levels) >= 2:
        for level in spec.contour_levels:
            for ix in range(len(x_levels) - 1):
                for iy in range(len(y_levels) - 1):
                    square = [
                        ((x_levels[ix], y_levels[iy]), grid[(x_levels[ix], y_levels[iy])]),
                        ((x_levels[ix + 1], y_levels[iy]), grid[(x_levels[ix + 1], y_levels[iy])]),
                        ((x_levels[ix + 1], y_levels[iy + 1]), grid[(x_levels[ix + 1], y_levels[iy + 1])]),
                        ((x_levels[ix], y_levels[iy + 1]), grid[(x_levels[ix], y_levels[iy + 1])]),
                    ]
                    lines.extend(_marching_squares_segment(square, level, min_x, max_x, min_y, max_y, margin_left, margin_top, plot_width, plot_height))
    lines.append("</svg>")
    return "\n".join(lines)


def _range(values: list[float]) -> tuple[float, float]:
    if not values:
        return 0.0, 1.0
    low = min(values)
    high = max(values)
    if low == high:
        return low - 0.5, high + 0.5
    return low, high


def _svg_style(spec: FigureSpec, *, extra: str = "") -> str:
    return (
        "<style>"
        "text{font-family:Arial, sans-serif;font-size:14px;}"
        ".axis{stroke:#222;stroke-width:1.2;}"
        ".grid{stroke:#ddd;stroke-width:0.8;}"
        f".label{{font-size:{spec.label_font_size}px;}}"
        f".title{{font-size:{spec.title_font_size}px;font-weight:700;}}"
        f".tick{{font-size:{spec.tick_font_size}px;}}"
        f"{extra}"
        "</style>"
    )


def _palette_colors(name: str) -> list[str]:
    palettes = {
        "default": ["#1f77b4", "#d62728", "#2ca02c", "#9467bd", "#ff7f0e"],
        "colorblind": ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00"],
        "mono": ["#333333", "#666666", "#999999", "#bbbbbb", "#111111"],
        "journal": ["#005A8D", "#C44900", "#2E7D32", "#6A4C93", "#8C564B"],
    }
    return palettes.get(name, palettes["default"])


def _tick_count(value: int) -> int:
    return max(2, min(12, int(value)))


def _tick_ratio(index: int, tick_count: int) -> float:
    return 0.0 if tick_count <= 1 else index / (tick_count - 1)


def _spec_range(low_override: float | None, high_override: float | None, values: list[float]) -> tuple[float, float]:
    low, high = _range(values)
    return (low if low_override is None else low_override, high if high_override is None else high_override)


def _scale(value: float, low: float, high: float, out_low: float, out_high: float) -> float:
    if low == high:
        return (out_low + out_high) / 2
    return out_low + (value - low) / (high - low) * (out_high - out_low)


def _format_value(value: float) -> str:
    return f"{value:.3g}"


def _iter_error_points(item: PlotSeries) -> list[tuple[float, float, float]]:
    errors = item.y_error or [0.0 for _ in item.y]
    return [(x, y, abs(error)) for x, y, error in zip(item.x, item.y, errors)]


def _heatmap_color(value: float, low: float, high: float) -> str:
    ratio = 0.5 if low == high else max(0.0, min(1.0, (value - low) / (high - low)))
    red = int(240 - 160 * ratio)
    blue = int(255 - 120 * ratio)
    green = int(245 - 90 * ratio)
    return f"rgb({red},{green},{blue})"


def _contour_levels(low: float, high: float) -> list[float]:
    if low == high:
        return [low]
    step = (high - low) / 6
    return [low + step * index for index in range(1, 6)]


def _marching_squares_segment(
    square: list[tuple[tuple[float, float], float]],
    level: float,
    min_x: float,
    max_x: float,
    min_y: float,
    max_y: float,
    margin_left: float,
    margin_top: float,
    plot_width: float,
    plot_height: float,
) -> list[str]:
    points = []
    intersections = []
    edges = [
        (square[0], square[1]),
        (square[1], square[2]),
        (square[2], square[3]),
        (square[3], square[0]),
    ]
    for left, right in edges:
        value_left = left[1]
        value_right = right[1]
        if (value_left - level) * (value_right - level) > 0:
            continue
        if value_left == value_right == level:
            continue
        ratio = 0.5 if value_left == value_right else (level - value_left) / (value_right - value_left)
        x = left[0][0] + ratio * (right[0][0] - left[0][0])
        y = left[0][1] + ratio * (right[0][1] - left[0][1])
        intersections.append((_scale(x, min_x, max_x, margin_left, margin_left + plot_width), _scale(y, min_y, max_y, margin_top + plot_height, margin_top)))
    if len(intersections) < 2:
        return []
    start, end = intersections[0], intersections[-1]
    return [f'<line class="contour" x1="{start[0]:.1f}" y1="{start[1]:.1f}" x2="{end[0]:.1f}" y2="{end[1]:.1f}" />']
