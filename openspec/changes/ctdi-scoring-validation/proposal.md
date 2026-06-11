## Why

CTDI simulations using OpenTOPAS parallel worlds produce divergent results between direct scoring methods (DoseToMaterial, DoseToWater) and the Track Length Estimator (TLE). TLE shows centre > peripheral dose while direct scorers show peripheral > centre. This discrepancy must be understood and resolved so that the simulation produces a defensible, measurement-equivalent CTDI value for comparison against physical measurements.

## What Changes

- Add a `ctdi-scoring-methods.md` reference document (already drafted at `docs/`) explaining the physics and scoring formalism.
- Refactor `CTDICalculator._process_file_type` to apply scorer-specific CTDI formalisms:
  - **TLE**: Collision kerma in air — the measurement-equivalent quantity. Uses the standard CTDI_w formula directly. No f-factor or conversion needed; TLE in air already approximates what a pencil chamber measures.
  - **DoseToMaterial (air)**: Analogue absorbed dose to air. Same CTDI_w formula as TLE but converges slowly. Used only as a validation cross-check.
  - **DoseToWater**: Analogue absorbed dose to water. A different physical quantity — cannot use the same calibration factor without spectrum-weighted (μ_en/ρ)_water/(μ_en/ρ)_air conversion. Reported as a secondary "water-referenced CTDI-like" metric, not calibrated against air-kerma measurements.
- Designate TLE as the primary scorer by convention: `calculate()` returns results for all scorer types, but `CalibrationService.apply()` only applies the DCF to TLE results by default. Downstream consumers select scorer type via a `scorer_type` parameter.
- Add a validation workflow: run TLE and analogue scorers side-by-side, compare results, report systematic differences (kerma approximation bias, convergence statistics).
- Add optional water-filled chamber scoring volumes to CTDI phantom templates as additional parallel worlds (config-gated via `ctdi.water_chamber_enabled`), alongside existing air chambers — not replacing them.
- Report scorer-specific results separately with clear labels.

## Non-goals

- Adding new TOPAS scorer types beyond the existing three (TLE, DTM, DTW).
- Changing the TOPAS physics list, cross-section data, or geometry engine.
- Modifying the DCF computation formula in `CalibrationService.compute_dcf()`.
- Producing pass/fail verdicts in the validation workflow — comparison reports only.
- Changing how `SpectrumGenerator` normalises the spectrum.

## Capabilities

### New Capabilities
- `ctdi-scorer-selection`: Scorer-aware CTDI post-processing. `CTDICalculator` labels results by scorer type. `CalibrationService.apply()` applies DCF to TLE by default, with optional scorer selection. `_process_file_type` is the primary refactoring target (lines 201–254 of ctdi_calculator.py).
- `ctdi-validation-workflow`: Side-by-side comparison of TLE vs analogue scorers, reporting systematic differences and convergence statistics.

### Modified Capabilities
- `ctdi-phantom-templates`: CTDIphantom_16.j2 and CTDIphantom_32.j2 gain optional water-filled chamber scoring volumes (additional parallel worlds, gated by config).

## Impact

### Core changes
- `src/services/ctdi_calculator.py` — scorer-type awareness in `_process_file_type`, labelled output dicts, TLE as primary
- `src/modes/ctdi_mode.py` — may need to pass scorer configuration context
- `src/boilerplates/TOPAS_includeFiles/CTDIphantom_16.j2` — optional water chamber volumes
- `src/boilerplates/TOPAS_includeFiles/CTDIphantom_32.j2` — same

### Downstream consumers
- `src/services/calibration.py` — `CalibrationService.apply()` must apply DCF to TLE results only by default, not indiscriminately to all scorer types. DoseToWater results require air-to-water conversion before calibration comparison.
- `src/services/benchmark.py` — `BenchmarkCalculator` compares against reference values; must respect scorer type semantics (TLE kerma vs DTW dose are different quantities).

### Tests requiring rework
- `tests/unit/test_calculate_ctdiw.py` — tests `_process_file_type`, `_find_chamber_files`, `calculate_ctdi_w` for all three file types
- `tests/unit/test_calibration_service.py` — tests calibration apply pipeline with all file types
- `tests/integration/test_calibration_workflow.py` — end-to-end calibration with all file types

### Documentation
- `docs/ctdi-scoring-methods.md` — reference document (already created)
