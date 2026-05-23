## MODIFIED Requirements

### Requirement: CTDI simulation executes as a single TOPAS run

The CTDI simulation mode MUST render a single combined parameter file containing the headsource code and the phantom template with all 5 chamber plug positions scored simultaneously via TOPAS Parallel Worlds (Layered Mass Geometry). The template context MUST provide `plug_positions` as a list of all 5 position names to correctly render the 15 scorers (3 scorer types × 5 positions).

#### Scenario: Single run produces all plug dose data
- **WHEN** a CTDI simulation is executed
- **THEN** a single TOPAS process runs with one combined parameter file
- **AND** 15 output CSV files are produced (ChamberPlug{Position}_{type}.csv for each position and scorer type)

#### Scenario: Scorer section renders correctly
- **WHEN** the phantom template is rendered with `plug_positions` in the context
- **THEN** the output file contains 15 scorer definitions (3 per plug position)

### Requirement: SimulationType enum value matches template expectation

`SimulationType.CTDI` MUST have the value `"CTDI"` to match the headsourcecode template conditional `{% if simulation_type == 'CTDI' %}`. The GUI combo box MUST continue displaying the human-readable label `"CTDI validation"`.

#### Scenario: Enum value used in template
- **WHEN** `CtdiMode.build_main_context()` provides `simulation_type` from the enum
- **THEN** the value is `"CTDI"` matching the template conditional

#### Scenario: GUI displays human-readable label
- **WHEN** the GUI combo box shows simulation types
- **THEN** CTDI option displays as `"CTDI validation"`
