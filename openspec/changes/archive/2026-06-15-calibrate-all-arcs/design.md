# Design: Calibrate All Energy/Fan Combinations + Arc Comparison

## Calibration Method

Same chain as validated on 125 Half Fan:

```
DCF = (reference_CTDI_mGy * 1e-3) / simulated_CTDI_w_Gy
```

Each calibration run uses `dose_calibration_factor: 1.0` in config. After the run, `uv run python calculate_ctdiw.py main <runfolder>` produces the raw CTDI_w in Gy. DCF computed from the formula above.

Cross-validation: set `dose_calibration_factor` to the computed DCF in config, run a second protocol with the same (kV, fan) but different mAs. Run `calculate_ctdiw.py main` and check the calibrated CTDI_w against the reference value. PASS if within 10% tolerance.

## Run Plan

### Phase 1: Calibrate (4 runs, ~30 min each = ~2 hours)

| Run | Config Change | Protocol | Purpose |
|-----|---------------|----------|---------|
| R1 | `imaging_mode: "Image Gently"`, `dose_calibration_factor: 1.0` | 80 kV Full Fan | Calibrate Group 1 |
| R2 | `imaging_mode: "Head"`, `dose_calibration_factor: 1.0` | 100 kV Full Fan | Calibrate Group 2 |
| R3 | `imaging_mode: "Pelvis Spotlight"`, `dose_calibration_factor: 1.0` | 125 kV Full Fan | Calibrate Group 3 |
| R4 | `imaging_mode: "Pelvis Large"`, `dose_calibration_factor: 1.0` | 140 kV Half Fan | Calibrate Group 5 |

For each:
1. Edit `ctdi_config.yaml` — update `imaging_mode` and reset `dose_calibration_factor: 1.0`
2. Run: `uv run python run_simulation.py run ctdi_config.yaml`
3. Compute: `uv run python calculate_ctdiw.py main <runfolder>`
4. Extract TLE CTDI_w from CSV output
5. Compute DCF = reference_mGy * 1e-3 / simulated_CTDI_w_Gy

### Phase 2: Cross-validate (3-4 runs, ~2 hours)

| Run | Calibration DCF | Validation Protocol | Same Group As | Expected CTDI |
|-----|----------------|-------------------|---------------|---------------|
| V1 | Group 1 DCF | Pediatric Head (80 kV, 50.1 mAs) | R1 | 0.5 mGy |
| V2 | Group 2 DCF | Head SRS (100 kV, 537 mAs) | R2 | 11.3 mGy |
| V3 | Group 3 DCF | Thorax Spotlight (125 kV Full Fan, 150.3 mAs) | R3 | 2.5 mGy |
| V4 | Group 5 DCF | (none — only one protocol in this group) | R4 | N/A |

### Phase 3: Arc Dependence Test

**Goal**: Test whether the 125 kV Half Fan DCF (calibrated on full-arc Pelvis) holds for a partial-arc configuration with the same beam quality.

**Config modification**: Copy the Pelvis config but:
- `timeline_end`: reduce from 900 s to 450 s (half the rotation arc)
- Keep `sequential_times: 80` unchanged (same statistics as full arc)
- Keep everything else identical: kV, fan_mode, field sizes, blade openings, histories

*Note: `NumberOfSequentialTimes` only controls total particles (statistics multiplier), not the arc geometry. The arc is controlled entirely by `timeline_end` and `rotation_rate`.*

**Predictions**:
- Raw CTDI_w ≈ 4.75 Gy (half of 9.51 Gy full arc, because same total_histories and head_cal_factor but half the rotation delivers half the dose per particle)
- Calibrated: 4.75 × 1000 × 0.001672 = 7.94 mGy (vs 7.95 mGy expected for half-arc reference = 15.9 / 2)
- If DCF is arc-independent: calibrated CTDI_w matches 7.95 mGy within statistics

Run the half-arc config with `dose_calibration_factor: 1.0` (raw), compute CTDI_w, then apply DCF manually or via benchmark.

### Phase 4: Update calibration.example.yaml

Write computed DCFs into `calibration.example.yaml`:

```yaml
calibrations:
  - kV: 80
    fan_mode: "Full Fan"
    reference_mAs: 100
    measured_ctdi_w_mGy: 0.9
    dcf: <computed>
  - kV: 100
    fan_mode: "Full Fan"
    reference_mAs: 150
    measured_ctdi_w_mGy: 3.2
    dcf: <computed>
  - kV: 125
    fan_mode: "Full Fan"
    reference_mAs: 750
    measured_ctdi_w_mGy: 12.3
    dcf: <computed>
  - kV: 125
    fan_mode: "Half Fan"
    reference_mAs: 1080
    measured_ctdi_w_mGy: 15.9
    dcf: 0.0016725
  - kV: 140
    fan_mode: "Half Fan"
    reference_mAs: 1700
    measured_ctdi_w_mGy: 37.1
    dcf: <computed>
  - kV: 140
    fan_mode: "Full Fan"
    reference_mAs: null
    measured_ctdi_w_mGy: null
    dcf: null
```

Also remove the spurious 120 kV Full Fan entry that doesn't correspond to any TrueBeam kV.

## Preset Selection Rationale

For each (kV, fan) group, pick the protocol with the highest mAs as the calibration reference. Higher mAs → higher statistics → lower relative noise in the simulated CTDI_w. This minimizes statistical uncertainty in the DCF.

| Group | Calibration Protocol | mAs | Rationale |
|-------|---------------------|-----|-----------|
| 80 Full Fan | Image Gently | 100.2 | Highest mAs in group (vs 50.1 for Pediatric Head) |
| 100 Full Fan | Head | 150.3 | Highest mAs in group (vs 150.3 for Extremity; Head SRS has 537 but uses different geometry/start_angle per imaging modes) |
| 125 Full Fan | Pelvis Spotlight | 751.5 | Highest mAs in group |
| 125 Half Fan | Pelvis | 1080 | Already calibrated and validated |
| 140 Half Fan | Pelvis Large | 1700.5 | Only protocol in group |
