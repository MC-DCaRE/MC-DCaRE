"""Compute the MC CAX HVL (mm Al) from a scored cax_spectrum CSV.

Folds the energy-binned CAX fluence histogram (``cax_spectrum.csv`` from the
``validate_bowtie`` block in ``ctdi_phsp_score.j2``) with NIST mu_en/rho(air)
and mu/rho(Al) via ``PhaseSpaceAnalyzer.compute_hvl_mm_al``, then compares to
the measured RaySafe CAX HVL.

The TOPAS energy-binned CSV layout is a single row of N values where the first
entry is the underflow bin, the next-to-last is overflow and the last is the
"no incident track" slot (per the file's own header comment). Real spectrum
bins are indices 1..N-3. The one-bin indexing ambiguity (<= 1 keV) is bounded
by also folding the naive all-N-bins mapping and reporting the spread.

Usage::

    python tools/compute_cax_hvl.py runfolder/<ts>/cax_spectrum.csv \
        [--measured 7.37] [--nist data/nist/hvl_coefficients.dat]
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.services.phase_space_analyzer import PhaseSpaceAnalyzer  # noqa: E402

logger = logging.getLogger(__name__)

_BIN_RE = re.compile(
    r"#\s+Binned by incident track energy in (\d+) bins of ([0-9.e+-]+) (MeV|keV)"
    r"\s+from ([0-9.e+-]+) (MeV|keV)\s+to ([0-9.e+-]+) (MeV|keV)",
    re.IGNORECASE,
)


def _to_mev(value: float, unit: str) -> float:
    return value / 1000.0 if unit.lower() == "kev" else value


def parse_cax_spectrum(path: str) -> Tuple[int, float, float, List[float]]:
    """Return (n_bins, bin_width_MeV, e_min_MeV, values) from the CSV."""
    text = Path(path).read_text()
    m = _BIN_RE.search(text)
    if not m:
        raise ValueError("No energy-binning header found in %s" % path)
    n_bins = int(m.group(1))
    width = float(m.group(2))
    width = _to_mev(width, m.group(3))
    e_min = _to_mev(float(m.group(4)), m.group(5))
    data_line = next(
        ln for ln in text.splitlines() if ln.strip() and not ln.startswith("#")
    )
    values = [float(v) for v in data_line.split(",")]
    return n_bins, width, e_min, values


def hvl_from_values(
    n_bins: int, width: float, e_min: float, values: List[float], nist_path: str
) -> Optional[float]:
    # compute_hvl_mm_al expects bin edges in keV.
    edges_kev = [(e_min + i * width) * 1000.0 for i in range(n_bins + 1)]
    return PhaseSpaceAnalyzer.compute_hvl_mm_al(edges_kev, values, nist_path)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
    parser = argparse.ArgumentParser(description="Compute MC CAX HVL (mm Al)")
    parser.add_argument("csv", help="cax_spectrum.csv from a validate_bowtie run")
    parser.add_argument("--measured", type=float, default=7.37)
    parser.add_argument(
        "--nist", default=str(PROJECT_ROOT / "data" / "nist" / "hvl_coefficients.dat")
    )
    args = parser.parse_args()

    n_bins, width, e_min, values = parse_cax_spectrum(args.csv)
    logger.info(
        "Parsed: %d declared bins x %.4g MeV from %.4g MeV, %d values",
        n_bins,
        width,
        e_min,
        len(values),
    )

    # CSV layout (per TOPAS header comment): N real bins, with underflow
    # prepended (index 0) and overflow + "no incident track" appended. So the
    # row has N + 3 values and the real spectrum is values[1 : N+1].
    results = {}
    real = values[1 : n_bins + 1]
    results["spectrum fold"] = hvl_from_values(n_bins, width, e_min, real, args.nist)

    print("\nMC CAX HVL (mm Al):")
    for label, hvl in results.items():
        if hvl is None:
            print("  %-26s : <could not determine>" % label)
            continue
        diff = hvl - args.measured
        print(
            "  %-26s : %.2f  (measured %.2f, diff %+.2f mm Al)"
            % (label, hvl, args.measured, diff)
        )


if __name__ == "__main__":
    main()
