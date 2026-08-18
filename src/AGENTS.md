# src

## Purpose
Core source package for MC-DCaRE (Monte Carlo Dose Calculation and Research Environment). Provides simulation configuration, TOPAS parameter file generation via Jinja2 templates, GUI, and post-processing for CT dosimetry.

## Architecture
`Orchestrator` is the central coordinator. Flow: `config.py` defines `SimulationConfig` -> `Orchestrator` creates a runfolder and selects a `SimulationMode` (DICOM, CTDI, or ICRP145) -> mode builds Jinja2 context dict -> `TemplateRenderer` renders `.j2` boilerplate templates -> `SimulationRunner` executes TOPAS as a single process per simulation (capturing output to log files) -> `CTDICalculator` post-processes results. For CTDI mode, all 5 chamber plug positions are scored simultaneously using TOPAS Parallel Worlds (Layered Mass Geometry) in a single process. Three scorer types run per position (TLE, DTM, DTW); TLE is designated primary (measurement-equivalent). Optional water-filled chamber volumes add 5 more DTM scorers (`_water_dtm`) gated by `ctdi.water_chamber_enabled`. `CalibrationService.apply()` calibrates only TLE results by default. ICRP145 mode loads an ICRP 145 tetrahedral-mesh reference phantom via the `TsTetGeom` extension and scores organ dose with `TsTetGeomScorer`. Python logging is tee'd to `<runfolder>/simulation.log` (filename configurable via `GeneralConfig.log_filename`).

