#!/usr/bin/env python3
"""
Optimized tetrahedral-to-voxel conversion for MRCP-AM phantom.
Iterates over tetrahedra (rasterization approach) instead of voxels.
Generates TOPAS parameter file with VoxelMaterials.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
import numpy as np


def read_nodes(filepath: str) -> np.ndarray:
    """Read TETGEN node file. Returns (N, 3) array of xyz coordinates."""
    print(f"Reading nodes from {filepath}...")
    data = np.loadtxt(filepath, skiprows=1)
    return data[:, 1:4].astype(np.float64)


def read_elements(filepath: str) -> tuple[np.ndarray, np.ndarray]:
    """Read TETGEN element file. Returns (node indices, material IDs)."""
    print(f"Reading elements from {filepath}...")
    data = np.loadtxt(filepath, skiprows=1)
    indices = data[:, 1:5].astype(np.int32)
    materials = data[:, 5].astype(np.int32)
    return indices, materials


def read_materials(filepath: str) -> dict[int, str]:
    """Read material file. Returns dict mapping material ID to organ name."""
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
                if len(parts) >= 1:
                    mat_id_str = parts[0][1:]
                    try:
                        mat_id = int(mat_id_str)
                        materials[mat_id] = current_organ
                    except ValueError:
                        pass
    return materials


def voxelize_mesh(
    nodes: np.ndarray,
    elements: np.ndarray,
    material_ids: np.ndarray,
    voxel_size: float,
) -> tuple[np.ndarray, tuple[int, int, int], tuple[np.ndarray, np.ndarray]]:
    """Voxelize tetrahedral mesh using rasterization approach.

    Iterates over each tetrahedron, finds overlapping voxels, and assigns material.
    Returns (3D material array, grid_shape, (origin, voxel_size)).
    """
    print(f"\nVoxelizing with voxel_size={voxel_size} cm...")

    # Compute grid bounds from node coordinates
    mins = nodes.min(axis=0)
    maxs = nodes.max(axis=0)
    origin = mins - voxel_size  # 1 voxel padding
    extent = maxs - mins + 2 * voxel_size

    grid_shape = tuple(np.ceil(extent / voxel_size).astype(int))
    print(f"  Grid: {grid_shape[0]} x {grid_shape[1]} x {grid_shape[2]} = {np.prod(grid_shape)} voxels")
    print(f"  Origin: ({origin[0]:.1f}, {origin[1]:.1f}, {origin[2]:.1f})")

    # Initialize grid with -1 (air/empty)
    grid = np.full(grid_shape, -1, dtype=np.int32)

    t0 = time.time()
    n_elems = len(elements)
    report_interval = max(n_elems // 100, 1)

    for i in range(n_elems):
        if i % report_interval == 0:
            elapsed = time.time() - t0
            if i > 0:
                rate = i / elapsed
                eta = (n_elems - i) / rate
                print(f"  {i}/{n_elems} ({100*i/n_elems:.0f}%) - {rate:.0f} tet/s, ETA {eta:.0f}s")
            else:
                print(f"  {i}/{n_elems} (0%)")

        # Get tetrahedron vertices
        tet_nodes = nodes[elements[i]]  # (4, 3)

        # Compute bounding box in voxel indices
        bbox_min = tet_nodes.min(axis=0)
        bbox_max = tet_nodes.max(axis=0)

        ix_min = max(0, int((bbox_min[0] - origin[0]) / voxel_size))
        ix_max = min(grid_shape[0] - 1, int((bbox_max[0] - origin[0]) / voxel_size) + 1)
        iy_min = max(0, int((bbox_min[1] - origin[1]) / voxel_size))
        iy_max = min(grid_shape[1] - 1, int((bbox_max[1] - origin[1]) / voxel_size) + 1)
        iz_min = max(0, int((bbox_min[2] - origin[2]) / voxel_size))
        iz_max = min(grid_shape[2] - 1, int((bbox_max[2] - origin[2]) / voxel_size) + 1)

        if ix_min > ix_max or iy_min > iy_max or iz_min > iz_max:
            continue

        # Get material for this tetrahedron
        mat_id = int(material_ids[i])

        # Tetrahedron vertices for barycentric coordinate computation
        v0 = tet_nodes[0]
        v1 = tet_nodes[1]
        v2 = tet_nodes[2]
        v3 = tet_nodes[3]

        # Precompute matrix for barycentric coordinates
        # Solve: point = v0 + a*(v1-v0) + b*(v2-v0) + c*(v3-v0)
        mat = np.array([
            v1 - v0,
            v2 - v0,
            v3 - v0,
        ]).T  # (3, 3)

        try:
            mat_inv = np.linalg.inv(mat)
        except np.linalg.LinAlgError:
            continue

        # Check each voxel center in the bounding box
        for ix in range(ix_min, ix_max + 1):
            for iy in range(iy_min, iy_max + 1):
                for iz in range(iz_min, iz_max + 1):
                    # Skip if already assigned
                    if grid[ix, iy, iz] != -1:
                        continue

                    # Voxel center in world coordinates
                    px = origin[0] + (ix + 0.5) * voxel_size
                    py = origin[1] + (iy + 0.5) * voxel_size
                    pz = origin[2] + (iz + 0.5) * voxel_size
                    point = np.array([px, py, pz])

                    # Compute barycentric coordinates
                    delta = point - v0
                    coords = mat_inv @ delta
                    a, b, c = coords[0], coords[1], coords[2]
                    d = 1.0 - a - b - c

                    # Check if inside tetrahedron
                    if a >= -1e-10 and b >= -1e-10 and c >= -1e-10 and d >= -1e-10:
                        grid[ix, iy, iz] = mat_id

    elapsed = time.time() - t0
    n_filled = np.count_nonzero(grid != -1)
    print(f"\nVoxelization complete in {elapsed:.1f}s")
    print(f"  Filled voxels: {n_filled} / {np.prod(grid_shape)} ({100*n_filled/np.prod(grid_shape):.1f}%)")
    print(f"  Rate: {n_elems/elapsed:.0f} tet/s")

    return grid, grid_shape, (origin, np.array([voxel_size]))


# ICRP organ -> Geant4 material mapping
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
    """Map organ name to Geant4 material."""
    for key, val in ORGAN_TO_G4.items():
        if key.lower() in organ.lower():
            return val
    return ORGAN_TO_G4["default"]


def generate_topas_voxel_file(
    grid: np.ndarray,
    grid_shape: tuple[int, int, int],
    origin: np.ndarray,
    voxel_size: float,
    materials: dict[int, str],
    output_file: str,
):
    """Generate TOPAS parameter file with VoxelMaterials."""
    print(f"\nGenerating TOPAS voxel file: {output_file}")

    nx, ny, nz = grid_shape

    # Build VoxelMaterials vector
    # Order: x varies fastest, then y, then z (matching TOPAS convention)
    print("  Building material vector...")
    mat_names: list[str] = []
    for iz in range(nz):
        for iy in range(ny):
            for ix in range(nx):
                mat_id = grid[ix, iy, iz]
                if mat_id == -1:
                    mat_names.append("Air")
                else:
                    organ = materials.get(mat_id, "Unknown")
                    mat_names.append(organ_to_g4(organ))

    total = len(mat_names)
    print(f"  Total voxels: {total}")

    # Write TOPAS include file
    hlx = nx * voxel_size / 2.0
    hly = ny * voxel_size / 2.0
    hlz = nz * voxel_size / 2.0
    cx = origin[0] + nx * voxel_size / 2.0
    cy = origin[1] + ny * voxel_size / 2.0
    cz = origin[2] + nz * voxel_size / 2.0

    with open(output_file, "w") as f:
        f.write("# Voxelized MRCP-AM phantom\n")
        f.write(f"# Voxel size: {voxel_size} cm\n")
        f.write(f"# Grid: {nx} x {ny} x {nz}\n\n")

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

        # Voxel divisions and materials
        f.write(f"i:Ge/Phantom/XBins = {nx}\n")
        f.write(f"i:Ge/Phantom/YBins = {ny}\n")
        f.write(f"i:Ge/Phantom/ZBins = {nz}\n")

        # Write VoxelMaterials as a single long vector
        f.write(f"sv:Ge/Phantom/VoxelMaterials = {total}")
        for name in mat_names:
            f.write(f' "{name}"')
        f.write("\n\n")

        # Dose scorer
        f.write('s:Sc/PhantomDose/Quantity = "DoseToMedium"\n')
        f.write('s:Sc/PhantomDose/Component = "Phantom"\n')
        f.write('s:Sc/PhantomDose/OutputFile = "phantom_dose"\n')
        f.write('s:Sc/PhantomDose/IfOutputFileAlreadyExists = "Overwrite"\n')

    fsize = os.path.getsize(output_file)
    print(f"  File size: {fsize / 1024 / 1024:.1f} MB")


def main():
    parser = argparse.ArgumentParser(description="Voxelize MRCP-AM phantom for TOPAS")
    parser.add_argument("phantom_dir", help="Directory with MRCP_AM .node/.ele/.material")
    parser.add_argument("output_dir", help="Output directory")
    parser.add_argument("--voxel-size", type=float, default=2.0,
                        help="Voxel size in cm (default: 2.0)")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    # Read mesh data
    nodes = read_nodes(os.path.join(args.phantom_dir, "MRCP_AM.node"))
    elements, material_ids = read_elements(os.path.join(args.phantom_dir, "MRCP_AM.ele"))
    materials = read_materials(os.path.join(args.phantom_dir, "MRCP_AM.material"))

    print(f"\nMesh summary:")
    print(f"  Nodes: {len(nodes)}")
    print(f"  Tetrahedra: {len(elements)}")
    print(f"  Materials: {len(materials)}")

    # Voxelize
    grid, grid_shape, (origin, _) = voxelize_mesh(
        nodes, elements, material_ids, args.voxel_size
    )

    # Save numpy array for later use
    np.save(os.path.join(args.output_dir, "mrcp_am_voxels.npy"), grid)
    np.save(os.path.join(args.output_dir, "mrcp_am_origin.npy"), origin)

    # Generate TOPAS file
    output_file = os.path.join(args.output_dir, "phantomVoxel.txt")
    generate_topas_voxel_file(
        grid, grid_shape, origin, args.voxel_size,
        materials, output_file,
    )

    print(f"\nDone! Output in: {args.output_dir}")


if __name__ == "__main__":
    main()