## Why

The TsCAD mesh bow-tie (Inbum measured STL, `research/Monte Carlo Stuff from
Inbum/bowtie.stl`) is fully integrated and runs cleanly at the validated
`Rotation` @ 18 cm placement (0 overlaps, symmetric Top/Bottom). But
end-to-end dosimetry shows it **over-attenuates**:

- Pelvis effective dose (125 kV HF, MRCP_AM voxel phantom):
  - new TsCAD bow-tie: **3.37 mSv** (geometric) / **3.13 mSv** (hybrid)
  - old CSG bow-tie system: **~5.5 mSv**
  - PCXMC reference: 4.2 mSv
  - Independent literature: Hauri 2017 (TLD) **5.4 mSv**, Abuhaimed 2018
    (BEAMnrc) **~6 mSv**

So the "real measured" STL lands ~40% below the TLD/MC literature, while the
hand-fitted CSG approximation it was meant to replace was actually closer.
Hybrid vs geometric filtration is a minor (~7%) effect -- the bow-tie asset
itself is the dominant driver. The CTDI DCF self-calibrates on the PMMA
cylinder, but the CTDI->phantom transfer does not compensate because the new
bow-tie shapes the beam profile differently.

The code is correct and complete; this is a **physics-data quality question
about the STL asset** that must be resolved before the TsCAD bow-tie is adopted
as the default (`legacy_bowtie=False`).

## What Changes

1. **Validate the STL against measurement.** Score the cross-plane air-kerma
   profile + HVL at isocenter (the `validate_bowtie` scorer + the RaySafe
   Oct-2023 data in `research/2023 - CBCT Dose PCXMC/New results Oct 2023
   (...).xlsx`) and compare TsCAD vs measured vs legacy CSG. This is the
   decisive test of whether the STL is the correct filter.
2. **Decision tree** on the outcome:
   - If the STL profile/HVL matches measurement -> the STL is correct; the low
     effective dose is physical (and the PCXMC/literature values are the
     off-by-~30% ones). Adopt the STL.
   - If it does NOT match -> diagnose: wrong filter asset, source-to-bowtie
     distance (18 cm), material assumption (G4_Al vs real alloy/hollow), or the
     STL including mounting hardware. Either source the correct STL, fix the
     placement/material, or retain the CSG bow-tie as default.
3. **Document the qualified bow-tie** and, once validated, re-run the full DCF
   calibration suite at the chosen bow-tie + filtration mode and flip
   `legacy_bowtie` accordingly.

## Capabilities

### Modified Capabilities
- `bowtie-filter`: the TsCAD mesh bow-tie must be qualified against measured
  cross-plane profile + HVL before it is enabled as the default; the legacy CSG
  bow-tie remains the default until qualified.
