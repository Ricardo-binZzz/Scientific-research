from __future__ import annotations

from argparse import Namespace
from pathlib import Path

from workflow.bootstrap import bootstrap_workspace
from workflow.library import (
    LibraryEntry,
    LibraryIndex,
    add_entry,
    export_bibtex,
    filter_library_by_source,
    filter_library_by_year,
    import_csv_metadata,
    import_bibtex,
    inspect_note_inventory,
    inspect_pdf_inventory,
    inspect_library_stats,
    load_index,
    render_index,
    render_library_stats,
    render_note_inventory_report,
    render_pdf_inventory_report,
    render_search_results,
    search_library,
)
from workflow.literature_map import build_literature_map, render_literature_map
from workflow.literature_table import build_literature_table, render_literature_table
from workflow.literature_tracker import build_literature_tracker, render_literature_tracker
from workflow.manuscript import inspect_manuscript, render_report_from_inspection
from workflow.notes import (
    LiteratureReviewParagraph,
    OutlineDraft,
    OutlineSection,
    PaperSummary,
    SearchLogEntry,
    create_note_file,
    render_literature_review,
    render_outline,
    render_paper_summary,
    render_search_log,
)
from workflow.project_report import build_project_check, build_project_report, render_project_check, render_project_report
from workflow.python.figure_exporter import build_contour_spec_from_dataset, build_heatmap_spec_from_dataset, build_spec_from_dataset, export_figure_bundle
from workflow.python.sim_result_loader import load_tabular_result
from workflow.simulation import (
    SimulationCase,
    check_dataset_ranges,
    collect_export_files,
    inspect_dataset,
    render_case_manifest,
    render_dataset_inspection,
    render_dataset_summary,
    render_range_check_report,
    render_dataset_validation_report,
    summarize_dataset,
    load_unit_metadata,
    validate_dataset_columns,
)
from workflow.writing_pack import build_writing_pack, render_writing_pack
from workflow.writing_dashboard import build_writing_dashboard, render_writing_dashboard


def handle_args(args: Namespace) -> int:
    if args.command == "init":
        bootstrap_workspace(Path(args.base_dir), project_slug=args.slug, project_name=args.name)
        return 0
    if args.command == "note":
        return _handle_note(args)
    if args.command == "simulation":
        return _handle_simulation(args)
    if args.command == "library":
        return _handle_library(args)
    if args.command == "figure":
        return _handle_figure(args)
    if args.command == "manuscript":
        return _handle_manuscript(args)
    if args.command == "project":
        return _handle_project(args)
    raise ValueError(f"Unsupported command: {args.command}")


def _handle_note(args: Namespace) -> int:
    notes_dir = Path(args.notes_dir)
    if args.note_type == "search-log":
        content = render_search_log(
            SearchLogEntry(
                question=args.question,
                keywords=args.keywords,
                query=args.query,
                source=args.source,
                date=args.date,
                filters=args.filters,
                result_count=args.result_count,
                notes=args.notes,
            )
        )
        create_note_file(notes_dir, note_type="search-log", title=args.question, content=content, timestamp=args.timestamp)
        return 0
    if args.note_type == "paper-summary":
        content = render_paper_summary(
            PaperSummary(
                title=args.title,
                authors=args.authors,
                source=args.source,
                year=args.year,
                doi=args.doi,
                problem=args.problem,
                method=args.method,
                data=args.data,
                key_figures=args.key_figures,
                main_result=args.main_result,
                limitation=args.limitation,
                reuse_value=args.reuse_value,
                source_pages=args.source_pages,
            )
        )
        create_note_file(notes_dir, note_type="paper-summary", title=args.title, content=content, timestamp=args.timestamp)
        return 0
    if args.note_type == "outline":
        sections = [
            OutlineSection(heading=item.split(":", 1)[0].strip(), bullets=[part.strip() for part in item.split(":", 1)[1].split("|") if part.strip()])
            if ":" in item
            else OutlineSection(heading=item, bullets=[])
            for item in args.sections
        ]
        content = render_outline(
            OutlineDraft(
                topic=args.topic,
                problem_statement=args.problem_statement,
                sections=sections,
                conclusion=args.conclusion,
            )
        )
        create_note_file(notes_dir, note_type="outline", title=args.topic, content=content, timestamp=args.timestamp)
        return 0
    if args.note_type == "literature-review":
        content = render_literature_review(
            LiteratureReviewParagraph(
                paper=args.paper,
                claim=args.claim,
                evidence=args.evidence,
                connection_to_current_work=args.connection,
                limit=args.limit,
            )
        )
        create_note_file(notes_dir, note_type="literature-review", title=args.paper, content=content, timestamp=args.timestamp)
        return 0
    raise ValueError(f"Unsupported note command: {args.note_type}")


