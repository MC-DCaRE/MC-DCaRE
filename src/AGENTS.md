# src

## Purpose
Core source package for MC-DCaRE (Monte Carlo Dose Calculation and Research Environment). Provides simulation configuration, TOPAS parameter file generation via Jinja2 templates, GUI, and post-processing for CT dosimetry.

## Architecture
`Orchestrator` is the central coordinator. Flow: `config.py` defines `SimulationConfig` -> `Orchestrator` selects a `SimulationMode` (DICOM or CTDI) -> mode builds Jinja2 context dict -> `TemplateRenderer` renders `.j2` boilerplate templates -> `SimulationRunner` executes TOPAS -> `CTDICalculator` post-processes results.

Subdirectories:
- **models/** — Immutable dataclasses: `Quantity`, `ImagingMode`, enums (`SimulationType`, `FanMode`), UI keys
- **modes/** — Strategy pattern: `SimulationMode` ABC with `DicomMode` and `CtdiMode` implementations
- **gui/** — FreeSimpleGUI MVC: `MainView` (layout) + `controller.py` (event handling)
- **services/** — Post-simulation services: `CTDICalculator` for CTDI dose metrics
- **boilerplates/** — Jinja2 TOPAS parameter file templates and include file directories

## Key Files

| File | Role |
|---|---|
| `config.py` | `SimulationConfig` dataclass, all configuration parameters |
| `orchestrator.py` | Central coordinator: mode selection, Jinja2 rendering, run execution |
| `boilerplate_manager.py` | Creates `TemplateRenderer`, manages `tmp/` working directory |
| `template_renderer.py` | Jinja2 template rendering with `FileSystemLoader` |
| `simulation_runner.py` | Executes TOPAS Monte Carlo simulations |
| `spectrum_generator.py` | Generates X-ray spectrum definitions via SpekPy |
| `fieldtobladeopening.py` | Converts field size to collimator blade opening positions |
| `imaging_modes_lookuptable.py` | Lookup table for TrueBeam imaging mode parameters |

## Conventions
- `from __future__ import annotations` in every module
- `logging.getLogger(__name__)` for all logging
- `frozen=True` dataclasses for immutable value objects in `models/`
- Abstract base classes define contracts in `modes/base.py`
- All imports use `src.` prefix (e.g., `from src.config import ...`)
- Modes build context dicts (`Dict[str, object]`) consumed by Jinja2 templates
- `TemplateRenderer` searches both `boilerplates/` and `TOPAS_includeFiles/` for templates
