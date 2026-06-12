## 1. Scorer-type labelling in CTDICalculator

- [x] 1.1 Add scorer type inference to `_process_file_type()`: parse `_tle`, `_dtm`, `_dtw` suffix from CSV filename and include `"scorer_type"` and `"is_primary"` fields in the result dict.
- [x] 1.2 Add `compare_scorers(results) -> Dict` method to `CTDICalculator`: compute TLE/DTM and TLE/DTW ratios per position, return structured comparison dict with `systematic_note`.
- [x] 1.3 Update `calculate()` to group results by scorer type (currently returns one dict per file type; change to one dict per scorer type, each containing averaged per-position doses).
- [x] 1.4 Add tests for scorer type inference, `compare_scorers()`, and grouped `calculate()` output.

## 2. CalibrationService scorer-aware apply

- [x] 2.1 Update `CalibrationService.apply()` to accept `scorer_type: str = "tle"` parameter; filter `calculate()` results to only calibrate matching scorer type; return uncalibrated results for others with `"dcf_applied": null`.
- [x] 2.2 Update `BenchmarkCalculator.compare()` to benchmark only TLE results by default.
- [x] 2.3 Update tests for scorer-filtered calibration and benchmark behaviour.

## 3. Water chamber template option

- [x] 3.1 Add `water_chamber_enabled: bool = False` to `CtdiConfig` dataclass.
- [x] 3.2 Update `CTDIphantom_16.j2`: when `water_chamber_enabled`, add 5 water-filled parallel world volumes and 5 DTM scorers with `_water_dtm` output suffix.
- [x] 3.3 Update `CTDIphantom_32.j2`: same water chamber additions.
- [x] 3.4 Update `CtdiMode.build_sub_context()` to pass `water_chamber_enabled` to template.
- [x] 3.5 Update `CTDICalculator._find_chamber_files()` to discover `_water_dtm.csv` files and include them in results with `"scorer_type": "dtw_water"`.
- [x] 3.6 Add tests for water chamber template rendering and CSV discovery.

## 4. Documentation

- [x] 4.1 Verify `docs/ctdi-scoring-methods.md` is complete and references the correct scorer terminology from the implementation.
- [x] 4.2 Update `src/AGENTS.md` and `tests/AGENTS.md` to reflect new scorer-aware processing.
