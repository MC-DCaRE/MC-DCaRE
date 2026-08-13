"""Process the Inbum bow-tie STL into TOPAS-ready binary STLs.

Reads the measured full-fan bow-tie (ASCII STL from
``research/Monte Carlo stuff from Inbum/bowtie.stl``), recenters it by its
bounding-box centroid, optionally decimates it (vertex-clustering weld), and
writes a binary STL (TOPAS ``TsCAD`` documents only binary STL). Also derives an
approximate half-fan STL by keeping one lateral half.

No external mesh libraries are required (numpy + stdlib only). For precise
triangle-target decimation, run the recentered output through MeshLab/trimesh.

Usage::

    python tools/process_bowtie_stl.py \\
        --input "research/Monte Carlo stuff from Inbum/bowtie.stl" \\
        --output-dir data/bowtie \\
        --decimate-eps 0.6
"""

from __future__ import annotations

import argparse
import logging
import struct
from pathlib import Path
from typing import cast

import numpy as np

logger = logging.getLogger(__name__)

# 80-byte header + 50 bytes per triangle (12 bytes normal + 3*12 bytes vertices
# + 2 bytes attribute) in a binary STL.
_BINARY_HEADER_SIZE = 80
_BINARY_TRIANGLE_SIZE = 50


def parse_ascii_stl(path: str | Path) -> np.ndarray:
    """Parse an ASCII STL into an (N, 3, 3) float32 array of triangle vertices.

    Each triangle is three rows [v0, v1, v2] of [x, y, z]. Normals are ignored
    (recomputed on write).
    """
    verts: list[tuple[float, float, float]] = []
    triangle_starts: list[int] = []
    with open(path) as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith("facet"):
                triangle_starts.append(len(verts))
            elif stripped.startswith("vertex"):
                parts = stripped.split()
                verts.append((float(parts[1]), float(parts[2]), float(parts[3])))

    if len(verts) % 3 != 0 or len(triangle_starts) * 3 != len(verts):
        raise ValueError(
            "STL parse mismatch: %d vertices, %d facets"
            % (len(verts), len(triangle_starts))
        )
    arr = np.asarray(verts, dtype=np.float32).reshape(-1, 3, 3)
    logger.info("Parsed %d triangles from %s", arr.shape[0], path)
    return arr


def bbox_centroid(triangles: np.ndarray) -> np.ndarray:
    """Return the centroid of the triangle-set bounding box (3,)."""
    flat = triangles.reshape(-1, 3)
    return cast(np.ndarray, (flat.min(axis=0) + flat.max(axis=0)) / 2.0)


def recenter(triangles: np.ndarray) -> np.ndarray:
    """Translate triangles so the bounding-box centroid is at the origin."""
    centroid = bbox_centroid(triangles)
    logger.info(
        "Recentering by %s; bbox %s..%s",
        centroid,
        triangles.reshape(-1, 3).min(axis=0),
        triangles.reshape(-1, 3).max(axis=0),
    )
    return cast(np.ndarray, triangles - centroid)


def decimate(triangles: np.ndarray, eps_mm: float) -> np.ndarray:
    """Decimate by vertex clustering (Rossignac-Borrel weld).

    Vertices within ``eps_mm`` (quantised onto an eps grid) are welded to a
    single representative; triangles that collapse to fewer than three distinct
    vertices are dropped. This is a real, parameter-tunable reduction (coarser
    eps -> fewer triangles) though it does not target an exact count.
    """
    flat = triangles.reshape(-1, 3)
    if eps_mm <= 0:
        logger.info("Decimate eps<=0: no decimation (%d triangles)", triangles.shape[0])
        return triangles
    keys = np.round(flat / eps_mm).astype(np.int64)
    # Unique-ify the 3D integer keys directly (robust for any coordinate range;
    # the prior packed-int64 scheme could collide for large coords/tiny eps).
    _, inverse = np.unique(keys, axis=0, return_inverse=True)
    n_unique = int(inverse.max()) + 1 if inverse.size else 0
    welded = np.zeros((n_unique, 3), dtype=np.float32)
    # Representative = mean of clustered vertices (smooths the weld).
    counts = np.bincount(inverse, minlength=n_unique)
    np.add.at(welded, inverse, flat)
    welded /= counts[:, None]
    new_tri = welded[inverse].reshape(-1, 3, 3)
    # Drop degenerate triangles (< 3 distinct vertices after welding).
    keep = np.ones(new_tri.shape[0], dtype=bool)
    for i in range(3):
        for j in range(i + 1, 3):
            same = np.all(new_tri[:, i] == new_tri[:, j], axis=1)
            keep &= ~same
    out = new_tri[keep]
    logger.info(
        "Decimate eps=%.3f mm: %d -> %d triangles",
        eps_mm,
        triangles.shape[0],
        out.shape[0],
    )
    return cast(np.ndarray, out)


