# Explore Brief: CTDI Phase Space Source

## Rejected Alternatives

1. **Score before collimators** — Would give blade-independent files (one per energy), but collimator tracking is the expensive upstream work. Keeping collimators in the replay run defeats the speedup purpose. Rejected because most compute time is likely in lead collimator tracking.

2. **Score in World frame (outside Rotation group)** — Would bake rotation into the file, making it rotation-pattern-specific. Rejected because it prevents reusing the same file for different rotation modes (continuous, kV-kV step, different rates).

3. **No Rotation group in replay** — Was explored but conflicts with the fact that the beam needs to rotate around the stationary phantom. The Rotation group + time feature is the correct mechanism for this.

## Final Approach

**Two-step architecture**: scoring run (once per protocol) → replay run (many times, fast).

### Scoring Run
- Full source-side geometry: source → collimators → bowtie → BHF (0.7mm Ti)
- PhaseSpace scorer attached to a surface after the BHF
- KillAfterPhaseSpace = True (no phantom tracking needed)
- No phantom, no dose scorers
- No IncludeTOPASTime — the beam is time-independent (tube output is constant)
- Output: Binary format .phsp file

### Replay Run
- PhaseSpace source (Type = "PhaseSpace") inside the Rotation group
- Rotation group + time feature KEPT — sweeps the fixed beam pattern around the phantom
- Same Tf/ parameters as scoring run
- Phantom + dose scorers (identical to current)
- No SpekPy, no spectrum file, no collimators, no bowtie, no BHF
- No NbParticlesInTime.txt

### Scoring Surface Placement
- After all source-side geometry (bowtie + BHF)
- Inside the Rotation group (beam's reference frame)
- Two options: (a) score on BHF exit face directly, (b) add a dedicated thin vacuum plane
- BHF exit face is simpler (no new geometry) but needs verification of which face is downstream
- Nested rotations make hand-calculation of absolute position unreliable
- Must verify placement with graphics or test run

### File Format
- Binary format for initial implementation
- Limited format could be considered later (compact, ~15 bytes/particle, works for photons-only)

## Key Data Flows

```
Scoring Pipeline:
  config (imaging mode, blades) → headsourcecode template → TOPAS → .phsp file
  .phsp file → post-processing → particle statistics (energy spectrum, survival fraction, spatial/angular distributions)

Replay Pipeline:
  config (phantom, scorers) + .phsp file → replay template → TOPAS → scorer output files
  scorer output → CtdiCalculator → CalibrationService → results
```

## Phase Space Source Parameters (from TOPAS source code)

- `So/beam/Type = "PhaseSpace"`
- `So/beam/PhaseSpaceFileName = "<path>"`
- `So/beam/Component = "<component>"` — positions the source in the geometry
- `So/beam/PhaseSpaceMultipleUse = <int>` — reuse each particle N times for statistics
- `So/beam/PhaseSpaceIncludeEmptyHistories = "True"` — include empty histories

## Phase Space Scorer Parameters (from TOPAS source code)

- `Sc/PhspOut/Quantity = "PhaseSpace"`
- `Sc/PhspOut/Surface = "<component>/<face>"` — scoring surface
- `Sc/PhspOut/OutputType = "Binary"` — ASCII, Binary, Limited, ROOT
- `Sc/PhspOut/OutputFile = "<name>"`
- `Sc/PhspOut/KillAfterPhaseSpace = "True"` — kill particles after scoring
- `Sc/PhspOut/IfOutputFileAlreadyExists = "Overwrite"`

## Calibration Chain Impact

Current: SpectrumGenerator → norm_factor = N_particles / (histories × mAs) → head_calibration_factor.txt → CalibrationService.apply()

With PhaseSpace: The number of effective histories becomes N_particles_in_file × PhaseSpaceMultipleUse. The norm_factor and calibration factor computation must account for this. SpectrumGenerator may not be needed for replay runs.

## Open Questions

1. **Scoring surface exact position** — Dedicated TsBox approach chosen. TransY must be verified with graphics or test run.
2. **PhaseSpaceMultipleUse value** — How many times to reuse particles? Affects statistics and calibration. Start with 1.
3. **Calibration chain details** — Resolved: replay metadata uses `norm_factor = original_norm_factor / PhaseSpaceMultipleUse`. CTDICalculator computes `calibration_factor = norm_factor × mAs × dcf_used`, producing `original_calibration_factor / M`. CalibrationService.apply() is unchanged.
4. **Exit window + primary collimator** — Not modeled yet. When added, phase space files need regeneration.
5. **Replay source positioning** — `Component = "Rotation"` assumes TOPAS interprets file positions in Component's local frame. If world-frame, double-transformation occurs. Must verify experimentally.
6. **DICOM mode** — Same approach applies but not in scope for this change.
