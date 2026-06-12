# Plan: Codebase Quality Improvements

## Problem
The MC-DCaRE codebase has accumulated technical debt across several dimensions: dead/duplicate code (~900 lines), zero docstrings, no config validation, security risks, silent failure modes, and test suite DRY violations. All 257 tests pass, lint/type checks are clean — this is the right time to address quality systematically.

## Approach
Six phases, ordered to avoid rework. Each phase is independently committable.

---

## Phase 1: Remove Dead Code

### 1a. Delete `src/guilayers.py` (755 lines)
`src/gui/view.py` is the authoritative GUI layout. `guilayers.py` is a legacy duplicate that uses hardcoded `-KEY-` strings instead of the centralized `keys.py` constants. Only consumed by:
- `topas_gui.py` (star import: `from src.guilayers import *`) — update to use `src.gui.view` / `src.gui.controller`
- `tests/smoke/test_guilayers.py` — delete this test (it tests dead code)

**Steps:**
1. Update `topas_gui.py` to import from `src.gui` instead of `src.guilayers`
2. Update `src/gui/controller.py` if it imports from `guilayers`
3. Delete `src/guilayers.py`
4. Delete `tests/smoke/test_guilayers.py`
5. Update `pyproject.toml` ruff per-file-ignores (remove `test_guilayers.py` F401 entry)
6. Run tests, lint, mypy

### 1b. Evaluate `src/run_preparer.py` for removal
`RunPreparer` duplicates logic now in `CtdiMode.prepare_run`, `DicomMode.prepare_run`, and `SimulationMode.copy_common_files`. Verify no active importers remain, then delete. If `run_preparer.py` is still imported, refactor callers first.

**Files to check for imports:** `src/orchestrator.py`, `src/modes/ctdi_mode.py`, `src/modes/dicom_mode.py`, all tests.

If deleted, also delete `tests/unit/test_run_preparer.py` and move any unique test coverage to the mode test files.

### Files
| File | Action | Purpose |
|------|--------|---------|
| `src/guilayers.py` | Delete | Dead code, duplicated by gui/view.py |
| `tests/smoke/test_guilayers.py` | Delete | Tests dead code |
| `topas_gui.py` | Edit | Update imports away from guilayers |
| `pyproject.toml` | Edit | Remove per-file-ignore for deleted test |
| `src/run_preparer.py` | Evaluate → Delete | Duplicated by mode classes |
| `tests/unit/test_run_preparer.py` | Evaluate → Delete | Tests for deleted module |

---

## Phase 2: Security & Silent Failures

### 2a. Fix `shell=True` in `simulation_runner.py`
Replace `subprocess.run(command, ..., shell=True)` with `subprocess.run(command.split(), ...)` or accept a list argument. The `command` string is built from `topas_path` and `main_file` — both user-configurable. Using a list avoids shell injection.

### 2b. Make `Quantity.parse()` raise on bad input
Currently returns `Quantity(0.0, "")` for unparseable strings like `"abc"`. Raise `ValueError` instead. Update any callers that depend on silent-zero behavior.

### 2c. Fix `CTDICalculator._extract_calibration_factor` silent fallback
Three `return 1.0` paths silently produce wrong dose calculations. Options:
- **Preferred**: Raise `ValueError` with descriptive message
- Caller (`__init__`) can catch and decide whether to abort or warn
- This is a breaking change for `calculate_ctdiw.py` CLI — add error handling there

### 2d. Fix `_parse_bool()` fragility
Currently only handles `True` and string `"True"`. Add handling for `"true"`, `"TRUE"`, `"1"`, `"yes"` (case-insensitive). YAML `safe_load` already converts booleans, so this mainly affects GUI string inputs.

### Files
| File | Action | Purpose |
|------|--------|---------|
| `src/simulation_runner.py` | Edit | Replace shell=True with list args |
| `src/models/quantity.py` | Edit | Raise ValueError on unparseable input |
| `src/services/ctdi_calculator.py` | Edit | Raise instead of silent 1.0 fallback |
| `calculate_ctdiw.py` | Edit | Catch ValueError from calculator |
| `src/config.py` | Edit | Make _parse_bool() more robust |

---

## Phase 3: Config Validation

