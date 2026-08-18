## Status

- [x] Phase 1: absolute CAX kerma + transmission ratios (anchors, tool, runs)
- [x] Phase 2: Ti-state bracketing + base-filtration attribution
  + NEW: `imaging.bhf_mode` toggle (geometric TsBox | spekpy-folded Ti)
- [x] Phase 3: HVL(Z) wedge map
- [x] Phase 4: Gros 2025 Kair per protocol
  + `imaging.bhf_mode` default flipped to spekpy (faster, mm=mm); geometric
    retained as the full-geometry validation toggle
- [x] Phase 5a (added): measured fluence anchor -- implemented + verified
- [x] Phase 5: literature per-100 mAs benchmarks + docs
- [x] Phase 6 (added 2026-08-18 PM): E-dose transfer analysis on the new
  beam model (14-protocol sweep, 2026-08-18 DCFs) -- `tools/analyze_edose_transfer.py`,
  Phase-0 table + findings in docs/bowtie_validation/README.md. Headline:
  pelvis E/CTDIw transfer fell 3.09 -> 1.83 mSv (vs Hauri -66%) while CTDIw
  and iso-Kair anchors hold; 100 kV head regressed vs Abuhaimed 2018
  (0.30 -> 0.17 vs 0.32); change is protocol-geometry-dependent (raw_ph
  spread 2.07x within 125 HF). Trusted anchors: Abuhaimed/Gros/Hauri;
  PCXMC demoted to caveat.
- [ ] Phase 7: hypothesis A/B experiments (DCF re-derived per variant,
  `scripts/validate_pelvis_edose.py`; mask toggle =
  `imaging.primary_mask_enabled`, default True)
  - [x] 7a mask-off (H1 confirmed) -- 2026-08-18: mask cuts 64% phantom dose,
    2% CTDI dose; mask-off E = 3.07 mSv (matches pre-mask 3.09); explains
    entire pelvis transfer regression
  - [x] 7b bowtie-off (H2 supported) -- 2026-08-19: mask-on no-bowtie
    E = 3.73 mSv (+103% vs 1.83 baseline); phantom raw +151% vs CTDI raw
    +23% -- the TsCAD bow-tie attenuates the human phantom far more than
    the CTDI cylinder; consistent with the known under-thick STL CAX
  - [x] 7c bhf geometric (H3 supported, diagnostic) -- 2026-08-19:
    mask-off + bhf-geometric E = 4.59 mSv (+50% vs 7a's 3.07); geometric
    renders 1.78 mm Ti (HLZ half-length) vs spekpy's 0.89 mm -- harder
    beam penetrates phantom better per unit CTDI. Production stays spekpy
    (HVL-validated); H3 quantifies the Ti-state transfer sensitivity
  - [x] 7d tight source cone cutoff (15/12 deg = housing-equivalent) -- 2026-08-18:
    uniform scaling, no E/CTDIw change (E = 1.84 ≈ baseline 1.83); cutoff
    ≠ mask: cutoff scales all angles equally, mask clips spatially at a
    downstream Z-plane disproportionately hitting the elongated human phantom
- [x] Phase 8: upstream housing aperture (physical fix for source sigma)
  - [x] Implement aperture TsBox: 3.5 cm SDD (Y=-96.5, only clear window
    upstream of the X-jaw boxes at Y=-95.8; 10 cm SDD overlapped Coll1),
    0.6 cm Pb walls, port 0.9 x 0.5 cm (X 14.4 deg / Z 8.1 deg), outer
    bounds match the retired mask angular cone
  - [x] Remove downstream primary mask (`primary_mask_enabled` default
    flipped to False, template block marked DEPRECATED)
  - [x] Acceptance A/B (2026-08-19): aperture-on default config
    E = 1.94 mSv, DCF 0.5910, clean run. Revises the mask story: ANY
    ~14/8-deg clipping (mask, aperture, resampled cutoff) lands at
    E 1.8-1.9 with CTDI flat -- clipping is correct (unclipped tails are
    absurd), residual -64% vs Hauri is phantom-pathway, not beam-model
  - [ ] Re-derive DCFs + full 14-protocol sweep -- overnight user-run
    (`scripts/run_full_calibration.py` + `scripts/run_edose_validation.py`,
    ~7 h)

## 5b. Measured fluence anchor (executed 2026-08-18, post blade fix)

- [x] 5b.1 derive F(kV) from with-BT anchor arms (Head 100 FF, Pelvis 125 HF,
  Spotlight 125 FF; spekpy Ti, clinical fields): F(100)=0.1070, F(125)=0.1077
  (<1% spread across kV and fan) -> data/measured/fluence_anchors.yaml
- [x] 5b.2 `imaging.fluence_anchor = measured|model` (default measured) in
  ImagingConfig + SpectrumGenerator (scales no_particles; recorded in metadata)
- [x] 5b.3 verify: Head anchor arm closes 59.0 vs 59.01 uGy (ratio 1.000);
  Gros 2025 per-protocol Kair ratios collapse 5.7-9.8x -> 1.01-1.13x
- [x] 5b.4 calibration.yaml marked stale (blade fix + anchor shift raw CTDIw);
  docs + AGENTS.md updated

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

- [x] 3.1 config + scorer: `ZBins=40 x EBins=150` energy-resolved profile (`validate_bowtie_hvlmap` flag; production profile config unchanged)
- [x] 3.2 `tools/compute_hvl_map.py`: per-Z fold -> HVL(Z) CSV + plot vs measured + STL ray-cast geometry prediction (Head FF TsCAD)
- [x] 3.3 verdict: off-axis |Z|>=7 cm matches measured to 0.3-0.5 mm Al (wedge shape correct); central plateau short (5.6 vs 7.37); ray-cast prediction tracks MC everywhere (transport == geometry). Artefacts: docs/bowtie_validation/hvl_map_tscad_ff.*

## 4. Gros 2025 Kair per protocol

- [x] 4.1 five clinical-field TsCAD runs (configs/validate_kerma_*.yaml incl. thorax_hf, pelvislarge_hf, spotlight_ff)
- [x] 4.2 all protocols 5.7-9.8x high (mean 8.1, 23% spread): confirms the fluence-scale bias against an independent group's data; Thorax/Spotlight CAX kerma identical (HF crop shares the FF thin spot -- consistency check). Table in README

## 5. Literature per-100 mAs benchmarks

- [x] 5.1 `data/literature/abuhaimed2023_tables.yaml` (Tables 2-3, full BMI classes C1-C6+All; staged for the phantom-library change)
- [x] 5.2 `tools/compare_abuhaimed2023.py` (+4 unit tests): E per 100 mAs vs tables (stale-sweep ratios Thorax 0.37 / Pelvis 0.24); organ-level table attaches post-recalibration
- [x] 5.3 docs: per-100 mAs subsection added to Literature comparison (kV caveat noted)
- [x] 5.4 quality gates (ruff/mypy/pytest) + commit/push (613 tests green)
