# bowtie-filter Specification

## Purpose

Defines the CBCT bow-tie filter as a TOPAS `TsCAD` tessellated-mesh component
loaded from a processed binary STL (full-fan from measured geometry, half-fan
derived), placed in the collimator hierarchy downstream of the beam-hardening
filter. The bow-tie is geometric in both filtration modes so the angular
off-axis profile is preserved. A legacy CSG fallback is retained.

## ADDED Requirements

### Requirement: Bow-tie loaded as a tessellated mesh

The bow-tie include templates (`bowtie_ff.j2`, `bowtie_hf.j2`) SHALL render a
TOPAS geometry component of type `"TsCAD"` with `FileFormat = "stl"` that loads
the processed STL by basename (`fullfan` or `halffan`) without extension. The
material SHALL be `"Aluminum"` and `Units` SHALL interpret STL coordinates in
millimetres.

#### Scenario: Full-fan renders TsCAD
- **WHEN** `bowtie_ff.j2` is rendered
- **THEN** the output contains `Type = "TsCAD"`, `FileFormat = "stl"`,
  `InputFile = "fullfan"`, `Material = "Aluminum"`, and `Units = 1.0 mm`

#### Scenario: Half-fan is laterally offset
- **WHEN** `bowtie_hf.j2` is rendered
- **THEN** the output sets a non-zero `TransX` matching the half-fan offset
  convention and `InputFile = "halffan"`

### Requirement: STL assets present in the runfolder

The mode's file-copy step SHALL place `fullfan.stl` and `halffan.stl` in the
runfolder working directory, because `TsCAD` resolves `InputFile` relative to
the TOPAS current working directory.

#### Scenario: STL copied to runfolder
- **WHEN** a CTDI/phantom run is prepared with the new bow-tie
- **THEN** `fullfan.stl` and `halffan.stl` exist in the runfolder

### Requirement: Main template dispatches on fan mode

`headsourcecode_boilerplate.j2` and `ctdi_phsp_score.j2` SHALL include the
bow-tie include matching `fan_mode` (`Full Fan` -> `bowtie_ff`, `Half Fan` ->
`bowtie_hf`). When `imaging.legacy_bowtie` is set, the original CSG
`fullfan.txt`/`halffan.txt` SHALL be included instead.

#### Scenario: Fan-mode dispatch
- **WHEN** the main template is rendered with `fan_mode = "Full Fan"` and
  `legacy_bowtie = false`
- **THEN** the output contains `includeFile = bowtie_ff.txt`

### Requirement: STL processing tool produces valid binary STLs

`tools/process_bowtie_stl.py` SHALL read the ASCII source STL, recenter it by
its bounding-box centroid, decimate to a configurable triangle target, and write
binary STLs. The half-fan output SHALL contain triangles from only one lateral
half of the source.

#### Scenario: Recentered and decimated full-fan
- **WHEN** the tool processes the source STL with a triangle target of N
- **THEN** the output binary STL has centroid at the origin and at most N
  triangles

#### Scenario: Half-fan is one-sided
- **WHEN** the half-fan STL is inspected
- **THEN** all retained triangles lie on one lateral side of the filter centre
