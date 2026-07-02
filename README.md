# MC-DCaRE
## Monte Carlo - Dose Calculation for Risk Evaluation

This project was developed by National Cancer Centre Singapore Department of Radiation Oncology Physics for use in determining imaging dose to the patient in the Varian TrueBeam kV Imaging system.

The project builds on both TOPAS and Geant4 libraries to simulate the Varian TrueBeam kV imaging beam delivery system and executes Monte Carlo dose computation.

A graphical user interface is provided to allow end-users easy input of the directory of CT DICOM image set as well as main imaging parameters.

As such, the kV imaging dose due to 3D CBCT or 2D kV-kV received by patients during treatment can be estimated by Monte Carlo computation.

The accuracy of our simulations is benchmarked against CTDI dose specifications specified in the Varian TrueBeam Technical Reference Guide - (Volume 2: Imaging) as well as in-house measurements.

Full descriptions of the simulation and beam model is in pre-publication.

Version: Beta Prerelease

## Supported Imaging Protocols

MC-DCaRE includes **47 pre-configured imaging modes** covering all Varian TrueBeam kV imaging protocols:

| Category | Protocols |
|---|---|
| **CBCT Clockwise / Anticlockwise** | Image Gently, Head, Short Thorax, Spotlight, Thorax, Pelvis, Pelvis Large |
| **CBCT Spotlight** | Head (4 variants), Abdo Spotlight (4 variants) |
| **CBCT Clinical** | Chest, Pelvis Small, Low Dose Thorax, Large Body |
| **kV-kV** | kV-kV pair |

Each protocol carries 21 beam parameters (rotation rate, voltage, exposure, fan mode, field size, blade openings, CTDI phantom, dose factor, acquisition geometry). Users select a protocol name in the GUI or YAML config; beam parameters are auto-populated from the lookup table.

## How to install and run

### Install TOPASMC and Geant 4

