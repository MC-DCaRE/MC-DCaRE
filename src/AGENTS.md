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
- **Known TOPAS limitation under investigation:** a PhaseSpace source into a LayeredMassGeometry (parallel-world) phantom scores ~14× high vs a matched Beam-source run, with an entry-to-exit gradient. Injection and air transport are verified faithful; the divergence is inside the parallel-world scorer. Tracked in `openspec/changes/fix-phase-space-replay-dose/`.
