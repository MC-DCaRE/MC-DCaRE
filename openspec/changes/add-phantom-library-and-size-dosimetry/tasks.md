## Status

- [ ] Phase 1: unify voxel path + config (on adult AM/AF baseline, unblocked)
- [ ] Phase 2: ingest ICRP 156 paediatric data + voxelize
- [ ] Phase 3: size-based dosimetry (percentile subset)

## 1. Unify voxel phantom path

- [~] 1.1 `phantomVoxel.txt` form produced directly by the voxelizer (B3 emits it; no separate .j2 needed)
- [x] 1.2 `headsourcecode_boilerplate.j2` routes ICRP145 -> phantomVoxel.txt when `use_voxel_phantom` (default True); phantomICRP145.txt when False
- [x] 1.3 `phantom_mode.prepare_run` copies phantomVoxel.txt + icrp_materials.txt from resolved voxel dir (no post-hoc swap)
- [~] 1.4 `scripts/run_full_calibration.py:swap_voxel_phantom` deprecated (no longer needed when use_voxel_phantom=True; left in place for legacy)

## 2. Phantom library config

- [x] 2.1 `PhantomConfig`: add `phantom_age`, `phantom_size_percentile`, `phantom_voxel_size_mm`, `phantom_voxel_directory`
- [x] 2.2 `phantom_name` resolver: age + sex + percentile (`resolve_phantom_name()` + `resolve_voxel_directory()`)
- [x] 2.3 `phantom_mode.py:build_sub_context`: emit voxel context + age-scaled couch offset
- [~] 2.4 size-scaled couch posterior offset (scale table added; needs per-age validation against real paediatric mesh extents)
- [x] 2.5 unit tests for name resolution + voxel dir + validation (TestPhantomResolution, 8 tests)

## 3. One voxelizer entry point

- [x] 3.1 `tools/voxelize_phantom.py` emits `.npy` + `phantomVoxel.txt` + `icrp_materials.txt` (verified on Omed mesh)
- [~] 3.2 generalize/retire `scripts/regenerate_voxel_phantom.py` + `scripts/voxelize_mrcp_am_fast.py` (logic ported to voxelize_phantom; old scripts left as legacy)
- [x] 3.3 document the voxelized-phantom directory contract (icrp156_ingest.md + tool docstrings)
- [ ] 3.4 voxelize adult female -> `data/P145/voxelized/MRCP_AF_5mm/` (needs MRCP_AF run)

## 4. Post-processing + CLI

- [ ] 4.1 `phantom_dose_calculator.py` + `calculate_phantom_dose.py`: resolve paths from `phantom_name`
- [ ] 4.2 restructure `calibration.yaml` `effective_dose_references` (add phantom + reference fields)
- [ ] 4.3 `icrp103.py`: no change; document age-agnostic mapping

## 5. ICRP 156 paediatric ingest

- [ ] 5.1 download ICRP 156 electronic supplement (10 phantoms: 0/1/5/10/15y x M/F)
- [ ] 5.2 stage into `data/P145/Phantom_data/MRCP_{sex}_{age}/`; tetgen convert if .obj-only
- [ ] 5.3 voxelize each at 5 mm -> `data/P145/voxelized/MRCP_{sex}_{age}_5mm/`
- [ ] 5.4 `data/P145/README.md` ingest + provenance doc
- [ ] 5.5 smoke run each paediatric phantom (short history)

## 6. Size-based dosimetry

- [ ] 6.1 obtain percentile subsets (Choi 2020 adult, Kim 2024 paediatric) per age/sex
- [ ] 6.2 voxelize 10th/90th percentile phantoms
- [ ] 6.3 reporting: E(height,weight) from three percentile runs per protocol
- [ ] 6.4 validate size-spread vs Martin 2022 / Abuhaimed 2023 trends

## 7. Quality gates + docs

- [ ] 7.1 tests: age/sex selection, voxel-template render, AF + paediatric round-trip
- [ ] 7.2 ruff + mypy + pytest green
- [ ] 7.3 update `src/AGENTS.md`, `tests/AGENTS.md`, `data/P145/README.md`
