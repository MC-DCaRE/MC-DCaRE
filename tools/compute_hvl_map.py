"""Compute the MC HVL(Z) wedge map from an energy-binned validate_bowtie run.

Parses the ``validate_bowtie_hvlmap`` scorer output (40 Z bins x 150 x 1 keV
energy columns per row), folds each Z row's fluence spectrum with NIST
mu_en/rho(air) + mu/rho(Al) via ``PhaseSpaceAnalyzer.compute_hvl_mm_al``, and
compares against (a) the measured RaySafe per-position HVL array and (b) a
geometry-only prediction obtained by folding a scored no-bow-tie CAX spectrum
through the STL ray-cast chord thickness (bow-tie plane Z = iso Z x 0.18).

Usage::

    python tools/compute_hvl_map.py --run runfolder/<hvlmap-run> \
        --nobt-spectrum runfolder/<nobt-run>/cax_spectrum.csv \
        --measured-mode-group 0
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.services.phase_space_analyzer import PhaseSpaceAnalyzer  # noqa: E402

logger = logging.getLogger(__name__)

NIST = str(PROJECT_ROOT / "data" / "nist" / "hvl_coefficients.dat")
MEASURED = (
    "research/2023 - CBCT Dose PCXMC/"
    "New results Oct 2023 (Spotlight, Raysafe X2) - fixed spotlight.xlsx"
)

_Z_RE = re.compile(r"#\s+Z\s+in\s+(\d+)\s+bins?\s+of\s+([0-9.]+)\s*(cm|mm|m)")
_E_RE = re.compile(
    r"#\s+Binned by incident track energy in (\d+) bins of ([0-9.e+-]+) (MeV|keV)"
)


def parse_map(path: str) -> Tuple[int, float, int, float, List[List[float]]]:
    """Return (n_z, z_width_cm, n_e, e_width_mev, per-Z spectra)."""
    text = Path(path).read_text()
    mz = _Z_RE.search(text)
    me = _E_RE.search(text)
    if not mz or not me:
        raise ValueError("Not an energy-binned bowtie_profile.csv")
    n_z, z_w = int(mz.group(1)), float(mz.group(2))
    z_w = (
        z_w / 10.0
        if mz.group(3) == "mm"
        else z_w * (100.0 if mz.group(3) == "m" else 1.0)
    )
    n_e, e_w = int(me.group(1)), float(me.group(2))
    if me.group(3) == "keV":
        e_w = e_w / 1000.0
    spectra: List[List[float]] = []
    for ln in text.splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        parts = [p.strip() for p in ln.split(",")]
        if len(parts) < (n_e + 3) * 4:
            continue
        try:
            float(parts[0])
        except ValueError:
            continue
        # Row layout: no spatial prefix; (n_e + 3) energy groups x 4 columns
        # (Sum, Histories, Count, StdDev). Group 0 is underflow, next-to-last
        # overflow, last no-track -- real bins are groups 1..n_e.
        sums = [float(parts[4 * k]) for k in range(n_e + 3)]
        spectra.append(sums)
    if len(spectra) != n_z:
        raise ValueError("expected %d Z rows, got %d" % (n_z, len(spectra)))
    return n_z, z_w, n_e, e_w, spectra


def hvl_per_z(n_e: int, e_w: float, spectra: List[List[float]]) -> List[float]:
    """Fold each Z row's real energy bins (groups 1..n_e) to HVL."""
    hvls = []
    for spec in spectra:
        real = spec[1 : n_e + 1]
        edges = [(i) * e_w * 1000.0 for i in range(len(real) + 1)]
        h = PhaseSpaceAnalyzer.compute_hvl_mm_al(edges, real, NIST)
        hvls.append(h if h is not None else float("nan"))
    return hvls


def load_nobt_spectrum(path: str) -> Tuple[np.ndarray, np.ndarray]:
    from tools.compute_cax_hvl import parse_cax_spectrum

    n, w, e_min, vals = parse_cax_spectrum(path)
    real = np.asarray(vals[1 : n + 1])
    edges = (e_min + np.arange(n + 1) * w) * 1000.0
    centers = 0.5 * (edges[:-1] + edges[1:])
    return centers, real


def geometry_hvl(
    centers_kev: np.ndarray, fluence: np.ndarray, chord_mm: float
) -> float:
    table = np.loadtxt(NIST, comments="#")
    muen = np.interp(centers_kev / 1000.0, table[:, 0], table[:, 1])
    mu_al = np.interp(centers_kev / 1000.0, table[:, 0], table[:, 2]) * 2.70
    att = np.exp(-mu_al * chord_mm / 10.0)
    k = fluence * muen * att
    cum = np.cumsum(k)
    if cum[-1] <= 0:
        return float("nan")
    i = int(np.searchsorted(cum, 0.5 * cum[-1]))
    mu_here = mu_al[i]  # cm^-1
    return 0.693 / mu_here * 10.0  # mm Al


