## Context

MC-DCaRE runs CT dose simulations via an Orchestrator + Strategy pattern. `SimulationMode` (abstract, `src/modes/base.py`) has two implementations: `DicomMode` (patient DICOM, single `TsDicomPatient` process) and `CtdiMode`. The orchestrator's core pipeline (`_run_off_mode`) is generic: it calls `build_main_context` → renders the main template → `build_sub_context` → renders a sub-include → `compute_histories` → `prepare_run` → `execute`. Mode selection is a hard-coded `if/else` in `_get_mode` (anything not `"DICOM"` returns `CtdiMode`).

The ICRP 145 "P145 Electronic files" package (downloaded, 1.88 GB; extracted to gitignored `data/P145/`) provides Adult Male/Female reference phantoms as TetGen tetrahedral meshes. Verified facts from the data:
- Units are **centimeters**; the body height runs along native **Z** (AM Z-span = 176.0 cm, AF = 163.0 cm), X is left/right (±28 cm), Y is anterior/posterior (±14 cm). Origin is near body center; posture is standing.
- Mesh size: AM = 1,222,593 nodes / 8,233,413 tets; AF similar. Each tet carries an organ ID (`.ele` 5th column) mapping into a ~141-medium ICRP tissue set (`_media.dat`).
- `Phantom_data` ships `_media.dat`, `_bone.dat`, `_blood.dat` but **no `.material`**. The Geant4 example (`MC_examples/MRCP_GEANT4.zip`) ships `MRCP_AM.material` / `MRCP_AF.material` in standard Geant4 material syntax (`m100 1000 -0.104` = material 100, element H, mass fraction 0.104). `TsTetGeom` is built on that example and reads `.node` + `.ele` + `.material` from one directory.

Runtime: OpenTOPAS 4.2.p3 is installed at `/opt/topas/TOPAS/OpenTOPAS-install/bin/topas`. Extensions register via the `TOPAS_EXTENSIONS_DIR` cmake variable (nBio is already built this way). The third-party `OpenTOPAS/OpenTOPAS-MeshGeom` extension (component `TsTetGeom`) is **not yet built** and is a prerequisite.

## Goals / Non-Goals

**Goals:**
- A third `SimulationMode` (`PhantomMode`, type `ICRP145`) that runs an ICRP 145 tet-mesh phantom supine on the couch under the existing beam geometry, scoring organ dose, behaving like a "reference DICOM" run.
- Full integration with config, YAML, orchestrator dispatch, GUI, and tests, parallel to DICOM/CTDI.
- Zero impact on existing DICOM/CTDI behavior, templates, and tests.

**Non-Goals:**
- No voxelized-phantom path (the whole point is tet-mesh fidelity).
- No changes to CTDI/DICOM scorers, post-processing services, or calibration.
- No DICOM-grid dose output; tet-mesh organ dose is CSV-based.
- No committing or redistributing ICRP data.
- No pediatric/pregnant phantoms (P145 reference adults only for this change).

## Decisions

### Decision 1: Tetrahedral mesh via `TsTetGeom` (not voxelization or GDML)
Transport the mesh directly using the OpenTOPAS-MeshGeom extension's `TsTetGeom` component.
- **Why**: P145 ships tets ready-to-use; tet transport preserves sub-mm source/target regions (lens, mucosa, skin) that voxelization destroys; `TsTetGeom` is purpose-built for the `.node/.ele/.material` layout; ~150–800× faster than raw tessellated surfaces (Yeom 2014).
- **Alternatives**: (a) Voxelize → `TsImageCube` + `MaterialTagNumber` on stock TOPAS — rejected: P145 ships no voxels (those are ICRP 110), a 1 mm full-body volume is ~100M+ voxels, and sub-mm organs are lost. (b) GDML tessellated — rejected: order-of-magnitude slower, `TsTetGeom` does not consume GDML.

### Decision 2: New `PhantomMode` strategy mirroring `DicomMode` shape
A single main template + single sub-include + single TOPAS process, exactly like DICOM. `build_main_context` sets `"simulation_type": "ICRP145"` plus the shared rotation/geometry vars already consumed by `headsourcecode_boilerplate.j2`.
- **Why**: The orchestrator's `_run_off_mode` pipeline is already generic; a conformant mode needs **no** orchestrator core changes beyond extending `_get_mode`.
- **Alternatives**: Extend `DicomMode` with geometry-type branching — rejected: different data source, geometry component, scorer, and config; branching would violate the Strategy isolation the modes directory is built around.

