# Spec: Calibration Service

## Capability

Compute, lookup, and apply dose calibration factors to CTDI simulation results.

## ADDED Requirements

### CAL-SVC-001: DCF computation
- `compute_dcf(kV, fan_mode, simulated_ctdi_w_Gy, measured_ctdi_w_mGy) -> float`
- Formula: `dcf = (measured_ctdi_w_mGy * 1e-3) / simulated_ctdi_w_Gy`
- Writes result back to calibration.yaml (see CAL-DATA-004)
- Returns the computed DCF

### CAL-SVC-002: DCF lookup
- `lookup_dcf(kV, fan_mode) -> Optional[float]`
- Returns DCF if entry exists and `dcf` is not null
- Returns `None` if entry not found or not yet calibrated
- Does not raise on missing — returns None

### CAL-SVC-003: Apply calibration
- `apply(runfolder, kV, fan_mode, target_mAs=None) -> List[Dict]`
- Pipeline:
  1. Read `simulation_metadata.yaml` from runfolder to get `sim_mAs`
  2. Run `CTDICalculator(runfolder).calculate()` — returns dose at `sim_mAs` with `dcf_used=1.0`
  3. Lookup `DCF(kV, fan_mode)` — raises if not calibrated (None DCF)
  4. For each result: `CTDI_w_calibrated = CTDI_w * dcf`
  5. If `target_mAs` provided and differs from `sim_mAs`: multiply by `target_mAs / sim_mAs`
- Returns list of dicts with keys: `FileType`, `PeripheralDoseAverage`, `CenterDose`, `CTDI_w`, `CalibrationFactor`, `Timestamp` (from CTDICalculator) plus `CTDI_w_calibrated` (float), `dcf_applied` (float), `mAs_ratio` (float, 1.0 if no scaling)
- **Note**: `apply()` requires runfolders produced after this change (containing `simulation_metadata.yaml`). Backward compatibility with old runfolders is scoped to CTDICalculator only (CAL-META-003).

#### Scenario: apply calibration at simulation mAs
- Given runfolder with `simulation_metadata.yaml` (`mAs: 100`), CTDICalculator returns `CTDI_w: 0.0437`
- And `calibration.yaml` has `(120, "Full Fan", dcf: 1.034)`
- When `apply(runfolder, 120, "Full Fan")`
- Then returns `CTDI_w_calibrated: 0.0452`, `dcf_applied: 1.034`, `mAs_ratio: 1.0`

#### Scenario: apply calibration at different mAs
- Given runfolder with `mAs: 100`, CTDI_w: 0.0437, dcf: 1.034
- When `apply(runfolder, 120, "Full Fan", target_mAs=200)`
- Then returns `CTDI_w_calibrated: 0.0904`, `dcf_applied: 1.034`, `mAs_ratio: 2.0`

#### Scenario: uncalibrated entry
- Given `calibration.yaml` has `(80, "Full Fan", dcf: null)`
- When `apply(runfolder, 80, "Full Fan")`
- Then raises `ValueError`

### CAL-SVC-004: Validation
- `apply()` raises `FileNotFoundError` if `simulation_metadata.yaml` missing from runfolder
- `apply()` raises `ValueError` if DCF is None for the requested `(kV, fan_mode)`
- `apply()` raises `ValueError` if CTDICalculator returns empty results
