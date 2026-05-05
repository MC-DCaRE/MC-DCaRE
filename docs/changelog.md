# Changelog

All notable changes to MC-DCaRE will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Replaced Python multiprocessing with TOPAS Parallel Worlds (Layered Mass Geometry) for CTDI simulations. A single TOPAS process now scores all 5 chamber plug positions (Centre, Top, Bottom, Left, Right) simultaneously using parallel worlds, eliminating the need for Python-level multiprocessing. The full `threads` count from the config is allocated to the single TOPAS process instead of being split across 5 separate processes, giving TOPAS/Geant4 maximum multithreading efficiency.
- CTDI simulations now generate a single `CTDI_all_positions.txt` parameter file with 15 scorers (3 per position) instead of 5 separate parameter files.
- `SimulationRunner` no longer uses `multiprocessing`; `run_ctdi()` removed in favour of direct `run_topas()` call from `CtdiMode.execute()`.

### Added

- `dose_calibration_factor` field in `GeneralConfig` for measurement-corrected dose output
- `BenchmarkCalculator` service with `benchmark` subcommand in `calculate_ctdiw.py`
- `compute_calibration_factor()` to derive simulation-to-measurement normalization ratio
- Simulation logs recorded to runfolder: `simulation.log` (Python application log), `topas_*.log` (per-process TOPAS output)
- `log_filename` field in `GeneralConfig` to configure the application log file name (default: `simulation.log`)
- `run_with_runfolder()` and `create_runfolder()` on `Orchestrator` for early runfolder creation and file logging
- Real-time TOPAS stdout/stderr capture via `subprocess.Popen` with per-process log files
- `.local_paths.yaml` and `config.local.yaml` in `.gitignore` for machine-specific configs

---

## [0.2.0] - 2026-05-01

### Added

- Jinja2 template system for TOPAS parameter file generation (`TemplateRenderer`, `.j2` boilerplates)
- `Orchestrator` coordinates mode selection, template rendering, and TOPAS execution
- Strategy pattern for simulation modes: `DicomMode` and `CtdiMode` extend `SimulationMode` ABC
- `Quantity` value object for type-safe physical quantities with units
- `CTDICalculator` service for post-simulation CTDI-w dose metric computation
- MVC separation in GUI: `MainView` (layout) + `GUIController` (events)
- CTDI calibration config support in YAML examples
- EM-only physics rationale documented for kV imaging simulations

### Changed

- Restructured monolithic scripts into modular `src/` package with `models/`, `modes/`, `gui/`, `services/`
- Configuration uses frozen dataclasses (`SimulationConfig`, `GeneralConfig`, `ImagingConfig`, etc.) with YAML round-trip
- CLI (`run_simulation.py`) provides `run`, `generate-config`, `validate`, `convert` commands via Typer
- `calculate_ctdiw.py` CLI for CTDI-w post-processing from runfolder output
- Defaults loaded from `config.yaml` before environment variables
- Boilerplate generation migrated from string manipulation to Jinja2 templates

### Fixed

- TOPAS return code checked after execution
- CTDI phantom includeFile directives corrected
- DICOM histories calculated as TIMESEQ * HIST (was string concatenation)
- Pre-existing bugs: init capitalization, calibration precision, env vars, bare excepts
- File I/O, logging, None guards, Quantity format string handling

### Removed

- Dead code and unused modules removed during restructuring
- Obsolete `defaultvalues.py` replaced by `SimulationConfig.defaults()`

---

## [0.1.0] - 2024-10-04

### Added

- FreeSimpleGUI-based desktop interface for Monte Carlo simulation configuration
- DICOM patient geometry simulation support
- CTDI phantom validation support (16 cm and 32 cm)
- TOPAS/Geant4 integration for kV imaging beam delivery simulation
- Beam energy spectrum generation using SpekPy
- Imaging mode presets (Image Gently, Head, Short Thorax, Spotlight, Thorax, Pelvis, Pelvis Large)
- Fan mode support (Full Fan, Half Fan)
- CBCT and kV-kV rotation directions
- Couch geometry support with configurable dimensions
- Collimator blade position calculations from field size
- Multiprocessing for CTDI simulations
- Patient ID extraction from DICOM datasets
- TOPAS parameter file editing via edit hooks

### Fixed

- Patient rotation in DICOM simulations
- CTDI 32 cm phantom invocation typo
- Calibration factor calculation referencing correct histories
- Firewall issues by changing batch file extension to `.txt`

---

## Version History Legend

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security vulnerability fixes
