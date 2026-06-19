## 1. Environment & data prerequisites

- [ ] 1.1 **BLOCKED (user action):** Build the `OpenTOPAS/OpenTOPAS-MeshGeom` extension against OpenTOPAS 4.2.p3. Requires cloning the repo, cmake build, and OpenTOPAS rebuild in the user's environment. See "ICRP 145 Phantom Mode" section in README.md for instructions.
- [ ] 1.2 **BLOCKED (depends on 1.1):** Resolve the `TsTetGeom` parameter contract for this build (support for `Age`/`Sex` shortcut vs explicit `NodeFile`/`EleFile`/`MaterialFile`; whether `.material` is auto-discovered; the exact scorer name `TsTetGeomScorer`). Template currently uses explicit file paths as a safe default; adjust if the build supports shortcuts.
- [x] 1.3 Assemble the phantom data directory under `data/P145/Phantom_data/{MRCP_AM,MRCP_AF}/`: confirm `.node`/`.ele` are present, and add `MRCP_AM.material` / `MRCP_AF.material` sourced from `MC_examples/MRCP_GEANT4.zip`. Also write a small `_media.dat`-to-`.material` generator script as a self-contained fallback and verify its output matches the example file.
- [x] 1.4 Confirm `data/` is gitignored (rule added in this change) and that `git status` does not show any ICRP data files.

## 2. Enum & configuration

- [x] 2.1 Add `ICRP145 = "ICRP145"` to `SimulationType` in `src/models/enums.py`.
- [x] 2.2 Add a frozen `PhantomConfig` dataclass to `src/config.py` modeled on `DicomConfig`: `phantom_data_directory`, `phantom_sex` (`"AM"`/`"AF"`), placement offsets (`trans_x/y/z`, `rot_x/y/z`), couch params (`couch_enabled`, `couch_width/thickness/length`), `graphics_enabled`, and organ-scoring fields. Define `_PHANTOM_Q_FIELDS` for `Quantity` coercion in `__post_init__`.
- [x] 2.3 Add `phantom: PhantomConfig` to `SimulationConfig` (with `field(default_factory=PhantomConfig)`).
- [x] 2.4 Add `"phantom"` to the section tuples in `SimulationConfig.to_yaml` and `from_yaml`; verify round-trip preserves values.

## 3. TOPAS templates

- [x] 3.1 Create `src/boilerplates/TOPAS_includeFiles/phantomICRP145.j2`: a `TsTetGeom` phantom component parented to `"World"`, selecting `MRCP_AM`/`MRCP_AF` from `phantom_sex`, with explicit `.node`/`.ele`/`.material` from `phantom_data_directory`, emitting `Trans/Rot` from `PhantomConfig` (cm-native axes; supine head-first), a configurable couch `TsBox` also parented to `"World"` with a non-overlapping posterior gap, and a `TsTetGeomScorer` CSV scorer named with the DICOM-style convention.
- [x] 3.2 Add `{% if simulation_type == 'ICRP145' %}includeFile = phantomICRP145.txt{% endif %}` to `src/boilerplates/headsourcecode_boilerplate.j2` next to the DICOM/CTDI branches; leave all shared geometry untouched.

## 4. PhantomMode strategy

- [x] 4.1 Create `src/modes/phantom_mode.py` implementing `PhantomMode(SimulationMode)` mirroring `DicomMode`. `build_main_context` MUST return every variable the main template consumes (`headsourcecode_boilerplate.j2`): `simulation_type="ICRP145"`, `g4_data_directory`, `seed`, `threads`, `histories`, `sequential_times`, `timeline_end`, `rotation_rate`, `start_angle`, `coll1_trans_y`/`coll2_trans_y`/`coll3_trans_x`/`coll4_trans_x`, `fan_mode`, `graphics_enabled` (sourced from `PhantomConfig.graphics_enabled`, matching how DicomMode/CTDIMode source it from their own config), `phantom_size` (`""`), `patient_yaw`/`patient_pitch`/`patient_roll_value`, `rotation_direction`, `start_angle_value`, `second_angle_value`. `main_template_name` = `"headsourcecode_boilerplate.j2"`, `main_output_name` = `"headsourcecode.txt"`, `build_sub_context` returns the phantom params + formatted `output_filename`, `get_sub_file_name`/`get_sub_template_name` → `phantomICRP145.txt`/`phantomICRP145.j2`, `compute_histories` = `sequential_times * histories`, `prepare_run` stages the rendered files + `copy_common_files` (no DICOM-only artifacts), and `execute` runs a single TOPAS process.
- [x] 4.2 Add a `run_phantom` method to `src/simulation_runner.py` mirroring `run_dicom` (distinct log filename) if not reusing `run_dicom` directly; wire `PhantomMode.execute` to it.

