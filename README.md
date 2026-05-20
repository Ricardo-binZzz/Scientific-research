# Research Workflow Workbench

[中文](README.zh-CN.md) | English

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB)
![Tests](https://img.shields.io/badge/tests-unittest-2E7D32)
![License](https://img.shields.io/badge/license-MIT-blue)
![Local first](https://img.shields.io/badge/local--first-no%20account-2E7D32)
![Interface](https://img.shields.io/badge/UI-web%20%2B%20CLI-455A64)

A local-first research workbench for literature intake, structured reading notes, simulation data checks, publication-ready SVG figures, and manuscript QA.

It is designed for mechanical and manufacturing research workflows where you need a practical bridge between Zotero/Word, solver-exported data, figure generation, and thesis or paper drafting.

![Workflow guide](workflow/web_assets/workflow-guide.svg)

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
| Literature library | Add papers, import CSV/BibTeX metadata, search by title/author/source/DOI/abstract/keywords, check missing PDFs and notes |
| Reading notes | Generate structured paper-summary notes and search-log notes for review work |
| Writing preparation | Build writing packs, literature comparison tables, writing dashboards, literature maps, and search trackers |
| Simulation data | Inspect normalized columns, summarize numeric ranges, validate required columns, check units, and flag out-of-range values |
| Figure generation | Create SVG/JSON figure bundles from CSV/JSON data, including trend, bar, error-bar, heatmap, and contour plots |
| Manuscript QA | Check Markdown/plain text/DOCX drafts for citations, headings, figure markers, captions, tables, and reference-section issues |
| Local web UI | Use common workflows from a browser without typing Python commands |

## Quick Start

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

Create a project health report:

```powershell
& $PY -m workflow.cli project check C:\path\to\workspace
```

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
- paper-summary notes
- a simulation CSV
- a manuscript draft
- project-check settings
- a literature tracker

Use it to evaluate the workflow before applying it to a real research project.

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

## Documentation

- [Chinese README](README.zh-CN.md)
- [Chinese beginner guide](USER_GUIDE.md)
- [Dedicated Chinese web UI guide](WEB_GUIDE.md)
- [English beginner guide](USER_GUIDE.en.md)
- [Examples](examples/README.md)
- [Contributing](CONTRIBUTING.md)
- [Security policy](SECURITY.md)
- [Changelog](CHANGELOG.md)

## Current Limits

- Literature search and paper downloads are still manual or handled by external tools.
- DOCX checking extracts text from Word XML but does not inspect Word layout or styles.
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
