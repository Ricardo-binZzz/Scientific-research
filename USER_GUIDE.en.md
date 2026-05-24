# Beginner Guide for the Research Workflow

Language: English | [中文](USER_GUIDE.md)

This guide is for first-time users of this research workflow. It explains what each folder is for, which command to run at each step, where human review is required, and where to find the results.

Use an editor that supports UTF-8 when reading or editing project documents. If Chinese text appears garbled in Windows PowerShell, check that the file is being read as UTF-8.

When user-facing features, commands, workflows, or assumptions change, update this guide together with the Chinese guide.

## 1. What This Tool Does

This workflow does not write a full paper for you automatically. It breaks the research process into traceable steps:

1. Search for papers and record the search process.
2. Download PDFs and manually decide whether each paper is worth adding to the library.
3. Create paper summary cards with reusable findings, page references, and limitations.
4. Generate paper outlines, review paragraph material, and writing packs.
5. Accept CSV/JSON data exported from tools such as ANSYS, Abaqus, and COMSOL.
6. Check simulation fields, numeric values, and unit metadata.
7. Generate Python-based research figures, including line charts, bar charts, error-bar charts, heatmaps, and contour plots.
8. Check manuscript drafts for citations, figure markers, required sections, and local-library coverage.

Human review remains important. You still need to judge whether a paper is reliable, whether a simulation setup is reasonable, and whether a generated figure is suitable for a paper.

## 2. Do Not Confuse the Two Directory Types

The current folder is the tool repository:

```text
C:\Users\YourName\Documents\科研
```

For each real research topic, create a separate project workspace, for example:

```text
C:\Users\YourName\Documents\fixture-study
```

The tool repository provides commands. The research workspace stores papers, notes, simulation data, manuscript drafts, and generated figures.

## 3. Open PowerShell and Set Python

First enter the tool repository:

```powershell
cd C:\Users\YourName\Documents\科研
```

Set the Python executable used in this environment:

```powershell
$PY='C:\path\to\python.exe'
```

All later commands assume that `$PY` has already been set.

Optional: if you want command entry points instead of typing `-m workflow.cli`, run this from the tool repository:

```powershell
& $PY -m pip install -e . --no-build-isolation
```

After that, use `research-workflow` for the CLI or `research-workflow-web` for the local web UI. You can also skip installation and keep using the `$PY -m workflow.cli ...` commands below.

## 4. Ten-Minute Quick Check

Before creating your own workspace, use the built-in examples to confirm that the tool can run.

Validate the sample simulation data:

```powershell
& $PY -m workflow.cli simulation validate-data C:\Users\YourName\Documents\科研\examples\simulation-result.csv `
  --required-column time `
  --required-column stress `
  --numeric-column time `
  --numeric-column stress
```

Generate a sample figure:

```powershell
& $PY -m workflow.cli figure from-data C:\Users\YourName\Documents\科研\examples\simulation-result.csv C:\Users\YourName\Documents\科研\examples\output `
  --stem quick-check `
  --title "Quick check" `
  --figure-type trend `
  --x-column time `
  --y-column stress `
  --x-label "Time (s)" `
  --y-label "Stress (MPa)"
```

Check the sample manuscript draft:

```powershell
& $PY -m workflow.cli manuscript check C:\Users\YourName\Documents\科研\examples\chapter.md `
  --required-section Introduction `
  --expected-figure "Figure 1"
```

If all three commands work, create your own research workspace next.

## 5. Create a New Research Workspace

Example: create a fixture optimization workspace.

```powershell
& $PY -m workflow.cli init C:\Users\YourName\Documents --slug fixture-study --name "Fixture Optimization Study"
```

The generated folder looks roughly like this:

```text
fixture-study
|-- literature           # PDFs and library-index.json
|-- notes                # search logs, paper summaries, outlines, review paragraphs
|-- manuscript           # manuscript drafts
|-- simulation           # data exported from simulation tools
|-- figures              # generated paper figures
|-- templates            # reusable templates
`-- project-check.json   # default project health-check configuration
```

`project-check.json` stores default health-check rules, such as required manuscript sections, expected figure markers, required simulation columns, numeric columns, and unit metadata files. Beginners can leave it unchanged at first and adjust it after the project structure becomes stable.

## 6. Record a Paper Search

After searching in Google Scholar, Web of Science, Scopus, CNKI, or another database, record the search conditions:

