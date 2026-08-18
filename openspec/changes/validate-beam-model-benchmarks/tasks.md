## Status

- [x] Phase 1: absolute CAX kerma + transmission ratios (anchors, tool, runs)
- [x] Phase 2: Ti-state bracketing + base-filtration attribution
  + NEW: `imaging.bhf_mode` toggle (geometric TsBox | spekpy-folded Ti)
- [ ] Phase 3: HVL(Z) wedge map
- [ ] Phase 4: Gros 2025 Kair per protocol
- [ ] Phase 5: literature per-100 mAs benchmarks + docs

## 1. Absolute CAX kerma (Ti in)

- [x] 1.1 `data/measured/cax_kerma_anchors.yaml` with provenance + ambiguity flags (120 kV 6.523 excluded; 80 kV HVL flagged)
- [x] 1.2 `tools/compare_cax_kerma.py` (canonical normalization; ratios; --mAs 1.6 default)
- [x] 1.3 clinical-field runs: Head FF TsCAD (vs 59.01), reuse 125 HF TsCAD (vs 106.3)
- [x] 1.4 no-bow-tie clinical runs: 100 kV (vs 112.8), 80 kV (vs 28.89)
- [x] 1.5 bow-tie transmission ratio MC 0.899 vs measured 0.523 (Head) -- STL CAX ~1.7x too transparent
- [x] 1.6 record results + verdicts in docs/bowtie_validation/ (Absolute CAX kerma section)

## 2. Ti-state bracketing

- [x] 2.1 no-BT Ti-out runs (`bhf_thickness_mm: 0.0`): 100 kV FF, 125 HF (HVL 2.99 / 3.72)
- [x] 2.2 bracketed: HVL 5.04 sits between Ti-out (2.99) and geometric default (7.96); spekpy-0.445 arm matches (-0.19). Measured Ti state unresolved (unstated in workbook)
- [x] 2.3 FINDINGS: (a) TOPAS HLZ half-length bug -- geometric default = 1.78 mm Ti (2x); (b) MC absolute kerma 3-7x high (photons_per_mAs fluence scale); (c) STL CAX too transparent (see 1.5). Follow-ups proposed: bhf_mode=spekpy default + re-cal; STL central thickness; fluence re-anchor

## 3. HVL(Z) wedge map

- [ ] 3.1 config + scorer: `ZBins=40 x EBins=100` energy-resolved profile (new config; production profile config unchanged)
- [ ] 3.2 `tools/compute_hvl_map.py`: per-Z fold -> HVL(Z) CSV + plot vs measured hvl_mmAl (Head FF + Pelvis HF, TsCAD + legacy)
- [ ] 3.3 record wedge-shape verdicts (this is the sharpest bow-tie test)

## 4. Gros 2025 Kair per protocol

- [ ] 4.1 five score-mode runs (Head/Thorax/Pelvis/Pelvis Large/Spotlight) clinical fields, absolute kerma at iso
- [ ] 4.2 compare to Gros Kair (5.3/17.8/64.3/132.0/44.7 mGy) with technique matching noted (Spotlight outlier expected)

## 5. Literature per-100 mAs benchmarks

- [ ] 5.1 `data/literature/abuhaimed2023_tables.yaml` (Tables 2-3 organ + SSED per 100 mAs)
- [ ] 5.2 tool/analysis: our edose organ_doses + E per 100 mAs vs tables; organ-level residual table
- [ ] 5.3 docs: update Literature comparison section (add per-100 mAs normalisation insight: bladder -8%, RBM ~4x low)
- [ ] 5.4 quality gates (ruff/mypy/pytest) + commit/push
