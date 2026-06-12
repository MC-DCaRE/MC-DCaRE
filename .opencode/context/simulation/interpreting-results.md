<!-- Context: simulation/interpreting-results | Priority: high | Version: 1.0 | Updated: 2026-06-12 -->

# Interpreting Simulation Results

**Purpose**: How to read TOPAS output, compute CTDI metrics, compare runs, and calibrate against measurement.
**Audience**: Simulation agent.

## TOPAS CSV Output Format

Files: `ChamberPlug{Position}_{scorer}.csv` where:
- Position: Centre, Top, Bottom, Left, Right
- Scorer: tle, dtm, dtw, water_dtm

Each CSV contains z-bin dose data (energy deposition per voxel along the phantom axis).

**Reading results:**
```bash
# List all output files
ls runfolder/<timestamp>/ChamberPlug*.csv

# View a specific scorer output
head runfolder/<timestamp>/ChamberPlugCentre_tle.csv
```

## CTDI-w Calculation

```bash
uv run python calculate_ctdiw.py main runfolder/<timestamp>
```

Output: `CTDIw_results.csv` in the runfolder containing:
- CTDI-w per scorer type (TLE, DTM, DTW)
- Per-position dose values
- Weighted composite

**Formula:**
```
CTDI-w = (1/3) x Centre + (2/3) x mean(Top, Bottom, Left, Right)
```

## Scorer Interpretation

### TLE (Primary)
- Track Length Estimator — variance reduction technique
- Directly analogous to ion chamber measurement
- Calibrated via DCF
- **Use for all quantitative dose reporting**
- Units in CSV: arbitrary (normalized by histories). Apply DCF for absolute dose.

### DTM (Dose To Medium)
- Raw energy deposition in phantom medium (PMMA)
- Not directly comparable to measurement
- Useful for relative comparisons within a single simulation set

### DTW (Dose To Water)
- Dose scaled to water-equivalent
- Also not measurement-comparable
- Useful for cross-phantom comparisons

### water_dtm (Optional)
- DTM scored in water-filled chamber volumes
- Only present when `water_chamber_enabled = true`
- 5 additional scorers (one per position)

## Calibration Workflow

### Step 1: Run Uncalibrated
```bash
# DCF = 1.0 in config
uv run python run_simulation.py run config/my_sim.yaml
```

### Step 2: Measure
Take physical CTDI-w measurement with ion chamber in CTDI phantom.

### Step 3: Benchmark
```bash
uv run python calculate_ctdiw.py benchmark runfolder/<timestamp> -r <measured_mSv>
```
Output:
- Simulated CTDI-w (TLE, DCF=1.0)
- Measured CTDI-w
- Recommended DCF = measured / simulated
- PASS/FAIL against tolerance

### Step 4: Apply DCF
Either:
- Update `general.dose_calibration_factor` in config and re-run
- Or apply post-hoc via CalibrationService (multiplies TLE results by DCF)

**DCF depends on beam quality** — different factors for each (kVp, filtration, fan_mode) combination.

## Comparing Runs

### Side-by-Side Comparison
1. Read `simulation_metadata.yaml` from each runfolder
2. Identify parameter differences (kVp, mAs, histories, DCF, phantom, protocol)
3. Compute or read CTDI-w results for each
4. Tabulate with percentage differences

### Key Comparison Points
| Parameter | Effect on Dose |
|-----------|---------------|
| kVp (higher) | Higher dose, harder spectrum |
| Filtration (more) | Lower dose, harder spectrum |
| Phantom 16→32 cm | Lower peripheral dose, similar central |
| Fan mode (full→half) | Different beam geometry, different dose distribution |
| Histories | Affects statistical precision, not mean dose |
| DCF | Direct scaling of TLE results |

### Presentation
```
| Metric        | Run A (100kV, Head) | Run B (120kV, Head) | Diff  |
|---------------|---------------------|---------------------|-------|
| CTDI-w (TLE)  | 12.3 mGy            | 18.7 mGy            | +52%  |
| CTDI-w (DTM)  | 14.1 (uncalibrated) | 21.4 (uncalibrated) | +52%  |
| Histories     | 500k                | 500k                | —     |
| DCF           | 0.82                | 0.85                | —     |
```

## Common Questions

**"Is my result reasonable?"**
- Head (16cm) CTDI-w at 100 kV: typically 10-30 mGy (depends on mAs, DCF)
- Body (32cm) CTDI-w at 120 kV: typically 5-15 mGy
- Centre/peripheral ratio: ~0.5-0.8 (lower for larger phantom)

**"Why is CTDI-w zero?"**
- Histories too low for statistical significance
- Geometry misconfiguration (field not covering phantom)
- Scorer not attached to correct volume

**"How many histories do I need?"**
- Minimum 100k for qualitative results
- 500k-1M for quantitative work (±5% statistical uncertainty)
- 5M+ for high-precision calibration work
