#!/usr/bin/env python3
"""
Fast vectorized tetrahedral-to-voxel conversion for MRCP-AM.
Uses numpy to batch-check voxels per tetrahedron.
"""

from __future__ import annotations

import os
import time
import numpy as np


def read_nodes(filepath: str) -> np.ndarray:
    print(f"Reading nodes from {filepath}...")
    import pandas as pd

    t0 = time.time()
    df = pd.read_csv(
        filepath,
        sep=r"\s+",
        skiprows=1,
        header=None,
        usecols=[1, 2, 3],
        dtype=np.float64,
        comment="#",
    )
    df = df.dropna()
    print(f"  Loaded {len(df)} nodes in {time.time() - t0:.1f}s")
    return df.to_numpy()


def read_elements(filepath: str) -> tuple[np.ndarray, np.ndarray]:
    print(f"Reading elements from {filepath}...")
    import pandas as pd

    t0 = time.time()
    df = pd.read_csv(
        filepath,
        sep=r"\s+",
        skiprows=1,
        header=None,
        usecols=[1, 2, 3, 4, 5],
        dtype=np.float64,
        comment="#",
    )
    df = df.dropna()
    print(f"  Loaded {len(df)} elements in {time.time() - t0:.1f}s")
    return df.iloc[:, :4].to_numpy().astype(np.int32), df.iloc[:, 4].to_numpy().astype(
        np.int32
    )


def read_materials(filepath: str) -> dict[int, str]:
    print(f"Reading materials from {filepath}...")
    materials: dict[int, str] = {}
    current_organ = "Unknown"
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("C "):
                parts = line.split(None, 2)
                if len(parts) >= 2:
                    current_organ = parts[1]
            elif line.startswith("m") and not line.startswith("m g"):
                parts = line.split()
                if parts:
                    try:
                        materials[int(parts[0][1:])] = current_organ
                    except ValueError:
                        pass
    return materials


