# Project Memory

## Current Direction

- This repository is for a semi-automated research workflow centered on literature intake, reading notes, thesis writing, figure generation, and simulation-to-Python plotting.
- The first version targets mechanical/manufacturing research.
- The preferred writing stack is Word + Zotero.

## Working Rules

- Keep workflows split into clear stages with explicit human review points.
- Treat simulation software output as an upstream data source, not a place to fully automate control in v1.
- Prefer reusable templates and compact contracts over broad automation.
- The CLI currently supports workspace initialization, note creation, simulation runbook/export listing, and literature library indexing.
- The literature library stores entries in `literature/library-index.json` and de-duplicates by DOI first, then normalized title.
- The figure pipeline now converts CSV/JSON tabular data into a FigureSpec JSON plus SVG line plot bundle.
- CSV loading uses `utf-8-sig` so PowerShell-generated UTF-8 files with BOM keep the expected first column name.
- Simulation CSV loading normalizes common ANSYS, Abaqus, and COMSOL export headers to stable names such as `time`, `stress`, `displacement`, `force`, and `temperature`; unmatched custom columns keep their original names.
- The manuscript checker currently supports Markdown/plain-text drafts, extracts `[@citation]` markers and `Figure N` markers, and checks required headings.
- Manuscript text loading also uses `utf-8-sig` to handle PowerShell-generated Markdown with BOM.
- The library can export basic BibTeX article entries through `library export-bibtex`.
- The library can import basic BibTeX article entries through `library import-bibtex` and merge them into `library-index.json`.
- The library can import common CSV metadata exports through `library import-csv`; supported headers include title, authors, year, source/journal, DOI, PDF/file, and notes/note.
- `library import-csv` has explicit coverage for common Scopus and Web of Science exports, including Scopus `Author full names` and Web of Science `Publication Name`.
- Figure SVG export supports both line plots and basic bar charts selected by `figure_type`.
- Figure SVG export also supports error-bar plots with `figure_type=errorbar` and one y-error column per y-series.
- Figure SVG export also supports heatmap plots with `figure_type=heatmap` for x/y/value grid data.
- Figure SVG export also supports contour plots with `figure_type=contour`; contour data must be a complete rectangular x/y/value grid.
- The manuscript checker can read `.docx` text directly from `word/document.xml` without requiring Office.
- Manuscript checks can compare extracted citation keys against a local library index via `--library-root` and report missing citations.
- Simulation data can be validated with `simulation validate-data` for required columns and numeric columns.
- Simulation data can be previewed with `simulation inspect-data`, which prints normalized columns and a few sample rows before validation or plotting.
- Simulation data can be summarized with `simulation summarize-data`, which reports count/min/max for numeric values and flags columns that contain non-numeric cells.
- Simulation data can be range-checked with `simulation check-ranges --range column:min:max`, reporting out-of-range and non-numeric counts.
- `README.md` documents the main CLI workflow and uses the bundled Python path because PATH `python` may be unavailable.
- User-facing tutorial updates must be merged into `USER_GUIDE.md`; do not create extra tutorial files for feature additions unless the user explicitly asks.
- Project status can be summarized with `project report`, which counts library entries, notes, figure bundles, simulation exports, and manuscript files.
- Project health can be checked with `project check`, which uses `project-check.json` to inspect literature PDFs, simulation exports, manuscript issues, and a summary count.
- A manuscript writing pack can be generated with `project writing-pack`, summarizing literature titles, note files, figure bundles, and simulation exports.
- Manuscript figure marker extraction supports both English `Figure N` and Chinese `图 N` forms.
- New workspaces include a `simulation-metadata.json` template for column-unit metadata.
- New workspaces include a root `project-check.json` template for default manuscript and simulation health-check settings.
- `simulation validate-data` accepts `--metadata` and reports numeric columns missing unit metadata.
- Simulation metadata validation also reports empty unit values and unit entries for columns absent from the dataset.
- Manuscript checks also report library citekeys that are not cited in the manuscript, useful for reference cleanup.
- Manuscript checks report duplicate English figure markers and skipped English figure numbers.
- `library check-pdfs` reports which indexed PDF files are present or missing.
- `USER_GUIDE.md` is the beginner-facing Chinese usage tutorial. Future user-facing features, command changes, workflow changes, or assumption changes should be reflected there.
- The repository remote is `https://github.com/Ricardo-binZzz/Scientific-research.git`; local branch `main` tracks `origin/main`.
- GitHub landing documentation uses `README.md` as the English entry point and `README.zh-CN.md` as the Chinese entry point, linked from the top of each file.
- Beginner usage guidance now exists in both `USER_GUIDE.md` (Chinese) and `USER_GUIDE.en.md` (English), with language links at the top of each guide.
