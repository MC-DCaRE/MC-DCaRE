## MODIFIED Requirements

### Requirement: Patient orientation supports pitch, roll, and yaw

DICOM mode MUST support all three patient rotation axes: pitch (RotX), yaw (RotY), and roll (RotZ). All values MUST default to `0 deg`.

#### Scenario: Non-zero yaw in DICOM mode
- **WHEN** `patient_yaw` is set to `"5 deg"` in config
- **THEN** the rendered template has `dc:Ge/Rotation/RotY= 180. deg + 5 deg`

#### Scenario: Non-zero pitch in DICOM mode
- **WHEN** `patient_pitch` is set to `"2 deg"` in config
- **THEN** the rendered template has `dc:Ge/Rotation/RotX= 2 deg`

#### Scenario: Roll combined with time feature
- **WHEN** `patient_roll` is set to `"1 deg"` in config
- **THEN** the rendered template RotZ combines roll with rotation time feature

#### Scenario: CTDI mode ignores rotations
- **WHEN** a CTDI simulation runs with pitch/roll/yaw in config
- **THEN** the rendered template has no patient rotation applied
