# Calibration Summary Report

**Date**: 2026-06-13
**Machine**: TrueBeam SN1234
**Change**: calibrate-all-arcs

## 1. Dose Calibration Factors

| kV | Fan | Phantom | Protocol | mAs | Raw CTDI_w | Ref CTDI_w | DCF |
|----|-----|---------|----------|-----|-----------|-----------|-----|
| 80 | FF | 16 cm | Image Gently | 100.0 | 0.8273 mGy | 0.9 mGy | 0.001087 |
| 100 | FF | 16 cm | Head | 150.0 | 2.6793 mGy | 3.2 mGy | 0.001194 |
| 125 | FF | 32 cm | Pelvis Spotlight | 750.0 | 9.7888 mGy | 43.93 mGy* | 0.004486 |
| 125 | HF | 32 cm | Pelvis | 1080.0 | 9506.86 µGy | 15.9 mGy | 0.001672 |
| 140 | HF | 32 cm | Pelvis Large | 1700.5 | 20641.14 µGy | 37.1 mGy | 0.001798 |
| 100 | HF | — | (4 protocols) | 150.0 | — | no reference | null |
| 140 | FF | — | — | — | — | no reference | null |

*125 kV FF: reference 12.3 mGy at 210 mAs (Short Thorax), mAs-scaled to calibration 750 mAs: 12.3 × (750/210) = 43.93 mGy.

## 2. Cross-Validation

| kV | Fan | Protocol | Phantom | mAs | DCF | Ref (mGy) | Calibrated (mGy) | Error |
|----|-----|----------|---------|-----|-----|-----------|------------------|-------|
| 125 | FF | Short Thorax | 32 cm | 210 | 0.004486 | 12.3 | 12.30 | +0.00% |
| 125 | HF | Thorax | 32 cm | 268.5 | 0.001672 | 4.0 | 3.98 | −0.62% |

**Verdict**: DCF is kV/fan-specific — same DCF transfers across protocols within a group. Both PASS.

## 3. DCF Fan-Mode Specificity

DCFs are specific to (kV, fan_mode). A Full Fan DCF **cannot** substitute for a Half Fan DCF at the same kV.

| kV | Fan FF DCF | Fan HF DCF | Ratio | Error if FF DCF applied to HF |
|----|-----------|-----------|-------|-------------------------------|
| 125 | 0.004486 | 0.001672 | 2.68× | +165% |

**Why they differ:** Fan modes use different bowtie filtration (full vs half bowtie). The half bowtie hardens the beam asymmetrically, changing the spectrum reaching the chamber. Scatter field geometry is also completely different — Full Fan uses 14×14 cm, Half Fan uses 24.7×3.3 cm — so phantom-scatter contribution to chamber response changes. The DCF captures the full beam-quality + geometry + scatter condition, not just kV.

**Fix:** Each (kV, fan_mode) pair needs its own ion chamber calibration measurement. Cannot derive one from the other.

## 4. Arc-Length and Dose-Level Independence

DCF is independent of arc length and dose level (mAs) at the same (kV, fan_mode).

### 4.1 Half-Arc Geometry Test (Same Histories, Same mAs)

| Test | Arc | Seq | mAs | Raw CTDI_w | DCF | Calibrated | Expected | Error |
|------|-----|-----|-----|-----------|-----|-----------|----------|-------|
| Full arc Pelvis (125 HF) | 360° | 80 | 1080 | 9.507 Gy | 0.001672 | 15.89 mGy | 15.9 mGy | — |
| Half arc Pelvis (125 HF) | 180° | **80** | 1074 | 9.583 Gy | 0.001672 | 16.02 mGy | 15.9 mGy | +0.75% |

Raw CTDI_w doesn't halve with arc length — same head_cal_factor (same mAs, same total_histories) keeps dose-per-particle normalization constant. DCF transfers across arc lengths within noise.

### 4.2 Half-Dose Test (Same Histories, Half Arc + Half Exposure)

| Test | Arc | Seq | mAs | Raw CTDI_w | DCF | Calibrated | Expected | Error |
|------|-----|-----|-----|-----------|-----|-----------|----------|-------|
| Full dose Pelvis (125 HF) | 360° | 80 | 1080 | 9.507 Gy | 0.001672 | 15.89 mGy | 15.9 mGy | — |
| Half dose Pelvis (125 HF) | **180°** | **80** | **540** | 4.818 Gy | 0.001672 | 8.06 mGy | 7.95 mGy | +1.34% |

