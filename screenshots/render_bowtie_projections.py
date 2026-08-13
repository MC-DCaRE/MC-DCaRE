"""Render the bow-tie STL in three orthogonal projections (placed frame) to
diagnose whether the thin axis aligns with the beam. Pure matplotlib, headless.

After the head template's RotZ=-90, STL-X -> TOPAS-Y (beam direction),
STL-Y -> TOPAS-X (lateral), STL-Z -> TOPAS-Z (scan axis). A correct bow-tie
has its THIN dimension along the beam (TOPAS-Y == STL-X).
"""
from __future__ import annotations

import os
import struct

import matplotlib.pyplot as plt
import numpy as np

STL = "src/boilerplates/TOPAS_includeFiles/fullfan.stl"


def load_triangles(path):
    with open(path, "rb") as f:
        f.read(80)
        n = struct.unpack("<I", f.read(4))[0]
        data = np.frombuffer(f.read(50 * n), dtype=np.uint8).reshape(n, 50)
        # layout per triangle: 12 normal + 36 (3 verts) + 2 attr
        verts = np.frombuffer(
            data[:, 12:48].tobytes(), dtype="<f4"
        ).reshape(n, 3, 3)
        return verts


def main():
    tris = load_triangles(STL)
    # STL is already recentered (centroid~0). Placed frame after RotZ=-90deg:
    # (x,y,z) -> (y, -x, z). TOPAS-X=STL-Y, TOPAS-Y(beam)=-STL-X, TOPAS-Z=STL-Z.
    R = np.array([[0, 1, 0], [-1, 0, 0], [0, 0, 1]], dtype=float)  # RotZ(-90)
    placed = tris @ R.T  # rotate each vertex

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    titles = [
        ("TOPAS X (lateral) cm", "TOPAS Z (scan) cm", "X-Z plane (view along beam)"),
        ("TOPAS X (lateral) cm", "TOPAS Y / beam cm", "X-Y plane (side, scan axis out of page)"),
        ("TOPAS Z (scan) cm", "TOPAS Y / beam cm", "Z-Y plane (side, lateral out of page)"),
    ]
    pairs = [(0, 2), (0, 1), (2, 1)]
    for ax, (ia, ib), (xl, yl, title) in zip(axes, pairs, titles):
        for tri in placed[::20]:  # subsample for speed
            poly = tri[:, [ia, ib]]
            poly = np.vstack([poly, poly[:1]])
            ax.plot(poly[:, 0] / 10, poly[:, 1] / 10, lw=0.3, color="steelblue")
        ax.set_xlabel(xl)
        ax.set_ylabel(yl)
        ax.set_title(title)
        ax.set_aspect("equal")
        ax.grid(True, alpha=0.3)
    # Annotate beam axis on the side views (beam travels +TOPAS-Y).
    for ax in axes[1:]:
        ymax = ax.get_ylim()[1]
        ax.annotate("beam ->", xy=(0, ymax * 0.85), ha="center", color="crimson")

    fig.suptitle(
        "Bow-tie STL in placed frame (RotZ=-90). Thin axis must align with beam (TOPAS-Y).",
        fontsize=11,
    )
    fig.tight_layout()
    out = "screenshots/bowtie_projections.png"
    fig.savefig(out, dpi=110)
    print("Wrote", out)

    # Report the bbox in the placed frame.
    flat = placed.reshape(-1, 3)
    print(
        "Placed bbox (cm): X[%.1f,%.1f] Y(beam)[%.1f,%.1f] Z(scan)[%.1f,%.1f]"
        % (
            flat[:, 0].min() / 10,
            flat[:, 0].max() / 10,
            flat[:, 1].min() / 10,
            flat[:, 1].max() / 10,
            flat[:, 2].min() / 10,
            flat[:, 2].max() / 10,
        )
    )
    print(
        "Beam-direction (Y) full thickness = %.1f cm of Al (bbox max)"
        % ((flat[:, 1].max() - flat[:, 1].min()) / 10)
    )


if __name__ == "__main__":
    if not os.path.isdir("src"):
        os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    main()
