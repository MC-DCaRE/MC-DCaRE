# MC-DCaRE Workflow Guide

Complete guide for running MC-DCaRE simulations: from local calibration through CTDI validation to patient-specific DICOM dose estimation.

## Prerequisites

- TOPAS MC installed (with Geant4 backend)
- Python 3.11+ with `uv` package manager
- SpekPy (installed automatically with project dependencies)

Configure paths in your YAML config or via environment variables:

```yaml
general:
  g4_data_directory: /path/to/G4Data          # or set G4DATA_DIR
  topas_directory: /path/to/topas/bin/topas   # or set TOPAS_DIR
```

## Overview

MC-DCaRE simulates kV imaging dose from the Varian TrueBeam system. Three simulation types are supported:

| Type | Geometry | Use Case |
|---|---|---|
| **CTDI** | Standard PMMA phantom (16 cm or 32 cm) | Beam model validation, calibration |
| **ICRP145** | ICRP 145 voxelized reference phantom | Standardized organ and effective dose |
| **DICOM** | Patient CT images | Patient-specific dose estimation |
| **kV-kV** | CTDI phantom with 2D pair geometry | kV-kV imaging dose |

The typical workflow has four phases:

1. **Calibrate** the beam model against measured CTDI data
2. **Validate** CTDI dose against reference specifications
3. **Estimate** organ dose using ICRP 145 reference phantoms
4. **Estimate** patient dose using DICOM geometry

---

## Phase 1: Local Calibration

Calibration aligns simulated dose with physical measurements on your specific TrueBeam unit. You run this once per kV/fan-mode combination.

### Step 1.1: Run a calibration simulation

Create a CTDI config (the run is uncalibrated; the DCF is applied during post-processing via `calibration.yaml`):

```yaml
# calibration_config.yaml
general:
  g4_data_directory: /path/to/G4Data
  topas_directory: /path/to/topas/bin/topas
  histories: "1000000"
  threads: "4"

imaging:
  simulation_type: "CTDI"
  rotation_direction: "CBCT Clockwise"
  imaging_mode: "Head"              # 100 kV, Full Fan, 16 cm phantom

ctdi:
  phantom_size: "16 cm"
```

Run:

```bash
uv run python run_simulation.py run calibration_config.yaml
```

This produces a runfolder (e.g. `runfolder/2026-06-12_14-30-00/`) containing dose output CSVs for all 5 chamber plug positions and 3 scorer types (TLE, DTM, DTW).

### Step 1.2: Compute the dose calibration factor

Use the benchmark CLI to compare simulated CTDI-w against your measured reference value:

```bash
uv run python calculate_ctdiw.py benchmark runfolder/2026-06-12_14-30-00/ \
  --reference 5.72 \
  --tolerance 10.0
```

Arguments:
- `--reference`: Measured CTDI-w in mSv (from your physical measurement or the Varian spec sheet)
- `--tolerance`: Acceptable deviation percentage (default 10%)

Output:
- PASS/FAIL verdict with deviation percentage
- Recommended DCF (also written to `calibration.yaml` by the `--kV`/`--fan-mode` options)

### Step 1.3: Store the calibration factor

Update `calibration.yaml` (the machine calibration database consumed by `CalibrationService` during post-processing):

```yaml
machine: "TrueBeam-SN1234"
date_calibrated: "2026-06-12"
calibrations:
  - kV: 100
    fan_mode: "Full Fan"
    reference_mAs: 150
    measured_ctdi_w_mGy: 5.72
    dcf_tle: 0.94    # TLE DCF, computed in Step 1.2
```

### Calibration scope

Repeat Steps 1.1-1.3 for each kV/fan-mode combination you intend to use. The calibration database (`calibration.yaml`) stores multiple entries keyed by `(kV, fan_mode)`. The `CalibrationService` automatically selects the correct DCF during post-processing based on the simulation's voltage and fan mode.

---

## Phase 2: CTDI Validation

Once calibrated, validate that your beam model reproduces CTDI reference values for the standard imaging protocols.