```powershell
& $PY -m workflow.cli note search-log C:\Users\YourName\Documents\fixture-study\notes `
  --question "Adaptive fixture optimization research" `
  --keyword "adaptive fixture" `
  --keyword "clamping force optimization" `
  --query "adaptive fixture clamping force optimization" `
  --source "Google Scholar" `
  --date "2026-05-18" `
  --filters "2020-2026" `
  --result-count 12 `
  --notes "Prioritize mechanical structure, clamping force, and finite-element validation."
```

The command writes a search-log note in the `notes` folder.

## 7. Manually Review Downloaded PDFs First

Put downloaded PDFs here:

```text
C:\Users\YourName\Documents\fixture-study\literature
```

Before adding a paper to the library, check:

- Is the paper relevant to the topic?
- Does it provide clear methods, data, figures, or conclusions?
- Can its findings be reused in your manuscript?
- Are there obvious limitations or conditions where it does not apply?

Do not add every downloaded PDF. Add only papers that are useful enough to track.

## 8. Create a Paper Summary Card

```powershell
& $PY -m workflow.cli note paper-summary C:\Users\YourName\Documents\fixture-study\notes `
  --title "Adaptive clamping fixture design" `
  --author "Zhang" `
  --author "Li" `
  --source "Journal of Manufacturing Systems" `
  --year 2024 `
  --doi "10.1000/example" `
  --problem "Traditional fixtures adapt poorly to complex parts" `
  --method "Build an adaptive clamping mechanism and validate it with finite-element analysis" `
  --data "Clamping force, deformation, and stress distribution" `
  --key-figures "Fig. 3 structure diagram; Fig. 6 stress contour" `
  --main-result "Clamping deformation decreased by about 20%" `
  --limitation "Small experimental sample size" `
  --reuse-value "Can reuse its clamping-force evaluation indicators" `
  --source-pages "pp. 4-8"
```

A useful summary card records where each important conclusion came from. Page references make later manuscript writing easier to verify.

## 9. Add Reviewed Papers to the Literature Library

Add one paper manually:

```powershell
& $PY -m workflow.cli library add C:\Users\YourName\Documents\fixture-study\literature `
  --title "Adaptive clamping fixture design" `
  --author "Zhang" `
  --author "Li" `
  --year 2024 `
  --source "Journal of Manufacturing Systems" `
  --doi "10.1000/example" `
  --pdf-name "adaptive-clamping-fixture-design.pdf" `
  --note-path "notes/paper-summary-adaptive-clamping-fixture-design.md"
```

If you exported paper metadata as CSV from Scopus, Web of Science, Crossref, or another platform, import it in bulk:

```powershell
& $PY -m workflow.cli library import-csv C:\Users\YourName\Documents\fixture-study\literature C:\Users\YourName\Documents\fixture-study\papers.csv
```

Common CSV headers are recognized automatically, including `Title`, `Article Title`, `Authors`, `Author full names`, `Year`, `Publication Year`, `Source title`, `Publication Name`, `Journal`, `DOI`, `PDF`, `File`, `Notes`, and `Note`. Scopus full-author fields and Web of Science publication-name fields are handled where possible. Imports de-duplicate by DOI first, then by normalized title.

CSV exports often do not contain local PDF file names. After importing, the `PDF` field may be empty. You can later rename PDFs manually in the `literature` folder or use `library check-pdfs` to find missing files.

List the library:

```powershell
& $PY -m workflow.cli library list C:\Users\YourName\Documents\fixture-study\literature
```

Check missing PDFs:

```powershell
& $PY -m workflow.cli library check-pdfs C:\Users\YourName\Documents\fixture-study\literature
```

Export BibTeX for Zotero:

```powershell
& $PY -m workflow.cli library export-bibtex C:\Users\YourName\Documents\fixture-study\literature C:\Users\YourName\Documents\fixture-study\export.bib
```

Import basic BibTeX entries back into the local library:

```powershell
& $PY -m workflow.cli library import-bibtex C:\Users\YourName\Documents\fixture-study\literature C:\Users\YourName\Documents\fixture-study\export.bib
```

## 10. Generate a Manuscript Outline

```powershell
& $PY -m workflow.cli note outline C:\Users\YourName\Documents\fixture-study\notes `
  --topic "Adaptive fixture optimization research" `
  --problem-statement "Complex-part machining lacks fixture adaptability and clamping stability" `
  --section "Introduction:background|existing problems|contribution" `
  --section "Method:structure design|simulation model|evaluation indicators" `
  --section "Results:clamping force results|stress results|comparison analysis" `
  --conclusion "Propose a verifiable fixture optimization workflow"
