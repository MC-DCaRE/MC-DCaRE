## Why

The per-protocol effective-dose comparison (`runfolder/effective_dose_comparison.csv`)
shows the **full-fan (FF) CBCT modes are systematically 65-88% low** vs the
PCXMC reference (Head 0.08 vs 0.5, Head SRS 0.28 vs 1.8, Extremity Spotlight
0.06 vs 0.5, Pelvis Spotlight 0.76 vs 2.2). Half-fan body modes are closer
(Thorax 0%, 4D Thorax -3%). The pattern implicates **bow-tie filter fidelity**:

- `fullfan.txt` / `halffan.txt` are hand-fitted Aluminum trapezoid stacks
  ("visuallymatched" comments) with no measurement citation, and the
  `fieldtobladeopening.py` coefficients carry an open `TODO: Cite measurement
  source` (`src/fieldtobladeopening.py:4`).
- `spectrum_generator.py` applies **no SpekPy filtration** (bare spectrum at
  `th=14`); all filtration is geometric. HVL is never computed or recorded.
- A measured-geometry full-fan bow-tie exists as an STL
  (`research/Monte Carlo Stuff from Inbum/bowtie.stl`, 147,880 triangles) and a
  companion `SpekPy-Notebook.ipynb` documents the TrueBeam filtration stack
  (2.7 mm Al inherent + 0.3 mm Al collimator + 0.89 mm Ti BHF + 1.53 mm Al
  full-fan bow-tie) plus an HVL-matching workflow.
- Measured cross-plane HVL/dose profiles for validation exist in
  `research/2023 - CBCT Dose PCXMC/New results Oct 2023 (Spotlight, Raysafe X2).xlsx`
  ("Collated results": Head 7.37 mmAl at CAX rising to 9.98 at +/-14 cm).

The current MC system is accepted as clinically validated for continuity; this
change *improves* fidelity for the FF modes and adds the validation tooling.

## What Changes

1. **STL bow-tie geometry** replaces the CSG trapezoid stack. A processing tool
   converts the ASCII STL to binary, decimates (~148k -> ~20k triangles for
   navigation performance), recenters it, and derives a half-fan STL by cropping
   one lateral half. Loaded in TOPAS via `TsCAD` (`FileFormat="stl"`).
2. **Both filtration pathways** are supported via a config switch
   `imaging.filtration_mode`:
   - `geometric` -- all filtration as geometry (slowest, most physical).
   - `hybrid` (default) -- base filtration (inherent 2.7 mm + collimator 0.3 mm
     Al) in the SpekPy spectrum; Ti BHF + bow-tie remain geometric to preserve
     the angular bow-tie profile.
3. **Ti BHF thickness** becomes configurable (default 0.89 mm per Inbum
   notebook; current hardcoded 0.7 mm).
4. **HVL is computed and recorded**: `s.get_hvl1()` in `spectrum_generator.py`
   (written to metadata + calibration file), and an HVL fold added to
   `PhaseSpaceAnalyzer` so a scored phase space yields an HVL.
5. **Validation utility** compares a scored cross-plane isocenter profile + HVL
   against the measured RaySafe data (openpyxl added as a dependency).

## Capabilities

### New Capabilities
- `bowtie-filter`: the bow-tie as a TOPAS `TsCAD` tessellated-mesh component
  loaded from a processed STL, full-fan and derived half-fan, with the
  filtration-mode switch driving where base filtration lives (geometry vs
  spectrum).

### Modified Capabilities
- `spectrum-generation`: SpekPy spectrum with optional base filtration, recorded
  HVL, configurable BHF thickness.
- `phase-space-analysis`: optional HVL computation by folding the scored energy
  spectrum with NIST mu_en/rho(Aluminum).
