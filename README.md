# Research Workflow Workbench

[中文](README.zh-CN.md) | English

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB)
![Tests](https://github.com/Ricardo-binZzz/Scientific-research/actions/workflows/tests.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue)
![Local first](https://img.shields.io/badge/local--first-no%20account-2E7D32)
![Interface](https://img.shields.io/badge/UI-web%20%2B%20CLI-455A64)

A local-first research workbench that connects literature notes, simulation checks, reproducible SVG figures, and manuscript QA in one beginner-friendly workflow.

It is built for mechanical and manufacturing research workflows where Zotero/Word, solver-exported data, figures, and thesis drafts need to stay traceable without forcing every user into a heavy workflow engine.

![Workflow guide](workflow/web_assets/workflow-guide.svg)

![Web workbench screenshot](docs/screenshots/web-workbench-home.png)

## Try the Demo in 3 Minutes

```powershell
.\start_web.bat
```

Then in the local web UI:

1. Load `examples/demo-project`.
2. Run `Workflow Status`.
3. Run `Scan Project Files`.
4. Run `Project Check`.
5. Try one literature, simulation, figure, or manuscript action.

The demo project includes sample literature, placeholder PDFs, notes, simulation data, a manuscript draft, and project-check settings. Its health check starts clean, so you can evaluate the workflow before using it on real research data.

## Why This Project?

Research projects often scatter important evidence across paper folders, reading notes, solver exports, spreadsheets, figure drafts, and manuscript files. This project keeps those pieces in one inspectable local workspace and adds lightweight checks before you write, plot, or submit.

It does not try to replace expert judgment, Zotero, Word, simulation software, or manual paper reading. Instead, it gives you repeatable checkpoints:

- What papers have been collected, summarized, and cited?
- Which PDFs or note files are still missing?
- Are simulation columns numeric, named consistently, and within expected ranges?
- Can a figure be regenerated from the same data and settings?
- Does the manuscript contain expected sections, citations, figure markers, captions, and references?

## Core Capabilities

| Area | What it does |
| --- | --- |
| Literature library | Add papers, import CSV/BibTeX metadata, search Crossref open metadata, download direct/open PDF links, search local records, check missing PDFs and notes |
| Reading notes | Generate structured paper-summary notes and search-log notes for review work |
| Writing preparation | Build writing packs, literature comparison tables, writing dashboards, literature maps, and search trackers |
| Simulation data | Run installed solver CLI commands with logs, inspect normalized columns, summarize numeric ranges, validate required columns, check units, and flag out-of-range values |
| Figure generation | Create SVG/JSON figure bundles from CSV/JSON data, including trend, bar, error-bar, heatmap, and contour plots |
| Manuscript QA | Check Markdown/plain text/DOCX drafts for citations, headings, figure markers, captions, tables, DOCX style/layout gaps, image target and alt-text gaps, review marks, hyperlink anchors, and Word reference-field issues |
| Local web UI | Use common workflows from a browser without typing Python commands |

![Project check screenshot](docs/screenshots/project-check.png)

## Who Is This For?

- Mechanical, manufacturing, and engineering researchers who manage literature, simulation exports, figures, and thesis drafts together.
- Students who want a local browser workflow before learning more Python automation.
- Researchers who need repeatable checks but still write in Word, manage references in Zotero, and review papers manually.
- Labs that want a transparent project folder structure instead of a cloud-only research workspace.

## Outputs You Get

- `literature/library-index.json` for local paper metadata.
- Paper-summary and search-log notes.
- Writing packs, literature tables, writing dashboards, literature maps, and search trackers.
- Simulation inspection, validation, summary, and range-check reports.
- SVG figures paired with JSON FigureSpec files.
- Manuscript QA reports for citations, sections, figures, captions, tables, and references.

## Quick Start

### Option A0: One-Click Windows Setup

On Windows, double-click `install_windows.bat` or run:

```powershell
.\install_windows.bat
```

It creates a local `.venv`, verifies the web app module, and creates `Research Workflow Web.bat` in the project folder and on the Desktop when possible. After that, double-click the launcher to open the browser workbench.

### Option A: Local Web UI

For beginners or daily use, start with the browser interface:

```powershell
.\start_web.bat
```

The launcher starts a local server on `127.0.0.1`, automatically tries the next port if `8000` is busy, and opens the actual URL after binding.

Recommended first run:

1. Open the web UI.
2. Load the demo project from `examples/demo-project`.
3. Run workflow status.
4. Scan project files.
5. Run project check.
6. Try literature, simulation, figure, and manuscript actions from the guided sections.

Detailed web guide: [WEB_GUIDE.md](WEB_GUIDE.md)

### Option B: Command Line

Use the Python runtime available in your environment:

```powershell
$PY='C:\path\to\python.exe'
& $PY -m workflow.cli init C:\path\to\workspace --slug demo-project --name "Demo Project"
```

Optional for contributors: the repository now includes `pyproject.toml`, so an editable install can expose `research-workflow` and `research-workflow-web` console scripts:

```powershell
& $PY -m pip install -e . --no-build-isolation
```

Create a project health report:

```powershell
& $PY -m workflow.cli project check C:\path\to\workspace
```

The report ends with `Next Actions`, turning missing PDFs, missing notes, simulation findings, and manuscript findings into concrete follow-up steps.

Generate a writing pack:

```powershell
& $PY -m workflow.cli project writing-pack C:\path\to\workspace --out writing-pack.md
```

Generate a figure from solver-exported data:

```powershell
& $PY -m workflow.cli figure from-data simulation/result.csv figures --stem stress-response --title "Stress response" --figure-type trend --x-column time --y-column stress --x-label "Time (s)" --y-label "Stress (MPa)"
```

Full beginner guide: [USER_GUIDE.en.md](USER_GUIDE.en.md)

## Demo Project

A runnable example workspace lives in [examples/demo-project](examples/demo-project). It includes:

- a small literature index
- placeholder PDF files for the indexed papers
- paper-summary notes
- a simulation CSV
- a manuscript draft
- project-check settings
- a literature tracker

Use it to evaluate the workflow before applying it to a real research project.

## Screenshots

Real browser screenshots captured from `examples/demo-project` live in [docs/screenshots](docs/screenshots):

- [Web workbench home](docs/screenshots/web-workbench-home.png)
- [Workflow status cards](docs/screenshots/workflow-status.png)
- [Project check cards](docs/screenshots/project-check.png)

Run `python tools/check_js_syntax.py` before regenerating screenshots, then use `node tools/capture_web_screenshots.js` after installing Playwright's Chromium browser.

## Project Maturity

This is an early-stage local-first workbench, not a mature package ecosystem. The current baseline is suitable for trial use, workflow evaluation, and focused contributions. It has a documented demo project, a web UI, a CLI, CI, privacy checks, citation metadata, and 174 unittest cases covering the main workflow modules, web action handlers, and JavaScript syntax check tooling.

## Project Layout

New workspaces use a consistent structure:

```text
literature/      paper files and library-index.json
notes/           search logs, paper summaries, tables, maps, trackers
manuscript/      draft material and writing reports
simulation/      solver exports and metadata
figures/         generated SVG/JSON figure bundles
templates/       reusable Markdown templates
project-check.json
literature-tracker.json
```

## What Makes It Different?

- Local-first: project data stays in normal files and folders.
- Beginner-friendly web UI: common tasks can be run from a browser.
- Scriptable CLI: the same workflow can be automated or versioned.
- Research-specific checks: literature assets, simulation data, figures, and manuscript structure are checked together.
- Human review points: the tool highlights gaps; it does not hide decisions behind opaque automation.
- Reproducible figures: SVG output is paired with a JSON spec that records plotting settings.

## How It Compares

| Tool | Primary focus | Relationship to this project |
| --- | --- | --- |
| Zotero | Reference management | Keep using it; this project tracks local reading notes, gaps, and writing assets around it. |
| Word | Manuscript writing | Keep writing in Word; this project adds lightweight text/structure checks. |
| Snakemake | General workflow automation | More powerful for computational pipelines; this project is narrower and beginner-oriented. |
| Cookiecutter Data Science | Data project structure | Similar folder-discipline idea, but tuned for literature, simulation, figures, and manuscripts. |
| This project | Local research workbench | Connects literature, simulation exports, figure bundles, and manuscript QA in one browser/CLI workflow. |

## Documentation

- [Chinese README](README.zh-CN.md)
- [Chinese beginner guide](USER_GUIDE.md)
- [Dedicated Chinese web UI guide](WEB_GUIDE.md)
- [English beginner guide](USER_GUIDE.en.md)
- [Examples](examples/README.md)
- [Contributing](CONTRIBUTING.md)
- [Security policy](SECURITY.md)
- [Changelog](CHANGELOG.md)
- [Roadmap](ROADMAP.md)

## Contributing

Issues and pull requests are welcome when they fit the local-first research workflow scope. Please use the GitHub issue templates and include sanitized sample data when a problem depends on CSV, Markdown, DOCX, or library-index input.

Before opening a pull request, run the test suite and check that no private paths, credentials, unpublished paper text, or private research data were committed.

## Citation

If this workbench helps your research workflow, cite it as software using [CITATION.cff](CITATION.cff). The citation file is contributor-based for v0.1.0 and can be refined as maintainership becomes more formal.

## What This Is Not

- Literature discovery is limited to open Crossref metadata and user-provided direct/open PDF URLs; it does not bypass publisher permissions, institutional login, or paywalls.
- It does not replace Zotero, Word, or human paper review.
- It does not directly control ANSYS, Abaqus, COMSOL, or other commercial solver GUIs, licenses, or model setup.
- It does not automatically write a thesis or paper.

## Current Limits

- DOCX checking inspects text and package-level signals, including page size presence and dimensions, header/footer part references, embedded image targets, footnote/endnote targets, hyperlink relationships and bookmark anchors, image alt-text metadata, and review marks, but does not render Word pages or validate full institution-specific formatting.
- Contour plots require a complete rectangular x/y/value grid.
- BibTeX support focuses on common article fields.

## Verification

```powershell
& $PY -m unittest discover -v
```

## Suggested GitHub About

Description:

```text
Local-first research workflow workbench for literature notes, simulation data checks, publication figures, and manuscript QA.
```

Topics:

```text
research-workflow, reproducible-research, academic-writing, literature-review, manuscript, simulation-data, scientific-figures, local-first, python
```
