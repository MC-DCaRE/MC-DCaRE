## 1. Add pitch/roll fields to config and keys

- [ ] 1.1 Add `patient_pitch: Quantity` and `patient_roll: Quantity` to `DicomConfig` (default `0 deg`)
- [ ] 1.2 Add `PATIENT_PITCH` and `PATIENT_ROLL` to `src/models/keys.py`
- [ ] 1.3 Update `examples/config/dicom_example.yaml` with pitch/roll defaults

## 2. Wire rotations into template and mode

- [ ] 2.1 Update `headsourcecode_boilerplate.j2` to use `{{ patient_pitch }}`, `{{ patient_yaw }}`, and combine `{{ patient_roll }}` with time feature on RotZ
- [ ] 2.2 Update `DicomMode.build_main_context()` to pass `patient_pitch`, `patient_roll`, `patient_yaw`
- [ ] 2.3 Remove hardcoded `d:Ge/patrotation/yaw= 0 deg` from template

## 3. Add GUI inputs

- [ ] 3.1 Add pitch and roll input fields to `_build_dicom_patient_layer()` in `view.py`
- [ ] 3.2 Update `GUIAdapter` (from config-modernization) with pitch/roll mapping

## 4. Update tests

- [ ] 4.1 Update `tests/unit/test_dicom_mode.py` for pitch/roll/yaw context
- [ ] 4.2 Update `tests/unit/shared.py` DICOM context constants
- [ ] 4.3 Update `tests/unit/test_template_renderer.py` if rotation variables are tested
- [ ] 4.4 Run full test suite, `ruff format`, `ruff check`, `mypy`
