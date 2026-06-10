# Explore Brief: Dose Calibration Workflow

## Alternatives Considered

1. **Pre-TOPAS DCF injection (current approach)** — `dose_calibration_factor` baked into `head_calibration_factor.txt` before simulation. Rejected: requires re-running TOPAS to change calibration factor; conflates normalization with empirical correction.

2. **Per-protocol calibration factors** — separate DCF for each of the 21 imaging mode presets. Rejected: rotation direction and mAs don't affect DCF. Only `(kV, fan_mode)` matters. Collapses to 6 unique pairs.

3. **Single global DCF** — one factor for all conditions. Rejected pending testing: kV changes the spectrum shape (different bin counts at different kV). DCF may differ per kV. User will test and discover whether one factor suffices.

4. **Per-phantom calibration** — separate factors for 16cm and 32cm phantoms. Rejected: phantom is the measurement medium, not a calibration variable. Geometry handles phantom physics.

**Selected: per-(kV, fan_mode) DCF, applied post-hoc, stored in calibration.yaml.**

## Calibration Factor Dimensions

### Unique (kV, fan_mode) pairs (6 total)

| kV | Fan Mode |
|----|----------|
| 80 | Full Fan |
| 100 | Full Fan |
| 125 | Full Fan |
| 125 | Half Fan |
| 140 | Full Fan |
| 140 | Half Fan |

### Factor decomposition

```
norm_factor = 4πr² × f(kV, 1 mAs) / N_total    (SpekPy-derived, stored in runfolder)
mAs          = simulation config mAs              (linear scale factor, exact)
DCF          = D_measured / D_sim                 (empirical, keyed by kV + fan_mode)
```

`D_absolute = D_raw × norm_factor × mAs × DCF(kV, fan_mode)`

## Cross-Module Data Flows

1. **SpectrumGenerator** computes `norm_factor` (currently called `calib_factor` with DCF=1.0) → writes to `tmp/head_calibration_factor.txt`
2. **CTDICalculator** reads `head_calibration_factor.txt` from runfolder → multiplies raw dose by that factor
3. **New: CalibrationService** reads `calibration.yaml` → provides `lookup_dcf(kV, fan_mode)` and `compute_dcf(simulated_Gy, measured_mGy)`
4. **New: CalibrationService.apply()** takes CTDICalculator output, looks up DCF, scales by mAs ratio if target_mAs differs from simulation mAs

### calibration.yaml schema

```yaml
machine: "TrueBeam-SN1234"
date_calibrated: "2026-06-10"
calibrations:
  - kV: 120
    fan_mode: "Full Fan"
    reference_mAs: 100
    measured_ctdi_w_mGy: 45.2
    dcf: 1.034
```

### Runfolder provenance (structured metadata)

Replace the unstructured `head_calibration_factor.txt` with a structured file containing: SpekPy inputs (kV, th, dk, z, mas), SpekPy version, total histories, norm_factor decomposed from mAs, mAs value, DCF used (1.0 for calibration runs).

## Known Open Questions

1. Will DCF differ significantly across kV values? User will test empirically. YAML supports per-kV entries regardless.
2. Should calibration.yaml live in the project root, a config directory, or next to the simulation config? Propose project root alongside existing config YAMLs.
3. Should CalibrationService be a CLI command, a GUI workflow, or both? Scope to service-layer first; CLI/GUI integration is a separate change.
