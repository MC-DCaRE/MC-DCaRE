# tests

## Purpose
Test suite for MC-DCaRE covering unit tests for all source modules, smoke tests for basic imports, and integration tests for end-to-end pipelines.

## Architecture
Three tiers by scope:
- **unit/** (~20 files) — Isolated tests per source module: config, modes, models, orchestrator, GUI, services. Contains `conftest.py` with shared fixtures.
- **smoke/** (~5 files) — Lightweight import and initialization checks: config loading, GUI layer creation, lookup table validation
- **integration/** — Cross-module pipeline tests: `test_dry_run_pipeline.py` validates full orchestration without running TOPAS

## Key Files

| File | Role |
|---|---|
| `unit/conftest.py` | Shared unit test fixtures |
| `unit/test_orchestrator.py` | Orchestrator mode selection and parameter editing tests |
| `unit/test_ctdi_mode.py` | CTDI simulation mode tests |
| `unit/test_dicom_mode.py` | DICOM simulation mode tests |
| `smoke/test_init.py` | Basic import validation |
| `integration/test_dry_run_pipeline.py` | End-to-end pipeline without Monte Carlo execution |

## Conventions
- pytest framework; `__init__.py` in each subdirectory
- Unit tests named `test_<module>.py` matching `src/` module names
- Smoke tests verify importability and basic instantiation only
- Integration tests use temporary directories and mock TOPAS execution
- `from __future__ import annotations` at top of test files (matching source convention)
