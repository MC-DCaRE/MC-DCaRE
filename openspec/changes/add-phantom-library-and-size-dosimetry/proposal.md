## Why

MC-DCaRE's phantom mode currently supports only the adult ICRP 145 MRCP-AM/AF,
and via a fragile two-path structure: the rendered `phantomICRP145.j2` uses
`TsTetGeom` (broken -- ~16k unscored hits, empty CSV), so a **post-hoc swap
script** (`scripts/run_full_calibration.py:swap_voxel_phantom`, hardcoded to
`test_voxel_output/mrcp_am`) rewrites the rendered file to a voxelized `TsBox`
form. This blocks two clinical needs:

1. **Paediatric CBCT dosimetry.** Four protocols (Image Gently, Pediatric
   Head/Body) have blank effective-dose references because PCXMC was never run
   for them. ICRP Publication 156 (2024) now publishes the paediatric
   mesh-type reference computational phantoms (MRCPs) for ages 0, 1, 5, 10, 15 y
   x M/F (Yeom et al. 2026, doi 10.1177/01466453251411690; source:
   https://www.icrp.org/publication.asp?id=ICRP%20Publication%20156 ). These
   ship in tetrahedral mesh and can be voxelized at 5 mm by the existing
   `tools/voxelize_phantom.py`.
2. **Size-based dosimetry.** A single reference-phantom effective dose hides the
   2-3x spread across patient size (Martin 2022; Abuhaimed 2023). The ICRP MRCP
   deformability produced a 212-adult body-size library (Choi 2020) and a
   637-paediatric library (Kim 2024). A representative subset
   (10th/50th/90th percentile per age/sex) lets MC-DCaRE report E(height,weight)
   instead of a single nominal value plus an ad-hoc correction factor.

The voxelization tool already works for any TetGen `.node/.ele/.material` mesh;
the work is the architecture (config-driven voxel path, one voxelizer entry
point) and the data (download ICRP 156, voxelize, assemble the library).

## What Changes

1. **Unified voxel phantom path.** A new `phantomVoxel.j2` renders the
   `TsBox` + `VoxelMaterials` form directly; `headsourcecode_boilerplate.j2`
   routes ICRP145 to it. The broken `TsTetGeom` template is deprecated and the
   post-hoc swap script removed.
2. **Phantom library config.** `PhantomConfig` gains `phantom_age`,
   `phantom_voxel_directory`, `phantom_voxel_size_mm`, and
   `phantom_size_percentile`. `phantom_name` resolves from age+sex+percentile
   (e.g. `MRCP_AM`, `MRCP_AM_10y_p90`).
3. **One voxelization entry point.** `tools/voxelize_phantom.py` becomes the
   sole voxelizer, emitting `.npy` (for `PhantomDoseCalculator`), the
   `phantomVoxel.txt` + `icrp_materials.txt` includes (for the template), and
   `material_map.txt`. The MRCP-AM-hardcoded helper scripts are generalized.
4. **ICRP 156 paediatric data.** Download the 10 paediatric MRCPs from the
   ICRP 156 electronic supplement; voxelize each at 5 mm into
   `data/P145/voxelized/MRCP_{sex}_{age}_5mm/`.
5. **Size-based dosimetry.** Integrate a 10th/50th/90th-percentile subset per
   age/sex (from the Choi 2020 / Kim 2024 libraries once obtained) and produce
   an E(height,weight) reporting path. `calibration.yaml`
   `effective_dose_references` is restructured to allow per-phantom entries.
6. **PhantomDoseCalculator** resolves voxel-grid + material-file from
   `phantom_name` rather than hardcoded `mrcp_am`.

## Capabilities

### New Capabilities
- `phantom-library`: an age/sex/size-keyed library of voxelized ICRP mesh
  phantoms loaded via a config-driven voxel path, replacing the hardcoded
  single-adult-male post-hoc swap.
- `size-specific-dose`: per-protocol effective dose reported as a function of
  patient height/weight via a percentile phantom subset.

### Modified Capabilities
- `reference-phantom-geometry`: voxelized loading (`TsBox` + `VoxelMaterials`)
  supersedes the broken `TsTetGeom` path; age/sex/size selection.
- `phantom-simulation-mode`: emits voxel context (dims, bins, materials include,
  origin) and scales the couch offset by phantom size.