def _handle_simulation(args: Namespace) -> int:
    if args.sim_command == "runbook":
        content = render_case_manifest(
            SimulationCase(
                name=args.name,
                software=args.software,
                version=args.version,
                geometry_source=args.geometry_source,
                material_set=args.material_set,
                boundary_conditions=args.boundary_conditions,
                mesh_summary=args.mesh_summary,
                solve_settings=args.solve_settings,
                export_format=args.export_format,
                validation_notes=args.validation_notes,
            )
        )
        create_note_file(Path(args.notes_dir), note_type="simulation", title=args.name, content=content, timestamp=args.timestamp)
        return 0
    if args.sim_command == "list-exports":
        for path in collect_export_files(Path(args.root_dir)):
            print(path.name)
        return 0
    if args.sim_command == "inspect-data":
        dataset = load_tabular_result(Path(args.data_path))
        print(render_dataset_inspection(inspect_dataset(dataset, sample_size=args.rows)))
        return 0
    if args.sim_command == "summarize-data":
        dataset = load_tabular_result(Path(args.data_path))
        print(render_dataset_summary(summarize_dataset(dataset)))
        return 0
    if args.sim_command == "check-ranges":
        dataset = load_tabular_result(Path(args.data_path))
        print(render_range_check_report(check_dataset_ranges(dataset, _parse_range_specs(args.ranges))))
        return 0
    if args.sim_command == "validate-data":
        dataset = load_tabular_result(Path(args.data_path))
        unit_metadata = load_unit_metadata(Path(args.metadata)) if args.metadata else None
        report = validate_dataset_columns(
            dataset,
            required_columns=args.required_columns,
            numeric_columns=args.numeric_columns,
            unit_metadata=unit_metadata,
        )
        print(render_dataset_validation_report(report))
        return 0
    raise ValueError(f"Unsupported simulation command: {args.sim_command}")


def _handle_library(args: Namespace) -> int:
    root = Path(args.root_dir)
    if args.library_command == "add":
        index = load_index(root)
        add_entry(
            root,
            index,
            LibraryEntry(
                title=args.title,
                authors=args.authors,
                year=args.year,
                source=args.source,
                doi=args.doi,
                pdf_name=args.pdf_name,
                note_path=args.note_path,
            ),
        )
        return 0
    if args.library_command == "list":
        print(render_index(load_index(root)))
        return 0
    if args.library_command == "export-bibtex":
        Path(args.out_path).write_text(export_bibtex(load_index(root)), encoding="utf-8")
        return 0
    if args.library_command == "import-bibtex":
        imported = import_bibtex(Path(args.bib_path).read_text(encoding="utf-8-sig"))
        combined = LibraryIndex(entries=[])
        for entry in load_index(root).entries + imported.entries:
            combined = add_entry(root, combined, entry)
        combined.save(root)
        return 0
    if args.library_command == "import-csv":
        imported = import_csv_metadata(Path(args.csv_path).read_text(encoding="utf-8-sig"))
        combined = LibraryIndex(entries=[])
        for entry in load_index(root).entries + imported.entries:
            combined = add_entry(root, combined, entry)
        combined.save(root)
        return 0
    if args.library_command == "check-pdfs":
        print(render_pdf_inventory_report(inspect_pdf_inventory(root, load_index(root))))
        return 0
    if args.library_command == "check-notes":
        print(render_note_inventory_report(inspect_note_inventory(root, load_index(root))))
        return 0
    if args.library_command == "stats":
        index = load_index(root)
        print(render_library_stats(inspect_library_stats(root, index)))
        return 0
    if args.library_command == "search":
        print(render_search_results(search_library(load_index(root), args.query)))
        return 0
    if args.library_command == "recent":
        print(render_search_results(filter_library_by_year(load_index(root), args.since)))
        return 0
    if args.library_command == "source":
        print(render_search_results(filter_library_by_source(load_index(root), args.query)))
        return 0
    if args.library_command == "map":
        content = render_literature_map(build_literature_map(root))
        if args.out:
            Path(args.out).write_text(content, encoding="utf-8")
        else:
            print(content)
        return 0
    raise ValueError(f"Unsupported library command: {args.library_command}")


