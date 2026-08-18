# Design: validate-beam-model-benchmarks

## Context

- Canonical normalization: `raw_absolute_Gy = (Sum / n_scorer_active_histories)
  x photons_per_mAs x mAs_used` (`src/services/calibration.py`, single source
  of truth). The new tool imports it; never re-derive.
- Measured anchors are per-frame at 40 mA x 40 ms = 1.6 mAs ("Dose uGy"
  column; verified consistent with the mGy/s column x 0.04 s to ~7%).
- The MC CAX bin is the profile-slab bin nearest the bow-tie thin axis
  (FF: Z=0; HF: Z~0, verified the HF field natively covers isocenter).
- Wide-field FF runs (user_field_x=32) stay valid for *ratios* (same field for
  both arms); absolute anchor comparisons use clinical-field configs.

## Decisions

1. **Ti state as a bracket**: run no-bow-tie variants with
   `bhf_thickness_mm: 0.89` (in) and `0.0` (out); the measured HVL/kerma pair
   identifies which state matches. The 100 kV no-BT anchor (HVL 5.04, TF 4.7)
   is the cleanest discriminator: our Ti-in no-BT control already reads HVL
   7.96, far harder than 5.04 -- suggesting either Ti-out measurement or an
   over-hard base filtration (SpekPy inherent Al).
2. **Transmission ratio first**: the bow-tie/no-bow-tie CAX kerma ratio is
   field- and normalization-independent (common-mode cancellation), so it is
   the most robust new test. Measured 0.52 (Head) vs MC ~? decides whether the
   STL CAX thickness is credible before any absolute-chain debugging.
3. **HVL(Z)**: extend the `BowtieProfile` scorer to `ZBins=40 x EBins=100`
   (0.5 cm x 1 keV) -- TOPAS supports energy binning on spatially binned
   scorers (Histograms.txt example). Fold each Z bin with the existing
   `compute_hvl_mm_al`. Keep the 1-D profile run config unchanged in
   production (new config for the map) so the committed Phase-1 artefacts stay
   reproducible.
4. **Per-100 mAs literature comparison**: normalize our edose results
   (E and organ doses) per 100 mAs; compare to Abuhaimed & Martin 2023
   Tables 2-3 (chest/pelvis organ + SSED). Organ-level residuals localise the
   systematic gap (bladder matches, RBM ~4x low) and direct the next change.

## Risks / Data-quality caveats

- The 120 kV no-bow-tie block reads "Dose 6.523" in unknown units -- excluded
  from anchors (flagged).
- 80 kV no-BT HVL 6.18 > 100 kV no-BT HVL 5.04 is physically inconsistent for
  identical filtration -- treat the 80 kV HVL as suspect; kerma 28.89 uGy is
  consistent via its rate column and is used.
- The Pelvis HF measured reference is "interpolated from meas" in the workbook.
- Second-machine (Coast) columns are replicates, not independent anchors.

## Follow-up papers (confirmation chain)

Abuhaimed & Martin 2018 (JRP 38, 61-80) organ/E; Martin & Abuhaimed 2022
(JRP 42, 031512) stature/beam-width; Martin et al 2016 (JRP 36, 215)
CTDI->organ (our DCF-transfer premise); Abuhaimed et al 2015/2014 (PMB)
CBCT dosimetry MC/measurement; Ding et al 2018 (AAPM TG-180); Alaei & Spezi
2015 review; Marchant & Joshi 2017 (Elekta XVI range); Khan et al 2022,
Ordonez-Sanz et al 2021 (protocol optimisation); Gros et al 2025
(arXiv:2502.01509) Kair/CBDIw.
