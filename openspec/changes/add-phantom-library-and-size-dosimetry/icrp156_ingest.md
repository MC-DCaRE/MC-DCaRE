# ICRP 156 Paediatric Phantom Ingest

Procedures to obtain, stage, and voxelize the ICRP Publication 156 paediatric
mesh-type reference computational phantoms (MRCPs) for use in MC-DCaRE. These
phantoms cover ages 0, 1, 5, 10, 15 years x male/female (10 phantoms) and
supersede the adult-only ICRP 145 set for paediatric CBCT dosimetry.

**Source:** ICRP Publication 156 (2024), electronic supplement.
<https://www.icrp.org/publication.asp?id=ICRP%20Publication%20156>

Reference: Yeom Y.S., Kim C.H., Choi C., Shin B., Kim S., Kim H. (2026).
*Mesh-type reference computational phantoms (MRCPs) for the next general
recommendations.* Ann. ICRP. doi:10.1177/01466453251411690

## 1. Obtain the mesh data

1. Download the ICRP 156 electronic supplement (zipped mesh files) from the
   publication page above. ICRP distributes phantom electronic files free for
   non-commercial research use.
2. Confirm the format. ICRP 145 shipped both polygon mesh (`.obj`/`.mtl`) and
   tetrahedral mesh (`.node`/`.ele`/`.material`); the paediatric set is expected
   to follow the same convention.
   - **TetGen `.node/.ele/.material` present:** proceed to step 3.
   - **Only `.obj`/`.mtl` present:** retetrahedralize with TetGen (see below).

## 2. Stage into the mesh data directory

For each phantom (sex x age), create a directory under `data/P145/Phantom_data/`
matching the naming convention used by `PhantomConfig.resolve_phantom_name()`:

```
data/P145/Phantom_data/
  MRCP_AM/          # existing adult male (ICRP 145)
  MRCP_AF/          # existing adult female (ICRP 145)
  MRCP_AM_0y/       # newborn male
  MRCP_AF_0y/
  MRCP_AM_1y/
  MRCP_AF_1y/
  MRCP_AM_5y/
  MRCP_AF_5y/
  MRCP_AM_10y/
  MRCP_AF_10y/
  MRCP_AM_15y/
  MRCP_AF_15y/
```

Each directory must contain `<name>.node`, `<name>.ele`, `<name>.material`
(+ `_media.dat` if shipped). The `.material` file uses the ICRP block syntax
(`C <OrganName> <density> g/cm3` / `m<id> <Z*1000> <-fraction>`) that
`tools/voxelize_phantom.py` parses.

### TetGen conversion (only if `.obj`-only)

```bash
# Build a .poly/.smesh from the OBJ, then tetrahedralize with material labels.
tetgen -pAY <name>.poly    # produces <name>.1.node / <name>.1.ele
```
`tetgen` availability must be confirmed on the host (`which tetgen`). The
`.material` file must be carried over or regenerated from `_media.dat`.

## 3. Voxelize at 5 mm

Run the voxelizer per phantom (output contract: `phantom.npy`,
`phantomVoxel.txt`, `icrp_materials.txt`, `material_map.txt`):

```bash
for name in MRCP_AM_0y MRCP_AF_0y MRCP_AM_1y ... MRCP_AF_15y; do
  uv run python tools/voxelize_phantom.py \
    --input  data/P145/Phantom_data/$name \
    --output data/P145/voxelized/${name}_5mm \
    --name   $name \
    --voxel-size 0.5
done
```

`data/P145/voxelized/` follows `{phantom_name}_{voxel_size_mm}mm` so
`PhantomConfig.resolve_voxel_directory()` resolves automatically. `data/` is
gitignored (large files); the directory is reproducible from this procedure.

Note: the smallest phantoms (0y, 1y) may need a finer voxel size (2-3 mm) to
resolve small organs (testes, thyroid); set `phantom_voxel_size_mm` accordingly.

## 4. Smoke test each phantom

```bash
uv run python calculate_phantom_dose.py \
  --voxel-grid      data/P145/voxelized/MRCP_AF_5y_5mm/phantom.npy \
  --material-file   data/P145/Phantom_data/MRCP_AF_5y/MRCP_AF_5y.material \
  --scorer-type tle \
  ... protocol args ...
```

Confirm non-zero organ dose for high-weight organs (bone marrow, colon, bladder).

## 5. Provenance

Record in `data/P145/README.md` (local, gitignored): download date, ICRP 156
version, whether TetGen conversion was needed, and the voxelization command per
phantom. This keeps the library reproducible across machines.

## Related

- Adult baseline: `data/P145/Phantom_data/MRCP_AM`, `MRCP_AF` (ICRP 145).
- Size-percentile libraries (Choi 2020 adult; Kim 2024 paediatric) follow the
  same ingest path with `phantom_size_percentile` in (10, 90); names resolve to
  `MRCP_{sex}_{age}_p{percentile}`.
