# beam-model-validation Specification

## ADDED Requirements

### Requirement: absolute CAX air kerma comparable to measurement

The system SHALL convert the validate_bowtie CAX-bin kerma to absolute
free-in-air kerma (uGy at a stated mAs) using the canonical normalization
(`compute_photons_per_mAs` + `raw_absolute_dose_Gy`), and compare it to the
extracted RaySafe anchors with explicit bow-tie and Ti-filter states.

#### Scenario: Head FF absolute kerma
- **WHEN** a clinical-field TsCAD Head FF run is compared at 1.6 mAs
- **THEN** the MC CAX kerma is reported against the measured 59.01 uGy anchor
  with the ratio and the run's Ti state recorded

#### Scenario: bow-tie transmission ratio
- **WHEN** bow-tie and no-bow-tie runs share an identical field
- **THEN** the MC CAX transmission ratio is reported against the measured 0.52
  (Head) so STL central thickness can be judged free of normalization
  common-mode error

### Requirement: Ti-filter state bracketing for no-bow-tie anchors

No-bow-tie comparisons SHALL bracket `bhf_thickness_mm` in {0.89, 0.0} until
the measured no-bow-tie HVL/kerma pair identifies the measurement's filter
state; the identification SHALL be recorded with the anchors.

#### Scenario: 100 kV no-bow-tie discrimination
- **WHEN** Ti-in and Ti-out no-bow-tie HVLs are compared to the measured 5.04
  (TF 4.7)
- **THEN** the matching state is recorded and the non-matching residual is
  attributed (base filtration model vs filter state)

### Requirement: measured anchors stored with provenance

All extracted anchors SHALL live in `data/measured/cax_kerma_anchors.yaml`
with value, mAs, kV, fan, bow-tie/Ti state, workbook cell provenance and
ambiguity flags; ambiguous blocks SHALL be excluded from pass/fail.

### Requirement: HVL(Z) wedge map comparable to measurement

The system SHALL score an energy-resolved Z profile (ZBins x EBins) and fold
each Z bin to HVL(Z), compared point-wise to the measured per-mode `hvl_mmAl`
arrays.

### Requirement: literature per-100 mAs benchmark comparison

Effective-dose and organ-dose results SHALL be comparable per 100 mAs against
published benchmarks (Abuhaimed & Martin 2023 Tables 2-3 minimum), with
organ-level residuals tabulated to localise systematic gaps.
