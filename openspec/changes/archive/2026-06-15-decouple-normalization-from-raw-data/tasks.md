## 1. CTDICalculator returns un-normalized output

- [x] 1.1 Refactor `CTDICalculator._process_file_type` to return `{raw_sum, positions, z_bin_data}` without multiplying by `calibration_factor`
- [x] 1.2 Add `metadata` field to `CTDICalculator.calculate()` return dict with `total_histories` and `exposure_mAs` read from `simulation_metadata.yaml`
- [x] 1.3 Add backward-compat fallback: read implied `total_histories` from `head_calibration_factor.txt` if `simulation_metadata.yaml` is missing, with deprecation warning
- [x] 1.4 Update `CTDICalculator.calculate()` return dict schema — no `CTDI_w` key at this level
- [x] 1.5 Update unit tests in `tests/unit/test_calculate_ctdiw.py` for new return format

## 2. CalibrationService as normalization authority

- [x] 2.1 Add `normalize(raw_result, kV, fan_mode, target_mAs=None, dcf_override=None)` method to `CalibrationService`
- [x] 2.2 Implement normalization formula: `CTDI_w = raw_ctdi × (spec_fluence / total_histories) × mAs × DCF`
- [x] 2.3 Implement DCF lookup from `calibration.yaml` keyed by `(kV, fan_mode)`
- [x] 2.4 Implement `dcf_override` parameter (bypass calibration.yaml lookup)
- [x] 2.5 Implement `target_mAs` rescaling (ratio-based)
- [x] 2.6 Return dict with full provenance: `{ctdi_w_calibrated_Gy, ctdi_w_raw_Gy, dcf_applied, dcf_source, mAs_used, mAs_simulated, norm_factor, scorer_type, is_primary}`
- [x] 2.7 Update unit tests in `tests/unit/test_calibration_service.py`

## 3. Update metadata schema in spectrum_generator.py

- [x] 3.1 Change `simulation_metadata.yaml` output: replace `norm_factor`, `dcf_used`, `calibration_factor` with `total_histories`, `exposure_mAs`, `spectrum_fluence_photons_per_mAs`, `dcf_hint` (optional)
- [x] 3.2 Keep `head_calibration_factor.txt` writer with deprecation comment (backward compat)
- [x] 3.3 Update metadata reader in CTDICalculator to handle both old and new schema
- [x] 3.4 Update tests in `tests/unit/test_spectrum_generator.py`

## 4. CLI updates for calculate_ctdiw.py

- [x] 4.1 `main` subcommand outputs raw Gy (norm_factor × mAs applied, no DCF) by default
- [x] 4.2 Add `--calibrated` flag: applies DCF from calibration.yaml
- [x] 4.3 Add `--dcf` flag: explicit DCF override
- [x] 4.4 Add `--target-mAs` flag: rescale to specified mAs
- [x] 4.5 All output includes clear labeling of which normalization steps were applied
- [x] 4.6 `benchmark` subcommand uses new normalization pipeline, writes to calibration.yaml

## 5. Deprecate dose_calibration_factor in config

- [x] 5.1 Emit deprecation warning during config validation when `dose_calibration_factor != 1.0`
- [x] 5.2 Write `dcf_hint` to metadata only (never applied automatically)
- [x] 5.3 Add deprecation note to `GeneralConfig.dose_calibration_factor` docstring

## 6. Integration tests and dry-run pipeline

- [x] 6.1 Update `tests/integration/test_dry_run_pipeline.py` for new metadata expectations
- [x] 6.2 Add integration test: `CTDICalculator.calculate()` + `CalibrationService.normalize()` end-to-end
- [x] 6.3 Add integration test: old format `head_calibration_factor.txt` fallback
