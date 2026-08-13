"""Convert a TOPAS binned bow-tie profile scorer CSV to a 2-column profile.

The ``BowtieProfile`` scorer (``TrackLengthEstimator`` on a thin air slab at
isocenter, 1-D X-binned) writes a TOPAS binned CSV with NO header row. Each
data line is ``voxel_x, voxel_y, voxel_z, Sum, [Histories, Count_In_Bin, ...]``.
The voxel_x is a bin *index*, not a position; the bin geometry is declared in a
``# X in N bins of W cm`` comment line.

This tool recovers the cross-plane position from the bin index (slab centred at
TransX=0, so x_i = -(N*W)/2 + (i+0.5)*W), takes the ``Sum`` column as the dose,
and writes a 2-column ``(position_cm, dose)`` CSV that
``src/services/bowtie_validator.load_mc_profile`` and
``tools/validate_bowtie.py`` consume.

Usage::

    python tools/convert_bowtie_profile.py \\
        --input runfolder/bowtie_profile.csv \\
        --output runfolder/profile.csv

If the scorer emitted one file per sequential time, pass a glob via ``--input``
and the doses are summed across files.
"""

from __future__ import annotations

import argparse
import csv
import glob
import logging
import os
import re

import numpy as np

logger = logging.getLogger(__name__)

# Matches "# X in 80 bins of 0.5 cm" or "# Z in 80 bins of 0.5 cm" (also mm, m).
_BIN_RE = re.compile(
    r"#\s*(X|Z)\s+in\s+(\d+)\s+bins?\s+of\s+([0-9.]+)\s*(mm|cm|m)\b", re.IGNORECASE
)


def _parse_bin_geometry(lines: list[str]) -> tuple[str, int, float, str]:
    """Return (axis, n_bins, bin_width, units) for the binned lateral axis.

    The BowtieProfileSlab bins one lateral axis (X or Z); TOPAS writes a
    ``# <axis> in N bins of W <units>`` comment per axis. The binned axis is the
    one with N > 1 (the others are "in 1 bin").
    """
    found: list[tuple[str, int, float, str]] = []
    for line in lines:
        m = _BIN_RE.search(line)
        if m:
            found.append(
                (
                    m.group(1).upper(),
                    int(m.group(2)),
                    float(m.group(3)),
                    m.group(4).lower(),
                )
            )
    if not found:
        raise ValueError(
            "Could not find '# X|Z in N bins of W <units>' comment in the TOPAS CSV. "
            "Cannot recover bin positions."
        )
    # Pick the axis with more than one bin (the actual profile axis).
    binned = [f for f in found if f[1] > 1]
    if not binned:
        raise ValueError("No binned axis (N>1) found in TOPAS CSV; got %r" % found)
    return binned[0]


def _units_to_cm(value: float, units: str) -> float:
    if units == "mm":
        return value / 10.0
    if units == "m":
        return value * 100.0
    return value


def load_binned_csv(path: str) -> tuple[list[str], list[list[str]]]:
    """Return (comment_lines, data_rows) from a TOPAS binned scorer CSV.

    ``#`` lines are comments (parsed separately); the remaining non-empty lines
    are data rows (TOPAS emits no column-header row for binned scorers).
    """
    comments: list[str] = []
    rows: list[list[str]] = []
    with open(path, newline="") as f:
        for line in f:
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("#"):
                comments.append(stripped)
                continue
            rows.append([c.strip() for c in stripped.split(",")])
    return comments, rows


def convert(
    input_pattern: str,
    output: str,
    dose_col_idx: int = 3,
) -> str:
    """Convert one or more TOPAS binned CSVs to a 2-column profile CSV.

    Sums dose across multiple files (e.g. per-sequential-time outputs). Bin
    geometry is read from the first file's comment header.
    """
    paths = sorted(glob.glob(input_pattern))
    if not paths and os.path.isfile(input_pattern):
        paths = [input_pattern]
    if not paths:
        raise FileNotFoundError("No input CSVs matched %s" % input_pattern)

    comments, first_rows = load_binned_csv(paths[0])
    axis, n_bins, width_raw, units = _parse_bin_geometry(comments)
    width_cm = _units_to_cm(width_raw, units)
    total_cm = n_bins * width_cm
    # Voxel index column: 0 for X-binning, 2 for Z-binning (vx, vy, vz).
    voxel_idx_col = 0 if axis == "X" else 2
    logger.info(
        "Bin geometry: %s in %d bins x %.4g %s (total %.3f cm, centred at 0)",
        axis,
        n_bins,
        width_raw,
        units,
        total_cm,
    )

    # Accumulate dose across files (sum), keyed by voxel index along the binned axis.
    idx_to_dose: dict[int, float] = {}
    for path in paths:
        _, rows = (comments, first_rows) if path == paths[0] else load_binned_csv(path)
        for row in rows:
            if len(row) <= max(voxel_idx_col, dose_col_idx):
                continue
            try:
                vi = int(float(row[voxel_idx_col]))
                d = float(row[dose_col_idx])
            except ValueError:
                continue
            idx_to_dose[vi] = idx_to_dose.get(vi, 0.0) + d

    indices = np.array(sorted(idx_to_dose))
    # x_i = -(total/2) + (i + 0.5) * width  (slab centred at TransX=0)
    positions = -total_cm / 2.0 + (indices + 0.5) * width_cm
    doses = np.array([idx_to_dose[i] for i in indices])

    with open(output, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["position_cm", "dose"])
        for p, d in zip(positions, doses):
            w.writerow(["%.4f" % p, "%.6e" % d])
    peak = float(doses.max()) if doses.size else 0.0
    logger.info(
        "Wrote %d-point profile to %s (peak=%.4e, CAX bin dose=%.4e)",
        len(positions),
        output,
        peak,
        float(idx_to_dose.get(n_bins // 2, 0.0)),
    )
    return output


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
    parser = argparse.ArgumentParser(
        description="Convert a TOPAS binned bow-tie profile CSV to (position_cm, dose)."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="TOPAS binned scorer CSV (or glob, e.g. bowtie_profile*.csv)",
    )
    parser.add_argument("--output", required=True, help="2-column output CSV path")
    parser.add_argument(
        "--dose-col-idx",
        type=int,
        default=3,
        help="0-based index of the dose (Sum) column (default 3: voxel_x,y,z,Sum)",
    )
    args = parser.parse_args()
    convert(args.input, args.output, dose_col_idx=args.dose_col_idx)


if __name__ == "__main__":
    main()
