# Comparative Analysis: PCXMC Research vs MC-DCaRE Implementation

A physics, systems, implementation, and gap analysis comparing the historical PCXMC-based CBCT dosimetry workflow (in `research/`) against the current MC-DCaRE codebase (`src/`).

**Date:** 2026-08-13
**Scope:** `research/2023 - CBCT Dose PCXMC/`, `research/2023 - CBCT Mode Standardisation/`, and the MC-DCaRE `src/` tree.

---

## 1. Executive summary

Two fundamentally different paradigms produce the same nominal quantity (ICRP 103 effective dose, mSv) for the same Varian TrueBeam CBCT modes:

```
  PCXMC research path                         MC-DCaRE path
  ───────────────────                         ────────────
  measured air kerma ──┐                   SpekPy spectrum
  + bow-tie sub-fields │                        │
  + gantry angles      ├──▶ PCXMCInput ──▶  TOPAS/Geant4
  + ellipsoidal phantom│                    (matrix paste)    explicit transport
                       │                         │                  │
                       ▼                         ▼                  ▼
                 PCXMC 2.0 (proprietary)    phase-space/TLE    voxelized phantom
                 kernel superposition       + DTM scorers       + ICRP 103
                 (Cristy-Eckerman math      CTDI-derived DCF    effective dose
                  phantom, CPE implicit)
                       │                                            │
                       ▼                                            ▼
              E (mSv) ────────────── both stored in ──────────▶ E (mSv)
                 Pelvis 4.2          calibration.yaml          Pelvis ~5.5
                 Thorax 1.3          effective_dose_refs       (TLE 5.70 / DTM 5.46)
                 Head 0.5
```

**Key findings:**

1. The PCXMC research code is a **geometry/input generator**, not a dose engine — the dose arithmetic lives in proprietary STUK PCXMC 2.0 (§2). MC-DCaRE replaces the entire pipeline with open, auditable Geant4 transport.
2. MC-DCaRE's full-MC effective dose for the 125 kV half-fan pelvis phantom (TLE 5.70 / DTM 5.46 mSv) lands between the PCXMC reference (4.2), the Hauri 2017 TLD literature value (5.4), and Abuhaimed 2018's ICRP-110 BEAMnrc value (M 6.05 / V2.5 7.05) — physically credible (§5).
3. MC-DCaRE is currently **benchmarked against PCXMC-derived E values** that came from a mathematical phantom with implicit CPE. This is a weaker anchor than the available independent full-MC literature (Abuhaimed 2018, Gilling 2019, Marchant 2017) — recommendation R3.
4. The highest-value gaps are: **paediatric phantoms** (PCXMC has 6 age groups; MC-DCaRE is adult-focused), **bow-tie validation against the measured profiles sitting unused in this very research folder**, and **heel-effect / spectrum-HVL validation** (§6).

---

## 2. The two paradigms

### 2.1 PCXMC: kernel superposition on a mathematical phantom

PCXMC (STUK, Tapiovaara & Siiskonen 2008) pre-computes, once, the **mean absorbed energy per photon per organ** (stored in `.en2` files inside the proprietary app) for a set of Cristy-Eckerman 1987 hermaphroditic mathematical phantoms (6 age groups, 29 organs). For any later exam it rescales these kernels by the user-supplied incident air kerma and spectrum. CBCT is not native to PCXMC — the Fetin/Cartwright workaround (`PCXMCStuff/PCXMC_Code/Main.m`, `Fetin2022_Article_...pdf`):

- decomposes the bow-tie into 4-15 lateral **sub-fields** of constant kerma/filtration,
- samples the gantry arc at 8 discrete **projections** (summing to 360°),
- clips each sub-field to the 2D ellipsoidal phantom cross-section,
- emits a 20-column `PCXMCInput` matrix that a human pastes into PCXMC's Excel front-end.

**The committed MATLAB/Python code stops at the matrix.** No dose, no organ sum, no effective dose, no CTDI is computed in any source file (confirmed by grep for `kernel|organ|effective|ICRP|weighting` → 0 matches). Effective doses in `TrueBeamCBCTmodes.xlsx` were produced by running PCXMC 2.0 manually.

