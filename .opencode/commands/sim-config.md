---
description: "Validate a simulation config without running — check parameters, ranges, and completeness"
---

Validate a simulation configuration file without executing TOPAS.

**Input**: The argument after `/sim-config` is either a config file path or a description of what to validate.

**Examples**:
- `/sim-config config/my_sim.yaml`
- `/sim-config Check if my Head protocol config is ready to run`

**Steps**

1. **Locate config** — If a file path is given, use it. If a description, find or generate the config.

2. **Run CLI validation**:
   ```bash
   uv run python run_simulation.py validate <config.yaml>
   ```

3. **Manual parameter checks**:
   - kVp range: 40-150
   - Histories: >= 100k
   - Phantom size: "16 cm" or "32 cm"
   - Fan mode: valid
   - Protocol key: resolves in IMAGING_MODES
   - TOPAS path: exists
   - G4 data path: exists
   - Mode-specific: CTDI section or DICOM section present and valid

4. **Report findings** — List any issues found, suggest fixes. If valid, say so.

**Output**: Validation report with pass/fail per check and actionable fix suggestions.
