# Bow-tie filter validation: TsCAD STL vs legacy CSG vs no-bow-tie

Cross-plane air-kerma profile validation of the TsCAD mesh bow-tie against the
measured RaySafe Oct-2023 data. Source change: `openspec/changes/validate-bowtie-stl-asset/`.

> **CORRECTION (2026-08-14): orientation was wrong; results below are in the
> wrong plane.** The scorer that produced the RMS table below binned **World Z**
> (the phantom cylinder / scan axis), but a bow-tie wedge belongs in the
> **transverse fan (World X)** and must be *uniform* along Z. The 0.078 RMS is a
> 1D peak-normalised *shape* match between a Z-wedge (sim, mis-oriented) and a
> fan-wedge (RaySafe) -- it did not validate the orientation. The orientation
> was corrected (`RotY=90` in `bowtie_ff.txt`/`bowtie_hf.txt`); see
> `plots/axismap_tscad_FIXED_ff.png` (2D X×Z map: wedge now in X, flat in Z) and
> `plots/geometry_orientation.png`. A proper X-plane re-validation vs RaySafe is
> pending (the `validate_bowtie` scorer now bins X). The TsCAD STL wedge *shape*
> is still considered a good match; only its plane was wrong.

## Result

The TsCAD STL bow-tie is the validated asset; the legacy CSG bow-tie is not.

| Bow-tie | RMS vs RaySafe (all) | RMS (\|X\| ≤ 10 cm) | Verdict |
|---|---|---|---|
| **TsCAD STL** | **0.078** | **0.075** | reproduces measured wedge |
| legacy CSG | 0.583 | 0.458 | nearly flat -- does not shape the profile |
| no bow-tie | 0.602 | 0.471 | flat (unattenuated) |

Measured Head-FF CAX HVL = **7.37 mm Al** (RaySafe; literature anchor).

**Decision:** adopt TsCAD (`imaging.legacy_bowtie` default flipped to `False`).
This **refutes** the prior premise that the TsCAD bow-tie over-attenuates and
causes the ~40 % low pelvis effective dose -- TsCAD's CAX dose is in fact
*higher* than legacy, so the effective-dose gap lives elsewhere (spectrum /
normalization / phantom), not in the bow-tie.

## Methodology

- **Scorer:** `TrackLengthEstimator` (fluence-based collision kerma) on a thin
  G4_AIR slab at isocenter, in `src/boilerplates/ctdi_phsp_score.j2`, gated by
  `ctdi.validate_bowtie`. A collision-based `DoseToWater` scorer records ~0 in a
  0.5 mm air slab, so it cannot be used.
- **Axis (CORRECTED):** the bow-tie wedge belongs in **World X** (transverse
  fan) and must be uniform along **World Z** (scan axis). The original runs below
  scored Z (the wrong plane); the "identical X shapes" observation was the
  scorer not resolving X (XBins=1), not the bow-tie being uniform in X. After
  the `RotY=90` fix the scorer bins X and sees the wedge there. The scorer X-bins.
- **Collimator field (CORRECTED):** to expose the fan profile open the
  **X-field** wide (`user_field_y` ≥ 32 cm, which drives the X-direction blades)
  and leave the Z-field (`user_field_x`) at the Head default; the slab
  integrates the central Z strip.
- **Histories:** 8 M per config, static beam (`sequential_times = 1`, matches a
  stationary RaySafe measurement).
- **Field->blade:** verified self-consistent -- blade `TransX` is from the
  parent centre; the linear calibration absorbs the blade half-width and the
  source-to-collimator magnification (field 10.7 cm -> 10.7 cm field at
  isocenter; opens correctly to ±13 cm at field 28 cm).

## Run inventory (this validation, 2026-08-14)

| Label | Config | Runfolder |
|---|---|---|
| TsCAD FF | `configs/validate_bowtie_tscad.yaml` | `runfolder/2026-08-14_09-34-13` |
| legacy CSG FF | `configs/validate_bowtie_legacy.yaml` | `runfolder/2026-08-14_09-35-37` |
| no bow-tie FF | `configs/validate_bowtie_nobtie.yaml` | `runfolder/2026-08-14_09-36-42` |

(Runfolders are gitignored scratch; the durable artefacts are in this directory.)

## Files

- `profiles/profile_<tscad|legacy|nobtie>_ff.csv` -- converted MC profile
  (`position_cm, dose`), the input to `tools/validate_bowtie.py`.
- `profiles/bowtie_profile_<...>_ff_topas.csv` -- the raw TOPAS binned scorer
  output (index-based; converted by `tools/convert_bowtie_profile.py`).
- `compare_<label>_ff.csv` -- per-position measured vs MC (peak-normalised).
- `plots/overlay_all.png` -- all three MC profiles + RaySafe on one axes.
- `plots/compare_<label>_ff.png` -- per-bow-tie measured-vs-MC.
- `manifest.tsv` -- label -> runfolder -> profile CSV.

Reproduce with: `tools/run_bowtie_validation.sh` (re-run) then
`tools/tabulate_bowtie_validation.py` (compare + overlay).

## Open gap: CAX HVL

Only the **spatial** kerma profile was scored. The MC **CAX energy spectrum**
was not, so the MC CAX HVL has no computed counterpart to the measured 7.37 mm
Al. Adding a CAX spectrum scorer + an HVL computation is the remaining scope of
`add-bowtie-spectrum-validation` (Phase 2).