Strengths: fast (kernels pre-computed); broad paediatric coverage (6 ages × many sizes); established STUK validation.
Weaknesses: mathematical phantom (no real anatomy heterogeneity); uniform-field-per-subfield bow-tie approximation; CPE implicit in kernels; proprietary, unauditable; manual handoff; no scatter outside the kernel's pre-computed geometry.

### 2.2 MC-DCaRE: explicit Monte Carlo transport

MC-DCaRE runs OpenTOPAS 4.2.p3 / Geant4 11 (`g4em-standard_opt4`, EMRange 100 eV–1 MeV) with three source/geometry modes:

- **CTDI mode** — beam or phase-space source → PMMA CTDI phantom (16/32 cm) with 5 chamber plugs scored simultaneously via LayeredMassGeometry parallel worlds; TLE (primary), DTM, DTW scorers; computes CTDIw via MEAN of per-bin doses.
- **DICOM mode** — voxelized `TsDicomPatient`, Schneider HU→material, DoseToMedium DICOM output.
- **Phantom mode** — ICRP 145 (mesh via `TsTetGeom`, broken → voxelized fallback) for organ dose + ICRP 103 effective dose.

Calibration: a CTDI-derived DCF (`dcf = measured_CTDIw / simulated_CTDIw`) transfers from the standard phantom to the patient via `raw_absolute_dose_Gy × DCF` (`src/services/calibration.py:92-125, 374`). CBCT rotation via TOPAS time features (`NumberOfSequentialTimes`, linear `RotZ`).

Strengths: explicit physics (no kernel/CPE assumption); real voxelized anatomy; fluence-based TLE (every photon scores, good statistics); phase-space replay decouples source from patient scoring; open and auditable; automated end-to-end.
Weaknesses: slow (full transport); adult-focused; bow-tie/blade coefficients unvalidated; heel effect absent in Beam source; phase-space replay has open bugs (§6).

---

## 3. Physics modelling comparison

| Dimension | PCXMC research | MC-DCaRE | Notes |
|---|---|---|---|
| **Transport** | None in committed code; PCXMC 2.0 proprietary MC kernels | Geant4/TOPAS `em-standard_opt4`, explicit | MC-DCaRE is auditable; PCXMC is a black box |
| **Phantom** | Cristy-Eckerman mathematical, 6 ages, hermaphroditic, ellipsoid cross-section | Voxelized DICOM patient; ICRP 145 mesh (broken→voxel); CTDI PMMA | PCXMC covers paediatrics MC-DCaRE lacks (§6 G1) |
| **Bow-tie filter** | Discrete sub-fields (4-15) of constant kerma/filtration (no geometry) | Static Al wedges: `fullfan.txt`/`halffan.txt`, Ti 0.7 mm BHF | Both approximate; MC-DCaRE's coefficients unvalidated (§6 G4) |
| **Heel effect** | Not modelled | Not modelled (Beam source = Gaussian focal spot) | Marchant 2017 models it; both omit it (§6 G5) |
| **Spectrum** | Measured HVL → total filtration via Siemens tool → PCXMC spectrum | SpekPy `kvp/th=14°/dk=0.2`; filtration is geometric, not in spectrum | MC-DCaRE can validate SpekPy HVL vs measured (§6 G6) |
| **CBCT rotation** | 8 discrete projections summed (uniform angle) | TOPAS Linear time feature, `NumberOfSequentialTimes` (default ~36-1000 sub-runs) | Both uniform; Marchant shows real trajectory is non-uniform |
| **Partial arc** | `startingAngle`/`finalAngle`, any arc | Linear time feature Rate/StartValue; kV-kV = Step (2 angles) | MC-DCaRE supports kV-kV planar PCXMC doesn't |
| **Scatter** | Implicit in kernels (pre-computed geometry only) | Fully transported | MC-DCaRE captures patient scatter PCXMC cannot |
| **CPE** | Implicit in kernels (TLE-equivalent) | TLE assumes CPE; DTM scores actual deposition; agree within 4% | MC-DCaRE can test where CPE fails |
| **Scorers** | Single organ-energy kernel | TLE (kerma), DTM (collision), DTW (water), phase-space | MC-DCaRE cross-validates 3 ways |
| **Tissue weighting** | ICRP 60/103 selectable in PCXMC GUI | ICRP 103 hardcoded (`src/models/icrp103.py`) | PCXMC offers ICRP 60; MC-DCaRE does not |
| **Charged particle range** | PCXMC internal | ECUT-equivalent via EMRangeMin 100 eV | Adequate for ≤140 kV |
| **Couch** | Not in PCXMC input | Al `TsBox` (CTDI/Phantom only; absent in DICOM mode) | Al over-attenuates kV; documented approximation (§6 G9) |