### Decision 3: Both phantom and couch parented to `World`, couch-top as the vertical datum
The phantom sits stationary (parented to `World`) while the gantry `Rotation` group spins, identical to how CTDI/DICOM parent their phantoms. Placement offsets are expressed relative to the couch top so the posterior rests on it.
- **Why**: Matches the proven parenting pattern and avoids coupling the phantom to gantry rotation.
- **Alternatives**: Parent phantom to a moving group — rejected: a reference patient must be stationary like a real CT patient.

### Decision 4: Supine rotation derived from the verified native axes, finalized empirically
Native axes are known (Z = height, cm, standing). The template applies a 90° rotation mapping body-height to the scanner long axis plus a vertical translation from posterior surface to couch top. Because the exact rotation sign depends on which way the phantom "faces", the final value is confirmed by dumping the bounding box at first geometry load and is exposed as tunable `PhantomConfig` offsets.
- **Why**: Avoids hard-coding an unverified transform; offsets stay user-tunable for couch-top height variation.
- **Alternatives**: Bake a fixed transform — rejected until verified, since a wrong sign puts the phantom face-down or standing.

### Decision 5: `.material` sourced from the Geant4 example, with a generator fallback
Use the ready-made `MRCP_{AM,AF}.material` from `MRCP_GEANT4.zip` (Geant4 syntax, proven). Provide a small script to regenerate `.material` from `_media.dat` as a self-contained fallback.
- **Why**: The extension expects `.material`; generation from `_media.dat` would only replicate what the example already provides. The fallback removes the dependency on the example zip.
- **Alternatives**: Require users to build `.material` themselves — rejected as poor UX.

### Decision 6: `PhantomConfig` frozen dataclass, added to `SimulationConfig` + YAML sections
Follow the `DicomConfig`/`CtdiConfig` pattern: a frozen dataclass with a `_<NAME>_Q_FIELDS` tuple for `Quantity` coercion in `__post_init__`, added as the `phantom` field, and added to the section tuples in `to_yaml`/`from_yaml`.
- **Why**: Consistency with the existing configuration architecture and project conventions (frozen models, `Quantity`-typed dimensions).

### Decision 7: GUI as a three-way dispatch from the existing two-way toggle
Extend the simulation-type combo with `"ICRP145"`, add a `PHANTOM_TAB`, and convert `set_tab_visibility` from a boolean to a multi-way visibility setter. The run path stays driven by `simulation_type` (not by which button).
- **Why**: Minimal disruption; the run pipeline already keys off `simulation_type`.

## Risks / Trade-offs

- **Requires OpenTOPAS + a built extension, not stock TOPAS** → Document the exact clone/build steps (cmake `TOPAS_EXTENSIONS_DIR` pointing at the MeshGeom tree, rebuild). Keep tests render-only / dry-run so they pass without the binary or data (matching how existing tests mock TOPAS).
- **`TsTetGeom` exact parameter names unverified for this extension version** (e.g. `Age`/`Sex` shortcut vs explicit `NodeFile`/`EleFile`/`MaterialFile`, and whether `.material` is auto-discovered) → Confirm against the built extension source at implementation; design the template so file paths are explicit and overridable.
- **Supine rotation sign** → Confirm via a `Ts/PauseBeforeQuit` bounding-box dump on first load; keep offsets tunable.
- **Phantom/couch overlap** → Give the couch real thickness (not a zero-thickness shell), keep a small gap at the posterior, and run Geant4's overlap check before the first real run.
- **Runtime cost** (~10 GB RAM; tet tracking slower than voxel) → Document hardware guidance and a conservative default history count; tet fidelity is the accepted trade-off.
- **Large data not redistributable** → `data/` is gitignored; each user downloads from icrp.org. A documented setup step assembles `MRCP_{AM,AF}.node/.ele/.material` into the configured directory.

## Migration Plan

Additive change; existing runs and configs are unaffected. To enable: build the MeshGeom extension, populate `data/P145`, and select `ICRP145` in the GUI (or set `simulation_type: ICRP145` in YAML). Rollback is reverting the new files and the small edits to `enums.py`, `config.py`, `orchestrator.py`, the main template conditional, and the GUI; DICOM/CTDI continue to work unchanged.

## Open Questions

- Does the installed `TsTetGeom` support the `Age`/`Sex` shortcut, or must `NodeFile`/`EleFile`/`MaterialFile` be stated explicitly? (Resolve against the built extension.)
- Is the scorer quantity named `TsTetGeomScorer` in this version (vs the README's `TsTetGeom`)? (Resolve against extension examples.)
- Default organ set for the first scorer — a single whole-body dose scorer plus a configurable organ list?
- Should the supine offset default assume the existing couch dimensions, or read them from `PhantomConfig` (preferred)?
