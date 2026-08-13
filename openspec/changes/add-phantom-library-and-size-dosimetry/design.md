# Design -- add-phantom-library-and-size-dosimetry

## The two-path problem (current)

```
rendered phantomICRP145.j2  --[TsTetGeom, BROKEN]--> empty CSV
        |
        | (post-hoc, hardcoded to test_voxel_output/mrcp_am)
        v
scripts/run_full_calibration.py:swap_voxel_phantom
  content.replace("phantomICRP145.txt", "phantomVoxel.txt")
        |
        v
phantomVoxel.txt (TsBox + VoxelMaterials vector)  --> WORKS
```

Two divergent codepaths, no config bridge, locked to adult male. Target state:

```
PhantomConfig(age, sex, percentile) -> phantom_name -> voxel dir
        |
        v
phantomVoxel.j2 renders TsBox + VoxelMaterials directly  --> WORKS
```

## Voxelized phantom loading contract

A voxelized phantom directory `data/P145/voxelized/<name>_5mm/` contains:
- `phantom.npy` -- int32 material-ID grid, shape (nx, ny, nz), C-order, the
  format `PhantomDoseCalculator.grid` loads via `np.load`.
- `phantomVoxel.txt` -- rendered-capable TOPAS include: `TsBox` with `XBins`/
  `YBins`/`ZBins` and the `sv:Ge/Phantom/VoxelMaterials` vector.
- `icrp_materials.txt` -- material definitions (`ICRP_<id>` element fractions +
  density) consumed by `phantomVoxel.txt`.
- `material_map.txt` -- `MaterialID  OrganName  Density  HU` for post-processing.
- `phantom.imagecube` + `phantom.bin` -- optional TsImageCube form (retained).

`phantomVoxel.j2` is parameterized: it reads the box dims, bin counts, and the
materials-include basename from context and emits the `TsBox` + `VoxelMaterials`
reference. The `VoxelMaterials` vector is large (hundreds of thousands of
entries); it is written to its own include file `<name>_voxelmaterials.txt` and
referenced, not inlined.

## Config resolution

`PhantomConfig` new fields:
- `phantom_age`: "adult" (default) | "15y" | "10y" | "5y" | "1y" | "0y"
- `phantom_sex`: "AM" | "AF"
- `phantom_size_percentile`: 50 (default) | 10 | 90  (size-based library)
- `phantom_voxel_size_mm`: 5.0 (default)
- `phantom_voxel_directory`: `data/P145/voxelized` (default)

`phantom_name` resolves as:
- adult, p50: `MRCP_{sex}`
- paediatric, p50: `MRCP_{sex}_{age}`
- any percentile != 50: `MRCP_{sex}_{age}_p{percentile}`

The voxel directory path is `{voxel_directory}/{phantom_name}_{voxel_size_mm}mm`.

`phantom_mode.py:build_sub_context` emits: `phantom_name`, voxel dir, box
dims/bins, materials-include basename, origin, and a **size-scaled** couch
posterior offset (replacing the hardcoded `14.0 cm` at `phantom_mode.py:69` --
scaled by the phantom torso depth relative to the adult reference).

## One voxelizer

`tools/voxelize_phantom.py` is extended to emit all four outputs above (`.npy`
added; `phantomVoxel.txt` + `icrp_materials.txt` generation moved here from
`scripts/regenerate_voxel_phantom.py`). `--name`/`--input`/`--output` already
parameterize it. The `density_to_hu` linear approximation is retained but the
`material_map.txt` records both density and the organ name so the
post-processor uses material IDs, not HU, for organ assignment (the working path
already does this).

`scripts/regenerate_voxel_phantom.py` and `scripts/voxelize_mrcp_am_fast.py`
become thin wrappers or are removed; `swap_voxel_phantom` is removed.

## ICRP 156 paediatric data

Source: https://www.icrp.org/publication.asp?id=ICRP%20Publication%20156
(electronic supplement, tetrahedral mesh). 10 phantoms: 0/1/5/10/15 y x M/F.
Expected format: `.node`/`.ele`/`.material` (matching ICRP 145 conventions per
Yeom 2026); if only `.obj` ships, a `tetgen -pA` retetrahedralization step is
needed (`tetgen` availability checked at data-ingest time).

Ingest (manual + scripted):
1. Download + unzip the supplement into `data/P145/Phantom_data/MRCP_{sex}_{age}/`.
2. Run `tools/voxelize_phantom.py --name MRCP_{sex}_{age} --voxel-size 0.5` per
   phantom -> `data/P145/voxelized/MRCP_{sex}_{age}_5mm/`.
3. Verify each with `calculate_phantom_dose.py --voxel-grid ... --material-file ...`
   on a short run.

`data/` is gitignored; a `data/P145/README.md` documents the ingest procedure
and provenance so the library is reproducible.

## Size-based dosimetry

The Choi 2020 (212 adult) and Kim 2024 (637 paediatric) libraries deform the
MRCPs across the height/weight distribution. Running the full library is
impractical for per-protocol CBCT MC; instead MC-DCaRE uses a **percentile
subset** (10th/50th/90th per age/sex = up to 30 phantoms for the full age x sex
grid, fewer for a single protocol). Each protocol run produces E at three
percentiles; the reporting layer fits these to the patient's height/weight and
returns a size-specific E.

`calibration.yaml.effective_dose_references` is restructured from a flat
protocol->mSv map to:
```yaml
effective_dose_references:
  Pelvis:
    reference: 4.2          # 50th percentile adult, existing value
    units: mSv
    phantom: MRCP_AM
```
so a validation comparison knows which phantom produced each reference. Size
library entries are added as obtained.

## Risks

- **TsTetGeom could be fixed instead** (Yeom 2026 stresses tetrahedral mesh goes
  directly into Geant4 without voxelization, preserving micron-scale targets).
  Out of scope here -- voxelization is the working path; a future change can
  revisit direct mesh loading if `TsTetGeom` is repaired upstream.
- **ICRP 156 data accessibility**: the supplement must be downloadable; format
  (tet vs obj) determines whether a `tetgen` step is needed. Flagged as a
  data-ingest task, not a code risk.
- **5 mm voxels under-resolve small paediatric organs** (testes, thyroid). The
  voxel size is configurable; 2-3 mm may be needed for the smallest phantoms.
  Documented trade-off.
- **Size-library availability**: the percentile subsets are not in-repo; this
  change builds the *machinery* and the adult-female baseline, with paediatric +
  percentile data slotted in as sourced.
