import json
import tempfile
import unittest
from pathlib import Path

from workflow.python.plot_contract import (
    FigureSpec,
    PlotSeries,
    build_figure_spec,
    figure_spec_to_dict,
    figure_spec_from_dict,
)
from workflow.python.sim_result_loader import load_tabular_result, dataset_to_plot_series


class WorkflowContractTests(unittest.TestCase):
    def test_figure_spec_round_trip_preserves_core_fields(self) -> None:
        spec = build_figure_spec(
            title="Stress response",
            figure_type="trend",
            x_label="Time (s)",
            y_label="Stress (MPa)",
            series=[
                PlotSeries(label="Case A", x=[0, 1, 2], y=[0.0, 1.5, 3.0]),
                PlotSeries(label="Case B", x=[0, 1, 2], y=[0.1, 1.4, 2.9]),
            ],
            width_mm=180,
            height_mm=120,
            dpi=300,
        )

        payload = figure_spec_to_dict(spec)
        restored = figure_spec_from_dict(payload)

        self.assertEqual(restored.title, "Stress response")
        self.assertEqual(restored.figure_type, "trend")
        self.assertEqual(restored.x_label, "Time (s)")
        self.assertEqual(restored.y_label, "Stress (MPa)")
        self.assertEqual(len(restored.series), 2)
        self.assertEqual(restored.width_mm, 180)
        self.assertEqual(restored.height_mm, 120)
        self.assertEqual(restored.dpi, 300)

    def test_tabular_result_loader_reads_csv_and_builds_plot_series(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "result.csv"
            path.write_text(
                "time,stress_A,stress_B\n"
                "0,0.0,0.1\n"
                "1,1.5,1.4\n"
                "2,3.0,2.9\n",
                encoding="utf-8",
            )

            dataset = load_tabular_result(path)
            series = dataset_to_plot_series(dataset, x_column="time", y_columns=["stress_A", "stress_B"])

        self.assertEqual(dataset.source.name, "result.csv")
        self.assertEqual(dataset.columns, ["time", "stress_A", "stress_B"])
        self.assertEqual(len(dataset.rows), 3)
        self.assertEqual([item.label for item in series], ["stress_A", "stress_B"])
        self.assertEqual(series[0].x, [0.0, 1.0, 2.0])
        self.assertEqual(series[1].y, [0.1, 1.4, 2.9])

    def test_tabular_result_loader_handles_utf8_bom(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "result.csv"
            path.write_text("\ufefftime,stress\n0,0.0\n1,1.5\n", encoding="utf-8")

            dataset = load_tabular_result(path)
            series = dataset_to_plot_series(dataset, x_column="time", y_columns=["stress"])

        self.assertEqual(dataset.columns, ["time", "stress"])
        self.assertEqual(series[0].x, [0.0, 1.0])

    def test_tabular_result_loader_normalizes_common_ansys_headers(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "ansys.csv"
            path.write_text(
                "Time [s],Equivalent Stress [MPa],Total Deformation [mm]\n"
                "0,12.5,0.01\n"
                "1,18.0,0.02\n",
                encoding="utf-8",
            )

            dataset = load_tabular_result(path)
            series = dataset_to_plot_series(dataset, x_column="time", y_columns=["stress", "displacement"])

        self.assertEqual(dataset.columns, ["time", "stress", "displacement"])
        self.assertEqual(series[0].y, [12.5, 18.0])
        self.assertEqual(series[1].y, [0.01, 0.02])

    def test_tabular_result_loader_normalizes_common_abaqus_headers(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "abaqus.csv"
            path.write_text(
                "Step Time,S: Mises,U: Magnitude,RF: Magnitude\n"
                "0,100,0.05,250\n"
                "1,120,0.07,275\n",
                encoding="utf-8",
            )

            dataset = load_tabular_result(path)
            series = dataset_to_plot_series(dataset, x_column="time", y_columns=["stress", "displacement", "force"])

        self.assertEqual(dataset.columns, ["time", "stress", "displacement", "force"])
        self.assertEqual(series[0].y, [100.0, 120.0])
        self.assertEqual(series[2].y, [250.0, 275.0])

    def test_tabular_result_loader_normalizes_common_comsol_headers(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "comsol.csv"
            path.write_text(
                "t (s),solid.mises (MPa),solid.disp (mm),T (K)\n"
                "0,80,0.01,293\n"
                "1,95,0.02,300\n",
                encoding="utf-8",
            )

            dataset = load_tabular_result(path)
            series = dataset_to_plot_series(dataset, x_column="time", y_columns=["stress", "displacement", "temperature"])

        self.assertEqual(dataset.columns, ["time", "stress", "displacement", "temperature"])
        self.assertEqual(series[0].y, [80.0, 95.0])
        self.assertEqual(series[2].y, [293.0, 300.0])

    def test_json_loader_accepts_list_of_records(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "result.json"
            path.write_text(
                json.dumps(
                    [
                        {"time": 0, "force": 10},
                        {"time": 1, "force": 11},
                    ],
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            dataset = load_tabular_result(path)

        self.assertEqual(dataset.columns, ["time", "force"])
        self.assertEqual(dataset.rows[1]["force"], 11)


if __name__ == "__main__":
    unittest.main()
