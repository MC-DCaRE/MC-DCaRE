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

## Final outcome (post re-calibration, 2026-08-14/18)

Adopted TsCAD (`legacy_bowtie=False` default), full DCF re-calibration at TsCAD
(6 protocols, `calibration.yaml` date_calibrated 2026-08-14: dcf_tle 80 FF
0.20361, 100 FF 0.19744, 125 FF 0.19097, 125 HF 0.26365, 140 HF 0.27683).

**Pelvis phantom (MRCP-AM, 150M hist): E = 3.09 mSv (TLE)** vs 4.2 PCXMC
(-26%) / 5.4 Hauri (-43%). Dominant contributor: bladder (28 mSy organ, 1.12
mSv weighted of the 3.09 total).

Full-protocol sweep (5M hist/protocol, `scripts/run_edose_validation.py` ->
`edose_validation_runs/validation_results.csv`), new-vs-old diff vs reference:

| protocol | legacy diff | TsCAD diff |
|---|---|---|
| Pelvis Spotlight (FF) | -65% | **-9%** |
| Abdo Spotlight (FF) | -56% | **-11%** |
| Pelvis (HF) | -54% | -28% |
| Abdomen (HF) | -62% | -28% |
| Thorax (HF) | 0% | -42% |
| Head / SRS / Extremity (FF) | -84..-88% | -56..-57% |
| Head and Shoulders | +140% | +153% |

The FF body modes closed almost entirely; a consistent residual ~-28..-56%
remains across modes. Since the bow-tie is measured-validated and the DCFs are
fresh, that residual is systematic elsewhere (spectrum fidelity vs TrueBeam,
PCXMC reference provenance, or the CTDI->phantom DCF transfer) -- follow-up
work, not a bow-tie issue.

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

### Effective dose: MC and measurement literature vs this work

Published TrueBeam-OBI-class effective doses (male phantoms, default
techniques):

| Source | Method | Head | Thorax | Pelvis |
|---|---|---|---|---|
| **This work** (TsCAD, 5M hist, MRCP-AM) | TOPAS MC + own-CTDIw DCF | see sweep table below | " | " |
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