### Step 2.1: Run a validated simulation

Use a standard protocol config (calibration is applied in post-processing, so no factor is needed in the config):

```yaml
# ctdi_validation.yaml
general:
  g4_data_directory: /path/to/G4Data
  topas_directory: /path/to/topas/bin/topas
  histories: "5000000"
  threads: "8"

imaging:
  simulation_type: "CTDI"
  rotation_direction: "CBCT Clockwise"
  imaging_mode: "Head"

ctdi:
  phantom_size: "16 cm"
```

### Step 2.2: Compute CTDI-w

```bash
uv run python calculate_ctdiw.py runfolder/2026-06-12_15-00-00/
```

This outputs `CTDIw_results.csv` with CTDI-w values for each scorer type:
- **TLE** (primary): Track Length Estimator — measurement-equivalent, calibrated
- **DTM**: Dose to Medium — uncalibrated, for comparison
- **DTW**: Dose to Water — uncalibrated, for comparison

### Step 2.3: Benchmark against reference

```bash
uv run python calculate_ctdiw.py benchmark runfolder/2026-06-12_15-00-00/ \
  --reference 5.72
```

A PASS result confirms your beam model is validated.

### Available protocols

47 imaging modes are available. Select via `rotation_direction` and `imaging_mode`:

| Rotation Direction | Imaging Mode | kV | Fan | Phantom |
|---|---|---|---|---|
| CBCT Clockwise / Anticlockwise | Image Gently | 80 | Full | 16 cm |
| CBCT Clockwise / Anticlockwise | Head | 100 | Full | 16 cm |
| CBCT Clockwise / Anticlockwise | Short Thorax | 100 | Full | 32 cm |
| CBCT Clockwise / Anticlockwise | Spotlight | 100 | Full | 32 cm |
| CBCT Clockwise / Anticlockwise | Thorax | 125 | Half | 32 cm |
| CBCT Clockwise / Anticlockwise | Pelvis | 125 | Half | 32 cm |
| CBCT Clockwise / Anticlockwise | Pelvis Large | 125 | Half | 32 cm |
| CBCT Clockwise / Anticlockwise | Chest | 100 | Full | 32 cm |
| CBCT Clockwise / Anticlockwise | Pelvis Small | 100 | Full | 32 cm |
| CBCT Clockwise / Anticlockwise | Low Dose Thorax | 100 | Full | 32 cm |
| CBCT Clockwise / Anticlockwise | Large Body | 125 | Half | 32 cm |
| CBCT Clockwise / Anticlockwise | Spotlight Head 1-4 | 100 | Full | 32 cm |
| CBCT Clockwise / Anticlockwise | Spotlight Abdo 1-4 | 100 | Full | 32 cm |
| kV-kV | kV-kV | 100 | Full | N/A |

### CTDI scoring

Each CTDI simulation scores all 5 chamber plug positions simultaneously (Centre, Top, Bottom, Left, Right) using TOPAS Parallel Worlds. Three scorer types run per position:

| Scorer | Physics | Role |
|---|---|---|
| **TLE** | Collision kerma (fluence-weighted) | Primary — measurement-equivalent |
| **DTM** | Absorbed dose (event-based) | Secondary comparison |
| **DTW** | Dose scored in water medium | Secondary comparison |

CTDI-w is calculated as:

```
CTDI_w = (2/3) x peripheral_avg + (1/3) x center_dose
```

---

## Phase 3: ICRP 145 Phantom Organ Dose

Estimate organ and effective dose for standardized reference phantoms (MRCP-AM adult male, MRCP-AF adult female) using the ICRP 145 tetrahedral mesh. The phantom is voxelized at a configurable resolution and simulated with the full beam line.

### Prerequisites

- Voxelized phantom data (run `scripts/voxelize_mrcp_am_fast.py` once per phantom/resolution)
- CTDIw calibration from Phase 1 for the matching kV/fan-mode

### Step 3.1: Voxelize the phantom

