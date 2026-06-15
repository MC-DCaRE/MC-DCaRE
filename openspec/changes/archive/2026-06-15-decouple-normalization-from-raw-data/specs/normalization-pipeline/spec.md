## ADDED Requirements

### Requirement: CTDICalculator returns un-normalized dose components

`CTDICalculator.calculate()` SHALL return raw Sum values from TOPAS CSVs without applying any dose calibration factor, norm_factor, or mAs scaling. The output SHALL include raw dose sums per position and per z-bin, along with the metadata needed for downstream normalization.

**Rationale**: Normalization is a post-processing concern. Raw data belongs in the calculator output so users can re-normalize with different parameters without re-running TOPAS.

#### Scenario: Calculate returns raw_sum and metadata
- **WHEN** `CTDICalculator.calculate()` is called on a valid runfolder
- **THEN** the returned dict SHALL contain `"scorer_type"`, `"is_primary"`, `"positions"` with raw Sum per position, and `"metadata"` with `total_histories` and `exposure_mAs`
- **AND** SHALL NOT contain a `"CTDI_w"` key (it moves to the normalization step)

#### Scenario: Backward compat with old metadata format
- **WHEN** a runfolder contains `head_calibration_factor.txt` instead of `simulation_metadata.yaml`
- **THEN** `CTDICalculator` SHALL emit a deprecation warning
- **AND** SHALL extract implied `total_histories` from the file header
- **AND** SHALL return the same un-normalized structure

### Requirement: Normalization service produces calibrated CTDI-w

A normalization function SHALL accept the raw output of `CTDICalculator.calculate()` and produce calibrated CTDI-w in Gy. The normalization SHALL apply three multiplicative factors in sequence: norm_factor, mAs scaling, and DCF.

**Normalization formula**:
```
norm_factor      = spectrum_fluence_photons_per_mAs / total_histories
raw_ctdi_w       = 1/3 × centre + 2/3 × average(peripheral)   [same formula, applied to raw Sum]
CTDI_w_raw_Gy    = raw_ctdi_w × norm_factor × exposure_mAs
CTDI_w_calibrated = CTDI_w_raw_Gy × DCF
```

#### Scenario: Normalize with automatic metadata and calibration lookup
- **WHEN** `normalize(raw_result, kV=100, fan_mode="Full Fan")` is called
- **THEN** it SHALL read `total_histories` and `exposure_mAs` from the raw result's metadata
- **AND** SHALL compute `norm_factor` from metadata
- **AND** SHALL look up DCF from `calibration.yaml` for `(kV=100, fan_mode="Full Fan")`
- **AND** SHALL return calibrated CTDI-w with `{ctdi_w_Gy, dcf_applied, dcf_source}`

#### Scenario: Normalize with DCF override
- **WHEN** `normalize(raw_result, kV=100, fan_mode="Full Fan", dcf_override=0.85)` is called
- **THEN** it SHALL use `0.85` instead of looking up calibration.yaml
- **AND** SHALL include `"dcf_source": "override"` in the output

#### Scenario: Normalize with target mAs rescaling
- **WHEN** `normalize(raw_result, kV=100, fan_mode="Full Fan", target_mAs=50)` is called
- **AND** the metadata `exposure_mAs` is `200`
- **THEN** the mAs ratio `50/200 = 0.25` SHALL be applied as a multiplicative factor
- **AND** SHALL include `"mAs_used": 50`, `"mAs_simulated": 200` in the output

### Requirement: CLI defaults to raw Gy (norm_factor × mAs, no DCF)

`calculate_ctdiw.py main <runfolder>` SHALL output CTDI-w in Gy with norm_factor and mAs applied but WITHOUT DCF. This produces physically meaningful but uncalibrated dose.

#### Scenario: Default output is raw Gy
- **WHEN** user runs `uv run python calculate_ctdiw.py main <runfolder>`
- **THEN** output SHALL include `CTDI_w_raw_Gy` (norm_factor × mAs applied, no DCF)
- **AND** SHALL state clearly that DCF has not been applied

#### Scenario: Calibrated output with --calibrated flag
- **WHEN** user runs `uv run python calculate_ctdiw.py main <runfolder> --calibrated`
- **THEN** output SHALL include `CTDI_w_calibrated_Gy` with DCF from calibration.yaml
- **AND** SHALL state which DCF was used and its `(kV, fan_mode)` key

#### Scenario: Explicit DCF with --dcf flag
- **WHEN** user runs `uv run python calculate_ctdiw.py main <runfolder> --dcf 0.87`
- **THEN** output SHALL use `0.87` as DCF
- **AND** SHALL NOT read from calibration.yaml

#### Scenario: mAs rescaling with --target-mAs
- **WHEN** user runs `uv run python calculate_ctdiw.py main <runfolder> --calibrated --target-mAs 50`
- **THEN** output SHALL scale to 50 mAs regardless of what was simulated
