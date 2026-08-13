from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from tools.voxelize_phantom import write_phantom_voxel_txt


def _parse_voxel_materials(path):
    """Return the list of material names from a rendered phantomVoxel.txt."""
    names = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("sv:Ge/Phantom/VoxelMaterials"):
                # tokens after '=' are: <count> then quoted material names
                rhs = line.split("=", 1)[1]
                tokens = [t.strip().strip('"') for t in rhs.split() if t.strip()]
                names = tokens[1:]  # drop the leading integer count
                break
    return names


def test_voxel_materials_ordering_is_x_fastest(tmp_path):
    """VoxelMaterials index iz*ny*nx + iy*nx + ix must map to grid[ix,iy,iz]."""
    # 2x2x2 grid with distinct IDs so ordering is observable.
    grid = np.zeros((2, 2, 2), dtype=np.int32)
    for ix in range(2):
        for iy in range(2):
            for iz in range(2):
                grid[ix, iy, iz] = 100 + ix * 10 + iy * 5 + iz
    nx, ny, nz = grid.shape

    out = tmp_path / "phantomVoxel.txt"
    write_phantom_voxel_txt(grid, (0.0, 0.0, 0.0), 0.5, "icrp_materials.txt", str(out))

    names = _parse_voxel_materials(str(out))
    assert len(names) == nx * ny * nz

    for ix in range(nx):
        for iy in range(ny):
            for iz in range(nz):
                x_fastest_index = iz * ny * nx + iy * nx + ix
                expected = "ICRP_%d" % grid[ix, iy, iz]
                assert names[x_fastest_index] == expected, (
                    "pos %d (ix=%d,iy=%d,iz=%d): expected %s got %s"
                    % (x_fastest_index, ix, iy, iz, expected, names[x_fastest_index])
                )


def test_voxel_materials_zero_id_is_air(tmp_path):
    grid = np.array([[[5, 0]]], dtype=np.int32)  # 1x1x2
    out = tmp_path / "phantomVoxel.txt"
    write_phantom_voxel_txt(grid, (0.0, 0.0, 0.0), 0.5, "icrp_materials.txt", str(out))
    names = _parse_voxel_materials(str(out))
    # X-fastest: ix=0 first -> grid[0,0,0]=5 then grid[0,0,1]=0
    assert names == ["ICRP_5", "Air"]