Convert the ICRP 145 tetrahedral mesh to a voxel grid with real tissue material definitions:

```bash
uv run python scripts/voxelize_mrcp_am_fast.py \
    data/P145/Phantom_data/MRCP_AM \
    test_voxel_output/mrcp_am \
    1.0  # voxel size in cm (10 mm)
```

This produces:
- `mrcp_am_voxels.npy` -- material ID grid
- `phantomVoxel.txt` -- TOPAS parameter file with VoxelMaterials and ICRP tissue definitions
- `icrp_materials.txt` -- 187 TOPAS material definitions (elemental compositions and densities)

### Step 3.2: Create a phantom config

```yaml
# phantom_pelvis.yaml
general:
  g4_data_directory: /path/to/G4Data
  topas_directory: /path/to/topas/bin/topas
  histories: "1000000"      # per time step; total = histories x sequential_times
  threads: "20"

imaging:
  simulation_type: "ICRP145"
  rotation_direction: "CBCT Anticlockwise"
  imaging_mode: "Pelvis"     # 125 kV, Half Fan
  sequential_times: "150"    # full rotation

phantom:
  phantom_data_directory: data/P145/Phantom_data
  phantom_sex: "AM"          # AM = adult male, AF = adult female
  organ_scoring_ids: "Blood" # comma-separated organ names for TsTetGeomScorer filter
```

### Step 3.3: Swap in voxelized phantom and run

The pipeline generates a tetrahedral phantom template by default. For voxelized mode, swap the include file:

```bash
# Dry run to generate beam line files
uv run python scripts/run_pelvis_mrcp_am.py

# Or manually: copy phantomVoxel.txt into the runfolder and edit headsourcecode.txt
# to use: includeFile = phantomVoxel.txt
```

Run with the standard TOPAS binary (no MeshGeom extension needed for voxelized phantoms):

```bash
cd runfolder/<timestamp>/
topas headsourcecode.txt
```

### Step 3.4: Compute organ and effective dose

```bash
uv run python calculate_phantom_dose.py runfolder/<timestamp>/ \
    --output organ_doses.csv
```

DCF normalization is applied automatically from `calibration.yaml` (same database as CTDI mode). The `--scorer-type` flag selects which scorer's DCF to use (default: `tle`).

Arguments:
- `--scorer-type` : Scorer for DCF lookup: `tle` (default), `dtw`, or `dtm`. Also auto-detects the matching CSV file (`phantom_tle.csv`, `phantom_dtw.csv`, `phantom_dtm.csv`).
- `--target-mAs` : Scale dose to a different mAs value (for partial scans)
- `--dcf` : Manual DCF override (skips calibration.yaml lookup)
- `--calibration` : Path to calibration.yaml (default: `calibration.yaml`)
- `--output` : CSV path for the organ dose table

Output:
- ICRP 103 tissue doses and effective dose (mSv)
- Per-organ dose table with voxel counts and standard error

### Per-scorer DCFs

Each (kV, fan_mode) entry in `calibration.yaml` stores three DCFs -- one per scorer type:

```yaml
- kV: 125
  fan_mode: Half Fan
  reference_mAs: 1080.0
  measured_ctdi_w_mGy: 15.9
  dcf_tle: 1.633637e-03    # Track Length Estimator (primary)
  dcf_dtw: 1.505360e-03    # Dose To Water
  dcf_dtm: 1.755722e-03    # Dose To Medium
  reference_protocol: Pelvis
```

Backward compat: old YAML files with `dcf:` are automatically mapped to `dcf_tle` on load.

### Dose normalization pipeline

All simulation modes (CTDI, ICRP145, DICOM) use the **same DCF normalization** from `calibration.yaml`:

```
photons_per_mAs = spectrum_fluence * total_histories / exposure_mAs
absolute_dose_Gy = (TOPAS_Sum / total_histories) * photons_per_mAs * target_mAs * DCF
```

