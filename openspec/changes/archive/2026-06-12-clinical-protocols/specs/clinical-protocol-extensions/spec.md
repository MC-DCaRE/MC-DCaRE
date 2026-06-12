## ADDED Requirements

### Requirement: ImagingMode dataclass has 21 fields
The `ImagingMode` frozen dataclass SHALL have exactly 21 string fields. The 8 new fields appended after the existing 13 SHALL be: `ctdi_phantom`, `dose_factor`, `start_angle`, `fan_detail`, `no_projections`, `proj_increment`, `acquisition_time`, `ctdiw_reference`.

#### Scenario: All 21 fields accessible
- **WHEN** an `ImagingMode` instance is created for `"CBCT Clockwise_Head"`
- **THEN** all 21 fields SHALL be accessible as attributes with non-empty string values

#### Scenario: Existing 13 fields unchanged
- **WHEN** the existing `"CBCT Clockwise_Head"` entry is accessed
- **THEN** the 13 original fields (rotation_rate, voltage, exposure, fan_mode, timeline_end, field_x1, field_x2, field_y1, field_y2, blade_x1, blade_x2, blade_y1, blade_y2) SHALL have the same values as before the change

### Requirement: IMAGING_MODES has 47 entries
`IMAGING_MODES` dict SHALL contain exactly 47 entries: 20 CBCT Clockwise + 20 CBCT Anticlockwise + 7 kV-kV.

#### Scenario: Entry count matches
- **WHEN** `len(IMAGING_MODES)` is evaluated
- **THEN** it SHALL equal 47

#### Scenario: All 13 new protocols exist in both directions
- **WHEN** checking for keys `"CBCT Clockwise_4D Spotlight"` and `"CBCT Anticlockwise_4D Spotlight"`
- **THEN** both keys SHALL exist in `IMAGING_MODES`

### Requirement: Thirteen new CBCT protocols
The following 13 new protocols SHALL be added to `IMAGING_MODES`, each with both Clockwise and Anticlockwise directions:
1. 4D Spotlight
2. 4D Thorax
3. Abdomen
4. Abdo Spotlight
5. Breast 360
6. Extremity Spotlight
7. Head and Shoulders
8. Head SRS
9. Paediatric Body
10. Pediatric Head
11. Pelvis Spotlight
12. SBRT Spine
13. Thorax Spotlight

#### Scenario: New protocol entry has all 21 fields
- **WHEN** `IMAGING_MODES["CBCT Clockwise_Abdomen"]` is accessed
- **THEN** all 21 fields SHALL be populated with string values

#### Scenario: Protocol key format
- **WHEN** looking up `"CBCT Clockwise_Breast 360"`
- **THEN** the key SHALL be present and resolve to a valid `ImagingMode` instance

### Requirement: Existing entries updated with 8 new fields
All 21 existing entries SHALL receive values for the 8 new fields. CBCT entries SHALL use real clinical values from Varian specifications. kV-kV entries SHALL use `"N/A"` for CBCT-specific fields (`ctdi_phantom`, `fan_detail`, `dose_factor`, `no_projections`, `proj_increment`, `acquisition_time`, `ctdiw_reference`) and `"0 deg"` for `start_angle`.

#### Scenario: Existing CBCT entry has real clinical values
- **WHEN** `IMAGING_MODES["CBCT Clockwise_Head"]` is accessed
- **THEN** `ctdi_phantom` SHALL be `"16 cm"` (matching PhantomSize enum) and `start_angle` SHALL be Quantity-parseable

#### Scenario: kV-kV entry has N/A values
- **WHEN** `IMAGING_MODES["kV-kV_Head"]` is accessed
- **THEN** `ctdi_phantom` SHALL be `"N/A"` and `start_angle` SHALL be `"0 deg"`

### Requirement: as_tuple returns 21 items
`ImagingMode.as_tuple()` SHALL return a tuple of exactly 21 string elements in field declaration order.

#### Scenario: Tuple length matches field count
- **WHEN** `mode.as_tuple()` is called on any `ImagingMode` instance
- **THEN** `len(result)` SHALL equal 21

### Requirement: IMAGING_MODE_SELECTION_LABELS has 21 labels
`IMAGING_MODE_SELECTION_LABELS` SHALL be a list of exactly 21 strings. The 8 new labels SHALL be: `"Phantom"`, `"Dose Factor"`, `"Start Angle"`, `"Fan Detail"`, `"Projections"`, `"Proj Increment"`, `"Acq Time"`, `"CTDIw Ref"`.

#### Scenario: Labels count matches fields
- **WHEN** `len(IMAGING_MODE_SELECTION_LABELS)` is evaluated
- **THEN** it SHALL equal 21

### Requirement: BACKWARD_COMPAT_LOOKUP has 48 entries
`BACKWARD_COMPAT_LOOKUP` SHALL have 1 `"selection"` key + 47 mode keys = 48 entries. Each mode entry's value SHALL be a list of 21 items (matching `as_tuple()` output).

#### Scenario: Lookup entry count
- **WHEN** `len(BACKWARD_COMPAT_LOOKUP)` is evaluated
- **THEN** it SHALL equal 48

#### Scenario: Per-entry list length
- **WHEN** `BACKWARD_COMPAT_LOOKUP["CBCT Clockwise_Head"]` is accessed
- **THEN** `len(result)` SHALL equal 21

### Requirement: GUI dropdown shows 20 CBCT protocols
The GUI protocol dropdown SHALL display 20 unique CBCT protocol names, dynamically extracted from `IMAGING_MODES` keys (filtering to CBCT keys only, stripping direction prefix, deduplicating).

#### Scenario: Dropdown has 20 items
- **WHEN** the GUI dropdown is populated
- **THEN** it SHALL contain exactly 20 protocol names

#### Scenario: kV-kV protocols excluded from dropdown
- **WHEN** the dropdown list is generated
- **THEN** no kV-kV protocol names SHALL appear
