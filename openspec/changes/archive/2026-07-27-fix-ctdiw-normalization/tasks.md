## 1. Canonical normalization helper

- [x] 1.1 Add module-level `raw_absolute_dose_Gy(raw_sum, photons_per_mAs, total_histories, mAs_used)` to `src/services/calibration.py` — computes `(raw_sum / total_histories) * photons_per_mAs * mAs_used`, raises on `total_histories <= 0`
- [x] 1.2 Refactor `CalibrationService.normalize_dose` to use `raw_absolute_dose_Gy` (replace inline formula at line 268)
- [x] 1.3 Strengthen `compute_photons_per_mAs` to raise `ValueError` on `total_histories <= 0` instead of silently returning 0.0

## 2. Route stale sites through the canonical helper

- [x] 2.1 `calculate_ctdiw.py` `_compute_raw_Gy`: replace `raw_sum * photons_per_mAs * exposure_mAs` with `compute_photons_per_mAs(metadata)` + `raw_absolute_dose_Gy(...)`
- [x] 2.2 `cross_validate_calibrations.py:175`: route through `raw_absolute_dose_Gy` (divide by `total_histories`)
- [x] 2.3 `ctdi_benchmark.py`: replace the manual `photons_per_mAs` block + `norm_factor=1.0` fallback (lines 72-85) with `compute_photons_per_mAs(metadata)`; replace the divide/no-divide block (lines 99-104) with `raw_absolute_dose_Gy`

## 3. Tests

- [x] 3.1 Unit test `raw_absolute_dose_Gy` (division applied; raises on `total_histories <= 0`)
- [x] 3.2 Unit test `compute_photons_per_mAs` raises on missing/zero `total_histories`
- [x] 3.3 Unit test `calculate_ctdiw._compute_raw_Gy` divides by `total_histories` (off by ~histories before the fix)

## 4. Verify across protocols (re-derive from existing calibration runs)

- [x] 4.1 `calculate_ctdiw.py main` on calibration runfolders for 80FF, 100FF, 125FF, 125HF, 140FF, 140HF — confirm `CTDI_w_raw_Gy` is sane (mGy-to-Gy range, not ~1e8)
- [x] 4.2 `calculate_ctdiw.py benchmark` on the 5 calibrated protocols — confirm recomputed DCF matches `calibration.yaml` to within rounding
- [x] 4.3 `cross_validate_calibrations.py` — confirm `error_pct` is sane (not ~1e8%); report PASS/FAIL per protocol

## 5. Quality gates

- [x] 5.1 `ruff format` + `ruff check` clean on changed files
- [x] 5.2 `mypy src/` introduces no new errors
- [x] 5.3 `pytest tests/` — no new failures (pre-existing imaging-mode/ICRP145 failures unchanged)
