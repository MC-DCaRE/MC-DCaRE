# Proposal: Calibrate All Energy/Fan Combinations + Arc Comparison

## Summary

Calibrate all 5 remaining unique (kV, fan) beam qualities against the user's reference CTDI table, populate `calibration.yaml` with computed DCFs, and empirically test whether calibration transfers from full-arc (360°) to partial-arc (~200°) configurations.

## Motivation

Only one of six beam-quality groups is currently calibrated (125 kV, Half Fan, DCF=0.0016725). The remaining 5 groups need calibration before the simulation can produce clinically meaningful dose values. Additionally, the question of arc-length dependence of DCF is open and can be answered with one controlled test.

## Calibration Groups

| Group | kV | Fan | Phantom | Protocols | Reference CTDI |
|-------|----|------|---------|-----------|---------------|
| 1 | 80 | Full | 16 cm | Image Gently, Paediatric Body, Pediatric Head | 0.5 - 0.9 mGy |
| 2 | 100 | Full | 16 cm | Head, Extremity Spotlight, Head SRS | 3.2 - 11.3 mGy |
| 3 | 125 | Full | 32 cm | 4D/Abdo/Pelvis/Thorax Spotlight | 2.5 - 12.3 mGy |
| 4 | 125 | Half | 32 cm | **DONE** (DCF=0.0016725, PASS) | 1.3 - 15.9 mGy |
| 5 | 140 | Half | 32 cm | Pelvis Large | 37.1 mGy |
| 6 | 140 | Full | 32 cm | kV-kV Pelvis Large (no reference) | N/A |

## Arc Dependence Test

The user's question: does a DCF calibrated on a full-arc protocol transfer to a partial-arc protocol with the same beam quality?

**Confounded in reference data**: In the reference table, all Half Fan protocols (e.g. Pelvis) use full arcs (360°) and all Full Fan protocols (e.g. Pelvis Spotlight) use partial arcs (~200°). There is no same-kV+fan pair with different arc lengths.

**Test design**: After calibrating 125 kV Half Fan (DCF=0.0016725), run a custom config with the same kV/fan but shorter timeline (partial arc). Expected result: calibrated CTDI agrees with the reference value within tolerance. If it does, DCF is arc-independent.

## Scope

### In scope
1. Run 4 uncalibrated simulations (DCF=1.0) — one representative protocol per beam-quality group
2. Compute DCF for each from reference CTDI
3. Cross-validate on a second protocol per group (same kV+fan, different mAs)
4. Populate `calibration.example.yaml` with computed DCFs
5. Test arc dependence: custom partial-arc run for 125 kV Half Fan, verify DCF holds
6. Document all results

### Out of scope
- 140 kV Full Fan (kV-kV mode, no reference CTDI available)
- Persistent `calibration.yaml` file (the existing `calibration.example.yaml` serves as the template; a full persistence layer was designed in the dose-calibration-workflow change but not yet implemented)
- GUI integration
- Uncertainty propagation
- Changes to TOPAS simulation parameters

## Risks

- **Missing 140 Full Fan reference**: kV-kV Pelvis Large has no reference CTDI in the table. May need measurement or can be left uncalibrated.
- **80 kV low statistics**: The reference CTDI for 80 kV Full Fan is 0.5-0.9 mGy. At 1M histories, the simulated dose may be near the noise floor. May need more histories.
- **Arc test inconclusive**: If the partial-arc config uses a different geometry (different field size if fan mode changes), the test is confounded. Must keep kV, fan mode, and field sizes constant — only vary timeline_end and sequential_times.
