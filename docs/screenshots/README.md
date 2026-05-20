# Screenshots

This folder is reserved for GitHub-facing screenshots and short demo visuals.

Real browser screenshots:

1. `web-workbench-home.png` - the local web UI after loading `examples/demo-project`.
2. `workflow-status.png` - the guided workflow status result card.
3. `project-check.png` - the project health cards after running project check.

Recommended future captures:

4. `simulation-summary.png` - simulation inspection or summary cards.
5. `figure-result.png` - figure generation result cards with SVG/JSON paths.

Regenerate the current screenshots from the repository root with:

```powershell
node tools/capture_web_screenshots.js
```

The script starts `workflow.web_app`, loads `examples/demo-project`, drives the browser with Playwright, redacts visible local absolute paths, and writes PNG files back into this folder.

Additional generic preview assets:

- `web-workbench-preview.svg` - stylized workbench overview for README use.
- `project-check-preview.svg` - stylized project health card preview.

Keep screenshots generic. Do not include private file paths, unpublished paper content, private data, or identifiable personal information.
