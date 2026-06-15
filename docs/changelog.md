# Changelog

All notable changes to MC-DCaRE will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Dose Calibration Factor (DCF) for all beam-quality groups:
  - **80 kV Full Fan** (Image Gently, 100 mAs): DCF = 0.001087
  - **100 kV Full Fan** (Head, 150 mAs): DCF = 0.001194
  - **125 kV Full Fan** (Pelvis Spotlight, 750 mAs, scaled from Short Thorax ref 12.3 mGy @ 210 mAs): DCF = 0.004486
  - **125 kV Half Fan** (Pelvis, 1080 mAs): DCF = 0.001672
  - **140 kV Half Fan** (Pelvis Large, 1700.5 mAs): DCF = 0.001798
- 4 calibration run configs (`configs/cal_*.yaml`) and 1 cross-validation config (`configs/xval_125kv_ff_short-thorax.yaml`)
- `calibration.example.yaml` populated with all computed DCFs and measured CTDI_w values
- Cross-validation confirms DCF transfer within (kV, fan) group:
  - 125 kV FF: Pelvis (750 mAs) → Short Thorax (210 mAs): +0.00% error
  - 125 kV HF: Pelvis (1080 mAs) → Thorax (268.5 mAs): −0.62% error
- Arc-dependence test confirms DCF is independent of arc length at same (kV, fan_mode):
  - 125 kV HF Pelvis half-arc (timeline_end=450 s, 80 seq, 80M histories, 1074 mAs): raw CTDI_w=9.583 Gy, DCF-applied=16.02 mGy vs 15.9 mGy ref (+0.75%), PASS
  - Raw CTDI_w does NOT halve with arc length — same head_cal_factor (same mAs + same total_histories) keeps dose-per-particle normalization constant; only angular distribution changes
  - `NumberOfSequentialTimes` controls total particles only, not arc geometry
- Dose-level linearity test confirms DCF scales correctly with mAs:
  - 125 kV HF Pelvis half-dose (540 mAs, half of 1080): raw CTDI_w=4.818 Gy (50.7% of full dose), calibrated=8.06 mGy vs half-reference 7.95 mGy (+1.34%), PASS
  - DCF linearity holds — the calibration chain correctly handles partial exposures
- Cross-fan-mode test confirms DCFs do NOT transfer between fan modes at the same kV:
  - 125 kV FF DCF (0.004486) applied to 125 kV HF simulation: +165% error
  - Each (kV, fan_mode) pair requires independent calibration

### Changed

- 125 kV FF DCF corrected from 0.001256 → 0.004486 (previous used un-scaled Short Thorax reference of 12.3 mGy at 210 mAs against 750 mAs calibration)

### Notes

- 100 kV Half Fan (4 protocols, 150 mAs): no reference CTDI_w available, cannot calibrate
- 140 kV Full Fan: no CBCT protocol in reference table, cannot calibrate
- Half fan summary: 100 kV HF: no reference, cannot calibrate. 125 kV HF (12 protocols): calibrated and cross-validated. 140 kV HF (2 protocols): calibrated, no second reference for cross-validation
- DCF is specific to (kV, fan_mode) — Full Fan and Half Fan at the same kV differ by factor 2.68× (125 kV) due to different bowtie filtration and scatter geometry

### Changed (previous)

- Replaced Python multiprocessing with TOPAS Parallel Worlds (Layered Mass Geometry) for CTDI simulations. A single TOPAS process now scores all 5 chamber plug positions (Centre, Top, Bottom, Left, Right) simultaneously using parallel worlds, eliminating the need for Python-level multiprocessing. The full `threads` count from the config is allocated to the single TOPAS process instead of being split across 5 separate processes, giving TOPAS/Geant4 maximum multithreading efficiency.
- CTDI simulations now generate a single `CTDI_all_positions.txt` parameter file with 15 scorers (3 per position) instead of 5 separate parameter files.
- `SimulationRunner` no longer uses `multiprocessing`; `run_ctdi()` removed in favour of direct `run_topas()` call from `CtdiMode.execute()`.
- YAML configs simplified: beam parameters (voltage, exposure, blades, field size, etc.) no longer need to be specified manually when `rotation_direction` and `imaging_mode` are set
- `imaging_modes_lookuptable.py` removed; all consumers now import directly from `imaging_mode.py`
- `IMAGING_MODE_SELECTION_LABELS` expanded from 7 to 21 entries
- `as_tuple()` uses `dataclasses.fields()` dynamically instead of hardcoded field count
- `BACKWARD_COMPAT_LOOKUP` maps 48 old-style keys to 21-element tuples

### Fixed

- `CtdiMode.compute_histories()` now correctly multiplies `histories` by `sequential_times` to produce total histories, matching `DicomMode`. This ensures the calibration factor in `head_calibration_factor.txt` is computed with the correct denominator for both CTDI and DICOM simulation modes.
- Empty string `rotation_direction` and `imaging_mode` values in YAML no longer raise `ValueError` — skip resolution for backward compatibility
- Whitespace-padded direction/mode values are stripped before lookup
- `field_x2` normalized from `"14.0 cm"` to `"14 cm"` for consistency with `field_x1`

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
