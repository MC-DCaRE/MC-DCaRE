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

**Amended 2026-08-18 (absolute-kerma round):** the profile result above is
*wedge-shape only*. The follow-up absolute tests qualify the asset more
precisely: the off-axis wedge is correct (HVL(Z) matches measurement within
0.3-0.5 mm Al at |Z| >= 7 cm; see the wedge-map section), but the **central
~5 cm plateau is ~5-6x under-thick** (STL CAX chord 1.48 mm Al vs ~8.3 mm
Al-eq measured), and the MC absolute fluence scale is 3-10x high. The TsCAD
adoption stands relative to legacy (which has the same central deficit), but a
corrected central slab + DCF re-calibration is the follow-up.

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

## CAX HVL validation (both fan models, 2026-08-18)

The MC **CAX energy spectrum** is scored by a `Fluence` scorer on a 1x0.01x1 cm
air slab at the isocenter bow-tie axis (`CaxSlab` in the `validate_bowtie`
block), binned in 150 x 1 keV bins (underflow/overflow/no-track columns
excluded). `tools/compute_cax_hvl.py` folds it with NIST mu_en/rho(air) +
mu/rho(Al) (`data/nist/hvl_coefficients.dat`) via
`PhaseSpaceAnalyzer.compute_hvl_mm_al`. All runs: 8M histories, static beam,
TsCAD = `bowtie_ff.txt`/`bowtie_hf.txt`, legacy = `fullfan.txt`/`halffan.txt`.

**Full Fan (Head, 100 kV; measured RaySafe CAX HVL = 7.37 mm Al):**

| model | MC CAX HVL (mm Al) | diff vs measured | verdict (~0.5 tol) |
|---|---|---|---|
| **TsCAD STL** | **7.80** | **+0.43** | **pass** |
| legacy CSG | 8.26 | +0.89 | fail |
| no bow-tie (control) | 7.96 | +0.59 | -- |
| source spectrum (SpekPy, pre-filtration-geometry) | 3.73 | -- | -- |

**Half Fan (Pelvis, 125 kV; measured CAX HVL = 8.06 mm Al, itself
"interpolated from meas" in the workbook):**

| model | MC CAX HVL (mm Al) | diff vs measured |
|---|---|---|
| **TsCAD STL (crop)** | **8.96** | **+0.90** |
| legacy CSG | 9.34 | +1.28 |
| no bow-tie (control) | 8.90 | +0.84 |
| source spectrum (SpekPy) | 4.69 | -- |

**Interpretation.** The bow-tie's CAX thin spot contributes almost nothing to
the CAX HVL (FF: TsCAD is 0.16 mm *below* the no-bowtie control -- a
scatter-softening effect; HF: +0.06). The hardening budget is dominated by the
base filtration: SpekPy hybrid spectrum (3.73 / 4.69 mm Al at 100 / 125 kV)
plus the geometric 0.89 mm Ti BHF, which carries the CAX HVL to ~7.9 / ~8.9.
The legacy CSG runs hot on both fans because its central `DemoFlat` (~1 mm Al
flat piece) adds real CAX thickness the measured filter does not have.

So: **TsCAD is correct on both fan models** -- FF within the ~0.5 mm Al
tolerance; HF closest of all models, with the +0.90 residual attributable to
the base-filtration model (inherent-Al estimate + 0.89 mm Ti BHF thickness),
not the bow-tie asset, per the no-bowtie controls. Tightening the HF residual
means revisiting the BHF thickness / SpekPy inherent filtration (and noting the
HF measured reference is interpolated), not the STL.

Spectra: `profiles/cax_spectrum_<tscad|legacy|nobtie>_<ff|hf>.csv`.
Reproduce: `run_simulation.py run configs/validate_bowtie_<model>[_hf].yaml`
then `tools/compute_cax_hvl.py runfolder/<ts>/cax_spectrum.csv`.

