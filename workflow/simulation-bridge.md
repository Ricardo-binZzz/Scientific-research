# Simulation Bridge

## Goal

Move results from engineering simulation software into Python with minimal manual cleanup.

## Bridge Rules

- Export simulation results into a documented tabular format.
- Keep one folder per simulation case.
- Preserve units in the file name or metadata.
- Record solver version, material set, boundary conditions, and mesh summary.

## Manual Review Points

- Geometry or model setup
- Boundary conditions
- Solver start
- Solver convergence
- Result export
- Plot generation

## Validation Rules

- Check units before plotting.
- Check column names before loading.
- Check that x/y series lengths match.
- Check that plotted values are plausible against the simulation report.