---

## 4. Systems / architecture comparison

| Dimension | PCXMC research | MC-DCaRE |
|---|---|---|
| **Pipeline** | MATLAB → manual paste → PCXMC GUI → manual result sum | `Orchestrator` → mode → Jinja2 render → `SimulationRunner` → post-process services; fully automated |
| **Config** | Hardcoded MATLAB vars / `protocol_config.m` | `SimulationConfig` frozen dataclass + 47-preset lookup (`imaging_mode.py`) + YAML |
| **Mode coverage** | ~18 modes run ad-hoc | 47 presets (20 CBCT-CW + 20 CCW + 7 kV-kV) |
| **Calibration** | None (PCXMC consumes air kerma directly) | CTDI-derived DCF, per-scorer (`dcf_tle`/`dcf_water_dtm` populated; `dcf_dtw`/`dcf_dtm` not) |
| **Effective dose** | Manual (PCXMC output) | `PhantomDoseCalculator` automated, ICRP 103, selection-bias-fixed |
| **CTDI** | Not computed (input only) | `CTDICalculator` (MEAN-of-bins, matches pencil chamber) |
| **Reproducibility** | Poor (manual handoff, per-protocol `Main_*.m` sprawl) | Strong (timestamped runfolders, provenance YAML, logs) |
| **Validation artifacts** | Excel result sheets, `.docx` notes | `BenchmarkCalculator` (PASS/FAIL 10% vs reference), `PhaseSpaceAnalyzer` |
| **Test coverage** | Python: 11 geometry tests (passing) + broken main tests | pytest unit/smoke/integration suite |

**Implementation quality:** The Python refactor (`pcxmc_py_refactor/`) is incomplete and buggy (2 geometry bugs, broken imports, overstates its own status in `REFACTOR_STATUS.md`). It is not a viable dose engine and should not be revived. MC-DCaRE's codebase is substantially more mature: typed dataclasses, strategy-pattern modes, centralized normalization, auditable calibration provenance.

---

## 5. Reference dose cross-check

Effective dose (mSv) for Varian TrueBeam/OBI CBCT, adult phantom. MC-DCaRE value is the 125 kV half-fan pelvis phantom (TLE 5.70 / DTM 5.46, from `src/AGENTS.md`).

| Source | Method | Head | Thorax | Pelvis | Notes |
|---|---|---|---|---|---|
| **PCXMC (this research, `TrueBeamCBCTmodes.xlsx`)** | Kernel superposition, math phantom | 0.5 | 1.3 | 4.2 | Stored as MC-DCaRE `effective_dose_references` |
| **MC-DCaRE (current)** | TOPAS full MC, voxelized pelvis | – | – | 5.5–5.7 | TLE/DTM 4% agreement |
| **Hauri 2017** (cited in `src/AGENTS.md`) | TLD, Alderson phantom | – | – | 5.4 | Physical measurement |
| **Abuhaimed 2018** | BEAMnrc/DOSXYZnrc, ICRP-110 | M 0.28 / F 0.45 | M 3.34 / F 3.97 | M 6.05 / F 11.30 | V1.6; V2.5 ~14-18% higher |
| **Gilling 2019** | GATE/Geant4 seTLE, ICRP voxel | 0.289 | 1.72 | 3.91 | TrueBeam XI |
| **Martin 2022** | BEAMnrc, NCI 193-phantom lib | – | M 3.8–7.6 | M 11–22 | Size-spread; 270/1080 mAs |
| **Fetin 2022** | PCXMC, spotlight 200° | – | – | 3.2 (spotlight) | Pelvis *spotlight*, not default |
| **Marchant 2017** | GATE seTLE, Elektra XVI | 0.03–0.09 | 1.38–3.19 | 2.80–7.60 | Different vendor (Elekta) |

