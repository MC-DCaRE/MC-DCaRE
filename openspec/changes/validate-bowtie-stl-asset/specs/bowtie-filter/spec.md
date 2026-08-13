# bowtie-filter Specification

## ADDED Requirements

### Requirement: TsCAD bow-tie qualified against measurement before default adoption

The TsCAD mesh bow-tie (`bowtie_ff.txt` / `bowtie_hf.txt`) SHALL NOT be enabled
as the default (`imaging.legacy_bowtie=False`) until its cross-plane air-kerma
profile and central-axis HVL have been compared against the measured RaySafe
reference and found to agree. The legacy CSG bow-tie (`fullfan.txt` /
`halffan.txt`) SHALL remain the default (`legacy_bowtie=True`) until the STL is
qualified.

#### Scenario: TsCAD matches measured profile
- **WHEN** the TsCAD cross-plane profile RMS misfit vs the RaySafe Oct-2023
  data is within tolerance AND the CAX HVL agrees to within ~0.5 mmAl
- **THEN** the TsCAD bow-tie is qualified for adoption and `legacy_bowtie` may
  be flipped to False after DCF re-calibration

#### Scenario: TsCAD over-attenuates vs measured
- **WHEN** the TsCAD profile/HVL does not match measurement (e.g. over-attenuates,
  consistent with the ~40% low effective dose observed 2026-08-14)
- **THEN** the asset is diagnosed (wrong STL / source-to-bowtie distance /
  material) and either corrected or the legacy CSG bow-tie is retained as the
  default

### Requirement: Cross-plane profile + HVL comparable to measurement

The system SHALL be able to produce, for any bow-tie configuration, a scored
cross-plane dose profile and CAX HVL at isocenter that can be compared to the
measured RaySafe data via `src/services/bowtie_validator.py`. The `validate_bowtie`
scorer (gated in `ctdi_phsp_score.j2`) and `PhaseSpaceAnalyzer.compute_hvl_mm_al`
provide the MC side; the RaySafe workbook provides the measured side.

#### Scenario: profile comparison artefact
- **WHEN** `tools/validate_bowtie.py` is run with a scored MC profile and the
  RaySafe workbook
- **THEN** it emits a per-position comparison CSV (measured vs MC, normalised)
  and an RMS misfit, plus a matplotlib PNG

### Requirement: Effective dose reported with bow-tie provenance

When the TsCAD bow-tie is used, the effective-dose output SHALL record which
bow-tie produced it (so a 3.x mSv result is not mistaken for a calibrated
production value until the asset is qualified).

#### Scenario: bow-tie recorded in run metadata
- **WHEN** a phantom effective-dose run uses `legacy_bowtie=False`
- **THEN** the run metadata records `legacy_bowtie: false` (the TsCAD asset) so
  post-processing can flag the result as STL-based / pending qualification
