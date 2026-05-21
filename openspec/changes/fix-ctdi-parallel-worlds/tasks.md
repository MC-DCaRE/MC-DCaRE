## 1. Fix SimulationType enum and GUI label

- [x] 1.1 Change `SimulationType.CTDI` value from `"CTDI validation"` to `"CTDI"` in `src/models/enums.py`
- [x] 1.2 Update GUI combo box in `src/gui/view.py` to use `"CTDI"` as value and update `set_tab_visibility`
- [x] 1.3 Update example YAML configs (`ctdi_example.yaml`, `kvk_example.yaml`, `ctdi_calibration_example.yaml`) to use `CTDI`
- [x] 1.4 Update `tests/unit/test_enums.py`, `test_config.py`, `test_orchestrator.py`, `test_gui_view.py`, `test_gui_controller.py`, `test_dry_run_pipeline.py`, and `shared.py` for new enum value

## 2. Fix CTDI context builder for parallel worlds

- [x] 2.1 `CtdiMode.build_sub_context()` already provides `plug_positions` as a list (done in prior session)
- [x] 2.2 `plug_material_*` variables already removed from context (done in prior session)
- [x] 2.3 `tests/unit/test_ctdi_mode.py` and `tests/unit/shared.py` context constants updated

## 3. Replace 5-run CTDI with single run

- [x] 3.1 `CtdiMode._generate_plug_files()` already removed (done in prior session)
- [x] 3.2 `CtdiMode.execute()` already concatenates rendered headsource + phantom into single file (done in prior session)
- [x] 3.3 `SimulationRunner.run_ctdi()` already accepts single combined file path (done in prior session)
- [x] 3.4 `CtdiMode.prepare_run()` already stages combined file (done in prior session)
- [x] 3.5 `tests/unit/test_ctdi_mode.py` already tests single-run behavior (done in prior session)
- [x] 3.6 `tests/unit/test_simulation_runner.py` already tests new `run_ctdi` signature (done in prior session)

## 4. Verify end-to-end

- [x] 4.1 Run full test suite — 319 passed
- [x] 4.2 Run `ruff format`, `ruff check`, `mypy` on changed files — all clean
