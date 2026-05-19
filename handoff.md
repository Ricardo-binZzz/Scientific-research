# Handoff

## Status

- Project scaffold, workflow docs, templates, and Python contract modules are in place.
- CLI supports `init`, `note`, `simulation`, `library`, `figure`, and `manuscript` commands.
- Literature entries can be added to and listed from `library-index.json`.
- Figure generation can create an SVG and JSON bundle from CSV/JSON data.
- Manuscript checking can inspect Markdown/plain-text drafts for citations, figure markers, and required headings.
- Library entries can be exported to BibTeX for Zotero import.
- BibTeX article entries can be imported back into the local library index.
- Common CSV metadata exports can be imported into the local library index with `library import-csv`.
- `library import-csv` now explicitly handles common Scopus and Web of Science CSV fields, including Scopus author full names and Web of Science publication names.
- Figure generation supports line and bar SVG output.
- Figure generation supports error-bar SVG output with `--figure-type errorbar` and matching `--y-error-column` arguments.
- Figure generation supports heatmap SVG output with `--figure-type heatmap` and `--value-column` for x/y/value grids.
- Figure generation supports contour SVG output with `--figure-type contour`; input must be a complete rectangular x/y/value grid.
- Manuscript checking can read `.docx` files by extracting Word XML text.
- Manuscript checking can compare citation keys against the local library through `--library-root`.
- Simulation data validation reports missing columns and non-numeric columns.
- Simulation CSV loading normalizes common ANSYS, Abaqus, and COMSOL export headers to stable names for validation and plotting.
- `simulation inspect-data` prints normalized columns and sample rows before validation or plotting.
- `simulation summarize-data` prints numeric count/min/max and flags columns containing non-numeric cells.
- `simulation check-ranges` checks expected numeric ranges with repeated `--range column:min:max` arguments.
- `README.md` documents the main workflow commands using the bundled Python executable.
- `unittest discover -v` now discovers and runs the full test suite.
- `project report` prints a compact status count for the active research workspace.
- `project check` prints a consolidated project health report using `project-check.json`.
- `project check` can also apply `simulation.ranges` from `project-check.json` to report out-of-range simulation values.
- `examples/` contains a minimal CSV and manuscript draft for quick command trials.
- `project writing-pack` can print or write a Markdown pack for manuscript drafting.
- CLI command execution is split into `workflow/commands.py`; `workflow/cli.py` now focuses on argument parsing.
- Manuscript checks recognize English and Chinese figure-number markers.
- Workspace templates include `simulation-metadata.json` for column-unit metadata.
- New workspaces include root-level `project-check.json` for default manuscript and simulation health-check settings.
- `simulation validate-data --metadata ...` reports numeric columns missing unit metadata.
- `simulation validate-data --metadata ...` also reports empty unit values and extra metadata columns not present in the dataset.
- Manuscript citation coverage reports both missing library citations and uncited library entries.
- Manuscript checks report duplicate English figure markers and skipped English figure numbers.
- `library check-pdfs` reports present and missing PDFs for indexed literature entries.
- `library stats` reports entry count, year range, missing PDF count, and source distribution.
- Global function check on 2026-05-18: `unittest discover -v` ran 54 tests with OK; CLI help, simulation validation, manuscript check, figure generation, and project report entry points were exercised successfully.
- Workflow expansion on 2026-05-19: CSV metadata import, error-bar plotting, manuscript figure-number quality checks, and stricter simulation unit metadata checks were implemented with focused tests.
- `USER_GUIDE.md` was added as the beginner-facing Chinese tutorial, and project instructions now require updating it when user-facing functionality changes.
- User preference recorded on 2026-05-19: future user-facing tutorial updates must go into `USER_GUIDE.md`; do not create separate tutorial files for new features unless explicitly requested.
- `USER_GUIDE.md` was reorganized on 2026-05-19 for beginner readability: new features were merged into the relevant workflow steps, a 10-minute quick-start was added, UTF-8 viewing guidance was added, and the old appended changelog-style section was removed.
- Workflow expansion on 2026-05-19: `project check` was added as a one-command health report, and new workspaces now get a default `project-check.json`.
- Workflow expansion on 2026-05-19: Scopus and Web of Science CSV metadata imports were covered with focused tests and documented in `USER_GUIDE.md`.
- Workflow expansion on 2026-05-19: common ANSYS, Abaqus, and COMSOL CSV result headers now normalize to stable simulation columns, with focused tests and `USER_GUIDE.md` updates.
- Workflow expansion on 2026-05-19: `simulation inspect-data` was added as a beginner-friendly preview step before validation and plotting.
- Workflow expansion on 2026-05-19: `simulation summarize-data` was added to report numeric ranges before strict validation and plotting.
- Workflow expansion on 2026-05-19: `simulation check-ranges` was added to flag out-of-range simulation results before plotting.
- Workflow expansion on 2026-05-19: `project check` now applies configured simulation range rules from `project-check.json`.
- Workflow expansion on 2026-05-19: `library stats` was added for a quick literature library overview before writing.
- Git setup on 2026-05-19: the repository now has a first local commit and tracks GitHub remote `origin` at `https://github.com/Ricardo-binZzz/Scientific-research.git`.
- GitHub push status on 2026-05-19: local branch `main` was pushed to `origin/main`; the existing remote README-only initial commit was merged without replacing the local project README.
- README language switch on 2026-05-19: `README.md` now links to `README.zh-CN.md`, and the Chinese README links back to the English entry point while keeping `USER_GUIDE.md` as the detailed beginner tutorial.
- Usage guide language switch on 2026-05-19: `USER_GUIDE.en.md` was added as the English beginner guide, `USER_GUIDE.md` links to it, and both README entry pages now point to the appropriate usage guides.

## Next Steps

- Add interpolation or smoothing for sparse 2D contour data when a real non-grid dataset requires it.
- Extend simulation export adapters when real ANSYS, Abaqus, or COMSOL files expose additional field names, units, or multi-table formats.
- Consider richer Scopus/Web of Science import fields later, such as abstracts, keywords, links, and citation counts, if the workflow starts using them.
