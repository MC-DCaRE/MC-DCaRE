# research/

Local research collection underpinning MC-DCaRE's CBCT dosimetry work. Two curated datasets: a PCXMC-based dose study (2023) and a multi-site clinical CBCT mode standardisation (2023).

## What lives here

| Folder | Purpose | Size | Key artifact |
|---|---|---|---|
| `2023 - CBCT Dose PCXMC/` | PCXMC cone-beam CT dose study: MATLAB/Python driver code, STUK PCXMC 2.0 install + docs, measured air-kerma data, PCXMC effective-dose results, literature | ~119 MB | `TrueBeamCBCTmodes.xlsx` (final E values) |
| `2023 - CBCT Mode Standardisation/` | Clinical CBCT-mode parameter standardisation across 5 linacs (CST, OBK, PL LA3/LA4/LA5): screenshots + the master modes/dose table | ~36 MB | `TrueBeamCBCTmodes.xlsx` (mode params + CTDI + E) |

See each subfolder's `AGENTS.md` for detailed file inventories.

## Relationship to MC-DCaRE

This research is the **historical baseline** MC-DCaRE replaces and improves upon:

- The PCXMC workflow (Aaron Fetin / Terry, NSW Health c.2020-2023) computed CBCT effective dose by feeding measured air kerma + sub-field geometry into the proprietary STUK PCXMC 2.0 kernel-superposition code. It produced the per-mode effective doses (Pelvis 4.2, Thorax 1.3, Head 0.5 mSv, etc.) that MC-DCaRE now stores in `calibration.yaml` as `effective_dose_references`.
- MC-DCaRE supersedes this with explicit Geant4/TOPAS Monte Carlo transport, fluence-based TLE + collision DTM scorers, CTDI-derived DCF calibration, and voxelized/mesh phantoms — no proprietary kernels, no mathematical-phantom assumption.
- The clinical mode table here (`TrueBeamCBCTmodes.xlsx`) is the source of truth for the 47 Varian TrueBeam kV imaging presets encoded in `src/models/imaging_mode.py`.

For the full physics/systems/gap comparison between this research and the current codebase, see `COMPARATIVE_ANALYSIS.md`.

## Critical caveat

The PCXMC driver code in `2023 - CBCT Dose PCXMC/PCXMCStuff/PCXMC_Code/` and `.../pcxmc_py_refactor/` **does not compute dose**. It generates a 20-column input matrix (`PCXMCInput`) that a user manually pastes into PCXMC's Excel front-end (`AutocalcRotation-sheet.xls`). The organ-dose kernel multiplication happens inside PCXMC 2.0, not in any committed source file. The Python refactor (`pcxmc_py_refactor/`) only reimplemented the geometry layer (and with two bugs: wrong sub-field boundary offset in the runner, wrong `wrap_to_360` range). Do not treat the Python/MATLAB code as a reusable dose engine.
