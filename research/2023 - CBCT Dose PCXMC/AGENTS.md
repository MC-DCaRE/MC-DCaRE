# 2023 - CBCT Dose PCXMC

PCXMC-based CBCT dose study (NSW Health, A. Fetin / L. Cartwright / "Terry", 2020-2023). Methodology and results from Fetin et al. 2022 (*Phys Eng Sci Med*, doi 10.1007/s13246-022-01103-9).

## Headline

The code here is a **PCXMC input-file generator**, not a dose engine. The MATLAB `Main.m` / Python `pcxmc_runner.py` build a 20-column `PCXMCInput` matrix; a human pastes it into STUK PCXMC 2.0's Excel front-end, which performs the kernel-superposition organ-dose calculation. There is no dose-kernel data, no organ-dose arithmetic, no effective-dose computation, and no CTDI calculation in any committed source file (MATLAB or Python). The proprietary PCXMC 2.0 application (install disk present in this folder) holds the kernels.

## Directory map

```
2023 - CBCT Dose PCXMC/
├── PCXMCStuff/PCXMC_Code/          Cleaned MATLAB driver (refactored variant)
│   ├── Main.m, Main_refactored.m   Geometry + rotation + amend loop -> PCXMCInput
│   ├── findIntersections.m         Line/ellipse quadratic solver
│   ├── withinEllipse.m             (x/a)^2+(y/b)^2 <= 1 test
│   ├── subFieldIntersection(s).m   Perpendicular boundary offset for amend test
│   ├── resScale.m                  Z-grid re-interpolation of kerma/filtration
│   ├── WrapTo360.m                 Angle wrap to [-360,360] (NOT [0,360))
│   ├── protocol_config.m           Sample protocol params (kerma, kV, dims)
│   ├── load_protocol_config.m      Config loader/validator
│   └── BasicNotesonMATLABCode.pdf  Documents the input-matrix handoff
│
├── pcxmc_py_refactor/              Python port attempt (GEOMETRY ONLY)
│   ├── src/geometry.py             Correct ports of within_ellipse/intersections
│   ├── src/pcxmc_runner.py         run() builds PCXMCInput; NO dose; has 2 bugs
│   ├── src/utils.py                wrap_to_360 returns [0,360) (range mismatch)
│   ├── src/interpolation.py        res_scale port
│   ├── src/config_loader.py        YAML loader; .m loader NotImplementedError
│   ├── src/visualization.py        Phantom/sub-field plots
│   ├── configs/demo_config.yaml    Sample config (kerma scaling NOT auto-applied)
│   ├── tests/test_geometry.py      11 passing geometry tests
│   ├── tests/test_main.py          BROKEN: imports non-existent API
│   ├── tests/test_pcxmc_runner.py  Asserts on keys the runner doesn't return
│   ├── docs/REFACTOR_STATUS.md     Overstates completeness (geometry only)
│   └── docs/specs/                 Aspirational specs (dose/CTDI never built)
│
├── from terry/                     Terry's working folder (PRODUCTION scripts)
│   ├── matlab/PCXMC_Code/          Real per-protocol Main_*.m scripts
│   │   ├── Main_pelvis_average_maleV3_final.m   ...and ~30 variants
│   │   │                             (head/thorax/breast/pelvis × 3 body sizes
│   │   │                              × spotlight/4D; oldDNU/ = deprecated scaling)
│   ├── PCXMC results spreadsheets/ Autocalc-sheet-*.xls (PCXMC front-end outputs)
│   ├── ImPACT/                     MCSET01-23.DAT = NRPB SR250 CT dose lookup
│   │                               (UK ImPACT CTDosimetry, vintage 1990s MC)
│   ├── CTDosimetry_1.0.4.xls/.pdf  ImPACT CT dosimetry tool
│   ├── papers already published.txt  2 URLs (Marchant 2017, Martin 2012)
│   ├── 2022-12-22 preliminary outcomes from PCXMC testing.docx
│   ├── Fetin2022_Article_...pdf    Published paper
│   ├── Aaron Fetin-PHYS5036_FinalReport_...pdf  Honours report (full method)
│   ├── Gilling, Luke_Master's Thesis.pdf  GATE/Geant4 CBCT MC (TrueBeam XI)
│   ├── PCXMC_20_UsersGuide.pdf et al.  STUK PCXMC 2.0 official docs
│   └── TrueBeamCBCTmodes.xlsx      Working master mode table (predecessor)
│
├── PCXMC20andPCXMC20Rotation-INSTALLDISK/  STUK PCXMC 2.0 installer + docs
│   (PCXMC20_Setup.exe, PCXMC_20_UsersGuide.pdf, Documentation.pdf)
│
├── related stuff/, related papers/  Academic PDFs (Abuhaimed, Martin, Marchant)
│
├── Results.xlsx, new results.xlsx              Measured air-kerma per mode
├── New results Oct 2023 (...).xlsx (x2)        RaySafe X2 service-mode profiles
├── scaling kerma for different exposures.xlsx  mAs-scaling of effective dose
├── PCXMC Results.docx, Terry's initial PCXMC Results.docx
└── Fetin2022_Article_...pdf                    Published paper (top-level copy)
```