- `photons_per_mAs` is a kV-dependent constant (histories cancel algebraically)
- `DCF` is looked up from `calibration.yaml` by (kV, fan_mode, scorer_type)
- `target_mAs` supports partial scans (defaults to simulated mAs)
- `TOPAS_Sum` is divided by `total_histories` to convert from total accumulated dose to per-history mean

The DCF is computed once from a CTDI calibration run (Phase 1) and applied to all subsequent simulations regardless of geometry. Three scorer-specific DCFs are stored per (kV, fan_mode): TLE (primary), DoseToWater, and DoseToMedium.

### ICRP 103 effective dose

Organ doses are mapped to 15 ICRP 103 tissue categories:

```
E = Sigma(wT * HT)

where:
  wT = ICRP 103 tissue weighting factor
  HT = mean absorbed dose to tissue T (mGy), DCF-normalized
```

### Organ-to-tissue mapping

ICRP 145 organ names are mapped to ICRP 103 tissue categories automatically:

| ICRP 103 Tissue | wT | Example ICRP 145 Organs |
|---|---|---|
| Bone marrow | 0.12 | RST_trunk, RST_legs, RST_arms |
| Colon | 0.12 | Ascending/descending/transverse/sigmoid colon walls |
| Lung | 0.12 | Lung(AI)_left, Lung(AI)_right |
| Bladder | 0.04 | Urinary_bladder_wall, Urinary_bladder_content |
| Bone surface | 0.01 | Pelvis_cortical, Femora_cortical, *_cortical |
| Skin | 0.01 | Skin_trunk, Skin_legs, Skin_arms |
| Remainder | 0.12 | Muscle, small intestine, lymph nodes, heart, kidneys, ... |

### Expected results

| Protocol | kV | Effective Dose (mSv) | Reference |
|---|---|---|---|
| Pelvis | 125 | ~3.0 (sim) vs 4.2 (PCXMC) | 0.71 ratio |
| Pelvis Spotlight | 125 | ~2.2 | PCXMC |
| Thorax | 125 | ~1.3 | PCXMC |
| Head | 100 | ~0.5 | PCXMC |

Differences from PCXMC reference values arise from: voxel resolution (10 mm default), limited organ coverage for small organs, and differences between the ICRP 145 mesh phantom and the PCXMC mathematical phantom.

### Voxelization scripts

| Script | Purpose |
|---|---|
| `scripts/voxelize_mrcp_am_fast.py` | Convert tetrahedral mesh to voxels (pandas-accelerated loading) |
| `scripts/regenerate_voxel_phantom.py` | Regenerate TOPAS files with real ICRP tissue materials |

---

## Phase 4: DICOM Patient Dose Estimation

With a validated beam model, estimate patient-specific imaging dose using CT DICOM datasets.

### Step 3.1: Prepare DICOM data

Place your CT DICOM image series in a directory. Optionally include an RT Plan DICOM file.

```
/path/to/patient/
├── CT_Slice001.dcm
├── CT_Slice002.dcm
├── ...
└── RP.Plan.dcm              # optional
```

### Step 3.2: Create a DICOM config

```yaml
# dicom_patient.yaml
general:
  g4_data_directory: /path/to/G4Data
  topas_directory: /path/to/topas/bin/topas
  histories: "5000000"
  threads: "8"

imaging:
  simulation_type: "DICOM"
  rotation_direction: "CBCT Clockwise"
  imaging_mode: "Head"

dicom:
  dicom_directory: "/path/to/patient"
  dicom_rp_file: "/path/to/patient/RP.Plan.dcm"
  patient_id: "PT001"
  isocenter_x: "0 mm"
  isocenter_y: "0 mm"
  isocenter_z: "0 mm"
  patient_shift_x: "0. mm"
  patient_shift_y: "0. mm"
  patient_shift_z: "0. mm"
  patient_yaw: "0. deg"
  patient_pitch: "0. deg"
  patient_roll: "0. deg"
```

Beam parameters (voltage, field size, blades, rotation rate) are auto-resolved from the protocol name, same as CTDI mode.

### Step 3.3: Run the simulation

