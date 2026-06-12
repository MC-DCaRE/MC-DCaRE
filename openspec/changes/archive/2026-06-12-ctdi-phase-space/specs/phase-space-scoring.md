## phase-space-scoring

### Requirement
CTDI mode must support generating phase space files that record particles surviving the beam line (source → collimators → bowtie → BHF), for use in replay runs and beam characterization.

### Specification
- Config parameter `ctdi.phase_space_mode` with value `"score"` activates scoring mode.
- `CtdiMode` renders `ctdi_phsp_score.j2` template instead of the standard headsourcecode + phantom combination.
- The scoring template includes all source-side geometry, a thin vacuum scoring surface after the BHF, and a PhaseSpace scorer with `KillAfterPhaseSpace = "True"`.
- No phantom geometry or dose scorers are included.
- `IncludeTOPASTime` is deliberately omitted from the PhaseSpace scorer because the beam is time-independent — all scored particles share the same beam state. Including it would add unnecessary data to the output file.
- `SpectrumGenerator` runs normally (source still needs the spectrum).
- After TOPAS execution, `PhaseSpaceAnalyzer` processes the `.phsp` file and writes beam statistics to the runfolder.
- `IfOutputFileAlreadyExists = "Overwrite"` ensures re-runs replace the previous phase space file rather than failing or appending.
- `simulation_metadata.yaml` is written to the runfolder with the scoring run's parameters (histories, norm_factor, mAs, kvp, fan_mode, blade positions).
- The `.phsp` file and `simulation_metadata.yaml` are co-located in `<runfolder>/phase_space/`.
- The PhaseSpace scorer outputs `beam_exit_phsp.phsp` (Binary format).

### Acceptance Criteria
- Given `phase_space_mode = "score"` and 1e6 histories, a `.phsp` file is produced in the runfolder.
- The `.phsp` file is valid Binary format readable by TOPAS PhaseSpace source.
- `PhaseSpaceAnalyzer` extracts particle count, survival fraction, energy spectrum, and spatial/angular distributions from the file.
- `simulation_metadata.yaml` in the runfolder contains all original run parameters.
- No phantom geometry is present in the rendered TOPAS parameter file.