### Literature anchor: measured TrueBeam HVL1 (Gros et al. 2025)

Gros et al. (arXiv:2502.01509, Table 2) measured first HVLs on a TrueBeam OBI
with the Ti beam-hardening filter **and** bow-tie in the beam at maximum
collimation:

| Protocol | kVp | Filter | HVL1 (mm Al) |
|---|---|---|---|
| Head | 100 | Ti + Full Fan | 7.5 |
| Pelvis / Thorax | 125 | Ti + Half Fan | 8.35 |
| Spotlight | 125 | Ti + Full Fan | 8.48 |
| Large Pelvis | 140 | Ti + Half Fan | 8.93 |

Our RaySafe Head-FF CAX measurement (7.37 mm Al) agrees with their Head value
to within 2%. These four values are the comparison targets for the Phase 2 CAX
spectrum scorer; note the hybrid SpekPy spectrum (uniform filtration only, no
geometric Ti BHF/bow-tie) sits at 4.69 mm Al at 125 kV, so the remaining
hardening must come from the geometric filters, not the spectrum model.

## Absolute CAX kerma + Ti-BHF bracketing (2026-08-18)

New tooling: `tools/compare_cax_kerma.py` (canonical normalization via
`compute_photons_per_mAs` + `raw_absolute_dose_Gy`), anchors in
`data/measured/cax_kerma_anchors.yaml` (with provenance; the 120 kV 6.523-unit
block and the 80 kV HVL are flagged/excluded). New config toggle:
**`imaging.bhf_mode`** — `spekpy` (default since 2026-08-18; Ti folded into the
source spectrum via `s.filter("Ti", mm)`, no TsBox, so mm means mm with no
TOPAS half-length ambiguity, marginally faster) vs `geometric` (physical Ti
TsBox; the full-geometry validation toggle). Zero thickness (Ti-out) is also
valid (geometric only).

**Ti-BHF bracketing, 100 kV no-bow-tie (measured HVL 5.04 mm Al, TF 4.7,
kerma 112.8 uGy @ 1.6 mAs; Ti state of the measurement unstated):**

| Ti arm | HVL mm Al | diff | CAX kerma uGy |
|---|---|---|---|
| geometric HLZ=0.89 = **1.78 mm physical** (production default) | 7.96 | +2.92 | 358 |
| geometric HLZ=0.445 = 0.89 mm physical | 6.29 | +1.25 | 583 |
| **spekpy 0.445 mm** | **4.85** | **-0.19** | 850 |
| spekpy 0.89 mm | 6.13 | +1.09 | 597 |
| Ti out | 2.99 | -2.05 | 1503 |

Findings:
1. **TOPAS `HLZ` is a half-length**: the production default renders
   1.78 mm of Ti, twice the intended 0.89. Equal-physical-thickness arms agree
   across modes (6.29/583 geometric vs 6.13/597 spekpy), validating the toggle
   and confirming the factor-2.
2. The measured no-bow-tie HVL (5.04) is bracketed by Ti-out (2.99) and the
   1.78 mm default (7.96); the spekpy-0.445 arm matches to -0.19 mm Al. Either
   the measurement was taken with a thin/absent BHF state, or the effective
   base filtration differs from the model by ~1 mm Al eq.
3. **Absolute kerma is 3-7x HIGH on every arm** (e.g. best-HVL arm 850 vs
   112.8 measured): the `photons_per_mAs` fluence scale overestimates the true
   tube output. The CTDI DCF absorbs this for calibrated dose, but any
   un-normalised absolute quantity is biased. Candidate follow-up: re-anchor
   `spectrum_fluence_photons_per_mAs` to the measured free-in-air kerma.
4. **Bow-tie CAX transmission: MC 0.899 vs measured 0.523 (Head FF, both-Ti-in
   pair, common-mode-free).** The TsCAD STL central region is ~1.7x too
   transparent. This was invisible to the peak-normalised profile comparison;
   the STL likely needs central thickness added (the legacy CSG's `DemoFlat`
   ~1 mm Al central piece is consistent with the real filter having a
   non-trivial CAX thickness).

