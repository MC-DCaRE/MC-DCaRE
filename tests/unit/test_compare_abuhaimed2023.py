from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from tools.compare_abuhaimed2023 import compare_effective, compare_organs, per_100mAs


def test_per_100mAs_normalization() -> None:
    assert per_100mAs(1.19, 100.0) == pytest.approx(1.19)
    assert per_100mAs(3.04, 1074.0) == pytest.approx(0.2831, abs=1e-4)
    assert per_100mAs(2.0, 50.0) == pytest.approx(4.0)


def _write_sweep(tmp_path: Path) -> str:
    p = tmp_path / "validation_results.csv"
    p.write_text(
        "protocol,status,kV,fan,mAs,e_sim_mSv,e_ref_mSv,diff_pct,rundir\n"
        "Thorax,ok,125,Half Fan,268.5,2.04,1.3,57,x\n"
        "Pelvis,ok,125,Half Fan,1074.0,3.04,4.2,-28,x\n"
        "Head,ok,100,Full Fan,150.3,0.30,0.5,-40,x\n"  # not in scan classes
        "4D Thorax,failed,125,Half Fan,671.2,9.9,3.3,999,x\n"  # failed -> skipped
    )
    return str(p)


def test_compare_effective_maps_and_filters(tmp_path: Path) -> None:
    rows = compare_effective(Path(_write_sweep(tmp_path)))
    protos = {r["protocol"] for r in rows}
    assert protos == {"Thorax", "Pelvis"}  # Head unmapped, failed run skipped
    by = {r["protocol"]: r for r in rows}
    assert by["Thorax"]["class"] == "chest"
    assert by["Thorax"]["ours_mSv_per_100mAs"] == pytest.approx(0.7598, abs=1e-3)
    assert by["Thorax"]["lit_mSv_per_100mAs"] == 2.07
    assert by["Pelvis"]["lit_mSv_per_100mAs"] == 1.19
    assert by["Thorax"]["primary"] is True


def test_compare_organs_missing_file(tmp_path: Path) -> None:
    assert compare_organs(tmp_path / "nope.csv", "pelvis", 1074.0) is None


def test_compare_organs_per_100mAs(tmp_path: Path) -> None:
    p = tmp_path / "organ_doses.csv"
    p.write_text(
        "organ,mean_mGy,icrp103_tissue\n"
        "Bladder wall,2.84,urinary_bladder\n"  # matches lit 2.84 at 100 mAs
        "Kidney L,0.34,kidneys\n"
        "Kidney R,0.34,kidneys\n"
    )
    rows = compare_organs(p, "pelvis", 1074.0)
    assert rows is not None
    by = {r["organ"]: r for r in rows}
    # literature display names are matched against our snake_case tissues
    assert by["Urinary bladder"]["ours_mGy_per_100mAs"] == pytest.approx(
        2.84 / 1074.0 * 100.0, abs=1e-3
    )
    # kidneys mean of (0.34, 0.34) -> same value; lit 0.17
    assert by["Kidneys"]["lit_mGy_per_100mAs"] == 0.17
    assert by["Kidneys"]["ours_mGy_per_100mAs"] == pytest.approx(
        0.34 / 1074.0 * 100.0, abs=1e-3
    )
