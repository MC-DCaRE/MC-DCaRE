# unit

## Purpose
Isolated unit tests for every module in `src/`. Each test file covers one source module, testing public interfaces with mocked dependencies.

## Architecture
24 test files mirroring `src/` module structure. `conftest.py` provides shared fixtures (default `SimulationConfig`, mock paths, sample data). `shared.py` provides context dict constants used by mode and orchestrator tests. Tests use `pytest-mock` for patching and `tmp_path` for filesystem operations. Real-TOPAS ground-truth fixtures live in `tests/fixtures/` (e.g. `topas_writebinary_example.{phsp,header}`, a 1031-particle proton run).

## Key Files

| File | Tests |
|---|---|
| `conftest.py` | Shared fixtures: default `SimulationConfig`, temporary directories, sample configs |
| `shared.py` | Context dict constants (`MAIN_CONTEXT`, `CTDI_SUB_CONTEXT`, `DICOM_SUB_CONTEXT`) for mode and orchestrator tests |
| `test_config.py` | `SimulationConfig` creation, YAML round-trip, validation, defaults, `_resolve_imaging_mode()` (15-field resolution, edge cases, completeness) |
| `test_orchestrator.py` | `Orchestrator` mode selection, Jinja2 rendering, run directory preparation |
| `test_ctdi_mode.py` | `CtdiMode` context building, plug file generation, blade opening calculation |
| `test_dicom_mode.py` | `DicomMode` context building, DICOM file staging, include file selection |
| `test_base_mode.py` | `SimulationMode` ABC contract, shared helper methods |
| `test_template_renderer.py` | `TemplateRenderer` Jinja2 rendering, file output, context substitution |
| `test_boilerplate_manager.py` | `BoilerplateManager` renderer creation, tmp directory management |
| `test_simulation_runner.py` | `SimulationRunner` TOPAS execution, subprocess mocking |
| `test_run_simulation_cli.py` | CLI entry point commands, config generation, validation |
| `test_spectrum_generator.py` | `SpectrumGenerator` X-ray spectrum generation, SpekPy integration |
| `test_gui_controller.py` | `GUIController` event handling, config updates, orchestrator delegation |
| `test_gui_view.py` | `MainView` layout construction, element presence, theme application, imaging mode field updates (including CTDI phantom) |
| `test_enums.py` | `SimulationType` and `FanMode` enum values and membership |
| `test_quantity.py` | `Quantity` dataclass immutability, value/unit access |
| `test_imaging_mode.py` | `ImagingMode` lookup tables (47 modes, 21 fields), parameter retrieval by mode name, fan/blade consistency, phantom validation, backward compat |
| `test_fieldtobladeopening.py` | `fieldtobladeopening` conversion function, boundary values |
| `test_calculate_ctdiw.py` | CTDI-w calculation from chamber plug CSV data; `_compute_raw_Gy` canonical-helper division regression |
| `test_calibration_service.py` | `CalibrationService` compute/lookup/normalize/apply DCF; canonical `raw_absolute_dose_Gy` + `compute_photons_per_mAs` guard helpers |
| `test_calibration_model.py` | `MachineCalibration`/`CalibrationEntry` YAML round-trip and validation |
| `test_ctdi_benchmark.py` | `BenchmarkCalculator` simulated-vs-reference comparison (TLE only) |
| `test_phase_space_analyzer.py` | Header-driven PhaseSpaceAnalyzer parsing + statistics; real-TOPAS fixture ground-truth regression |

## Conventions
- Test files named `test_<src_module>.py` matching source module names
- `from __future__ import annotations` at top of every test file
- Fixtures from `conftest.py` for shared setup; `mocker` fixture from `pytest-mock` for patching
- `tmp_path` pytest fixture for filesystem-dependent tests (never write to project directories)
- TOPAS execution always mocked -- no TOPAS binary required for tests
- Test functions named `test_<behavior>_<condition>` or `test_<method>_<scenario>`
- `__init__.py` present for test discovery