Configs: `configs/validate_kerma_*.yaml`. Switching `bhf_mode` or thickness
changes the beam spectrum and requires re-running the CTDI DCF calibration.

### Why the CAX transmission is 0.899 despite an acceptable HVL

HVL and transmission are independent observables: HVL is a *normalised
spectral-shape* metric (which half-attenuates the beam in Al), transmission is
a *magnitude* metric (how much kerma survives). Our with-bow-tie HVL agreement
(7.80 vs measured 7.37) is real but **degenerate** — it results from error
cancellation: the base filtration over-hardens (no-bow-tie HVL 7.96 MC vs 5.04
measured) while the bow-tie under-attenuates, and the two errors partially
cancel in the with-bow-tie spectrum. The transmission test breaks the
degeneracy. The quantitative chain (all arms consistent):

| quantity | value | implies |
|---|---|---|
| STL CAX chord (ray-cast, watertight) | **1.48 mm Al** | spectral fold -> T = 0.85-0.90 |
| MC bt/nobt transmission (Ti-in pair) | 0.899 | ~1.0-1.5 mm effective: transport consistent with the mesh |
| measured CAX TF (RaySafe TF column) | 13 mm Al (base 4.7) | **~8.3 mm Al-eq of real central bow-tie material** -> T = 0.52 |
| measured bt/nobt | 0.523 | confirms ~6-8 mm Al-eq |

So the TsCAD STL central region is **~5-6x too thin** (1.48 vs ~8.3 mm Al-eq).
Crucially, the original Inbum scan (`research/Monte Carlo Stuff from
Inbum/bowtie.stl`) has the *same* 1.48 mm CAX chord — the processing pipeline
is faithful; the source scan itself lacks the central material (likely a
scan/segmentation artifact at the wedge minimum). Off-axis the asset is about
right: the chord ramps 1.5 -> 4 -> 11 -> 28 mm at Z = 0/5/10/20 mm, matching
the measured edge HVL (~10 mm Al at iso +/-12-14 cm). This is exactly why the
peak-normalised profile comparison passed (RMS 0.078): normalising at the peak
divides out the central deficit, and the wedge *shape* (edges) is correct.

**Legacy corroboration:** the legacy CSG's wedges are entirely commented out
in `fullfan.txt` — the only live central element is the `DemoFlat` slab
(HLX = 1 mm half-length -> 2.0 mm Al), predicting T = 0.811. So both prior
bow-ties under-attenuate the CAX by a similar factor, which is why the TsCAD
and legacy DCFs came out nearly equal, and why the "legacy is flat" profile
behaviour was observed (it is literally a flat slab, no wedge).

**Consequence / follow-up:** composite the STL with a central Al slab (or
re-source the scan) to bring the CAX to ~8.3 mm Al-eq, then re-run the profile
+ HVL + transmission validation and the full DCF calibration. This is a
candidate contributor to the residual effective-dose gap (the CAX fluence
entering the phantom is over-weighted ~1.7x at the beam centre).

## HVL(Z) wedge map (2026-08-18)

Energy-resolved Z profile (config `validate_bowtie_hvlmap_tscad.yaml`: the
`validate_bowtie` slab with `ZBins=40 x EBins=150 x 1 keV`, wide field),
each Z row folded with NIST Al by `tools/compute_hvl_map.py`. The tool also
computes a **geometry-only prediction** (scored no-bow-tie spectrum folded
through the STL ray-cast chord at the corresponding bow-tie-plane position,
magnification 0.18) -- if the MC matches this prediction, transport is
consistent with the mesh and any residual is the asset itself.

