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

    # Also save material ID grid for organ-level post-processing
    mat_path = os.path.join(output_dir, "material_ids.bin")
    voxel_grid.T.flatten("C").astype("<i4").tofile(mat_path)
    logger.info("Wrote material ID grid to %s", mat_path)

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


# Z number (as encoded in ICRP .material files, Z*1000) to TOPAS element name.
_Z_TO_NAME = {
    1000: "Hydrogen",
    2000: "Helium",
    6000: "Carbon",
    7000: "Nitrogen",
    8000: "Oxygen",
    9000: "Fluorine",
    11000: "Sodium",
    12000: "Magnesium",
    13000: "Aluminum",
    14000: "Silicon",
    15000: "Phosphorus",
    16000: "Sulfur",
    17000: "Chlorine",
    19000: "Potassium",
    20000: "Calcium",
    26000: "Iron",
    27000: "Cobalt",
    29000: "Copper",
    30000: "Zinc",
    53000: "Iodine",
    79000: "Gold",
    82000: "Lead",
}


def parse_material_elements(mat_path: str) -> dict[int, dict]:
    """Parse an ICRP .material file including element mass fractions.

    Returns ``{material_id: {name, density, elements: [(z_encoded, fraction)]}}``.
    Ported from scripts/regenerate_voxel_phantom.py.
    """
    materials: dict[int, dict] = {}
    current_name = ""
    current_density = 0.0
    current_id = None
    current_elements: list[tuple[int, float]] = []

    def flush() -> None:
        if current_id is not None:
            materials[current_id] = {
                "name": current_name,
                "density": current_density,
                "elements": current_elements[:],
            }

    with open(mat_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("C ") and "g/cm" in line:
                flush()
                parts = line.split()
                current_name = parts[1]
                current_density = float(parts[2])
                current_id = None
                current_elements = []
            elif line == "C":
                flush()
                current_id = None
            elif line.startswith("m") and not line.startswith("m g"):
                parts = line.split()
                try:
                    current_id = int(parts[0][1:])
                except ValueError:
                    continue
                z = int(parts[1])
                frac = abs(float(parts[2]))
                current_elements = [(z, frac)]
            elif current_id is not None and line[:1].isdigit():
                parts = line.split()
                if len(parts) >= 2:
                    current_elements.append((int(parts[0]), abs(float(parts[1]))))
    flush()
    return materials


def write_icrp_materials(materials: dict[int, dict], output_file: str) -> None:
    """Write TOPAS material definitions (icrp_materials.txt)."""
    with open(output_file, "w") as f:
        f.write("# ICRP tissue material definitions (generated by voxelize_phantom)\n")
        f.write("# %d materials\n\n" % len(materials))
        for mat_id in sorted(materials.keys()):
            mat = materials[mat_id]
            names: list[str] = []
            fracs: list[float] = []
            for z, frac in mat["elements"]:
                name = _Z_TO_NAME.get(z)
                if name is None:
                    logger.warning(
                        "Unknown Z=%d in material %d (%s)", z, mat_id, mat["name"]
                    )
                    continue
                names.append(name)
                fracs.append(frac)
            if not names:
                continue
            mat_name = "ICRP_%d" % mat_id
            n = len(names)
            comp_str = " ".join('"%s"' % nm for nm in names)
            frac_str = " ".join("%.6f" % fr for fr in fracs)
            f.write(
                "# %s (ID=%d, density=%s g/cm3)\n"
                % (mat["name"], mat_id, mat["density"])
            )
            f.write("sv:Ma/%s/Components = %d %s\n" % (mat_name, n, comp_str))
            f.write("uv:Ma/%s/Fractions = %d %s\n" % (mat_name, n, frac_str))
            f.write("d:Ma/%s/Density = %s g/cm3\n\n" % (mat_name, mat["density"]))


def write_phantom_npy(voxel_grid: np.ndarray, output_dir: str) -> None:
    """Save the material-ID grid as phantom.npy for PhantomDoseCalculator."""
    path = os.path.join(output_dir, "phantom.npy")
    np.save(path, voxel_grid.astype(np.int32))
    logger.info("Wrote material-ID grid to %s", path)


def write_phantom_voxel_txt(
    voxel_grid: np.ndarray,
    origin: tuple[float, ...],
    voxel_size: float,
    materials_include: str,
    output_file: str,
) -> None:
    """Render the TsBox + VoxelMaterials phantom include (phantomVoxel.txt).

    Ported from scripts/regenerate_voxel_phantom.py; uses mat_id 0 -> "Air".
    """
    nx, ny, nz = voxel_grid.shape
    total = int(voxel_grid.size)
    logger.info(
        "Building VoxelMaterials vector for %d voxels (%dx%dx%d)...",
        total,
        nx,
        ny,
        nz,
    )

    # TOPAS TsBox VoxelMaterials is X-fastest (ix varies fastest): index
    # iz*ny*nx + iy*nx + ix. The grid is filled as grid[ix,iy,iz], so transpose
    # to (nz,ny,nx) then C-flatten -- matching write_imagecube's voxel_grid.T
    # convention and scripts/regenerate_voxel_phantom.py's iz,iy,ix loop.
    flat = voxel_grid.transpose(2, 1, 0).reshape(-1)
    hlx = nx * voxel_size / 2.0
    hly = ny * voxel_size / 2.0
    hlz = nz * voxel_size / 2.0
    cx = float(origin[0]) + nx * voxel_size / 2.0
    cy = float(origin[1]) + ny * voxel_size / 2.0
    cz = float(origin[2]) + nz * voxel_size / 2.0

    with open(output_file, "w") as f:
        f.write(
            "# Voxelized phantom with ICRP materials (generated by voxelize_phantom)\n"
        )
        f.write("# Voxel size: %s cm (%.1f mm)\n" % (voxel_size, voxel_size * 10))
        f.write("# Grid: %d x %d x %d = %d voxels\n\n" % (nx, ny, nz, total))
        f.write("includeFile = %s\n\n" % os.path.basename(materials_include))

        f.write('s:Ge/Phantom/Type = "TsBox"\n')
        f.write('s:Ge/Phantom/Parent = "World"\n')
        f.write('s:Ge/Phantom/Material = "G4_WATER"\n')
        f.write("d:Ge/Phantom/HLX = %.2f cm\n" % hlx)
        f.write("d:Ge/Phantom/HLY = %.2f cm\n" % hly)
        f.write("d:Ge/Phantom/HLZ = %.2f cm\n" % hlz)
        f.write("d:Ge/Phantom/TransX = %.2f cm\n" % cx)
        f.write("d:Ge/Phantom/TransY = %.2f cm\n" % cy)
        f.write("d:Ge/Phantom/TransZ = %.2f cm\n" % cz)
        f.write("d:Ge/Phantom/RotX = 0.0 deg\n")
        f.write("d:Ge/Phantom/RotY = 0.0 deg\n")
        f.write("d:Ge/Phantom/RotZ = 0.0 deg\n")
        f.write('s:Ge/Phantom/Color = "yellow"\n\n')
        f.write("i:Ge/Phantom/XBins = %d\n" % nx)
        f.write("i:Ge/Phantom/YBins = %d\n" % ny)
        f.write("i:Ge/Phantom/ZBins = %d\n\n" % nz)

        f.write("sv:Ge/Phantom/VoxelMaterials = %d" % total)
        for mat_id in flat:
            f.write(' "Air"' if int(mat_id) == 0 else ' "ICRP_%d"' % int(mat_id))
        f.write("\n\n")

        f.write("# TLE scorer (primary)\n")
        f.write('s:Sc/PhantomTLE/Quantity = "TrackLengthEstimator"\n')
        f.write('s:Sc/PhantomTLE/InputFile = "Muen.dat"\n')
        f.write('s:Sc/PhantomTLE/Component = "Phantom"\n')
        f.write('s:Sc/PhantomTLE/OutputFile = "phantom_tle"\n')
        f.write('s:Sc/PhantomTLE/IfOutputFileAlreadyExists = "Overwrite"\n\n')
        f.write("# DoseToWater scorer\n")
        f.write('s:Sc/PhantomDTW/Quantity = "DoseToWater"\n')
        f.write('s:Sc/PhantomDTW/Component = "Phantom"\n')
        f.write('s:Sc/PhantomDTW/OutputFile = "phantom_dtw"\n')
        f.write('s:Sc/PhantomDTW/IfOutputFileAlreadyExists = "Overwrite"\n\n')
        f.write("# DoseToMedium scorer\n")
        f.write('s:Sc/PhantomDTM/Quantity = "DoseToMedium"\n')
        f.write('s:Sc/PhantomDTM/Component = "Phantom"\n')
        f.write('s:Sc/PhantomDTM/OutputFile = "phantom_dtm"\n')
        f.write('s:Sc/PhantomDTM/IfOutputFileAlreadyExists = "Overwrite"\n')
    logger.info("Wrote %s (%.1f MB)", output_file, os.path.getsize(output_file) / 1e6)


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

    # Emit the contract outputs consumed by the working phantom pipeline:
    # phantom.npy (PhantomDoseCalculator), phantomVoxel.txt + icrp_materials.txt
    # (the rendered template includes). This makes voxelize_phantom.py the single
    # voxelization entry point (supersedes scripts/regenerate_voxel_phantom.py).
    write_phantom_npy(voxel_grid, args.output)
    materials_full = parse_material_elements(str(input_dir / f"{args.name}.material"))
    materials_path = os.path.join(args.output, "icrp_materials.txt")
    write_icrp_materials(materials_full, materials_path)
    write_phantom_voxel_txt(
        voxel_grid,
        origin,
        args.voxel_size,
        materials_path,
        os.path.join(args.output, "phantomVoxel.txt"),
    )

    logger.info("Done. Output in %s", args.output)


if __name__ == "__main__":
    main()
