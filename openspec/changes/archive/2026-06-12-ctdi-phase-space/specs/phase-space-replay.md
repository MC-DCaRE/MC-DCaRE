## phase-space-replay

### Requirement
CTDI mode must support replaying pre-generated phase space files, replacing the full beam line with a PhaseSpace source inside the Rotation group, for faster phantom dose scoring.

### Specification
- Config parameter `ctdi.phase_space_mode` with value `"replay"` activates replay mode.
- Config parameter `ctdi.phase_space_file` specifies the path to the `.phsp` file.
- Config parameter `ctdi.phase_space_multiple_use` (default 1) sets `PhaseSpaceMultipleUse` in the replay template.
- `CtdiMode` renders `ctdi_phsp_replay.j2` + `CTDIphantom_*.j2` instead of the standard templates.
- The replay template contains: world geometry, physics, Rotation group (with time feature), PhaseSpace source inside Rotation, phantom include, dose scorers.
- The replay template does NOT contain: BeamPosition, collimators, bowtie, BHF, spectrum include, NbParticlesInTime.txt.
- `SpectrumGenerator` is skipped for replay runs.
- `CalibrationService` uses the scoring run's `simulation_metadata.yaml` (co-located with `.phsp` file) with `norm_factor` adjusted to `original_norm_factor / PhaseSpaceMultipleUse`. This compensates for the M× higher raw dose from particle reuse. `CalibrationService.apply()` applies the same DCF and mAs_ratio as direct mode.
- PhaseSpace source `Component` is set to `"Rotation"` so particles are positioned in the beam's local frame and rotated by the time feature.
- `PhaseSpaceIncludeEmptyHistories` is NOT set (defaults to False). Empty histories represent original particles that were absorbed before reaching the scoring surface — including them would inject zero-weight particles that waste tracking time without contributing to dose.
- All existing dose scorers (TLE, DTM, DTW) and optional water chamber scorers work identically to the direct-beam pipeline.
- `CtdiCalculator` and `BenchmarkCalculator` process replay output files the same way as direct-beam output.

### Acceptance Criteria
- Given `phase_space_mode = "replay"` and a valid `.phsp` file, the simulation runs without the full beam line geometry.
- The replay produces identical scorer output format as the direct-beam pipeline.
- `CalibrationService.apply()` produces correctly normalized results using the scoring run's metadata.
- Rotation group + time feature are present and functioning (beam rotates around stationary phantom).
- No SpekPy spectrum file is generated for replay runs.
