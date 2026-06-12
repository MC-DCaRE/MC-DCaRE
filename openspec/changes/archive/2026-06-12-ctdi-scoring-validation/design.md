## Context

MC-DCaRE runs CTDI simulations in OpenTOPAS using parallel worlds (Layered Mass Geometry) to score all 5 chamber plug positions simultaneously. Three scorer types run in every simulation: TLE, DoseToMaterial (air), and DoseToWater. The current `CTDICalculator` processes all three identically — same formula, same calibration factor, same result structure. This is physically incorrect because TLE estimates collision kerma (a fluence-weighted quantity) while DTM/DTW score absorbed dose (event-based), and they have different relationships to the measured CTDI.

Current architecture:
- `CTDICalculator._process_file_type()` reads CSV, extracts dose, applies calibration factor uniformly
- `CalibrationService.apply()` wraps `CTDICalculator.calculate()` and applies DCF to all results indiscriminately
- Templates already produce separate CSV files per scorer type (`_tle`, `_dtm`, `_dtw`)

## Goals / Non-goals

### Goals
- Distinguish TLE (primary, measurement-equivalent) from analogue scorers in post-processing
- Apply calibration only to TLE results by default; report DTM/DTW as secondary comparisons
- Add optional water-filled chamber volumes to phantom templates for sensitivity studies
- Provide validation comparison between TLE and analogue scorers

### Non-goals
- New TOPAS scorer types, physics lists, or cross-section data
- Changing DCF computation formula
- Pass/fail validation verdicts
- Spectrum-weighted air-to-water conversion factors (future work)
- Modifying spectrum normalisation

## Decisions

### D1: TLE as primary by convention, not config flag

**Choice**: TLE is the primary scorer by hard convention in `CalibrationService.apply()`. The `calculate()` method returns all scorer types; downstream selects TLE by default.

**Alternatives considered**:
- (a) Config flag `primary_scorer: "tle"` — adds config surface, validation burden, and users could misconfigure. Overkill when TLE is the only physically correct choice for measurement equivalence.
- (b) Return only TLE from `calculate()` — loses the validation cross-comparison capability.
- (c) Separate methods `calculate_tle()`, `calculate_analogue()` — fragments the API unnecessarily.

**Rationale**: Convention-over-configuration. TLE is the only scorer that approximates what a pencil chamber measures (collision kerma in air). Making it the default with an optional override for validation purposes is the simplest correct design.

### D2: Result dict gains `scorer_type` field and `is_primary` flag

**Choice**: Each result dict from `calculate()` includes `"scorer_type": "tle"|"dtm"|"dtw"` and `"is_primary": bool`.

**Rationale**: Downstream consumers (`CalibrationService`, `BenchmarkCalculator`) need to know which results are measurement-equivalent without hardcoding scorer name checks. `is_primary` is derived from `scorer_type == "tle"`.

### D3: Calibration applies to TLE only; DTM/DTW pass through uncalibrated

**Choice**: `CalibrationService.apply()` filters results by `is_primary`, applies DCF and mAs scaling only to those, and passes DTM/DTW through with `dcf_applied: null` and a `"note": "uncalibrated — secondary comparison"` field.

**Rationale**: Applying a DCF derived from TLE air kerma to DoseToWater results is physically wrong (different quantity). DTM can theoretically use the same DCF (same medium, air) but with different statistical properties — still reported separately for clarity.

### D4: Water chamber volumes as additional parallel worlds

**Choice**: When `ctdi.water_chamber_enabled: true`, the phantom template adds 5 additional parallel world volumes with `Material="Water"` and 5 additional DTM scorers, named `ChamberPlugCentre_water`, etc. Air chambers remain unchanged.

**Alternatives considered**:
- (a) Replace air with water — loses the primary TLE scorer. Rejected.
- (b) Separate template file — duplicates 150 lines for a material swap. Rejected.
- (c) Config flag that swaps material globally — prevents simultaneous air+water comparison. Rejected.

**Rationale**: Additional parallel worlds allow simultaneous air+water scoring with no extra simulation time (same particle transport). The only cost is extra output files and slightly longer finalisation.

### D5: Validation workflow as a post-hoc comparison function

**Choice**: Add `CTDICalculator.compare_scorers()` method that takes the output of `calculate()` and returns a comparison report: TLE vs DTM ratio, TLE vs DTW ratio, per-position breakdowns.

**Alternatives considered**:
- (a) Separate `ValidationService` class — over-engineering for a comparison function.
- (b) CLI command `mc-dcare validate-scorers` — could be added later, but the core logic should be in the calculator.

**Rationale**: The comparison is a post-processing step on existing results. A method on `CTDICalculator` keeps it co-located with the data it needs.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Water chamber parallel worlds increase TOPAS geometry complexity — potential overlap errors | Gate behind config flag; validate template output in tests before running TOPAS |
| DTM/DTW results change meaning (now "uncalibrated secondary") — breaks existing consumers | `is_primary` flag allows backward-compatible filtering; document the change |
| TLE vs DTM discrepancy is inherent (kerma vs dose) and won't converge with more particles | Report the ratio as a known systematic; reference `docs/ctdi-scoring-methods.md` |
| `BenchmarkCalculator` currently compares all scorers against the same reference | Update to only benchmark primary (TLE) against reference; skip DTM/DTW or compare against TLE |

## Migration Plan

1. Add `scorer_type` and `is_primary` to result dicts — backward-compatible (additive).
2. Update `CalibrationService.apply()` to filter by `is_primary` — changes behaviour for non-TLE results.
3. Add water chamber template option — gated by config, default off.
4. Add `compare_scorers()` method — new functionality, no migration.
5. Update tests to assert on new fields and filtered calibration behaviour.

No rollback needed — old behaviour is preserved by not using `water_chamber_enabled` and by the additive fields.

## Open Questions

- Should `BenchmarkCalculator` skip DTM/DTW comparisons entirely, or report them with a warning label? (Recommendation: skip unless explicitly requested.)
- Should the validation comparison report be written to a file in the runfolder, or just returned as a dict? (Recommendation: returned as dict, CLI or service layer handles persistence.)
