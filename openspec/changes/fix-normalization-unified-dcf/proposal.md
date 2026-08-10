## Why

The dose normalization pipeline produces inconsistent absolute dose values for direct beam source simulations (CTDI calibration) vs phase space replay simulations (phantom organ dose). This prevents the CTDI-derived Dose Calibration Factor (DCF) from transferring to phantom organ dose — the DCF from CTDI measurements cannot be used to calibrate phantom effective dose without a separate reference-derived correction. The root cause is that `compute_photons_per_mAs()` uses `total_histories` (which varies by simulation type) instead of the scoring run's `N_scoring` (a fixed constant), causing the normalization to silently break when the actual simulation histories differ from the scoring run histories.

## What Changes

- **Fix `compute_photons_per_mAs()`**: Use `N_scoring` (from scoring metadata `total_histories`) as the constant scaling factor, not the current simulation's `total_histories`. This makes `photons_per_mAs` a property of the beam model (constant across all simulations using the same scoring run), not of the current run configuration.

- **Fix `raw_absolute_dose_Gy()`**: Accept `N_scorer_active_histories` (the actual number of scorer-accumulated histories from the TOPAS CSV `Histories_with_Scorer_Active` column) instead of `total_histories` from metadata. This auto-scales for direct beam (R × histories_per_run), phase space replay (N_phsp × M × R), and any other source type.

- **Fix `_write_replay_metadata()`**: Stop dividing `spectrum_fluence` by M × R. The division now happens naturally through `N_scorer_active_histories` in the normalization formula. The sf stays at the scoring-run value for all downstream runs.

- **Update CTDICalculator**: Read `Histories_with_Scorer_Active` from the CSV and pass it through as `N_scorer_active_histories` to the normalization.

- **Update PhantomDoseCalculator**: Same — read scorer histories from the phantom dose CSV and use it for normalization.

- **BREAKING**: The `total_histories` parameter in `raw_absolute_dose_Gy()` is renamed to `n_scorer_active_histories`. All callers must be updated.

## Capabilities

### New Capabilities

### Modified Capabilities

- `dose-normalization`: The normalization formula changes from `(raw_sum / total_histories) × ppm × mAs` where `ppm = sf × total_histories / mAs` (which cancels to `raw_sum × sf`) to `(raw_sum / n_scorer_active_histories) × ppm × mAs` where `ppm = sf × N_scoring / mAs` (which correctly gives `raw_sum × sf × N_scoring / n_scorer_active_histories`). This ensures the DCF transfers between CTDI calibration (direct beam) and phantom dose (phase space replay).

## Impact

- `src/services/calibration.py`: `compute_photons_per_mAs()`, `raw_absolute_dose_Gy()` signature change
- `src/orchestrator.py`: `_write_replay_metadata()` — remove sf division by M×R
- `src/services/ctdi_calculator.py`: Pass scorer-active histories from CSV
- `src/services/phantom_dose_calculator.py`: Pass scorer-active histories from CSV
- `src/services/benchmark_calculator.py`: Update if it calls `raw_absolute_dose_Gy()`
- `calculate_phantom_dose.py` (CLI entry point): Update caller
- All existing DCF values in `calibration.yaml` will change (must be recomputed)
- Tests: `test_calibration.py` and any test using `raw_absolute_dose_Gy`
