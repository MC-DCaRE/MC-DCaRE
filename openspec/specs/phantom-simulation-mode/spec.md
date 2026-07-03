# phantom-simulation-mode Specification

## Purpose

Defines ICRP145 as a third simulation type alongside DICOM and CTDI: the
`SimulationType.ICRP145` enum member, the `PhantomConfig` dataclass,
orchestrator dispatch to `PhantomMode`, and the end-to-end run path
(configure, render, prepare, execute a single TOPAS process) for an ICRP 145
reference phantom, plus the GUI tab and adapter plumbing.

## Requirements

### Requirement: ICRP145 simulation type is a recognized selection

The `SimulationType` enum SHALL include an `ICRP145` member. `SimulationConfig.validate()` SHALL accept `simulation_type == "ICRP145"` without error.

#### Scenario: Config validates with ICRP145 type
- **WHEN** a `SimulationConfig` is built with `imaging.simulation_type = "ICRP145"` and validated
- **THEN** validation passes (no exception raised)

#### Scenario: Enum member present
- **WHEN** the `SimulationType` enum is inspected
- **THEN** it contains a member whose value is `"ICRP145"`

### Requirement: Orchestrator dispatches the phantom mode

The `Orchestrator._get_mode` factory SHALL return a `PhantomMode` instance when `config.imaging.simulation_type == "ICRP145"`. Dispatch for `"DICOM"` and `"CTDI"` SHALL remain unchanged, and any unrecognized type SHALL still fall back to `CtdiMode` (preserving existing behavior).

#### Scenario: ICRP145 selects PhantomMode
- **WHEN** `_get_mode` is called with a config whose `simulation_type` is `"ICRP145"`
- **THEN** it returns an instance of `PhantomMode`

#### Scenario: DICOM and CTDI dispatch unchanged
- **WHEN** `_get_mode` is called with `simulation_type` of `"DICOM"` then `"CTDI"`
- **THEN** it returns `DicomMode` and `CtdiMode` respectively, as before

#### Scenario: Unknown type still falls back to CTDI
- **WHEN** `_get_mode` is called with an unrecognized `simulation_type`
- **THEN** it returns `CtdiMode` (fallback preserved)

### Requirement: PhantomConfig holds phantom run parameters

A frozen `PhantomConfig` dataclass SHALL be added to `config.py` and exposed as the `phantom` field of `SimulationConfig`. It SHALL include, at minimum: a phantom data directory path, a phantom sex selection (`"AM"` or `"AF"`), supine placement offsets (translation and rotation), a graphics toggle, and organ-scoring controls. Fields expressing physical quantities SHALL be coerced to `Quantity` in `__post_init__`, following the `DicomConfig` pattern.

#### Scenario: Defaults are valid
- **WHEN** a `PhantomConfig` is constructed with no arguments
- **THEN** it provides usable defaults (a data directory, a default sex, zero offsets)

#### Scenario: Quantity coercion
- **WHEN** a `PhantomConfig` is constructed from YAML with string-valued dimensional fields
- **THEN** those fields are parsed into `Quantity` instances during `__post_init__`

### Requirement: PhantomConfig round-trips through YAML

`SimulationConfig.to_yaml` and `SimulationConfig.from_yaml` SHALL serialize and deserialize the `phantom` section alongside `general`, `imaging`, `dicom`, and `ctdi`.

#### Scenario: YAML round-trip preserves phantom settings
- **WHEN** a `SimulationConfig` with a non-default `PhantomConfig` is written to YAML and read back
- **THEN** the reconstructed config's `phantom` field equals the original

### Requirement: PhantomMode implements the SimulationMode contract

`PhantomMode` SHALL implement every abstract method of `SimulationMode`: `main_template_name` returns `"headsourcecode_boilerplate.j2"`, `main_output_name` returns `"headsourcecode.txt"`, `build_main_context` returns a dict containing `"simulation_type": "ICRP145"` and the shared geometry/rotation variables consumed by the main template, `build_sub_context` returns the phantom parameters, `get_sub_file_name`/`get_sub_template_name` select the phantom include, `compute_histories` returns `sequential_times * histories`, `prepare_run` stages all required files, and `execute` runs a single TOPAS process.

#### Scenario: Main context flags ICRP145
- **WHEN** `build_main_context` is called
- **THEN** the returned dict maps `"simulation_type"` to `"ICRP145"`

#### Scenario: History count matches DICOM formula
- **WHEN** `compute_histories` is called with `sequential_times = 1000` and `histories = 100000`
- **THEN** it returns `"100000000"`

#### Scenario: Execution runs a single TOPAS process
- **WHEN** `execute` is called
- **THEN** it invokes `SimulationRunner` to run `headsourcecode.txt` exactly once in the run directory

### Requirement: prepare_run stages phantom and shared files

`PhantomMode.prepare_run` SHALL copy the rendered main file, the phantom sub-include, and the shared files via `SimulationMode.copy_common_files`. It SHALL NOT require DICOM-specific artifacts (e.g. `HUtoMaterialSchneider.txt`) that are irrelevant to the mesh phantom.

#### Scenario: Required files copied into run directory
- **WHEN** `prepare_run` runs
- **THEN** the run directory contains `headsourcecode.txt`, the rendered phantom include, and the common spectrum/bowtie/calibration files

### Requirement: GUI exposes the phantom mode

The simulation-type dropdown SHALL include `"ICRP145"`. Selecting it SHALL show a phantom input tab and hide the DICOM and CTDI tabs. The adapter SHALL map phantom GUI fields to/from `PhantomConfig`, and the run path SHALL build a `SimulationConfig` with `simulation_type = "ICRP145"`.

#### Scenario: Selecting ICRP145 shows the phantom tab
- **WHEN** the user selects `"ICRP145"` in the dropdown
- **THEN** the phantom tab becomes visible and the DICOM and CTDI tabs are hidden

#### Scenario: GUI values populate PhantomConfig
- **WHEN** the user runs a simulation from the phantom tab
- **THEN** the resulting `SimulationConfig.phantom` reflects the entered values and `simulation_type` is `"ICRP145"`

