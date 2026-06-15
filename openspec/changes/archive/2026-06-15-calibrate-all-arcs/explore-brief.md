# Explore Brief: Calibrate All Energy/Fan Combinations + Arc Comparison

## Reference CTDI Table

User-provided CTDI values (mGy) for 18 Varian TrueBeam protocols:

| Mode Name | kV | Fan | CTDI (mGy) | Trajectory | Exposure (mAs) |
|-----------|----|------|-----------|------------|-------|
| Image Gently | 80 | Full | 0.9 | Half | 100.2 |
| Paediatric Body | 80 | Full | 0.9 | Half | 100.2 |
| Pediatric Head | 80 | Full | 0.5 | Half | 50.1 |
| Head | 100 | Full | 3.2 | Half | 150.3 |
| Extremity Spotlight | 100 | Full | 3.2 | Half | 150.3 |
| Head SRS | 100 | Full | 11.3 | Full | 537 |
| 4D Spotlight | 125 | Full | 6.1 | Half | 373.6 |
| Abdo Spotlight | 125 | Full | 6.6 | Half | 400.8 |
| Pelvis Spotlight | 125 | Full | 12.3 | Half | 751.5 |
| Thorax Spotlight | 125 | Full | 2.5 | Half | 150.3 |
| 4D Thorax | 125 | Half | 9.9 | Full | 671.2 |
| Abdomen | 125 | Half | 10.6 | Full | 716 |
| Breast 360 | 125 | Half | 1.3 | Full | 89.5 |
| Head and Shoulders | 125 | Half | 4.0 | Full | 268.5 |
| Pelvis | 125 | Half | 15.9 | Full | 1074 |
| SBRT Spine | 125 | Half | 5.3 | Full | 358 |
| Thorax | 125 | Half | 4.0 | Full | 268.5 |
| Pelvis Large | 140 | Half | 37.1 | Full | 1700.5 |

Note: no reference CTDI provided for 140 kV Full Fan (kV-kV mode only).

## Unique (kV, fan) Calibration Groups

Grouping by beam quality (same kV + fan = same DCF):

| Group | kV | Fan | Phantom | Representative Protocols | CTDI Range |
|-------|----|------|---------|------------------------|------------|
| 1 | 80 | Full | 16 cm | Image Gently, Paediatric Body, Pediatric Head | 0.5 - 0.9 |
| 2 | 100 | Full | 16 cm | Head, Extremity Spotlight, Head SRS | 3.2 - 11.3 |
| 3 | 125 | Full | 32 cm | 4D Spotlight, Abdo Spotlight, Pelvis Spotlight, Thorax Spotlight | 2.5 - 12.3 |
| 4 | 125 | Half | 32 cm | Pelvis, Thorax, Abdomen, Breast 360, 4D Thorax, SBRT Spine, Head and Shoulders | 1.3 - 15.9 |
| 5 | 140 | Half | 32 cm | Pelvis Large | 37.1 |
| 6 | 140 | Full | 32 cm | kV-kV Pelvis Large (no reference CTDI given) | N/A |

## Phantom Size Mapping

From MC-DCaRE imaging mode definitions:
- **16 cm (head)**: Image Gently, Paediatric Body, Pediatric Head, Head, Extremity Spotlight, Head SRS
- **32 cm (body)**: All Spotlight modes, Thorax, Pelvis, Abdomen, 4D, Breast, SBRT, Head and Shoulders

## Calibration Status

| Group | Status |
|-------|--------|
| 125 Half Fan | **DONE**: DCF=0.0016725, validated Thorax vs Pelvis (−0.62%) |
| 125 Full Fan | Not started |
| 100 Full Fan | Not started |
| 80 Full Fan | Not started |
| 140 Half Fan | Not started |
| 140 Full Fan | No reference data available |

## Half Arc vs Full Arc Question

The user asks: "if I calibrate based on a full arc, is a half arc CTDI still going to be accurate?"

Key insight from the reference table: **Trajectory and Fan mode are confounded**. All Full Fan protocols use a half trajectory (501s, ~200°, full fan bowtie) and all Half Fan protocols use a full trajectory (900s, 360°, half fan bowtie). There is no protocol pair with the same kV+fan but different arc lengths in the reference table.

To test arc dependence in isolation, a custom config would be needed: take a calibrated (kV, fan) pair and run with a modified timeline to change the arc length while keeping everything else constant.

The physics expectation: DCF is a beam-quality correction (spectrum, filtration, normalization). Arc length is a geometric scaling factor that cancels out in the DCF ratio (measured/simulated). Therefore DCF should be independent of arc length, just as it is independent of mAs.

## Run Time Estimate

Each simulation: 80 sequential times, 1M histories, 20 threads → ~30 min. 80M particles total per run.

Calibration runs needed: 4 (one per uncalibrated group) = ~2 hours.
Validation runs needed: 1-2 cross-checks per group = ~2-3 hours.
Arc-dependence test: 1 custom run = ~30 min.

Total: ~5 hours wall time if run sequentially.
