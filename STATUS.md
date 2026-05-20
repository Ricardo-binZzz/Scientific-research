# Current Status

## Implemented

- Workspace initialization with standard research folders and templates.
- Literature library JSON index with DOI/title de-duplication.
- BibTeX import/export for basic article records.
- PDF inventory checks for indexed literature entries.
- Search logs, paper summaries, literature review snippets, and outline note generation.
- Simulation runbooks, export discovery, data validation, and unit metadata checks.
- Figure generation from CSV/JSON into SVG plus FigureSpec JSON.
- Line and bar SVG renderers.
- Manuscript checks for citations, figure markers, required headings, library citation coverage, and `.docx` text extraction.
- Project status reports and manuscript writing packs.
- Simulation validation can check required columns, numeric values, and missing unit metadata.
- Examples are included for simulation validation, manuscript checking, and figure generation.
- End-to-end smoke test covering the main research workflow.

## Known Limits

- Literature search and PDF download are not automated yet.
- DOCX checks inspect text only, not layout, styles, references, or comments.
- BibTeX parsing targets common article fields and does not fully implement the BibTeX grammar.
- Figure rendering is lightweight SVG and does not yet support error bars, contours, or image overlays.
- Simulation software is not controlled directly; the current bridge starts from exported CSV/JSON.

## Recommended Next Work

1. Add real paper metadata import from a source export format, such as Crossref CSV, Scopus CSV, or Zotero RDF.
2. Add figure types for error bars and contour-like grid data.
3. Add DOCX style/layout inspection using a document-specific runtime when needed.
4. Add adapters for common simulation export folders once a real ANSYS/Abaqus/COMSOL case is available.

## Verification

Run:

```powershell
$PY='C:\path\to\python.exe'
& $PY -m unittest discover -v
```

