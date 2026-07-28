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

### Conclusion -- BUG LOCALIZED to in-phantom LayeredMassGeometry scoring
A PhaseSpace scorer placed 0.1 mm downstream of the injection point
(InjectCheck at Y=-85.9 cm, replay WITH the phantom present) shows the
re-injected particles are byte-identical to the input file: X std 15.218 vs
15.361, U std 0.5540 vs 0.5535, V 0.6104 vs 0.6040, E 0.0223 vs 0.0223
(506 665 crossings = 100 951 x M=5). **Injection is faithful.** Combined
with the faithful air transport to Y=-8 cm, the particle stream entering the
phantom is correct.

Therefore the ~14x over-deposit is generated *inside the phantom*, in the
LayeredMassGeometry (parallel-world) chamber scoring. Corroborating signs:
- A whole-CTDI `DoseToMedium` scorer returns 0 in replay (the base PMMA mass
  geometry is not being scored the same way under PhaseSpace).
- An embedded (non-parallel) Centre chamber also returns 0, while the
  parallel-world Centre returns non-zero -- the parallel-world scorer is
  crediting tracks that do not physically enter the chamber, and it credits
  them differently for PhaseSpace-source vs Beam-source particles.

This is a TOPAS-internal interaction between the PhaseSpace source and the
LayeredMassGeometry parallel-world navigator/scorer. It cannot be reached
from a parameter file. Two viable fix directions:

1. **TOPAS-level**: G4 stepping diagnostic (custom `TsVNtupleScorer` or
   stepping action) to compare per-step tracks in the parallel worlds for
   Beam-source vs PhaseSpace-source, then either a TOPAS patch or a bug
   report upstream. Requires TOPAS dev-header access to write the extension
   (this environment can list `/opt/topas` but not read header contents, so
   the extension must be authored against the published API and built where
   the headers are readable).
2. **Application-level workaround**: drop LayeredMassGeometry for replay and
   score one plug position per run (the pre-2026-05-22 approach). This
   avoids the parallel-world navigator entirely. Cost: 5x the replay runs,
   but each is correct. Needs validation that single-plug replay converges
   to the direct dose.

## Risks
- The diagnostic may reveal the frame is NOT the cause (e.g., a TOPAS
  PhaseSpace-MultipleUse interaction). If so, fall back to a World-volume
  spatial diagnostic to localize where replayed particles deposit.
- The arc-rotation fix (candidate 1) must preserve the CT gantry sweep;
  verify the dose is arc-averaged correctly at sequential_times=100.
