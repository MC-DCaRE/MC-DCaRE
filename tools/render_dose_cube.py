#!/usr/bin/env python3
"""Render the phantom dose cube as orthogonal views with body outline.

Loads a TOPAS phantom dose CSV (ix, iy, iz, Sum), folds it onto the
voxelized MRCP-AM material grid, and renders:

- Coronal MAX-intensity projection (X horizontal, body-Z vertical)
- Sagittal MAX-intensity projection (Y horizontal, body-Z vertical)
- Axial slice at the dose-weighted-mean Z (X vs Y)

Dose is shown peak-normalized on a log color scale (4 decades). The body
outline is the grid != -1 mask edge. Output PNG is written into the
runfolder.

Usage:
    uv run python tools/render_dose_cube.py <runfolder> [--dose-file phantom_tle.csv]
        [--grid test_voxel_output/mrcp_am/mrcp_am_voxels.npy] [--decades 4]
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_GRID = PROJECT_ROOT / "test_voxel_output" / "mrcp_am" / "mrcp_am_voxels.npy"


def render(
    runfolder: Path,
    dose_file: str = "phantom_tle.csv",
    grid_path: Path | None = None,
    decades: float = 4.0,
) -> Path:
    """Render orthogonal dose views for one runfolder and save the PNG.

    Called by the CLI below and by the phantom verification workflows
    (run_edose_validation / run_isocenter_sweep) for per-protocol
    diagnostics: coronal + sagittal MAX-ips, axial slice at the
    dose-weighted mean Z and at the isocenter plane, body outline overlay,
    peak-normalized log color scale.

    Args:
        runfolder: Simulation runfolder containing the dose CSV and
            ``phantomVoxel.txt`` (for the box translation).
        dose_file: Dose CSV filename (e.g. ``phantom_tle.csv``,
            ``phantom_dtm.csv``).
        grid_path: Material-ID grid ``.npy``; defaults to the coarse
            MRCP-AM grid matching the phantom-mode scorer geometry.
        decades: Log display range in decades below peak.

    Returns:
        Path of the saved PNG (``<runfolder>/dose_render_<dose>.png``).

    Raises:
        FileNotFoundError: If the dose CSV or phantomVoxel.txt is missing.
        ValueError: If the dose cube is all zeros.
    """
    runfolder = Path(runfolder)
    dose_csv = runfolder / dose_file
    if not dose_csv.exists():
        raise FileNotFoundError(f"{dose_csv} not found")
    grid_file = grid_path or DEFAULT_GRID

    grid = np.load(grid_file)
    cube = np.zeros(grid.shape)
    with open(dose_csv) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.strip().split(", ")
            if len(parts) < 4:
                continue
            ix, iy, iz = int(parts[0]), int(parts[1]), int(parts[2])
            if ix < grid.shape[0] and iy < grid.shape[1] and iz < grid.shape[2]:
                cube[ix, iy, iz] += float(parts[3])
    peak = float(cube.max())
    if peak <= 0:
        raise ValueError("dose cube is all zeros")

    body = grid != -1
    # World-frame axes (cm): voxel centers relative to box center + Trans
    trans = {}
    for line in (runfolder / "phantomVoxel.txt").read_text().splitlines():
        for key in ("TransX", "TransY", "TransZ"):
            if line.startswith(f"d:Ge/Phantom/{key}"):
                trans[key] = float(line.split("=")[1].split("cm")[0])
    xs = np.arange(grid.shape[0]) - grid.shape[0] / 2 + 0.5 + trans.get("TransX", 0.0)
    ys = np.arange(grid.shape[1]) - grid.shape[1] / 2 + 0.5 + trans.get("TransY", 0.0)
    zs = np.arange(grid.shape[2]) - grid.shape[2] / 2 + 0.5 + trans.get("TransZ", 0.0)

    disp = np.log10(np.where(cube > 0, cube / peak, np.nan))
    vmin, vmax = -decades, 0.0

    fig, axes = plt.subplots(1, 4, figsize=(20, 6))
    fig.suptitle(
        f"{dose_file} -- {runfolder.name} (peak-normalized, log scale)",
        fontsize=11,
    )

    def outline(ax: plt.Axes, mask2d: np.ndarray, x: np.ndarray, y: np.ndarray) -> None:
        ax.contour(x, y, mask2d, levels=[0.5], colors="white", linewidths=1.0)

    # Coronal: max over Y (X horizontal, Z vertical)
    cor = np.nanmax(disp, axis=1).T
    im = axes[0].pcolormesh(
        xs, zs, cor, vmin=vmin, vmax=vmax, cmap="inferno", shading="auto"
    )
    outline(axes[0], np.nanmax(body.astype(float), axis=1).T > 0.5, xs, zs)
    axes[0].set_title("Coronal MAX-ip (X-Z)")
    axes[0].set_xlabel("world X (cm)")
    axes[0].set_ylabel("world Z (cm)")
    axes[0].set_aspect("equal")

    # Sagittal: max over X
    sag = np.nanmax(disp, axis=0).T
    axes[1].pcolormesh(
        ys, zs, sag, vmin=vmin, vmax=vmax, cmap="inferno", shading="auto"
    )
    outline(axes[1], np.nanmax(body.astype(float), axis=0).T > 0.5, ys, zs)
    axes[1].set_title("Sagittal MAX-ip (Y-Z)")
    axes[1].set_xlabel("world Y (cm)")
    axes[1].set_ylabel("world Z (cm)")
    axes[1].set_aspect("equal")

    # Axial at dose-weighted mean Z
    idx = np.arange(cube.shape[2])
    zmean = float(np.average(idx, weights=cube.sum(axis=(0, 1))))
    ax_slice = disp[:, :, int(round(zmean))].T
    axes[2].pcolormesh(
        xs, ys, ax_slice, vmin=vmin, vmax=vmax, cmap="inferno", shading="auto"
    )
    outline(axes[2], body[:, :, int(round(zmean))].T, xs, ys)
    axes[2].set_title(f"Axial at iz={int(round(zmean))} (dose-weighted mean Z)")
    axes[2].set_xlabel("world X (cm)")
    axes[2].set_ylabel("world Y (cm)")
    axes[2].set_aspect("equal")

    # Axial at isocenter (beam plane, world Z = 0)
    iz_iso = int(np.argmin(np.abs(zs)))
    ax_iso = disp[:, :, iz_iso].T
    axes[3].pcolormesh(
        xs, ys, ax_iso, vmin=vmin, vmax=vmax, cmap="inferno", shading="auto"
    )
    outline(axes[3], body[:, :, iz_iso].T, xs, ys)
    axes[3].set_title(f"Axial at isocenter iz={iz_iso} (world Z={zs[iz_iso]:.2f} cm)")
    axes[3].set_xlabel("world X (cm)")
    axes[3].set_ylabel("world Y (cm)")
    axes[3].set_aspect("equal")

    cbar = fig.colorbar(im, ax=axes, shrink=0.85, pad=0.02)
    cbar.set_label("dose / peak (log10)")
    out_png = runfolder / f"dose_render_{dose_file.replace('.csv', '')}.png"
    fig.savefig(out_png, dpi=140, bbox_inches="tight")
    plt.close(fig)
    return out_png


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runfolder", type=Path)
    parser.add_argument("--dose-file", default="phantom_tle.csv")
    parser.add_argument("--grid", type=Path, default=DEFAULT_GRID)
    parser.add_argument("--decades", type=float, default=4.0)
    args = parser.parse_args()

    out_png = render(
        args.runfolder, args.dose_file, grid_path=args.grid, decades=args.decades
    )
    print(f"saved {out_png}")


if __name__ == "__main__":
    main()