### 3a. Use enums in config instead of raw strings
Replace `simulation_type: str`, `fan_mode: str`, `rotation_direction: str` with their enum types from `models/enums.py`. Update `SimulationConfig.from_yaml()` to validate string values against enum members.

### 3b. Add missing enums
- `PhantomSize` enum: `"16 cm"`, `"32 cm"`
- Consider `ImagingModeName` enum for the 7 body-part mode names

### 3c. Add validation to `SimulationConfig.from_yaml()`
- Check `yaml.safe_load` result is a dict
- Validate numeric fields (`seed`, `threads`, `histories`, `zbins`) are parseable as positive integers
- Validate enum fields against enum members
- Validate path fields are non-empty
- Raise `ValueError` with field-specific messages on invalid input

### 3d. Make sub-configs frozen
Add `frozen=True` to `GeneralConfig`, `ImagingConfig`, `DicomConfig`, `CtdiConfig`. This matches project conventions and prevents accidental mutation.

### 3e. Fix `SimulationType.CTDI` value
Currently `"CTDI validation"` but orchestrator compares against `"DICOM"` string. With enum usage this becomes moot, but verify the enum value matches all usage sites.

### Files
| File | Action | Purpose |
|------|--------|---------|
| `src/models/enums.py` | Edit | Add PhantomSize enum, fix CTDI value |
| `src/config.py` | Edit | Use enums, add validation, freeze sub-configs |
| `src/orchestrator.py` | Edit | Use enum comparison instead of string |
| `src/modes/ctdi_mode.py` | Edit | Use PhantomSize enum |
| `src/modes/dicom_mode.py` | Edit | Update int() casts to work with validated config |
| `tests/unit/test_config.py` | Edit | Add validation test cases |

---

## Phase 4: Add Docstrings

Add PEP 257 compliant docstrings to all public classes and functions in `src/`. Focus on:
- Module-level docstrings (purpose + key exports)
- Class docstrings (purpose, usage)
- Public method docstrings (args, returns, raises)
- Skip private methods (`_prefix`) unless non-trivial

Order: models → config → modes → services → gui → remaining modules

### Files
| File | Action |
|------|--------|
| `src/models/quantity.py` | Add docstrings |
| `src/models/enums.py` | Add docstrings |
| `src/models/imaging_mode.py` | Add docstrings |
| `src/models/keys.py` | Add module docstring |
| `src/config.py` | Add docstrings |
| `src/orchestrator.py` | Add docstrings |
| `src/modes/base.py` | Add docstrings (especially abstract methods) |
| `src/modes/ctdi_mode.py` | Add docstrings |
| `src/modes/dicom_mode.py` | Add docstrings |
| `src/services/ctdi_calculator.py` | Add docstrings |
| `src/gui/controller.py` | Add docstrings |
| `src/gui/view.py` | Add docstrings |
| `src/boilerplate_manager.py` | Add docstrings |
| `src/parameter_editor.py` | Add docstrings |
| `src/simulation_runner.py` | Add docstrings |
| `src/spectrum_generator.py` | Add docstrings |
| `src/fieldtobladeopening.py` | Add docstrings |

Also add `from __future__ import annotations` to the 7 files missing it:
- `src/boilerplate_manager.py`
- `src/simulation_runner.py`
- `src/spectrum_generator.py`
- `src/run_preparer.py` (if kept)
- `src/fieldtobladeopening.py`
- `src/imaging_modes_lookuptable.py`

---

## Phase 5: Test Suite Cleanup

### 5a. Create root `tests/conftest.py`
Add `sys.path` configuration once, shared by all test files. Remove `sys.path.insert()` from every individual test file.

### 5b. Consolidate shared test fixtures into `tests/unit/conftest.py`
Move to conftest.py:
- `MAIN_FILE_CONTENT`, `DICOM_SUB_FILE_CONTENT`, `CTDI_SUB_FILE_CONTENT` (currently duplicated in 4 files)
- `fake_project` fixture (duplicated in 2 test files)
- `make_config` fixture (already in conftest, keep)