```

Use the generated outline as a starting point, then manually revise it into your actual chapter structure.

## 11. Generate Literature Review Material

```powershell
& $PY -m workflow.cli note literature-review C:\Users\YourName\Documents\fixture-study\notes `
  --paper "Zhang et al. 2024" `
  --claim "Adaptive fixtures can reduce deformation during complex-part clamping" `
  --evidence "The authors compare stress distributions between conventional and adaptive fixtures using finite-element analysis" `
  --connection "This study can reuse the clamping-force evaluation indicators and add manufacturing constraints" `
  --limit "The experimental sample size is small, so generalization still needs validation"
```

Each key claim in a review paragraph should trace back to a paper, page range, or summary card.

## 12. Use Simulation Data

Export CSV or JSON from tools such as ANSYS, Abaqus, and COMSOL, then place the files here:

```text
C:\Users\YourName\Documents\fixture-study\simulation
```

CSV loading recognizes some common simulation headers and converts them to stable column names:

- Time: `Time [s]`, `Step Time`, `t (s)` -> `time`
- Stress: `Equivalent Stress [MPa]`, `S: Mises`, `solid.mises (MPa)` -> `stress`
- Displacement or deformation: `Total Deformation [mm]`, `U: Magnitude`, `solid.disp (mm)` -> `displacement`
- Reaction force or load: `RF: Magnitude`, `Reaction Force` -> `force`
- Temperature: `T (K)`, `Temperature` -> `temperature`

This means many CSV files exported directly from ANSYS, Abaqus, or COMSOL can be checked and plotted with standard names such as `time`, `stress`, `displacement`, `force`, and `temperature`. If a header is not recognized, pass the original CSV column name to the command.

Suppose the exported file is:

```text
C:\Users\YourName\Documents\fixture-study\simulation\result.csv
```

If it contains `time` and `stress`, validate it:

```powershell
& $PY -m workflow.cli simulation validate-data C:\Users\YourName\Documents\fixture-study\simulation\result.csv `
  --required-column time `
  --required-column stress `
  --numeric-column time `
  --numeric-column stress
```

If you have unit metadata like this:

```json
{"columns":{"time":"s","stress":"MPa"}}
```

validate data and metadata together:

```powershell
& $PY -m workflow.cli simulation validate-data C:\Users\YourName\Documents\fixture-study\simulation\result.csv `
  --required-column time `
  --required-column stress `
  --numeric-column time `
  --numeric-column stress `
  --metadata C:\Users\YourName\Documents\fixture-study\templates\simulation-metadata.json
```

Common report messages:

- `Missing columns`: required columns are absent.
- `Non-numeric columns`: a column that should be numeric contains text or empty values.
- `Missing unit metadata`: a numeric column has no unit record.
- `Empty unit metadata`: a unit field exists but is empty.
- `Extra unit metadata`: metadata includes a column that is not present in the dataset.

## 13. Generate Paper Figures

### Line Chart

Use a line chart for time responses, load-deformation curves, and other continuous data:

```powershell
& $PY -m workflow.cli figure from-data C:\Users\YourName\Documents\fixture-study\simulation\result.csv C:\Users\YourName\Documents\fixture-study\figures `
  --stem stress-response `
  --title "Stress response" `
  --figure-type trend `
  --x-column time `
  --y-column stress `
  --x-label "Time (s)" `
  --y-label "Stress (MPa)"
```

### Bar Chart

Use a bar chart for comparing different schemes, cases, or samples. Change the figure type:

```powershell
--figure-type bar
```

### Error-Bar Chart

If simulation or experiment data contains a mean column and an error column, such as `stress` and `stress_sd`, run:

```powershell
& $PY -m workflow.cli figure from-data C:\Users\YourName\Documents\fixture-study\simulation\result.csv C:\Users\YourName\Documents\fixture-study\figures `
  --stem stress-error `
  --title "Stress response" `
  --figure-type errorbar `
  --x-column time `
  --y-column stress `
  --y-error-column stress_sd `
  --x-label "Time (s)" `
  --y-label "Stress (MPa)"
```

Each `--y-column` needs one matching `--y-error-column`.

### Heatmap and Contour Plot

For `x, y, value` data, generate a two-dimensional plot:

