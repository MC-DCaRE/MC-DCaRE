# unit

## Purpose
Isolated unit tests for every module in `src/`. Each test file covers one source module, testing public interfaces with mocked dependencies.

## Architecture
17 test files mirroring `src/` module structure. `conftest.py` provides shared fixtures (default `SimulationConfig`, mock paths, sample data). `shared.py` provides context dict constants used by mode and orchestrator tests. Tests use `pytest-mock` for patching and `tmp_path` for filesystem operations.

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
| `test_calculate_ctdiw.py` | CTDI-w calculation from chamber plug CSV data |

## Conventions
- Test files named `test_<src_module>.py` matching source module names
- `from __future__ import annotations` at top of every test file
- Fixtures from `conftest.py` for shared setup; `mocker` fixture from `pytest-mock` for patching
- `tmp_path` pytest fixture for filesystem-dependent tests (never write to project directories)
- TOPAS execution always mocked -- no TOPAS binary required for tests
- Test functions named `test_<behavior>_<condition>` or `test_<method>_<scenario>`
- `__init__.py` present for test discovery
