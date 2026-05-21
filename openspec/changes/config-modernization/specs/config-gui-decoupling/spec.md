## ADDED Requirements

### Requirement: GUI adapter decouples config from element keys

A `GUIAdapter` class MUST own the mapping between `SimulationConfig` fields and FreeSimpleGUI element keys. `SimulationConfig` MUST NOT import from `keys.py`.

#### Scenario: Config to GUI values
- **WHEN** `adapter.config_to_gui(config)` is called
- **THEN** returns `Dict[str, str]` mapping GUI keys to string values

#### Scenario: GUI values to config
- **WHEN** `adapter.gui_to_config(values)` is called
- **THEN** returns a `SimulationConfig` with `Quantity`-typed fields parsed from GUI strings
