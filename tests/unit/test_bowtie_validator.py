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
    load_measured_profile,
)


def _write_measured_workbook(path, n_groups=2, header_row=13, extra_gap=False):
    """Build a tiny workbook mirroring the RaySafe 'Collated results' layout.

    Position lives in column C (header '/cm'); each mode is a 4-col group
    (Dose uGy, uGy/s, HVL, blank) starting at column E. With ``extra_gap`` the
    groups are spaced non-uniformly (an extra column between groups 0 and 1),
    matching the real workbook where Spotlight/Pelvis carry extra columns.
    """
    import openpyxl

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Collated results"
    positions = [-4, -2, 0, 2, 4]
    # Header row: '/cm' in col C, 'Dose uGy'/'uGy/s'/'HVL (mm Al)' per group.
    ws.cell(row=header_row, column=3, value="/cm")
    col = 5  # column E
    group_cols = []
    for g in range(n_groups):
        ws.cell(row=header_row, column=col, value="Dose uGy")
        ws.cell(row=header_row, column=col + 1, value="uGy/s")
        ws.cell(row=header_row, column=col + 2, value="HVL (mm Al)")
        group_cols.append(col)
        col += 4
        if extra_gap and g == 0:
            col += 1  # non-uniform spacing between group 0 and 1
    for i, pos in enumerate(positions, start=header_row + 1):
        ws.cell(row=i, column=3, value=pos)
        for g in range(n_groups):
            dose = 10 * (g + 1) + pos
            hvl = 7.0 + g + 0.01 * abs(pos)
            ws.cell(row=i, column=group_cols[g], value=dose)
            ws.cell(row=i, column=group_cols[g] + 2, value=hvl)
    wb.save(path)
    return positions


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


def test_load_measured_profile_selects_mode_group(tmp_path):
    xlsx = tmp_path / "meas.xlsx"
    positions = _write_measured_workbook(str(xlsx), n_groups=2)

    g0 = load_measured_profile(str(xlsx), mode_group=0)
    g1 = load_measured_profile(str(xlsx), mode_group=1)

    # Positions sorted ascending; matches what was written.
    assert g0.position_cm.tolist() == sorted(positions)
    assert g1.position_cm.tolist() == sorted(positions)
    # Group 1 doses are offset by +10 vs group 0 at every position.
    assert np.allclose(g1.dose - g0.dose, 10.0)
    # HVL columns differ between groups (group1 HVL ~ 1 higher).
    assert (g1.hvl_mmAl > g0.hvl_mmAl).all()


def test_load_measured_profile_normalises_order(tmp_path):
    xlsx = tmp_path / "meas.xlsx"
    _write_measured_workbook(str(xlsx), n_groups=1)
    prof = load_measured_profile(str(xlsx), mode_group=0)
    # Positions must be ascending (the loader sorts).
    assert all(
        prof.position_cm[i] <= prof.position_cm[i + 1]
        for i in range(len(prof.position_cm) - 1)
    )


def test_load_measured_profile_non_uniform_spacing(tmp_path):
    """Groups are not always 4 columns apart (Spotlight/Pelvis carry extra
    columns). The loader must find 'Dose uGy' columns by scanning the header,
    not by a fixed 4-column offset."""
    xlsx = tmp_path / "meas.xlsx"
    _write_measured_workbook(str(xlsx), n_groups=2, extra_gap=True)

    g0 = load_measured_profile(str(xlsx), mode_group=0)
    g1 = load_measured_profile(str(xlsx), mode_group=1)
    # Group 1 doses are offset by +10 vs group 0 at every position, even though
    # group 1 is 5 columns (not 4) after group 0. A fixed-offset reader would
    # read the wrong column and fail this.
    assert np.allclose(g1.dose - g0.dose, 10.0)
    assert (g1.hvl_mmAl > g0.hvl_mmAl).all()


def test_load_measured_profile_mode_group_out_of_range(tmp_path):
    xlsx = tmp_path / "meas.xlsx"
    _write_measured_workbook(str(xlsx), n_groups=2)
    with pytest.raises(ValueError, match="out of range"):
        load_measured_profile(str(xlsx), mode_group=5)