def _handle_figure(args: Namespace) -> int:
    if args.figure_command == "from-data":
        dataset = load_tabular_result(Path(args.data_path))
        style_options = _figure_style_options(args)
        if args.figure_type == "heatmap":
            if not args.value_column:
                raise ValueError("value-column is required for heatmap figures")
            spec = build_heatmap_spec_from_dataset(
                dataset,
                title=args.title,
                x_column=args.x_column,
                y_column=args.y_columns[0],
                value_column=args.value_column,
                x_label=args.x_label,
                y_label=args.y_label,
                width_mm=args.width_mm,
                height_mm=args.height_mm,
                dpi=args.dpi,
                **style_options,
            )
        elif args.figure_type == "contour":
            if not args.value_column:
                raise ValueError("value-column is required for contour figures")
            spec = build_contour_spec_from_dataset(
                dataset,
                title=args.title,
                x_column=args.x_column,
                y_column=args.y_columns[0],
                value_column=args.value_column,
                x_label=args.x_label,
                y_label=args.y_label,
                width_mm=args.width_mm,
                height_mm=args.height_mm,
                dpi=args.dpi,
                **style_options,
            )
        else:
            spec = build_spec_from_dataset(
                dataset,
                title=args.title,
                figure_type=args.figure_type,
                x_column=args.x_column,
                y_columns=args.y_columns,
                y_error_columns=args.y_error_columns,
                x_label=args.x_label,
                y_label=args.y_label,
                width_mm=args.width_mm,
                height_mm=args.height_mm,
                dpi=args.dpi,
                **style_options,
            )
        export_figure_bundle(spec, Path(args.out_dir), stem=args.stem)
        return 0
    raise ValueError(f"Unsupported figure command: {args.figure_command}")


def _handle_manuscript(args: Namespace) -> int:
    if args.manuscript_command == "check":
        library_index = load_index(Path(args.library_root)) if args.library_root else None
        report = inspect_manuscript(
            Path(args.path),
            required_sections=args.required_sections,
            expected_figures=args.expected_figures,
            library_index=library_index,
        )
        print(render_report_from_inspection(report))
        return 0
    raise ValueError(f"Unsupported manuscript command: {args.manuscript_command}")


def _handle_project(args: Namespace) -> int:
    if args.project_command == "report":
        print(render_project_report(build_project_report(Path(args.root_dir))))
        return 0
    if args.project_command == "check":
        print(render_project_check(build_project_check(Path(args.root_dir))))
        return 0
    if args.project_command == "writing-pack":
        content = render_writing_pack(build_writing_pack(Path(args.root_dir)))
        if args.out:
            Path(args.out).write_text(content, encoding="utf-8")
        else:
            print(content)
        return 0
    if args.project_command == "literature-table":
        content = render_literature_table(build_literature_table(Path(args.root_dir) / "notes"))
        if args.out:
            Path(args.out).write_text(content, encoding="utf-8")
        else:
            print(content)
        return 0
    if args.project_command == "writing-dashboard":
        content = render_writing_dashboard(build_writing_dashboard(Path(args.root_dir)))
        if args.out:
            Path(args.out).write_text(content, encoding="utf-8")
        else:
            print(content)
        return 0
    if args.project_command == "literature-tracker":
        content = render_literature_tracker(build_literature_tracker(Path(args.root_dir)))
        if args.out:
            Path(args.out).write_text(content, encoding="utf-8")
        else:
            print(content)
        return 0
    raise ValueError(f"Unsupported project command: {args.project_command}")


def _parse_range_specs(items: list[str]) -> dict[str, tuple[float, float]]:
    ranges: dict[str, tuple[float, float]] = {}
    for item in items:
        parts = item.split(":")
        if len(parts) != 3:
            raise ValueError(f"Range must use column:min:max format: {item}")
        column, minimum, maximum = parts
        ranges[column] = (float(minimum), float(maximum))
    return ranges


def _figure_style_options(args: Namespace) -> dict[str, object]:
    return {
        "show_legend": args.show_legend == "true",
        "show_grid": args.show_grid == "true",
        "palette": args.palette,
        "title_font_size": args.title_font_size,
        "label_font_size": args.label_font_size,
        "tick_font_size": args.tick_font_size,
        "line_width": args.line_width,
        "tick_count": args.tick_count,
    }