Subdirectories:
- **models/** — Immutable dataclasses: `Quantity`, `ImagingMode` (21 fields, 47 protocols), enums (`SimulationType` with DICOM/CTDI/ICRP145, `FanMode`), UI keys, `icrp103` (ICRP 103 tissue weighting factors and organ-to-tissue mapping)
- **modes/** — Strategy pattern: `SimulationMode` ABC with `DicomMode`, `CtdiMode`, and `PhantomMode` implementations
- **gui/** — FreeSimpleGUI MVC: `MainView` (layout with DICOM/CTDI/ICRP145 tabs) + `controller.py` (event handling)
- **services/** — Post-simulation services: `CTDICalculator` (scorer-aware CTDI metrics with TLE as primary), `CalibrationService` (per-scorer DCFs: `dcf_tle`/`dcf_dtw`/`dcf_water_dtm` selected via `scorer_type` parameter; raw-dose normalization centralized in the module-level `raw_absolute_dose_Gy()` helper so every CLI/service applies the same `(raw_sum / n_scorer_active_histories) × photons_per_mAs × mAs` formula), `BenchmarkCalculator` (benchmarks TLE only), `PhantomDoseCalculator` (voxelized phantom organ dose + ICRP 103 effective dose with DCF normalization), `PhaseSpaceAnalyzer` (header-driven TOPAS Binary `.phsp` reader — parses the self-describing `.header` sibling, 34-byte records of 7×f4 + i4 PDG + 2 flags; converts MeV→keV; decodes PDG codes)
- **boilerplates/** — Jinja2 TOPAS parameter file templates and include file directories

## Key Files

| File | Role |
|---|---|
| `config.py` | `SimulationConfig` dataclass, all configuration parameters, `_resolve_imaging_mode()` for name-based config resolution |
| `orchestrator.py` | Central coordinator: mode selection, Jinja2 rendering, run execution |
| `boilerplate_manager.py` | Creates `TemplateRenderer`, manages `tmp/` working directory |
| `template_renderer.py` | Jinja2 template rendering with `FileSystemLoader` |
| `simulation_runner.py` | Executes TOPAS simulations as single processes, captures stdout/stderr to log files |
| `spectrum_generator.py` | Generates X-ray spectrum definitions via SpekPy |
| `fieldtobladeopening.py` | Converts field size to collimator blade opening positions |

Also see `calculate_phantom_dose.py` (project root): CLI entry point for phantom mode post-processing, invokes `PhantomDoseCalculator`.

## Conventions
- `from __future__ import annotations` in every module
- `logging.getLogger(__name__)` for all logging
- `frozen=True` dataclasses for immutable value objects in `models/`
- Abstract base classes define contracts in `modes/base.py`
- All imports use `src.` prefix (e.g., `from src.config import ...`)
- Modes build context dicts (`Dict[str, object]`) consumed by Jinja2 templates
- `TemplateRenderer` searches both `boilerplates/` and `TOPAS_includeFiles/` for templates

## TOPAS Reference
- **Docs:** <https://opentopas.readthedocs.io/en/latest/> (consult for any TOPAS implementation question — parameter syntax, source/scorer behavior, parallel worlds, extensions). Key pages: [Phase Space Sources](https://opentopas.readthedocs.io/en/latest/parameters/source/phasespace.html), [Phase Space Scorer](https://opentopas.readthedocs.io/en/latest/parameters/scoring/phasespace.html), [Parallel Worlds](https://opentopas.readthedocs.io/en/latest/parameters/geometry/parallel_world.html), [LayeredMassGeometry](https://opentopas.readthedocs.io/en/latest/examples-docs/Basic/LayeredMassGeometry.html), [Custom Scorers](https://opentopas.readthedocs.io/en/latest/extension-docs/scoring.html).
- **Installed version/paths (this host):** OpenTOPAS 4.2.p3 on Geant4.11. Binary `topas` (on `PATH`) at `/opt/topas/TOPAS/OpenTOPAS-install/bin/topas`; headers at `/opt/topas/TOPAS/OpenTOPAS-install/include/`; Geant4 data via `TOPAS_G4_DATA_DIR=/opt/topas/GEANT4/G4DATA`. Run TOPAS with the runfolder as CWD (the PhaseSpace source resolves `PhaseSpaceFileName` and `.header` relative to CWD).
- **TOPAS Binary phase-space format:** 34 bytes/particle (7×f4 + i4 PDG + 2 flag bytes), self-describing via the `.header` sibling (energy in MeV). See `src/services/phase_space_analyzer.py`.
- **Phase-space scoring plane placement:** the PhspSurface at Y=-86cm sits inside the collimator jaw geometry (the complex 4-level nested rotation makes the jaw extent analytically invisible). This causes the direct (Beam-source) sim to lose ~94% of phantom-directed particles between Y=-86 and Y=-80cm. The PhaseSpace replay is correct (confirmed by geometric ray-tracing). Fix: move PhspSurface to Y ≤ -75cm. Tracked in `openspec/changes/fix-phase-space-replay-dose/`.

## Bow-tie filter

Two bow-tie models, selected by `imaging.legacy_bowtie` (default **False** = TsCAD):
- **TsCAD mesh** (`bowtie_ff.txt`/`bowtie_hf.txt`): the measured Inbum bow-tie (`research/Monte Carlo Stuff from Inbum/bowtie.stl`), processed to binary STL by `tools/process_bowtie_stl.py` (recentered, decimated). Loaded via `TsCAD` (`FileFormat="stl"`, `Units=1.0 mm`). Validated against the RaySafe Oct-2023 profile (`validate-bowtie-stl-asset`): peak-normalised RMS misfit 0.078 (TsCAD) vs 0.583 (legacy CSG) vs 0.602 (no bow-tie).
- **Legacy CSG** (`fullfan.txt`/`halffan.txt`): hand-fitted Aluminum trapezoid wedges in the collimator bay. Retained as a fallback (`legacy_bowtie=True`).

**Bow-tie wedge varies in World Z.** With `RotZ=-90` (and `RotY=0`) the STL thin axis lies along the beam (Y), the wedge falls in World Z, and the extrusion is uniform in World X. Verified by a 2D X×Z isocenter kerma map + visual 3-view (`docs/bowtie_validation/plots/`). The `validate_bowtie` scorer in `ctdi_phsp_score.j2` (a `TrackLengthEstimator` on a thin air slab at isocenter) bins Z with a wide Z-field (`user_field_x` ≥ 32 cm) so the collimator does not cut the profile; `tools/convert_bowtie_profile.py` + `tools/validate_bowtie.py` do the comparison. Measured Head-FF CAX HVL = 7.37 mmAl (RaySafe, literature anchor).

**TsCAD placement (validated 2026-08-13):** the STL bow-tie is parented to `Rotation` (rotates with the tube) at a source-to-bowtie distance of **18 cm** (`TransY = Ge/BeamPosition/TransY + 18 cm`), thin axis (STL-X) aligned with the beam via `RotZ=-90`, `RotY=0`. It must NOT be parented to the collimator bay (`CollimatorsHorizontal`) — the STL's 140 mm extent overlaps the collimator jaws (Coll1) and Ti BHF there, which corrupts Geant4 navigation and attenuates the beam ~80×. At the correct 18 cm placement the run is clean (0 overlaps). The half-fan `bowtie_hf.txt` is a one-sided crop of the full-fan STL (approximation; the TrueBeam half-fan is a distinct filter).

`imaging.bhf_thickness_mm` (default 0.89) drives the Ti beam-hardening filter, and `imaging.bhf_mode` selects where it lives: **`spekpy` (default — prefer this)** folds the Ti into the SpekPy source spectrum (`s.filter("Ti", mm)`; mm means mm, no TsBox, marginally faster) vs `geometric` (physical Ti TsBox — **NB: TOPAS HLZ is a half-length, so the box spans 2× the thickness along Z**, i.e. 0.89 renders 1.78 mm Ti; keep as the toggle for full-geometry validation runs). The two agree at equal physical thickness to ~3% (see `docs/bowtie_validation/`). `bhf_thickness_mm: 0` removes the filter entirely (Ti-out bracketing; geometric only). `imaging.filtration_mode` (`geometric` bare spectrum | `hybrid` inherent+collimator Al folded into SpekPy, default **hybrid**) selects where the uniform base filtration lives; the bow-tie stays geometric in both. `imaging.bowtie_enabled` (default True) removes the bow-tie include entirely when False (baseline/reference runs). Switching bow-tie/BHF/filtration modes changes the beam spectrum and requires re-running the CTDI DCF calibration (the 2026-08-14 DCFs were calibrated at geometric 1.78 mm Ti — stale for spekpy runs). `imaging.fluence_anchor` (default **measured**) scales the SpekPy particle count by the per-kV factor in `data/measured/fluence_anchors.yaml` (F(100)=0.1070, F(125)=0.1077; `model` = raw SpekPy for auditing) — the 2026-08-18 anchor round collapsed the Gros-2025 per-protocol Kair bias from 5.7-9.8x to 1.01-1.13x. Known residual: the TsCAD STL CAX transmission is 0.899 vs 0.523 measured (central region ~1.7x too transparent; ~8 mm Al-eq of real central bow-tie material vs ~1.5 in the STL) — absorbed into the anchored fluence/DCF for dose work. The 2026-08-14 DCFs predate the rectangular-blade fix and the fluence anchor: re-calibrate before absolute/phantom work.

## Phase-Space Replay Gotchas

### Component choice controls rotation
- `Component = "World"` (default in `ctdi_phsp_replay.j2`): PhaseSpace particles are placed at their absolute World positions. The beam does NOT rotate. Correct for stationary CTDI scoring where all chamber positions are scored simultaneously via LayeredMassGeometry.
- `Component = "Rotation"`: particles inherit the Rotation group's time-dependent transform (`RotZ = Tf/Rotate/Value`). Required for CBCT 360° rotational dose into voxelized phantoms (TsDicomPatient). Without this, all dose comes from a single anterior angle regardless of time-feature settings.

### Rotation wiring
- `dc:Ge/Rotation/RotZ = Tf/Rotate/Value deg` is the required wiring. A static `RotZ = 0 deg` produces no rotation — the beam stays at a single angle.
- `Function = "Linear deg"` with `NumberOfSequentialTimes = N`: divides [0°, Rate×TimelineEnd] into N equal steps. N=36 (10° steps) gives good 360° coverage with 20 threads. Each sequential time is a separate TOPAS sub-run; the DoseToMedium scorer accumulates across all sub-runs.
- `Tf/RandomizeTimeDistribution = "True"` exists but requires `NumberOfThreads = 1` (TOPAS hard error otherwise). Impractically slow for production. Use sequential mode instead.
- kV-kV planar imaging: `rotation_direction = "kV-kV"` triggers a Step function with 2 angles (`start_angle` and `start_angle + 90°`). Only those 2 angles contribute dose.

### Phase-space Z-filtering for phantom replay
The PhspSurface is 100cm × 100cm and captures scattered photons out to ±42cm in Z. For phantom replay, filter the `.phsp` file to the primary beam field (e.g., `|Z| < 8cm` for pelvis) before replaying into the voxelized phantom. Without filtering, scattered particles deposit spurious dose in non-target anatomy (chest, head).

### TsTetGeom is broken
The `TsTetGeom` extension (tetrahedral mesh phantom) has parameterization navigation errors in the available `topas_meshgeom_fixed` binary (~16k unscored hits, empty CSV output). Use the voxelized `TsDicomPatient` path instead. Convert mesh to voxels via `tools/voxelize_phantom.py` (5mm resolution, KDTree-accelerated point-in-tetrahedron lookup, outputs DICOM CT slices with Schneider HU-to-material conversion).

### DCF normalization
- **Effective dose vs CTDIw are fundamentally different quantities.** Effective dose (E, in mSv) is the ICRP 103 whole-body stochastic risk metric computed from organ doses in a human phantom. CTDIw (in mGy) is the dose to an ionization chamber inside a CTDI dosimetry phantom (16 or 32 cm PMMA cylinder). They measure different things — E captures the full-body biological risk; CTDIw captures the local dose in a standardized phantom. Never compare them directly without an E/CTDIw conversion factor.
- **Reference effective doses** for the generic 80 kg reference phantom are stored in `calibration.yaml` under `effective_dose_references`, keyed by protocol name (e.g. `"Pelvis": 4.2`). These are manufacturer-provided whole-body effective doses, distinct from the `measured_ctdi_w_mGy` values which are chamber measurements.
- **All scorer types work in LayeredMassGeometry (LMG) parallel worlds.** TLE (fluence-based), DTM, and DTW all register non-zero dose when the parallel-world material is dense enough to interact. The air-filled CTDI chamber plugs give Count_in_Bin=0 for DTM/DTW because *air has a negligible interaction probability*, not because of a scorer/SD limitation — confirmed by enabling `water_chamber_enabled` (water-filled plug copies): the `_water_dtm` scorers return non-zero dose (Count_in_Bin > 0). LMG scoring works because TOPAS attaches the sensitive detector to the parallel-world component and the G4ParallelWorldProcess delivers physics with the parallel-world material.
- **DCF for TLE** is calibrated from CTDI phantom measurements: `DCF = measured_CTDIw / raw_absolute_CTDIw`. This works because TLE is fluence-based (every photon contributes regardless of interaction).
- **Both TLE and DTM transfer from CTDI to phantom effective dose.** DTM and TLE agree within 4% on the 125 kV HF pelvis phantom (DTM 5.46 mSv, TLE 5.70 mSv), consistent with the Hauri 2017 literature value (5.4 mSv, TLD in Alderson phantom, same protocol). The prior `dcf_dtm = 0.02761` was circular — derived from the reference effective dose (`E_ref / E_raw_MC = 4.2 / 152.13`) — and has been removed. The phantom effective dose comes from applying CTDI-derived DCFs (`dcf_tle` for TLE scorer, `dcf_water_dtm` for DTM scorer) to the voxelized phantom. Both DCFs are CTDI-derived, non-circular, and transferable. `calculate_phantom_dose.py` and `PhantomDoseCalculator.calculate()` default to `scorer_type="tle"`.
- **Never anchor phantom doses to other simulation results.** Always compute absolute effective dose by applying the CTDI-derived DCF directly via the standard normalization formula (`raw_absolute_dose_Gy × DCF`). Do NOT scale, calibrate, or anchor phantom results to match a reference or another run. Compute the DCF-calibrated dose independently and compare it directly to `E_ref` — the difference IS the result, not something to correct away.
- **Phase-space replay normalization.** For phase-space replay with `PhaseSpaceMultipleUse = M` and `NumberOfSequentialTimes = R`, set `n_scorer_active_histories = N_scoring × R × M` in the replay metadata (NOT the TOPAS-reported `N_phsp × M × R`). This accounts for the fact that each phase-space particle represents `N_scoring / N_phsp` primary source events. Using the TOPAS-reported value overestimates the dose by `N_scoring / N_phsp_filtered ≈ 24×`. Also use a wide Z-filter (`|Z| < 20cm`) on the phase space — the prior `|Z| < 8cm` captured only 20% of the beam field, underestimating dose by ~50%.
- **Selection-bias fix in PhantomDoseCalculator (2026-08-12).** The prior code skipped every voxel with `dose <= 0`, which exclusively removed DTM voxels (collision-based; many zeros in low-fluence organs) while keeping all TLE voxels (fluence-based; always positive). This inflated DTM organ means by up to 11x on the 5M-history phantom run, producing the spurious "DTM doesn't transfer" conclusion. The fix includes zero-dose voxels in the mean (only excludes unmapped material IDs like air, and `mat_id == -1`). With the fix, DTM and TLE agree within 4% on effective dose — exactly what CPE physics predicts.
- **Water-chamber requirements (`water_chamber_enabled=True`)** — three things must hold or TOPAS crashes: (1) water parallel worlds must be listed in `LayeredMassGeometryWorlds` (else SIGSEGV "Parallel world X has material, but this world not specified") — handled conditionally in `headsourcecode_boilerplate.j2`/`ctdi_phsp_replay.j2`; (2) all plug colors must be in TOPAS's default palette (`TsDefaultParameters.cc`) — "Cyan"/"Aquamarine" are NOT defaults (TOPAS ships "Aqua"), and `GetColor` returns NULL → NULL-deref segfault, so the phantom templates define `Gr/Color/Cyan` and `Gr/Color/Aquamarine` explicitly; (3) Geant4 caps total navigators at 16, and each binned parallel-world scorer spawns a divided-copy world — air chambers already use 10, so the `_water_dtm` scorers are unbinned (no `ZBins`) to stay under the cap.
- **Scorer type must match the DCF type — never cross-apply.** The DCF and the scorer quantify dose differently (TLE is fluence/kerma-based; DTM and DTW are collision/deposition-based), so a DCF calibrated for one is invalid for another. Always pair them: TLE scorer ↔ `dcf_tle`, CTDI water-chamber DTM ↔ `dcf_water_dtm`, DTW ↔ `dcf_dtw`. `CalibrationService.normalize_dose(scorer_type=...)` enforces this via `_DCF_FIELDS` — the `scorer_type` argument selects both the DCF field and must match the scorer that produced the raw dose. Both `dcf_tle` and `dcf_water_dtm` are CTDI-derived and transfer to the phantom (DTM 5.46 mSv vs TLE 5.70 mSv, 4% agreement, both consistent with the 5.4 mSv Hauri 2017 literature value).
- **TLE vs DTM: per-organ divergence is real but modest at the effective-dose level.** TLE estimates collision kerma (fluence × μ_en/ρ) under a charged-particle-equilibrium (CPE) assumption; DTM scores actual energy deposition. They agree where CPE holds (large uniform soft-tissue regions) and diverge where it fails — small organs, tissue interfaces, spongiosa/cortical bone, air cavities. After the selection-bias fix, both TLE and DTM effective doses land at 5.5-5.7 mSv on the 125 kV HF pelvis phantom. The tissue-weighted effective dose is more stable than individual organ doses because the high-weight organs (bone marrow, colon, bladder, stomach) tend to be large uniform regions where TLE/DTM agree.
- kV lookup in `_normalize_dose`: falls back to `metadata["spekpy"]["kvp"]` when `metadata["kV"]` is absent (fixed commit e6aa255).

### CTDI Calculator Normalization Fix
The CTDICalculator uses MEAN of per-bin doses (not SUM) to match pencil chamber physics:
- Pencil chamber measures: E_total / m_total = mean dose over 100mm volume
- TOPAS Z-binned scorer outputs: per-bin Sum = E_bin / m_bin (dose at each 1mm position)
- SUM of per-bin values = N_bins × mean_dose (inflated by 100×)
- MEAN of per-bin values = mean_dose (correct, matches chamber reading)
- Without this fix, the DCF absorbs the 100× factor and cannot transfer to organ dose

### Sequential Times for Rotational CTDI
CTDI measurements are rotational (the tube rotates 360° around the phantom). With
`NumberOfSequentialTimes = 1`, all histories fire at a single angle — no rotation.
Use `NumberOfSequentialTimes >= 36` (10° steps) for correct rotational CTDI_w.
This also equalizes Top/Bottom/Left/Right statistics (from 12:1 imbalance to ~1:1).
