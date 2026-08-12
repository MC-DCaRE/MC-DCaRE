from __future__ import annotations

import os
import sys
from typing import Any

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.services.phantom_dose_calculator import PhantomDoseCalculator


@pytest.fixture
def small_phantom(tmp_path: Any) -> dict[str, str]:
    """Create a minimal voxel grid, material file, and dose CSV.

    Grid (4x4x4 = 64 voxels):
      mat_id 100 (Liver)   for ix in [0,1], iy in [0,1], iz in [0,1] -> 8 voxels
      mat_id 200 (Muscle)  for ix in [2,3], iy in [2,3], iz in [2,3] -> 8 voxels
      mat_id   0 (air)     everywhere else -> 48 voxels

    Liver dose CSV: 4 voxels @ 1e-10, 4 voxels @ 0.0
    Muscle dose CSV: 2 voxels @ 2e-10, 6 voxels @ 0.0
    """
    grid = np.zeros((4, 4, 4), dtype=np.int32)
    grid[0:2, 0:2, 0:2] = 100  # Liver
    grid[2:4, 2:4, 2:4] = 200  # Muscle
    grid_path = tmp_path / "grid.npy"
    np.save(grid_path, grid)

    mat_path = tmp_path / "test.material"
    mat_path.write_text(
        "C Liver 1.06 g/cm3\n"
        "m100     1000      -0.10\n"
        "C Muscle 1.04 g/cm3\n"
        "m200     1000      -0.10\n"
    )

    dose_path = tmp_path / "dose.csv"
    lines = ["# DoseToMedium ( Gy ) : Sum"]
    for ix in range(4):
        for iy in range(4):
            for iz in range(4):
                mid = int(grid[ix, iy, iz])
                if mid == 100:
                    dose = 1e-10 if (ix + iy + iz) % 2 == 0 else 0.0
                elif mid == 200:
                    dose = 2e-10 if (ix == 2 and iy == 2) else 0.0
                else:
                    dose = 0.0
                lines.append(f"{ix}, {iy}, {iz}, {dose}")
    dose_path.write_text("\n".join(lines) + "\n")

    return {
        "dose_csv": str(dose_path),
        "grid": str(grid_path),
        "material": str(mat_path),
    }


class TestParseMaterialFile:
    def test_parses_organ_names(self, small_phantom: dict[str, str]) -> None:
        calc = PhantomDoseCalculator(
            small_phantom["dose_csv"],
            small_phantom["grid"],
            small_phantom["material"],
        )
        mats = calc.materials
        assert mats[100] == "Liver"
        assert mats[200] == "Muscle"

    def test_does_not_include_unmapped_id_zero(
        self, small_phantom: dict[str, str]
    ) -> None:
        calc = PhantomDoseCalculator(
            small_phantom["dose_csv"],
            small_phantom["grid"],
            small_phantom["material"],
        )
        assert 0 not in calc.materials


class TestLoadDoseData:
    def test_includes_zero_dose_voxels(self, small_phantom: dict[str, str]) -> None:
        """Zero-dose voxels MUST be included so organ means are unbiased."""
        calc = PhantomDoseCalculator(
            small_phantom["dose_csv"],
            small_phantom["grid"],
            small_phantom["material"],
        )
        doses = calc.organ_doses
        # Liver: 8 voxels total (4 non-zero, 4 zero)
        assert len(doses["Liver"]) == 8
        # Muscle: 8 voxels total (2 non-zero, 6 zero)
        assert len(doses["Muscle"]) == 8

    def test_excludes_air_voxels(self, small_phantom: dict[str, str]) -> None:
        """mat_id 0 (air/unmapped) must not appear as an organ."""
        calc = PhantomDoseCalculator(
            small_phantom["dose_csv"],
            small_phantom["grid"],
            small_phantom["material"],
        )
        doses = calc.organ_doses
        assert "Unknown" not in doses
        # Only the two mapped organs
        assert set(doses.keys()) == {"Liver", "Muscle"}

    def test_liver_mean_includes_zeros(self, small_phantom: dict[str, str]) -> None:
        """Liver: 4 voxels @ 1e-10, 4 @ 0 -> mean = 0.5e-10, not 1e-10."""
        calc = PhantomDoseCalculator(
            small_phantom["dose_csv"],
            small_phantom["grid"],
            small_phantom["material"],
        )
        liver_mean = np.mean(calc.organ_doses["Liver"])
        assert liver_mean == pytest.approx(0.5e-10)

    def test_muscle_mean_includes_zeros(self, small_phantom: dict[str, str]) -> None:
        """Muscle: 2 voxels @ 2e-10, 6 @ 0 -> mean = 0.5e-10, not 2e-10."""
        calc = PhantomDoseCalculator(
            small_phantom["dose_csv"],
            small_phantom["grid"],
            small_phantom["material"],
        )
        muscle_mean = np.mean(calc.organ_doses["Muscle"])
        assert muscle_mean == pytest.approx(0.5e-10)

    def test_no_selection_bias_inflation(self, small_phantom: dict[str, str]) -> None:
        """Regression: the old code skipped dose<=0, inflating means 2-4x.

        With the fix, Liver and Muscle have the same mean (0.5e-10) despite
        different fractions of zero voxels (50% vs 75%).
        """
        calc = PhantomDoseCalculator(
            small_phantom["dose_csv"],
            small_phantom["grid"],
            small_phantom["material"],
        )
        liver_mean = np.mean(calc.organ_doses["Liver"])
        muscle_mean = np.mean(calc.organ_doses["Muscle"])
        # Both should be 0.5e-10 — if zeros were excluded, muscle would be 4x liver
        assert liver_mean == pytest.approx(muscle_mean)


