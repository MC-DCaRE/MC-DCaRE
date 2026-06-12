## Architecture Overview

The phase space feature introduces a two-step simulation workflow for CTDI mode. The existing direct-beam pipeline remains unchanged (when `phase_space_mode = "off"`). Two new modes are added alongside it.

```
                          ┌─────────────────────────────────┐
                          │     phase_space_mode = "off"     │
                          │     (current pipeline, unchanged) │
                          └─────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                  phase_space_mode = "score"                       │
│                                                                   │
│  SpectrumGenerator → headsourcecode (full beam line)              │
│                         ↓                                         │
│  PhaseSpace Scorer after BHF (inside Rotation group)              │
│  KillAfterPhaseSpace = True                                       │
│  No phantom, no dose scorers                                      │
│                         ↓                                         │
│  .phsp file (Binary) + simulation_metadata.yaml                   │
│                         ↓                                         │
│  PhaseSpaceAnalyzer → beam statistics                             │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                  phase_space_mode = "replay"                      │
│                                                                   │
│  .phsp file → PhaseSpace Source (inside Rotation group)           │
│               Rotation group + time feature rotates source         │
│                         ↓                                         │
│  Phantom (CTDIphantom_*.j2) + dose scorers                        │
│                         ↓                                         │
│  scorer output files → CtdiCalculator → CalibrationService        │
│                                                                   │
│  ❌ No SpectrumGenerator, no collimators, no bowtie, no BHF       │
└──────────────────────────────────────────────────────────────────┘
```

## Config Changes

Add to the `ctdi` section of `SimulationConfig`:

| Parameter | Type | Default | Values |
|-----------|------|---------|--------|
| `phase_space_mode` | `str` | `"off"` | `"off"`, `"score"`, `"replay"` |
| `phase_space_file` | `str` | `""` | Path to `.phsp` file (used in replay mode) |
| `phase_space_multiple_use` | `int` | `1` | How many times to reuse each particle in replay |

The YAML config would look like:

```yaml
ctdi:
  phase_space_mode: "score"    # or "replay" or "off"
  phase_space_file: "path/to/beam_exit_phsp.phsp"
  phase_space_multiple_use: 10
  # ... existing ctdi params ...
```

## Template Design

### Scoring Template: `ctdi_phsp_score.j2`

Based on `headsourcecode_boilerplate.j2` with these modifications:
- Keep all source-side geometry (Rotation group, BeamPosition, collimators, bowtie, BHF)
- Keep physics, seed, threads, time feature, graphics
- Remove phantom include logic (`{% if simulation_type == 'CTDI' %}`)
- Remove `sv:Ph/Default/LayeredMassGeometryWorlds` (no parallel worlds)
- Add scoring surface geometry (thin vacuum TsBox after BHF)
- Add PhaseSpace scorer on the scoring surface
- Keep SpectrumGenerator dependency (needs spectrum for source)

Scoring surface — a dedicated thin vacuum TsBox parented to the Rotation group, positioned after the BHF:

```
s:Ge/PhspSurface/Type     = "TsBox"
s:Ge/PhspSurface/Parent   = "Rotation"
s:Ge/PhspSurface/Material = "Vacuum"
d:Ge/PhspSurface/HLX      = 50.0 cm
d:Ge/PhspSurface/HLY      = 0.1 mm    # thin along beam axis
d:Ge/PhspSurface/HLZ      = 50.0 cm
d:Ge/PhspSurface/TransY   = <calculated downstream position>
```

The exact TransY must be verified experimentally (graphics or test run). The surface must clear all source-side geometry without gaps. A dedicated surface is preferred over scoring on the BHF exit face because it captures scattered particles that bypass the BHF. After verification (task 9), TransY will be hardcoded in the template as a geometry constant derived from the beam line component positions — not a user-configurable parameter.

