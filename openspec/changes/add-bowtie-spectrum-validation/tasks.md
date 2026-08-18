## Status

> **UPDATE 2026-08-14 (validate-bowtie-stl-asset landed).** The bow-tie premise
> of this change is **refuted**: the TsCAD STL was validated against the RaySafe
> cross-plane profile (peak-normalised RMS 0.078 vs 0.583 for legacy CSG) and
> matches measurement -- see `docs/bowtie_validation/`. The legacy CSG bow-tie
> is the one that fails to shape the profile. The FF-modes-low symptom this
> change blamed on the bow-tie therefore has another cause (spectrum /
> normalization / phantom), **not** the bow-tie. `imaging.legacy_bowtie` now
> defaults to False (TsCAD).
>
> Consequences for the remaining work here:
> - Phases 1, 2, 5 (STL tooling, TsCAD templates, validation utility) are DONE
>   and superseded by `validate-bowtie-stl-asset`.
> - Phase 6 (re-calibration) is RUNNING via `scripts/run_full_calibration.py`
>   at the TsCAD bow-tie.
> - The **genuine remaining gap is the CAX HVL** (Phases 3-4): the spatial
>   profile was validated, but the MC CAX energy spectrum / HVL was never
>   scored (measured = 7.37 mmAl). That is the focused follow-up below.

- [x] Phase 1: STL bow-tie geometry + spectrum filtration (DONE; superseded by validate-bowtie-stl-asset)
- [ ] Phase 2: CAX HVL computation + validation (REMAINING -- the open gap)
- [~] Phase 3: re-calibration + regression (re-cal RUNNING at TsCAD; regression after)

## 1. STL processing tool

- [x] 1.1 `tools/process_bowtie_stl.py`: ASCII STL parser (stdlib)
- [x] 1.2 recenter by bbox centroid
- [x] 1.3 decimate to configurable triangle target (vertex-clustering weld)
- [x] 1.4 write binary STL -> `fullfan.stl`
- [x] 1.5 derive half-fan (crop one lateral half + recenter) -> `halffan.stl`
- [x] 1.6 inspection report -> README in output dir
- [x] 1.7 unit tests: triangle count, bbox, half-fan one-sidedness

## 2. TsCAD bow-tie templates

- [x] 2.1 `bowtie_ff.txt`, `bowtie_hf.txt` TsCAD parameter includes (generated assets in TOPAS_includeFiles/)
- [x] 2.2 `headsourcecode_boilerplate.j2` / `ctdi_phsp_score.j2` fan_mode + legacy_bowtie dispatch
- [x] 2.3 `base.copy_common_files()` copies `fullfan.stl`/`halffan.stl` + TsCAD includes to runfolder
- [x] 2.4 `imaging.legacy_bowtie` flag (default True = validated CSG fallback)
- [x] 2.5 BHF thickness from `imaging.bhf_thickness_mm` (replace hardcoded 0.7; default 0.89)
- [x] 2.6 dry-run render test: TsCAD params present, dispatch correct (TestBowtieDispatch)
- [x] 2.7 TOPAS validation: TsCAD bow-tie loads + transports cleanly. Placement
      fixed: reparented to Rotation at 18 cm source-to-bowtie distance (was in
      the collimator bay, overlapping Coll1/BHF). Result: 0 overlaps, symmetric
      Top/Bottom dose. UPDATE 2026-08-14: TsCAD validated against RaySafe and
      adopted -- `legacy_bowtie` default is now False (see validate-bowtie-stl-asset).

## 3. Spectrum filtration + HVL

- [x] 3.1 `imaging.filtration_mode` config field (geometric|hybrid, default hybrid)
- [x] 3.2 `spectrum_generator.py`: apply Al filters in hybrid mode
- [x] 3.3 compute `s.get_hvl1()` -> metadata `spekpy.hvl_mmAl` + calibration file
- [x] 3.4 unit test: hybrid mode filters, geometric does not, HVL recorded

## 4. HVL in PhaseSpaceAnalyzer

- [x] 4.1 ship `data/nist/hvl_coefficients.dat` (NIST XCOM Al + air, 10-150 keV)
- [x] 4.2 `analyze()` HVL fold -> `hvl_mmAl` in result dict (gated by nist_coefficients_path)
- [x] 4.3 unit test: 60 keV monoenergetic -> ~9.2 mm (matches ln2/mu)

## 5. Validation utility

- [x] 5.1 add `openpyxl` to pyproject dependencies
- [x] 5.2 isocenter-plane cross-profile scorer in `ctdi_phsp_score.j2` -- DONE in validate-bowtie-stl-asset (the `validate_bowtie` TLE slab, Z-binned, wide field; see `docs/bowtie_validation/`)
- [x] 5.3 `src/services/bowtie_validator.py`: read measured RaySafe profile + compare to MC CSV (peak-normalised, RMS misfit)
- [x] 5.4 `tools/validate_bowtie.py` CLI -> CSV + PNG
- [x] 5.5 unit tests (4) + smoke test against the real Oct 2023 workbook (Head CAX HVL 7.37 mmAl)

## 5a. CAX HVL follow-up (the remaining gap)

The spatial kerma profile is validated (TsCAD matches). The MC **CAX HVL** is
not yet scored -- the infrastructure exists (4.1-4.3 PhaseSpaceAnalyzer NIST
fold; 3.3 SpekPy source spectrum HVL), but there is no post-bow-tie CAX
spectrum scorer to feed it. Measured Head-FF CAX HVL = 7.37 mm Al.

- [x] 5a.1 add an energy-binned fluence scorer at the isocenter CAX bin (alongside the `validate_bowtie` slab) so the post-bow-tie CAX spectrum is recorded
  *(done: `CaxSlab` + `Sc/CaxSpectrum` Fluence scorer, 150 x 1 keV bins, in `ctdi_phsp_score.j2`)*
- [x] 5a.2 fold that spectrum with the shipped NIST Al mu_en/rho (`data/nist/hvl_coefficients.dat`) via `PhaseSpaceAnalyzer.compute_hvl_mm_al` to get the MC CAX HVL
  *(done: `tools/compute_cax_hvl.py`)*
- [x] 5a.2 compare MC CAX HVL to the measured 7.37 mm Al (tolerance ~0.5 mm Al); record in `docs/bowtie_validation/`
  *(done 2026-08-18, both fans + no-bowtie controls: FF TsCAD 7.80 vs 7.37 = +0.43 PASS,
  legacy 8.26 fail; HF TsCAD 8.96 vs 8.06 = +0.90, legacy 9.34; no-bowtie controls
  7.96/8.90 prove the residual is base filtration (Ti BHF + inherent Al), not the
  bow-tie. Full tables in docs/bowtie_validation/README.md)*


## 6. Re-calibration + regression

- [x] 6.1 re-run the 5 DCF calibration runs at Ti 0.89 mm + STL bow-tie
  *(done 2026-08-14 overnight: 6 protocols at TsCAD, 180M each)*
- [x] 6.2 update `calibration.yaml` DCF entries
  *(date_calibrated 2026-08-14; dcf_tle per protocol in the file)*
- [x] 6.3 re-run FF modes; confirm the -65..-88% gap narrows
  *(edose sweep 2026-08-18: Pelvis Spotlight -65%->-9%, Abdo -56%->-11%,
  Head/SRS/Extremity -84..-88%->-56%; residual is systematic, not bow-tie)*
- [ ] 6.4 quality gates: ruff, mypy, pytest green
- [ ] 6.5 update `src/AGENTS.md` + `fieldtobladeopening.py` TODO (cite Oct 2023 data)
