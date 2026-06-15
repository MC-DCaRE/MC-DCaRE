# Proposal: Dose Calibration Workflow

## Summary

Add a post-hoc dose calibration workflow that allows simulated CTDI dose to be tuned against measured ion chamber readings on a per-machine basis. The calibration factor (DCF) is keyed by `(kV, fan_mode)`, independent of mAs, and applied after the TOPAS simulation completes. Also fixes a misleading comment in spectrum_generator.py and removes a stale file copy.

## Motivation

The current pipeline produces dose values that require a `dose_calibration_factor` (DCF) to match reality. This factor is injected *before* the TOPAS run via `SpectrumGenerator`, meaning every recalibration requires re-running the full simulation. The existing `BenchmarkCalculator.compute_calibration_factor()` computes `reference/simulated` but has nowhere to persist the result.

From the physics analysis:
- mAs is exactly linear in SpekPy fluence (confirmed at machine precision), so the DCF is independent of mAs
- kV changes the spectrum shape (different bin counts), so DCF may differ per kV
- Rotation direction does not affect calibration (same beam, same geometry)
- Different phantoms are handled by geometry, not calibration
- Post-hoc factor application is mathematically identical to pre-application for both DTM and TLE scorers

There are 6 unique `(kV, fan_mode)` combinations across the 21 imaging mode presets that need calibration entries.

## Calibration Model

### Factor decomposition

The current `head_calibration_factor.txt` contains a single combined value:

```
calib_factor = (4πr² × fluence(kV, mAs) / N_total) × DCF
```

This conflates physics-derived normalization with empirical correction. The clean decomposition is:

```
norm_factor = 4πr² × f(kV, 1 mAs) / N_total     (SpekPy-derived, per-mAs)
D_absolute  = D_raw × norm_factor × mAs × DCF(kV, fan_mode)
```

- `norm_factor` — computed by `SpectrumGenerator` per run, stored in runfolder
- `mAs` — linear scale factor, exact (SpekPy fluence is linear in mAs to machine precision)
- `DCF` — empirical dose calibration factor, keyed by `(kV, fan_mode)`, independent of mAs

Post-hoc application is valid because TOPAS dose is linear in histories. Confirmed for both DTM and TLE scorers.

### Calibration surface (6 unique pairs)

| kV | Fan Mode | Protocols |
|----|----------|-----------|
| 80 | Full Fan | Image Gently |
| 100 | Full Fan | Head |
| 125 | Full Fan | Short Thorax, Spotlight |
| 125 | Half Fan | Thorax, Pelvis |
| 140 | Full Fan | Pelvis Large (kV-kV) |
| 140 | Half Fan | Pelvis Large (CBCT) |

### calibration.yaml schema

Lives in project root alongside existing config YAMLs.

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

### Cross-module data flow

1. **SpectrumGenerator** computes `norm_factor` (with DCF=1.0) → writes to `tmp/simulation_metadata.yaml`
2. **CTDICalculator** reads metadata from runfolder → produces raw scaled dose
3. **CalibrationService** reads `calibration.yaml` → provides `lookup_dcf(kV, fan_mode)` and `compute_dcf(simulated_Gy, measured_mGy)`
4. **CalibrationService.apply()** takes CTDICalculator output, applies DCF, scales by mAs ratio if target differs from simulation

## Scope

### In scope

1. **calibration.yaml** — per-machine calibration data file with DCF keyed by `(kV, fan_mode)`, reference measurement details, and metadata
2. **CalibrationService** in `src/services/` — compute DCF from measurement vs simulation, lookup DCF, apply calibration with mAs scaling
3. **Runfolder provenance** — structured `simulation_metadata.yaml` in runfolder containing: SpekPy inputs (kV, th, dk, z, mas), SpekPy version, total histories, norm_factor decomposed from mAs, mAs value, DCF used (1.0 for calibration runs), fan_mode, seed, threads, timestamp
4. **Remove stale file copy** — stop copying `NbParticlesInTime.txt` to runfolders (it's a TOPAS output log, never referenced by any parameter file)
5. **Fix `dk` comment** — `dk=0.2` in `SpectrumGenerator` is keV energy bin width, not mm Al filtration

### Out of scope

- GUI integration for calibration (service-layer only)
- CLI commands for calibration (can be a follow-up)
- Automated simulation sweeps across multiple kV values
- Uncertainty propagation through the calibration chain
- Changes to the TOPAS simulation itself (beam geometry, physics, scoring)
- Changes to how mAs enters the normalization (current SpekPy approach is correct)

## Dependencies

- Existing `CTDICalculator` and `BenchmarkCalculator` remain unchanged
- `SpectrumGenerator` continues to compute the SpekPy-derived normalization factor
- `head_calibration_factor.txt` format may change to structured metadata

## Risks

- **Breaking change**: If `head_calibration_factor.txt` format changes, existing runfolders become incompatible with the new `CTDICalculator`. Mitigate by keeping backward-compatible reading.
- **Calibration accuracy**: The `4πr²` isotropic assumption overestimates total photon count by ~15-30% due to heel effect. The DCF absorbs this, but users should not interpret DCF as a pure measurement correction.
- **Schema evolution**: calibration.yaml may need additional fields (e.g., measurement uncertainty, date of last calibration). Start minimal and extend.
