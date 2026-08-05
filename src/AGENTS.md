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
- The CTDI DCF (`dcf_dtm` from `calibration.yaml`) is the only absolute dose correction. It converts raw MC dose to physical dose using the measured-vs-simulated CTDI_w ratio. The DCF is calibrated for DTM scorer in air-filled chamber cavities (LayeredMassGeometry). When applied to organ DoseToMedium in body tissue (TsDicomPatient), the absolute values may differ. Report E/CTDIw ratio alongside the DCF-corrected effective dose.
- kV lookup in `_normalize_dose`: falls back to `metadata["spekpy"]["kvp"]` when `metadata["kV"]` is absent (fixed commit e6aa255).
