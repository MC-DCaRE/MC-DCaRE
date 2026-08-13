from __future__ import annotations

import csv
import os
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from tools.convert_bowtie_profile import convert, _parse_bin_geometry


def _write_topas_csv(path: str, axis: str, n_bins: int, width_cm: float) -> None:
    """Write a tiny TOPAS binned-scorer CSV (no header row; comment preamble)."""
    other = "X" if axis == "Z" else "Z"
    lines = [
        "# TOPAS Version: 4.2.p3",
        "# Results for scorer: BowtieProfile",
        "# %s in %d bins of %g cm" % (axis, n_bins, width_cm),
        "# %s in 1 bin  of 10 cm" % other,
        "# TrackLengthEstimator ( Gy ) : Sum   Histories   Count_in_Bin   Standard_Deviation",
    ]
    for i in range(n_bins):
        # dose = bin index, so we can check ordering and position maths exactly
        lines.append(
            "%d, 0, %d, %.6e, 1000, %d, 0"
            % (i if axis == "X" else 0, i if axis == "Z" else 0, float(i), i)
        )
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


def _read_out(path: str):
    rows = list(csv.reader(open(path)))
    return rows[0], [(float(r[0]), float(r[1])) for r in rows[1:]]


def test_convert_x_binning(tmp_path):
    inp = str(tmp_path / "bp.csv")
    out = str(tmp_path / "prof.csv")
    _write_topas_csv(inp, "X", n_bins=4, width_cm=2.0)
    convert(inp, out)
    header, data = _read_out(out)
    assert header == ["position_cm", "dose"]
    # HLX=4cm total (4 bins x 2cm), centred at 0 -> centres at -3,-1,+1,+3
    assert [round(p, 3) for p, _ in data] == [-3.0, -1.0, 1.0, 3.0]
    assert [d for _, d in data] == [0.0, 1.0, 2.0, 3.0]


def test_convert_z_binning(tmp_path):
    inp = str(tmp_path / "bp.csv")
    out = str(tmp_path / "prof.csv")
    _write_topas_csv(inp, "Z", n_bins=4, width_cm=2.0)
    convert(inp, out)
    _, data = _read_out(out)
    # Same geometry but binned in Z -> same positions, dose from vz column.
    assert [round(p, 3) for p, _ in data] == [-3.0, -1.0, 1.0, 3.0]
    assert [d for _, d in data] == [0.0, 1.0, 2.0, 3.0]


def test_parse_bin_geometry_picks_binned_axis(tmp_path):
    """With X in 1 bin and Z in 80 bins, the binned axis is Z."""
    inp = str(tmp_path / "bp.csv")
    _write_topas_csv(inp, "Z", n_bins=80, width_cm=0.5)
    comments, _rows = __import__(
        "tools.convert_bowtie_profile", fromlist=["load_binned_csv"]
    ).load_binned_csv(inp)
    axis, n, w, u = _parse_bin_geometry(comments)
    assert (axis, n, w, u) == ("Z", 80, 0.5, "cm")


def test_convert_mm_units(tmp_path):
    inp = str(tmp_path / "bp.csv")
    out = str(tmp_path / "prof.csv")
    # 5 mm bins -> positions must come out in cm.
    _write_topas_csv(inp, "X", n_bins=4, width_cm=0.5)  # write as cm; override below
    # rewrite header to say mm
    txt = open(inp).read().replace("X in 4 bins of 0.5 cm", "X in 4 bins of 5 mm")
    open(inp, "w").write(txt)
    convert(inp, out)
    _, data = _read_out(out)
    # 4 bins x 5 mm = 20 mm = 2 cm total -> centres at -0.75,-0.25,0.25,0.75 cm
    assert [round(p, 3) for p, _ in data] == [-0.75, -0.25, 0.25, 0.75]
