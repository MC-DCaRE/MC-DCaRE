## Why

The CTDI-w post-processing pipeline has two divergent normalization
formulas. The canonical path (`CalibrationService.normalize_dose`,
`src/services/calibration.py:268`) correctly divides the TOPAS Sum by
`total_histories` before scaling:

    raw_absolute_Gy = (raw_sum / total_histories) * photons_per_mAs * mAs

Two CLI scripts were left stale by the `decouple-normalization-from-raw-data`
refactor and omit that division, so their output is off by a factor of
`total_histories` (typically ~1e8 to ~1e9):

- `calculate_ctdiw.py:39` `_compute_raw_Gy` — the `main` command's displayed
  `CTDI_w_raw_Gy`. The archived re-run log records `4.193768e+08` for an
  80 kV run (should be ~0.8 Gy).
- `cross_validate_calibrations.py:175` — the cross-validation raw dose.

The `benchmark` path (`ctdi_benchmark.py`) divides correctly, so the DCFs
committed in `calibration.yaml` are themselves correct — only the `main`
raw display and the cross-validation report are wrong.

Two related robustness gaps compound this: `compute_photons_per_mAs`
silently returns `0.0` when `total_histories` is missing (rather than
raising), and `ctdi_benchmark.py:80-85` falls back to `norm_factor=1.0`
when no normalization source is present, producing a meaningless result.

## What Changes

- Add one canonical raw-dose helper (`raw_absolute_dose_Gy`) in
  `src/services/calibration.py`; route `normalize_dose`, `_compute_raw_Gy`,
  `cross_validate_calibrations`, and `BenchmarkCalculator.compare` through it
  so there is a single normalization formula.
- `compute_photons_per_mAs` raises on non-positive `total_histories` instead
  of silently returning 0.0.
- Remove the `norm_factor=1.0` silent fallback in `ctdi_benchmark.py` (now
  goes through `compute_photons_per_mAs`, which raises).
- Re-derive DCFs from the existing calibration runfolders and confirm
  `main`, `benchmark`, and `cross_validate` produce sane values for every
  protocol in `calibration.yaml`.

## Capabilities

### Modified Capabilities
- `ctdi-normalization`: single canonical raw-dose normalization across all
  post-processing entry points; loud failure on missing metadata.
