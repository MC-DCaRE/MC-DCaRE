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

Organ dose estimation using ICRP 145 tetrahedral-mesh reference phantoms (MRCP-AM / MRCP-AF).

### Prerequisites

**1. Build the OpenTOPAS MeshGeom extension**

The `TsTetGeom` component is required to load tetrahedral mesh geometries. It is not included in the base OpenTOPAS distribution.

```bash
# Clone the extension
git clone https://github.com/OpenTOPAS/OpenTOPAS-MeshGeom.git

# Build against your OpenTOPAS installation
cd OpenTOPAS-MeshGeom
mkdir build && cd build
cmake -DTOPAS_EXTENSIONS_DIR=<your_extensions_dir> ..
make -j$(nproc)
```

Rebuild OpenTOPAS with the extension included. Verify by running a parameter file that instantiates `TsTetGeom` — no "unknown component" error confirms success.

**2. Assemble phantom data**

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

The `.node` and `.ele` files come from the ICRP 145 phantom distribution. The `.material` files can be generated from `_media.dat` using:

```bash
uv run python scripts/generate_material_from_media.py <input>_media.dat <output>.material
```

### Minimal YAML Configuration

```yaml
general:
  simulation_type: "ICRP145"

phantom:
  phantom_sex: "AM"          # or "AF"
  phantom_data_directory: "data/P145/Phantom_data"
```

## Project Structure

```
src/
├── config.py              # SimulationConfig, YAML loading, mode resolution
├── orchestrator.py        # Central coordinator
├── models/                # Immutable value objects (Quantity, ImagingMode, enums)
├── modes/                 # DicomMode, CtdiMode, PhantomMode (strategy pattern)
├── gui/                   # FreeSimpleGUI interface (MVC)
├── services/              # CTDI calculator, calibration, benchmark
├── boilerplates/          # Jinja2 TOPAS parameter templates
└── spectrum_generator.py  # SpekPy X-ray spectrum generation
```

