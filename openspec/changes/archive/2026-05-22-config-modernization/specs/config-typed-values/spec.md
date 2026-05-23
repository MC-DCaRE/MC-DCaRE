## MODIFIED Requirements

### Requirement: Dimensional config fields use Quantity type

All config fields representing physical quantities (lengths, angles, voltages, exposures) MUST be stored as `Quantity` objects with numeric value and unit string. Validation MUST occur at config construction time.

#### Scenario: Valid dimensional value from YAML
- **WHEN** YAML contains `anode_voltage: "100 kV"`
- **THEN** `config.imaging.anode_voltage` is a `Quantity(100.0, "kV")`

#### Scenario: Invalid dimensional value from YAML
- **WHEN** YAML contains `isocenter_x: "banana"`
- **THEN** config construction raises `ValueError` with field name and invalid value

#### Scenario: Quantity serializes to YAML
- **WHEN** `config.to_yaml(path)` is called
- **THEN** dimensional fields are written as `"100 kV"` strings (backward compatible)

### Requirement: SimulationConfig is immutable

`SimulationConfig` and all sub-configs MUST use `frozen=True`. Modification after construction MUST raise `FrozenInstanceError`.

#### Scenario: Attempt to mutate config
- **WHEN** `config.imaging.simulation_type = "banana"` is called
- **THEN** `FrozenInstanceError` is raised
