# MC-DCaRE Validation Results — 2026-08-13

## Overview

Effective dose comparison for 20 unique CBCT protocols (CBCT Anticlockwise
direction) on the ICRP 145 MRCP-AM adult male voxelized phantom (5mm resolution).

## Method

### Phase space scoring
Each protocol was scored individually through the TrueBeam beam model
(collimators, bowtie filter, beam hardening) at 5M histories per angle, capturing
the full beam model including the protocol-specific collimator field. The
phase space scoring plane is at Y=-75cm.

### Phantom replay
Each phase space was replayed into the voxelized MRCP-AM phantom using TOPAS
with `PhaseSpaceMultipleUse=2` and `NumberOfSequentialTimes=36` (10-degree
steps, 360-degree rotation). Both TrackLengthEstimator (TLE) and DoseToMedium
(DTM) scorers were used.

### Isocenter placement
Isocenter Z was set from actual MRCP-AM organ centroids:

| Region | Isocenter Z (mm) | Protocols |
|---|---|---|
| Pelvis | 0 | Pelvis, Pelvis Large, Pelvis Spotlight |
| Abdomen | 200 | Abdomen, Abdo Spotlight, Spotlight, Image Gently, Paediatric Body |
| Spine | 300 | SBRT Spine |
| Thorax | 460 | Thorax, 4D Thorax, Breast 360, Short Thorax, 4D Spotlight, Thorax Spotlight |
| Neck | 600 | Head and Shoulders |
| Head | 795 | Head, Head SRS, Paediatric Head |
| Extremity | -200 | Extremity Spotlight |

### Normalization
- `n_scorer_active = N_scoring × R × M` (= 5M × 36 × 2 = 360M for all protocols)
- `photons_per_mAs = spectrum_fluence × N_scoring / exposure_mAs`
- `raw_absolute_Gy = (raw_sum / n_scorer_active) × photons_per_mAs × mAs`
- Effective dose = `raw_absolute_Gy × DCF × 1000` with ICRP 103 tissue weighting
- DCF from CTDI phantom calibration (per kV/fan combination)

### DCF calibration entries

| kV | Fan | DCF (TLE) | Source |
|---|---|---|---|
| 80 | Full Fan | 0.10720 | Measured (Image Gently) |
| 100 | Full Fan | 0.11837 | Measured (Head) |
| 100 | Half Fan | 0.15850 | Interpolated |
| 125 | Full Fan | 0.12002 | Measured (Pelvis Spotlight) |
| 125 | Half Fan | 0.16070 | Measured (Pelvis) |
| 140 | Half Fan | 0.17572 | Measured (Pelvis Large) |

## Results

See `effective_dose_comparison_2026-08-13.csv` for the full data table.

### Summary

| Metric | Count |
|---|---|
| Protocols with reference E | 14 |
| Within ±3 mSv | 14/14 |
| Within ±50% | 5/14 |

### Best matches

| Protocol | E_MC (mSv) | E_ref (mSv) | Diff |
|---|---|---|---|
| Thorax | 1.30 | 1.3 | 0% |
| 4D Thorax | 3.20 | 3.3 | -3% |
| 4D Spotlight | 1.09 | 1.6 | -32% |
| SBRT Spine | 0.99 | 1.7 | -42% |
| Thorax Spotlight | 0.44 | 0.7 | -37% |

### Known issues

1. **Pelvis/abdomen underestimate** (-54% to -62%): The `n_scorer_active =
   N_scoring × R × M` normalization approximation works well for thoracic
   isocenters but systematically underestimates at pelvic/abdominal isocenters.
   This may be due to the phase-space replay missing scatter contributions
   that are captured in the direct-beam CTDI calibration.

2. **Head protocols underestimate** (-84% to -88%): The head isocenter (Z=795mm)
   is at the superior extreme of the phantom. The brain's low density and small
   irradiated volume contribute to low TLE scores.

3. **Small-field Full Fan protocols underestimate** (Pelvis Spotlight -65%,
   Abdo Spotlight -56%): The Full Fan (SFOV) collimator delivers a smaller
   beam than the Half Fan (LFOV) used for the calibration DCF. The DCF
   transfer from CTDI to phantom may not fully account for field-size
   differences.

4. **Breast 360 (+115%) and Head and Shoulders (+140%)**: These overestimates
   may indicate questionable reference values. Breast 360 uses the same beam
   as Thorax but at 89.5 mAs (vs 268.5 mAs); the 0.2 mSv reference seems low
   for a 360-degree CBCT. Head and Shoulders at 125 kV/268.5 mAs delivering
   only 0.3 mSv also seems low.

## Selection-bias fix (PhantomDoseCalculator)

The PhantomDoseCalculator previously skipped voxels with `dose <= 0`, which
exclusively removed DTM voxels (collision-based; many zeros in low-fluence
organs) while keeping all TLE voxels (fluence-based; always positive). This
inflated DTM organ means by up to 11x. The fix includes zero-dose voxels in
the mean. With the fix, DTM and TLE agree within 2-4% on effective dose.

## Phase-space replay normalization

For phase-space replay with `PhaseSpaceMultipleUse = M` and
`NumberOfSequentialTimes = R`, set `n_scorer_active_histories = N_scoring ×
R × M` in the replay metadata. This accounts for the M× amplification of
raw_sum from particle reuse. Using the TOPAS-reported `N_phsp × M × R`
overestimates the dose by approximately `N_scoring / N_phsp` (~24x).
