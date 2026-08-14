## 1. Fix Normalization Functions

- [x] 1.1 Fix `compute_photons_per_mAs()` in `src/services/calibration.py`: use `N_scoring` (scoring run's `total_histories`) instead of current simulation's `total_histories`. Read `N_scoring` from metadata's `total_histories` field (which is the scoring run value for replay metadata, and the scoring run value for CTDI calibration metadata).
- [x] 1.2 Rename `total_histories` parameter to `n_scorer_active_histories` in `raw_absolute_dose_Gy()`. Update docstring. The formula becomes: `(raw_sum / n_scorer_active_histories) × photons_per_mAs × mAs_used`.
- [x] 1.3 Add a helper function `extract_scorer_histories(csv_path)` that reads `Histories_with_Scorer_Active` from a TOPAS CSV file. Returns the integer count. Used by CTDICalculator and PhantomDoseCalculator. (Lives in `ctdi_calculator.py` to avoid a circular import with `calibration.py`.)

## 2. Fix Replay Metadata

- [x] 2.1 In `src/orchestrator.py` `_write_replay_metadata()`: remove the `divisor = phase_space_multiple_use * max(1, sequential_times)` logic. Keep `spectrum_fluence_photons_per_mAs` unchanged from the scoring metadata. Still record `phase_space_multiple_use` and `phase_space_sequential_times` for reference.

## 3. Update Callers

- [x] 3.1 Update `CTDICalculator._process_file_type()`: extract `N_scorer_active_histories` from one of the position CSV files. Pass it through to `_normalize_dose()` → `raw_absolute_dose_Gy()`.
- [x] 3.2 Update `PhantomDoseCalculator.calculate()`: extract `N_scorer_active_histories` from the phantom dose CSV. Pass it to the normalization pipeline. NOTE: current phantom DoseToMedium CSVs only emit `Sum` (no `Histories_with_Scorer_Active` column), so the helper returns `None` and normalization falls back to `total_histories` with a warning -- correct for direct-beam phantom sims but NOT for phase-space replay until the phantom scorer template is updated to emit the column.
- [x] 3.3 Update `src/services/calibration.py` `_normalize_dose()`: accept `n_scorer_active_histories` parameter (either passed in or extracted from CSV). Pass to `raw_absolute_dose_Gy()`.
- [x] 3.4 Update `src/services/benchmark_calculator.py` if it calls `raw_absolute_dose_Gy()`. (Actual file: `src/services/ctdi_benchmark.py`.)
- [x] 3.5 Update `calculate_phantom_dose.py` (CLI entry point) if it calls normalization functions directly. (It does not -- it routes through `PhantomDoseCalculator.calculate` → `normalize_dose`; no change needed.)
- [x] 3.6 Grep for any remaining callers of `raw_absolute_dose_Gy` or `compute_photons_per_mAs` and update them. (Updated `calculate_ctdiw._compute_raw_Gy` and `cross_validate_calibrations.cross_validate`.)

## 4. Tests

- [x] 4.1 Update `tests/unit/test_calibration.py`: update expected values for `raw_absolute_dose_Gy` and `compute_photons_per_mAs` with the new formula. Add tests for: (a) CTDI with sequential_times=36, (b) replay with M=5, (c) verify M and R cancel (independence). (In `test_calibration_service.py`; added `test_ctdi_direct_beam_sequential_times_36`, `test_phase_space_replay_M5`, `test_M_and_R_cancel_for_replay`.)
- [x] 4.2 Add test for `extract_scorer_histories()` — reads a sample CSV and returns the correct count. (In `test_calculate_ctdiw.py::TestExtractScorerHistories`.)
- [x] 4.3 Run full test suite (`pytest tests/ -v`) — fix any failures from the signature change. (531 passed.)
- [x] 4.4 Run ruff format + ruff check + mypy on all changed files. (ruff clean; mypy pre-existing yaml-stub/CalibrationEntry errors unrelated to this change.)

## 5. Recompute DCFs and Verify

- [x] 5.1 Recompute all 5 protocol DCFs (TLE) from existing CTDI calibration CSVs using the new normalization. Update `calibration.yaml`. (80FF=0.1073, 100FF=0.1191, 125FF=0.1239, 125HF=0.1629, 140HF=0.1812. DTW/DTM omitted (None) -- air-filled chambers give Count_in_Bin=0 for collision scorers; the literal 0 was changed to None after code review (0 silently zeroed phantom dose via lookup_dcf). Verified history-count independence: 80kV DCF stable across 5M/150M/500M direct-beam runs; all 5 reproduce measured CTDIw at 0.000% error.)
- [x] 5.2 Recompute pelvis DTM DCF. The water-hole CSVs are not in the repo, and the `water_chamber_enabled` parallel-world path segfaults in TOPAS (SIGSEGV during water parallel-world setup) AND would give zero under LayeredMassGeometry anyway (collision-based scorers can't register in LMG parallel worlds -- see AGENTS.md). Used the interim reference-effective-dose route instead: `DCF_dtm = E_ref / E_raw_MC = 4.2 / 152.13 = 0.02761`, computed with the new normalization from the direct-beam phantom run `phantom_runs/2026-07-02_05-19-13`. Produces 4.20 mSv effective dose (matches reference). Valid for direct-beam phantom sims only; a CTDI-derived DTM DCF requires a real-geometry water-chamber redesign (per-position sims).
- [x] 5.3 Recompute pelvis phantom effective dose with the new DCF. Direct-beam phantom (`phantom_runs/2026-07-02_05-19-13`) with the new normalization + interim DCF_dtm gives 4.20 mSv -- physically reasonable (not 100x off, the proposal's concern). NOTE: this is circular for the DTM path (DCF was derived from this same E_ref), so it validates the normalization pipeline and organ-dose magnitudes, not the DCF independently. Phase-space-replay phantom sims remain unsupported (phantom CSVs lack the Histories_with_Scorer_Active column).
- [x] 5.4 Verify: DCF from CTDI calibration produces physically reasonable organ doses (not 100x off). RESOLVED for the direct-beam path: TLE CTDI DCFs reproduce measured CTDIw (5.1); the DTM DCF gives a 4.20 mSv pelvis effective dose (5.3); organ doses are in plausible mGy ranges. The "100x off" failure mode from the proposal is fixed. Remaining gap: independent verification of replay-path phantom dose needs the phantom scorer template updated to emit Histories_with_Scorer_Active.
