## Status

- [~] Phase 1: STL bow-tie geometry + spectrum filtration (plumbing done; needs TOPAS validation)
- [ ] Phase 2: HVL computation + validation utility
- [ ] Phase 3: re-calibration + regression

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
      Top/Bottom dose (TsCAD Centre 2.96e-10 vs legacy CSG 4.6e-10 -- the real
      measured filter attenuates ~36% more, as expected). legacy_bowtie stays
      default True until DCF re-calibration at the new bow-tie.

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
- [~] 5.2 isocenter-plane cross-profile scorer in `ctdi_phsp_score.j2` (deferred -- needs TOPAS; validator accepts a scored CSV instead)
- [x] 5.3 `src/services/bowtie_validator.py`: read measured RaySafe profile + compare to MC CSV (peak-normalised, RMS misfit)
- [x] 5.4 `tools/validate_bowtie.py` CLI -> CSV + PNG
- [x] 5.5 unit tests (4) + smoke test against the real Oct 2023 workbook (Head CAX HVL 7.37 mmAl)

## 6. Re-calibration + regression

- [ ] 6.1 re-run the 5 DCF calibration runs at Ti 0.89 mm + STL bow-tie
- [ ] 6.2 update `calibration.yaml` DCF entries
- [ ] 6.3 re-run FF modes; confirm the -65..-88% gap narrows
- [ ] 6.4 quality gates: ruff, mypy, pytest green
- [ ] 6.5 update `src/AGENTS.md` + `fieldtobladeopening.py` TODO (cite Oct 2023 data)