```bash
uv run python run_simulation.py run dicom_patient.yaml
```

### Step 3.4: Review output

The runfolder contains:

| File | Purpose |
|---|---|
| `headsourcecode.txt` | TOPAS beam line parameter file |
| `patientDICOM.txt` | Patient geometry include file |
| `HUtoMaterialSchneider.txt` | HU-to-material conversion table |
| `PT001_CBCT Clockwise_Head_0 deg_DOSE_PTV.*` | 3D dose distribution output |

DICOM mode produces a 3D dose grid rather than per-position CSVs. Use your standard DICOM-RT analysis tools to evaluate the dose distribution.

---

## Advanced Features

### Phase Space Scoring and Replay (CTDI only)

For repeated simulations with the same beam line, score the phase space once and replay it to skip beam transport.

**Score mode** (beam line only, no phantom):

```yaml
ctdi:
  phase_space_mode: "score"
```

Produces `beam_exit_phsp.phsp` + beam statistics in the `phase_space/` subdirectory.

**Replay mode** (uses scored phase space with phantom):

```yaml
ctdi:
  phase_space_mode: "replay"
  phase_space_file: "/path/to/beam_exit_phsp.phsp"
  phase_space_multiple_use: 5  # reuse each particle 5 times
```

No spectrum generation in replay mode. The norm factor is divided by `phase_space_multiple_use` for correct normalization.

### Water Chamber Volumes (CTDI only)

Enable water-filled chamber volumes for additional DTM scoring:

```yaml
ctdi:
  water_chamber_enabled: true
```

Adds 5 extra DTM scorers (`_water_dtm`) — one per chamber plug position.

### Dry Run

Validate your configuration and render templates without running TOPAS:

```bash
uv run python run_simulation.py run config.yaml --dry-run
```

### Detached Mode

Run TOPAS in the background:

```bash
uv run python run_simulation.py run config.yaml --detach
```

Writes `topas.pid` to the runfolder. Monitor progress via `topas_ctdi.log`.

---

## CLI Reference

### Simulation CLI (`run_simulation.py`)

```bash
# Run simulation
uv run python run_simulation.py run <config_file> [--dry-run] [--detach]

# Generate default config template
uv run python run_simulation.py generate-config [--output my_config.yaml]

# Validate config without running
uv run python run_simulation.py validate <config_file>

# Convert config between YAML and JSON
uv run python run_simulation.py convert <input> <output> [--format yaml|json]
```

### Post-Processing CLI (`calculate_ctdiw.py`)

```bash
# Compute CTDI-w for all scorer types
uv run python calculate_ctdiw.py <runfolder> [--output results.csv]

# Benchmark against measured reference
uv run python calculate_ctdiw.py benchmark <runfolder> \
  --reference <mSv> [--tolerance 10.0] [--output benchmark.csv]
```

### Phantom Dose CLI (`calculate_phantom_dose.py`)

```bash
# TLE scorer (default, best statistics)
uv run python calculate_phantom_dose.py <runfolder> [--output organ_doses.csv]

# DoseToWater or DoseToMedium scorer
uv run python calculate_phantom_dose.py <runfolder> --scorer-type dtw

# Scale to partial scan mAs
uv run python calculate_phantom_dose.py <runfolder> --target-mAs 500

# Manual DCF override
uv run python calculate_phantom_dose.py <runfolder> --dcf 1.634e-03
```

### DICOM Dose CLI (`calculate_dicom_dose.py`)

```bash
# Fully automatic DCF normalization
uv run python calculate_dicom_dose.py <runfolder>

# Scale to partial scan mAs
uv run python calculate_dicom_dose.py <runfolder> --target-mAs 500
```

---

## Runfolder Structure

Every simulation produces a timestamped runfolder:

