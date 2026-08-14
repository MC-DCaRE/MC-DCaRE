## Status

- [x] Phase 1: score cross-plane profiles (legacy CSG, TsCAD STL, no-bow-tie)
- [x] Phase 2: compare to measured RaySafe profile + HVL; decision
- [ ] Phase 3: act on the decision (adopt / diagnose / retain CSG); re-calibrate

## 1. Score the cross-plane profiles

- [x] 1.1 Run CTDI score-mode with `validate_bowtie` scorer ON, legacy CSG bow-tie (Head FF) -> cross-plane dose profile
- [x] 1.2 Same with TsCAD STL bow-tie (`legacy_bowtie=false`)
- [x] 1.3 Same with no bow-tie (baseline beam profile)
- [ ] 1.4 Repeat for one Half Fan mode (Pelvis HF) since the HF is a derived crop
- [x] 1.5 Export each profile to CSV (position_cm, dose)

> **Phase 1 notes (2026-08-14).** Two scaffolding defects were found and fixed
> before the profiles could be scored: (a) `validate_bowtie` / `bowtie_enabled`
> were not wired through `CtdiConfig`/`ImagingConfig` and the mode contexts, so
> the scorer was silently skipped and the bow-tie include could not be disabled;
> (b) the scorer was `DoseToWater` in a 0.5 mm air slab, which records ~0
> (collision dose in thin air) -- switched to `TrackLengthEstimator`.
>
> The decisive geometry correction: the bow-tie wedge varies in **World Z**
> (verified from `fullfan.txt` wedge layout + the fact that tscad/legacy/nobtie
> give identical X-shapes). The scorer was originally X-binned (10.7 cm
> Head-mode X-field) -- binned Z instead, with a wide Z-field (user_field_x=32 cm)
> so the collimator does not cut the bow-tie profile. The field->blade
> conversion was verified correct and self-consistent (field 10.7 cm -> 10.7 cm
> X-field at isocenter; blade TransX is from the parent centre and the blade
> half-width is absorbed in the linear calibration).

## 2. Compare to measurement + decide

- [x] 2.1 `tools/validate_bowtie.py --measured <RaySafe xlsx> --mc-profile <csv>` for each bow-tie; collect RMS misfit + HVL
- [x] 2.2 Tabulate: measured vs legacy CSG vs TsCAD vs no-bow-tie (normalised profile + CAX HVL)
- [x] 2.3 Decide:
   - TsCAD matches measured -> ADOPT (3.x mSv is physical; PCXMC/literature off)
   - TsCAD over-attenuated vs measured -> go to Phase 3 diagnose

> **Phase 2 DECISION (2026-08-14): TsCAD MATCHES -> ADOPT.**
> Peak-normalised RMS vs RaySafe Head FF (Z axis, wide field, 8M histories):
>
> | bow-tie | RMS (all) | RMS (\|X\|<=10) |
> |---|---|---|
> | TsCAD STL | **0.078** | **0.075** |
> | legacy CSG | 0.583 | 0.458 |
> | no bow-tie | 0.602 | 0.471 |
>
> The TsCAD STL reproduces the measured bow-tie wedge shape (central peak,
> attenuation to ~0.14 at +-8-12 cm). The legacy CSG bow-tie is nearly FLAT
> (~0.85 across +-16 cm) -- it attenuates the CAX like a uniform filter but does
> NOT shape the cross-plane profile. Measured CAX HVL = 7.37 mmAl (literature
> anchor, matched). Per the design decision tree, TsCAD matches -> adopt.
>
> This **refutes** the original premise (that TsCAD over-attenuates and causes
> the ~40 % low pelvis effective dose). The bow-tie asset is correct; the
> effective-dose discrepancy (3.x mSv vs 5.4 mSv Hauri 2017) has another cause.
> Notably the TsCAD CAX dose (5.45e-11) is *higher* than legacy (4.59e-11), so
> the bow-tie cannot be what lowers the phantom dose.

## 3. Diagnose (only if TsCAD does NOT match)

- [ ] 3.1 Confirm the Inbum STL is the correct TrueBeam full-fan filter (cross-check the asset provenance / a second source)
- [ ] 3.2 Sweep source-to-bowtie distance (15/18/21 cm) -- does the profile shape converge to measured?
- [ ] 3.3 Check material: is the STL a solid block or a true wedge? Compare ray-cast thickness profile to a published bow-tie profile
- [ ] 3.4 Outcome: source correct STL / fix placement+material, OR retain CSG (`legacy_bowtie=True` default, documented)

> **N/A -- TsCAD matches measured, so no diagnosis is required.**

## 4. Finalise

- [ ] 4.1 Re-run the full DCF calibration suite at the chosen bow-tie + filtration mode
- [ ] 4.2 Update `calibration.yaml` DCF entries
- [x] 4.3 Flip `legacy_bowtie` to the validated default; update `src/AGENTS.md`
- [ ] 4.4 Re-run the pelvis phantom effective dose; confirm vs reference within tolerance
- [x] 4.5 Commit + push

> **Phase 4 status (2026-08-14).** 4.3 + 4.5 done: `imaging.legacy_bowtie` default
> flipped to False (TsCAD), `src/AGENTS.md` updated with the validated decision,
> code/config/docs/tests committed and pushed (develop 073e93b, d67dba3).
> 4.1 is RUNNING: `scripts/run_full_calibration.py` launched in the background
> (PTY `tscad-recalibration`) at the TsCAD bow-tie -- 6 CTDI calibrations
> (180M histories each) + verification + pelvis phantom, ~6-8 h. On completion
> it writes the TsCAD DCFs to `calibration.yaml` (4.2) and emits the phantom
> effective dose (4.4). The stale-DCF note in `calibration.yaml` is removed
> when 4.2 lands.
