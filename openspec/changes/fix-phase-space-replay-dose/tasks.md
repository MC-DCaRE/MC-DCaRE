## 1. Diagnose Bug B root cause -- INVESTIGATION COMPLETE, root cause NOT found

- [x] 1.1 Component="World" vs "Rotation": identical dose -- frame DISPROVED.
- [x] 1.2 M=1 vs M=5: M-independent -- M-reuse DISPROVED.
- [x] 1.3 /M compensation: applied (metadata ratio exactly 5) -- DISPROVED.
- [x] 1.4 Phase-space energy, beam-line parity, particle types/weights,
      secondary bookkeeping (all gammas are first-in-history), direction
      cosines (U^2+V^2 <= 1): all physical -- DISPROVED.
- [ ] 1.5 **OPEN**: track-level stepping diagnostic (TOPAS /tracking or a
      custom stepping-action scorer) -- print trajectories of a few
      phase-space particles in replay vs the same particles continuing in
      the direct run, to find where their paths diverge. This is the next
      step; it requires custom TOPAS scoring beyond the current templates.

## 2. Bug A -- normalize replay by (M x sequential_times) -- NOT YET DONE

Deferred: the fix is clear but replay is not usable until Bug B resolves,
and the exact R-delivery model is entangled with the Bug-B investigation.
Do once Bug B is understood, so the fix is validated against a working replay.

- [ ] 2.1 `_write_replay_metadata`: divide `spectrum_fluence` by
      `(M x sequential_times)`; unit-test R-invariance.

## 3. Bug B -- fix -- BLOCKED on task 1.5

- [ ] 3.1 Implement the fix indicated by the track-level diagnostic.

## 4. Convergence validation -- BLOCKED on Bug B fix

- [ ] 4.1 replay raw_Gy lands on direct ~0.92 (single-angle) / ~0.84 (arc).

## 5. Quality gates + docs

- [ ] 5.1 ruff/mypy/pytest; docs; commit; push.
