## Why

CTDI Monte Carlo simulations spend most of their compute time tracking particles through the upstream beam line: the X-ray source, collimators (lead jaws), bowtie filter, and beam hardening filter. Many particles are absorbed by the lead collimators and never reach the phantom — their tracking is wasted computation that gets repeated every run, even when the imaging parameters haven't changed.

A phase space approach records particles that survive the beam line into a file, then replays that file in subsequent runs. This eliminates all upstream tracking. The phase space file also provides beam characterization data (post-filtration energy spectrum, transmission efficiency, spatial and angular distributions) that isn't currently available.

## What Changes

- Add a **scoring run** mode to CTDI simulation: full beam line geometry + PhaseSpace scorer after the bowtie/BHF, no phantom, no dose scorers. Outputs a Binary format `.phsp` file.
- Add a **replay run** mode to CTDI simulation: PhaseSpace source inside the Rotation group (with time feature), phantom + dose scorers. No SpekPy, no collimators, no bowtie, no BHF.
- Add config parameters to select between direct beam (current), scoring, and replay modes.
- Add a scoring surface geometry component (or use BHF exit face) positioned after all source-side geometry, inside the Rotation group.
- Update the calibration chain to handle PhaseSpace source normalization (particle count × PhaseSpaceMultipleUse replaces histories).
- Add post-processing of `.phsp` files for beam characterization statistics: energy spectrum, survival fraction, spatial distribution, angular distribution.

## Non-goals

- DICOM mode phase space support (same approach applies, but out of scope).
- Adding exit window or primary collimator geometry (will invalidate phase space files when added later).
- Changing the TOPAS physics list, scorer types, or existing dose scoring formalism.
- Optimizing file format beyond Binary (Limited/ROOT can be considered later).
- Automated "generate phsp if missing" logic in the orchestrator.

## Capabilities

### New Capabilities

- `ctdi-phase-space-scoring`: Generate phase space files from CTDI beam line. New Jinja2 template variant of `headsourcecode_boilerplate.j2` with PhaseSpace scorer instead of phantom include. Config-gated via `ctdi.phase_space_mode = "score"`.
- `ctdi-phase-space-replay`: Run CTDI phantom simulations from pre-generated phase space files. New Jinja2 template with PhaseSpace source inside Rotation group, phantom include, dose scorers. Config-gated via `ctdi.phase_space_mode = "replay"`.
- `phase-space-statistics`: Post-process `.phsp` files to extract beam characterization data: energy spectrum histogram, survival fraction (particles at scoring surface / histories), spatial distribution (x, y histograms), angular distribution (dx, dy histograms).

### Modified Capabilities

- `ctdi-simulation-config`: `SimulationConfig` gains `phase_space_mode` field (values: `"off"`, `"score"`, `"replay"`) and `phase_space_file` path field.
- `ctdi-mode-execution`: `CtdiMode` branches on `phase_space_mode` to select template, context, and execution path.
- `calibration-chain`: Orchestrator pre-adjusts `norm_factor` in replay metadata (`original_norm_factor / PhaseSpaceMultipleUse`) so `CalibrationService.apply()` needs no changes.

## Impact

### Core changes

- `src/config.py` — add `phase_space_mode` and `phase_space_file` to CTDI config section
- `src/modes/ctdi_mode.py` — branch execution on phase_space_mode, new template selection, new context building
- `src/boilerplates/` — two new Jinja2 templates: scoring template and replay template
- `src/services/` — new `PhaseSpaceAnalyzer` for .phsp file statistics
- `src/services/calibration.py` — no changes; normalization handled by orchestrator writing adjusted metadata

### Downstream consumers

- `src/orchestrator.py` — may need to skip `SpectrumGenerator` for replay mode
- `src/gui/` — config UI for phase space mode selection and file path

### Tests requiring rework

- `tests/unit/test_ctdi_mode.py` — test new mode branching and template selection
- `tests/unit/test_orchestrator.py` — test phase space pipeline orchestration
- New: `tests/unit/test_phase_space_analyzer.py` — test .phsp file parsing and statistics

### Documentation

- Phase space workflow documentation (scoring → replay pipeline)
- TOPAS PhaseSpace parameter reference for the project
