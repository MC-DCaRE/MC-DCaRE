# Design -- add-bowtie-spectrum-validation

## Filtration-mode decision

Two modeling philosophies, both retained and selectable via
`imaging.filtration_mode`:

| Mode | Inherent + collimator Al | Ti BHF | Bow-tie | Angular profile |
|---|---|---|---|---|
| `geometric` | geometry | geometry | geometry (STL) | captured |
| `hybrid` (default) | **SpekPy spectrum** | geometry | geometry (STL) | captured |

Rationale: inherent (2.7 mm Al) and collimator-window (0.3 mm Al) filtration are
pre-bow-tie and spatially uniform, so folding them into the source spectrum is
physically equivalent and avoids wasteful uniform-slab transport. The Ti BHF and
bow-tie are angular-dependent, so they stay geometric in both modes to preserve
the off-axis profile that the FF modes currently under-resolve. The angular
profile is the physics the FF-mode discrepancy points at, so the STL bow-tie is
used in *both* modes.

## STL processing (`tools/process_bowtie_stl.py`)

Input: `research/Monte Carlo stuff from Inbum/bowtie.stl` (ASCII, 42 MB,
147,880 triangles, bbox X[-0.06,28.49] Y[-31.24,30.42] Z[-70.69,70.13] mm,
centroid X=14.21 mm).

Steps:
1. Parse ASCII STL (stdlib only; no numpy-stl dependency required).
2. Recenter: subtract the bbox centroid so the TsCAD component origin is the
   filter center (corrects the X=14.2 mm export offset).
3. Decimate to ~15-25k triangles (quadric edge collapse). Target is set so
   Geant4 `G4TessellatedSolid` navigation cost is acceptable vs the current 12
   CSG primitives; benchmark with a short transport run and adjust.
4. Write binary STL (50 bytes/header + 50 bytes/triangle -> ~3 MB).
5. Derive half-fan: keep the triangles on one lateral half (Y >= 0 wedge
   stack) and offset to the half-fan `TransX` convention used by the current
   `halffan.txt`. **This is an approximation** -- the TrueBeam half-fan is a
   distinct physical filter, not half of the full-fan. Documented as such; a
   real half-fan STL supersedes it when available.

Outputs: `data/bowtie/fullfan.stl`, `data/bowtie/halffan.stl` (binary), plus an
inspection report (triangle count, bbox, centroid) to `data/bowtie/README.md`.

## TOPAS integration

`TsCAD` (per OpenTOPAS "Specialized Components -> CAD" docs):
```
s:Ge/BowtieFilter/Type       = "TsCAD"
s:Ge/BowtieFilter/Parent     = "CollimatorsHorizontal"
s:Ge/BowtieFilter/Material   = "Aluminum"
s:Ge/BowtieFilter/InputFile  = "fullfan"        # no extension, case-sensitive
s:Ge/BowtieFilter/FileFormat = "stl"
d:Ge/BowtieFilter/Units      = 1.0 mm
d:Ge/BowtieFilter/TransZ     = 38.5 mm          # existing placement
d:Ge/BowtieFilter/RotZ       = -90 deg
d:Ge/BowtieFilter/TransX     = <recenter + fan offset>
```
`TsCAD` resolves `InputFile` relative to CWD, so the STL must be copied into the
runfolder by the mode's `copy_common_files()` alongside the existing include
files. Docs list only **binary** STL as supported -> the ASCII->binary step is
mandatory.

Two new rendered includes replace the static `.txt`:
- `src/boilerplates/TOPAS_includeFiles/bowtie_ff.j2` (full-fan)
- `src/boilerplates/TOPAS_includeFiles/bowtie_hf.j2` (half-fan, TransX offset)

`headsourcecode_boilerplate.j2:5-9` and `ctdi_phsp_score.j2:7-11` dispatch on
`fan_mode` to the new includes. The old `fullfan.txt`/`halffan.txt` are kept as a
documented fallback (config flag `imaging.legacy_bowtie`).

## Spectrum filtration + HVL

`src/spectrum_generator.py`: after `sp.Spek(kvp, th=14, ...)`:
- `hybrid`: `s.filter('Al', 2.7).filter('Al', 0.3)`.
- `geometric`: no filters.
- Always: `hvl_mmAl = s.get_hvl1()`; write to `metadata["spekpy"]["hvl_mmAl"]`
  and append to `head_calibration_factor.txt`.

`imaging.bhf_thickness_mm` (default 0.89) flows into the BHF template
(`headsourcecode_boilerplate.j2:225` HLZ) instead of the literal `0.7 mm`.

## HVL in PhaseSpaceAnalyzer

`analyze()` already builds an energy histogram (fluence per bin). Add an HVL
fold: load NIST mass energy-absorption coefficients for Aluminum
(`data/nist/mu_en_aluminium.dat`, E[MeV] vs mu_en/rho [cm^2/g]); compute air
kerma K0 = sum(Phi(E) * E * mu_en/rho_air(E)); find the Al thickness t such that
sum(Phi(E)*E*mu_en/rho_air(E)*exp(-mu_Al(E)*t)) = K0/2. Store as `hvl_mmAl`.
This reproduces what SpekPy's `get_hvl1` does on the *scored* spectrum, giving a
post-transport validation handle.

## Validation utility (`src/services/bowtie_validator.py`)

- Reads measured profiles from the Oct 2023 workbook "Collated results" via
  `openpyxl` (new dependency): per-position cross-plane dose (uGy, uGy/s) and
  HVL (mmAl) for Head/Spotlight/Img-Gently/Pelvis/Pelvis-Large.
- A new isocenter-plane scorer (thin air slab, 1D cross-plane `DoseToWater`,
  gated by `ctdi.validate_bowtie`) in `ctdi_phsp_score.j2` produces the MC side.
- Emits `bowtie_validation.csv` (per-position MC vs measured dose + HVL) and a
  matplotlib PNG. CLI: `tools/validate_bowtie.py`.

## Risks

- **TsCAD navigation cost** with a decimated ~20k-triangle mesh is the main
  runtime risk. Mitigation: make decimation target a tunable, benchmark, keep
  the legacy CSG fallback.
- **Half-fan derivation** is an approximation; HF modes are already close to
  reference so the bar is "do no harm". Flagged for replacement by a real STL.
- **Ti 0.7 -> 0.89 mm** changes beam hardening; re-run the calibration DCFs
  after the change (the 5 existing `calibration.yaml` entries were generated at
  0.7 mm).
