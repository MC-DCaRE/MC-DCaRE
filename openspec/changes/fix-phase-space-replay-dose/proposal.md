## Why

The phase-space replay pipeline runs (unblocked by `6f41b5d`, which added the
missing `LayeredMassGeometryWorlds` line) and produces TLE signal in all five
chambers, but the absolute dose is wrong. A head-to-head convergence test
against a matched direct simulation:

| Run | raw_Gy |
|---|---|
| Direct 80 kV Image Gently, single-angle, 5M primaries | **0.92** |
| Direct 80 kV FF calibration, full-arc, 500M primaries | 0.84 |
| Replay 100k particles x M=5, sequential_times=1 | **13.14** |
| Replay same, sequential_times=10 | **88.4** |

Two independent bugs:

**Bug A -- `sequential_times` is unnormalized.** raw_Gy scales with R
(13.1 -> 88.4 at x10). The replay delivers `N x M x R` particles but
`_write_replay_metadata` only divides `spectrum_fluence` by `M`.

**Bug B -- ~15x per-particle chamber inflation from a PhaseSpace-source
coordinate-frame mismatch.** The `/M` compensation is correctly applied
(metadata ratio exactly 5.0) and the normalization formula is algebraically
correct. The inflation is entirely in chamber **hit-rate** (8-24x, varying
geometrically: Top 23.7x, Right 8.3x); per-hit TLE deposit is faithful (~1x).
So replayed particles are placed/aimed wrong, not scored wrong. Root cause
(hypothesis to confirm by diagnostic): `So/beam/Component = "Rotation"`
re-interprets the world-frame recorded positions/directions in the
Rotation-local frame, which carries the `RotY = 180 deg + yaw` (+ pitch/roll)
transform -- the double-transform the archived `2026-06-12-ctdi-phase-space`
design flagged (design.md:127) but never verified for dose (only geometry
errors).

## What Changes

1. Bug A: divide the replay normalization by `(M x sequential_times)`.
2. Bug B: fix the PhaseSpace-source frame so replayed particles deposit in
   the correct location; confirm with a World-volume diagnostic.
3. Re-run the convergence test: replay raw_Gy must land on the direct value
   (~0.92 single-angle, ~0.84 full-arc) within MC noise.

## Capabilities

### Modified Capabilities
- `phase-space-replay`: dose correctness -- single canonical normalization
  accounting for M and sequential_times; correct PhaseSpace-source frame.
