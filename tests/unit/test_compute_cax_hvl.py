from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from tools.compute_cax_hvl import hvl_from_values, parse_cax_spectrum


HEADER = """# TOPAS Version: 4.2.p3
# Results for scorer: CaxSpectrum
# Scored in component: CaxSlab
# Fluence ( /mm2 ) : Sum
# Binned by incident track energy in {n} bins of 0.001 MeV from 0 MeV to 0.15 MeV
# First bin is underflow, next to last bin is overflow, last bin is for case of no incident track.
"""


def _write_csv(tmp_path: Path, n_bins: int, values: list[float]) -> str:
    p = tmp_path / "cax_spectrum.csv"
    p.write_text(HEADER.format(n=n_bins) + ",".join(repr(v) for v in values) + "\n")
    return str(p)


def test_parse_cax_spectrum_layout(tmp_path: Path) -> None:
    # 150 declared bins -> row has 153 values (underflow + 150 + overflow + no-track)
    values = [0.0] + [1.0] * 150 + [0.0, 0.0]
    path = _write_csv(tmp_path, 150, values)
    n, width, e_min, vals = parse_cax_spectrum(path)
    assert n == 150
    assert width == pytest.approx(0.001)
    assert e_min == pytest.approx(0.0)
    assert len(vals) == 153


def test_monoenergetic_60kev_hvl(tmp_path: Path) -> None:
    # 150 x 1 keV bins; all fluence in the 60 keV bin (index 60 of the real bins).
    real = [0.0] * 150
    real[60] = 100.0
    values = [0.0] + real + [0.0, 0.0]
    path = _write_csv(tmp_path, 150, values)
    n, width, e_min, vals = parse_cax_spectrum(path)
    hvl = hvl_from_values(
        n, width, e_min, vals[1 : n + 1], "data/nist/hvl_coefficients.dat"
    )
    # ln2 / (mu/rho_Al at 60 keV = 0.2778 cm^2/g * 2.70 g/cm^3) ~ 0.92 cm... in mm:

    expected = 0.693 / (0.2778 * 2.70) * 10.0
    assert hvl is not None
    assert hvl == pytest.approx(expected, rel=0.05)
    # Sanity: near the known ~9.2 mm Al for 60 keV monoenergetic.
    assert 8.5 < hvl < 10.0


def test_real_scored_spectrum_roundtrip() -> None:
    # Smoke against a committed validation spectrum (TsCAD FF, 8M histories).
    path = (
        Path(__file__).resolve().parent.parent.parent
        / "docs"
        / "bowtie_validation"
        / "profiles"
        / "cax_spectrum_tscad_ff.csv"
    )
    if not path.exists():
        pytest.skip("committed cax_spectrum_tscad_ff.csv not present")
    n, width, e_min, vals = parse_cax_spectrum(str(path))
    hvl = hvl_from_values(
        n, width, e_min, vals[1 : n + 1], "data/nist/hvl_coefficients.dat"
    )
    assert hvl is not None
    # The documented result for this spectrum is 7.80 mm Al.
    assert hvl == pytest.approx(7.80, abs=0.05)
