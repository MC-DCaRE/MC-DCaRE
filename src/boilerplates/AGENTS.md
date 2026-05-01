# boilerplates

## Purpose
TOPAS parameter file templates and include files that define the Monte Carlo simulation geometry, beam source, physics, scoring, and visualization. These files are loaded by `BoilerplateManager`, edited in-place by `ParameterEditor` and `SimulationMode` implementations, then written to the run directory for TOPAS execution.

## Architecture
Two layers:
- `headsourcecode_boilerplate.txt` -- Main TOPAS parameter file. Defines world geometry, collimators (X/Y blades with lead + steel layers), beam hardening filter, beam source (position, angular/spatial distribution, spectrum placeholders), physics list, time features (rotation), and graphics. This is the file that modes edit via `ParameterEditor`.
- `TOPAS_includeFiles/` -- Fragment files included by the main boilerplate or by each other. Selected at runtime by the active `SimulationMode` based on phantom type and fan mode.

Include file dependency chain:
```
headsourcecode_boilerplate.txt
  includes: fullfan.txt OR halffan.txt
  includes: patientDICOM.txt (DICOM mode only)
  includes: ConvertedTopasFile.txt (spectrum, generated at runtime)
  includes: NbParticlesInTime.txt (particles per time step)

patientDICOM.txt
  includes: HUtoMaterialSchneider.txt
```

## Key Files

| File | Role |
|---|---|
| `headsourcecode_boilerplate.txt` | Main TOPAS parameter file: world geometry, collimators, beam source, physics, time features, graphics (309 lines) |
| `TOPAS_includeFiles/CTDIphantom_16.txt` | 16cm CTDI body phantom: PMMA cylinder (80mm radius), 5 chamber plugs, couch, 3 scorers (TLE, DoseToMaterial, DoseToWater) |
| `TOPAS_includeFiles/CTDIphantom_32.txt` | 32cm CTDI body phantom: PMMA cylinder (160mm radius), same plug/scorer structure as 16cm variant |
| `TOPAS_includeFiles/fullfan.txt` | Full-fan bowtie filter geometry: aluminum trapezoid wedges (DemoLTrap/DemoRTrap series), side boxes, flat base piece |
| `TOPAS_includeFiles/halffan.txt` | Half-fan bowtie filter geometry: offset aluminum wedges, similar structure with different positioning |
| `TOPAS_includeFiles/patientDICOM.txt` | DICOM patient geometry: TsDicomPatient component, isocenter translation, Schneider HU-to-material conversion, DoseToMedium scorer |
| `TOPAS_includeFiles/HUtoMaterialSchneider.txt` | Hounsfield Unit to material conversion tables (Schneider method): density correction vector, 25 tissue material weights, tissue colors |
| `TOPAS_includeFiles/NbParticlesInTime.txt` | Particle count per time step (900 rows): maps time index to number of histories for time-feature rotation |
| `TOPAS_includeFiles/Muen.dat` | Binary data file: mass energy-absorption coefficients used by TrackLengthEstimator scorer |

## TOPAS Parameter Conventions

These files follow strict TOPAS syntax rules (see `.opencode/rules/topas_syntax.md` for full reference):

- **Parameter format**: `type:prefix/Name/Property = value # comment` where type is `s` (string), `d` (dimensioned double), `u` (unitless), `i` (integer), `b` (boolean), or vector variants (`sv`, `dv`, `uv`, `iv`, `bv`)
- **Prefix conventions**: `Ge/` for geometry, `So/` for sources, `Sc/` for scoring, `Ph/` for physics, `Ma/` for materials, `Tf/` for time features, `Ts/` for TOPAS control, `Gr/` for graphics
- **Units required** on all `d:` and `dv:` parameters (e.g., `cm`, `mm`, `deg`, `MeV`, `g/cm3`)
- **Strings quoted** with double quotes (e.g., `"G4_WATER"`, `"TsCylinder"`)
- **Booleans quoted** (e.g., `"True"`, `"False"`)
- **Relative parameters** use bare parameter names without type prefix (e.g., `Ge/CTDI/RMax + Ge/couch/HLY mm`)
- **No spaces** in parameter names; spaces required around `+`, `-`, `*` operators in relative expressions

## Placeholder Markers
The boilerplate uses `@@PLACEHOLDER@@` markers that `ParameterEditor` replaces at runtime:
- `@@PLACEHOLDER@@` in scorer `Component` fields -- replaced with specific chamber plug name (e.g., `ChamberPlugCentre`)
- `@@PLACEHOLDER@@` in scorer `OutputFile` fields -- replaced with plug-specific output filename suffix

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

For CTDI modes, the phantom and couch are parented to `World` (not `Rotation`), so the beam rotates around a stationary phantom. For DICOM mode, the patient is also parented to `World`.

## Scoring Conventions
Three scorer types used in CTDI phantom files:
1. **TrackLengthEstimator (TLE)** -- requires `Muen.dat` input file for mass energy-absorption coefficients
2. **DoseToMaterial (DTM)** -- material set to "Air" with `PreCalculateStoppingPowerRatios = "True"`
3. **DoseToWater (DTW)** -- with `PreCalculateStoppingPowerRatios = "True"`

All scorers use `ZBins=100` (1mm binning for 100mm chamber length) and `IfOutputFileAlreadyExists = "Overwrite"`.

## Editing Rules
- Do not change parameter names -- `ParameterEditor` matches on exact name strings
- Maintain `includeFile` directives at the top of the main boilerplate
- Preserve geometry parent-child relationships to avoid TOPAS overlap errors
- Dimensional parameters must always include units after editing
- The `ConvertedTopasFile.txt` include is a generated spectrum file, not a boilerplate -- `SpectrumGenerator` creates it at runtime