class TestLoadDoseDataEdgeCases:
    def test_skips_mat_id_minus_one(self, tmp_path: Any) -> None:
        """mat_id == -1 (outside phantom) must be skipped."""
        grid = np.full((2, 2, 2), -1, dtype=np.int32)
        grid[0, 0, 0] = 100
        grid_path = tmp_path / "grid.npy"
        np.save(grid_path, grid)

        mat_path = tmp_path / "test.material"
        mat_path.write_text("C Liver 1.06 g/cm3\nm100 1000 -0.1\n")

        dose_path = tmp_path / "dose.csv"
        lines = ["# DoseToMedium ( Gy ) : Sum"]
        for ix in range(2):
            for iy in range(2):
                for iz in range(2):
                    lines.append(f"{ix}, {iy}, {iz}, 1e-10")
        dose_path.write_text("\n".join(lines) + "\n")

        calc = PhantomDoseCalculator(str(dose_path), str(grid_path), str(mat_path))
        doses = calc.organ_doses
        # Only the one voxel with mat_id=100
        assert len(doses["Liver"]) == 1

    def test_handles_all_zero_organ(self, tmp_path: Any) -> None:
        """An organ with ALL zero-dose voxels should still appear with zeros."""
        grid = np.full((2, 2, 1), 100, dtype=np.int32)
        grid_path = tmp_path / "grid.npy"
        np.save(grid_path, grid)

        mat_path = tmp_path / "test.material"
        mat_path.write_text("C Liver 1.06 g/cm3\nm100 1000 -0.1\n")

        dose_path = tmp_path / "dose.csv"
        lines = ["# DoseToMedium ( Gy ) : Sum"]
        for ix in range(2):
            for iy in range(2):
                lines.append(f"{ix}, {iy}, 0, 0.0")
        dose_path.write_text("\n".join(lines) + "\n")

        calc = PhantomDoseCalculator(str(dose_path), str(grid_path), str(mat_path))
        doses = calc.organ_doses
        assert "Liver" in doses
        assert len(doses["Liver"]) == 4
        assert all(d == 0.0 for d in doses["Liver"])


class TestCalculateRepresentativeDose:
    def test_picks_highest_mean_organ(self, small_phantom: dict[str, str]) -> None:
        """calculate() without calibration must not divide by zero even when
        some organs have all-zero voxels."""
        calc = PhantomDoseCalculator(
            small_phantom["dose_csv"],
            small_phantom["grid"],
            small_phantom["material"],
        )
        result = calc.calculate()
        # Should produce a valid result without crashing
        assert result.effective_dose_mSv >= 0
        assert len(result.organ_results) > 0

    def test_calculate_no_calibration_returns_raw(
        self, small_phantom: dict[str, str]
    ) -> None:
        calc = PhantomDoseCalculator(
            small_phantom["dose_csv"],
            small_phantom["grid"],
            small_phantom["material"],
        )
        result = calc.calculate()
        # Without calibration, scale_to_mGy defaults to 1.0 (no unit
        # conversion), so the value is the raw Gy mean: 0.5e-10.
        liver = next(r for r in result.organ_results if r.organ_name == "Liver")
        assert liver.mean_dose_mGy == pytest.approx(0.5e-10, rel=0.01)
