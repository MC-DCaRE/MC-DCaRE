## proposal Round 1 — 2026-06-10

### 🟢 Good
- Physics-grounded motivation with clear decomposition of calibration factor
- Scope well-bounded (no GUI, no CLI, no automated sweeps)
- All 5 deliverables listed (calibration.yaml, CalibrationService, provenance, stale file, dk comment)
- Risks identified including backward compat and 4πr² overestimation
- Rejected alternatives section covers per-protocol, global, per-phantom approaches

### 🟡 Suggestions (non-blocking)
- Add the factor decomposition formula `D_absolute = D_raw × norm_factor × mAs × DCF(kV, fan_mode)` explicitly to proposal
- Add calibration.yaml schema (the YAML example from the explore brief)
- Add the 6-row (kV, fan_mode) pair table
- List runfolder provenance fields
- State calibration.yaml location (project root alongside existing config YAMLs)
- Include the 4-step cross-module data flow from explore brief

### 🔴 Must Fix
- (None)

## design Round 1 — 2026-06-10

### 🟢 Good
- Factor decomposition matches proposal and explore brief
- All 6 unique (kV, fan_mode) pairs covered
- simulation_metadata.yaml schema includes every field from proposal
- Backward compatibility strategy addresses proposal risk #1
- Out-of-scope boundaries respected
- Cleanup items have correct file references
- Design decisions documented with reasoning

### 🟡 Suggestions (non-blocking)
- "Pydantic model" misnomer — project uses frozen dataclasses, not Pydantic
- compute_dcf() write-back semantics unclear (update-in-place vs append)
- Missing calibration.yaml in File Changes Summary table

### 🔴 Must Fix
- Missing simulation_metadata.yaml copy in base.py — file would never reach runfolder
- CTDICalculator × CalibrationService.apply() factor interaction needs clarification to prevent mAs double-counting

## design Round 1 fixes — 2026-06-10

### 🔴 Fixed
- Added simulation_metadata.yaml copy to base.py file changes entry
- Added clarifying docstring to apply() explaining CTDICalculator returns dose at sim_mAs with dcf_used=1.0
### 🟡 Addressed
- Changed "Pydantic model" to "frozen dataclasses" throughout
- Changed "append-only" to "filled in-place" with explicit (kV, fan_mode) matching
- Added calibration.yaml row to File Changes Summary
- Fixed decision #5 wording

## specs+tasks Round 1 — 2026-06-10

### 🟢 Good
- All 5 proposal in-scope items have matching spec coverage
- No out-of-scope items leaked into specs
- 6 (kV, fan_mode) pairs consistent across all artifacts
- Backward compatibility strategy thorough
- Error conditions well-specified
- Task dependency ordering correct
- Every task lists test file explicitly
- Cleanup items have precise file:line references

### 🟡 Suggestions (non-blocking)
- Task 3 leaves gitignore decision to implementer
- CAL-META-001 norm_factor decomposition algorithm unspecified in spec
- CalibrationService.apply() doesn't work with old runfolders — note this limitation
- Specs lack scenario blocks for test mapping

### 🔴 Must Fix
- CAL-META-004 and Task 4 don't provision seed and threads for SpectrumGenerator metadata
- All 4 spec files use "## Requirements" instead of "## ADDED Requirements"

## specs+tasks Round 1 fixes — 2026-06-10

### 🔴 Fixed
- Updated CAL-META-004 to include seed, threads, fan_mode in SpectrumGenerator parameter changes
- Updated Task 4 to include seed and threads in SpectrumGenerator.generate() signature change
- Changed all 4 spec files from "## Requirements" to "## ADDED Requirements"
### 🟡 Addressed
- Task 3: resolved gitignore decision — `calibration.yaml` gitignored, `calibration.example.yaml` tracked with populated entry
- CAL-META-001: added norm_factor computation algorithm (derive from combined_factor / mAs)
- CAL-SVC-003: added note that apply() requires new-format runfolders; backward compat is CTDICalculator only
- CAL-DATA-004: added `force` parameter for re-calibration, plus 3 scenarios
- CAL-SVC-003: listed exact return dict keys and added 3 scenarios
- CAL-SVC-001: added scenario for DCF computation
