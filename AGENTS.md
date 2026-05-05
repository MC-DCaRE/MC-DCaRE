# MC-DCaRE

## Purpose
Monte Carlo Dose Calculation for Risk Evaluation. Simulates Varian TrueBeam kV imaging beam delivery using TOPAS/Geant4 to estimate patient imaging dose from CBCT and kV-kV acquisitions. Developed by National Cancer Centre Singapore, Department of Radiation Oncology Physics.

## Architecture
Three entry points feed into the `src/` package:

1. **`topas_gui.py`** — FreeSimpleGUI desktop application. `MainView` (layout) + `GUIController` (events) + `Orchestrator` (simulation).
2. **`run_simulation.py`** — Typer CLI with commands: `run`, `generate-config`, `validate`, `convert`. Reads YAML configs via `SimulationConfig`.
3. **`calculate_ctdiw.py`** — Post-processing CLI. Takes a runfolder of TOPAS CSV output and computes CTDI-w weighted dose metrics.

Core data flow: `SimulationConfig` (YAML) -> `Orchestrator` creates runfolder and selects `SimulationMode` (CTDI or DICOM) -> mode builds Jinja2 context dict -> `TemplateRenderer` renders `.j2` boilerplate templates -> `SimulationRunner` executes TOPAS as a single process per simulation (capturing output to log files) -> `CTDICalculator` post-processes results. For CTDI mode, all 5 chamber plug positions are scored simultaneously using TOPAS Parallel Worlds (Layered Mass Geometry) in a single process. All Python logging is tee'd to `<runfolder>/simulation.log`.

## Repository Structure
```
AGENTS.md              # This file
run_simulation.py      # CLI entry point (typer)
topas_gui.py           # GUI entry point (FreeSimpleGUI)
calculate_ctdiw.py     # CTDI post-processing CLI
pyproject.toml         # Project config (hatchling build, deps, tool settings)
pytest.ini             # pytest overrides
src/                   # Core source package (see src/AGENTS.md)
  models/              # Domain value objects and enums
  modes/               # Simulation mode strategies (CTDI, DICOM)
  gui/                 # FreeSimpleGUI view and controller
  services/            # Post-simulation services (CTDI calculator)
  boilerplates/        # TOPAS parameter file templates
tests/                 # Test suite (see tests/AGENTS.md)
  unit/                # Isolated unit tests (17 files)
  smoke/               # Import and initialization checks
  integration/         # End-to-end pipeline tests
docs/                  # Design and implementation documentation
examples/config/       # Example YAML config files
runfolder/             # Runtime output (gitignored)
```

## Build/Test/Lint Commands
```bash
uv run python -m pytest tests/ -v              # Run tests
uv run python -m pytest tests/ --cov=src        # Tests with coverage
uv run black src/ tests/                        # Format
uv run ruff check src/ tests/ --fix             # Lint
uv run mypy src/                                # Type check
```

Test runner: pytest with `--cov=src --cov-report=html --cov-report=term-missing` configured in `pyproject.toml`. A simpler `pytest.ini` overrides addopts to `-v` only.

## Conventions
- Python >=3.8, `from __future__ import annotations` in every module
- `logging.getLogger(__name__)` for all logging, never `print()` (except entry points)
- `frozen=True` dataclasses for immutable value objects
- All imports use `src.` prefix (e.g., `from src.config import SimulationConfig`)
- Build system: hatchling, package defined as `src`
- Line length: 88 (black/ruff), mypy targets Python 3.9
- Commit format: `type(scope): description` (feat/fix/docs/style/refactor/test/chore)
- Base branch: `develop`; `main` for stable releases only

## Operational Gotchas
- **TOPAS + Geant4 required** for actual Monte Carlo execution. Tests mock TOPAS calls.
- **FreeSimpleGUI** is the GUI framework; requires a display server for GUI mode
- **CTDI Parallel Worlds**: CTDI simulations use TOPAS Layered Mass Geometry with 5 parallel worlds (one per chamber plug position). All plugs are scored simultaneously in a single TOPAS process — no Python multiprocessing is involved.
- `runfolder/` and `tmp/` are runtime output directories, gitignored
- `src/boilerplates/TOPAS_includeFiles/Muen.dat` is a binary data file (mass energy-absorption coefficients)
- `ruff.lint.per-file-ignores` allows `F403`/`F405` in `topas_gui.py` for star imports
- mypy ignores missing imports for `FreeSimpleGUI`, `spekpy`, `pandas`