**Interpretation:** MC-DCaRE's pelvis E (5.5-5.7) is within the spread of independent full-MC values (3.9-7.1 for male reference phantoms) and matches the physical TLD measurement (5.4) closely. The PCXMC reference (4.2) sits at the low end — consistent with PCXMC's mathematical phantom under-representing pelvis heterogeneity relative to voxelized anatomy. The ~30% MC-DCaRE-vs-PCXMC difference is plausible physics, not necessarily a bug, but warrants confirmation against organ-level independent data (§6 G3).

---

## 6. Gap analysis and recommendations

Prioritized: C = critical/correctness, H = high value, M = medium, L = low. Each references where the gap manifests and where the data to close it already exists.

### G1 — Paediatric phantoms [H]
PCXMC ships 6 age groups (newborn → adult); Fetin 2022 reports paediatric pelvis-spotlight E of 4.21-8.07 mSv vs 3.44 adult. MC-DCaRE's ICRP 145 path loads MRCP_AM/AF (adult) only; the 4 paediatric modes (Image Gently, Pediatric Head/Body) have blank E in the research table because PCXMC was never run for them.
**Action:** Add paediatric ICRP 145 mesh/voxel phantoms (or University of Florida/NCI paediatric library) to the Phantom mode. This is where MC-DCaRE can uniquely fill a gap the PCXMC baseline left open.

### G2 — Patient-size / BMI scaling [M]
Abuhaimed 2023 + Martin 2022 quantify: 5 cm shorter → +3-10% E; 10 kg lighter → +10-14%; thin-vs-obese pelvis E 0.92 vs 0.43 (per 100 mAs). MC-DCaRE computes for the loaded phantom only — no stature correction on a nominal result.
**Action:** Either (a) compute E for a size-phantom library and report a range, or (b) apply a documented stature correction factor to the reference-phantom E. At minimum, document that the reported E is for a specific phantom and does not scale.

### G3 — Validate against independent full-MC organ doses [H]
MC-DCaRE currently anchors to PCXMC E_refs (mathematical phantom) and internal TLE↔DTM consistency. The research folder contains stronger independent references: Abuhaimed 2018 per-organ mGy (bladder 44.75, prostate 34.55, colon 11.2 M) and Gilling 2019 (bladder D50% 18.7, rectum 17.8 mGy).
**Action:** Add organ-level benchmark cases (not just whole-E) to `BenchmarkCalculator` using Abuhaimed 2018 / Gilling 2019 tables. This converts the validation anchor from "agrees with a weaker method" to "agrees with an independent stronger method."

### G4 — Bow-tie / blade coefficient validation [H]
`fullfan.txt`/`halffan.txt` wedges and the `fieldtobladeopening.py` linear coefficients (`xbladeopening`, `ybladeopening`) carry no measurement citation — there is an explicit `TODO: Cite measurement source` at `src/fieldtobladeopening.py:4`. The research folder **already contains** the validation data: cross-plane dose profiles per mode in `Results.xlsx` (New tests August, 94-column grids) and `New results Oct 2023 (...).xlsx`.
**Action:** Compare MC-DCaRE's simulated cross-plane profile (phase-space scorer at the chamber plane) against the measured RaySafe profiles. Tune/document the bow-tie wedge dimensions against measured HVL-and-profile. Closes the open TODO.

### G5 — Heel effect [M]
Neither PCXMC nor MC-DCaRE models the anode-heel spatial intensity variation. Marchant 2017 captures it by embedding the source 2.5 µm in the tungsten anode; Gilling 2019 couldn't and recommends a phase-space source. MC-DCaRE's Beam source is a symmetric Gaussian focal spot.
**Action:** Low priority for symmetric 360° protocols (averages out). Relevant if pursuing partial-arc or 2D planar accuracy. A validated phase-space source from a real tube model would capture it.

### G6 — Spectrum ↔ measured HVL validation [H]
MC-DCaRE's SpekPy spectrum uses hardcoded `th=14°`, no filtration parameter (filtration is geometric via BHF+bowtie). The research folder has measured HVL per mode (Head 6.887, Pelvis 8.371, Pelvis Large 8.942, Thorax 7.953, Breast 7.849, Image Gently 5.737 mm Al).
**Action:** Compute MC-DCaRE's effective HVL from the phase-space scorer spectrum (`PhaseSpaceAnalyzer` can do this) and compare to the measured values per mode. Discrepancy points to bow-tie/BHF thickness errors. This is a cheap, high-signal validation.

