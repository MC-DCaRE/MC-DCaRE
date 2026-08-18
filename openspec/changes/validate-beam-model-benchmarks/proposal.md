# Proposal: validate-beam-model-benchmarks

## Why

The bow-tie asset is validated (profile RMS 0.078, CAX HVL +0.43 FF) and the
TsCAD DCFs are calibrated, yet the effective-dose sweep retains a systematic
residual (-28..-57% vs manufacturer references; -26..-43% vs literature per-mAs
benchmarks). Two measured datasets in the RaySafe workbook remain unused, and
they target exactly the layers the residual lives in:

1. **Absolute free-in-air CAX kerma** (Sheet1): Head FF 59.01 uGy, Spotlight FF
   107.1 uGy, Pelvis HF 106.3 uGy, all at 40 mA x 40 ms (1.6 mAs); plus
   no-bow-tie CAX blocks (100 kV: 112.8 uGy, HVL 5.04, TF 4.7 mm Al; 80 kV:
   28.89 uGy, HVL 6.18). Everything validated so far was peak-normalised or
   DCF-anchored; absolute kerma exercises the full normalization chain
   (photons_per_mAs x mAs) independently.
2. **Bow-tie vs no-bow-tie CAX ratios**: measured Head transmission
   59.01/112.8 = 0.52 -- the real bow-tie's CAX thin spot still removes ~48%.
   Our no-bowtie HVL control (7.96) ~= TsCAD (7.80) suggests the STL CAX is
   nearly transparent. If confirmed by absolute kerma, the STL central
   thickness is wrong and is a candidate for the residual dose gap.

The Ti-filter state of the service-mode measurements must be treated as a
bracketing variable (profile blocks say "Ti Filter in"; the no-bow-tie blocks
do not state it), and "Coast"/"Outback" columns are second-machine (local
TrueBeam names) replicates for consistency only.

Literature: Abuhaimed & Martin 2023 (BMI phantom library) provides organ and
size-specific effective doses per 100 mAs for chest and pelvis (chest all-size
2.07, pelvis 1.19 mSv/100 mAs) against which our edose sweep can be compared
organ-by-organ (early check: our pelvis bladder 2.61 vs their 2.84 mGy/100 mAs
= -8%, but RBM 0.30 vs 1.13 = ~4x low -- the gap is organ-localisable).

## What Changes

- `data/measured/cax_kerma_anchors.yaml`: the extracted absolute anchors
  (value, mAs, kV, fan, bow-tie state, Ti state, source cell provenance,
  ambiguity notes incl. the 6.523-unit 120 kV block and the 80 kV HVL 6.18
  anomaly).
- `tools/compare_cax_kerma.py`: CAX-bin kerma from a validate_bowtie runfolder
  -> absolute uGy @ 1.6 mAs via the canonical normalization
  (`compute_photons_per_mAs` + `raw_absolute_dose_Gy`), compared to anchors;
  bow-tie/no-bow-tie transmission ratios MC-vs-measured.
- `configs/validate_kerma_*.yaml`: clinical-field runs (Head FF TsCAD; 100 kV
  no-BT Ti-in; 100 kV no-BT Ti-out via `bhf_thickness_mm: 0`; 80 kV no-BT;
  125 HF no-BT Ti-out).
- HVL(Z) wedge validation: energy-binned fluence per Z bin on the existing
  profile slab (`ZBins x EBins`), `tools/compute_hvl_map.py` folding each bin
  against the measured `hvl_mmAl` arrays (17 points/mode) -- a far sharper
  bow-tie discriminator than the CAX HVL.
- Gros 2025 Kair free-in-air per protocol (5 score-mode runs).
- Literature benchmark tables (Abuhaimed & Martin 2023 organ/per-100 mAs +
  follow-ups) in `docs/bowtie_validation/` and a data file for per-organ
  comparison against `edose_validation_runs` organ_doses.csv.

## Impact

New validation tooling + configs + docs only; no production behaviour change
unless the absolute-kerma test indicts the normalization chain or the STL CAX
thickness, in which case follow-up changes (BHF recalibration / STL re-center)
are proposed separately with the evidence.
