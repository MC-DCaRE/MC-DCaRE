from __future__ import annotations

import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.services.bowtie_validator import (
    Profile,
    compare_profiles,
    load_mc_profile,
)


def _make_csv(tmp_path, rows):
    p = tmp_path / "mc.csv"
    with open(p, "w") as f:
        f.write("position_cm,dose\n")
        for r in rows:
            f.write("%.3f,%.5f\n" % r)
    return str(p)


def test_load_mc_profile(tmp_path):
    p = _make_csv(tmp_path, [(-10, 0.2), (0, 1.0), (10, 0.2)])
    prof = load_mc_profile(p)
    assert prof.position_cm.tolist() == [-10.0, 0.0, 10.0]
    assert prof.dose.tolist() == [0.2, 1.0, 0.2]


def test_compare_identical_profiles(tmp_path):
    measured = Profile("m", np.array([-5.0, 0.0, 5.0]), np.array([0.5, 1.0, 0.5]))
    mc = Profile("mc", np.array([-5.0, 0.0, 5.0]), np.array([0.5, 1.0, 0.5]))
    out = tmp_path / "out.csv"
    res = compare_profiles(measured, mc, output_csv=str(out))
    assert res["rms_misfit"] == pytest.approx(0.0, abs=1e-9)
    assert out.exists()


def test_compare_writes_png(tmp_path):
    measured = Profile("m", np.array([-4.0, 0.0, 4.0]), np.array([0.3, 1.0, 0.3]))
    mc = Profile("mc", np.array([-4.0, 0.0, 4.0]), np.array([0.4, 1.0, 0.4]))
    png = tmp_path / "out.png"
    compare_profiles(measured, mc, output_png=str(png))
    assert png.exists() and png.stat().st_size > 0


def test_compare_interpolates_mc_onto_measured(tmp_path):
    # MC grid finer than measured; interpolation should land measured positions on the curve.
    measured = Profile("m", np.array([-2.0, 2.0]), np.array([1.0, 1.0]))
    mc = Profile("mc", np.array([-2.0, 0.0, 2.0]), np.array([1.0, 2.0, 1.0]))
    res = compare_profiles(measured, mc)
    # At +-2 cm, both measured and interpolated MC normalise to 0.5 (peak 2 at centre).
    assert res["mc_norm"][0] == pytest.approx(0.5, abs=1e-6)
