# src

## Purpose
Core source package for MC-DCaRE (Monte Carlo Dose Calculation and Research Environment). Provides simulation configuration, TOPAS parameter file generation via Jinja2 templates, GUI, and post-processing for CT dosimetry.

## Architecture
`Orchestrator` is the central coordinator. Flow: `config.py` defines `SimulationConfig` -> `Orchestrator` creates a runfolder and selects a `SimulationMode` (DICOM or CTDI) -> mode builds Jinja2 context dict -> `TemplateRenderer` renders `.j2` boilerplate templates -> `SimulationRunner` executes TOPAS as a single process per simulation (capturing output to log files) -> `CTDICalculator` post-processes results. For CTDI mode, all 5 chamber plug positions are scored simultaneously using TOPAS Parallel Worlds (Layered Mass Geometry) in a single process. Three scorer types run per position (TLE, DTM, DTW); TLE is designated primary (measurement-equivalent). Optional water-filled chamber volumes add 5 more DTM scorers (`_water_dtm`) gated by `ctdi.water_chamber_enabled`. `CalibrationService.apply()` calibrates only TLE results by default. Python logging is tee'd to `<runfolder>/simulation.log` (filename configurable via `GeneralConfig.log_filename`).

Subdirectories:
- **models/** — Immutable dataclasses: `Quantity`, `ImagingMode` (21 fields, 47 protocols), enums (`SimulationType`, `FanMode`), UI keys
- **modes/** — Strategy pattern: `SimulationMode` ABC with `DicomMode` and `CtdiMode` implementations
- **gui/** — FreeSimpleGUI MVC: `MainView` (layout) + `controller.py` (event handling)
- **services/** — Post-simulation services: `CTDICalculator` (scorer-aware CTDI metrics with TLE as primary), `CalibrationService` (DCF applied to TLE only), `BenchmarkCalculator` (benchmarks TLE only)
- **boilerplates/** — Jinja2 TOPAS parameter file templates and include file directories

## Key Files

| File | Role |
|---|---|
| `config.py` | `SimulationConfig` dataclass, all configuration parameters, `_resolve_imaging_mode()` for name-based config resolution |
| `orchestrator.py` | Central coordinator: mode selection, Jinja2 rendering, run execution |
| `boilerplate_manager.py` | Creates `TemplateRenderer`, manages `tmp/` working directory |
| `template_renderer.py` | Jinja2 template rendering with `FileSystemLoader` |
| `simulation_runner.py` | Executes TOPAS simulations as single processes, captures stdout/stderr to log files |
| `spectrum_generator.py` | Generates X-ray spectrum definitions via SpekPy |
| `fieldtobladeopening.py` | Converts field size to collimator blade opening positions |

## Conventions
- `from __future__ import annotations` in every module
- `logging.getLogger(__name__)` for all logging
- `frozen=True` dataclasses for immutable value objects in `models/`
- Abstract base classes define contracts in `modes/base.py`
- All imports use `src.` prefix (e.g., `from src.config import ...`)
- Modes build context dicts (`Dict[str, object]`) consumed by Jinja2 templates
- `TemplateRenderer` searches both `boilerplates/` and `TOPAS_includeFiles/` for templates
