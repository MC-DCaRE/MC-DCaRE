# Tasks: Dose Calibration Workflow

## Task 1: Fix dk comment and remove NbParticlesInTime.txt copy
- [x] Fix comment in `src/spectrum_generator.py` lines 41-43 (dk is keV bin width, not filtration)
- [x] Remove `shutil.copy(NbParticlesInTime.txt)` from `src/modes/base.py`
- [x] Update `tests/unit/test_base_mode.py` — remove NbParticlesInTime assertions
- [x] Update `tests/integration/test_dry_run_pipeline.py` — remove from expected file lists
- [x] Run `ruff format`, `ruff check`, `mypy`, `pytest`

## Task 2: Create calibration data model
- [x] Create `src/models/calibration.py` with `CalibrationEntry` and `MachineCalibration` frozen dataclasses
- [x] Implement `from_yaml(path)` classmethod with duplicate-key validation
- [x] Implement `to_yaml(path)` method
- [x] Create `tests/unit/test_calibration_model.py` with tests for loading, saving, duplicate detection
- [x] Run `ruff format`, `ruff check`, `mypy`, `pytest`

## Task 3: Create initial calibration.yaml
- [x] Create `calibration.yaml` in project root with all 6 (kV, fan_mode) entries, dcf: null
- [x] Add `calibration.yaml` to `.gitignore` (contains machine-specific measurement data)
- [x] Create `calibration.example.yaml` committed to repo with one populated entry as documentation:
  ```yaml
  machine: "TrueBeam-SN1234"
  date_calibrated: "2026-06-10"
  calibrations:
    - kV: 120
      fan_mode: "Full Fan"
      reference_mAs: 100
      measured_ctdi_w_mGy: 45.2
      dcf: 1.034
    - kV: 80
      fan_mode: "Full Fan"
      reference_mAs: 100
      measured_ctdi_w_mGy: null
      dcf: null
    # ... remaining entries with null values
  ```

## Task 4: Add simulation_metadata.yaml output to SpectrumGenerator
- [x] Add `fan_mode`, `seed`, `threads` parameters to `SpectrumGenerator.generate()`
- [x] Compute `norm_factor` separately from combined factor (per-mAs: `norm_factor = calib_factor / mAs`, with DCF=1.0, using SpekPy fluence linearity)
- [x] Write `simulation_metadata.yaml` to `tmp/` with all fields from CAL-META-001
- [x] Continue writing backward-compatible `head_calibration_factor.txt`
- [x] Update `src/modes/base.py` `copy_common_files()` to copy `simulation_metadata.yaml` to runfolder
- [x] Update `src/orchestrator.py` to pass `fan_mode` to `SpectrumGenerator.generate()`
- [x] Update `tests/unit/test_spectrum_generator.py` for new output file and parameter
- [x] Run `ruff format`, `ruff check`, `mypy`, `pytest`

## Task 5: Add backward-compatible metadata reader to CTDICalculator
- [x] Add `_read_simulation_metadata()` method — try `simulation_metadata.yaml` first, fall back to `head_calibration_factor.txt`
- [x] No behavior change when only `head_calibration_factor.txt` exists
- [x] Update `tests/unit/test_ctdi_calculator.py` with tests for both paths
- [x] Run `ruff format`, `ruff check`, `mypy`, `pytest`

## Task 6: Create CalibrationService
- [x] Create `src/services/calibration.py` with `CalibrationService` class
- [x] Implement `compute_dcf()` — compute, write back to calibration.yaml
- [x] Implement `lookup_dcf()` — return DCF or None
- [x] Implement `apply()` — full pipeline: CTDICalculator → DCF → mAs scaling
- [x] Create `tests/unit/test_calibration_service.py` with happy path and error conditions
- [x] Run `ruff format`, `ruff check`, `mypy`, `pytest`

## Task 7: Integration test
- [x] Add test to `tests/integration/` that exercises the full calibration flow: generate metadata → compute DCF → apply → verify scaling
- [x] Use temporary directories and mock TOPAS output
- [x] Verify backward compatibility with old-format runfolders
- [x] Run full test suite
