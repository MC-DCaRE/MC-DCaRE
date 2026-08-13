# reference-phantom-geometry Specification

## Purpose

Defines the TOPAS geometry and scoring for an ICRP 145 tetrahedral-mesh
reference phantom (MRCP-AM/AF) placed supine head-first on the CT couch: the
`TsTetGeom` component loaded from `.node`/`.ele`/`.material` data, supine
positioning and rotation driven by `PhantomConfig`, couch integration without
overlap, and `TsTetGeomScorer` organ-dose output.

## Requirements

### Requirement: Phantom loaded as a tetrahedral mesh

The phantom include template (`phantomICRP145.j2`) SHALL render a TOPAS geometry component of type `"TsTetGeom"` that loads the MRCP tetrahedral mesh (`MRCP_AM` or `MRCP_AF`) from a configurable data directory containing the `.node`, `.ele`, and `.material` files. The component SHALL be parented to `"World"` (not the rotating `"Rotation"` group) so the phantom remains stationary while the beam rotates.

#### Scenario: Rendered include references TsTetGeom and World
- **WHEN** the phantom include is rendered with an AM config
- **THEN** the output contains `Type = "TsTetGeom"`, `Parent = "World"`, and references the `MRCP_AM` data directory

#### Scenario: Sex selection switches the mesh
- **WHEN** the include is rendered with sex `"AF"`
- **THEN** the output references `MRCP_AF` data rather than `MRCP_AM`

### Requirement: Phantom placed supine head-first on the couch

The template SHALL rotate and translate the phantom so it lies supine (posterior surface down, anterior face up) and head-first along the scanner's long axis, with its back resting on the couch top. Because the native mesh is in centimeters with the body height along native Z (standing), the template SHALL apply the rotation that maps the body-height axis onto the scanner axis and set the vertical translation from the phantom posterior surface to the couch top, using offsets supplied by `PhantomConfig`.

#### Scenario: Supine placement parameters emitted
- **WHEN** the include is rendered with non-zero placement offsets
- **THEN** the output emits `TransX`/`TransY`/`TransZ` and `RotX`/`RotY`/`RotZ` parameters derived from `PhantomConfig`

#### Scenario: Native units handled
- **WHEN** the template emits translations
- **THEN** values account for the mesh's centimeter coordinate units so the phantom is positioned in the TOPAS world consistently with the couch geometry

### Requirement: Couch integration without overlap

The couch geometry SHALL be parented (directly or via an intermediate group such as the existing `couchgroup` pattern) so its top-level ancestor is `"World"`. The phantom `TsTetGeom` component SHALL itself declare `Parent = "World"`. The phantom posterior SHALL sit on or just above the couch top surface with a non-coincident boundary to avoid Geant4 overlap errors. The couch parameters (width, thickness, length, material) SHALL be driven by `PhantomConfig`, reusing the existing couch pattern.

#### Scenario: Couch and phantom both resolve to World
- **WHEN** the include is rendered
- **THEN** the phantom component declares `Parent = "World"`, and the couch component's parent chain resolves to `"World"` (the couch MAY be wrapped in an intermediate group whose own parent is `"World"`)

#### Scenario: Couch geometry is configurable
- **WHEN** the include is rendered with couch width, thickness, and length set
- **THEN** the rendered couch component emits those dimensions

### Requirement: Organ dose scored with the tet-mesh scorer

The template SHALL define at least one dose scorer using `Quantity = "TsTetGeomScorer"` scoped to the phantom component, restricted to the configured organ media, and writing a CSV output file named from the run identifiers (mirroring the DICOM `output_filename` convention).

#### Scenario: Scorer targets the tet phantom
- **WHEN** the include is rendered
- **THEN** the output contains a scorer with `Quantity = "TsTetGeomScorer"` whose `Component` is the phantom geometry and whose `OutputFile` follows the run's naming convention

### Requirement: Phantom data assembled and kept out of version control

The system SHALL assemble, per sex, a directory containing `MRCP_{AM,AF}.node`, `MRCP_{AM,AF}.ele`, and `MRCP_{AM,AF}.material`. The `.material` file SHALL be sourced from the P145 Geant4 example (or generated from `_media.dat`), since `Phantom_data` ships only `_media.dat`. The `data/` directory containing these large files SHALL be gitignored and MUST NOT be committed.

#### Scenario: Material file present for each sex
- **WHEN** the phantom data directory is prepared
- **THEN** it contains `MRCP_AM.material` and `MRCP_AF.material` alongside the matching `.node` and `.ele` files

#### Scenario: Data is not tracked by git
- **WHEN** `git status` is run after populating `data/`
- **THEN** the ICRP 145 phantom files do not appear as tracked or untracked-eligible additions (covered by the `data/` ignore rule)

### Requirement: Main template includes the phantom sub-file

`headsourcecode_boilerplate.j2` SHALL include a conditional `{% if simulation_type == 'ICRP145' %}includeFile = phantomICRP145.txt{% endif %}` so the rendered main parameter file pulls in the phantom include for ICRP145 runs. The shared beam, collimator, source, and time-feature sections SHALL be unchanged.

#### Scenario: Main template includes phantom file for ICRP145
- **WHEN** the main template is rendered with `simulation_type = "ICRP145"`
- **THEN** the output contains `includeFile = phantomICRP145.txt`

#### Scenario: Main template unaffected for other modes
- **WHEN** the main template is rendered with `simulation_type` of `"DICOM"` or `"CTDI"`
- **THEN** the output does NOT contain the phantom include line