## What the code actually does (the implemented pipeline)

1. Compute gantry angles from `startingAngle`/`finalAngle`/`numAnglesSimmed` (closed 360° arcs drop the duplicate final angle).
2. Optionally re-grid sub-field z-centres via `resScale`.
3. Rotate each sub-field centre to every gantry angle (2D rotation + iso offset).
4. **Amend loop**: for each rotated sub-field, test whether it falls inside the ellipsoidal phantom cross-section. If the centre is outside but the field clips the phantom, snap the centre to the phantom surface via `findIntersections` and recompute width. Drop fully-outside sub-fields.
5. Pack survivors into the 20-column `PCXMCInput` matrix (columns include kerma, filtration, phantom dims, angle).

Steps 6-8 (paste into PCXMC, run MC, sum results) are manual and external.

## Key measured/derived data

**Air kerma (central axis, RaySafe measurement, mGy)** — from `Results.xlsx` / `from terry/Results.xlsx`:

| Mode | kV | Air kerma (mGy) | HVL (mm Al) | Fan | Arc |
|---|---|---|---|---|---|
| Head | 100 | 1.392 | 6.887 | Full | Half |
| Pelvis | 125 | 9.280 | 8.371 | Half | Full |
| Pelvis Large | 140 | 6.008 | 8.942 | Half | Full |
| Breast 360 | 125 | 0.689 | 7.849 | Full | Half |
| Thorax | 125 | 3.839 | 7.953 | Half | Full |
| Image Gently | 80 | 0.631 | 5.737 | Full | Half |

**Finalized PCXMC effective doses (adult 80 kg/180 cm, ICRP 103)** — from `2023 - CBCT Mode Standardisation/TrueBeamCBCTmodes.xlsx` (the cleaned `For printing Apr25` / `TB4.1 July25` sheets):

| Mode | kV | mAs | CTDI (mGy) | E (mSv) |
|---|---|---|---|---|
| Head | 100 | 150 | 3.171 | 0.5 |
| Head SRS | 100 | 540 | 11.331 | 1.8 |
| Thorax | 125 | 270 | 3.974 | 1.3 |
| 4D Thorax | 125 | 672 | 9.934 | 3.3 |
| Pelvis | 125 | 1080 | 15.895 | 4.2 |
| Pelvis Spotlight | 125 | 750 | 12.325 | 2.2 |
| 4D Spotlight | 125 | 374 | 6.127 | 1.6 |
| Abdomen | 125 | 720 | 10.597 | 2.8 |
| Breast 360 | 125 | 90 | 1.325 | 0.2 |
| Thorax Spotlight | 125 | 150 | 2.465 | 0.7 |
| Head and Shoulders | 125 | 270 | 3.974 | 0.3 |
| Extremity Spotlight | 100 | 150 | 3.171 | 0.5 |
| SBRT Spine | 125 | 360 | 5.298 | 1.7 |

(Effective dose blanks in source: Image Gently, Pelvis Large, Pediatric Head/Body — PCXMC not run for those.)

These exact E values are stored in MC-DCaRE's `calibration.yaml` under `effective_dose_references`, keyed by protocol short-name.

## Python refactor bugs (do not trust numeric output)

1. `pcxmc_runner.py` `_subfield_intersection` offsets along the inter-centre line, not perpendicular to the beam (the correct version exists in `geometry.py` but is unused).
2. `utils.wrap_to_360` returns `[0,360)`; MATLAB `WrapTo360` returns `[-360,360]`.
3. `test_main.py` imports `run_example_calculation` that doesn't exist; `test_pcxmc_runner.py` asserts on keys the runner doesn't return (`widthsFinal` vs `sFWFinal`).
4. `export_pcxmc_matrix.py` is syntactically truncated mid-function.