### 5c. Remove duplicated content from test files
- `tests/unit/test_orchestrator.py` — remove local MAIN_FILE_CONTENT, use conftest
- `tests/unit/test_ctdi_mode.py` — remove local constants, use conftest
- `tests/unit/test_dicom_mode.py` — remove local constants, use conftest
- `tests/unit/test_boilerplate_manager.py` — use shared fake_project
- `tests/unit/test_base_mode.py` — use shared fake_project
- All test files — remove `sys.path.insert()` lines

### 5d. Add CLI tests
- `tests/unit/test_run_simulation_cli.py` — test `run`, `generate-config`, `validate`, `convert` commands via `typer.testing.CliRunner`
- `tests/unit/test_calculate_ctdiw_cli.py` — test `calculate_ctdiw.py` command

### Files
| File | Action | Purpose |
|------|--------|---------|
| `tests/conftest.py` | Create | Root-level sys.path setup |
| `tests/unit/conftest.py` | Edit | Add shared boilerplate strings and fixtures |
| `tests/unit/test_orchestrator.py` | Edit | Remove dupes, use conftest |
| `tests/unit/test_ctdi_mode.py` | Edit | Remove dupes, use conftest |
| `tests/unit/test_dicom_mode.py` | Edit | Remove dupes, use conftest |
| `tests/unit/test_boilerplate_manager.py` | Edit | Use shared fake_project |
| `tests/unit/test_base_mode.py` | Edit | Use shared fake_project |
| All test files | Edit | Remove sys.path.insert lines |
| `tests/unit/test_run_simulation_cli.py` | Create | CLI tests for run_simulation.py |
| `tests/unit/test_calculate_ctdiw_cli.py` | Create | CLI tests for calculate_ctdiw.py |

---

## Phase 6: Minor Cleanups

These don't warrant a full phase but should be addressed:

1. **Remove triple file-copy duplication**: `SimulationMode.copy_common_files` (base.py), `RunPreparer._copy_common_files`, and `DicomMode.prepare_run` all copy the same files. After Phase 1b removes `RunPreparer`, ensure `DicomMode.prepare_run` calls `copy_common_files` instead of duplicating.

2. **`src/boilerplate_manager.py` repetitive copy blocks**: 4 nearly identical `shutil.copy2` pairs. Extract a `_copy_file(src, dst)` helper.

3. **`src/gui/controller.py` bare `except Exception`**: Lines 97, 112, 124. Add logging of the caught exception before showing error popup.

---

## Implementation Order

```
Phase 1 → Phase 2 → Phase 3 → Phase 5 → Phase 4 → Phase 6
(dead code) (safety)  (config)   (tests)   (docs)   (cleanup)
```

Rationale:
- Dead code removal first (no point documenting/deleting code that will be removed)
- Safety fixes second (behavior changes that tests must reflect)
- Config validation third (behavior changes, depends on enum cleanup)
- Test cleanup fourth (consolidate after source changes stabilize)
- Docstrings fifth (stable API surface to document)
- Minor cleanups last (polish)

## Key Design Decisions

1. **`Quantity.parse()` raises `ValueError`** instead of silent zero. This is a behavior change. Callers that relied on silent-zero need updating. Search for `Quantity.parse` usages and add try/except where appropriate.

2. **`CTDICalculator._extract_calibration_factor` raises on failure**. The `calculate_ctdiw.py` CLI will catch and report the error. This prevents silently wrong dose calculations.

3. **Config sub-configs become `frozen=True`**. This matches project conventions. Any code that mutates config after creation needs refactoring.

4. **Enum-based config fields**. `simulation_type`, `fan_mode`, `rotation_direction` use their enum types. YAML values are validated on load. Invalid values raise `ValueError` with a clear message listing valid options.

5. **`run_preparer.py` deletion depends on import audit**. If it's imported by the orchestrator or modes, refactor those callers first. The test file has useful coverage that should be preserved in mode tests if deleted.

## Completion Quality Gates
- [ ] `uv run python -m pytest tests/ -v` — all tests pass (target: 260+)
- [ ] `uv run ruff check src/ tests/` — clean
- [ ] `uv run black --check src/ tests/` — clean
- [ ] `uv run mypy src/` — clean
- [ ] No dead code imports remain
- [ ] Config validation rejects invalid YAML with clear error messages
- [ ] No silent failure paths in Quantity.parse or CTDICalculator
