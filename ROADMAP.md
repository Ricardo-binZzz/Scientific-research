# Roadmap

This roadmap keeps the project focused on practical, local-first research workflows. It is not a promise of delivery dates; it is a direction for prioritizing issues and pull requests.

## Near Term

- [x] Improve GitHub-facing README positioning and first-run demo path.
- [x] Add GitHub metadata, contribution templates, citation metadata, and CI privacy scanning.
- [x] Add real browser screenshots for the local web UI.
- [x] Make `examples/demo-project` a clean zero-issue first-run demo.
- [ ] Keep expanding beginner documentation for common literature, simulation, figure, and manuscript workflows.

## Workflow Improvements

- [ ] Add more simulation export adapters when real ANSYS, Abaqus, COMSOL, or other solver exports expose additional field names, units, or multi-table structures.
- [ ] Add optional interpolation or smoothing for sparse 2D contour-like data while keeping the current strict rectangular-grid path.
- [ ] Improve library import support for richer Zotero exports and additional database metadata variants.
- [ ] Add more manuscript checks for institution-specific Word formatting without requiring Microsoft Office.
- [ ] Improve report outputs so users can move from project health checks to the next concrete action faster.

## Web UI Improvements

- [x] Persist recent successful actions to localStorage.
- [ ] Consider cancellation support if long-running actions become common.
- [ ] Add file-picker helpers if the local browser environment can support a reliable path workflow.
- [ ] Continue improving result cards so users can understand outcomes before reading raw text reports.

## Out of Scope for Now

- Paywall bypass, institutional-login automation, or bulk publisher PDF harvesting.
- Cloud-first storage or account-based collaboration.
- Direct control of commercial simulation software GUIs, licenses, or model setup.
- Replacing Word, Zotero, or human paper review.
- Black-box paper writing or automatic thesis generation.

## Contribution Priorities

High-value contributions should be small, reproducible, and connected to a real research workflow. Good issues usually include:

- a sanitized sample CSV, Markdown, DOCX, or library index
- the current command or web UI action
- the expected report or generated file
- the actual confusing output, missing check, or workflow gap