def derive_half_fan(
    triangles: np.ndarray, lateral_axis: int = 1, keep_positive: bool = True
) -> np.ndarray:
    """Keep one lateral half of the bow-tie and recenter it.

    Args:
        triangles: (N, 3, 3) recentred full-fan triangles.
        lateral_axis: axis index (0=X, 1=Y, 2=Z) of the wedge-build direction.
        keep_positive: keep triangles whose centroid is on the positive side.

    The TrueBeam half-fan is a distinct physical filter; this one-sided crop is
    an approximation. The kept subset is recentered by its own centroid so the
    TsCAD component origin sits at the half-fan centre (the template then applies
    the lateral TransX offset).
    """
    centroids = triangles.mean(axis=1)
    side = (
        centroids[:, lateral_axis] >= 0
        if keep_positive
        else centroids[:, lateral_axis] < 0
    )
    kept = triangles[side]
    if kept.shape[0] == 0:
        raise ValueError("Half-fan derivation kept zero triangles; check lateral_axis")
    kept = kept - bbox_centroid(kept)
    logger.info(
        "Half-fan: kept %d / %d triangles on %s side of axis %d",
        kept.shape[0],
        triangles.shape[0],
        "positive" if keep_positive else "negative",
        lateral_axis,
    )
    return cast(np.ndarray, kept)


def write_binary_stl(triangles: np.ndarray, path: str | Path) -> None:
    """Write triangles as a binary STL (normals recomputed)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    n = int(triangles.shape[0])
    with open(path, "wb") as f:
        f.write(b"\0" * _BINARY_HEADER_SIZE)
        f.write(struct.pack("<I", n))
        for tri in triangles:
            v0, v1, v2 = tri[0], tri[1], tri[2]
            normal = _facet_normal(v0, v1, v2)
            f.write(struct.pack("<3f", *normal))
            for v in (v0, v1, v2):
                f.write(struct.pack("<3f", *v))
            f.write(struct.pack("<H", 0))
    logger.info("Wrote binary STL: %s (%d triangles)", path, n)


def _facet_normal(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> np.ndarray:
    """Outward facet normal (zero-vector for degenerate facets)."""
    n = np.cross(b - a, c - a)
    norm = np.linalg.norm(n)
    if norm < 1e-12:
        return cast(np.ndarray, np.zeros(3, dtype=np.float32))
    return cast(np.ndarray, (n / norm).astype(np.float32))


def report(triangles: np.ndarray) -> dict:
    flat = triangles.reshape(-1, 3)
    return {
        "triangles": int(triangles.shape[0]),
        "bbox_min": flat.min(axis=0).tolist(),
        "bbox_max": flat.max(axis=0).tolist(),
        "centroid": bbox_centroid(triangles).tolist(),
    }


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
    parser = argparse.ArgumentParser(
        description="Process the Inbum bow-tie STL for TOPAS TsCAD"
    )
    parser.add_argument("--input", required=True, help="Input ASCII STL")
    parser.add_argument("--output-dir", default="data/bowtie", help="Output directory")
    parser.add_argument(
        "--decimate-eps",
        type=float,
        default=0.6,
        help="Vertex-clustering cell size in mm (0 = no decimation)",
    )
    parser.add_argument(
        "--half-fan-axis",
        type=int,
        default=1,
        choices=(0, 1, 2),
        help="Lateral axis for half-fan crop (0=X,1=Y,2=Z)",
    )
    parser.add_argument(
        "--no-half-fan", action="store_true", help="Skip half-fan derivation"
    )
    args = parser.parse_args()

    triangles = parse_ascii_stl(args.input)
    logger.info("Source report: %s", report(triangles))

    full = recenter(triangles)
    if args.decimate_eps > 0:
        full = decimate(full, args.decimate_eps)
    full_path = Path(args.output_dir) / "fullfan.stl"
    write_binary_stl(full, full_path)
    logger.info("Full-fan report: %s", report(full))

    if not args.no_half_fan:
        half = derive_half_fan(full, lateral_axis=args.half_fan_axis)
        half_path = Path(args.output_dir) / "halffan.stl"
        write_binary_stl(half, half_path)
        logger.info("Half-fan report: %s", report(half))

    readme = Path(args.output_dir) / "README.md"
    with open(readme, "w") as f:
        f.write("# Bow-tie STL assets\n\n")
        f.write("Processed from `research/Monte Carlo stuff from Inbum/bowtie.stl` ")
        f.write("by `tools/process_bowtie_stl.py`.\n\n")
        f.write("- `fullfan.stl` -- binary STL, recentered, decimated.\n")
        f.write("- `halffan.stl` -- one lateral half of the full-fan (approximation; ")
        f.write("TrueBeam half-fan is a distinct filter).\n\n")
        f.write('Loaded by TOPAS `TsCAD` (`FileFormat = "stl"`).\n')
    logger.info("Wrote %s", readme)


if __name__ == "__main__":
    main()
