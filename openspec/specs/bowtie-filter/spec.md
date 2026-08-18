# bowtie-filter Specification

## Purpose

Governs the bow-tie filter asset: qualification against measurement, the
validation tooling, and provenance of dose results. The TsCAD mesh bow-tie was
qualified against the RaySafe Oct-2023 cross-plane profile on 2026-08-14
(RMS 0.078 vs 0.583 for the legacy CSG) and adopted as the default
(`imaging.legacy_bowtie=False`).

## Requirements

### Requirement: Bow-tie qualified against measurement before default adoption

A bow-tie model SHALL NOT be the production default until its cross-plane
air-kerma profile and central-axis HVL have been compared against the measured
RaySafe reference and found to agree. The TsCAD mesh bow-tie
(`bowtie_ff.txt` / `bowtie_hf.txt`) was qualified 2026-08-14 (RMS 0.078);
the legacy CSG bow-tie (`fullfan.txt` / `halffan.txt`) failed qualification
(RMS 0.583, near-flat cross-plane profile) and is retained only as a fallback
(`legacy_bowtie=True`).

#### Scenario: bow-tie matches measured profile
- **WHEN** a bow-tie's cross-plane profile RMS misfit vs the RaySafe Oct-2023
  data is within tolerance AND the CAX HVL agrees to within ~0.5 mmAl
- **THEN** the bow-tie is qualified for adoption and may be made the default
  after DCF re-calibration

#### Scenario: bow-tie over-attenuates vs measured
- **WHEN** a bow-tie's profile/HVL does not match measurement
- **THEN** the asset is diagnosed (wrong STL / source-to-bowtie distance /
  material) and either corrected or the other bow-tie is retained as the
  default

### Requirement: Cross-plane profile + HVL comparable to measurement

The system SHALL be able to produce, for any bow-tie configuration, a scored
cross-plane dose profile and CAX HVL at isocenter that can be compared to the
measured RaySafe data via `src/services/bowtie_validator.py`. The `validate_bowtie`
scorer (gated in `ctdi_phsp_score.j2`, a TrackLengthEstimator on a thin air
slab, Z-binned, wide field) and `PhaseSpaceAnalyzer.compute_hvl_mm_al`
provide the MC side; the RaySafe workbook provides the measured side.

#### Scenario: profile comparison artefact
- **WHEN** `tools/validate_bowtie.py` is run with a scored MC profile and the
  RaySafe workbook
- **THEN** it emits a per-position comparison CSV (measured vs MC, normalised)
  and an RMS misfit, plus a matplotlib PNG

### Requirement: Effective dose reported with bow-tie provenance

Effective-dose outputs SHALL record which bow-tie produced them, so results
from an unqualified or newly-changed bow-tie are not mistaken for established
production values.

#### Scenario: bow-tie recorded in run metadata
- **WHEN** a phantom effective-dose run uses `legacy_bowtie=False`
- **THEN** the run metadata records `legacy_bowtie: false` (the TsCAD asset)
  so post-processing can identify the result as STL-based
