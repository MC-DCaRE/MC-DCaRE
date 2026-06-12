# Tasks: Calibrate All Energy/Fan Combinations + Arc Comparison

## Task 1: Calibrate 80 kV Full Fan (Image Gently)
- [ ] Edit `ctdi_config.yaml`: `imaging_mode: Image Gently`, `dose_calibration_factor: 1.0`
- [ ] Run: `uv run python run_simulation.py run ctdi_config.yaml`
- [ ] Compute CTDI-w: `uv run python calculate_ctdiw.py main <runfolder>`
- [ ] Extract TLE CTDI_w from `CTDIw_results.csv`
- [ ] Compute DCF = (0.9 * 1e-3) / CTDI_w_Gy

## Task 2: Calibrate 100 kV Full Fan (Head)
- [ ] Edit `ctdi_config.yaml`: `imaging_mode: Head`, `dose_calibration_factor: 1.0`
- [ ] Run: `uv run python run_simulation.py run ctdi_config.yaml`
- [ ] Compute CTDI-w: `uv run python calculate_ctdiw.py main <runfolder>`
- [ ] Extract TLE CTDI_w from CSV
- [ ] Compute DCF = (3.2 * 1e-3) / CTDI_w_Gy

## Task 3: Calibrate 125 kV Full Fan (Pelvis Spotlight)
- [ ] Edit `ctdi_config.yaml`: `imaging_mode: Pelvis Spotlight`, `dose_calibration_factor: 1.0`
- [ ] Run: `uv run python run_simulation.py run ctdi_config.yaml`
- [ ] Compute CTDI-w: `uv run python calculate_ctdiw.py main <runfolder>`
- [ ] Extract TLE CTDI_w from CSV
- [ ] Compute DCF = (12.3 * 1e-3) / CTDI_w_Gy

## Task 4: Calibrate 140 kV Half Fan (Pelvis Large)
- [ ] Edit `ctdi_config.yaml`: `imaging_mode: Pelvis Large`, `dose_calibration_factor: 1.0`
- [ ] Run: `uv run python run_simulation.py run ctdi_config.yaml`
- [ ] Compute CTDI-w: `uv run python calculate_ctdiw.py main <runfolder>`
- [ ] Extract TLE CTDI_w from CSV
- [ ] Compute DCF = (37.1 * 1e-3) / CTDI_w_Gy

## Task 5: Cross-validate 80 kV Full Fan
- [ ] Edit `ctdi_config.yaml`: `imaging_mode: Pediatric Head`, `dose_calibration_factor: <DCF from Task 1>`
- [ ] Run: `uv run python run_simulation.py run ctdi_config.yaml`
- [ ] Compute CTDI-w: `uv run python calculate_ctdiw.py main <runfolder>`
- [ ] Compare calibrated CTDI_w to reference 0.5 mGy
- [ ] Report PASS/FAIL (tolerance: ±10%)

## Task 6: Cross-validate 100 kV Full Fan
- [ ] Edit `ctdi_config.yaml`: `imaging_mode: Head SRS`, `dose_calibration_factor: <DCF from Task 2>`
- [ ] Run: `uv run python run_simulation.py run ctdi_config.yaml`
- [ ] Compute CTDI-w
- [ ] Compare calibrated CTDI_w to reference 11.3 mGy
- [ ] Report PASS/FAIL (±10%)

## Task 7: Cross-validate 125 kV Full Fan
- [ ] Edit `ctdi_config.yaml`: `imaging_mode: Thorax Spotlight`, `dose_calibration_factor: <DCF from Task 3>`
- [ ] Run: `uv run python run_simulation.py run ctdi_config.yaml`
- [ ] Compute CTDI-w
- [ ] Compare calibrated CTDI_w to reference 2.5 mGy
- [ ] Report PASS/FAIL (±10%)

## Task 8: Arc dependence test for 125 kV Half Fan
- [ ] Create a custom config based on Pelvis (125 kV, Half Fan, full arc=900s) but reduced:
  - `sequential_times: 40` (half of 80)
  - `timeline_end: 450 s` (half of 900 s)
- [ ] Run with `dose_calibration_factor: 1.0` (raw)
- [ ] Compute CTDI-w
- [ ] Verify raw CTDI_w ≈ half the Pelvis raw value (linear scaling check)
- [ ] Run `calculate_ctdiw.py benchmark` with reference = 7.95 mGy (= 15.9/2 for half arc)
- [ ] Report PASS/FAIL (±10% against half-arc reference)

## Task 9: Update calibration.example.yaml
- [ ] Remove spurious 120 kV Full Fan entry
- [ ] Fill in computed DCFs for all 5 groups
- [ ] Add measurement metadata (reference protocol, reference CTDI, date)
- [ ] Commit updated file

## Task 10: Summary report
- [ ] Tabulate all DCFs with (kV, fan, phantom) keys
- [ ] Tabulate all cross-validation results (protocol, reference, simulated, % error, PASS/FAIL)
- [ ] Document arc-dependence test conclusion
- [ ] Note any anomalies or recommendations
