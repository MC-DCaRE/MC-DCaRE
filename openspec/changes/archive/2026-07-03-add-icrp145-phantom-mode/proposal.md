## Why

MC-DCaRE simulates dose on patient DICOM datasets (`DicomMode`) and CTDI phantoms (`CtdiMode`), but has no standardized, reproducible reference patient. ICRP Publication 145 supplies adult reference computational phantoms as tetrahedral meshes (MRCP-AM/AF) that retain sub-mm source/target organs. We need a mode that places an ICRP 145 reference phantom supine on the CT couch and scores dose under the existing beam geometry, giving a repeatable "reference DICOM" run. OpenTOPAS 4.2.p3 plus the `TsTetGeom` extension make direct tetrahedral-mesh transport possible without voxelizing (which would discard the sub-mm detail that is the reason to adopt ICRP 145).

## What Changes

- New `ICRP145` simulation type (enum) and a `PhantomMode` strategy that mirrors `DicomMode`: builds a main context + a sub-include context, selects templates, prepares the run directory, and executes a single TOPAS process.
- New `PhantomConfig` dataclass (phantom data path, sex selection, supine placement offsets, organ scoring, graphics toggle) wired into `SimulationConfig` and YAML (de)serialization.
- New `phantomICRP145.j2` TOPAS include rendering a `TsTetGeom` phantom parented to `World`, positioned supine head-first on the configurable couch, with organ-dose scoring via `TsTetGeomScorer`.
- One added `{% if simulation_type == 'ICRP145' %}` include line in the main `headsourcecode_boilerplate.j2`; no change to shared beam/collimator geometry.
- Data pipeline: assemble `MRCP_{AM,AF}.node`/`.ele`/`.material` into a gitignored `data/` directory. The `.material` files (Geant4 syntax) are sourced from the P145 `MC_examples/MRCP_GEANT4.zip`, since `Phantom_data` ships only `_media.dat`.
- Build prerequisite: clone and build the third-party `OpenTOPAS/OpenTOPAS-MeshGeom` extension against the installed OpenTOPAS 4.2.p3 (registered via `TOPAS_EXTENSIONS_DIR`).
- GUI: third simulation-type dropdown entry, a phantom input tab, run-button/key wiring, and adapter plumbing.
- Orchestrator `_get_mode` extended from if/else to dispatch the third mode; the existing CTDI fallback for unrecognized types is preserved.
- Tests mirroring `test_dicom_mode.py` plus an orchestrator dispatch test for `ICRP145`.

## Capabilities

### New Capabilities

- `phantom-simulation-mode`: Selecting, configuring, rendering, and executing an ICRP 145 reference-phantom CT dose run as a third `SimulationMode` — the `ICRP145` enum member, `PhantomConfig`, orchestrator dispatch, `PhantomMode` strategy, GUI tab/keys/adapter, and unit tests.
- `reference-phantom-geometry`: The TOPAS geometry and scoring for the ICRP 145 tetrahedral mesh lying supine on the couch — the `TsTetGeom` component and its `.node`/`.ele`/`.material` data, the supine positioning/rotation, couch integration, and `TsTetGeomScorer` organ-dose scoring.

### Modified Capabilities

None. No capability specs exist yet; this change introduces them.

## Impact

- **Code**: `src/models/enums.py`, `src/config.py`, `src/orchestrator.py`, new `src/modes/phantom_mode.py`, new `src/boilerplates/TOPAS_includeFiles/phantomICRP145.j2`, one conditional in `src/boilerplates/headsourcecode_boilerplate.j2`, `src/gui/{view,controller,adapter}.py`, `src/models/keys.py`, and new tests under `tests/`.
- **Runtime/infra**: Requires OpenTOPAS (not stock TOPAS) and a built `OpenTOPAS-MeshGeom` extension; budget ~10 GB RAM per run. No change to DICOM/CTDI execution paths.
- **Data**: 2.6 GB of ICRP 145 phantoms live in a gitignored `data/P145/`; each user downloads from icrp.org (the data is not freely redistributable, so it is never committed).
- **Breaking**: None to existing modes. DICOM and CTDI behavior, templates, and tests are untouched.
