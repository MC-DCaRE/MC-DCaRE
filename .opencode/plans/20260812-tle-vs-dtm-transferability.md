# TLE vs DTM DCF Transferability — Test Plan

## Finding (confirmed on existing data)

The "DTM DCF doesn't transfer to phantom effective dose" conclusion in
`AGENTS.md` and `calibration.yaml` is a **selection-bias artifact**, not a
physics limitation.

### Root cause

`PhantomDoseCalculator._load_dose_data` (phantom_dose_calculator.py:172)
skips every voxel with `dose <= 0`:

```python
dose = float(parts[3])
if dose <= 0:
    continue
```

DTM (DoseToMedium, collision-based) produces `dose = 0` for voxels where no
photon interaction occurred. TLE (TrackLengthEstimator, fluence-based)
produces `dose > 0` for every voxel a photon track traverses. The filter
therefore **exclusively removes DTM voxels**, inflating DTM organ means.

### Evidence (pelvis_phantom_5M, 125 kV HF, 5M histories)

| Method | Eff. Dose (mSv) | vs TLE |
|---|---|---|
| TLE (all voxels) | 5.77 | 1.00x (anchor) |
| DTM (nonzero only) [CURRENT BUG] | 61.33 | 10.63x |
| **DTM (all voxels) [FIXED]** | **5.53** | **0.96x** |

DTM agrees with TLE within 4% when zero-dose voxels are included.

Worst bias is in far-from-beam organs (Brain, Lung, Heart, Spleen) where
100% of DTM voxels are zero at 5M histories — the few that score are rare
scatter events with enormous per-voxel dose.

### Voxel statistics

- 2,468,670 total voxels in the 114x61x355 grid
- DTM non-zero: 20.2%, TLE non-zero: 47.2%
- DTM=0 but TLE>0: 27.1% (these are the voxels the filter discards)
- DTM>0 but TLE=0: 0.0% (every DTM voxel also has TLE — expected)

## Literature validation

| Source | Pelvis CBCT Eff. Dose |
|---|---|
| Hauri 2017 (TLD, Alderson, same protocol) | 5.4 mSv ±5% |
| Our TLE result | 5.77 mSv (+7% vs Hauri) |
| Our DTM [FIXED] result | 5.53 mSv (+2% vs Hauri) |
| Manufacturer reference (calibration.yaml) | 4.2 mSv |
| Our DTM [BUG] result | 61.33 mSv (clearly wrong) |

The 4.2 mSv manufacturer reference is below the independent literature
range. Both TLE and DTM(fixed) land at 5.5-5.8 mSv, consistent with Hauri.

## Experiments

### Exp 1: Fix PhantomDoseCalculator and recompute (no TOPAS needed)

Change: remove `dose <= 0` filter, keep only `mat_id == -1` (outside body)
filter. Recompute effective dose from existing pelvis_phantom_5M data.

Expected: DTM effective dose drops from ~60 mSv to ~5.5 mSv.

### Exp 2: Higher-history phantom run (TOPAS) — COMPLETED

Ran the phantom simulation at 75.5M histories (209K phase space particles ×
M=10 × 36 angles, ~16 min wall time on 20 threads). Both TLE and DTM scored
simultaneously on the same voxel grid.

| Metric | 5M histories | 75M histories |
|---|---|---|
| DTM non-zero fraction (body) | ~20% | 48.4% |
| DTM=0 but TLE>0 | ~27% | 37.3% |
| DTM(nz)/TLE [OLD BUG] | 10.6x | 1.15x |
| **DTM(all)/TLE [FIXED]** | **0.96x** | **0.98x** |
| Selection-bias inflation | 11.0x | 1.2x |

The selection bias collapsed from 11x to 1.2x with 15x more histories,
proving it was statistical (low interaction counts), not a physics limitation.
DTM(all)/TLE improved from 0.96x to 0.98x — near-perfect CPE convergence.

### Exp 3: Voxel-by-voxel TLE/DTM ratio map

For voxels where both are non-zero, plot DTM/TLE ratio vs. dose level.
Expected: ratio clusters near 1.0 for high-dose voxels (good CPE,
well-converged), scatter widely for low-dose voxels (poor statistics).

## Cleanup

Keep only the 5 calibration runs (2026-08-11 batch, referenced in
calibration.yaml header):
- 2026-08-11_14-33-57 (80 FF)
- 2026-08-11_15-34-37 (100 FF)
- 2026-08-11_16-34-38 (125 FF)
- 2026-08-11_17-33-14 (125 HF)
- 2026-08-11_18-32-20 (140 HF)

Delete everything else (~97 folders, ~15 GB).
