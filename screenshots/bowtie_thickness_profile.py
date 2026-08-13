"""Ray-cast through the bow-tie STL along the beam axis to get the Aluminum
thickness profile. After RotZ=-90 the beam runs along STL-X, so we cast rays
along X at lateral STL-Y positions (Z=0) and report the solid thickness."""
from __future__ import annotations

import struct

import numpy as np


def load(path):
    with open(path, "rb") as f:
        f.read(80)
        n = struct.unpack("<I", f.read(4))[0]
        d = np.frombuffer(f.read(50 * n), dtype=np.uint8).reshape(n, 50)
        return np.frombuffer(d[:, 12:48].tobytes(), dtype="<f4").reshape(n, 3, 3)


def thickness_at_y(y0, tris):
    """Solid thickness along X for a ray at (Y=y0, Z=0). Uses the 2D (Y,Z)
    projection: a triangle is 'hit' if (y0,0) lies inside its YZ projection;
    the X entry is the plane-intersection."""
    hits = []
    for p0, p1, p2 in tris:
        ay, az = p0[1], p0[2]
        by, bz = p1[1], p1[2]
        cy, cz = p2[1], p2[2]
        # barycentric in YZ plane for point (y0, 0)
        v0 = (cy - ay, cz - az)
        v1 = (by - ay, bz - az)
        v2 = (y0 - ay, 0.0 - az)
        d00 = v0[0] * v0[0] + v0[1] * v0[1]
        d01 = v0[0] * v1[0] + v0[1] * v1[1]
        d02 = v0[0] * v2[0] + v0[1] * v2[1]
        d11 = v1[0] * v1[0] + v1[1] * v1[1]
        d12 = v1[0] * v2[0] + v1[1] * v2[1]
        denom = d00 * d11 - d01 * d01
        if abs(denom) < 1e-12:
            continue
        v = (d11 * d02 - d01 * d12) / denom
        w = (d00 * d12 - d01 * d02) / denom
        u = 1.0 - v - w
        if u >= -1e-9 and v >= -1e-9 and w >= -1e-9:
            x = u * p0[0] + v * p2[0] + w * p1[0]  # barycentric X
            hits.append(x)
    if len(hits) < 2:
        return 0.0
    hits.sort()
    # odd crossings -> take pairwise (entry,exit); approximate thickness as range/2
    th = 0.0
    for i in range(0, len(hits) - 1, 2):
        th += hits[i + 1] - hits[i]
    return th


def main():
    tris = load("src/boilerplates/TOPAS_includeFiles/fullfan.stl")
    print("Beam-along-X (Al) thickness profile at Z=0:")
    for y_cm in [-2.5, -1.5, -0.5, 0.0, 0.5, 1.5, 2.5]:
        t = thickness_at_y(y_cm * 10.0, tris) / 10.0
        print("  lateral Y=%+.1f cm : %.2f cm Al" % (y_cm, t))


if __name__ == "__main__":
    main()
