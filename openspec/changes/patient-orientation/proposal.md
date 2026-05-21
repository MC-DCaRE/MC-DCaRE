## Why

The headsourcecode template has `d:Ge/patrotation/yaw= 0 deg` hardcoded. The DICOM mode context builder creates `patient_yaw` but never passes it to the main template. Patient orientation support is limited to yaw only, with no pitch or roll. For accurate DICOM patient dose calculations, all three rotation axes are needed to model patient setup variations.

## What Changes

- Add `patient_pitch` and `patient_roll` fields to `DicomConfig` alongside existing `patient_yaw`
- Wire all three rotations into the headsourcecode template via Jinja2 variables
- Add GUI inputs for pitch and roll
- Update DICOM mode context builder to pass rotation values

**Depends on**: `config-modernization` (uses `Quantity`-typed fields for pitch/roll/yaw)

## Capabilities

### Modified Capabilities
- `patient-orientation`: Full 3-axis rotation (yaw + pitch + roll) replaces yaw-only

## Impact

- `src/config.py` — add pitch/roll fields to `DicomConfig`
- `src/boilerplates/headsourcecode_boilerplate.j2` — parameterize rotation components
- `src/modes/dicom_mode.py` — include rotations in context
- `src/gui/view.py` — add pitch/roll input fields
- `src/models/keys.py` — add GUI key constants
- `examples/config/dicom_example.yaml` — add pitch/roll defaults
