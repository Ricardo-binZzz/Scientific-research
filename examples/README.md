# Examples

This folder contains small sample files for trying the workflow commands.

## Figure Example

```powershell
$PY='C:\path\to\python.exe'
& $PY -m workflow.cli figure from-data examples/simulation-result.csv examples/output --stem stress-response --title "Stress response" --figure-type trend --x-column time --y-column stress --x-label "Time (s)" --y-label "Stress (MPa)"
```

## Simulation Validation Example

```powershell
& $PY -m workflow.cli simulation validate-data examples/simulation-result.csv --required-column time --required-column stress --numeric-column time --numeric-column stress
```

## Manuscript Check Example

```powershell
& $PY -m workflow.cli manuscript check examples/chapter.md --required-section Introduction --required-section Method --expected-figure "Figure 1"
```