def raycast_chord_mm(z_bt_mm: float) -> float:
    """Chord through fullfan.stl along the beam at wedge position z_bt_mm."""
    import struct

    stl = PROJECT_ROOT / "src/boilerplates/TOPAS_includeFiles/fullfan.stl"
    with open(stl, "rb") as f:
        f.read(80)
        n = struct.unpack("<I", f.read(4))[0]
        data = np.frombuffer(f.read(n * 50), dtype=np.uint8).reshape(n, 50)
    tri = data[:, 12:48].copy().view(np.float32).reshape(-1, 3, 3).astype(np.float64)
    d = np.array([1.0, 0.0, 0.0])
    o = np.array([-1e4, 0.0, z_bt_mm])
    v0, v1, v2 = tri[:, 0], tri[:, 1], tri[:, 2]
    e1, e2 = v1 - v0, v2 - v0
    h = np.cross(d, e2)
    a = np.einsum("ij,ij->i", e1, h)
    m = np.abs(a) > 1e-12
    f = np.zeros_like(a)
    f[m] = 1.0 / a[m]
    s = o - v0
    u = f * np.einsum("ij,ij->i", s, h)
    q = np.cross(s, e1)
    v = f * np.einsum("j,ij->i", d, q)
    t = f * np.einsum("ij,ij->i", e2, q)
    hit = m & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > 0)
    ts = np.sort(t[hit])
    return float(ts[-1] - ts[0]) if len(ts) >= 2 else 0.0


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True, help="hvlmap runfolder")
    parser.add_argument("--nobt-spectrum", default="")
    parser.add_argument("--measured-mode-group", type=int, default=0)
    parser.add_argument("--out", default="")
    args = parser.parse_args()

    n_z, z_w, n_e, e_w, spectra = parse_map(str(Path(args.run) / "bowtie_profile.csv"))
    hvls = hvl_per_z(n_e, e_w, spectra)
    total = n_z * z_w

    from src.services.bowtie_validator import load_measured_profile

    meas = load_measured_profile(str(PROJECT_ROOT / MEASURED), args.measured_mode_group)

    centers, fluence = (None, None)
    if args.nobt_spectrum:
        centers, fluence = load_nobt_spectrum(args.nobt_spectrum)

    rows: List[Dict[str, float]] = []
    for i, h in enumerate(hvls):
        z_iso = -total / 2.0 + (i + 0.5) * z_w
        m_here = float("nan")
        j = int(np.argmin(np.abs(meas.position_cm - z_iso)))
        if abs(meas.position_cm[j] - z_iso) <= z_w:
            m_here = meas.hvl_mmAl[j]
        g_here = float("nan")
        if centers is not None:
            g_here = geometry_hvl(
                centers, fluence, raycast_chord_mm(z_iso * 10.0 * 0.18)
            )
        rows.append(
            {
                "z_cm": z_iso,
                "mc_hvl_mmAl": h,
                "measured_hvl_mmAl": m_here,
                "geometry_pred_hvl_mmAl": g_here,
            }
        )

    out = args.out or str(Path(args.run) / "hvl_map.csv")
    with open(out, "w") as f:
        f.write("z_cm,mc_hvl_mmAl,measured_hvl_mmAl,geometry_pred_hvl_mmAl\n")
        for r in rows:
            f.write(
                "%.2f,%.3f,%s,%s\n"
                % (
                    r["z_cm"],
                    r["mc_hvl_mmAl"],
                    ""
                    if np.isnan(r["measured_hvl_mmAl"])
                    else "%.3f" % r["measured_hvl_mmAl"],
                    ""
                    if np.isnan(r["geometry_pred_hvl_mmAl"])
                    else "%.3f" % r["geometry_pred_hvl_mmAl"],
                )
            )
    logger.info("Wrote %s", out)

    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(
            [r["z_cm"] for r in rows],
            [r["mc_hvl_mmAl"] for r in rows],
            "s-",
            label="MC HVL(Z)",
            ms=3,
        )
        mz = [
            (p, h) for p, h in zip(meas.position_cm, meas.hvl_mmAl) if not np.isnan(h)
        ]
        ax.plot(
            [p for p, _ in mz], [h for _, h in mz], "k*-", label="measured HVL(Z)", ms=7
        )
        gz = [
            (r["z_cm"], r["geometry_pred_hvl_mmAl"])
            for r in rows
            if not np.isnan(r["geometry_pred_hvl_mmAl"])
        ]
        ax.plot(
            [p for p, _ in gz],
            [h for _, h in gz],
            "d--",
            label="STL ray-cast prediction",
            ms=3,
        )
        ax.set_xlabel("Lateral position (cm)")
        ax.set_ylabel("HVL (mm Al)")
        ax.set_title("Bow-tie HVL(Z) wedge map: MC vs measured vs STL geometry")
        ax.legend()
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(str(Path(args.run) / "hvl_map.png"), dpi=120)
        logger.info("Wrote %s", str(Path(args.run) / "hvl_map.png"))
    except Exception as e:  # pragma: no cover
        logger.warning("plot skipped: %s", e)

    # Console summary at measured positions
    print("\n  Z_cm   MC_HVL  meas_HVL  geom_pred")
    for r in rows:
        if not np.isnan(r["measured_hvl_mmAl"]):
            print(
                "  %5.1f   %6.2f  %8.2f  %s"
                % (
                    r["z_cm"],
                    r["mc_hvl_mmAl"],
                    r["measured_hvl_mmAl"],
                    "%.2f" % r["geometry_pred_hvl_mmAl"]
                    if not np.isnan(r["geometry_pred_hvl_mmAl"])
                    else "-",
                )
            )


if __name__ == "__main__":
    main()