### G7 — Phase-space replay bugs (active) [C]
Tracked in `openspec/changes/fix-phase-space-replay-dose/` (7/11 tasks done): Bug A (sequential-times normalization unnormalized, dose scales with R) and Bug B (~15× per-particle chamber inflation from `Component="Rotation"` coordinate-frame mismatch). Until resolved, phase-space replay dose is unreliable — the direct-beam path is the trustworthy one.
**Action:** Complete the open tasks in that change. No new work needed here; just finish what's scoped.

### G8 — DTW calibration populated [L]
`dcf_dtw` is defined (`src/models/calibration.py`) but never populated; `CalibrationService.lookup_dcf(scorer_type="dtw")` returns None. DTW matters if you want to report dose-to-water (radiotherapy convention) rather than dose-to-medium.
**Action:** Run the DTW calibration analogously to the 5 TLE/water-DTM runs already in `calibration.yaml`. Low urgency unless DTW reporting is required.

### G9 — DICOM-mode couch + couch-material fidelity [M]
Couch is modelled in CTDI/Phantom modes (Al `TsBox`) but absent in DICOM mode. Real TrueBeam couch is carbon-fiber; Al over-attenuates kV photons (documented in `src/AGENTS.md`).
**Action:** Add couch to DICOM mode; switch material from Al to a carbon-fiber composite (or a validated multi-layer model). Affects posterior-arc dose to posterior anatomy.

### G10 — ICRP 60 weighting option [L]
PCXMC lets the user pick ICRP 60 vs 103; MC-DCaRE hardcodes ICRP 103 (`src/models/icrp103.py`). ICRP 60 is largely historical but some legacy comparisons require it.
**Action:** Add `weighting_standard` config field dispatching between ICRP 60 and 103 tables. Low priority.

### G11 — Clinical reporting quantities (DLP, SSDE) [M]
MC-DCaRE computes CTDIw and effective dose but not DLP (CTDIvol × scan length) or SSDE (size-specific dose estimate). These are standard clinical CT reporting quantities.
**Action:** Add DLP and SSDE to `CTDICalculator` output. DLP is trivial (CTDIvol × N·slice); SSDE needs a patient-size correction factor (AAPM TG-204/220).

### G12 — TsTetGeom mesh phantom (active) [H]
ICRP 145 mesh phantom via `TsTetGeom` is broken (~16k unscored hits, empty CSV); voxelized fallback via `tools/voxelize_phantom.py` works. `src/AGENTS.md:60-61`.
**Action:** Either fix upstream `TsTetGeom` (TOPAS extension) or commit fully to the voxelized path and deprecate the mesh template. The voxelized path loses fine mesh organ boundaries; 5 mm resolution may under-resolve small organs (testes, thyroid).

---

## 7. Summary: where MC-DCaRE stands

| vs PCXMC research | Verdict |
|---|---|
| Physics rigour | **Strongly improved** — explicit transport, real anatomy, multi-scorer cross-validation replace kernel superposition on a math phantom |
| Automation / reproducibility | **Strongly improved** — no manual matrix handoff; provenance-tracked runfolders |
| Paediatric coverage | **Regression** — PCXMC had 6 age groups; MC-DCaRE is adult-focused (G1) |
| Bow-tie / source fidelity | **Comparable, unvalidated** — both approximate; MC-DCaRE's coefficients lack measurement citation (G4, G6) |
| Validation anchor | **Weaker than it could be** — anchored to PCXMC E_refs when independent full-MC literature exists in this folder (G3) |
| Phase-space replay | **In progress** — open bugs (G7); direct-beam path is sound |
| Clinical reporting | **Partial** — CTDI/E yes, DLP/SSDE no (G11) |

The single highest-leverage next step is **G3 + G4 + G6 together**: use the measured air-kerma profiles, HVL values, and independent full-MC organ doses already in this research folder to validate MC-DCaRE's bow-tie, spectrum, and organ-dose output. That converts the research collection from a historical baseline into an active validation corpus, and shifts MC-DCaRE's anchor from the PCXMC mathematical-phantom values to independent Geant4/EGSnrc literature.
