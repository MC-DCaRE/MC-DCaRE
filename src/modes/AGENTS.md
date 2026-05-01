# modes

## Purpose
Strategy pattern for simulation modes. Each mode builds a Jinja2 template context dict for the main TOPAS file and sub-include file, selects the correct templates, and handles run preparation and execution.

## Architecture
`base.py` defines the `SimulationMode` abstract base class with these contracts:
- `main_template_name` / `main_output_name` -- properties identifying the `.j2` template and output filename
- `build_main_context(config)` -- builds `Dict[str, object]` of Jinja2 variables for the main TOPAS file
- `build_sub_context(config, plug_position)` -- builds context for the sub-include file (phantom or patient)
- `get_sub_template_name(config)` / `get_sub_file_name(config)` -- selects the `.j2` template and output filename
- `compute_histories(config)` -- returns the number of histories string
- `prepare_run(config, rundir, project_root)` -- copies required files into the run directory
- `execute(config, rundir, project_root)` -- runs the simulation

Two concrete implementations:
- `ctdi_mode.py` -- CTDI phantom validation. Builds contexts with blade openings, phantom size, rotation parameters. Generates 5 plug files (Centre/Top/Bottom/Left/Right) by rendering the phantom template per plug position and concatenating with the main file.
- `dicom_mode.py` -- DICOM patient dose. Builds contexts with patient geometry, isocenter shifts, and output filename. Single execution run with headsource + patientDICOM combined.

## Key Files

| File | Role |
|---|---|
| `base.py` | `SimulationMode` ABC with context-building, template selection, and file-copying abstract methods |
| `ctdi_mode.py` | CTDI mode: blade positions, phantom size, plug-file generation, 5 sequential TOPAS runs |
| `dicom_mode.py` | DICOM mode: patient geometry context, DICOM file staging, single TOPAS run |

## Conventions
- `SimulationConfig` passed to all methods, not stored on the mode instance
- Context dicts use `Dict[str, object]` typed as Jinja2 template variables
- `build_sub_context` accepts `plug_position: str = ""` (DicomMode ignores it)
- Include file selection driven by `FanMode` value from config
- `fieldtobladeopening` imported from `src.fieldtobladeopening` for user-blade field-to-opening conversion
- `SimulationRunner` invoked in `execute()` with mode-specific run methods (`run_ctdi` vs `run_dicom`)
- `copy_common_files()` static method on base class handles shared files (Muen.dat, NbParticlesInTime, spectrum, bowtie)
