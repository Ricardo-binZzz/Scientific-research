# Contributing

Thanks for improving this research workflow workbench.

## Project Scope

This repository focuses on a local-first research workflow stack:

- literature intake and local library checks
- structured reading notes
- simulation data inspection and validation
- reproducible SVG/JSON figure generation
- manuscript quality checks
- a beginner-friendly local web UI and scriptable CLI

Keep changes inside that scope. Avoid unrelated app rewrites, broad framework migrations, or features that require cloud accounts by default.

## Development Setup

Use Python 3.10 or newer.

```powershell
$PY='C:\path\to\python.exe'
& $PY -m unittest discover -v
```

For the local browser UI:

```powershell
.\start_web.bat
```

## Change Guidelines

- Keep changes small and reviewable.
- Preserve the current file layout unless the workflow requires a change.
- Add or update focused tests for behavior changes.
- Update user-facing documentation when commands, workflows, assumptions, or web UI behavior change.
- Keep examples generic. Do not commit personal paths, account names, private datasets, tokens, keys, or unpublished paper content.

## Documentation Rules

- `README.md` is the English GitHub landing page.
- `README.zh-CN.md` is the Chinese GitHub landing page.
- `USER_GUIDE.md` is the overall Chinese beginner guide.
- `WEB_GUIDE.md` is the dedicated Chinese guide for the local web UI.
- `USER_GUIDE.en.md` is the English beginner guide.

When adding a visible workflow feature, update the relevant guide in the same change.

## Before Opening a Pull Request

Run:

```powershell
$PY='C:\path\to\python.exe'
& $PY -m unittest discover -v
git grep -n -I -E "C:\\Users\\YourRealName|sk-[A-Za-z0-9]|api[_-]?key|secret|password"
```

The privacy grep is a reminder to check for personal paths and secrets. Adjust the personal-path pattern for your own machine before running it.
