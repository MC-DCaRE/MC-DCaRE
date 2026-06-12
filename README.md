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

### Running MC-DCaRE

**GUI mode:** Run `run_simulation.py` and launch the GUI. Select your Geant4 directory and TOPAS binary location, then configure your simulation.

**CLI mode:**
```bash
# Run a simulation from YAML config
uv run python run_simulation.py run --config config.yaml

# Generate a default config file
uv run python run_simulation.py generate-config --output my_config.yaml

# Validate a config without running
uv run python run_simulation.py validate --config my_config.yaml
```

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

## Project Structure

```
src/
├── config.py              # SimulationConfig, YAML loading, mode resolution
├── orchestrator.py        # Central coordinator
├── models/                # Immutable value objects (Quantity, ImagingMode, enums)
├── modes/                 # DicomMode, CtdiMode (strategy pattern)
├── gui/                   # FreeSimpleGUI interface (MVC)
├── services/              # CTDI calculator, calibration, benchmark
├── boilerplates/          # Jinja2 TOPAS parameter templates
└── spectrum_generator.py  # SpekPy X-ray spectrum generation
```

