# Current Status

## Implemented

- Workspace initialization with standard research folders and templates.
- Literature library JSON index with DOI/title de-duplication.
- BibTeX import/export for basic article records.
- Crossref open metadata discovery and direct/open PDF URL download helpers.
- PDF inventory checks for indexed literature entries.
- Search logs, paper summaries, literature review snippets, and outline note generation.
- Simulation runbooks, external solver command logging, export discovery, data validation, range checks, and unit metadata checks.
- Figure generation from CSV/JSON into SVG plus FigureSpec JSON.
- Line, bar, error-bar, heatmap, and contour SVG renderers.
- Manuscript checks for citations, figure markers, required headings, library citation coverage, captions, references, `.docx` text extraction, and basic DOCX package signals.
- Project status reports, project health checks, manuscript writing packs, literature tables, writing dashboards, literature maps, and literature trackers.
- Simulation validation can check required columns, numeric values, and missing unit metadata.
- A clean first-run demo project is included under `examples/demo-project`.
- End-to-end smoke test covering the main research workflow.

## Known Limits

- Literature discovery uses open Crossref metadata and user-provided direct/open PDF URLs only; it does not bypass paywalls or institutional login.
- DOCX checks inspect text and package-level signals, but do not render Word pages or validate full institution-specific formatting.
- BibTeX parsing targets common article fields and does not fully implement the BibTeX grammar.
- Figure rendering is lightweight SVG and does not yet support image overlays.
- Simulation automation can launch installed solver CLI commands and capture logs, but does not control commercial solver GUIs, licenses, or model setup.

## Recommended Next Work

1. Add richer Zotero/export metadata support when real user exports expose new fields.
2. Add optional interpolation or smoothing for sparse contour-like data.
3. Add institution-specific Word formatting checks when a real template is available.
4. Add adapters for common simulation export folders once a real ANSYS/Abaqus/COMSOL case is available.

## Verification

Run:

```powershell
$PY='C:\path\to\python.exe'
& $PY -m unittest discover -v
```