PhaseSpace scorer parameters:
```
s:Sc/PhspOut/Quantity            = "PhaseSpace"
s:Sc/PhspOut/Surface             = "PhspSurface/YPlusSurface"
s:Sc/PhspOut/OutputType          = "Binary"
s:Sc/PhspOut/OutputFile          = "beam_exit_phsp"
b:Sc/PhspOut/KillAfterPhaseSpace = "True"
s:Sc/PhspOut/IfOutputFileAlreadyExists = "Overwrite"
```

No `IncludeTOPASTime` — the beam is time-independent.

### Replay Template: `ctdi_phsp_replay.j2`

Minimal template containing:
- World geometry (same as headsourcecode)
- Physics (same modules, same EM range)
- Seed, threads, Ts control parameters
- Rotation group with time feature (same Tf/ parameters as scoring run)
  - PhaseSpace source attached to the Rotation group via `Component = "Rotation"`
- No BeamPosition, collimators, bowtie, BHF
- No spectrum include (ConvertedTopasFile.txt not needed)
- No NbParticlesInTime.txt
- Phantom include (CTDIphantom_*.j2, same as current) — concatenated using the same `_generate_single_parameter_file()` pattern as direct CTDI mode
- All dose scorers (same as current)

PhaseSpace source parameters:
```
s:So/beam/Type                  = "PhaseSpace"
s:So/beam/PhaseSpaceFileName    = "{{ phase_space_file }}"
s:So/beam/Component             = "Rotation"
i:So/beam/PhaseSpaceMultipleUse = {{ phase_space_multiple_use }}
```

**Positioning note**: The source attaches to the Rotation group (`Component = "Rotation"`). Particle positions in the `.phsp` file are recorded in Rotation's local frame at the scoring surface location. TOPAS interprets these positions relative to the Component's coordinate system, so the spatial offset is preserved. The Rotation group's time feature then sweeps these fixed-pattern particles around the stationary phantom. This must be verified experimentally — if TOPAS interprets file positions in world frame instead of component-local frame, the replay would double-transform particles.

## Mode Branching in CtdiMode

`CtdiMode` checks `config.ctdi.phase_space_mode` and branches:

| Mode | Template | SpectrumGenerator | Phantom | Scorers |
|------|----------|-------------------|---------|---------|
| `off` | `headsourcecode_boilerplate.j2` + `CTDIphantom_*.j2` | Yes | Yes | Dose |
| `score` | `ctdi_phsp_score.j2` | Yes | No | PhaseSpace |
| `replay` | `ctdi_phsp_replay.j2` + `CTDIphantom_*.j2` | No | Yes | Dose (TLE, DTM, DTW) + optional water chamber DTM |

For `score` mode:
- `build_main_context()` provides the same context as current (source-side params)
- `build_sub_context()` is not called (no phantom sub-template)
- `execute()` runs a single TOPAS process with the scoring template
- After execution, `PhaseSpaceAnalyzer` processes the output file

For `replay` mode:
- `build_main_context()` provides replay-specific context (phase_space_file, phase_space_multiple_use, rotation params, phantom params)
- `build_sub_context()` provides the same phantom context as current
- `execute()` runs a single TOPAS process with the replay template + phantom include

## Calibration Chain

### Current Flow
```
SpectrumGenerator.generate()
  → norm_factor = N_particles / (histories × mAs)
  → head_calibration_factor.txt
  → CalibrationService.apply(dcf)
```

### Replay Flow

`CTDICalculator` computes `calibration_factor = norm_factor × mAs × dcf_used` from `simulation_metadata.yaml`, then multiplies raw TOPAS dose by this factor to get absolute dose.

For replay mode, the raw dose scales with `PhaseSpaceMultipleUse`:
- Direct beam: `raw_dose ∝ N` (N survivors out of H histories reach the phantom)
- Replay: `raw_dose_replay ∝ N × M` (N survivors, each replayed M times)
- Ratio: `raw_dose_replay / raw_dose = M`

So `calibration_factor_replay = calibration_factor_direct / M`.

