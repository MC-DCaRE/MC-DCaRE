## 0. Status (2026-07-28)

- [x] Phase 0a: replay source `Component = "World"` (documented default). Done (commit 2520897).
- [x] Phase 0b (Bug A): normalize replay by `(M x sequential_times)`. Done (commit 2520897) + R-invariance unit test.
- [x] Bug B localization: injection + air transport faithful; over-deposit is inside the LayeredMassGeometry parallel-world scorer for PhaseSpace-source particles. Confirmed (commit 7f377ab).
- [~] Phase 1 (custom stepping scorer): **BLOCKED in this environment** -- the opencode permission guard denies writes to `/opt/topas`, so a TOPAS extension cannot be built and TOPAS source cannot be modified/rebuilt here. The diagnostic source is staged at `diagnostics/TsTrackDumper.cc` for deployment where `/opt/topas` is writable.

## 1. Diagnose Bug B root cause -- investigation COMPLETE, root cause localized

- [x] 1.1..1.4 nine suspects ruled out empirically (see design.md).
- [x] 1.5 injection proven byte-faithful (InjectCheck at Y=-85.9 cm).
- [ ] 1.6 **OPEN (needs /opt/topas write access)**: deploy `TsTrackDumper.cc`, rebuild TOPAS extensions, run Beam-source vs PhaseSpace-source, diff per-step ntuples to pinpoint the divergence step.

## 2. Bug A -- DONE
- [x] 2.1 `_write_replay_metadata` divides by `(M x sequential_times)`.

## 3. Bug B fix -- BLOCKED on 1.6
- [ ] 3.1 Apply the fix indicated by the track dump (expected: a TOPAS LayeredMassGeometry/PhaseSpace-source patch, or an application-level workaround if one exists).

## 4. Convergence validation -- BLOCKED on 3.1
- [ ] 4.1 replay raw_Gy lands on direct ~0.92 (single-angle) / ~0.84 (arc).

## 5. Quality gates + docs
- [x] 5.1 AGENTS.md (root + src/) now reference OpenTOPAS docs.
- [ ] 5.2 final commit/push once Bug B is fixed.
