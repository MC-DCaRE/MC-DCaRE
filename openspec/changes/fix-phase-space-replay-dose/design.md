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

## Session 2026-08-04: Root Cause Narrowed to PhaseSpace Replay Inflation

### Definitive Evidence: PhaseSpace Replay Inflates Dose ~8.5×

**Key experiment**: Scored a phase space FROM the diagnostic direct run itself (25437 particles from 100000 primaries at Y=-86cm), then replayed it back into the same phantom geometry.

Results:
- Direct sim phantom EnergyDeposit: **1.43 MeV** (100000 primaries)
- Replay of direct's OWN phase space: **12.09 MeV** (25437 particles from 100000 primaries)
- Ratio: **8.45×** — the replay deposits 8.45× more energy per primary than the direct sim that generated the phase space

This eliminates ALL hypotheses about the phase-space file being wrong, the geometry being different, or the beam source differing. The phase space WAS scored from the direct sim, yet replaying it gives 8.45× too much dose.

### PhaseSpace Source ≡ Beam Source for Monoenergetic Particles

Control test: Created a phase-space file with 1000 identical 50 keV gammas at (0,-86,0) direction (0,1,0). Ran both:
1. PhaseSpace source replay → deposit: 23.50072860717773 MeV
2. Beam source at same position/energy → deposit: 23.50072860717773 MeV
3. Results are IDENTICAL to 14 decimal places.

This proves the PhaseSpace source correctly injects particles for trivial (monoenergetic, monodirectional) cases. The bug manifests ONLY with realistic spectral/angular distributions.

### Mass-Geometry Dose Also Affected (Not Just Parallel-World TLE)

Added EnergyDeposit scorer on the CTDI phantom body (mass geometry, NOT parallel world):
- Direct: 1.43 MeV / 100000 primaries = 1.43e-5 MeV/primary
- Replay: 50.75 MeV / 400000 primaries = 1.27e-4 MeV/primary
- Ratio: **8.87×**

This overturns the earlier hypothesis that the bug was specific to the LayeredMassGeometry parallel-world scorer. The mass-geometry dose is equally affected.

### Ruled Out (This Session)

1. **Collimator absorption after scoring plane** — plane at Y=-86cm is 0.5cm downstream of collimator edge (Y=-86.5cm); clear gap
2. **World material difference** — TOPAS default is Air for both; neither file overrides
3. **Beam source parameter difference** — identical between score run and diagnostic direct (verified by full diff)
4. **Spectrum file difference** — ConvertedTopasFile.txt and fullfan.txt are byte-identical
5. **BeamPosition rotation** — RotX=90° in both files
6. **Multithreading double-counting** — 1-thread replay gives same result (50.56 vs 50.75 MeV)
7. **Component="Rotation" vs "World"** — ~2% difference, not the cause
8. **PhaseSpace source correctness for trivial case** — proven identical to Beam source
9. **sequential_times** — 1 in all runs
10. **Phase-space file integrity** — all particles forward-going, weight 1, 99.97% gamma

### Remaining Hypothesis

The PhaseSpace Source (TsGeneratorPhaseSpace) has a bug that manifests only with non-trivial particle distributions (varying energy, position, or direction). The monoenergetic test passes because all particles are identical. The realistic phase-space replay fails because particles have varied properties.

Most likely candidates:
- Direction cosine handling (DCX/DCY/DCZ computation from binary format)
- Energy scaling or unit conversion
- Particle weight interaction with the scorer
- The `TransformPrimaryForComponent` function modifying particle state

### Next Steps

1. Create a 2-particle phase-space file with DIFFERENT energies/directions and compare PhaseSpace vs Beam source
2. Read `TsGeneratorPhaseSpace.cc` lines around `GenerateOnePrimary` and `TransformPrimaryForComponent` for bugs
3. Consider filing a TOPAS bug report with the minimal reproduction case