[TOPASMC download link](https://www.topasmc.org/download)

[Geant4 Toolkit download link](https://geant4.web.cern.ch/)

Take note of the file directory for TOPASMC and Geant4.

### Quick Start

```bash
# Generate a default config file
uv run python run_simulation.py generate-config --output my_config.yaml

# Edit paths and protocol selection
# Then run:
uv run python run_simulation.py run my_config.yaml
```

### CLI Reference

```bash
# Run simulation
uv run python run_simulation.py run <config_file> [--dry-run] [--detach]

# Validate config without running
uv run python run_simulation.py validate <config_file>

# Compute CTDI-w from runfolder output
uv run python calculate_ctdiw.py <runfolder>

# Benchmark against measured reference
uv run python calculate_ctdiw.py benchmark <runfolder> --reference <mSv>
```

### Complete Workflow

See **[docs/workflow.md](docs/workflow.md)** for the full end-to-end guide:

1. **Calibrate** — align simulated dose with physical measurements on your TrueBeam
2. **Validate** — verify CTDI dose against Varian reference specifications
3. **Estimate** — compute patient-specific imaging dose using DICOM CT datasets

### Minimal YAML Configuration

Beam parameters are resolved from the protocol name, so configs only need to specify the mode:

```yaml
imaging:
  simulation_type: "CTDI"
  rotation_direction: "CBCT Clockwise"
  imaging_mode: "Head"
  n_histories: 1000000

ctdi:
  phantom_size: "16 cm"
```

## ICRP 145 Phantom Mode

Organ dose estimation using ICRP 145 reference phantoms (MRCP-AM adult male, MRCP-AF adult female). Two geometry approaches are supported:

- **Voxelized phantom** (default): Converts the tetrahedral mesh to a voxel grid with real ICRP tissue material definitions. Works with standard TOPAS (no extensions needed).
- **Tetrahedral mesh**: Uses the TsTetGeom component from the MeshGeom extension. Requires the fixed parameterization for Geant4 11.x (see `scripts/meshgeom_fix/`).

### Prerequisites

**1. Voxelized phantom data (one-time setup)**

Voxelize the tetrahedral mesh at the desired resolution:

```bash
uv run python scripts/voxelize_mrcp_am_fast.py \
    data/P145/Phantom_data/MRCP_AM \
    test_voxel_output/mrcp_am \
    1.0  # voxel size in cm (10 mm)
```

This produces `phantomVoxel.txt` (TOPAS parameter file with VoxelMaterials) and `icrp_materials.txt` (187 tissue material definitions from the ICRP 145 composition data).

**2. Phantom data files**

Place ICRP 145 mesh files under `data/P145/Phantom_data/`:

```
data/P145/Phantom_data/
├── MRCP_AM/
│   ├── MRCP_AM.node
│   ├── MRCP_AM.ele
│   └── MRCP_AM.material
└── MRCP_AF/
    ├── MRCP_AF.node
    ├── MRCP_AF.ele
    └── MRCP_AF.material
```

The `.material` files can be generated from `_media.dat` using:

```bash
uv run python scripts/generate_material_from_media.py <input>_media.dat <output>.material
```

**3. CTDIw calibration**

Run a CTDI calibration (Phase 1 in `docs/workflow.md`) for the matching kV/fan-mode to obtain the empirical DCF and CTDIw reference value.

### Minimal YAML Configuration

```yaml
general:
  g4_data_directory: /path/to/G4Data
  topas_directory: /path/to/topas/bin/topas
  histories: "1000000"        # per time step

imaging:
  simulation_type: "ICRP145"
  rotation_direction: "CBCT Anticlockwise"
  imaging_mode: "Pelvis"
  sequential_times: "150"     # full rotation

phantom:
  phantom_sex: "AM"
  phantom_data_directory: "data/P145/Phantom_data"
  organ_scoring_ids: "Blood"
```

### Running the simulation

```bash
# Run the pipeline (generates beam line + phantom template)
uv run python scripts/run_pelvis_mrcp_am.py

# Or: dry run, then swap in voxelized phantom manually
uv run python scripts/generate_dose_sim.py
cp test_voxel_output/mrcp_am/phantomVoxel.txt runfolder/<timestamp>/
cp test_voxel_output/mrcp_am/icrp_materials.txt runfolder/<timestamp>/
# Edit headsourcecode.txt: includeFile = phantomVoxel.txt
cd runfolder/<timestamp>/ && topas headsourcecode.txt
```

### Computing organ and effective dose

```bash
uv run python calculate_phantom_dose.py runfolder/<timestamp>/ \
    --output organ_doses.csv
```

DCF normalization is applied automatically from `calibration.yaml` (same database as CTDI mode). Supports `--target-mAs` for partial scan dose estimation.

This produces:
- Per-organ dose table (mGy) with voxel counts and standard error
- ICRP 103 tissue doses and effective dose (mSv)
- Full DCF provenance (DCF value, source, photons_per_mAs, mAs)

### Dose normalization

All simulation modes use the same DCF from `calibration.yaml`. Per-scorer DCFs (`dcf_tle`, `dcf_dtw`, `dcf_dtm`) are stored for each (kV, fan_mode) and selected via `--scorer-type`:

```
absolute_dose = (TOPAS_Sum / total_histories) * photons_per_mAs * target_mAs * DCF
```

The DCF is computed from a CTDI calibration run and applied to all geometries (CTDI, phantom, DICOM). Three scorer-specific DCFs allow flexibility: TLE (primary, best statistics), DoseToWater, and DoseToMedium. See `docs/workflow.md` for the full normalization pipeline.

## Project Structure

```
src/
├── config.py              # SimulationConfig, YAML loading, mode resolution
├── orchestrator.py        # Central coordinator
├── models/                # Immutable value objects (Quantity, ImagingMode, enums, ICRP 103)
├── modes/                 # DicomMode, CtdiMode, PhantomMode (strategy pattern)
├── gui/                   # FreeSimpleGUI interface (MVC)
├── services/              # CTDI calculator, calibration, benchmark, phantom dose calculator
├── boilerplates/          # Jinja2 TOPAS parameter templates
└── spectrum_generator.py  # SpekPy X-ray spectrum generation
```

