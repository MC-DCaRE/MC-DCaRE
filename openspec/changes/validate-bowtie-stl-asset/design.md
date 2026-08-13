# Design -- validate-bowtie-stl-asset

## Evidence: the new bow-tie over-attenuates

125 kV Half Fan Pelvis, MRCP_AM voxel phantom, lean histories (geometric 200k x
36; hybrid matched). Effective dose = raw organ dose x CTDI-derived DCF x
ICRP-103 weights.

| configuration | DCF (125 HF) | effective dose | % of 4.2 ref |
|---|---|---|---|
| old CSG bow-tie, bare spectrum (prior system) | 0.161 | ~5.5 mSv | 131% |
| new TsCAD bow-tie, geometric | 0.228 | 3.37 mSv | 80% |
| new TsCAD bow-tie, hybrid | 0.291 | 3.13 mSv | 74% |
| PCXMC reference | -- | 4.2 mSv | 100% |
| Hauri 2017 (TLD, Alderson) | -- | 5.4 mSv | 129% |
| Abuhaimed 2018 (BEAMnrc, ICRP-110) | -- | ~6 mSv | 143% |

- Filtration mode (hybrid vs geometric) is a **~7%** effect (3.37 -> 3.13).
- The bow-tie asset is the dominant driver: both modes land ~3.1-3.4 mSv, far
  below the old system's ~5.5 and the TLD/MC literature.
- CTDI self-calibration holds (sim x DCF = 15.9 mGy measured), but the
  CTDI->phantom DCF transfer does not compensate: the bow-tie shapes the beam
  profile, and the uniform CTDI cylinder vs the anatomical phantom respond
  differently.

## Validation methodology (decisive test)

Compare three bow-ties on the **same measurable quantity**: the cross-plane
air-kerma profile + HVL at isocenter.

1. Score the cross-plane profile. The `validate_bowtie` scorer (thin air slab
   at isocenter, 1-D cross-plane DoseToWater, already scaffolded in
   `ctdi_phsp_score.j2`) produces the MC side. Run it for: legacy CSG, TsCAD
   STL, and (for reference) no-bow-tie.
2. Read the measured reference with `src/services/bowtie_validator.py`
   (`load_measured_profile`) from the RaySafe Oct-2023 workbook "Collated
   results" (per-mode 4-column groups: dose, uGy/s, HVL). Head mode CAX HVL =
   7.37 mmAl is the literature anchor.
3. `compare_profiles` normalises all to peak=1, interpolates, reports the RMS
   misfit + per-position HVL.

The bow-tie that matches the measured profile is the physically-correct one.

## Decision tree

```
score legacy CSG, TsCAD STL, no-bow-tie profiles + HVL
            |
   compare to RaySafe measured profile
            |
   +--------+----------------+
   |                         |
TsCAD matches            TsCAD does NOT match
(measured profile)       (over-attenuated / wrong shape)
   |                         |
ADOPT TsCAD.              Diagnose:
3.x mSv is physical;      (a) wrong STL asset? (Inbum filter != TrueBeam FF?)
literature/PCXMC are      (b) source-to-bowtie distance (18 cm) -> magnification?
the ~30%-off values.      (c) material: G4_Al vs real alloy / hollow structure?
                          (d) STL includes mounting hardware / is a solid block
                              not a true wedge?
                              |
                          Either source correct STL / fix placement+material,
                          or RETAIN CSG bow-tie as default (legacy_bowtie=True).
```

Known inputs to the diagnosis:
- STL beam-direction thickness ~2 mm Al (ray-cast of the recentered STL) -- a
  true bow-tie wedge centre, so the bulk shape is plausible.
- STL alone in a vacuum world has 0 overlaps -> the asset itself is a valid
  closed mesh; the over-attenuation is its material/extent, not a navigation
  artefact.

## Out of scope (already done)

- TsCAD integration, `Rotation` @ 18 cm placement, copy step, `legacy_bowtie`
  flag -- all working (`add-bowtie-spectrum-validation`).
- DCF computation pipeline, voxel-phantom effective-dose pipeline -- working.
- Hybrid vs geometric filtration isolation -- done (hybrid is minor).

## Deliverable

A qualified bow-tie decision recorded in `src/AGENTS.md` + `calibration.yaml`,
with the DCF suite re-run at the chosen configuration. `legacy_bowtie` flipped
to the validated default.