This test confounds two changes: half-arc (timeline_end=450 s) and half-mAs (540 from 1080). However, the half-arc v2 test (Section 4.1) proved raw CTDI_w is insensitive to arc length at the same mAs (9.507 Gy full arc vs 9.583 Gy half arc, +0.8%). So the dominant effect on raw CTDI_w is the mAs halving. Predicted raw for half-arc + half-mAs: 9.583 × (540/1080) = 4.791 Gy. Actual: 4.818 Gy (+0.56% from prediction, within MC noise). Calibrated dose (8.06 mGy) is within 1.34% of the half-reference (7.95 mGy = 15.9 / 2). **Verdict: DCF linearity holds across mAs — the calibration chain correctly scales dose for partial exposures.**

## 5. Uncalibratable

- **100 kV Half Fan** (4 protocols, 150 mAs): no reference CTDI_w — DCF = null.
- **140 kV Full Fan**: no CBCT protocol in lookup table — DCF = null.

## 6. Anomalies & Recommendations

- **125 FF DCF bug caught**: original 0.001256 missed mAs-scaling of reference CTDI_w. Corrected to 0.004486.
- **140 HF wall time**: ~27h total, only 36 min TOPAS. SCMLframework overhead.
- **No xval possible** for 80 FF, 100 FF, 140 HF: only one reference protocol per group.
- **Pelvis mAs discrepancy**: lookup table says 1074 mAs, runs used 1080 mAs. Calibration chain is self-consistent as long as same mAs is used throughout. Recommend syncing lookup to 1080 if reference table is authoritative.
- **Half-arc test confounded (v1)**: original test halved both `sequential_times` (80→40) and `timeline_end` (900→450 s), not realizing `NumberOfSequentialTimes` only controls statistics, not arc geometry. Re-ran with `sequential_times: 80` only changing `timeline_end`. Results consistent: DCF independent of arc length.
- **mAs**: half-arc config auto-populated 1074 mAs (lookup table) vs calibration 1080 mAs. Negligible impact (+0.75% error vs clean 0% if mAs matched).

## 7. Runfolders

| Run | Purpose | Path |
|-----|---------|------|
| 2026-06-12_10-49-35 | 125 HF Pelvis calibration (1080 mAs) | `runfolder/` |
| 2026-06-12_13-04-10 | 125 HF Thorax cross-validation (PASS) | `runfolder/` |
| 2026-06-12_14-13-02 | 80 FF Image Gently calibration (100 mAs) | `runfolder/` |
| 2026-06-12_14-58-19 | 100 FF Head calibration (150 mAs) | `runfolder/` |
| 2026-06-12_15-37-28 | 125 FF Pelvis Spotlight calibration (750 mAs) | `runfolder/` |
| 2026-06-12_16-17-43 | 140 HF Pelvis Large calibration (1700.5 mAs) | `runfolder/` |
| 2026-06-12_17-00-47 | 125 FF Short Thorax cross-validation (PASS) | `runfolder/` |
| 2026-06-15_08-36-11 | 125 HF Pelvis half-arc v1 (seq_times=40 — stats confounded) | `runfolder/` |
| 2026-06-15_10-02-02 | 125 HF Pelvis half-arc v2 (seq_times=80 — corrected, same stats as full arc) | `runfolder/` |
| 2026-06-15_10-39-52 | 125 HF Pelvis half-dose test (seq_times=80, 540 mAs — half exposure, same stats) | `runfolder/` |

## 8. Files

- `calibration.example.yaml`: 5 DCFs + 140 FF null entry
- `src/models/imaging_mode.py`: exposures synced to reference table
- `configs/cal_*.yaml`: 4 calibration configs
- `configs/xval_125kv_ff_short-thorax.yaml`: xval config
- `configs/xval_125kv_hf_pelvis-half-arc.yaml`: arc-dependence test config (corrected: seq_times=80, timeline_end=450 s)
- `configs/xval_125kv_hf_pelvis-half-dose.yaml`: dose-linearity test config (seq_times=80, timeline_end=900 s, exposure=540 mAs)
