## ctdi-scorer-selection

### Requirement
`CTDICalculator` must label every result by scorer type and designate TLE as primary.

### Specification
- `calculate()` returns `List[Dict]` where each dict includes `"scorer_type": "tle"|"dtm"|"dtw"` and `"is_primary": bool`.
- `is_primary` is `True` iff `scorer_type == "tle"`.
- `_process_file_type()` infers scorer type from the CSV filename suffix (`_tle.csv`, `_dtm.csv`, `_dtw.csv`).
- All three scorer types are processed in every `calculate()` call — no filtering at this layer.
- `CalibrationService.apply()` accepts an optional `scorer_type: str = "tle"` parameter to select which results to calibrate. Default is TLE only. Results not matching the selected scorer type are returned uncalibrated with `"dcf_applied": null`.
- `BenchmarkCalculator.compare()` benchmarks only TLE results by default. Other scorer types are skipped unless explicitly requested.

### Acceptance Criteria
- Given a runfolder with all 15 CSV files (5 positions × 3 scorers), `calculate()` returns 3 results (one per scorer type), each with correct `scorer_type` and `is_primary` fields.
- `CalibrationService.apply()` with default settings applies DCF only to the TLE result.
- Existing tests updated to assert on new fields without breaking.
