# src

## Purpose
Core source package for MC-DCaRE (Monte Carlo Dose Calculation and Research Environment). Provides simulation configuration, TOPAS parameter file generation via Jinja2 templates, GUI, and post-processing for CT dosimetry.

## Architecture
`Orchestrator` is the central coordinator. Flow: `config.py` defines `SimulationConfig` -> `Orchestrator` creates a runfolder and selects a `SimulationMode` (DICOM, CTDI, or ICRP145) -> mode builds Jinja2 context dict -> `TemplateRenderer` renders `.j2` boilerplate templates -> `SimulationRunner` executes TOPAS as a single process per simulation (capturing output to log files) -> `CTDICalculator` post-processes results. For CTDI mode, all 5 chamber plug positions are scored simultaneously using TOPAS Parallel Worlds (Layered Mass Geometry) in a single process. Three scorer types run per position (TLE, DTM, DTW); TLE is designated primary (measurement-equivalent). Optional water-filled chamber volumes add 5 more DTM scorers (`_water_dtm`) gated by `ctdi.water_chamber_enabled`. `CalibrationService.apply()` calibrates only TLE results by default. ICRP145 mode loads an ICRP 145 tetrahedral-mesh reference phantom via the `TsTetGeom` extension and scores organ dose with `TsTetGeomScorer`. Python logging is tee'd to `<runfolder>/simulation.log` (filename configurable via `GeneralConfig.log_filename`).

Subdirectories:
- **models/** — Immutable dataclasses: `Quantity`, `ImagingMode` (21 fields, 47 protocols), enums (`SimulationType` with DICOM/CTDI/ICRP145, `FanMode`), UI keys, `icrp103` (ICRP 103 tissue weighting factors and organ-to-tissue mapping)
- **modes/** — Strategy pattern: `SimulationMode` ABC with `DicomMode`, `CtdiMode`, and `PhantomMode` implementations
- **gui/** — FreeSimpleGUI MVC: `MainView` (layout with DICOM/CTDI/ICRP145 tabs) + `controller.py` (event handling)
- **services/** — Post-simulation services: `CTDICalculator` (scorer-aware CTDI metrics with TLE as primary), `CalibrationService` (per-scorer DCFs: `dcf_tle`/`dcf_dtw`/`dcf_dtm` selected via `scorer_type` parameter; raw-dose normalization centralized in the module-level `raw_absolute_dose_Gy()` helper so every CLI/service applies the same `(raw_sum / total_histories) × photons_per_mAs × mAs` formula), `BenchmarkCalculator` (benchmarks TLE only), `PhantomDoseCalculator` (voxelized phantom organ dose + ICRP 103 effective dose with DCF normalization), `PhaseSpaceAnalyzer` (header-driven TOPAS Binary `.phsp` reader — parses the self-describing `.header` sibling, 34-byte records of 7×f4 + i4 PDG + 2 flags; converts MeV→keV; decodes PDG codes)
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
- **No body-tissue `dcf_dtm` — phantom effective dose uses TLE.** The prior `dcf_dtm = 0.02761` (125 HF) was circular — derived from the reference effective dose (`E_ref / E_raw_MC = 4.2 / 152.13`), so it reproduced the 4.2 mSv reference by construction when applied back to the phantom. It has been removed. The phantom effective dose now comes from the **TLE path**: CTDI `dcf_tle` → phantom TLE scorer → 5.77 mSv (+37% vs ref), the only non-circular CTDI-derived route. `calculate_phantom_dose.py` and `PhantomDoseCalculator.calculate()` now default to `scorer_type="tle"`. The CTDI water-chamber `dcf_water_dtm` does NOT fill this role — applying it to body DTM gives 25.4 mSv (+505%) because the water-chamber DCF doesn't transfer to body-tissue voxels (DTM is collision-based, geometry-specific).
- **Water-chamber requirements (`water_chamber_enabled=True`)** — three things must hold or TOPAS crashes: (1) water parallel worlds must be listed in `LayeredMassGeometryWorlds` (else SIGSEGV "Parallel world X has material, but this world not specified") — handled conditionally in `headsourcecode_boilerplate.j2`/`ctdi_phsp_replay.j2`; (2) all plug colors must be in TOPAS's default palette (`TsDefaultParameters.cc`) — "Cyan"/"Aquamarine" are NOT defaults (TOPAS ships "Aqua"), and `GetColor` returns NULL → NULL-deref segfault, so the phantom templates define `Gr/Color/Cyan` and `Gr/Color/Aquamarine` explicitly; (3) Geant4 caps total navigators at 16, and each binned parallel-world scorer spawns a divided-copy world — air chambers already use 10, so the `_water_dtm` scorers are unbinned (no `ZBins`) to stay under the cap.
- **Scorer type must match the DCF type — never cross-apply.** The DCF and the scorer quantify dose differently (TLE is fluence/kerma-based; DTM and DTW are collision/deposition-based), so a DCF calibrated for one is invalid for another. Always pair them: TLE scorer ↔ `dcf_tle`, CTDI water-chamber DTM ↔ `dcf_water_dtm`, DTW ↔ `dcf_dtw`. `CalibrationService.normalize_dose(scorer_type=...)` enforces this via `_DCF_FIELDS` — the `scorer_type` argument selects both the DCF field and must match the scorer that produced the raw dose. Example of the failure mode: applying `dcf_tle` (0.16) to a phantom DTM scorer gives 24.5 mSv (+482% vs 4.2 ref) because the DTM raw dose in tissue is ~4× the TLE raw. The TLE path is independently transferable (CTDI `dcf_tle` → phantom TLE scorer → 5.77 mSv, +37% vs ref, no phantom reference needed).
- **TLE vs DTM: expect large per-organ divergence, modest effective-dose divergence.** TLE estimates collision kerma (fluence × μ_en/ρ) under a charged-particle-equilibrium (CPE) assumption; DTM scores actual energy deposition. They agree where CPE holds (large uniform soft-tissue regions) and diverge where it fails — small organs, tissue interfaces, spongiosa/cortical bone, air cavities. On the 125 kV HF pelvis phantom: TLE effective dose is 5.77 mSv (+37% vs the 4.2 mSv reference), with per-organ differences spanning -85% to +200%+ (TLE overestimates in heterogeneous regions). This is expected TLE physics, not a normalization bug. For radiation-protection effective dose, TLE is acceptable; for organ-level accuracy, DTM is more accurate but has no non-circular CTDI-derived DCF (would need an independent body-tissue reference). The tissue-weighted effective dose is more stable than individual organ doses because the high-weight organs (bone marrow, colon, bladder, stomach) tend to be large uniform regions where TLE/DTM agree.
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
