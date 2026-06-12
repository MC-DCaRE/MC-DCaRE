---
description: "Run a MC-DCaRE simulation — configure, validate, execute, or query results in natural language"
---

Run a MC-DCaRE Monte Carlo simulation. This is the main entry point for simulation workflows.

**Input**: The argument after `/sim` is a natural language description of what you want to do.

**Examples**:
- `/sim Run a CTDI simulation at 120kVp, large focal spot, total filtration 6.5mmAl`
- `/sim Run the Head protocol with 500k histories`
- `/sim What did I run yesterday?`
- `/sim Compare my last two CTDI runs`
- `/sim Run a kVp sweep from 80 to 140 in steps of 20 for the Body protocol`

**Steps**

1. **Parse intent** — Determine what the user wants: configure, validate, execute, query, compare, sweep, or interpret.

2. **Route to appropriate workflow**:
   - **Configure + Run**: Generate or edit config YAML, validate, confirm with user, execute
   - **Query Results**: Scan runfolder/ directories, read metadata and CTDI-w results
   - **Compare Runs**: Read multiple runfolders, tabulate differences
   - **Parameter Sweep**: Create variant configs, run sequentially, collect results
   - **Interpret**: Explain CTDI metrics, scorer outputs, calibration

3. **Execute** — Follow the workflow, using:
   - `uv run python run_simulation.py` for CLI operations
   - `uv run python calculate_ctdiw.py` for post-processing
   - Direct file reads for querying past results

4. **Report** — Always report the runfolder path after execution, check for errors in logs.

**Constraints**:
- Always validate config before running TOPAS
- Always confirm with user before executing TOPAS (resource-intensive)
- Use TLE as primary scorer for quantitative reporting
- Never fabricate results — read actual output files
