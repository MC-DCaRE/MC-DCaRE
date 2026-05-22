## 1. Enhance Quantity type

- [x] 1.1 Add `to_topas_string()` method in `Quantity.__str__()` for Jinja2 context rendering (e.g., `"100 kV"`)
- [x] 1.2 Add `__str__()` returning `"100 kV"` format with repr-based precision
- [x] 1.3 Add `__eq__()` and `__hash__()` for frozen dataclass compatibility
- [x] 1.4 Update `tests/unit/test_quantity.py` for new methods

## 2. Convert config fields to Quantity

- [x] 2.1 Convert dimensional fields in `ImagingConfig` to `Quantity` (start_angle, rotation_rate, timeline_end, anode_voltage, exposure, field_x1/x2/y1/y2, blade_x1/x2/y1/y2)
- [x] 2.2 Convert dimensional fields in `DicomConfig` to `Quantity` (isocenter_x/y/z, patient_shift_x/y/z, patient_yaw)
- [x] 2.3 Convert dimensional fields in `CtdiConfig` to `Quantity` (couch_width/thickness/length, user_field_x1/x2/y1/y2)
- [x] 2.4 Make `SimulationConfig` frozen=True
- [x] 2.5 Update `from_yaml()` to parse strings into `Quantity` via `__post_init__` auto-coercion
- [x] 2.6 Update `to_yaml()` to serialize `Quantity` to strings
- [x] 2.7 Add dimensional validation in `validate()` for `anode_voltage` and `exposure`

## 3. Create GUI adapter

- [ ] 3.1 Create `src/gui/adapter.py` with `config_to_gui()` and `gui_to_config()` methods
- [ ] 3.2 Move `_PLACEHOLDER_MAP` and `_BOOL_FIELDS` from `config.py` to `adapter.py`
- [ ] 3.3 Update `src/gui/controller.py` to use adapter instead of `SimulationConfig.from_gui_values()`
- [ ] 3.4 Remove `from_gui_values()` and `to_dict()` from `SimulationConfig`
- [ ] 3.5 Remove `keys.py` imports from `config.py`

## 4. Update consumers

- [x] 4.1 Update `CtdiMode.build_main_context()` and `build_sub_context()` to read `Quantity` fields
- [x] 4.2 Update `DicomMode.build_main_context()` and `build_sub_context()` similarly
- [x] 4.3 SpectrumGenerator already receives `float` from orchestrator (`.value` extraction) — no change needed
- [x] 4.4 fieldtobladeopening already uses `Quantity.parse()` internally — callers wrap with `str()`
- [x] 4.5 Update `orchestrator.py` for typed parameter flow

## 5. Update tests

- [x] 5.1 Update `tests/unit/test_config.py` for `Quantity`-typed fields and frozen config
- [x] 5.2 Update `tests/unit/shared.py` context constants (file unused by tests, updated in place)
- [x] 5.3 Update `tests/unit/test_ctdi_mode.py` and `test_dicom_mode.py`
- [ ] 5.4 Update `tests/unit/test_gui_controller.py` for adapter usage (blocked on Group 3)
- [x] 5.5 Run full test suite, `ruff format`, `ruff check`, `mypy` — 320 pass, all clean
