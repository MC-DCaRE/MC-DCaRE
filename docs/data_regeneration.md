# Regenerating the `data/` Directory (Fresh Clone)

Everything under `data/` is gitignored (large reference datasets and ICRP mesh
files). A fresh clone has an empty `data/` and several features will silently
no-op until it is populated. This document is the canonical procedure; the
automation lives in `tools/setup_data.py`.

## What lives in `data/` and who needs it

| Asset | Path | Needed by | Source |
|---|---|---|---|
| NIST HVL coefficients | `data/nist/hvl_coefficients.dat` | `PhaseSpaceAnalyzer.compute_hvl_mm_al` (bow-tie/spectrum HVL) | NIST XCOM (embedded in `setup_data.py nist`) |
| Adult mesh (ICRP 145) | `data/P145/Phantom_data/MRCP_{AM,AF}/` | Phantom mode (adult) | ICRP 145 electronic supplement |
| Paediatric mesh (ICRP 156) | `data/P145/Phantom_data/MRCP_{sex}_{age}/` | Phantom mode (paediatric) | ICRP 156 electronic supplement (~12 GB) |
| Voxelized phantoms | `data/P145/voxelized/<name>_<N>mm/` | Phantom mode (runtime) | `tools/voxelize_phantom.py` from the mesh |
| MC code examples | `data/P145/MC_examples/` | Reference / material files | ICRP distribution |

The processed bow-tie STLs (`fullfan.stl`, `halffan.stl`) live in
`src/boilerplates/TOPAS_includeFiles/` (tracked), regenerated from the tracked
source `research/Monte Carlo Stuff from Inbum/bowtie.stl` by
`tools/process_bowtie_stl.py`.

## Quick start

```bash
# 1. Self-contained: NIST table + bow-tie STLs + voxelize any staged meshes.
uv run python tools/setup_data.py all
```

Then complete the ICRP mesh downloads (license-gated, manual) and re-run the
voxelizer:

```bash
uv run python tools/setup_data.py phantom-mesh     # prints the exact URLs + steps
# ...download + unzip into data/P145/Phantom_data/...
uv run python tools/setup_data.py phantom-voxel    # voxelize all staged meshes
```

## Step-by-step

### 1. NIST HVL coefficient table (automated, self-contained)

```bash
uv run python tools/setup_data.py nist
```

Writes `data/nist/hvl_coefficients.dat` (NIST XCOM mass attenuation/
energy-absorption coefficients for air and Aluminum, 10-150 keV). Values are
public NIST reference data embedded in the script; verify against
<https://physics.nist.gov/PhysRefData/Xcom> before production use. Without this
file, `PhaseSpaceAnalyzer` returns `hvl_mmAl: null`.

### 2. Bow-tie STLs (automated)

```bash
uv run python tools/setup_data.py bowtie
```

Runs `tools/process_bowtie_stl.py` on `research/Monte Carlo Stuff from
Inbum/bowtie.stl`, producing `fullfan.stl` + a derived `halffan.stl` in
`src/boilerplates/TOPAS_includeFiles/`. Requires the
`develop-bowtie-spectrum-validation` branch (or its merge) for the processing
tool.

### 3. ICRP phantom meshes (manual download, license-gated)

```bash
uv run python tools/setup_data.py phantom-mesh
```

Prints the two download URLs and the staging convention:

- **Adult (ICRP 145):** `P145 Electronic files.zip` from the SAGE supplement.
- **Paediatric (ICRP 156):** `P156 Electronic files.zip` (~12 GB) from
  <https://www.icrp.org/docs/P156%20Electronic%20files.zip>.

Unzip into `data/P145/Phantom_data/` with directory names matching
`PhantomConfig.resolve_phantom_name()`:

```
data/P145/Phantom_data/
  MRCP_AM/   MRCP_AF/                 # adult (ICRP 145)
  MRCP_AM_0y/ MRCP_AF_0y/             # newborn (ICRP 156)
  ... MRCP_AM_15y/ MRCP_AF_15y/       # 15-year-old
```

Each directory must contain TetGen `<name>.node`, `<name>.ele`, `<name>.material`.
If the supplement ships only `.obj` polygon meshes, retetrahedralize:
`tetgen -pAY <name>.poly` (then carry over the `.material` file).

ICRP distributes phantom electronic files free for non-commercial research use.
Record provenance (download date, version, any TetGen conversion) in a local
`data/P145/README.md` (gitignored, not tracked).

### 4. Voxelize the meshes (automated)

```bash
uv run python tools/setup_data.py phantom-voxel                # default 5 mm
uv run python tools/setup_data.py phantom-voxel --voxel-size-cm 0.25  # 2.5 mm
```

Discovers every `MRCP_*/` directory under `data/P145/Phantom_data/` that has a
matching `.node` file and runs `tools/voxelize_phantom.py`, writing the full
output contract to `data/P145/voxelized/<name>_<N>mm/`:

- `phantom.npy` — material-ID grid consumed by `PhantomDoseCalculator`.
- `phantomVoxel.txt` + `icrp_materials.txt` — the TOPAS voxel-phantom include
  (consumed by the head template when `phantom.use_voxel_phantom=True`).
- `material_map.txt`, `phantom.bin`, `phantom.imagecube`, `material_ids.bin`.

For the smallest paediatric phantoms (0y, 1y) use a finer voxel size
(2-3 mm) to resolve small organs.

## Verification

```bash
# NIST table present and HVL computes (should print a finite HVL).
uv run python -c "
from src.services.phase_space_analyzer import PhaseSpaceAnalyzer
print('HVL:', PhaseSpaceAnalyzer.compute_hvl_mm_al([59.,60.,61.], [0.,1000.], 'data/nist/hvl_coefficients.dat'))
"

# Bow-tie STLs present.
ls -la src/boilerplates/TOPAS_includeFiles/{fullfan,halffan}.stl

# A voxelized phantom is loadable.
uv run python -c "import numpy as np; print('grid:', np.load('data/P145/voxelized/MRCP_AM_5mm/phantom.npy').shape)"
```

## Fresh-clone checklist

```
[ ] uv run python tools/setup_data.py nist
[ ] uv run python tools/setup_data.py bowtie          # needs bowtie branch merged
[ ] uv run python tools/setup_data.py phantom-mesh    # follow printed download steps
[ ] (download + unzip ICRP 145 + 156 into data/P145/Phantom_data/)
[ ] uv run python tools/setup_data.py phantom-voxel
[ ] run the verification commands above
```

## Reproducibility notes

- `data/` is gitignored by design (the ICRP meshes alone are tens of GB). The
  contents are fully reproducible from this procedure + the cited ICRP sources.
- The NIST table and bow-tie STLs are deterministic (same inputs -> same outputs).
- Voxelization is deterministic for a fixed `--voxel-size` and mesh version.
