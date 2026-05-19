import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from workflow.simulation import (
    SimulationCase,
    build_case_manifest,
    collect_export_files,
    render_case_manifest,
    load_unit_metadata,
    validate_dataset_columns,
)
from workflow.python.sim_result_loader import load_tabular_result
from workflow.cli import main


class SimulationBridgeTests(unittest.TestCase):
    def test_build_case_manifest_records_core_fields(self) -> None:
        case = SimulationCase(
            name="case-a",
            software="ANSYS",
            version="2024 R1",
            geometry_source="CAD model v3",
            material_set="steel",
            boundary_conditions="fixed + load",
            mesh_summary="coarse to fine",
            solve_settings="static structural",
            export_format="csv",
            validation_notes="check units",
        )

        manifest = build_case_manifest(case)

        self.assertIn("ANSYS", manifest)
        self.assertIn("case-a", manifest)
        self.assertIn("check units", manifest)

    def test_collect_export_files_discovers_tabular_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "result_a.csv").write_text("x,y\n0,1\n", encoding="utf-8")
            (root / "result_b.json").write_text('{"rows":[{"x":0,"y":2}]}', encoding="utf-8")
            (root / "ignore.txt").write_text("skip", encoding="utf-8")

            files = collect_export_files(root)

        self.assertEqual([path.name for path in files], ["result_a.csv", "result_b.json"])

    def test_render_case_manifest_lists_all_sections(self) -> None:
        case = SimulationCase(
            name="case-b",
            software="Abaqus",
            version="2023",
            geometry_source="geometry step",
            material_set="aluminum",
            boundary_conditions="clamped",
            mesh_summary="50000 elements",
            solve_settings="dynamic implicit",
            export_format="json",
            validation_notes="compare residuals",
        )

        text = render_case_manifest(case)

        self.assertIn("# Simulation Runbook", text)
        self.assertIn("Abaqus", text)
        self.assertIn("compare residuals", text)

    def test_cli_simulation_runbook_writes_note(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            exit_code = main(
                [
                    "simulation",
                    "runbook",
                    tmpdir,
                    "--name",
                    "case-c",
                    "--software",
                    "COMSOL",
                    "--version",
                    "6.2",
                    "--geometry-source",
                    "CAD",
                    "--material-set",
                    "steel",
                    "--boundary-conditions",
                    "load + clamp",
                    "--mesh-summary",
                    "120k elements",
                    "--solve-settings",
                    "stationary",
                    "--export-format",
                    "csv",
                    "--validation-notes",
                    "check dimensionless groups",
                    "--timestamp",
                    "20260518-090400",
                ]
            )

            self.assertEqual(exit_code, 0)
            files = list(Path(tmpdir).glob("20260518-090400-case-c*.md"))
            self.assertEqual(len(files), 1)
            content = files[0].read_text(encoding="utf-8")
            self.assertIn("COMSOL", content)

    def test_cli_simulation_list_exports_prints_csv_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "a.csv").write_text("x,y\n0,1\n", encoding="utf-8")
            (root / "b.json").write_text('{"rows":[{"x":0,"y":2}]}', encoding="utf-8")
            (root / "c.txt").write_text("skip", encoding="utf-8")

            output = StringIO()
            with redirect_stdout(output):
                exit_code = main(["simulation", "list-exports", tmpdir])

            self.assertEqual(exit_code, 0)
            self.assertIn("a.csv", output.getvalue())
            self.assertIn("b.json", output.getvalue())

    def test_validate_dataset_columns_reports_missing_and_non_numeric(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / "result.csv"
            path.write_text("time,stress,label\n0,1,A\n1,not-a-number,B\n", encoding="utf-8")
            dataset = load_tabular_result(path)

            report = validate_dataset_columns(
                dataset,
                required_columns=["time", "stress", "strain"],
                numeric_columns=["time", "stress"],
            )

        self.assertIn("strain", report.missing_columns)
        self.assertIn("stress", report.non_numeric_columns)

    def test_cli_simulation_validate_data_prints_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / "result.csv"
            path.write_text("time,stress\n0,1\n1,bad\n", encoding="utf-8")
            output = StringIO()

            with redirect_stdout(output):
                exit_code = main(
                    [
                        "simulation",
                        "validate-data",
                        str(path),
                        "--required-column",
                        "time",
                        "--required-column",
                        "strain",
                        "--numeric-column",
                        "stress",
                    ]
                )

            self.assertEqual(exit_code, 0)
            text = output.getvalue()
            self.assertIn("strain", text)
            self.assertIn("stress", text)

    def test_load_unit_metadata_reads_column_units(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "metadata.json"
            path.write_text('{"columns":{"time":"s","stress":"MPa"}}', encoding="utf-8")

            metadata = load_unit_metadata(path)

        self.assertEqual(metadata["time"], "s")
        self.assertEqual(metadata["stress"], "MPa")

    def test_cli_simulation_validate_data_reports_missing_unit_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            data_path = root / "result.csv"
            metadata_path = root / "metadata.json"
            data_path.write_text("time,stress\n0,1\n", encoding="utf-8")
            metadata_path.write_text('{"columns":{"time":"s"}}', encoding="utf-8")
            output = StringIO()

            with redirect_stdout(output):
                exit_code = main(
                    [
                        "simulation",
                        "validate-data",
                        str(data_path),
                        "--required-column",
                        "time",
                        "--required-column",
                        "stress",
                        "--numeric-column",
                        "time",
                        "--numeric-column",
                        "stress",
                        "--metadata",
                        str(metadata_path),
                    ]
                )

        self.assertEqual(exit_code, 0)
        self.assertIn("stress", output.getvalue())

    def test_validate_dataset_columns_reports_empty_and_extra_unit_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "result.csv"
            path.write_text("time,stress\n0,1\n", encoding="utf-8")
            dataset = load_tabular_result(path)

            report = validate_dataset_columns(
                dataset,
                required_columns=["time", "stress"],
                numeric_columns=["time", "stress"],
                unit_metadata={"time": "s", "stress": "", "temperature": "K"},
            )

        self.assertIn("stress", report.empty_unit_columns)
        self.assertIn("temperature", report.extra_unit_columns)
        self.assertFalse(report.ok)

    def test_cli_simulation_validate_data_prints_strict_metadata_findings(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            data_path = root / "result.csv"
            metadata_path = root / "metadata.json"
            data_path.write_text("time,stress\n0,1\n", encoding="utf-8")
            metadata_path.write_text('{"columns":{"time":"s","stress":"","temperature":"K"}}', encoding="utf-8")
            output = StringIO()

            with redirect_stdout(output):
                exit_code = main(
                    [
                        "simulation",
                        "validate-data",
                        str(data_path),
                        "--required-column",
                        "time",
                        "--required-column",
                        "stress",
                        "--numeric-column",
                        "time",
                        "--numeric-column",
                        "stress",
                        "--metadata",
                        str(metadata_path),
                    ]
                )

        self.assertEqual(exit_code, 0)
        text = output.getvalue()
        self.assertIn("Empty unit metadata: stress", text)
        self.assertIn("Extra unit metadata: temperature", text)


if __name__ == "__main__":
    unittest.main()
