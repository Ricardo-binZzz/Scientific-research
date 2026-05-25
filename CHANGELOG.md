# Changelog

All notable changes to this project are summarized here.

## Unreleased

### Added

- `project check` now ends with `Next Actions`, turning project gaps into concrete follow-up steps.
- The web project-check companion now surfaces those `Next Actions` as a dedicated next-step card.
- Added `pyproject.toml` with project metadata, package data, and local CLI/web console-script entry points.
- Added `tools/check_js_syntax.py` to run `node --check` against web assets and the screenshot driver before regenerating real browser screenshots.
- DOCX manuscript QA now flags Word images and drawing objects that lack `descr` or `title` alternative text metadata.
- DOCX manuscript QA now flags leftover Word tracked changes and comment markers.
- DOCX manuscript QA now reports missing page size settings alongside missing page margins.
- DOCX manuscript QA now reports incomplete page size width/height attributes.
- DOCX manuscript QA now reports unresolved or missing DOCX header/footer target parts.
- DOCX manuscript QA now reports unresolved or missing embedded image target parts.
- DOCX manuscript QA now reports missing footnote and endnote target definitions.

### Changed

- Updated README maturity notes to match the current 162-test baseline.
- Split web action dispatch and action helpers into `workflow.web_actions`, leaving `workflow.web_app` focused on page rendering and HTTP serving.
- Updated README maturity notes again after the web action boundary test brought the baseline to 163 tests.
- Split result companion renderers into `workflow/web_assets/renderers.js`, leaving `app.js` focused on state, inputs, and event wiring.
- Split web action payload and preflight validation helpers into `workflow/web_assets/actions.js`, and fixed malformed frontend status/toast strings caught by `node --check`.
- Updated README maturity notes after the JavaScript syntax-check regression brought the baseline to 164 tests.
- Made `tools/capture_web_screenshots.js` resolve bundled Codex Playwright and Python paths automatically, then refreshed the real browser screenshots.
- Documented the screenshot viewport and expanded screenshot tests to validate PNG headers and `1440 x 980` dimensions.
- Updated README maturity notes after DOCX alt-text coverage brought the baseline to 166 tests.
- Updated README maturity notes after DOCX review-mark coverage brought the baseline to 167 tests.
- Updated README maturity notes after DOCX page-size dimension coverage brought the baseline to 168 tests.
- Updated README maturity notes after DOCX header/footer reference coverage brought the baseline to 169 tests.
- Updated README maturity notes after DOCX embedded-image target coverage brought the baseline to 170 tests.
- Updated README maturity notes after DOCX note-reference coverage brought the baseline to 172 tests.

## v0.1.0 - 2026-05-23

### Added

- Professional GitHub landing pages in English and Chinese.
- Real GitHub Actions badge and a 3-minute demo path in both README entry points.
- Real browser screenshots and screenshot capture guidance in `docs/screenshots`.
- Generic SVG preview assets for the web workbench and project-check output.
- `docs/releases/v0.1.0.md` release notes for creating the first GitHub release.
- Portable `start_web.bat` launcher that discovers `.venv`, `py`, or `python`.
- Dedicated project metadata files: `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md`, and this changelog.
- GitHub Actions test workflow for the Python unittest suite.
- Citation metadata in `CITATION.cff`.
- Project direction notes in `ROADMAP.md`.
- CI privacy scan for obvious local paths and secret-like assignments.
- Windows one-click setup through `install_windows.bat`.
- Crossref open metadata discovery and direct/open PDF URL download helpers.
- DOCX package-level QA checks for styles, page margins, and Word citation/bibliography field signals.
- External solver CLI command logging through `simulation run-command`.

### Changed

- Sanitized tracked documentation examples to avoid user-specific local paths.
- Repositioned the README around the local-first research workbench value proposition, web-first onboarding, demo project, core capabilities, differentiators, and documentation entry points.
- Clarified target users, expected outputs, and current non-goals in the README entry points.
- Added project maturity and comparison sections to the README entry points.
- Converted near-term roadmap items into checklist form.
- Made `examples/demo-project` a clean first-run demo with placeholder PDFs, complete citations, and a zero-issue project check.

## 2026-05-20

### Added

- Dedicated local web UI guide in `WEB_GUIDE.md`.
- Rich web result cards for project checks, manuscript checks, simulation reports, figure results, saved reports, notes, library actions, planning reports, project overview, workflow status, file scanning, and fallback guidance.
- Web preflight validation for common missing project roots and file paths.
- Literature metadata fields for abstracts, keywords, URLs, database sources, and citation counts.
- Richer writing reports and literature insights based on metadata coverage, high-citation candidates, keywords, and database sources.

### Changed

- Improved beginner documentation structure and clarified the roles of `USER_GUIDE.md` and `WEB_GUIDE.md`.
- Polished the local web UI toward a modern SaaS/professional workbench style.

## 2026-05-19

### Added

- Local browser UI for common project, literature, note, simulation, figure, and manuscript actions.
- Demo project under `examples/demo-project`.
- Writing pack, writing dashboard, literature table, literature map, and literature tracker reports.
- CSV/BibTeX literature import and export.
- Simulation inspection, numeric summaries, validation, range checks, and common solver header normalization.
- Figure generation for trend, bar, error-bar, heatmap, and contour plots.
- Manuscript checks for citations, figures, headings, `.docx` text extraction, and local library coverage.

### Changed

- Split CLI command execution from argument parsing.
- Expanded tests for the main workflow and web action handlers.
