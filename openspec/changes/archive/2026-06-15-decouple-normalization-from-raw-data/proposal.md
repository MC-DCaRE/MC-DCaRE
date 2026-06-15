## Why

The normalization pipeline has two DCF multiplication points — one baked into simulation metadata (`dcf_used` in config YAML → `calibration_factor` in `simulation_metadata.yaml`) and one applied post-hoc via `CalibrationService.apply()`. This dual path makes it easy to double-count DCF, obscures the provenance of "raw" vs "calibrated" results, and ties normalization factors to individual runfolders instead of the beam quality they describe. A DCF is a property of `(kV, fan_mode)`, not of a particular simulation run, but the current system embeds it per-run.

## What Changes

- **BREAKING**: Remove `dcf_used` from `simulation_metadata.yaml` and `head_calibration_factor.txt`. Raw simulation output remains un-normalized. The CSV files already store raw Sum values — leave them raw.
- **BREAKING**: Store `total_histories`, `exposure_mAs`, and `spectrum_fluence` as separate metadata fields, not combined into a `norm_factor * mAs * dcf_used` product.
- **Single DCF authority**: DCF lives in `calibration.yaml` keyed by `(kV, fan_mode)`. All normalization happens in post-processing via `CalibrationService`, which is the only code that multiplies by DCF.
- **CTDICalculator refactor**: Stops applying the combined calibration_factor internally. Instead returns dose components (raw_sum, histories, mAs) as separate fields, letting downstream consumers choose how to normalize.
- **CLI updates**: `calculate_ctdiw.py main` and `calculate_ctdiw.py benchmark` accept an explicit `--dcf` flag or lookup from `calibration.yaml`.

## Capabilities

### New Capabilities
- `normalization-pipeline`: Post-processing normalization that applies norm_factor, mAs scaling, and DCF as separate, explicit steps. Accepts raw TOPAS Sum output and produces calibrated CTDI-w.
- `calibration-authority`: Single-source DCF lookup keyed by `(kV, fan_mode)` in `calibration.yaml`. `CalibrationService` is the only entry point for DCF application. Removes per-run DCF embedding.

### Modified Capabilities

None. No existing specs to modify.

## Impact

- `src/services/ctdi_calculator.py` — `CTDICalculator` no longer applies calibration_factor internally. Returns un-normalized dose components + metadata. May break callers that depend on calibrated CTDI_w directly.
- `src/services/calibration.py` — `CalibrationService.apply()` becomes the primary normalization pipeline. Extends to accept raw CTDICalculator output and apply all normalization steps (norm_factor, mAs, DCF).
- `src/spectrum_generator.py` — `simulation_metadata.yaml` schema changes: replaces combined `norm_factor` with explicit `total_histories`, `exposure_mAs`, `spectrum_fluence`. Removes `dcf_used`.
- `src/config.py` — Consider deprecating `dose_calibration_factor` from `GeneralConfig`. If kept, it becomes a "hint" for post-processing only.
- `calculate_ctdiw.py` — CLI changes: `main` subcommand accepts `--dcf` flag or auto-lookup. `benchmark` subcommand writes to `calibration.yaml` as always.
- `tests/unit/test_ctdi_calculator.py` — Update for new return format.
- `tests/integration/test_dry_run_pipeline.py` — Update metadata expectations.

