"""Voxelize an ICRP 145 tetrahedral mesh phantom into a DICOM CT volume.

Reads .node/.ele/.material files, creates a 3D voxel grid at the requested
resolution, assigns each voxel the material of its containing tetrahedron,
maps materials to HU values, and writes DICOM CT slices.

Usage:
    python voxelize_phantom.py --input data/P145/Phantom_data/MRCP_AM \
        --output data/P145/voxelized/MRCP_AM_5mm --voxel-size 5.0
"""

from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)


def read_node_file(node_path: str) -> np.ndarray:
    """Read .node file: returns Nx3 array of vertex coordinates (cm)."""
    logger.info("Reading nodes from %s", node_path)
    with open(node_path) as f:
        first = f.readline().split()
        n = int(first[0])
        nodes = np.empty((n, 3), dtype=np.float64)
        for i in range(n):
            parts = f.readline().split()
            nodes[i] = [float(parts[1]), float(parts[2]), float(parts[3])]
    logger.info(
        "  %d nodes, bbox X=[%.1f,%.1f] Y=[%.1f,%.1f] Z=[%.1f,%.1f]",
        n,
        nodes[:, 0].min(),
        nodes[:, 0].max(),
        nodes[:, 1].min(),
        nodes[:, 1].max(),
        nodes[:, 2].min(),
        nodes[:, 2].max(),
    )
    return nodes


def read_ele_file(ele_path: str) -> tuple[np.ndarray, np.ndarray]:
    """Read .ele file: returns (Nx4 node indices, N material IDs)."""
    logger.info("Reading elements from %s", ele_path)
    with open(ele_path) as f:
        first = f.readline().split()
        n = int(first[0])
        nnodes = int(first[1])
        indices = np.empty((n, nnodes), dtype=np.int64)
        materials = np.empty(n, dtype=np.int64)
        for i in range(n):
            parts = f.readline().split()
            indices[i] = [int(parts[j]) for j in range(1, 1 + nnodes)]
            materials[i] = int(parts[-1])
    logger.info("  %d elements, %d unique materials", n, len(np.unique(materials)))
    return indices, materials


