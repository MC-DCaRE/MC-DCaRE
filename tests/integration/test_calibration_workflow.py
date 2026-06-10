"""Integration test for the full dose calibration workflow.

Exercises: SpectrumGenerator metadata output -> CTDICalculator reads metadata
-> CalibrationService computes DCF and applies calibration with mAs scaling.
Also verifies backward compatibility with old-format runfolders.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.services.calibration import CalibrationService
from src.services.ctdi_calculator import CTDICalculator


class MockSpek:
    """Minimal SpekPy mock matching SpectrumGenerator test convention."""

    class _State:
        def get_current_state_str(self, mode: str, results: object) -> str:
            return "Integration test state"

    def __init__(self, **kwargs: object) -> None:
        self.state = self._State()

    def get_flu(self) -> float:
        return 5000.0

    def get_spectrum(self, edges: bool = False, diff: bool = False) -> tuple:
        import numpy as np

        return np.array([10.0, 20.0]), np.array([100.0, 200.0])

    def get_std_results(self) -> object:
        class R:
            pass

        return R()


def _make_calibration_yaml(path: Path) -> Path:
    data = {
        "machine": "IntegrationTestMachine",
        "date_calibrated": "2026-06-10",
        "calibrations": [
            {
                "kV": 100,
                "fan_mode": "Full Fan",
                "reference_mAs": 100,
                "measured_ctdi_w_mGy": None,
                "dcf": None,
            },
            {
                "kV": 120,
                "fan_mode": "Full Fan",
                "reference_mAs": 100,
                "measured_ctdi_w_mGy": None,
                "dcf": None,
            },
        ],
    }
    path.write_text(yaml.dump(data, default_flow_style=False, sort_keys=False))
    return path


def _make_runfolder_with_metadata(
    tmp_path: Path,
    mAs: float = 100.0,
    kV: float = 100.0,
) -> Path:
    """Create a runfolder with simulation_metadata.yaml and chamber plug CSVs."""
    rf = tmp_path / "runfolder"
    rf.mkdir()

    tmp_dir = tmp_path / "tmp"
    tmp_dir.mkdir(exist_ok=True)

    from src.spectrum_generator import SpectrumGenerator

    with patch("src.spectrum_generator.sp") as mock_sp:
        mock_sp.Spek.return_value = MockSpek()
        mock_sp.__version__ = "2.0.1"
        SpectrumGenerator.generate(
            kV,
            mAs,
            "1000",
            str(tmp_path),
            fan_mode="Full Fan",
            seed=42,
            threads=4,
        )

    import shutil

    shutil.copy(
        tmp_path / "tmp" / "simulation_metadata.yaml",
        rf / "simulation_metadata.yaml",
    )
    shutil.copy(
        tmp_path / "tmp" / "head_calibration_factor.txt",
        rf / "head_calibration_factor.txt",
    )

    for position in ["Bottom", "Top", "Left", "Right", "Centre"]:
        for ftype in ["dtm", "tle", "dtw"]:
            (rf / "ChamberPlug{}_{}.csv".format(position, ftype)).write_text("1.0e-10")

    return rf


class TestFullCalibrationFlow:
    # With MockSpek.get_flu()=5000, no_particles = 4π×0.01×5000 = 6.283...
    # histories=1000, mAs=100, norm_factor = 6.283... / (1000 * 100) = 6.283e-3
    # calib_factor = 6.283e-3 * 100 * 1.0 = 0.628318...
    # Mock dose = 2.0e-2 → CTDI_w = 2.0e-2 × calib_factor
    def _expected_ctdi_w(self) -> float:
        import math

        # calib_factor = norm_factor × mAs × dcf_used
        # = (4π×0.1²×flu / (histories×mAs)) × mAs × dcf_used
        # = 4π×0.01×5000 / 1000 = 0.628318...
        calib_factor = 4.0 * math.pi * 0.01 * 5000.0 / 1000.0
        return 2.0e-2 * calib_factor

    def test_generate_metadata_compute_dcf_apply(self, tmp_path: Path) -> None:
        cal_path = _make_calibration_yaml(tmp_path / "calibration.yaml")
        rf = _make_runfolder_with_metadata(tmp_path, mAs=100.0, kV=100.0)

        # Simulate: compute CTDI raw
        with patch.object(
            CTDICalculator, "_extract_dose_from_file", return_value=2.0e-2
        ):
            svc = CalibrationService(cal_path)
            dcf = svc.compute_dcf(100, "Full Fan", 0.02, 20.0)

        expected_dcf = (20.0 * 1e-3) / 0.02
        assert abs(dcf - expected_dcf) < 1e-10

        # Apply calibration
        with patch.object(
            CTDICalculator, "_extract_dose_from_file", return_value=2.0e-2
        ):
            svc2 = CalibrationService(cal_path)
            results = svc2.apply(rf, 100, "Full Fan")

        assert len(results) == 3
        for r in results:
            assert abs(r["dcf_applied"] - expected_dcf) < 1e-10
            assert r["mAs_ratio"] == 1.0
            expected_calibrated = self._expected_ctdi_w() * expected_dcf
            assert abs(r["CTDI_w_calibrated"] - expected_calibrated) < 1e-12

    def test_apply_with_mAs_scaling(self, tmp_path: Path) -> None:
        cal_path = _make_calibration_yaml(tmp_path / "calibration.yaml")
        rf = _make_runfolder_with_metadata(tmp_path, mAs=100.0, kV=100.0)

        svc = CalibrationService(cal_path)
        svc.compute_dcf(100, "Full Fan", 0.02, 20.0)
        expected_dcf = (20.0 * 1e-3) / 0.02

        with patch.object(
            CTDICalculator, "_extract_dose_from_file", return_value=2.0e-2
        ):
            svc2 = CalibrationService(cal_path)
            results = svc2.apply(rf, 100, "Full Fan", target_mAs=200.0)

        for r in results:
            assert r["mAs_ratio"] == 2.0
            expected_calibrated = self._expected_ctdi_w() * expected_dcf * 2.0
            assert abs(r["CTDI_w_calibrated"] - expected_calibrated) < 1e-12


class TestBackwardCompatibility:
    def test_old_format_runfolder_works(self, tmp_path: Path) -> None:
        """CTDICalculator reads head_calibration_factor.txt when no metadata YAML."""
        rf = tmp_path / "old_runfolder"
        rf.mkdir()
        (rf / "head_calibration_factor.txt").write_text("2.5\n")

        for position in ["Bottom", "Top", "Left", "Right", "Centre"]:
            for ftype in ["dtm", "tle", "dtw"]:
                (rf / "ChamberPlug{}_{}.csv".format(position, ftype)).write_text(
                    "1.0e-10"
                )

        calc = CTDICalculator(rf)
        assert calc.calibration_factor == 2.5
        assert calc.simulation_metadata is None

        with patch.object(calc, "_extract_dose_from_file", return_value=1.0e-10):
            results = calc.calculate()
        assert len(results) == 3

    def test_new_format_runfolder_metadata(self, tmp_path: Path) -> None:
        """CTDICalculator reads simulation_metadata.yaml when present."""
        rf = tmp_path / "new_runfolder"
        rf.mkdir()

        metadata = {
            "norm_factor": 1.27e16,
            "mAs": 100.0,
            "dcf_used": 1.0,
        }
        (rf / "simulation_metadata.yaml").write_text(
            yaml.dump(metadata, default_flow_style=False)
        )
        (rf / "head_calibration_factor.txt").write_text("999.0\n")

        for position in ["Bottom", "Top", "Left", "Right", "Centre"]:
            for ftype in ["dtm", "tle", "dtw"]:
                (rf / "ChamberPlug{}_{}.csv".format(position, ftype)).write_text(
                    "1.0e-10"
                )

        calc = CTDICalculator(rf)
        assert calc.calibration_factor == 1.27e16 * 100.0 * 1.0
        assert calc.simulation_metadata is not None
        assert calc.simulation_metadata["norm_factor"] == 1.27e16


if __name__ == "__main__":
    pytest.main([__file__])
