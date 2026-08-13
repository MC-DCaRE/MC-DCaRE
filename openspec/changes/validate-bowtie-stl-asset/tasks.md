## Status

- [ ] Phase 1: score cross-plane profiles (legacy CSG, TsCAD STL, no-bow-tie)
- [ ] Phase 2: compare to measured RaySafe profile + HVL; decision
- [ ] Phase 3: act on the decision (adopt / diagnose / retain CSG); re-calibrate

## 1. Score the cross-plane profiles

- [ ] 1.1 Run CTDI score-mode with `validate_bowtie` scorer ON, legacy CSG bow-tie (Head FF) -> cross-plane dose profile
- [ ] 1.2 Same with TsCAD STL bow-tie (`legacy_bowtie=false`)
- [ ] 1.3 Same with no bow-tie (baseline beam profile)
- [ ] 1.4 Repeat for one Half Fan mode (Pelvis HF) since the HF is a derived crop
- [ ] 1.5 Export each profile to CSV (position_cm, dose)

## 2. Compare to measurement + decide

- [ ] 2.1 `tools/validate_bowtie.py --measured <RaySafe xlsx> --mc-profile <csv>` for each bow-tie; collect RMS misfit + HVL
- [ ] 2.2 Tabulate: measured vs legacy CSG vs TsCAD vs no-bow-tie (normalised profile + CAX HVL)
- [ ] 2.3 Decide:
   - TsCAD matches measured -> ADOPT (3.x mSv is physical; PCXMC/literature off)
   - TsCAD over-attenuated vs measured -> go to Phase 3 diagnose

## 3. Diagnose (only if TsCAD does NOT match)

- [ ] 3.1 Confirm the Inbum STL is the correct TrueBeam full-fan filter (cross-check the asset provenance / a second source)
- [ ] 3.2 Sweep source-to-bowtie distance (15/18/21 cm) -- does the profile shape converge to measured?
- [ ] 3.3 Check material: is the STL a solid block or a true wedge? Compare ray-cast thickness profile to a published bow-tie profile
- [ ] 3.4 Outcome: source correct STL / fix placement+material, OR retain CSG (`legacy_bowtie=True` default, documented)

## 4. Finalise

- [ ] 4.1 Re-run the full DCF calibration suite at the chosen bow-tie + filtration mode
- [ ] 4.2 Update `calibration.yaml` DCF entries
- [ ] 4.3 Flip `legacy_bowtie` to the validated default; update `src/AGENTS.md`
- [ ] 4.4 Re-run the pelvis phantom effective dose; confirm vs reference within tolerance
- [ ] 4.5 Commit + push