def voxelize_vectorized(
    nodes: np.ndarray,
    elements: np.ndarray,
    material_ids: np.ndarray,
    voxel_size: float,
) -> tuple[np.ndarray, tuple[int, int, int], np.ndarray]:
    """Vectorized voxelization: batch-check all voxels per tetrahedron."""
    print(f"\nVoxelizing (vectorized) with voxel_size={voxel_size} cm...")

    mins = nodes.min(axis=0)
    maxs = nodes.max(axis=0)
    origin = mins - voxel_size
    extent = maxs - mins + 2 * voxel_size
    grid_shape = tuple(np.ceil(extent / voxel_size).astype(int))

    total_voxels = int(np.prod(grid_shape))
    print(
        f"  Grid: {grid_shape[0]} x {grid_shape[1]} x {grid_shape[2]} = {total_voxels} voxels"
    )
    print(f"  Origin: ({origin[0]:.1f}, {origin[1]:.1f}, {origin[2]:.1f})")

    grid = np.full(grid_shape, -1, dtype=np.int32)

    t0 = time.time()
    n_elems = len(elements)
    report_interval = max(n_elems // 200, 1)

    for i in range(n_elems):
        if i % report_interval == 0:
            elapsed = time.time() - t0
            pct = 100 * i / n_elems
            if i > 0:
                rate = i / elapsed
                eta = (n_elems - i) / rate
                print(
                    f"  {i}/{n_elems} ({pct:.0f}%) - {rate:.0f} tet/s, ETA {eta:.0f}s"
                )
            else:
                print("  Starting...")

        tet = nodes[elements[i]]  # (4, 3)
        mat_id = int(material_ids[i])

        # Bounding box in voxel indices
        bbox_min = tet.min(axis=0)
        bbox_max = tet.max(axis=0)

        ix0 = max(0, int((bbox_min[0] - origin[0]) / voxel_size))
        ix1 = min(grid_shape[0] - 1, int((bbox_max[0] - origin[0]) / voxel_size) + 1)
        iy0 = max(0, int((bbox_min[1] - origin[1]) / voxel_size))
        iy1 = min(grid_shape[1] - 1, int((bbox_max[1] - origin[1]) / voxel_size) + 1)
        iz0 = max(0, int((bbox_min[2] - origin[2]) / voxel_size))
        iz1 = min(grid_shape[2] - 1, int((bbox_max[2] - origin[2]) / voxel_size) + 1)

        # Skip if bounding box is outside grid or tiny
        n_voxels = (ix1 - ix0 + 1) * (iy1 - iy0 + 1) * (iz1 - iz0 + 1)
        if n_voxels == 0:
            continue

        # Generate voxel centers in bounding box
        xs = origin[0] + (np.arange(ix0, ix1 + 1) + 0.5) * voxel_size
        ys = origin[1] + (np.arange(iy0, iy0 + 1) + 0.5) * voxel_size
        zs = origin[2] + (np.arange(iz0, iz1 + 1) + 0.5) * voxel_size

        # Build meshgrid of points
        px, py, pz = np.meshgrid(xs, ys, zs, indexing="ij")
        points = np.stack([px.ravel(), py.ravel(), pz.ravel()], axis=1)  # (N, 3)

        # Compute barycentric coordinates vectorized
        v0, v1, v2, v3 = tet[0], tet[1], tet[2], tet[3]
        mat = np.array([v1 - v0, v2 - v0, v3 - v0]).T  # (3, 3)

        try:
            mat_inv = np.linalg.inv(mat)
        except np.linalg.LinAlgError:
            continue

        delta = points - v0  # (N, 3)
        coords = delta @ mat_inv.T  # (N, 3) barycentric a, b, c
        d = 1.0 - coords[:, 0] - coords[:, 1] - coords[:, 2]

        inside = (
            (coords[:, 0] >= -1e-10)
            & (coords[:, 1] >= -1e-10)
            & (coords[:, 2] >= -1e-10)
            & (d >= -1e-10)
        )

        if not np.any(inside):
            continue

        # Get indices of voxels that are inside
        inside_idx = np.where(inside)[0]
        for idx in inside_idx:
            ix = ix0 + (idx // ((iy1 - iy0 + 1) * (iz1 - iz0 + 1)))
            rem = idx % ((iy1 - iy0 + 1) * (iz1 - iz0 + 1))
            iy = iy0 + (rem // (iz1 - iz0 + 1))
            iz = iz0 + (rem % (iz1 - iz0 + 1))
            if grid[ix, iy, iz] == -1:
                grid[ix, iy, iz] = mat_id

    elapsed = time.time() - t0
    n_filled = np.count_nonzero(grid != -1)
    print(f"\nVoxelization complete in {elapsed:.1f}s")
    print(
        f"  Filled: {n_filled} / {total_voxels} ({100 * n_filled / total_voxels:.1f}%)"
    )
    print(f"  Rate: {n_elems / elapsed:.0f} tet/s")

    return grid, grid_shape, origin


ORGAN_TO_G4 = {
    "Blood": "G4_BLOOD_ICRP",
    "Brain": "G4_BRAIN_ICRP",
    "Heart": "G4_MUSCLE_ICRP",
    "Liver": "G4_LIVER_ICRP",
    "Lung": "G4_LUNG_ICRP",
    "Kidney": "G4_KIDNEY_ICRP",
    "Spleen": "G4_SPLEEN_ICRP",
    "Pancreas": "G4_PANCREAS_ICRP",
    "Stomach": "G4_STOMACH_ICRP",
    "Skin": "G4_SKIN_ICRP",
    "Thyroid": "G4_THYROID_ICRP",
    "Muscle": "G4_MUSCLE_ICRP",
    "Adipose": "G4_ADIPOSE_TISSUE_ICRP",
    "Cartilage": "G4_CARTILAGE_ICRP",
    "Bone": "G4_BONE_COMPACT_ICRU",
    "Bladder": "G4_BLADDER_ICRP",
    "Intestine": "G4_INTESTINE_ICRP",
    "default": "G4_WATER",
}


def organ_to_g4(organ: str) -> str:
    for key, val in ORGAN_TO_G4.items():
        if key.lower() in organ.lower():
            return val
    return ORGAN_TO_G4["default"]


def generate_topas_file(
    grid: np.ndarray,
    grid_shape: tuple[int, int, int],
    origin: np.ndarray,
    voxel_size: float,
    materials: dict[int, str],
    output_file: str,
):
    print(f"\nGenerating TOPAS file: {output_file}")
    nx, ny, nz = grid_shape

    # Build flat material name array
    # TOPAS orders voxels as: x varies fastest, then y, then z
    print("  Building material vector...")
    mat_names = []
    for iz in range(nz):
        for iy in range(ny):
            for ix in range(nx):
                mat_id = int(grid[ix, iy, iz])
                if mat_id == -1:
                    mat_names.append("Air")
                else:
                    organ = materials.get(mat_id, "Unknown")
                    mat_names.append(organ_to_g4(organ))

    total = len(mat_names)
    print(f"  Total voxels: {total}")

    hlx = nx * voxel_size / 2.0
    hly = ny * voxel_size / 2.0
    hlz = nz * voxel_size / 2.0
    cx = origin[0] + nx * voxel_size / 2.0
    cy = origin[1] + ny * voxel_size / 2.0
    cz = origin[2] + nz * voxel_size / 2.0

    with open(output_file, "w") as f:
        f.write("# Voxelized MRCP-AM phantom\n")
        f.write(f"# Voxel size: {voxel_size} cm ({voxel_size * 10} mm)\n")
        f.write(f"# Grid: {nx} x {ny} x {nz} = {total} voxels\n\n")

        f.write('s:Ge/Phantom/Type = "TsBox"\n')
        f.write('s:Ge/Phantom/Parent = "World"\n')
        f.write('s:Ge/Phantom/Material = "G4_WATER"\n')
        f.write(f"d:Ge/Phantom/HLX = {hlx:.2f} cm\n")
        f.write(f"d:Ge/Phantom/HLY = {hly:.2f} cm\n")
        f.write(f"d:Ge/Phantom/HLZ = {hlz:.2f} cm\n")
        f.write(f"d:Ge/Phantom/TransX = {cx:.2f} cm\n")
        f.write(f"d:Ge/Phantom/TransY = {cy:.2f} cm\n")
        f.write(f"d:Ge/Phantom/TransZ = {cz:.2f} cm\n")
        f.write("d:Ge/Phantom/RotX = 0.0 deg\n")
        f.write("d:Ge/Phantom/RotY = 0.0 deg\n")
        f.write("d:Ge/Phantom/RotZ = 0.0 deg\n")
        f.write('s:Ge/Phantom/Color = "yellow"\n\n')

        f.write(f"i:Ge/Phantom/XBins = {nx}\n")
        f.write(f"i:Ge/Phantom/YBins = {ny}\n")
        f.write(f"i:Ge/Phantom/ZBins = {nz}\n")

        f.write(f"sv:Ge/Phantom/VoxelMaterials = {total}")
        for name in mat_names:
            f.write(f' "{name}"')
        f.write("\n\n")

        f.write('s:Sc/PhantomDose/Quantity = "DoseToMedium"\n')
        f.write('s:Sc/PhantomDose/Component = "Phantom"\n')
        f.write('s:Sc/PhantomDose/OutputFile = "phantom_dose"\n')
        f.write('s:Sc/PhantomDose/IfOutputFileAlreadyExists = "Overwrite"\n')

    fsize = os.path.getsize(output_file)
    print(f"  File size: {fsize / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    import sys

    phantom_dir = sys.argv[1] if len(sys.argv) > 1 else "data/P145/Phantom_data/MRCP_AM"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "test_voxel_output/mrcp_am"
    voxel_size = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0

    os.makedirs(output_dir, exist_ok=True)

    nodes = read_nodes(os.path.join(phantom_dir, "MRCP_AM.node"))
    elements, material_ids = read_elements(os.path.join(phantom_dir, "MRCP_AM.ele"))
    materials = read_materials(os.path.join(phantom_dir, "MRCP_AM.material"))

    print(
        f"\nMesh: {len(nodes)} nodes, {len(elements)} tets, {len(materials)} materials"
    )

    grid, grid_shape, origin = voxelize_vectorized(
        nodes, elements, material_ids, voxel_size
    )

    np.save(os.path.join(output_dir, "mrcp_am_voxels.npy"), grid)
    np.save(os.path.join(output_dir, "mrcp_am_origin.npy"), origin)

    generate_topas_file(
        grid,
        grid_shape,
        origin,
        voxel_size,
        materials,
        os.path.join(output_dir, "phantomVoxel.txt"),
    )

    print(f"\nDone! Output in: {output_dir}")
