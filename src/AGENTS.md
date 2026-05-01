# src

## Purpose
Core source package for MC-DCaRE (Monte Carlo Dose Calculation and Research Environment). Provides simulation configuration, TOPAS parameter file generation, GUI, and post-processing for CT dosimetry.

## Architecture
`Orchestrator` is the central coordinator. Flow: `config.py` defines `SimulationConfig` -> `Orchestrator` selects a `SimulationMode` (DICOM or CTDI) -> mode edits TOPAS boilerplate files via `ParameterEditor` -> `SimulationRunner` executes TOPAS -> `CTDICalculator` post-processes results.

Subdirectories:
- **models/** — Immutable dataclasses: `Quantity`, `ImagingMode`, enums (`SimulationType`, `FanMode`), UI keys
- **modes/** — Strategy pattern: `SimulationMode` ABC with `DicomMode` and `CtdiMode` implementations
- **gui/** — FreeSimpleGUI MVC: `MainView` (layout) + `controller.py` (event handling)
- **services/** — Post-simulation services: `CTDICalculator` for CTDI dose metrics
- **boilerplates/** — TOPAS parameter file templates and include file directories

## Key Files

| File | Role |
|---|---|
| `config.py` | `SimulationConfig` dataclass, all configuration parameters |
| `orchestrator.py` | Central coordinator: mode selection, parameter editing, run execution |
| `boilerplate_manager.py` | Loads and manages TOPAS boilerplate templates |
| `parameter_editor.py` | String-level edits to TOPAS parameter files |
| `simulation_runner.py` | Executes TOPAS Monte Carlo simulations |
| `spectrum_generator.py` | Generates X-ray spectrum definitions via SpekPy |
| `run_preparer.py` | Prepares run directories with necessary files |
| `fieldtobladeopening.py` | Converts field size to collimator blade opening positions |
| `imaging_modes_lookuptable.py` | Lookup table for TrueBeam imaging mode parameters |
| `guilayers.py` | Additional GUI layer definitions |

## Conventions
- `from __future__ import annotations` in every module
- `logging.getLogger(__name__)` for all logging
- `frozen=True` dataclasses for immutable value objects in `models/`
- Abstract base classes define contracts in `modes/base.py`
- All imports use `src.` prefix (e.g., `from src.config import ...`)
