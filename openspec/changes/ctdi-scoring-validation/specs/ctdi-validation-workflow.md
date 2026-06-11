## ctdi-validation-workflow

### Requirement
Provide a structured comparison between TLE and analogue scorer results for validation and quality assurance.

### Specification
- `CTDICalculator.compare_scorers(results: List[Dict]) -> Dict` takes the output of `calculate()` and returns:
  - `"tle_vs_dtm_ratio"`: per-position and overall ratio of TLE CTDI_w to DTM CTDI_w
  - `"tle_vs_dtw_ratio"`: per-position and overall ratio of TLE CTDI_w to DTW CTDI_w
  - `"systematic_note"`: human-readable note explaining kerma-vs-dose discrepancy
- The method raises `ValueError` if `results` does not contain at least TLE and one analogue scorer.
- No file I/O — returns a dict. Persistence is the caller's responsibility.

### Acceptance Criteria
- Given results with TLE, DTM, and DTW entries, `compare_scorers()` returns ratios for all pairings.
- Given results with only TLE, `compare_scorers()` raises `ValueError`.
- Unit tests cover: full comparison, missing analogue scorer, TLE-only.
