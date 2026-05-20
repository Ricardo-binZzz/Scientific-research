# Research Workflow

Language: English | [中文](README.zh-CN.md)

This repository contains a semi-automated research workflow for mechanical and manufacturing research. It focuses on literature intake, structured notes, manuscript checks, simulation data validation, and figure generation.

For a beginner-friendly walkthrough, read [USER_GUIDE.en.md](USER_GUIDE.en.md). For the Chinese walkthrough, read [USER_GUIDE.md](USER_GUIDE.md). The local web UI has its own Chinese operating guide: [WEB_GUIDE.md](WEB_GUIDE.md).

## Quick Start

Use the bundled Python runtime in this environment:

```powershell
$PY='C:\path\to\python.exe'
& $PY -m workflow.cli init C:\path\to\workspace --slug demo-project --name "Demo Project"
```

The command creates:

- `literature`: paper files and `library-index.json`
- `notes`: search logs, summaries, outlines, and review paragraphs
- `manuscript`: draft material
- `simulation`: solver input/output records
- `figures`: generated SVG/JSON figure bundles
- `templates`: reusable Markdown templates

## Main Workflow

1. Record literature searches:

```powershell
& $PY -m workflow.cli note search-log notes --question "Adaptive clamping papers" --keyword "adaptive clamping" --query "adaptive clamping fixture" --source Scopus --date 2026-05-18 --filters "2020-2026" --result-count 12 --notes "Focus on mechanism design."
```

2. Add reviewed papers to the local library:

```powershell
& $PY -m workflow.cli library add literature --title "Adaptive clamping fixture" --author Zhang --author Li --year 2024 --source "Journal of Manufacturing Systems" --doi "10.1000/example" --pdf-name paper.pdf --note-path notes/summary.md
```

Check whether indexed PDFs exist:

```powershell
& $PY -m workflow.cli library check-pdfs literature
```

3. Export or import BibTeX for Zotero:

```powershell
& $PY -m workflow.cli library export-bibtex literature export.bib
& $PY -m workflow.cli library import-bibtex literature export.bib
```

Import paper metadata from a CSV export:

```powershell
& $PY -m workflow.cli library import-csv literature papers.csv
```

The CSV importer recognizes common headers including `Title`, `Authors`, `Year`, `Source title`, `Journal`, `DOI`, `PDF`/`File`, and `Notes`/`Note`.

4. Validate simulation data:

```powershell
& $PY -m workflow.cli simulation validate-data simulation/result.csv --required-column time --required-column stress --numeric-column time --numeric-column stress
```

Add `--metadata templates/simulation-metadata.json` to also check unit metadata for numeric columns.
The metadata report flags missing units, empty unit values, and unit entries for columns that are not in the dataset.

5. Generate figures from CSV/JSON data:

```powershell
& $PY -m workflow.cli figure from-data simulation/result.csv figures --stem stress-response --title "Stress response" --figure-type trend --x-column time --y-column stress --x-label "Time (s)" --y-label "Stress (MPa)"
```

Use `--figure-type bar` for a basic bar chart.
Use `--figure-type heatmap` with `--x-column`, `--y-column`, and `--value-column` for dense x/y/value grid data.
Use `--figure-type contour` with the same x/y/value columns when the data forms a complete rectangular grid.
Use `--figure-type errorbar` with matching `--y-error-column` values for mean plus error plots:

```powershell
& $PY -m workflow.cli figure from-data simulation/result.csv figures --stem stress-error --title "Stress response" --figure-type errorbar --x-column time --y-column stress --y-error-column stress_sd --x-label "Time (s)" --y-label "Stress (MPa)"
```

6. Check manuscript drafts:

```powershell
& $PY -m workflow.cli manuscript check manuscript/chapter.md --required-section Introduction --required-section Method --expected-figure "Figure 1" --library-root literature
```

7. Print a project status report:

```powershell
& $PY -m workflow.cli project report .
```

8. Generate a writing pack:

```powershell
& $PY -m workflow.cli project writing-pack . --out writing-pack.md
```

## Current Limits

- Literature search and paper download are still manual or external-tool steps.
- The figure renderer currently supports line and bar SVG output.
- Error-bar SVG output is supported for tabular data with one error column per y-series.
- Heatmap and contour SVG output are supported for x/y/value data; contour input must form a complete rectangular grid.
- DOCX checking extracts text from Word XML but does not yet inspect Word styles or layout.
- Manuscript checks report duplicate English figure markers and skipped English figure numbers.
- BibTeX parsing supports basic article entries and common fields.

## Verification

```powershell
& $PY -m unittest discover -v
```

## Examples

Small sample inputs live in `examples/`:

- `examples/simulation-result.csv`
- `examples/chapter.md`

See `examples/README.md` for commands that validate data, check a manuscript draft, and generate an SVG figure.
