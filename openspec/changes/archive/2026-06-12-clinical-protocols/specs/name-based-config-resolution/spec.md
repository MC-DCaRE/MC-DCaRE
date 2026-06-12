## ADDED Requirements

### Requirement: Resolution from protocol name
The system SHALL resolve a protocol name (`rotation_direction` + `imaging_mode`) into an `ImagingMode` entry and auto-populate `ImagingConfig` and `CtdiConfig` fields from the mode's values. The resolution function `_resolve_imaging_mode()` SHALL operate on raw YAML dicts before dataclass construction.

#### Scenario: Valid CBCT protocol resolves all mapped fields
- **WHEN** `imaging_data` contains `rotation_direction: "CBCT Clockwise"` and `imaging_mode: "Head"`
- **THEN** the function populates all 15 mapped fields in `imaging_data` and `ctdi_data` from `IMAGING_MODES["CBCT Clockwise_Head"]`

#### Scenario: Invalid protocol name raises ValueError
- **WHEN** `imaging_data` contains `rotation_direction: "CBCT Clockwise"` and `imaging_mode: "NonExistent"`
- **THEN** the function raises `ValueError` listing all valid mode keys

#### Scenario: Anticlockwise direction resolves correctly
- **WHEN** `imaging_data` contains `rotation_direction: "CBCT Anticlockwise"` and `imaging_mode: "Thorax"`
- **THEN** the function resolves `IMAGING_MODES["CBCT Anticlockwise_Thorax"]`

#### Scenario: Missing rotation_direction raises ValueError
- **WHEN** `imaging_data` does not contain the key `rotation_direction`
- **THEN** the function raises `ValueError` with a message indicating the missing key

#### Scenario: kV-kV direction raises ValueError
- **WHEN** `imaging_data` contains `rotation_direction: "kV-kV"`
- **THEN** the function raises `ValueError` because resolution is only supported for CBCT directions

### Requirement: YAML overrides win over mode defaults
The system SHALL preserve explicit YAML values over mode defaults. If a YAML dict key is present and its value is not `None` or empty string, the YAML value SHALL be used. If the YAML dict key is absent or its value is `None` or empty string, the mode default SHALL populate the field.

#### Scenario: YAML value overrides mode default
- **WHEN** `imaging_data` contains `anode_voltage: "80 kV"` and the resolved mode has `voltage: "100 kV"`
- **THEN** the resulting `imaging_data["anode_voltage"]` SHALL be `"80 kV"`

#### Scenario: Absent YAML key falls back to mode default
- **WHEN** `imaging_data` does not contain the key `rotation_rate`
- **THEN** the resulting `imaging_data["rotation_rate"]` SHALL be the mode's `rotation_rate` value

#### Scenario: Null YAML value falls back to mode default
- **WHEN** `imaging_data` contains `exposure: null`
- **THEN** the resulting `imaging_data["exposure"]` SHALL be the mode's `exposure` value

#### Scenario: Empty string YAML value falls back to mode default
- **WHEN** `imaging_data` contains `exposure: ""`
- **THEN** the resulting `imaging_data["exposure"]` SHALL be the mode's `exposure` value

### Requirement: Mapping of 15 fields from mode to config
The system SHALL map exactly these mode fields to config dict keys:

| Mode field | Target dict | Target key |
|---|---|---|
| `voltage` | `imaging_data` | `anode_voltage` |
| `ctdi_phantom` | `ctdi_data` | `phantom_size` |
| `start_angle` | `imaging_data` | `start_angle` |
| `rotation_rate` | `imaging_data` | `rotation_rate` |
| `timeline_end` | `imaging_data` | `timeline_end` |
| `fan_mode` | `imaging_data` | `fan_mode` |
| `field_x1` | `imaging_data` | `field_x1` |
| `field_x2` | `imaging_data` | `field_x2` |
| `field_y1` | `imaging_data` | `field_y1` |
| `field_y2` | `imaging_data` | `field_y2` |
| `blade_x1` | `imaging_data` | `blade_x1` |
| `blade_x2` | `imaging_data` | `blade_x2` |
| `blade_y1` | `imaging_data` | `blade_y1` |
| `blade_y2` | `imaging_data` | `blade_y2` |
| `exposure` | `imaging_data` | `exposure` |

Fields NOT mapped: `dose_factor`, `fan_detail`, `no_projections`, `proj_increment`, `acquisition_time`, `ctdiw_reference`. These are metadata fields not auto-populated into config dicts.

#### Scenario: All 15 fields populated for minimal YAML
- **WHEN** `imaging_data` contains only `rotation_direction`, `imaging_mode`, and `simulation_type`
- **THEN** the resolution populates all 15 target keys from the mode

#### Scenario: ctdi_phantom maps to phantom_size in ctdi_data
- **WHEN** the resolved mode has `ctdi_phantom: "16 cm"`
- **THEN** `ctdi_data["phantom_size"]` SHALL be `"16 cm"`

### Requirement: dose_factor excluded from mapping
The resolution function SHALL NOT map `ImagingMode.dose_factor` to any target dict key. The `dose_factor` field is metadata only and is not written to `imaging_data` or `ctdi_data`.

#### Scenario: dose_factor not present in resolution output
- **WHEN** the resolved mode has `dose_factor: "0.87"`
- **THEN** neither returned dict SHALL contain a `dose_factor` or `dose_calibration_factor` key that originated from resolution

### Requirement: Value format compatibility with Quantity parsing
The system SHALL ensure all mode field values that map to `Quantity`-typed config fields use Quantity-parseable format with units. `ctdi_phantom` values SHALL exactly match `PhantomSize` enum values.

#### Scenario: start_angle value parses as Quantity
- **WHEN** the resolved mode has `start_angle: "0 deg"`
- **THEN** `Quantity.parse("0 deg")` SHALL succeed

#### Scenario: ctdi_phantom matches PhantomSize enum
- **WHEN** the resolved mode has `ctdi_phantom: "32 cm"`
- **THEN** `"32 cm"` SHALL be a valid `PhantomSize` enum value

### Requirement: Backward compatibility with full-format YAML
The system SHALL accept existing YAML files that specify all beam parameters explicitly. The resolution function SHALL not override any value that is already present and non-empty in the YAML dict.

#### Scenario: Existing full-format YAML unchanged
- **WHEN** an existing `ctdi_config.yaml` specifies all 13 original beam parameters explicitly
- **THEN** all YAML values SHALL be preserved as-is after resolution

### Requirement: Integration with from_yaml
`_resolve_imaging_mode()` SHALL be called from `from_yaml()` after `yaml.safe_load()` returns raw dicts but before dataclass construction.

#### Scenario: Minimal YAML produces fully populated SimulationConfig
- **WHEN** `from_yaml()` loads a YAML containing only `rotation_direction: "CBCT Clockwise"`, `imaging_mode: "Head"`, and `simulation_type: "CTDI"`
- **THEN** the resulting `SimulationConfig.imaging` SHALL have all beam parameters populated from the resolved mode