def read_material_file(mat_path: str) -> dict[int, tuple[str, float]]:
    """Read .material file: returns {material_id: (organ_name, density_g/cc)}."""
    logger.info("Reading materials from %s", mat_path)
    materials: dict[int, tuple[str, float]] = {}
    with open(mat_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("C "):
                cleaned = line[2:].strip().replace(" g/cm3", "").replace(" g/cm3", "")
                parts = cleaned.rsplit(" ", 1)
                name = parts[0].strip()
                density = float(parts[1]) if len(parts) > 1 else 1.0
            elif line.startswith("m") and not line.startswith("mM"):
                parts = line.split()
                mat_id = int(parts[0][1:])
                if name:
                    materials[mat_id] = (name, density)
    logger.info("  %d materials loaded", len(materials))
    return materials


def point_in_tet_batch(points: np.ndarray, tet_nodes: np.ndarray) -> np.ndarray:
    """Test if points are inside tetrahedra using barycentric coordinates.

    Args:
        points: (N, 3) query points
        tet_nodes: (N, 4, 3) tetrahedron vertices (one per query)

    Returns:
        (N,) bool array: True if point is inside the corresponding tet.
    """
    v0 = tet_nodes[:, 0]
    v1 = tet_nodes[:, 1]
    v2 = tet_nodes[:, 2]
    v3 = tet_nodes[:, 3]

    d0 = v1 - v0
    d1 = v2 - v0
    d2 = v3 - v0
    dp = points - v0

    det = (
        d0[:, 0] * (d1[:, 1] * d2[:, 2] - d1[:, 2] * d2[:, 1])
        - d0[:, 1] * (d1[:, 0] * d2[:, 2] - d1[:, 2] * d2[:, 0])
        + d0[:, 2] * (d1[:, 0] * d2[:, 1] - d1[:, 1] * d2[:, 0])
    )

    safe_det = np.where(np.abs(det) < 1e-30, 1e-30, det)

    b1 = (
        dp[:, 0] * (d1[:, 1] * d2[:, 2] - d1[:, 2] * d2[:, 1])
        - dp[:, 1] * (d1[:, 0] * d2[:, 2] - d1[:, 2] * d2[:, 0])
        + dp[:, 2] * (d1[:, 0] * d2[:, 1] - d1[:, 1] * d2[:, 0])
    ) / safe_det

    b2 = (
        d0[:, 0] * (dp[:, 1] * d2[:, 2] - dp[:, 2] * d2[:, 1])
        - d0[:, 1] * (dp[:, 0] * d2[:, 2] - dp[:, 2] * d2[:, 0])
        + d0[:, 2] * (dp[:, 0] * d2[:, 1] - dp[:, 1] * d2[:, 0])
    ) / safe_det

    b3 = (
        d0[:, 0] * (d1[:, 1] * dp[:, 2] - d1[:, 2] * dp[:, 1])
        - d0[:, 1] * (d1[:, 0] * dp[:, 2] - d1[:, 2] * dp[:, 0])
        + d0[:, 2] * (d1[:, 0] * dp[:, 1] - d1[:, 1] * dp[:, 0])
    ) / safe_det

    b0 = 1.0 - b1 - b2 - b3

    eps = -1e-6
    return (b0 >= eps) & (b1 >= eps) & (b2 >= eps) & (b3 >= eps)


def density_to_hu(density: float) -> int:
    """Approximate HU value from density (g/cm³)."""
    if density < 0.01:
        return -1000
    return int(round((density - 1.0) * 1000))


def voxelize(
    nodes: np.ndarray,
    tet_indices: np.ndarray,
    tet_materials: np.ndarray,
    voxel_size: float = 0.5,
    k_neighbors: int = 20,
) -> tuple[np.ndarray, tuple[float, ...], np.ndarray, np.ndarray]:
    """Voxelize the tetrahedral mesh.

    Returns:
        voxel_grid: (nx, ny, nz) int16 array of material IDs (0 = air)
        origin: (x0, y0, z0) world position of first voxel center
        voxel_coords: unused (None)
        voxel_hu: (nx, ny, nz) int16 HU values
    """
    bbox_min = nodes.min(axis=0)
    bbox_max = nodes.max(axis=0)

    padding = voxel_size
    bbox_min -= padding
    bbox_max += padding

    extents = bbox_max - bbox_min
    n_voxels = np.ceil(extents / voxel_size).astype(int)

    logger.info(
        "Voxel grid: %d × %d × %d = %d voxels (%.1f mm)",
        n_voxels[0],
        n_voxels[1],
        n_voxels[2],
        n_voxels.prod(),
        voxel_size * 10,
    )

    tet_centroids = nodes[tet_indices].mean(axis=1)
    logger.info("Building KDTree of %d tetrahedron centroids...", len(tet_centroids))
    tree = cKDTree(tet_centroids)

    voxel_grid = np.zeros(n_voxels, dtype=np.int64)
    total = n_voxels.prod()

    origin = bbox_min + voxel_size / 2.0

    for iz in range(n_voxels[2]):
        z = origin[2] + iz * voxel_size
        for iy in range(n_voxels[1]):
            y = origin[1] + iy * voxel_size
            nx_slice = n_voxels[0]
            voxel_points = np.column_stack(
                [
                    origin[0] + np.arange(nx_slice) * voxel_size,
                    np.full(nx_slice, y),
                    np.full(nx_slice, z),
                ]
            )

            dists, indices = tree.query(voxel_points, k=k_neighbors)

            assigned = np.zeros(nx_slice, dtype=bool)
            for k_idx in range(k_neighbors):
                if assigned.all():
                    break
                candidate = indices[:, k_idx]
                tet_verts = nodes[tet_indices[candidate]]
                inside = point_in_tet_batch(voxel_points, tet_verts)
                newly = inside & ~assigned
                voxel_grid[newly, iy, iz] = tet_materials[candidate[newly]].astype(
                    np.int64
                )
                assigned |= inside

        if iz % 20 == 0:
            filled = (voxel_grid[:, :, : iz + 1] > 0).sum()
            logger.info(
                "  Slice %d/%d (%.0f%%), %d voxels filled",
                iz,
                n_voxels[2],
                100.0 * (iz + 1) / n_voxels[2],
                filled,
            )

    filled = (voxel_grid > 0).sum()
    logger.info(
        "Voxelization complete: %d / %d voxels filled (%.1f%%)",
        filled,
        total,
        100.0 * filled / total,
    )

    return voxel_grid, tuple(origin), None, None


def write_imagecube(
    voxel_grid: np.ndarray,
    origin: tuple[float, ...],
    voxel_size: float,
    materials: dict[int, tuple[str, float]],
    output_dir: str,
) -> None:
    """Write as TOPAS TsImageCube format.

    TsImageCube expects:
    - A binary file with voxel values (material IDs or HU)
    - A .imagecube header file with dimensions and spacing
    """
    os.makedirs(output_dir, exist_ok=True)

    nx, ny, nz = voxel_grid.shape

    hu_values = np.zeros(voxel_grid.shape, dtype=np.int16)
    for mat_id in np.unique(voxel_grid):
        if mat_id == 0:
            continue
        if mat_id in materials:
            _, density = materials[mat_id]
            hu_values[voxel_grid == mat_id] = density_to_hu(density)
        else:
            hu_values[voxel_grid == mat_id] = 0

    bin_path = os.path.join(output_dir, "phantom.bin")
    logger.info("Writing ImageCube binary to %s", bin_path)
    hu_values.T.flatten("C").astype("<i2").tofile(bin_path)

    header_path = os.path.join(output_dir, "phantom.imagecube")
    with open(header_path, "w") as f:
        f.write("# ImageCube voxelized phantom\n")
        f.write(f"{nx} {ny} {nz}\n")
        f.write(
            f"{voxel_size * 10:.1f} {voxel_size * 10:.1f} {voxel_size * 10:.1f} mm\n"
        )
        f.write(f"{origin[0] * 10:.1f} {origin[1] * 10:.1f} {origin[2] * 10:.1f} mm\n")
        f.write("Integer\n")

    mat_path = os.path.join(output_dir, "material_map.txt")
    with open(mat_path, "w") as f:
        f.write("# MaterialID  OrganName  Density(g/cm3)  HU\n")
        for mat_id in sorted(materials.keys()):
            name, density = materials[mat_id]
            f.write(f"{mat_id}\t{name}\t{density:.3f}\t{density_to_hu(density)}\n")

    logger.info("Wrote %s, %s, %s", bin_path, header_path, mat_path)


def main():
    parser = argparse.ArgumentParser(description="Voxelize ICRP 145 tetrahedral mesh")
    parser.add_argument(
        "--input", required=True, help="Input directory with .node/.ele/.material"
    )
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument(
        "--voxel-size",
        type=float,
        default=0.5,
        help="Voxel size in cm (default: 0.5 = 5mm)",
    )
    parser.add_argument("--name", default="MRCP_AM", help="Phantom name prefix")
    args = parser.parse_args()

    input_dir = Path(args.input)
    nodes = read_node_file(str(input_dir / f"{args.name}.node"))
    tet_indices, tet_materials = read_ele_file(str(input_dir / f"{args.name}.ele"))
    materials = read_material_file(str(input_dir / f"{args.name}.material"))

    voxel_grid, origin, _, _ = voxelize(
        nodes,
        tet_indices,
        tet_materials,
        voxel_size=args.voxel_size,
    )

    write_imagecube(voxel_grid, origin, args.voxel_size, materials, args.output)

    logger.info("Done. Output in %s", args.output)


if __name__ == "__main__":
    main()