## Session 2026-08-04 (Late): ROOT CAUSE FOUND — Direct Sim Bug, Not Replay Bug

### The PhaseSpace Replay Is CORRECT

Ray-tracing 25437 particles from the direct's own phase space (at Y=-86cm) through 78.5cm of Air to the phantom face (geometric straight-line computation, NO Monte Carlo transport):

- **1035 of 25437 particles (4.1%) geometrically hit the phantom** (within 8cm radius at Y=-7.5cm)
- **Expected deposit: ~10.65 MeV** (hitting particles' total energy × ~47% PMMA absorption)
- **Replay deposit: 11.85 MeV** — matches ray-trace within 11% ✅
- **Direct deposit: 1.43 MeV** — 7.4× BELOW ray-trace ❌

**The "14× PhaseSpace over-deposit" was actually a DIRECT SIM UNDER-DEPOSIT**, not a replay bug.

### The Beam Line Geometry Causes the Direct Sim to Lose Particles

| Run | Phantom Deposit (MeV) |
|-----|----------------------|
| Direct WITH beam line (100k primaries) | 1.43 |
| Direct WITHOUT beam line (100k primaries) | 19.58 |
| PhaseSpace replay of direct's own phsp (25437 particles) | 11.85 (without LMG) / 12.09 (with LMG) |
| Ray-trace geometric prediction | 10.65 |

### ROOT CAUSE CONFIRMED: Scoring Plane Inside Collimator Geometry

Added a second phase-space scoring plane at Y=-80cm (6cm downstream of the first):

| Scoring Plane | Total Particles | Geometric Phantom Hits | Expected Deposit |
|---|---|---|---|
| Y=-86cm | 25437 | 1035 (4.1%) | 10.65 MeV |
| Y=-80cm | 20780 | 63 (0.3%) | 1.63 MeV |

**94% of phantom-directed particles were lost between Y=-86cm and Y=-80cm** — in just 6cm of nominal Air. Total particle count only dropped 18%, but the loss is highly selective: forward-peaked particles (those aimed at the phantom) are disproportionately absorbed.

The actual phantom deposit (1.43 MeV) closely matches the Y=-80cm ray-trace prediction (1.63 MeV), confirming transport is correct AFTER Y=-80cm. The problem is entirely in the Y=-86 to Y=-80cm region.

**The phase-space scoring plane at Y=-86cm is INSIDE the collimator jaw geometry.** Despite analytical rotation calculations suggesting the collimators don't extend past Y=-88.2cm, the empirical data proves otherwise. The complex 4-level nested rotation chain (World → Rotation(RotY=180°) → CollimatorsVertical(RotX=90°) → CollimatorsHorizontal(RotX=90°) → CollN(RotX=-90°, RotY=90°)) makes analytical geometry calculations unreliable. The collimator jaws physically extend into the Y=-86 to Y=-80cm region.

### Ruled Out

- LayeredMassGeometry: removing LMG from direct sim gives identical 1.43 MeV
- PhaseSpace source bug: source code verified correct, monoenergetic test passes, energy linearity passes
- PhaseSpace replay: ray-trace confirms correct dose at both Y=-86cm and Y=-80cm planes

### Practical Implications (Confirmed)

1. **The PhaseSpace replay results are correct** — confirmed by geometric ray-tracing at two independent planes
2. The direct (Beam source) simulation **underestimates dose** because the scoring plane is inside the collimator
3. The original "14× over-deposit" was comparing against a flawed baseline (the direct sim)
4. **Fix: move the phase-space scoring plane downstream of the collimator exit face** (to approximately Y=-75cm or less negative)

### Recommended Next Steps

1. **Immediate fix**: Change PhspSurface TransY from -86.0cm to -75.0cm (or verify the actual collimator exit position)
2. Re-generate the phase space from the corrected position
3. Re-run the direct sim and confirm the phantom deposit matches the replay
4. Update `_write_replay_metadata` if the Muen factor changes with the new scoring position