| Z (cm) | MC HVL | measured | STL ray-cast pred |
|---|---|---|---|
| -0.5 | 5.74 | 7.37 | 6.14 |
| 0.5 | 5.62 | 7.37 | 6.14 |
| 4.5 | 7.27 | 7.81 | 7.84 |
| 6.5 | 8.25 | 8.48 | 9.09 |
| 7.5 | 9.00 | 9.42 | 9.43 |
| 9.5 | 9.57 | 9.65 | 9.70 |
| 11.5 | 9.22 | 9.81 | 9.70 |
| 13.5 | 9.49 | 9.98 | 9.70 |

(The Z=5.5 row is a ramp-boundary artefact; full table in the runfolder's
`hvl_map.csv`, plot in `hvl_map.png`.)

**Verdict:** off-axis (|Z| >= 7 cm) the MC wedge matches measurement to
0.3-0.5 mm Al -- the wedge *shape* is right. The central plateau is short
(5.6 vs 7.37), and the ray-cast prediction tracks the MC closely across the
whole wedge, confirming transport == geometry: the deficit is in the asset's
central thickness, not the simulation. This spatially localises the
transmission finding and closes the sharpest open bow-tie test.

## Per-protocol absolute free-in-air kerma vs Gros 2025 (2026-08-18)

CAX kerma per mAs from the five clinical-field TsCAD arms
(`tools/compare_cax_kerma.py`), scaled to each protocol's technique mAs and
compared to Gros et al. 2025 (arXiv:2502.01509) Farmer free-in-air Kair:

| protocol | MC uGy/mAs | MC @ mAs (mGy) | Gros Kair (mGy) | ratio |
|---|---|---|---|---|
| Head (100 FF) | 201 | 30.2 | 5.3 | 5.7x |
| Thorax (125 HF) | 575 | 154.4 | 17.8 | 8.7x |
| Pelvis (125 HF) | 397 | 426.0 | 64.3 | 6.6x |
| Pelvis Large (140 HF) | 758 | 1289.1 | 132.0 | 9.8x |
| Spotlight (125 FF) | 575 | 432.3 | 44.7 | 9.7x |

**Findings.** (1) Every protocol is high by 5.7-9.8x, re-confirming the
`photons_per_mAs` fluence-scale bias already measured against the RaySafe
per-frame anchors (5-7x there) -- an independent group's measurements agree
with our own machine's, so the bias is in the MC normalization chain, not the
references. (2) The bias is *not* perfectly constant (23% spread; lowest for
Head FF at 5.7x, highest for the 140 kV and Spotlight protocols at ~9.8x).
A single global fluence rescale would leave this residual protocol dependence
behind, so at least one further kV/filtration-dependent error rides along
(candidates: the over-hard base filtration model, the under-thin STL centre,
or SpekPy output scaling with kV). Disentangling needs the fluence re-anchor
first. (3) Thorax (HF) and Spotlight (FF) give identical CAX kerma per mAs
(575.2) -- expected: the HF STL is a lateral crop of the FF, so both share
the same thin-spot geometry and spectrum at the exact CAX; a useful internal
consistency check.

## Measured fluence anchor (2026-08-18, post blade fix)

The absolute fluence scale is now anchored to measurement:
`imaging.fluence_anchor = measured` (default; `model` keeps the raw SpekPy
isotropic inflation for auditing) scales `no_particles` in
`SpectrumGenerator` by a per-kV factor from
`data/measured/fluence_anchors.yaml`, recorded in run metadata.

**Derivation** (with-bow-tie, spekpy Ti, clinical fields, 1.6 mAs anchors):
F(100) = 59.01/551.6 = **0.1070** (Head FF); F(125) = mean(106.3/989.4,
107.1/990.3) = **0.1077** -- <1% spread across two kV and both fans, i.e. a
single multiplicative bias (SpekPy tube-output normalization + 4*pi isotropic
inflation at z=10 cm), no longer protocol-dependent after the rectangular
blade fix. Option-A anchoring: the with-BT factors absorb the (accepted)
under-thin STL centre into an effective fluence, mirroring the DCF philosophy;
no-bow-tie arms read ~1.7x low at the CAX by construction.

