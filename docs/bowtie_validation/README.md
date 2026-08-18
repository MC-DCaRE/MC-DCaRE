# Bow-tie filter validation: TsCAD STL vs legacy CSG vs no-bow-tie

Cross-plane air-kerma profile validation of the TsCAD mesh bow-tie against the
measured RaySafe Oct-2023 data. Source change: `openspec/changes/validate-bowtie-stl-asset/`.

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
- **Axis:** the bow-tie wedge varies in **World Z**, not X (verified from the
  `fullfan.txt` wedge layout and the fact that tscad/legacy/nobtie give
  identical X shapes). The scorer Z-bins.
- **Collimator field:** wide Z-field (`user_field_x` = 32 cm) so the collimator
  does not cut the bow-tie profile before it develops. The Head-mode X-field
  (10.7 cm) is left at default; the slab integrates the central X strip.
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

## Final outcome (post re-calibration, 2026-08-14/18)

Adopted TsCAD (`legacy_bowtie=False` default), full DCF re-calibration at TsCAD
(6 protocols, `calibration.yaml` date_calibrated 2026-08-14: dcf_tle 80 FF
0.20361, 100 FF 0.19744, 125 FF 0.19097, 125 HF 0.26365, 140 HF 0.27683).

**Pelvis phantom (MRCP-AM, 150M hist): E = 3.09 mSv (TLE)** vs 4.2 PCXMC
(-26%) / 5.4 Hauri (-43%). Dominant contributor: bladder (28 mSy organ, 1.12
mSv weighted of the 3.09 total).

Full-protocol sweep (5M hist/protocol, `scripts/run_edose_validation.py` ->
`edose_validation_runs/validation_results.csv`), new-vs-old diff vs reference:

| protocol | legacy diff | TsCAD diff |
|---|---|---|
| Pelvis Spotlight (FF) | -65% | **-9%** |
| Abdo Spotlight (FF) | -56% | **-11%** |
| Pelvis (HF) | -54% | -28% |
| Abdomen (HF) | -62% | -28% |
| Thorax (HF) | 0% | -42% |
| Head / SRS / Extremity (FF) | -84..-88% | -56..-57% |
| Head and Shoulders | +140% | +153% |

The FF body modes closed almost entirely; a consistent residual ~-28..-56%
remains across modes. Since the bow-tie is measured-validated and the DCFs are
fresh, that residual is systematic elsewhere (spectrum fidelity vs TrueBeam,
PCXMC reference provenance, or the CTDI->phantom DCF transfer) -- follow-up
work, not a bow-tie issue.