```powershell
& $PY -m workflow.cli figure from-data C:\Users\YourName\Documents\fixture-study\simulation\grid.csv C:\Users\YourName\Documents\fixture-study\figures `
  --stem temperature-field `
  --title "Temperature field" `
  --figure-type heatmap `
  --x-column x `
  --y-column y `
  --value-column value `
  --x-label X `
  --y-label Y
```

Change `--figure-type heatmap` to `--figure-type contour` to generate a contour plot. Contour input must form a complete rectangular grid.

Outputs are written to the `figures` folder:

```text
figures\stress-response.svg
figures\stress-response.json
```

The `.svg` file is the figure. The `.json` file records figure parameters and data sources for reproducibility.

## 14. Check a Manuscript Draft

Put drafts here:

```text
C:\Users\YourName\Documents\fixture-study\manuscript
```

Check Markdown, plain text, or basic `.docx` drafts:

```powershell
& $PY -m workflow.cli manuscript check C:\Users\YourName\Documents\fixture-study\manuscript\chapter.md `
  --required-section Introduction `
  --required-section Method `
  --expected-figure "Figure 1" `
  --library-root C:\Users\YourName\Documents\fixture-study\literature
```

The check reports:

- Which citations are recognized.
- Which figure markers are recognized.
- Whether required sections exist.
- Whether manuscript citations can be found in the local literature library.
- Whether the library contains entries that are not cited.
- Whether English figure markers are duplicated, such as repeated `Figure 1`.
- Whether English figure numbers are skipped, such as `Figure 1` and `Figure 3` with no `Figure 2`.
- Whether `.docx` images or drawing objects are missing alternative text in Word `descr` or `title` metadata.

## 15. View Project Status and Run a Health Check

```powershell
& $PY -m workflow.cli project report C:\Users\YourName\Documents\fixture-study
```

This counts literature entries, notes, figures, simulation exports, and manuscript drafts.

To check the whole project at once:

```powershell
& $PY -m workflow.cli project check C:\Users\YourName\Documents\fixture-study
```

`project check` summarizes:

- Literature entry count.
- Missing PDFs recorded in the literature library.
- Whether simulation CSV/JSON files are readable, required columns exist, numeric columns are numeric, and unit metadata is complete.
- Whether drafts are missing required sections, figure markers, or citations.
- Whether citations can be found in the local library.
- Whether figure markers are duplicated or skipped.
- Counts for notes, figures, simulation exports, and manuscript files.

## 16. Generate a Writing Pack

```powershell
& $PY -m workflow.cli project writing-pack C:\Users\YourName\Documents\fixture-study --out C:\Users\YourName\Documents\fixture-study\writing-pack.md
```

`writing-pack.md` summarizes literature, notes, figures, and simulation results that can support manuscript writing.

## 17. Recommended Daily Workflow

For each research topic, move through this sequence:

```text
Search papers -> record search-log
-> download PDFs
-> manually decide whether to add papers to the library
-> write paper-summary notes
-> run library add or library import-csv
-> write outline / literature-review notes
-> run simulations and export CSV/JSON
-> run simulation validate-data
-> run figure from-data
-> run manuscript check
-> run project check
-> run project report
-> generate writing-pack
```

## 18. Common Questions

### PowerShell Says It Cannot Find python

Use the `$PY` path shown in this guide instead of typing `python` directly.

### What If a Command Is Too Long?

In PowerShell, the backtick character `` ` `` continues a command onto the next line. When copying multi-line commands from this guide, keep the trailing backticks.

### What If Chinese Text Looks Garbled?

Read the file as UTF-8. For example:

```powershell
Get-Content C:\Users\YourName\Documents\科研\USER_GUIDE.md -Encoding UTF8
```

### Where Are Generated Figures?

They are in the `figures` folder of the research workspace.

### Why Does PDF Checking Show missing?

It means that the `pdf_name` recorded in `library-index.json` does not match an actual PDF file in the `literature` folder, or the PDF has not been placed there.

### Can This Tool Directly Control Simulation Software?

The first version does not directly control ANSYS, Abaqus, or COMSOL. Model, solve, and export CSV/JSON in the simulation software first, then use this workflow for data checking and plotting.

### Can It Automatically Check Word Layout?

Currently it can read `.docx` text and inspect several package-level Word signals: missing `styles.xml`, missing page margins, undefined paragraph styles, missing citation/reference fields, missing bibliography fields, and images or drawing objects without alternative text. It still does not render Word pages or replace final template review in Word.

