## Architecture Overview

This change fixes dose correctness in CTDI phase-space replay. The score
pipeline is validated and unchanged. Two bugs are addressed.

## Bug A: sequential_times normalization

### Current (buggy) replay metadata
`_write_replay_metadata` (src/orchestrator.py) divides `spectrum_fluence` by
`M` and preserves `total_histories = H_score`. It does NOT account for the
replay's `sequential_times` (R).

### Evidence raw_Gy scales with R
- R=1: 13.14, R=10: 88.4 (ratio 6.7, ~R within angular-redistribution noise).
TOPAS re-delivers the phase space at each of the R time steps, so the
delivered count is `N x M x R`, but the normalization only divides by `M`.

### Fix
Divide `spectrum_fluence` by `(M x R)` instead of `M`. Equivalently, set
`total_histories_replay = H_score x R`. Either makes `raw_Gy_replay`
independent of R (and M), matching `raw_Gy_direct`.

Algebraically, with the fix, `raw_Gy_replay = raw_sum_replay x no_particles
/ (H_score x M x R)`, and since `raw_sum_replay ~ N x M x R ~ H_score x M x
R`, the result is intensive and equals the direct per-primary dose x
no_particles.

## Bug B: PhaseSpace-source per-particle inflation -- root cause NOT yet found

### Ruled out (each verified empirically)
1. **Rotation frame** -- DISPROVED. `Component="World"` gives statistically
   identical chamber Sums to `Component="Rotation"` (Centre 1.14e-9 vs
   1.39e-9, Top 1.32e-8 vs 1.35e-8).
2. **PhaseSpaceMultipleUse** -- DISPROVED. M=1 gives raw_Gy 14.23 vs M=5
   13.14 (M-independent; the `/M` compensation works).
3. **`/M` not applied** -- DISPROVED. Replay `spectrum_fluence` = score/5
   exactly.
4. **Phase-space energy** -- DISPROVED. Total .phsp energy (5.6 eV per
   primary crossing PhspSurface) is consistent with the direct beam.
5. **Beam-line difference (score vs direct)** -- DISPROVED. The score and
   headsourcecode templates have identical source + collimators + BHF.
6. **Particle types/weights** -- DISPROVED. 99.97% gammas, weight 1.0,
   positions Y=-86 cm traveling +Y, energies 1-79 keV.

### The anomaly
Per transport, a replayed phase-space particle hits the Top (beam-entry)
chamber ~6x more often than a direct survivor; per-hit TLE deposit is
faithful (~1x). So replayed particles cross the chambers more despite
recorded positions/directions/energies that look correct and a Component
frame that does not matter. Algebraically the per-primary dose should match
the direct exactly; empirically it is ~14x too high in raw_Gy.

### Why it is hard
The recorded particles ARE the direct beam at PhspSurface. Re-injecting them
(even M=1, Component=World) should reproduce the direct's phantom dose. It
does not. The divergence is not visible in the parameter files or .phsp
contents.

### Next investigation (not completed this session)
Track-level debugging -- print step-by-step trajectories of a few
phase-space particles in replay vs the same particles continuing in the
direct run, to find where their paths diverge. Suspects that remain:
- TOPAS PhaseSpace-source direction reconstruction (W-sign flag, V>>0 case)
  placing particles on subtly different trajectories.
- Secondary bookkeeping (phase space captures beam-line secondaries; direct
  generates phantom secondaries -- which "counts" toward chamber dose may
  differ).
- PhaseSpace-source x LayeredMassGeometry interaction (a whole-CTDI
  DoseToMedium scorer returned 0 in replay, hinting the mass geometry is
  set up non-obviously under PhaseSpace replay).

### Decision
Bug B is not safely fixable without the track-level diagnostic; a blind fix
risks false convergence. Bug A is independent and clear, but replay is not
production-usable until Bug B is resolved.

## Risks
- The diagnostic may reveal the frame is NOT the cause (e.g., a TOPAS
  PhaseSpace-MultipleUse interaction). If so, fall back to a World-volume
  spatial diagnostic to localize where replayed particles deposit.
- The arc-rotation fix (candidate 1) must preserve the CT gantry sweep;
  verify the dose is arc-averaged correctly at sequential_times=100.
