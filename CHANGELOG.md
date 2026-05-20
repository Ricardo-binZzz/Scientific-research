# Changelog

All notable changes to this project are summarized here.

## Unreleased

### Added

- Professional GitHub landing pages in English and Chinese.
- Real GitHub Actions badge and a 3-minute demo path in both README entry points.
- Screenshot capture guidance in `docs/screenshots`.
- Portable `start_web.bat` launcher that discovers `.venv`, `py`, or `python`.
- Dedicated project metadata files: `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md`, and this changelog.
- GitHub Actions test workflow for the Python unittest suite.
- Citation metadata in `CITATION.cff`.
- Project direction notes in `ROADMAP.md`.
- CI privacy scan for obvious local paths and secret-like assignments.

### Changed

- Sanitized tracked documentation examples to avoid user-specific local paths.
- Repositioned the README around the local-first research workbench value proposition, web-first onboarding, demo project, core capabilities, differentiators, and documentation entry points.
- Clarified target users, expected outputs, and current non-goals in the README entry points.

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
