# Agent Instructions

## Python Commands

Always use `uv run` as the prefix for all Python commands in this project. Examples:

- `uv run pytest tests/ -v`
- `uv run python script.py`
- `uv run ruff check src/`
- `uv run ruff format src/`

Never use bare `python`, `python3`, or `pip install` commands.

## Project Overview

MC-DCaRE (Monte Carlo - Dose Calculation for Risk Evaluation) simulates Varian TrueBeam kV imaging dose using TOPAS/Geant4 Monte Carlo. The GUI (`topas_gui.py`) is the main entrypoint for end-users; `run_simulation.py` is the CLI entrypoint for YAML-driven runs; `calculate_ctdiw.py` is a standalone CLI tool for post-processing CTDI results.

External dependencies not installable via pip: TOPAS and Geant4 must be installed separately and their paths configured at runtime via the GUI, CLI YAML config, or env vars (`G4DATA_DIR`, `TOPAS_DIR`).

## Architecture

- `topas_gui.py` — FreeSimpleGUI application, main entrypoint. Uses `Orchestrator` for all simulation logic.
- `run_simulation.py` — CLI entrypoint for running simulations from YAML config files via Typer.
- `calculate_ctdiw.py` — Standalone Typer CLI for computing CTDI_w from ChamberPlug CSV output files.
- `src/` — All library code (the `src` package is the wheel target):
  - `config.py` — `SimulationConfig` dataclasses (`GeneralConfig`, `ImagingConfig`, `DicomConfig`, `CtdiConfig`) + YAML I/O + `quantity_unit_stripper`
  - `boilerplate_manager.py` — `BoilerplateManager` class for boilerplate file copying/reset
  - `parameter_editor.py` — `ParameterEditor` class for TOPAS parameter file editing (was `edits_handler.py`)
  - `spectrum_generator.py` — `SpectrumGenerator` class for X-ray spectrum generation via Spekpy (was `Energyspectrum.py`)
  - `run_preparer.py` — `RunPreparer` class for runfolder creation and file generation
  - `simulation_runner.py` — `SimulationRunner` class for TOPAS process execution
  - `orchestrator.py` — `Orchestrator` class coordinating config → edit → prepare → run pipeline
  - `guilayers.py` — GUI element definitions with readable keys/labels (imports `SimulationConfig.defaults()`)
  - `fieldtobladeopening.py` — Field-size-to-blade-position conversion
  - `imaging_modes_lookuptable.py` — Hardcoded lookup table for Varian imaging protocols
  - `boilerplates/` — TOPAS text templates copied to `tmp/` at runtime and edited in-place
- `tmp/` — Runtime working directory for editable copies of boilerplates (gitignored)
- `runfolder/` — Timestamped output directories for simulation results (gitignored)

## Testing

Tests are organized into three tiers under `tests/`:

- `tests/unit/` — Unit tests with mocks (no external dependencies needed)
- `tests/smoke/` — Smoke tests for module imports and basic value checks
- `tests/integration/` — Integration tests (currently empty)

Test configuration is split between `pytest.ini` (simple) and `pyproject.toml` `[tool.pytest.ini_options]`. The pyproject.toml version adds `--cov=src` coverage flags; `pytest.ini` does not. Running bare `uv run pytest` will use `pytest.ini` settings by default.

Run a single test file:
- `uv run pytest tests/unit/test_config.py -v`
- `uv run pytest tests/unit/test_parameter_editor.py -v`

Run a single tier:
- `uv run pytest tests/unit/ -v`
- `uv run pytest tests/smoke/ -v`

Tests use `sys.path.append` / `sys.path.insert` to import from `src/` rather than relying on an installed package.

## Lint & Format

- Formatter: `ruff` and `black` (both configured, line-length 88, target Python 3.8)
- Type checker: `mypy` with `disallow_untyped_defs = true` — all functions need type annotations
- Linter: `ruff check`

Suggested check order: `ruff format src/` → `ruff check src/` → `uv run pytest tests/ -v`

## Key Quirks

- Python target is 3.8+ (`requires-python = ">=3.8"`). Avoid walrus operator, `str.removeprefix`, `match` statements, or other post-3.8 features.
- `src/` is both a Python package (`__init__.py`) and the hatch wheel build target. Imports use `from src.module import ...`.
- The GUI (`topas_gui.py`) does `from src.guilayers import *` — wildcard import pulls in FreeSimpleGUI element globals and defaults from `SimulationConfig.defaults()`.
- The `src/config.py` module contains `SimulationConfig.defaults()` which replaces `defaultvalues.py`. Env vars `G4DATA_DIR` and `TOPAS_DIR` are read there.
- TOPAS parameter files are plain text edited via string search-and-replace (`parameter_editor.py`), not structured config parsing.
- `tmp/` must exist at runtime; `BoilerplateManager.reset_tmp()` copies boilerplates there before each simulation run.
- `spekpy` is used for X-ray spectrum generation and must be importable for unit tests (tests mock it).