```
runfolder/2026-06-12_14-30-00/
├── config.yaml                       # Copy of source config (provenance)
├── simulation.log                    # Python application log
├── simulation_metadata.yaml          # norm_factor, mAs, dcf_used, SpekPy params
├── head_calibration_factor.txt       # Legacy combined calibration factor
├── ConvertedTopasFile.txt            # TOPAS energy spectrum
├── Muen.dat                          # Mass-energy absorption coefficients
├── fullfan.txt                       # Bowtie filter (Full Fan) or halffan.txt (Half Fan)
│
│── # CTDI mode:
├── CTDI_all_positions.txt            # Combined TOPAS parameter file
├── topas_ctdi.log                    # TOPAS stdout/stderr
├── ChamberPlugCentre_tle.csv         # Dose outputs (15 files: 5 positions x 3 scorers)
├── ChamberPlugCentre_dtm.csv
├── ChamberPlugCentre_dtw.csv
├── ChamberPlugTop_tle.csv
├── ...
│
│── # DICOM mode:
├── headsourcecode.txt                # TOPAS beam line parameter file
├── patientDICOM.txt                  # Patient geometry include file
├── HUtoMaterialSchneider.txt         # HU-to-material conversion
├── topas_dicom.log                   # TOPAS stdout/stderr
└── PT001_CBCT Clockwise_Head_0 deg_DOSE_PTV.*  # 3D dose output
│
│── # ICRP145 mode (voxelized):
├── headsourcecode.txt                # TOPAS beam line parameter file
├── phantomVoxel.txt                  # Voxelized phantom geometry
├── icrp_materials.txt                # 187 ICRP tissue material definitions
├── phantom_tle.csv                   # TLE scorer output (primary)
├── phantom_dtw.csv                   # DoseToWater scorer output
├── phantom_dtm.csv                   # DoseToMedium scorer output
├── Muen.dat                          # Mass energy absorption data (for TLE)
└── organ_doses.csv                   # Per-organ dose summary (from calculate_phantom_dose.py)
```

---

## Configuration Reference

### Minimal CTDI Config

```yaml
general:
  g4_data_directory: /path/to/G4Data
  topas_directory: /path/to/topas/bin/topas

imaging:
  simulation_type: "CTDI"
  rotation_direction: "CBCT Clockwise"
  imaging_mode: "Head"

ctdi:
  phantom_size: "16 cm"
```

All beam parameters (voltage, exposure, field size, blade openings, rotation rate, fan mode) are auto-resolved from the protocol lookup table. Override any parameter by including it explicitly in the config — explicit values take precedence.

### Minimal DICOM Config

```yaml
general:
  g4_data_directory: /path/to/G4Data
  topas_directory: /path/to/topas/bin/topas

imaging:
  simulation_type: "DICOM"
  rotation_direction: "CBCT Clockwise"
  imaging_mode: "Head"

dicom:
  dicom_directory: /path/to/patient/dicom
  patient_id: "PT001"
```

### Minimal ICRP145 Phantom Config

```yaml
general:
  g4_data_directory: /path/to/G4Data
  topas_directory: /path/to/topas/bin/topas
  histories: "1000000"

imaging:
  simulation_type: "ICRP145"
  rotation_direction: "CBCT Anticlockwise"
  imaging_mode: "Pelvis"
  sequential_times: "150"

phantom:
  phantom_data_directory: data/P145/Phantom_data
  phantom_sex: "AM"
  organ_scoring_ids: "Blood"
```

### kV-kV Config

kV-kV configs do **not** use mode resolution. All beam parameters must be specified explicitly:

```yaml
imaging:
  simulation_type: "CTDI"
  rotation_direction: "kV-kV"
  anode_voltage: "100 kV"
  exposure: "100 mAs"
  fan_mode: "Full Fan"
  rotation_rate: "0.4 deg/s"
  timeline_end: "501 s"
  start_angle: "0 deg"
  field_x1: "14 cm"
  field_x2: "14 cm"
  field_y1: "10.7 cm"
  field_y2: "10.7 cm"
  blade_x1: "6.175536078965273 cm"
  blade_x2: "-6.175536078965273 cm"
  blade_y1: "5.814471115800571 cm"
  blade_y2: "-5.814471115800571 cm"
```
