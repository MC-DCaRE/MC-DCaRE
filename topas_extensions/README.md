# topas_extensions — diagnostic scorer for the phase-space-replay dose bug

This holds a custom OpenTOPAS scorer (`TrackDumper`) built to pinpoint the
replay dose bug tracked in
`openspec/changes/fix-phase-space-replay-dose/`.

## Why this lives here (and not built)

The replay bug is **inside TOPAS**: a PhaseSpace source into a
LayeredMassGeometry (parallel-world) phantom scores ~14x high vs a matched
Beam-source run, with an entry-to-exit gradient. Injection and air transport
were proven byte-faithful; the divergence is generated inside the
parallel-world scorer. Confirming the exact step — and fixing it — needs a
per-step track dump, which requires a TOPAS C++ extension and a TOPAS rebuild.

The opencode agent sandbox is **walled off from `/opt/topas`** (no read of
file contents, no writes), so the agent cannot build or rebuild TOPAS. These
artifacts are staged for you to build/install from a shell that has full
`/opt/topas` access.

## Files

| File | Purpose |
|---|---|
| `TsTrackDumper.cc` | `TsVNtupleScorer` subclass. Dumps one ntuple row per step: `x,y,z (cm)`, direction cosines, `energy (MeV)`, weight, eventID, volume, material. Authored from the [Custom Scorers](https://opentopas.readthedocs.io/en/latest/extension-docs/scoring.html) doc API. |
| `deploy.sh` | Copies the source into the TOPAS extensions tree, rebuilds the `extensions` target, runs `make install`, and smoke-tests on a water box. Run from your own shell. |
| `test_TrackDumper.txt` | Minimal TOPAS param file (10 gammas into a water box with the TrackDumper scorer) for the smoke test. |

## Build & install (do this in your terminal, not the sandbox)

```bash
cd topas_extensions
./deploy.sh
```

If `deploy.sh` reports the extensions CMakeLists doesn't glob sources,
append `TsTrackDumper.cc` to its source list manually and re-run.

## Run the diagnostic

Once installed, attach the scorer to a chamber plug and run two simulations
that differ **only** in the source type:

1. **Beam source** (the direct run, known-correct dose).
2. **PhaseSpace source** (the replay of the scored `.phsp`).

Both with:
```
s:Sc/Track/Quantity  = "TrackDumper"
s:Sc/Track/Component = "ChamberPlugCentre"   # or Top/Bottom/Left/Right
```

Diff the two ntuple outputs (e.g. with `diff`/`csvdiff` on the
`x,y,z,energy,weight,volume,material` columns). The first row where they
diverge is the exact step at which the PhaseSpace-source transport parts
company with the Beam-source transport inside the LayeredMassGeometry. That
locates the TOPAS bug precisely and tells us whether the fix is a TOPAS
parameter, a geometry re-parenting, or an upstream TOPAS patch.

## Expected compile fixes (if any)

`TsTrackDumper.cc` was written from the published doc API without local
header read access. If the build complains, the likely adjustments:
- Base-class constructor arg list — `TsVNtupleScorer` takes the standard 8
  scorer args; verify against `TsVScorer.hh`.
- `RegisterColumnD(name, unit)` — drop the unit arg for unitless columns
  (use `RegisterColumnF`/`RegisterColumnI`/`RegisterColumnS`).
- `fNtuple->Fill(...)` columns must match registration order.
