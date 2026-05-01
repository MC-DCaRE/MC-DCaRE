# modes

## Purpose
Strategy pattern for simulation modes. Each mode knows how to apply configuration parameters to TOPAS boilerplate files and select the correct include files for a given simulation type.

## Architecture
`base.py` defines the `SimulationMode` abstract base class with two contracts:
- `apply_parameters(lines, config)` -- edits TOPAS parameter lines in place, returns modified lines
- `get_include_files(config)` -- returns list of (filename, content) pairs for include files to copy into the run directory

Two concrete implementations:
- `ctdi_mode.py` -- CTDI phantom validation. Applies spectrum, blade openings, histories, phantom size, rotation parameters. Uses `fieldtobladeopening` to convert field size to blade positions. Selects CTDI phantom include (16cm or 32cm) plus bowtie (fullfan/halffan).
- `dicom_mode.py` -- DICOM patient dose. Copies patient DICOM directory into run folder, applies spectrum and rotation parameters. Selects patientDICOM include plus bowtie.

## Key Files

| File | Role |
|---|---|
| `base.py` | `SimulationMode` ABC with `apply_parameters()` and `get_include_files()` abstract methods; includes shared helper for file copying |
| `ctdi_mode.py` | CTDI validation mode: edits blade positions, phantom size, spectrum, rotation, scoring placeholders |
| `dicom_mode.py` | DICOM patient mode: copies DICOM files, edits spectrum, rotation, and patient geometry parameters |

## Conventions
- `SimulationConfig` passed to both abstract methods, not stored on the mode instance
- `apply_parameters()` returns `List[str]` of edited boilerplate lines
- `get_include_files()` returns `List[Tuple[str, str]]` of (filename, content) pairs
- Include file selection driven by `FanMode` enum from `models/enums.py`
- `ParameterEditor` from `src.parameter_editor` used for string-level TOPAS parameter substitution
- `fieldtobladeopening` imported from `src.fieldtobladeopening` for CTDI blade position calculation
