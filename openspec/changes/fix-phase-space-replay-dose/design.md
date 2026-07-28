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
   identical chamber Sums to `Component="Rotation"`.
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
7. **PhspSurface size / scatter** -- DISPROVED. A 20 cm surface (11 758
   particles, primary-dominated) gives the same replay over-deposit as the
   1 m surface (100 981 particles). BeamHardeningFilter is upstream of
   PhspSurface, so the score captures the post-filter beam.
8. **Air transport** -- DISPROVED. Re-injecting into empty space, 3668 of
   100 979 particles cross the phantom-entry plane Y=-8 cm, matching the
   analytic ~4% aimed at the 16 cm phantom. Directions preserved (the
   near-axial subset that reaches Y=-8 has U std 0.149, V mean 0.968 -- the
   divergent particles simply miss the plane).
9. **Chamber / phantom geometry** -- DISPROVED. The ChamberPlug definitions
   (Type, Parent, Material=Air, RMax, HL, isParallel, ParallelWorldName)
   and `LayeredMassGeometryWorlds` are byte-identical between the direct
   and replay parameter files.

### The anomaly
Among particles that ENTER the phantom, replayed ones cross the Top
(beam-entry) chamber ~6x more often than direct survivors, with an
entry-to-exit gradient (Top per-count TLE 3.83x; Centre 1.27x; Bottom
1.19x). The gradient is the signature of longer tracks (grazing crossings)
on the beam-entry side. Yet the air transport to the phantom is faithful
and the chamber geometry is identical.

### Conclusion
The divergence is inside TOPAS: how PhaseSpace-source particles transport
into the LayeredMassGeometry (parallel-world) phantom differs from how the
same particles continue in a Beam-source history. It is not visible in any
parameter file or .phsp content. Pinning it requires G4 track-level
stepping output (custom Ts stepping action or `/tracking/verbose`) to
compare per-step trajectories of individual phase-space particles in replay
vs the direct run.

## Risks
- The diagnostic may reveal the frame is NOT the cause (e.g., a TOPAS
  PhaseSpace-MultipleUse interaction). If so, fall back to a World-volume
  spatial diagnostic to localize where replayed particles deposit.
- The arc-rotation fix (candidate 1) must preserve the CT gantry sweep;
  verify the dose is arc-averaged correctly at sequential_times=100.
