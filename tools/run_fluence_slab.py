#!/usr/bin/env python3
"""Patient-free beam fluence diagnostic.

Generates a phantom-mode runfolder for a protocol, REPLACES the phantom
include with a thin air slab at the isocenter plane (no patient), runs a
single-angle irradiation, and renders the beam's X-Z fluence-kerma map
plus X and Z profiles. Answers: where do particles actually hit the
patient plane (collimator field, bow-tie shaping, out-of-field leakage)?

Scorers on the slab:
- ``slab_tle``: binned TrackLengthEstimator (fluence x mu_en/rho kerma),
  1 cm bins over X in +-50 cm, Z in +-100 cm -> direct 2D profile map
- ``slab_phsp``: PhaseSpace scorer (entering only) for particle-level
  follow-up with PhaseSpaceAnalyzer

Usage:
    uv run python tools/run_fluence_slab.py [--mode Pelvis] [--histories 2000000]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from run_edose_validation import (  # noqa: E402
    OUTPUT_BASE,
    PHANTOM_CONFIG,
    load_and_patch_config,
    run_simulation,
    run_topas,
    swap_voxel_phantom,
    write_temp_config,
)

SLAB_TEMPLATE = """# Patient-free fluence slab (diagnostic: replaces the voxel phantom)
# Thin air slab at the isocenter plane; beam travels +Y from Y=-100 cm.

s:Ge/FluenceSlab/Type = "TsBox"
s:Ge/FluenceSlab/Parent = "World"
s:Ge/FluenceSlab/Material = "G4_AIR"
d:Ge/FluenceSlab/HLX = 50.0 cm
d:Ge/FluenceSlab/HLY = 0.1 cm
d:Ge/FluenceSlab/HLZ = 100.0 cm
d:Ge/FluenceSlab/TransX = 0.0 cm
d:Ge/FluenceSlab/TransY = 0.0 cm
d:Ge/FluenceSlab/TransZ = 0.0 cm
s:Ge/FluenceSlab/Color = "Blue"

# Binned kerma map (fluence-weighted): 1 cm bins
s:Sc/SlabTLE/Quantity = "TrackLengthEstimator"
s:Sc/SlabTLE/InputFile = "Muen.dat"
s:Sc/SlabTLE/Component = "FluenceSlab"
s:Sc/SlabTLE/OutputFile = "slab_tle"
s:Sc/SlabTLE/IfOutputFileAlreadyExists = "Overwrite"
i:Sc/SlabTLE/XBins = 100
i:Sc/SlabTLE/YBins = 1
i:Sc/SlabTLE/ZBins = 200

# NOTE: a PhaseSpace scorer on the TsBox requires extra surface
# parameterization (Position/DetectionDistance) that TOPAS rejects here;
# the binned TLE map above already answers "where do particles hit".
"""


def load_slab_map(csv: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (X centers cm, Z centers cm, 2D Sum array) from a binned slab CSV.

    TOPAS binned scorer CSVs carry BIN INDICES, not positions; the slab is
    fixed at X +-50 cm in 100 bins and Z +-100 cm in 200 bins, so index i
    maps to center ``i - (nbins/2) + 0.5`` cm.
    """
    counts = {0: 100, 2: 200}
    extents = {0: 100.0, 2: 200.0}  # full width, cm
    vals: dict[int, list[float]] = {0: [], 2: []}
    rows: list[tuple[int, int, float]] = []
    with open(csv) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            p = line.strip().split(", ")
            if len(p) < 4:
                continue
            rows.append((int(p[0]), int(p[2]), float(p[3])))
            vals[0].append(int(p[0]))
            vals[2].append(int(p[2]))
    axes = {}
    for col in (0, 2):
        n = counts[col]
        axes[col] = np.array(sorted(set(vals[col]))) - n / 2 + 0.5
        assert axes[col][0] == -extents[col] / 2 + 0.5, "unexpected bin origin"
    xu, zu = axes[0], axes[2]
    m = np.zeros((len(zu), len(xu)))
    for xb, zb, v in rows:
        m[zb, xb] = v
    return xu, zu, m


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", default="Pelvis", help="imaging_mode protocol")
    parser.add_argument("--histories", default="2000000")
    parser.add_argument("--threads", default="20")
    args = parser.parse_args()

    overrides = {
        "general": {"threads": args.threads, "histories": args.histories},
        "imaging": {
            "rotation_direction": "CBCT Anticlockwise",
            "imaging_mode": args.mode,
            "sequential_times": "1",  # single angle
        },
    }
    data = load_and_patch_config(PHANTOM_CONFIG, overrides)
    temp = write_temp_config(data, f"slab_{args.mode.lower().replace(' ', '_')}")
    rundir = run_simulation(temp, OUTPUT_BASE, dry_run=True)
    swap_voxel_phantom(rundir)

    slab_file = Path(rundir) / "phantomVoxel.txt"
    backup = Path(rundir) / "phantomVoxel.txt.phantom.bak"
    backup.write_bytes(slab_file.read_bytes())
    slab_file.write_text(SLAB_TEMPLATE)
    print(f"[{args.mode}] slab written to {slab_file} (phantom backed up)")

    rc = run_topas(rundir)
    if rc != 0:
        raise SystemExit(f"TOPAS failed rc={rc}; see {rundir}/topas_ctdi.log")

    csv = Path(rundir) / "slab_tle.csv"
    xs, zs, m = load_slab_map(csv)
    peak = m.max()
    print(f"slab map peak = {peak:.3e}; nonzero bins = {(m > 0).sum()}/{m.size}")

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle(
        f"{args.mode} -- patient-plane kerma map, single angle ({args.histories} hist)",
        fontsize=11,
    )
    disp = np.where(m > 0, m / peak, np.nan)
    im = axes[0].pcolormesh(
        xs, zs, disp, cmap="inferno", shading="auto", vmin=-4, vmax=0
    )
    axes[0].set_title("X-Z kerma map (log, peak-normalized)")
    axes[0].set_xlabel("world X (cm)")
    axes[0].set_ylabel("world Z (cm)")
    axes[0].set_aspect("equal")
    fig.colorbar(im, ax=axes[0], shrink=0.8, label="log10(kerma/peak)")

    xprof = np.nansum(np.where(np.isfinite(disp), disp * peak, 0), axis=0)
    axes[1].semilogy(xs, np.maximum(xprof, xprof.max() * 1e-6))
    axes[1].set_title("X profile (sum over Z)")
    axes[1].set_xlabel("world X (cm)")
    axes[1].set_ylabel("kerma (a.u.)")

    zprof = np.nansum(np.where(np.isfinite(disp), disp * peak, 0), axis=1)
    axes[2].semilogy(zs, np.maximum(zprof, zprof.max() * 1e-6))
    axes[2].set_title("Z profile (sum over X)")
    axes[2].set_xlabel("world Z (cm)")
    axes[2].set_ylabel("kerma (a.u.)")

    out = Path(rundir) / "fluence_profiles.png"
    fig.savefig(out, dpi=140, bbox_inches="tight")
    print(f"saved {out}")
    print(f"runfolder: {rundir}")


if __name__ == "__main__":
    main()