**Verification:** the Head anchor arm re-run with the anchor closes to
59.0 vs 59.01 uGy (ratio 1.000). Independent check vs Gros 2025 Kair
(all five protocols re-run post-fix, anchored):

| protocol | MC @ mAs (mGy) | Gros Kair (mGy) | ratio (was, pre-fix) |
|---|---|---|---|
| Head | 5.5 | 5.3 | 1.05 (5.7x) |
| Thorax | 17.9 | 17.8 | 1.01 (8.7x) |
| Pelvis | 71.6 | 64.3 | 1.11 (6.6x) |
| Pelvis Large | 149.1 | 132.0 | 1.13 (9.8x) |
| Spotlight | 50.1 | 44.7 | 1.12 (9.7x) |

The prior 5.7-9.8x bias is gone; the residual +10-13% on body modes vs
+1-5% on head/thorax is the remaining small systematic (candidates: off-axis
wedge detail, technique-generation differences between machines -- Gros
themselves report machine-to-machine spread of this order). Note the DCFs in
`calibration.yaml` (2026-08-14) predate the blade fix AND the anchor and are
stale for absolute work until re-calibrated.

## Final outcome (post re-calibration, 2026-08-14/18)

(6 protocols, `calibration.yaml` date_calibrated 2026-08-14: dcf_tle 80 FF
0.20361, 100 FF 0.19744, 125 FF 0.19097, 125 HF 0.26365, 140 HF 0.27683).

**Pelvis phantom (MRCP-AM, 150M hist): E = 3.09 mSv (TLE)** vs 4.2 PCXMC
(-26%) / 5.4 Hauri (-43%). Dominant contributor: bladder (28 mSy organ, 1.12
mSv weighted of the 3.09 total).

Full-protocol sweep (5M hist/protocol, `scripts/run_edose_validation.py` ->
`edose_validation_runs/validation_results.csv`), direct-beam voxel-phantom
runs at **region-specific isocenters** (MRCP-AM organ centroids, same
placement as the 2026-08-13 replay study: pelvis 0, abdomen 200, spine 300,
thorax 460, neck 600, head 795 mm; the swapped `phantomVoxel.txt` TransZ is
patched per run):

| Protocol | kV | Fan | mAs | E_sim (mSv) | E_ref (mSv) | Diff |
|---|---|---|---|---|---|---|
| 4D Spotlight | 125 | FF | 373.6 | 3.12 | 1.6 | +95.0% |
| 4D Thorax | 125 | HF | 671.2 | 5.09 | 3.3 | +54.2% |
| Abdo Spotlight | 125 | FF | 400.8 | 1.21 | 1.2 | +0.8% |
| Abdomen | 125 | HF | 716.0 | 3.23 | 2.8 | +15.4% |
| Breast 360 | 125 | HF | 89.5 | 0.68 | 0.2 | +240.0% |
| Extremity Spotlight | 100 | FF | 150.3 | 0.23 | 0.5 | -54.0% |
| Head | 100 | FF | 150.3 | 0.30 | 0.5 | -40.0% |
| Head and Shoulders | 125 | HF | 268.5 | 2.19 | 0.3 | +630.0% |
| Head SRS | 100 | FF | 537.0 | 1.06 | 1.8 | -41.1% |
| Pelvis | 125 | HF | 1074.0 | 3.04 | 4.2 | -27.6% |
| Pelvis Spotlight | 125 | FF | 751.5 | 2.01 | 2.2 | -8.6% |
| SBRT Spine | 125 | HF | 358.0 | 3.78 | 1.7 | +122.4% |
| Thorax | 125 | HF | 268.5 | 2.04 | 1.3 | +56.9% |
| Thorax Spotlight | 125 | FF | 150.3 | 1.26 | 0.7 | +80.0% |

