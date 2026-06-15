## ADDED Requirements

### Requirement: CalibrationService is the single entry point for DCF

`CalibrationService` SHALL be the only component that applies DCF to simulation results. No other code path MAY multiply by DCF.

**Rationale**: The current system has two DCF multiplication points (`dcf_used` in config and `CalibrationService.apply()`), creating a double-counting risk. Making `CalibrationService` the single authority eliminates this.

#### Scenario: CalibrationService.normalize() is the only DCF path
- **WHEN** a user calls `normalize()` on `CalibrationService`
- **THEN** the DCF SHALL come exclusively from `calibration.yaml` (or an explicit override parameter)
- **AND** no other function or service SHALL multiply by DCF

#### Scenario: Trying to set dcf_used in config emits deprecation warning
- **WHEN** `dose_calibration_factor` in config YAML is not `1.0`
- **THEN** a deprecation warning SHALL be emitted during config validation
- **AND** the value SHALL be written to metadata as `dcf_hint` only (not applied)

### Requirement: CalibrationService exposes a normalize() method

`CalibrationService` SHALL expose a `normalize()` method that accepts raw CTDICalculator output, a `(kV, fan_mode)` key, optional `target_mAs`, and optional `dcf_override`, and returns calibrated CTDI-w in Gy.

```
CalibrationService.normalize(
    raw_result: Dict,       # from CTDICalculator.calculate()
    kV: int,                 # e.g. 100
    fan_mode: str,           # "Full Fan" or "Half Fan"
    target_mAs: float = None,  # optional rescaling
    dcf_override: float = None,  # optional DCF override
) -> Dict
```

#### Scenario: normalize() returns calibrated dict with full provenance
- **WHEN** `normalize()` returns
- **THEN** the returned dict SHALL contain:
  - `ctdi_w_calibrated_Gy`: float
  - `ctdi_w_raw_Gy`: float (norm_factor × mAs only)
  - `dcf_applied`: float or None
  - `dcf_source`: "calibration.yaml" or "override" or None
  - `mAs_used`: float
  - `mAs_simulated`: float
  - `norm_factor`: float
  - `scorer_type`: str
  - `is_primary`: bool

### Requirement: calibration.yaml remains the persistent DCF store

No schema changes to `MachineCalibration` / `CalibrationEntry`. The existing keying on `(kV, fan_mode)` is sufficient.

#### Scenario: Benchmark writes DCF to calibration.yaml
- **WHEN** `calculate_ctdiw.py benchmark <runfolder> -r <measured_mSv>` runs
- **THEN** it SHALL compute DCF = measured_Gy / simulated_Gy (using raw Gy from normalizer)
- **AND** SHALL write the DCF to `calibration.yaml` under the matching `(kV, fan_mode)` entry
- **AND** SHALL report the DCF value and PASS/FAIL status

#### Scenario: Calibration lookup by (kV, fan_mode)
- **WHEN** `lookup_dcf(kV=120, fan_mode="Half Fan")` is called
- **AND** an entry exists
- **THEN** the corresponding DCF SHALL be returned
- **WHEN** no entry exists
- **THEN** `None` SHALL be returned (no implicit default of 1.0)
