## 1. Fix Normalization Functions

- [ ] 1.1 Fix `compute_photons_per_mAs()` in `src/services/calibration.py`: use `N_scoring` (scoring run's `total_histories`) instead of current simulation's `total_histories`. Read `N_scoring` from metadata's `total_histories` field (which is the scoring run value for replay metadata, and the scoring run value for CTDI calibration metadata).
- [ ] 1.2 Rename `total_histories` parameter to `n_scorer_active_histories` in `raw_absolute_dose_Gy()`. Update docstring. The formula becomes: `(raw_sum / n_scorer_active_histories) × photons_per_mAs × mAs_used`.
- [ ] 1.3 Add a helper function `extract_scorer_histories(csv_path)` that reads `Histories_with_Scorer_Active` from a TOPAS CSV file. Returns the integer count. Used by CTDICalculator and PhantomDoseCalculator.

## 2. Fix Replay Metadata

- [ ] 2.1 In `src/orchestrator.py` `_write_replay_metadata()`: remove the `divisor = phase_space_multiple_use * max(1, sequential_times)` logic. Keep `spectrum_fluence_photons_per_mAs` unchanged from the scoring metadata. Still record `phase_space_multiple_use` and `phase_space_sequential_times` for reference.

## 3. Update Callers

- [ ] 3.1 Update `CTDICalculator._process_file_type()`: extract `N_scorer_active_histories` from one of the position CSV files. Pass it through to `_normalize_dose()` → `raw_absolute_dose_Gy()`.
- [ ] 3.2 Update `PhantomDoseCalculator.calculate()`: extract `N_scorer_active_histories` from the phantom dose CSV. Pass it to the normalization pipeline.
- [ ] 3.3 Update `src/services/calibration.py` `_normalize_dose()`: accept `n_scorer_active_histories` parameter (either passed in or extracted from CSV). Pass to `raw_absolute_dose_Gy()`.
- [ ] 3.4 Update `src/services/benchmark_calculator.py` if it calls `raw_absolute_dose_Gy()`.
- [ ] 3.5 Update `calculate_phantom_dose.py` (CLI entry point) if it calls normalization functions directly.
- [ ] 3.6 Grep for any remaining callers of `raw_absolute_dose_Gy` or `compute_photons_per_mAs` and update them.

## 4. Tests

- [ ] 4.1 Update `tests/unit/test_calibration.py`: update expected values for `raw_absolute_dose_Gy` and `compute_photons_per_mAs` with the new formula. Add tests for: (a) CTDI with sequential_times=36, (b) replay with M=5, (c) verify M and R cancel (independence).
- [ ] 4.2 Add test for `extract_scorer_histories()` — reads a sample CSV and returns the correct count.
- [ ] 4.3 Run full test suite (`pytest tests/ -v`) — fix any failures from the signature change.
- [ ] 4.4 Run ruff format + ruff check + mypy on all changed files.

## 5. Recompute DCFs and Verify

- [ ] 5.1 Recompute all 5 protocol DCFs (TLE) from existing CTDI calibration CSVs using the new normalization. Update `calibration.yaml`.
- [ ] 5.2 Recompute pelvis DTM DCF from the 36-angle rotational water-hole CTDI CSV. Update `calibration.yaml`.
- [ ] 5.3 Recompute pelvis phantom effective dose with the new DCF. Compare with 4.2 mSv reference.
- [ ] 5.4 Verify: DCF from CTDI calibration produces physically reasonable organ doses (not 100× off).
