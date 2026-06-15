# Spec: Calibration Data Model

## Capability

Persist and retrieve per-machine dose calibration factors keyed by `(kV, fan_mode)`.

## ADDED Requirements

### CAL-DATA-001: calibration.yaml schema
- File location: project root
- Contains: `machine` (str), `date_calibrated` (ISO date str), `calibrations` (list of entries)
- Each entry has: `kV` (int), `fan_mode` (str), `reference_mAs` (float), `measured_ctdi_w_mGy` (float or null), `dcf` (float or null)
- Entries keyed by `(kV, fan_mode)` — no duplicates allowed

### CAL-DATA-002: Data model
- `CalibrationEntry` frozen dataclass in `src/models/calibration.py`
- `MachineCalibration` frozen dataclass in `src/models/calibration.py`
- `from_yaml(path)` classmethod on `MachineCalibration` — reads file, validates no duplicate keys
- `to_yaml(path)` method — writes back to file preserving structure

### CAL-DATA-003: Pre-seeded entries
- Initial `calibration.yaml` contains all 6 unique `(kV, fan_mode)` pairs with `dcf: null`
- Pairs: (80, Full Fan), (100, Full Fan), (125, Full Fan), (125, Half Fan), (140, Full Fan), (140, Half Fan)

### CAL-DATA-004: DCF write-back
- `compute_dcf(kV, fan_mode, simulated_ctdi_w_Gy, measured_ctdi_w_mGy, force=False)` finds entry by `(kV, fan_mode)`, fills `dcf` and `measured_ctdi_w_mGy`, writes file
- Raises `ValueError` if no matching entry found
- Raises `ValueError` if entry already has a non-null `dcf` and `force` is False (prevents accidental overwrite; `force=True` allows re-calibration)

#### Scenario: compute DCF for uncalibrated entry
- Given `calibration.yaml` with entry `(120, "Full Fan", dcf: null)`
- When `compute_dcf(120, "Full Fan", 0.0437, 45.2)`
- Then entry becomes `(120, "Full Fan", dcf: 1.034, measured_ctdi_w_mGy: 45.2)`
- And `calibration.yaml` is rewritten to disk

#### Scenario: overwrite existing DCF without force
- Given entry `(120, "Full Fan", dcf: 1.034)`
- When `compute_dcf(120, "Full Fan", 0.0437, 46.0)`
- Then raises `ValueError`

#### Scenario: overwrite existing DCF with force
- Given entry `(120, "Full Fan", dcf: 1.034)`
- When `compute_dcf(120, "Full Fan", 0.0437, 46.0, force=True)`
- Then entry becomes `(120, "Full Fan", dcf: 1.053, measured_ctdi_w_mGy: 46.0)`
