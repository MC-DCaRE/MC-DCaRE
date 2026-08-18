"""Compare MC absolute CAX air kerma against the measured RaySafe anchors.

Reads a ``validate_bowtie`` runfolder (``bowtie_profile.csv`` +
``simulation_metadata.yaml``), takes the profile bin nearest the bow-tie thin
axis (World Z ~ 0), and converts its TLE Sum to absolute free-in-air kerma via
the canonical normalization chain (``compute_photons_per_mAs`` +
``raw_absolute_dose_Gy`` from ``src/services/calibration.py`` -- the single
source of truth). With two or more runs supplied, also reports bow-tie
transmission ratios (field-consistent pairs), which are
normalization-independent.

Usage::

    python tools/compare_cax_kerma.py \
        --run bt=runfolder/A --run nobt=runfolder/B \
        --anchor data/measured/cax_kerma_anchors.yaml --mAs 1.6
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path
from typing import Dict, Tuple

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.services.calibration import (  # noqa: E402
    compute_photons_per_mAs,
    raw_absolute_dose_Gy,
)

logger = logging.getLogger(__name__)

_BIN_RE = re.compile(
    r"#\s+(X|Z)\s+in\s+(\d+)\s+bins?\s+of\s+([0-9.]+)\s*(mm|cm|m)", re.IGNORECASE
)


def _units_to_cm(value: float, units: str) -> float:
    if units == "mm":
        return value / 10.0
    if units == "m":
        return value * 100.0
    return value


def cax_bin(path: str) -> Tuple[float, float]:
    """Return (absolute_kerma_uGy_at_1mAs, n_active) for the CAX bin.

    The CAX bin is the row whose binned-axis position is nearest 0 (the
    bow-tie thin axis; verified for both FF and HF fields).
    """
    text = Path(path).read_text()
    binned = [
        m
        for m in (_BIN_RE.search(ln) for ln in text.splitlines())
        if m and int(m.group(2)) > 1
    ]
    if not binned:
        raise ValueError("No binned axis in %s" % path)
    m = binned[0]
    axis, n_bins, width = m.group(1).upper(), int(m.group(2)), float(m.group(3))
    width_cm = _units_to_cm(width, m.group(4))
    total = n_bins * width_cm
    col = 0 if axis == "X" else 2

    best_pos, best_sum, n_active = None, None, None
    for ln in text.splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        parts = [p.strip() for p in ln.split(",")]
        if len(parts) < 5:
            continue
        try:
            idx = int(float(parts[col]))
            val = float(parts[3])
            hist = float(parts[4])
        except ValueError:
            continue
        pos = -total / 2.0 + (idx + 0.5) * width_cm
        if best_pos is None or abs(pos) < abs(best_pos):
            best_pos, best_sum, n_active = pos, val, hist
    if best_sum is None:
        raise ValueError("No data rows parsed in %s" % path)
    return best_sum, n_active


def absolute_uGy(rundir: str, mAs: float) -> Tuple[float, float]:
    """Return (kerma_uGy_at_mAs, kerma_uGy_per_mAs) for the run's CAX bin."""
    prof = Path(rundir) / "bowtie_profile.csv"
    meta = yaml.safe_load((Path(rundir) / "simulation_metadata.yaml").read_text())
    best_sum, n_active = cax_bin(str(prof))
    ppm = compute_photons_per_mAs(meta)
    gy = raw_absolute_dose_Gy(best_sum, ppm, n_active, mAs)
    return gy * 1e6, gy * 1e6 / mAs


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run", action="append", required=True, help="label=runfolder (repeatable)"
    )
    parser.add_argument(
        "--anchor",
        default=str(PROJECT_ROOT / "data" / "measured" / "cax_kerma_anchors.yaml"),
    )
    parser.add_argument("--mAs", type=float, default=1.6)
    args = parser.parse_args()

    results: Dict[str, float] = {}
    for spec in args.run:
        label, _, rd = spec.partition("=")
        ugy, per_mAs = absolute_uGy(rd, args.mAs)
        results[label] = per_mAs
        logger.info(
            "%-12s CAX kerma = %.3f uGy @ %.2f mAs (%.3f uGy/mAs)",
            label,
            ugy,
            args.mAs,
            per_mAs,
        )

    anchors = yaml.safe_load(Path(args.anchor).read_text())
    print("\nMC absolute CAX kerma vs measured anchors (uGy @ %.2f mAs):" % args.mAs)
    for a in anchors.get("anchors", []):
        aid = a["id"]
        ref = a["dose_uGy_at_1.6mAs"]
        print(
            "  %-28s meas %7.2f  (kVp %.1f, %s, bowtie=%s, Ti=%s)"
            % (
                aid,
                ref,
                a.get("kVp_measured", 0),
                a.get("fan", ""),
                a.get("bowtie"),
                a.get("ti_filter"),
            )
        )

    pairs = [("bt", "nobt")]
    for a, b in pairs:
        if a in results and b in results:
            ratio = results[a] / results[b]
            measured = anchors.get("derived", {}).get("bowtie_cax_transmission_head")
            print("\nMC bow-tie CAX transmission (%s/%s) = %.3f" % (a, b, ratio))
            if measured:
                print("measured (Head FF 100 kV)      = %.3f" % measured)


if __name__ == "__main__":
    main()