## 5. Orchestrator dispatch

- [x] 5.1 Extend `Orchestrator._get_mode` in `src/orchestrator.py` from if/else to dispatch `PhantomMode` for `"ICRP145"`; import `PhantomMode`. Preserve the existing CTDI fallback for unrecognized types.

## 6. GUI integration

- [x] 6.1 Add GUI keys in `src/models/keys.py`: `PHANTOM_TAB`, `PHANTOM_RUN`, and field keys for each phantom input (data dir, sex, offsets, couch, graphics).
- [x] 6.2 In `src/gui/view.py`: add `"ICRP145"` to the simulation-type combo; add a `PHANTOM_TAB` with the phantom inputs; convert `set_tab_visibility` from a boolean toggle to a three-way dispatch that shows only the matching tab. Also update `reset_all` (currently `view.py:1003-1008`, which enumerates tabs by name) to hide `PHANTOM_TAB` — or refactor both methods to iterate a shared `[DICOM_TAB, CTDI_TAB, PHANTOM_TAB]` list so a tab is never missed on reset.
- [x] 6.3 In `src/gui/adapter.py`: map phantom GUI keys to/from `PhantomConfig` in `_PLACEHOLDER_MAP`, and extend `gui_to_config`/`config_to_gui` to pass `phantom=PhantomConfig(...)`.
- [x] 6.4 In `src/gui/controller.py`: register the `PHANTOM_RUN` handler (routes through the existing `_on_run` path) and the tab-visibility event.

## 7. Tests

- [x] 7.1 Add `tests/unit/test_phantom_mode.py` mirroring `test_dicom_mode.py`: main context sets `simulation_type="ICRP145"`, history math, sub context fields, template/file-name selection, `prepare_run` copies expected files (mocked), `execute` calls the runner once.
- [x] 7.2 Add an orchestrator dispatch test for `ICRP145` → `PhantomMode` in `tests/unit/test_orchestrator.py`; keep the "unknown type → CtdiMode" fallback test green.
- [x] 7.3 Add a `TestPhantomConfig` block (defaults valid, Quantity coercion, YAML round-trip) to `tests/unit/test_config.py`.
- [x] 7.4 Add a render-only test asserting `phantomICRP145.j2` emits `Type = "TsTetGeom"` on the phantom component with `Parent = "World"`, the correct `MRCP_{AM,AF}` selection, and a `TsTetGeomScorer` scorer; assert the couch's top-level parent resolves to `"World"` (permit an intermediate group like the CTDI `couchgroup`, so don't substring-match the couch line directly); and that the main template emits `includeFile = phantomICRP145.txt` only for `ICRP145`.
- [x] 7.5 Add an ICRP145 branch to `tests/integration/test_dry_run_pipeline.py` exercising the full orchestration in dry-run (no TOPAS).

## 8. Verification

- [x] 8.1 Run the pipeline in order: `uv run ruff format src/ tests/`, `uv run ruff check src/ tests/ --fix`, `rm -rf .mypy_cache && uv run mypy src/`, `uv run python -m pytest tests/ -v`. Fix until all pass.
- [x] 8.2 Update affected `AGENTS.md` files (`src/AGENTS.md`, `src/modes/AGENTS.md`, `src/boilerplates/AGENTS.md`, `tests/AGENTS.md`) to document the new mode, template, and config section.
- [x] 8.3 Document the user setup steps (build MeshGeom extension; download + assemble ICRP data) in the appropriate docs/config reference.
