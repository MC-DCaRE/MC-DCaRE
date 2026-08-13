# spectrum-generation Specification

## Purpose

Defines SpekPy spectrum generation for the kV beam source: the anode voltage,
anode angle, and an optional base filtration applied in the `hybrid` mode
(inherent + collimator Aluminum). The spectrum SHALL record its first half-value
layer (mmAl). Beam-hardening-filter thickness is configurable and flows into the
geometry template.

## ADDED Requirements

### Requirement: Filtration mode selects where base filtration lives

`SimulationConfig.imaging.filtration_mode` SHALL accept `geometric` or `hybrid`
(default `hybrid`). In `hybrid` mode the generator SHALL apply the uniform base
filtration (inherent 2.7 mm Al + collimator 0.3 mm Al) to the SpekPy spectrum.
In `geometric` mode no spectral filtration SHALL be applied. The Ti
beam-hardening filter and the bow-tie remain geometric in both modes.

#### Scenario: Hybrid mode filters the spectrum
- **WHEN** the spectrum is generated with `filtration_mode = "hybrid"`
- **THEN** SpekPy `.filter('Al', 2.7).filter('Al', 0.3)` is applied and the
  recorded HVL is greater than the bare-spectrum HVL

#### Scenario: Geometric mode applies no spectral filter
- **WHEN** the spectrum is generated with `filtration_mode = "geometric"`
- **THEN** no `.filter(...)` calls are made on the SpekPy spectrum

### Requirement: First half-value layer is computed and recorded

The generator SHALL compute the first HVL in mmAl via `s.get_hvl1()` and write
it to the simulation metadata under `spekpy.hvl_mmAl` and to the calibration
factor text output.

#### Scenario: HVL recorded in metadata
- **WHEN** a spectrum is generated
- **THEN** `simulation_metadata.yaml` contains `spekpy.hvl_mmAl` as a positive
  float

### Requirement: Beam-hardening-filter thickness is configurable

`SimulationConfig.imaging.bhf_thickness_mm` (default 0.89) SHALL flow into the
beam-hardening-filter geometry component half-length instead of a hardcoded
value. The default reflects the measured filtration stack.

#### Scenario: BHF thickness drives the template
- **WHEN** the head-source template is rendered with `bhf_thickness_mm = 0.89`
- **THEN** the beam-hardening-filter `HLZ` equals 0.89 mm

### Requirement: Spectrum energy/weights written for the TOPAS beam source

The generator SHALL write `ConvertedTopasFile.txt` containing
`dv:So/beam/BeamEnergySpectrumValues` (energies, keV) and
`uv:So/beam/BeamEnergySpectrumWeights` (fluence-normalized), included by the main
template. This behaviour is unchanged from the current implementation.

#### Scenario: Spectrum file produced
- **WHEN** a run is prepared
- **THEN** `ConvertedTopasFile.txt` exists and contains both the values and
  weights vectors