Isocenter placement dominates the head/thorax/abdomen results: with all
protocols at the pelvis isocenter (first sweep) thorax modes read ~-42%; at
the correct thorax isocenter they read +54-57%, bracketing the reference.
Head protocols read -40..-54% vs the manufacturer PCXMC table at any
placement, but the **Head result (0.30 mSv at 150.3 mAs) agrees with the
independent Abuhaimed 2018 EGSnrc MC (0.32 mSv at 150 mAs, ICRP male) to
within 6%** -- evidence the simulator itself transfers, and that the
manufacturer PCXMC head reference (0.5 mSv) sits high. Similarly our Pelvis
(3.04) sits between the PCXMC (4.2) and Hauri TLD (5.4) anchors and below the
Abuhaimed pelvis MC (7.05); the pelvis literature spread is wide (see table
above). Breast 360 and Head and Shoulders remain extreme outliers (+240% /
+630%) -- both were already flagged as suspicious references in the
2026-08-13 study. Pelvis-family protocols are isocenter-invariant (Z=0), so
the bowtie-era conclusions (FF body modes closed: Pelvis Spotlight -8.6%,
Abdo Spotlight +0.8%) stand unchanged.

## Literature comparison

### Protocol dosimetry: Gros et al. 2025 vs this machine

Gros S. et al., *Proposal and Evaluation of a Practical CBCT Dose Optimization
Method*, arXiv:2502.01509 (2025): Farmer-chamber free-in-air kerma (Kair) and
pencil-chamber CBDI/CBDIw in CTDI phantoms for five default TrueBeam OBI
protocols. Their default techniques match this machine's protocols (150/270/
1080/1688/750 mAs vs 150.3/268.5/1074/1700.5/751.5 mAs):

| Protocol | kV | Fan | Gros CBDIw (mGy) | Gros Kair (mGy) | This machine CTDIw (mGy) | Diff |
|---|---|---|---|---|---|---|
| Head | 100 | FF | 3.2 | 5.3 | 3.2 | 0% |
| Thorax | 125 | HF | 5.0 | 17.8 | 4.0 | +25% |
| Pelvis | 125 | HF | 18.1 | 64.3 | 15.9 | +14% |
| Pelvis Large | 140 | HF | 38.3 | 132.0 | 37.1 | +3% |
| Spotlight | 125 | FF | 29.7 | 44.7 | 12.3 | +142% |

Head/Pelvis/Pelvis-Large agree within 0-14% and Thorax within 25% -- good
machine-to-machine consistency, and independent confirmation that this repo's
measured_ctdi_w reference values (the DCF anchors) are representative. The
Spotlight outlier (+142%) suggests a different Spotlight technique generation
between the two machines; this machine's 12.3 mGy chamber measurement is what
the 125 FF DCF is anchored to and is retained.

### Per-100 mAs benchmark (Abuhaimed & Martin 2023 BMI library)

`data/literature/abuhaimed2023_tables.yaml` (Tables 2-3, full BMI classes)
+ `tools/compare_abuhaimed2023.py` normalise our sweep to mSv/100 mAs. On the
current (pre-blade-fix, pre-anchor) sweep the ratios are Thorax 0.37 and
Pelvis 0.24 vs their all-size 2.07 / 1.19 mSv per 100 mAs -- consistent with
the documented residual gap; the organ-level table (bladder vs RBM
localisation) attaches once the post-recalibration sweep lands. Caveats: their
120 kV vs our 125 kV (per-100 mAs removes mAs, not kV) and OBI-generation
differences. The BMI-class columns are staged for the phantom-library change
(size-specific dosimetry).

### Effective dose: MC and measurement literature vs this work

Published TrueBeam-OBI-class effective doses (male phantoms, default
techniques):

