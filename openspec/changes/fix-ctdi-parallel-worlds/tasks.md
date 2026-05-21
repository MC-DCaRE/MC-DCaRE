## 1. Fix SimulationType enum and GUI label

- [ ] 1.1 Change `SimulationType.CTDI` value from `"CTDI validation"` to `"CTDI"` in `src/models/enums.py`
- [ ] 1.2 Update GUI combo box in `src/gui/view.py` to display `"CTDI validation"` as label with `"CTDI"` as value
- [ ] 1.3 Update `config.py` default for `simulation_type` from `"DICOM"` behavior check (verify orchestrator still routes correctly)
- [ ] 1.4 Update `tests/unit/test_enums.py` and `tests/unit/test_config.py` for new enum value

## 2. Fix CTDI context builder for parallel worlds

- [ ] 2.1 Modify `CtdiMode.build_sub_context()` to provide `plug_positions` as a list `["ChamberPlugCentre", "ChamberPlugTop", ...]` instead of singular `plug_position`
- [ ] 2.2 Remove `plug_material_*` variables from context (template hardcodes all plugs as Air)
- [ ] 2.3 Update `tests/unit/test_ctdi_mode.py` and `tests/unit/shared.py` context constants

## 3. Replace 5-run CTDI with single run

- [ ] 3.1 Remove `CtdiMode._generate_plug_files()` method
- [ ] 3.2 Update `CtdiMode.execute()` to concatenate rendered headsource + phantom into a single file and run one TOPAS process
- [ ] 3.3 Update `SimulationRunner.run_ctdi()` to accept single combined file path
- [ ] 3.4 Update `CtdiMode.prepare_run()` to stage the combined file instead of 5 separate plug files
- [ ] 3.5 Update `tests/unit/test_ctdi_mode.py` for single-run behavior
- [ ] 3.6 Update `tests/unit/test_simulation_runner.py` for new `run_ctdi` signature

## 4. Verify end-to-end

- [ ] 4.1 Run full test suite and confirm all tests pass
- [ ] 4.2 Run `ruff format`, `ruff check`, `mypy` on changed files
