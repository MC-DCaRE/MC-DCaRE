# Spec: Cleanup

## Capability

Remove dead file copy and fix misleading comment.

## ADDED Requirements

### CAL-CLEAN-001: Remove NbParticlesInTime.txt copy
- Delete the `shutil.copy(NbParticlesInTime.txt)` line from `src/modes/base.py` `copy_common_files()`
- The file is a TOPAS output log (written when `Tf/Verbosity >= 1`), never an input
- Not referenced by any TOPAS parameter file in the templates

### CAL-CLEAN-002: Fix dk comment
- In `src/spectrum_generator.py`, replace lines 41-43 comment block
- Current: claims `dk=0.2 mm Al inherent filtration`
- Correct: `dk=0.2 keV` is energy bin width (spectral resolution)
- No SpekPy filtration is applied; filtration is in TOPAS geometry (0.7 mm Ti + bowtie)

### CAL-CLEAN-003: Update tests
- Remove assertions for `NbParticlesInTime.txt` in `tests/unit/test_base_mode.py`
- Remove from expected file lists in `tests/integration/test_dry_run_pipeline.py`
