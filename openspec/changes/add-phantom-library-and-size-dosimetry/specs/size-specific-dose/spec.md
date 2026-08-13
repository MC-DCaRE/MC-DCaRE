# size-specific-dose Specification

## Purpose

Reports per-protocol effective dose as a function of patient height/weight by
running a representative body-size percentile subset (10th/50th/90th) of the
voxelized phantom library, instead of a single reference-phantom value with an
ad-hoc stature correction. Grounded in the MRCP deformability libraries (Choi
2020 adult; Kim 2024 paediatric) and the size-spread literature (Martin 2022;
Abuhaimed 2023).

## ADDED Requirements

### Requirement: Percentile subset drives the size curve

For a protocol run in size-specific mode, the system SHALL compute effective
dose for the 10th, 50th, and 90th body-size percentile phantoms of the selected
age/sex. The reporting layer SHALL return E at each percentile plus a
height/weight interpolation.

#### Scenario: Three-percentile run
- **WHEN** a protocol is run with size-specific mode enabled for adult male
- **THEN** E is computed for MRCP_AM, MRCP_AM_p10, and MRCP_AM_p90

### Requirement: Reference provenance recorded

`calibration.yaml.effective_dose_references` SHALL record, per protocol, the
phantom (name incl. age/sex/percentile) and reference source that produced each
reference value, not just a flat mSv number.

#### Scenario: Reference carries phantom identity
- **WHEN** the validation comparison loads a reference
- **THEN** the entry includes `phantom` (e.g. `MRCP_AM`) and `reference` fields
  alongside the mSv value

### Requirement: Size spread validated against literature trends

The 10th-vs-90th percentile E spread SHALL be checked for consistency with
published size-sensitivity (Martin 2022: 10 kg lighter -> +10-14% E; thin-vs-obese
pelvis ~2x). A divergence > 2x from the literature trend SHALL raise a warning.

#### Scenario: Spread within expected range
- **WHEN** adult pelvis E is computed at p10 and p90
- **THEN** the p10/p90 ratio is reported and checked against the Martin 2022 band
