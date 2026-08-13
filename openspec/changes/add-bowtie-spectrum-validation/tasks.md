## Status

- [ ] Phase 1: STL bow-tie geometry + spectrum filtration (unblocked)
- [ ] Phase 2: HVL computation + validation utility
- [ ] Phase 3: re-calibration + regression

## 1. STL processing tool

- [ ] 1.1 `tools/process_bowtie_stl.py`: ASCII STL parser (stdlib)
- [ ] 1.2 recenter by bbox centroid
- [ ] 1.3 decimate to configurable triangle target (~20k)
- [ ] 1.4 write binary STL -> `data/bowtie/fullfan.stl`
- [ ] 1.5 derive half-fan (crop one lateral half + TransX offset) -> `data/bowtie/halffan.stl`
- [ ] 1.6 inspection report -> `data/bowtie/README.md`
- [ ] 1.7 unit tests: triangle count, bbox, half-fan one-sidedness

## 2. TsCAD bow-tie templates

- [ ] 2.1 `bowtie_ff.j2`, `bowtie_hf.j2` rendered includes (TsCAD params)
- [ ] 2.2 `headsourcecode_boilerplate.j2` / `ctdi_phsp_score.j2` fan_mode dispatch
- [ ] 2.3 `base.copy_common_files()` copies `fullfan.stl`/`halffan.stl` to runfolder
- [ ] 2.4 `imaging.legacy_bowtie` flag to keep CSG `.txt` fallback
- [ ] 2.5 BHF thickness from `imaging.bhf_thickness_mm` (replace hardcoded 0.7)
- [ ] 2.6 dry-run render test: TsCAD params present, InputFile correct

## 3. Spectrum filtration + HVL

- [ ] 3.1 `imaging.filtration_mode` config field (geometric|hybrid, default hybrid)
- [ ] 3.2 `spectrum_generator.py`: apply Al filters in hybrid mode
- [ ] 3.3 compute `s.get_hvl1()` -> metadata `spekpy.hvl_mmAl` + calibration file
- [ ] 3.4 unit test: hybrid mode produces lower bare-spectrum fluence + records HVL

## 4. HVL in PhaseSpaceAnalyzer

- [ ] 4.1 ship `data/nist/mu_en_aluminium.dat` (NIST XCOM Al)
- [ ] 4.2 `analyze()` HVL fold -> `hvl_mmAl` in result dict
- [ ] 4.3 unit test: known monoenergetic spectrum -> expected HVL

## 5. Validation utility

- [ ] 5.1 add `openpyxl` to pyproject dev/optional deps
- [ ] 5.2 `isocenter-plane` cross-profile scorer in `ctdi_phsp_score.j2` (gated)
- [ ] 5.3 `src/services/bowtie_validator.py`: read measured profile + compare
- [ ] 5.4 `tools/validate_bowtie.py` CLI -> CSV + PNG
- [ ] 5.5 smoke test on synthetic data

## 6. Re-calibration + regression

- [ ] 6.1 re-run the 5 DCF calibration runs at Ti 0.89 mm + STL bow-tie
- [ ] 6.2 update `calibration.yaml` DCF entries
- [ ] 6.3 re-run FF modes; confirm the -65..-88% gap narrows
- [ ] 6.4 quality gates: ruff, mypy, pytest green
- [ ] 6.5 update `src/AGENTS.md` + `fieldtobladeopening.py` TODO (cite Oct 2023 data)