The simplest correct approach: write the replay run's `simulation_metadata.yaml` with `norm_factor` set to `original_norm_factor / M`. Then `CTDICalculator` computes:
```
calibration_factor = (original_norm_factor / M) × mAs × dcf_used
                   = original_calibration_factor / M
```

This correctly compensates for the M× higher raw dose from particle reuse. No other calibration changes needed — `CalibrationService.apply()` applies the same DCF and mAs_ratio as direct mode.

For the replay's `simulation_metadata.yaml`:
- `norm_factor`: original_norm_factor / M
- `mAs`: same as scoring run
- `dcf_used`: same as scoring run
- `total_histories`: N × M (effective histories, for provenance)
- `phase_space_multiple_use`: M
- `phase_space_source`: path to .phsp file (for provenance)

This metadata must be stored alongside the `.phsp` file (copy `simulation_metadata.yaml` from the scoring runfolder, then adjust `norm_factor`).

## PhaseSpaceAnalyzer

New service class that reads Binary format `.phsp` files and computes:

| Statistic | Description |
|-----------|-------------|
| `particle_count` | Total particles in file |
| `survival_fraction` | particle_count / original_histories |
| `energy_spectrum` | Histogram of particle energies (bin edges configurable) |
| `spatial_distribution_x` | Histogram of x positions |
| `spatial_distribution_y` | Histogram of y positions |
| `angular_distribution_dx` | Histogram of x direction cosines |
| `angular_distribution_dy` | Histogram of y direction cosines |
| `particle_types` | Count by particle type (all gammas for kV) |
| `mean_energy` | Mean and std of energy distribution |
| `file_size_mb` | File size in MB |

Output: structured dict + optional matplotlib plots saved to runfolder.

## Orchestrator Changes

`Orchestrator.run_with_runfolder()` branches on mode:

```python
mode = self._get_mode(config)

if config.ctdi.phase_space_mode == "score":
    # Render scoring template
    # Run SpectrumGenerator (still need spectrum for source)
    # Execute TOPAS
    # Run PhaseSpaceAnalyzer on output
    # Copy simulation_metadata.yaml to runfolder
elif config.ctdi.phase_space_mode == "replay":
    # Render replay template + phantom include (same concatenation as _generate_single_parameter_file)
    # Skip SpectrumGenerator
    # Override prepare_run to skip copy_common_files (no spectrum/calibration files needed)
    # Instead, copy: phase_space_file, scoring run's simulation_metadata.yaml (with adjusted norm_factor)
    #                Muen.dat (needed by TLE scorer), bowtie filter (not needed — no bowtie in replay)
    # Execute TOPAS
    # Run existing post-processing (CtdiCalculator, CalibrationService)
    # For replay, compute_histories() returns N × M (particle_count × PhaseSpaceMultipleUse) for provenance
else:
    # Current pipeline unchanged
```

## File Management

Scoring run outputs to the runfolder:
- `beam_exit_phsp.phsp` — the phase space file
- `simulation_metadata.yaml` — original run metadata (for calibration)

Replay run expects:
- `.phsp` file path in config
- Corresponding `simulation_metadata.yaml` in the same directory (or copied to runfolder)

Both files should be co-located. Convention: `<runfolder>/phase_space/beam_exit_phsp.phsp` + `<runfolder>/phase_space/simulation_metadata.yaml`.

## Open Questions

1. **Scoring surface position** — Dedicated geometry with TransY that must be verified by test run with graphics. Recommend dedicated geometry approach.
2. **PhaseSpaceMultipleUse default** — Needs experimental tuning. Start with 1 (no reuse), increase based on statistical convergence analysis.
3. **PhaseSpaceAnalyzer Binary format parsing** — Need to implement IAEA Binary format reader. TOPAS Binary format is a specific binary layout. Check if TOPAS provides any Python utilities for reading.
4. **Replay source positioning** — `Component = "Rotation"` assumes TOPAS interprets file positions in the Component's local frame. If TOPAS uses world-frame positions instead, particles would be double-transformed by the Rotation group. Must verify experimentally.
