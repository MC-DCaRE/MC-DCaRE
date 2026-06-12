---
description: "Query and analyze results from past MC-DCaRE simulation runs"
---

Query simulation results from completed MC-DCaRE runs.

**Input**: The argument after `/sim-results` is a query about past results.

**Examples**:
- `/sim-results What's the CTDIvol for my last run?`
- `/sim-results Show me the Head protocol results from last week`
- `/sim-results List all my CTDI runs`
- `/sim-results What parameters did I use for the run on June 10?`

**Steps**

1. **Scan runfolders** — List available runs:
   ```bash
   ls -t runfolder/
   ```

2. **Identify target run(s)**:
   - By timestamp (exact or relative: "last", "yesterday", "last week")
   - By parameters (protocol name, kVp, phantom size — read metadata)
   - By index (most recent, second most recent, etc.)

3. **Read results**:
   - `simulation_metadata.yaml` — parameters used
   - `ctdi_config.yaml` — full config
   - `simulation.log` — orchestrator log
   - `ChamberPlug*.csv` — dose output files
   - `CTDIw_results.csv` — computed CTDI-w (if available)

4. **Compute if needed**:
   ```bash
   uv run python calculate_ctdiw.py main runfolder/<timestamp>
   ```

5. **Present results** — Structured format with key metrics. Always use TLE (primary scorer) for quantitative values.

**Output**: Structured result summary with CTDI-w values, parameters used, and any anomalies noted in logs.