| Source | Method | Head | Thorax | Pelvis |
|---|---|---|---|---|
| **This work** (TsCAD, 5M hist, MRCP-AM) | TOPAS MC + own-CTDIw DCF | 0.30 | 2.04 | 3.04 |
| Abuhaimed & Martin 2018 (OBI V2.5, ICRP male) | BEAMnrc/DOSXYZnrc MC | 0.32 | 3.92 | 7.05 |
| Martin & Abuhaimed 2022 (SED, male phantoms) | MC review | -- | 3.8-7.6 | 11-22 |
| Abuhaimed & Martin 2023 (BMI phantom library) | MC, mSv/100 mAs | -- | -- | 0.85-1.53 per 100 mAs (9.1-16.4 at 1080 mAs) |
| Marchant & Joshi 2017 (Elekta XVI range, cited in the two papers above) | MC | 0.03-0.09 | 0.64-7.88 | 0.16-7.60 |
| Manufacturer table (this repo E_ref) | PCXMC | 0.5 | 1.3 | 4.2 |
| Hauri et al. 2017 | TLD, Alderson phantom | -- | -- | 5.4 |

References:

- Abuhaimed A, Martin CJ, Sulieman A. *A Monte Carlo study of organ and
  effective doses of cone beam computed tomography scans in radiotherapy.*
  J Radiol Prot 38(1):61-79 (2018). V2.5 male values; head 0.32, thorax 3.92,
  pelvis 7.05 mSv at 150/270/1080 mAs. V2.5 organ detail for context: bladder
  51.4 mGy, prostate 39.3 mGy (pelvis protocol).
- Martin CJ, Abuhaimed A. *Variations in size-specific effective dose with
  patient stature and beam width for kV cone beam CT imaging in radiotherapy.*
  J Radiol Prot 42:031512 (2022).
- Abuhaimed A, Martin CJ. *Assessment of organ and size-specific effective
  doses from cone beam CT (CBCT) in IGRT based on body mass index (BMI).*
  Radiat Phys Chem 208:110889 (2023).
- Gros S, Bian J, Jackson J, Delafuente M, Kang H, Small W Jr, Mahesh M.
  *Proposal and Evaluation of a Practical CBCT Dose Optimization Method.*
  arXiv:2502.01509 (2025).

The literature E spread for pelvis (4.2 PCXMC / 5.4 TLD / 7.05-22 MC / 0.16-7.6
XVI range) is wide -- protocol version, scan-length, phantom and E-convention
differences all contribute. MC-DCaRE's simulated values should be judged against
this spread, not a single number.

## Phase-0 transfer analysis (2026-08-18, post blade fix + masks + anchor)

Full 14-protocol sweep on the complete new beam model (rectangular blades +
primary masks + spekpy Ti + measured anchor, 2026-08-18 DCFs; 10M hist/protocol,
`tools/analyze_edose_transfer.py`, CSV in `edose_validation_runs/phase0_transfer.csv`).
Trusted anchors only (PCXMC carried as caveat per 2026-08-18 decision):
Abuhaimed & Martin 2023 all-size per-100 mAs (chest 2.07, pelvis 1.19),
Abuhaimed 2018 Head EGSnrc (0.32 mSv @ 150.3 mAs), Hauri 2017 pelvis TLD
(5.4 mSv), Gros 2025 iso-Kair (passes, 1.01-1.13).

