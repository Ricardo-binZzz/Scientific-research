import json
import tempfile
import unittest
from pathlib import Path

from workflow.cli import main
from workflow.python.figure_exporter import (
    build_spec_from_dataset,
    build_heatmap_spec_from_dataset,
    build_contour_spec_from_dataset,
    export_figure_bundle,
    render_svg_errorbar_plot,
    render_svg_bar_chart,
    render_svg_contour_plot,
    render_svg_heatmap_plot,
    render_svg_line_plot,
)
from workflow.python.sim_result_loader import load_tabular_result


class FigureExportTests(unittest.TestCase):
    def test_build_spec_from_dataset_uses_named_columns(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "result.csv"
            path.write_text("time,stress\n0,0\n1,2\n", encoding="utf-8")
            dataset = load_tabular_result(path)

            spec = build_spec_from_dataset(
                dataset,
                title="Stress response",
                figure_type="trend",
                x_column="time",
                y_columns=["stress"],
                x_label="Time (s)",
                y_label="Stress (MPa)",
            )

        self.assertEqual(spec.title, "Stress response")
        self.assertEqual(spec.series[0].label, "stress")
        self.assertEqual(spec.series[0].y, [0.0, 2.0])

    def test_build_spec_from_dataset_can_attach_y_error_columns(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "result.csv"
            path.write_text("time,stress,stress_sd\n0,10,1\n1,14,2\n", encoding="utf-8")
            dataset = load_tabular_result(path)

            spec = build_spec_from_dataset(
                dataset,
                title="Stress response",
                figure_type="errorbar",
                x_column="time",
                y_columns=["stress"],
                y_error_columns=["stress_sd"],
                x_label="Time (s)",
                y_label="Stress (MPa)",
            )

        self.assertEqual(spec.series[0].y_error, [1.0, 2.0])

    def test_build_heatmap_spec_from_dataset_uses_coordinate_columns(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "result.csv"
            path.write_text("x,y,value\n0,0,1\n1,0,2\n0,1,3\n1,1,4\n", encoding="utf-8")
            dataset = load_tabular_result(path)

            spec = build_heatmap_spec_from_dataset(
                dataset,
                title="Temperature field",
                x_column="x",
                y_column="y",
                value_column="value",
                x_label="X",
                y_label="Y",
            )

        self.assertEqual(spec.figure_type, "heatmap")
        self.assertEqual(spec.heatmap_points[0]["value"], 1.0)

    def test_build_contour_spec_from_dataset_uses_coordinate_columns(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "result.csv"
            path.write_text("x,y,value\n0,0,1\n1,0,2\n0,1,3\n1,1,4\n", encoding="utf-8")
            dataset = load_tabular_result(path)

            spec = build_contour_spec_from_dataset(
                dataset,
                title="Temperature field",
                x_column="x",
                y_column="y",
                value_column="value",
                x_label="X",
                y_label="Y",
            )

        self.assertEqual(spec.figure_type, "contour")
        self.assertEqual(len(spec.contour_levels), 5)

    def test_render_svg_line_plot_contains_paths_and_labels(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "result.csv"
            path.write_text("time,stress\n0,0\n1,2\n", encoding="utf-8")
            dataset = load_tabular_result(path)
            spec = build_spec_from_dataset(
                dataset,
                title="Stress response",
                figure_type="trend",
                x_column="time",
                y_columns=["stress"],
                x_label="Time (s)",
                y_label="Stress (MPa)",
            )

            svg = render_svg_line_plot(spec)

        self.assertIn("<svg", svg)
        self.assertIn("Stress response", svg)
        self.assertIn("Stress (MPa)", svg)
        self.assertIn("<polyline", svg)

    def test_render_svg_bar_chart_contains_rectangles_and_labels(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "result.csv"
            path.write_text("case,force\n1,12\n2,18\n", encoding="utf-8")
            dataset = load_tabular_result(path)
            spec = build_spec_from_dataset(
                dataset,
                title="Force comparison",
                figure_type="bar",
                x_column="case",
                y_columns=["force"],
                x_label="Case",
                y_label="Force (N)",
            )

            svg = render_svg_bar_chart(spec)

        self.assertIn("<svg", svg)
        self.assertIn("Force comparison", svg)
        self.assertIn("Force (N)", svg)
        self.assertIn("<rect", svg)

    def test_render_svg_errorbar_plot_contains_error_segments(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "result.csv"
            path.write_text("time,stress,stress_sd\n0,10,1\n1,14,2\n", encoding="utf-8")
            dataset = load_tabular_result(path)
            spec = build_spec_from_dataset(
                dataset,
                title="Stress response",
                figure_type="errorbar",
                x_column="time",
                y_columns=["stress"],
                y_error_columns=["stress_sd"],
                x_label="Time (s)",
                y_label="Stress (MPa)",
            )

            svg = render_svg_errorbar_plot(spec)

        self.assertIn("<svg", svg)
        self.assertIn('class="errorbar"', svg)
        self.assertIn("<polyline", svg)

    def test_render_svg_heatmap_plot_contains_cells_and_labels(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "result.csv"
            path.write_text("x,y,value\n0,0,1\n1,0,2\n0,1,3\n1,1,4\n", encoding="utf-8")
            dataset = load_tabular_result(path)
            spec = build_heatmap_spec_from_dataset(
                dataset,
                title="Temperature field",
                x_column="x",
                y_column="y",
                value_column="value",
                x_label="X",
                y_label="Y",
            )

            svg = render_svg_heatmap_plot(spec)

        self.assertIn("<svg", svg)
        self.assertIn('class="cell"', svg)
        self.assertIn("Temperature field", svg)

    def test_render_svg_contour_plot_contains_lines_and_labels(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "result.csv"
            path.write_text("x,y,value\n0,0,1\n1,0,2\n0,1,3\n1,1,4\n", encoding="utf-8")
            dataset = load_tabular_result(path)
            spec = build_contour_spec_from_dataset(
                dataset,
                title="Temperature field",
                x_column="x",
                y_column="y",
                value_column="value",
                x_label="X",
                y_label="Y",
            )

            svg = render_svg_contour_plot(spec)

        self.assertIn("<svg", svg)
        self.assertIn('class="contour"', svg)
        self.assertIn("Temperature field", svg)

    def test_export_figure_bundle_writes_svg_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir)
            csv_path = out_dir / "result.csv"
            csv_path.write_text("time,stress\n0,0\n1,2\n", encoding="utf-8")
            dataset = load_tabular_result(csv_path)
            spec = build_spec_from_dataset(
                dataset,
                title="Stress response",
                figure_type="trend",
                x_column="time",
                y_columns=["stress"],
                x_label="Time (s)",
                y_label="Stress (MPa)",
            )

            bundle = export_figure_bundle(spec, out_dir, stem="stress-response")

            self.assertTrue(bundle.svg_path.is_file())
            self.assertTrue(bundle.json_path.is_file())
            payload = json.loads(bundle.json_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["title"], "Stress response")

    def test_export_figure_bundle_uses_bar_renderer_for_bar_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir)
            csv_path = out_dir / "result.csv"
            csv_path.write_text("case,force\n1,12\n2,18\n", encoding="utf-8")
            dataset = load_tabular_result(csv_path)
            spec = build_spec_from_dataset(
                dataset,
                title="Force comparison",
                figure_type="bar",
                x_column="case",
                y_columns=["force"],
                x_label="Case",
                y_label="Force (N)",
            )

            bundle = export_figure_bundle(spec, out_dir, stem="force-comparison")

            self.assertIn("<rect", bundle.svg_path.read_text(encoding="utf-8"))

    def test_cli_figure_from_data_accepts_error_columns(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            csv_path = root / "result.csv"
            csv_path.write_text("time,stress,stress_sd\n0,10,1\n1,14,2\n", encoding="utf-8")
            out_dir = root / "figures"

            exit_code = main(
                [
                    "figure",
                    "from-data",
                    str(csv_path),
                    str(out_dir),
                    "--stem",
                    "stress-response",
                    "--title",
                    "Stress response",
                    "--figure-type",
                    "errorbar",
                    "--x-column",
                    "time",
                    "--y-column",
                    "stress",
                    "--y-error-column",
                    "stress_sd",
                    "--x-label",
                    "Time (s)",
                    "--y-label",
                    "Stress (MPa)",
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertIn('class="errorbar"', (out_dir / "stress-response.svg").read_text(encoding="utf-8"))

    def test_cli_figure_from_data_accepts_heatmap_columns(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            csv_path = root / "result.csv"
            csv_path.write_text("x,y,value\n0,0,1\n1,0,2\n0,1,3\n1,1,4\n", encoding="utf-8")
            out_dir = root / "figures"

            exit_code = main(
                [
                    "figure",
                    "from-data",
                    str(csv_path),
                    str(out_dir),
                    "--stem",
                    "temperature-field",
                    "--title",
                    "Temperature field",
                    "--figure-type",
                    "heatmap",
                    "--x-column",
                    "x",
                    "--y-column",
                    "y",
                    "--value-column",
                    "value",
                    "--x-label",
                    "X",
                    "--y-label",
                    "Y",
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertIn('class="cell"', (out_dir / "temperature-field.svg").read_text(encoding="utf-8"))

    def test_cli_figure_from_data_accepts_contour_columns(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            csv_path = root / "result.csv"
            csv_path.write_text("x,y,value\n0,0,1\n1,0,2\n0,1,3\n1,1,4\n", encoding="utf-8")
            out_dir = root / "figures"

            exit_code = main(
                [
                    "figure",
                    "from-data",
                    str(csv_path),
                    str(out_dir),
                    "--stem",
                    "temperature-field",
                    "--title",
                    "Temperature field",
                    "--figure-type",
                    "contour",
                    "--x-column",
                    "x",
                    "--y-column",
                    "y",
                    "--value-column",
                    "value",
                    "--x-label",
                    "X",
                    "--y-label",
                    "Y",
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertIn('class="contour"', (out_dir / "temperature-field.svg").read_text(encoding="utf-8"))

    def test_cli_figure_from_data_writes_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            csv_path = root / "result.csv"
            csv_path.write_text("time,stress\n0,0\n1,2\n", encoding="utf-8")
            out_dir = root / "figures"

            exit_code = main(
                [
                    "figure",
                    "from-data",
                    str(csv_path),
                    str(out_dir),
                    "--stem",
                    "stress-response",
                    "--title",
                    "Stress response",
                    "--figure-type",
                    "trend",
                    "--x-column",
                    "time",
                    "--y-column",
                    "stress",
                    "--x-label",
                    "Time (s)",
                    "--y-label",
                    "Stress (MPa)",
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue((out_dir / "stress-response.svg").is_file())
            self.assertTrue((out_dir / "stress-response.json").is_file())


if __name__ == "__main__":
    unittest.main()
