## Tasks

- [x] ### 1. Add phase space config parameters
**Spec**: phase-space-config
**Files**: `src/config.py`, `tests/unit/test_config.py`
- Added `phase_space_mode: str = "off"` to CTDI config dataclass
- Added `phase_space_file: str = ""` to CTDI config dataclass
- Added `phase_space_multiple_use: int = 1` to CTDI config dataclass
- Added validation: replay mode requires non-empty `phase_space_file` pointing to existing file
- Added validation: `phase_space_multiple_use >= 1`
- Updated YAML config schema documentation
- Wrote unit tests for validation rules

- [x] ### 2. Create scoring template
**Spec**: phase-space-scoring
**Files**: `src/boilerplates/ctdi_phsp_score.j2`
- Copied `headsourcecode_boilerplate.j2` as base
- Removed phantom include logic (`{% if simulation_type == 'CTDI' %}`)
- Removed `sv:Ph/Default/LayeredMassGeometryWorlds` (no parallel worlds)
- Added thin vacuum scoring surface geometry after BHF (parented to Rotation)
- Added PhaseSpace scorer on scoring surface (Binary, KillAfterPhaseSpace, no IncludeTOPASTime)
- Kept all source-side geometry, physics, time feature, graphics
- TransY position set to -86.0 cm (requires verification with graphics run — task 9)

- [x] ### 3. Create replay template
**Spec**: phase-space-replay
**Files**: `src/boilerplates/ctdi_phsp_replay.j2`
- World geometry, physics, seed, threads (same as headsourcecode)
- Rotation group with time feature (same Tf/ parameters)
- PhaseSpace source inside Rotation (Type, PhaseSpaceFileName, Component, PhaseSpaceMultipleUse)
- Phantom include (CTDIphantom_*.j2, conditional on phantom size)
- All dose scorers via phantom include (same as current)
- No BeamPosition, collimators, bowtie, BHF, spectrum include, NbParticlesInTime

- [x] ### 4. Implement mode branching in CtdiMode
**Spec**: phase-space-scoring, phase-space-replay
**Files**: `src/modes/ctdi_mode.py`, `tests/unit/test_ctdi_mode.py`
- Added `phase_space_mode` property that reads from config
- Branched `build_main_context()` on mode: score mode returns scoring context, replay mode returns replay context
- Branched template selection: score → `ctdi_phsp_score.j2`, replay → `ctdi_phsp_replay.j2`
- Branched `build_sub_context()`: score mode returns empty (no phantom), replay mode returns phantom context
- Branched `compute_histories()`: replay mode histories from metadata or config
- Branched `execute()`: score mode runs scoring template, replay runs replay + phantom combined file
- Wrote unit tests for each mode branch

- [x] ### 5. Update orchestrator for phase space pipeline
**Spec**: phase-space-scoring, phase-space-replay
**Files**: `src/orchestrator.py`, `tests/unit/test_orchestrator.py`
- In `run_with_runfolder()`, branched on `config.ctdi.phase_space_mode`
- Score mode: run SpectrumGenerator → render scoring template → execute → run PhaseSpaceAnalyzer → copy metadata
- Replay mode: skip SpectrumGenerator → override `prepare_run` to skip `copy_common_files()` (no spectrum/calibration files exist) → copy phase_space_file + scoring run metadata (with norm_factor adjusted by dividing by PhaseSpaceMultipleUse) + Muen.dat to runfolder → render replay template → execute → run existing post-processing
- Off mode: current pipeline unchanged
- Created `<runfolder>/phase_space/` subdirectory for score mode output
- Wrote tests for orchestrator branching

- [x] ### 6. Implement PhaseSpaceAnalyzer
**Spec**: phase-space-statistics
**Files**: `src/services/phase_space_analyzer.py`, `tests/unit/test_phase_space_analyzer.py`
- Implemented Binary format `.phsp` file reader using numpy
- Parse particle records: position (x, y, z), direction (dx, dy), energy, weight
- Compute statistics: particle_count, survival_fraction, energy spectrum histogram, spatial/angular distributions, mean/std energy, particle type counts
- Accept metadata_path for survival_fraction calculation
- Wrote unit tests with a synthetic `.phsp` test fixture

- [x] ### 7. Update calibration chain for replay mode
**Spec**: phase-space-replay
**Files**: `src/services/ctdi_calculator.py`, `src/services/calibration.py`, `tests/unit/test_calibration_service.py`
- `CTDICalculator` reads `simulation_metadata.yaml` and computes `calibration_factor = norm_factor × mAs × dcf_used`
- For replay, the `simulation_metadata.yaml` has `norm_factor` set to `original_norm_factor / PhaseSpaceMultipleUse`
- This compensates for the M× higher raw dose from particle reuse
- `CalibrationService.apply()` applies the same DCF and mAs_ratio as direct mode — no changes needed there
- The orchestrator adjusts `norm_factor` when copying metadata for replay (task 5)
- Wrote tests verifying: (a) replay calibration_factor = direct calibration_factor / M, (b) CTDI_w values match given the same raw dose

- [x] ### 8. Integration test: scoring + replay pipeline
**Spec**: phase-space-scoring, phase-space-replay
**Files**: `tests/integration/test_phase_space_pipeline.py`
- Dry-run scoring mode: verified template renders correctly with PhaseSpace scorer, no phantom
- Dry-run replay mode: verified template renders with PhaseSpace source + phantom, no beam geometry
- Verified config validation: replay without file raises error
- Verified replay `simulation_metadata.yaml` has norm_factor = original_norm_factor / M

- [ ] ### 9. Verify scoring surface position
**Spec**: phase-space-scoring
**Files**: `src/boilerplates/ctdi_phsp_score.j2`
- Run scoring template with graphics enabled on a short test (1e4 histories)
- Visually verify scoring surface position relative to BHF
- Confirm PhaseSpace scorer captures particles (non-zero output file)
- Adjust TransY if needed to clear all source-side geometry
- Document the verified position in the template comments
- **SKIPPED: Requires live TOPAS installation**

- [ ] ### 10. Verify replay source positioning
**Spec**: phase-space-replay
**Files**: `src/boilerplates/ctdi_phsp_replay.j2`
- Run replay template with graphics enabled on a short test using the .phsp file from task 9
- Verify that particles enter the phantom from the correct direction (same as direct-beam run)
- Verify that the Rotation group time feature correctly sweeps the PhaseSpace source around the phantom
- If `Component = "Rotation"` produces incorrect particle positions (double-transformation), add a positioning component inside Rotation and re-test
- Document the verified configuration in the template comments
- **SKIPPED: Requires live TOPAS installation**