| protocol | kV/fan | E new | E old | ratio | raw_ph* | /100 mAs |
|---|---|---|---|---|---|---|
| Head SRS | 100 FF | 0.61 | 1.06 | 0.57 | 0.77 | 0.113 |
| Extremity Spotlight | 100 FF | 0.09 | 0.23 | 0.37 | 0.49 | 0.057 |
| Head | 100 FF | 0.17 | 0.30 | 0.57 | 0.76 | 0.113 |
| Pelvis Spotlight | 125 FF | 1.58 | 2.01 | 0.78 | 1.39 | 0.210 |
| Abdo Spotlight | 125 FF | 1.10 | 1.21 | 0.91 | 1.61 | 0.275 |
| 4D Spotlight | 125 FF | 2.97 | 3.12 | 0.95 | 1.69 | 0.795 |
| Thorax Spotlight | 125 FF | 1.20 | 1.26 | 0.95 | 1.68 | 0.795 |
| Pelvis | 125 HF | 1.83 | 3.04 | 0.60 | 1.56 | 0.171 |
| Abdomen | 125 HF | 1.64 | 3.23 | 0.51 | 1.32 | 0.230 |
| 4D Thorax | 125 HF | 4.25 | 5.09 | 0.83 | 2.16 | 0.633 |
| SBRT Spine | 125 HF | 1.86 | 3.78 | 0.49 | 1.27 | 0.519 |
| Head and Shoulders | 125 HF | 0.88 | 2.19 | 0.40 | 1.04 | 0.328 |
| Thorax | 125 HF | 1.70 | 2.04 | 0.83 | 2.15 | 0.633 |
| Breast 360 | 125 HF | 0.57 | 0.68 | 0.83 | 2.15 | 0.633 |

\* raw_ph = unanchored raw phantom-dose transport ratio new/old
(E_ratio x DCF_old/DCF_new / anchor). Old = 2026-08-18 10:31 sweep (wedge
blades, geometric 1.78 mm Ti, no masks, no anchor, 2026-08-14 DCFs).

Findings:

1. **Not a uniform scale.** raw_ph spans 1.04-2.16 within 125 HF alone
   (2.07x spread); identical beam settings, different field/iso. The change
   is protocol-geometry-dependent, so no single renormalization fixes it.
2. **E/CTDIw transfer regression vs every absolute anchor.** Pelvis E =
   1.83 mSv vs Hauri 5.4 (-66%) / PCXMC 4.2 (-56%, caveat) while CTDIw
   matches by construction (DCF) and iso-Kair matches (Gros 1.11). Within
   the direct-beam pathway the pelvis transfer fell 3.09 -> 1.83 mSv
   (E/CTDIw 0.20 -> 0.117 mSv/mGy). The earlier 5.70 mSv (2026-08-12) is
   the phase-space replay pathway (different normalization semantics) and
   is not apples-to-apples.
3. **100 kV head regression against its matched anchor.** Old Head 0.30 vs
   Abuhaimed 2018 0.32 (+6%); new 0.17 (0.53x). raw_ph fell 24% while
   unanchored raw_CTDI rose 33% -- the two phantoms diverged in opposite
   directions at 100 kV.
4. iso-Z correlation weak (Pearson +0.33 over 125 HF), confounded by field
   size (Head and Shoulders: smallest HF field, lowest raw_ph 1.04).
5. Abuhaimed-2023 per-mAs comparison (0.14-0.67 of their values) carries an
   mAs-convention caveat: their per-mAs x our mAs = 12.8 mSv for pelvis,
   exceeding even their own 2018 absolute (7.05). Direction is consistent
   with finding 2; magnitude is not load-bearing.

Hypotheses ranked for Phase 2 (A/B Monte Carlo, DCF re-derived per variant,
`scripts/validate_pelvis_edose.py --mask-off`):
- **H1 (primary masks starve scatter)**: masks are new since the 3.09-era
  run and selectively cut wide-angle head scatter that the 179-cm human
  phantom integrates into E but the 15-cm CTDI cylinder barely sees.
  Analytic check already done: the 5.0 x 2.7 cm port clears every clinical
  blade aperture, so the primary field is intact -- only scatter is in play.
- H2 (bow-tie STL Z-dependent error): supported by the Z-gradient
  (our chest/pelvis per-mAs ratio 3.7 vs Abuhaimed 1.7), partially absorbed
  by the DCF.
- H3 (Ti 0.89 spekpy vs 1.78 geometric): spectrum softening interacts with
  mu_en/rho scoring; test via bhf_mode toggle.

