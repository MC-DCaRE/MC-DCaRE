<!-- Context: simulation/procedures | Priority: critical | Version: 1.0 | Updated: 2026-06-12 -->

# Simulation Procedures

**Purpose**: Step-by-step procedures for configuring, validating, executing, and post-processing MC-DCaRE simulations.
**Audience**: Simulation agent.

## Procedure 1: Configure a New Simulation

### From Natural Language
1. Parse user intent for: simulation type (CTDI/DICOM), kVp, mAs, protocol name, phantom size
2. Generate base config:
   ```bash
   uv run python run_simulation.py generate-config -o config/my_sim.yaml
   ```
3. Edit the YAML to match user specs
4. If protocol name given, set `imaging.rotation_direction` and `imaging.imaging_mode` so `_resolve_imaging_mode()` auto-fills remaining fields
5. Present summary to user

### From Existing Config
1. Copy an existing config YAML
2. Modify the relevant fields
3. Validate before running

### Config YAML Structure
```yaml
imaging:
  simulation_type: "CTDI"        # or "DICOM"
  anode_voltage: "100 kV"
  exposure: "100 mAs"
  fan_mode: "Full Fan"
  imaging_mode: "Head"
  rotation_direction: "CBCT Clockwise"
  field_x1: -7.0
  field_x2: 7.0
  field_y1: -7.0
  field_y2: 7.0

ctdi:
  phantom_size: "16 cm"
  couch_enabled: false
  water_chamber_enabled: false
  user_blade_enabled: false

general:
  histories: "100000"
  threads: 4
  seed: 12345
  dose_calibration_factor: 1.0
  topas_directory: "/path/to/topas"
  g4_data_directory: "/path/to/Geant4/data"
```

## Procedure 2: Validate Configuration

Always validate before execution:
```bash
uv run python run_simulation.py validate config/my_sim.yaml
```

**Manual checks:**
- `anode_voltage`: 40-150 kV (TrueBeam kV range)
- `histories`: >= 100,000 for CTDI statistical accuracy
- `phantom_size`: exactly "16 cm" or "32 cm"
- `fan_mode`: "Full Fan" or "Half Fan"
- Protocol key: `rotation_direction + imaging_mode` must match IMAGING_MODES dict
- TOPAS path: `general.topas_directory` points to valid TOPAS executable
- G4 data: `general.g4_data_directory` exists

**Mode-specific:**
- CTDI: `simulation_type` = "CTDI", `ctdi` section present
- DICOM: `simulation_type` = "DICOM", `dicom.dicom_directory` exists, RP file valid

## Procedure 3: Execute Simulation

### Foreground (blocks until done)
```bash
uv run python run_simulation.py run config/my_sim.yaml
```

### Dry Run (no TOPAS execution)
```bash
uv run python run_simulation.py run config/my_sim.yaml --dry-run
```
Use to inspect generated parameter files before committing to a long run.

### Background (detached)
```bash
uv run python run_simulation.py run config/my_sim.yaml --detach
```
Monitor: `cat runfolder/<timestamp>/topas_ctdi.log`

**Always confirm with user before executing TOPAS** — runs can take minutes to hours.

## Procedure 4: Post-Process CTDI Results

1. Compute CTDI-w from TOPAS CSV output:
   ```bash
   uv run python calculate_ctdiw.py main runfolder/<timestamp>
   ```
   Creates `CTDIw_results.csv` in the runfolder.

2. Benchmark against measurement:
   ```bash
   uv run python calculate_ctdiw.py benchmark runfolder/<timestamp> -r <measured_mSv>
   ```
   Reports PASS/FAIL, recommended DCF.

3. Apply calibration:
   - Set `general.dose_calibration_factor` to recommended DCF
   - Or re-run with updated config

## Procedure 5: Parameter Sweep

1. Confirm sweep parameters and ranges with user
2. Create base config
3. For each variant:
   a. Copy base config
   b. Edit sweep parameter(s)
   c. Validate
   d. Execute (sequentially)
4. Collect results into comparison table

**Keep sweeps small.** Each TOPAS run is resource-intensive. Offer dry-run first.

## Procedure 6: Query Past Runs

1. List runs: `ls -t runfolder/`
2. Read metadata: `cat runfolder/<ts>/simulation_metadata.yaml`
3. Read config used: `cat runfolder/<ts>/ctdi_config.yaml`
4. Check log: `cat runfolder/<ts>/simulation.log`
5. If CTDI CSV output exists, compute or read CTDI-w results

## Runfolder Contents

Each runfolder (`runfolder/YYYY-MM-DD_HH-MM-SS/`) contains:
- `CTDI_all_positions.txt` — main TOPAS parameter file
- `ChamberPlug{Position}_{scorer}.csv` — dose output per position/scorer
- `simulation.log` — orchestrator log
- `topas_ctdi.log` — TOPAS output
- `simulation_metadata.yaml` — kVp, mAs, histories, DCF, SpekPy params
- `ctdi_config.yaml` — config YAML used for the run
- `spectrum.txt` — SpekPy-generated spectrum
- Various include files (Muen.dat, NbParticlesInTime, etc.)
