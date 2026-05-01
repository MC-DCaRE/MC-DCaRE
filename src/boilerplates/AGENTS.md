# boilerplates

## Purpose
Jinja2 templates and static data files for TOPAS parameter file generation. `TemplateRenderer` renders `.j2` templates with context dicts built by `SimulationMode` implementations. Static `.txt` and `.dat` files are copied as-is into the run directory.

## Architecture
Two layers:
- `headsourcecode_boilerplate.j2` -- Main Jinja2 template. Uses `{{ variable }}` substitutions and `{% if %}` conditionals for fan mode, simulation type, and graphics. Rendered by `TemplateRenderer` to `tmp/headsourcecode.txt`.
- `TOPAS_includeFiles/` -- Sub-templates (`.j2`) and static data files (`.txt`, `.dat`). Sub-templates are rendered per plug position (CTDI) or per run (DICOM). Static files are copied at runtime.

Template rendering flow:
```
Orchestrator
  -> mode.build_main_context(config) -> Dict
  -> renderer.render("headsourcecode_boilerplate.j2", context, "headsourcecode.txt")
  -> mode.build_sub_context(config) -> Dict
  -> renderer.render(sub_template, context, sub_output)
```

CTDI mode additionally concatenates the rendered headsource with per-plug phantom renders into 5 plug files.

## Key Files

| File | Role |
|---|---|
| `headsourcecode_boilerplate.j2` | Main Jinja2 template: world geometry, collimators, beam source, physics, time features, graphics (298 lines) |
| `TOPAS_includeFiles/CTDIphantom_16.j2` | 16cm CTDI phantom template: PMMA cylinder (80mm radius), 5 chamber plugs, couch, 3 scorers |
| `TOPAS_includeFiles/CTDIphantom_32.j2` | 32cm CTDI phantom template: PMMA cylinder (160mm radius), same plug/scorer structure |
| `TOPAS_includeFiles/patientDICOM.j2` | DICOM patient template: TsDicomPatient component, isocenter translation, Schneider HU conversion, DoseToMedium scorer |
| `TOPAS_includeFiles/fullfan.txt` | Full-fan bowtie filter geometry: aluminum trapezoid wedges (static, not templated) |
| `TOPAS_includeFiles/halffan.txt` | Half-fan bowtie filter geometry: offset aluminum wedges (static, not templated) |
| `TOPAS_includeFiles/HUtoMaterialSchneider.txt` | HU-to-material conversion tables (Schneider method) |
| `TOPAS_includeFiles/NbParticlesInTime.txt` | Particle count per time step (900 rows) |
| `TOPAS_includeFiles/Muen.dat` | Binary data file: mass energy-absorption coefficients for TLE scorer |

## Jinja2 Template Variables

### headsourcecode_boilerplate.j2
| Variable | Source | Description |
|---|---|---|
| `g4_data_directory` | `config.general` | Geant4 data path |
| `seed` | `config.general` | Random seed |
| `threads` | `config.general` | Thread count |
| `histories` | `config.general` | Number of histories |
| `sequential_times` | `config.imaging` | Time steps for rotation |
| `timeline_end` | `config.imaging` | Simulation timeline end |
| `rotation_rate` | `config.imaging` | Gantry rotation rate |
| `start_angle` | `config.imaging` | Starting gantry angle |
| `coll1_trans_y` .. `coll4_trans_x` | mode | Collimator blade positions |
| `fan_mode` | `config.imaging` | "Full Fan" or "Half Fan" (conditional include) |
| `simulation_type` | mode | "CTDI" or "DICOM" (conditional include/LayeredMassGeometry) |
| `graphics_enabled` | `config.ctdi`/`config.dicom` | Toggle Qt graphics |
| `phantom_size` | mode | "16" or "32" (CTDI), empty string (DICOM) |

### CTDIphantom_*.j2
| Variable | Source | Description |
|---|---|---|
| `couch_enabled` | `config.ctdi` | Toggle couch geometry |
| `couch_width/thickness/length` | `config.ctdi` | Couch dimensions |
| `plug_position` | CtdiMode | Current active plug name |
| `plug_material_centre/top/bottom/left/right` | CtdiMode | "Air" for active plug, "PMMA" for others |
| `dose_to_medium_zbins/tle_zbins/dose_to_water_zbins` | `config.ctdi` | Scorer bin counts |

### patientDICOM.j2
| Variable | Source | Description |
|---|---|---|
| `dicom_directory` | `config.dicom` | Path to DICOM dataset |
| `isocenter_x/y/z` | `config.dicom` | Isocenter translation |
| `patient_shift_x/y/z` | `config.dicom` | Patient position shifts |
| `output_filename` | DicomMode | Formatted output file name |

## TOPAS Parameter Conventions

Templates follow strict TOPAS syntax (see `.opencode/rules/topas_syntax.md`):
- **Parameter format**: `type:prefix/Name/Property = value # comment`
- **Prefix conventions**: `Ge/` geometry, `So/` sources, `Sc/` scoring, `Ph/` physics, `Tf/` time features, `Ts/` control, `Gr/` graphics
- **Units required** on all `d:` and `dv:` parameters
- **Relative parameters** use bare names without type prefix (e.g., `Ge/CTDI/RMax + Ge/couch/HLY mm`)

## Geometry Hierarchy
```
World
  Rotation (group, time-feature rotation)
    BeamPosition (source location, SAD offset)
    CollimatorsVertical (group)
      Coll1, Coll2 (lead top/bottom blades)
      Coll1steel, Coll2steel (steel backing)
    CollimatorsHorizontal (group)
      Coll3, Coll4 (lead left/right blades)
      Coll3steel, Coll4steel (steel backing)
      BowtieFilter (fullfan or halffan)
    BeamHardeningFilter (titanium)
```

CTDI phantom and couch are parented to `World` (not `Rotation`), so the beam rotates around a stationary phantom. DICOM patient is also parented to `World`.

## Scoring Conventions
Three scorer types in CTDI phantom templates:
1. **TrackLengthEstimator (TLE)** -- requires `Muen.dat` input file
2. **DoseToMaterial (DTM)** -- material set to "Air"
3. **DoseToWater (DTW)** -- with `PreCalculateStoppingPowerRatios = "True"`

## Template Editing Rules
- Jinja2 variables (`{{ var }}`) must match context dict keys from mode `build_*_context()` methods
- `{% if %}` conditionals control include directives and LayeredMassGeometry
- Static `.txt` files (bowtie, HU conversion, particle counts) are copied as-is, not templated
- `ConvertedTopasFile.txt` is generated at runtime by `SpectrumGenerator`, not a template
- Preserve geometry parent-child relationships to avoid TOPAS overlap errors
