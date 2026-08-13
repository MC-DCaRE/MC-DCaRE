# phantom-library Specification

## Purpose

An age/sex/size-percentile-keyed library of voxelized ICRP mesh-type reference
computational phantoms, loaded via a single config-driven voxel path. Covers
adult (ICRP 145 MRCP-AM/AF) and paediatric (ICRP Publication 156, ages 0/1/5/10/
15 y x M/F), with optional body-size percentiles. Replaces the hardcoded
single-adult-male post-hoc swap.

## ADDED Requirements

### Requirement: Phantom selected by age, sex, and size percentile

`PhantomConfig` SHALL resolve a unique voxelized phantom from `phantom_age`
(adult | 0y | 1y | 5y | 10y | 15y), `phantom_sex` (AM | AF), and
`phantom_size_percentile` (10 | 50 | 90, default 50). The resolved
`phantom_name` SHALL follow the convention `MRCP_{sex}` (adult p50),
`MRCP_{sex}_{age}` (paediatric p50), or `MRCP_{sex}_{age}_p{percentile}`.

#### Scenario: Adult male default
- **WHEN** no phantom fields are set
- **THEN** `phantom_name` resolves to `MRCP_AM`

#### Scenario: Paediatric selection
- **WHEN** `phantom_age = "5y"` and `phantom_sex = "AF"`
- **THEN** `phantom_name` resolves to `MRCP_AF_5y`

### Requirement: Voxelized phantom loaded as a divided box

The phantom include (`phantomVoxel.j2`) SHALL render a TOPAS `TsBox` divided by
`XBins`/`YBins`/`ZBins` with a per-voxel `VoxelMaterials` vector loaded from the
phantom's voxel directory. The component SHALL be parented to `"World"` so the
phantom is stationary while the beam rotates.

#### Scenario: Rendered voxel box
- **WHEN** `phantomVoxel.j2` is rendered for a resolved phantom
- **THEN** the output contains `Type = "TsBox"`, bin counts, and a
  `VoxelMaterials` reference to the phantom's materials include

### Requirement: Voxel directory contract

Each voxelized phantom directory SHALL contain `phantom.npy` (int32 material-ID
grid for post-processing), `phantomVoxel.txt` + `icrp_materials.txt` (template
includes), and `material_map.txt` (organ/density/HU map). The voxel directory
path SHALL resolve to `{phantom_voxel_directory}/{phantom_name}_{voxel_size_mm}mm`.

#### Scenario: Directory resolved from name
- **WHEN** `phantom_name = "MRCP_AF_5y"` and `phantom_voxel_size_mm = 5.0`
- **THEN** the voxel directory is `.../MRCP_AF_5y_5.0mm`

### Requirement: Voxelizer is the single entry point

`tools/voxelize_phantom.py` SHALL produce all contract outputs (`.npy`,
`phantomVoxel.txt`, `icrp_materials.txt`, `material_map.txt`) from a TetGen
`.node`/`.ele`/`.material` mesh for any phantom name. No other script SHALL
perform voxelization.

#### Scenario: Voxelizer emits all outputs
- **WHEN** the voxelizer runs on a paediatric mesh
- **THEN** the output directory contains `phantom.npy`,
  `phantomVoxel.txt`, `icrp_materials.txt`, and `material_map.txt`

### Requirement: Paediatric data sourced from ICRP 156

The paediatric mesh source SHALL be the ICRP Publication 156 electronic
supplement (ages 0/1/5/10/15 y x M/F). The ingest procedure SHALL be documented
in `data/P145/README.md` including provenance and any `tetgen` conversion step.

#### Scenario: Ingest documented
- **WHEN** a new paediatric phantom is added
- **THEN** `data/P145/README.md` records the source, format, and voxelization command
