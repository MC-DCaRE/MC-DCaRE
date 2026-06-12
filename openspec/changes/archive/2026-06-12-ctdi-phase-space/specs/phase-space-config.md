## phase-space-config

### Requirement
`SimulationConfig` must support phase space mode selection and file path configuration for CTDI simulations.

### Specification
- Add `phase_space_mode: str` to the CTDI config section with values `"off"` (default), `"score"`, `"replay"`.
- Add `phase_space_file: str` to the CTDI config section (path to `.phsp` file, used only in replay mode).
- Add `phase_space_multiple_use: int` to the CTDI config section (default 1, used only in replay mode).
- Validation: `phase_space_mode = "replay"` requires `phase_space_file` to be a non-empty string pointing to an existing file.
- Validation: `phase_space_mode = "score"` requires standard imaging parameters (kV, fan mode, blades) to be set.
- Validation: `phase_space_multiple_use` must be >= 1.
- The config YAML schema uses `ctdi.phase_space_mode`, `ctdi.phase_space_file`, `ctdi.phase_space_multiple_use`.

### Acceptance Criteria
- Default config (`phase_space_mode = "off"`) produces identical behavior to the current pipeline.
- Setting `phase_space_mode = "replay"` without a `phase_space_file` raises a validation error.
- Setting `phase_space_multiple_use = 0` raises a validation error.
- Config round-trips correctly through YAML load/save.
