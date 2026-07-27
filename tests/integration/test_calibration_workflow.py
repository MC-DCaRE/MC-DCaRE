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
    """Create a runfolder with a hand-authored simulation_metadata.yaml.

    The metadata is written directly rather than generated via
    ``SpectrumGenerator`` so that CTDICalculator's reader is exercised against
    an independent fixture (if the writer and reader drifted together, a
    generated fixture would mask it).
    """
    rf = tmp_path / "runfolder"
    rf.mkdir()

    metadata = {
        "total_histories": 1000,
        "exposure_mAs": mAs,
        "spectrum_fluence_photons_per_mAs": 2.34e8,  # kV-dependent constant
        "fan_mode": "Full Fan",
        "spekpy": {"kvp": int(kV)},
    }
    (rf / "simulation_metadata.yaml").write_text(
        yaml.dump(metadata, default_flow_style=False)
    )

    for position in ["Bottom", "Top", "Left", "Right", "Centre"]:
        for ftype in ["dtm", "tle", "dtw"]:
            (rf / "ChamberPlug{}_{}.csv".format(position, ftype)).write_text("1.0e-10")

    return rf


class TestFullCalibrationFlow:
    def test_calculate_and_normalize_end_to_end(self, tmp_path: Path) -> None:
        """CTDICalculator.calculate() + CalibrationService.normalize()."""
        cal_path = _make_calibration_yaml(tmp_path / "calibration.yaml")
        rf = _make_runfolder_with_metadata(tmp_path, mAs=100.0, kV=100.0)

        with patch.object(
            CTDICalculator, "_extract_dose_from_file", return_value=2.0e-2
        ):
            calculator = CTDICalculator(rf)
            raw_results = calculator.calculate()

        assert len(raw_results) == 3
        tle_raw = [r for r in raw_results if r["scorer_type"] == "tle"][0]
        assert "raw_sum" in tle_raw
        assert "CTDI_w" not in tle_raw
        assert tle_raw["metadata"]["total_histories"] == 1000
        assert tle_raw["metadata"]["exposure_mAs"] == 100.0

        # Compute DCF
        svc = CalibrationService(cal_path)
        dcf = svc.compute_dcf(100, "Full Fan", 3.14159e-4, 20.0)
        expected_dcf = (20.0 * 1e-3) / 3.14159e-4
        assert abs(dcf - expected_dcf) < 1e-6

        # Normalize
        norm_result = svc.normalize(tle_raw, 100, "Full Fan")
        assert norm_result["dcf_applied"] is not None
        assert norm_result["ctdi_w_calibrated_Gy"] is not None
        assert norm_result["ctdi_w_raw_Gy"] > 0
        assert norm_result["dcf_source"] == "calibration.yaml"

    def test_generate_metadata_compute_dcf_apply(self, tmp_path: Path) -> None:
        cal_path = _make_calibration_yaml(tmp_path / "calibration.yaml")
        rf = _make_runfolder_with_metadata(tmp_path, mAs=100.0, kV=100.0)

        with patch.object(
            CTDICalculator, "_extract_dose_from_file", return_value=2.0e-2
        ):
            svc = CalibrationService(cal_path)
            dcf = svc.compute_dcf(100, "Full Fan", 0.02, 20.0)

        expected_dcf = (20.0 * 1e-3) / 0.02
        assert abs(dcf - expected_dcf) < 1e-10

        with patch.object(
            CTDICalculator, "_extract_dose_from_file", return_value=2.0e-2
        ):
            svc2 = CalibrationService(cal_path)
            results = svc2.apply(rf, 100, "Full Fan")

        assert len(results) == 3
        tle_results = [r for r in results if r["scorer_type"] == "tle"]
        assert len(tle_results) == 1
        assert abs(tle_results[0]["dcf_applied"] - expected_dcf) < 1e-10
        assert tle_results[0]["mAs_ratio"] == 1.0
        assert tle_results[0]["CTDI_w_calibrated"] is not None

        non_tle = [r for r in results if r["scorer_type"] != "tle"]
        for r in non_tle:
            assert r["dcf_applied"] is None
            assert r["CTDI_w_calibrated"] is None

    def test_apply_with_mAs_scaling(self, tmp_path: Path) -> None:
        cal_path = _make_calibration_yaml(tmp_path / "calibration.yaml")
        rf = _make_runfolder_with_metadata(tmp_path, mAs=100.0, kV=100.0)

        svc = CalibrationService(cal_path)
        svc.compute_dcf(100, "Full Fan", 0.02, 20.0)

        with patch.object(
            CTDICalculator, "_extract_dose_from_file", return_value=2.0e-2
        ):
            svc2 = CalibrationService(cal_path)
            results = svc2.apply(rf, 100, "Full Fan", target_mAs=200.0)

        tle_results = [r for r in results if r["scorer_type"] == "tle"]
        assert len(tle_results) == 1
        assert tle_results[0]["mAs_ratio"] == 2.0


class TestBackwardCompatibility:
    def test_old_format_head_calibration_factor_fallback(self, tmp_path: Path) -> None:
        """CTDICalculator reads head_calibration_factor.txt when no metadata YAML."""
        rf = tmp_path / "old_runfolder"
        rf.mkdir()
        (rf / "head_calibration_factor.txt").write_text(
            "2.5\n"
            "Multiply dose by the factor above to get absolute dose\n"
            "The number of histories in this run was: 50000\n"
        )

        for position in ["Bottom", "Top", "Left", "Right", "Centre"]:
            for ftype in ["dtm", "tle", "dtw"]:
                (rf / "ChamberPlug{}_{}.csv".format(position, ftype)).write_text(
                    "1.0e-10"
                )

        calc = CTDICalculator(rf)
        assert calc.total_histories == 50000
        assert calc.exposure_mAs == 0.0
        assert calc.simulation_metadata is None

        with patch.object(calc, "_extract_dose_from_file", return_value=1.0e-10):
            results = calc.calculate()
        assert len(results) == 3
        for r in results:
            assert "raw_sum" in r
            assert r["metadata"]["total_histories"] == 50000

    def test_new_format_runfolder_metadata(self, tmp_path: Path) -> None:
        """CTDICalculator reads simulation_metadata.yaml when present."""
        rf = tmp_path / "new_runfolder"
        rf.mkdir()

        metadata = {
            "total_histories": 1000000,
            "exposure_mAs": 100.0,
            "spectrum_fluence_photons_per_mAs": 2.34e8,
        }
        (rf / "simulation_metadata.yaml").write_text(
            yaml.dump(metadata, default_flow_style=False)
        )

        for position in ["Bottom", "Top", "Left", "Right", "Centre"]:
            for ftype in ["dtm", "tle", "dtw"]:
                (rf / "ChamberPlug{}_{}.csv".format(position, ftype)).write_text(
                    "1.0e-10"
                )

        calc = CTDICalculator(rf)
        assert calc.total_histories == 1000000
        assert calc.exposure_mAs == 100.0
        assert calc.simulation_metadata is not None
        assert calc.simulation_metadata["total_histories"] == 1000000

        with patch.object(calc, "_extract_dose_from_file", return_value=1.0e-10):
            results = calc.calculate()
        assert len(results) == 3
        for r in results:
            assert "spectrum_fluence_photons_per_mAs" in r["metadata"]

    def test_old_format_yaml_metadata(self, tmp_path: Path) -> None:
        """CTDICalculator reads old-format YAML metadata."""
        rf = tmp_path / "old_yaml_runfolder"
        rf.mkdir()

        metadata = {
            "norm_factor": 1.27e16,
            "mAs": 100.0,
            "dcf_used": 1.0,
            "total_histories": 500000,
        }
        (rf / "simulation_metadata.yaml").write_text(
            yaml.dump(metadata, default_flow_style=False)
        )

        for position in ["Bottom", "Top", "Left", "Right", "Centre"]:
            for ftype in ["dtm", "tle", "dtw"]:
                (rf / "ChamberPlug{}_{}.csv".format(position, ftype)).write_text(
                    "1.0e-10"
                )

        calc = CTDICalculator(rf)
        assert calc.total_histories == 500000
        assert calc.exposure_mAs == 100.0
        assert calc.simulation_metadata is not None
        assert calc.simulation_metadata["norm_factor"] == 1.27e16


if __name__ == "__main__":
    pytest.main([__file__])
