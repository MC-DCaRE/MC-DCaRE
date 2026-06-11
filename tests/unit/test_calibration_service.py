"""Tests for CalibrationService: compute, lookup, and apply DCF."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.models.calibration import MachineCalibration
from src.services.calibration import CalibrationService
from src.services.ctdi_calculator import CTDICalculator


def _write_calibration(
    path: Path,
    entries: list[dict[str, Any]],
    machine: str = "TestMachine",
    date: str = "2026-06-10",
) -> Path:
    data = {
        "machine": machine,
        "date_calibrated": date,
        "calibrations": entries,
    }
    path.write_text(yaml.dump(data, default_flow_style=False, sort_keys=False))
    return path


@pytest.fixture
def cal_file(tmp_path: Path) -> Path:
    return _write_calibration(
        tmp_path / "calibration.yaml",
        [
            {
                "kV": 120,
                "fan_mode": "Full Fan",
                "reference_mAs": 100,
                "measured_ctdi_w_mGy": 45.2,
                "dcf": 1.034,
            },
            {
                "kV": 80,
                "fan_mode": "Full Fan",
                "reference_mAs": 100,
                "measured_ctdi_w_mGy": None,
                "dcf": None,
            },
        ],
    )


class TestComputeDCF:
    def test_compute_dcf_for_uncalibrated_entry(self, cal_file: Path) -> None:
        svc = CalibrationService(cal_file)
        dcf = svc.compute_dcf(80, "Full Fan", 0.0437, 45.0)
        expected = (45.0 * 1e-3) / 0.0437
        assert abs(dcf - expected) < 1e-10

        # Verify written back to file
        reloaded = MachineCalibration.from_yaml(cal_file)
        entry = reloaded.find_entry(80, "Full Fan")
        assert entry is not None
        assert entry.dcf is not None
        assert abs(entry.dcf - expected) < 1e-10
        assert entry.measured_ctdi_w_mGy == 45.0

        # Verify sibling entry unchanged
        sibling = reloaded.find_entry(120, "Full Fan")
        assert sibling is not None
        assert sibling.dcf == 1.034

    def test_compute_dcf_raises_on_existing_without_force(self, cal_file: Path) -> None:
        svc = CalibrationService(cal_file)
        with pytest.raises(ValueError, match="already has DCF"):
            svc.compute_dcf(120, "Full Fan", 0.0437, 46.0)

    def test_compute_dcf_overwrites_with_force(self, cal_file: Path) -> None:
        svc = CalibrationService(cal_file)
        dcf = svc.compute_dcf(120, "Full Fan", 0.0437, 46.0, force=True)
        expected = (46.0 * 1e-3) / 0.0437
        assert abs(dcf - expected) < 1e-10

    def test_compute_dcf_raises_on_missing_entry(self, cal_file: Path) -> None:
        svc = CalibrationService(cal_file)
        with pytest.raises(ValueError, match="No calibration entry"):
            svc.compute_dcf(999, "Unknown", 0.01, 10.0)

    def test_compute_dcf_raises_on_zero_simulated(self, cal_file: Path) -> None:
        svc = CalibrationService(cal_file)
        with pytest.raises(ValueError, match="positive finite"):
            svc.compute_dcf(80, "Full Fan", 0.0, 45.0)

    def test_compute_dcf_raises_on_negative_simulated(self, cal_file: Path) -> None:
        svc = CalibrationService(cal_file)
        with pytest.raises(ValueError, match="positive finite"):
            svc.compute_dcf(80, "Full Fan", -0.01, 45.0)

    def test_compute_dcf_raises_on_zero_measured(self, cal_file: Path) -> None:
        svc = CalibrationService(cal_file)
        with pytest.raises(ValueError, match="positive finite"):
            svc.compute_dcf(80, "Full Fan", 0.0437, 0.0)

    def test_compute_dcf_raises_on_nan_simulated(self, cal_file: Path) -> None:
        svc = CalibrationService(cal_file)
        with pytest.raises(ValueError, match="positive finite"):
            svc.compute_dcf(80, "Full Fan", float("nan"), 45.0)

    def test_compute_dcf_raises_on_inf_simulated(self, cal_file: Path) -> None:
        svc = CalibrationService(cal_file)
        with pytest.raises(ValueError, match="positive finite"):
            svc.compute_dcf(80, "Full Fan", float("inf"), 45.0)

    def test_compute_dcf_raises_on_nan_measured(self, cal_file: Path) -> None:
        svc = CalibrationService(cal_file)
        with pytest.raises(ValueError, match="positive finite"):
            svc.compute_dcf(80, "Full Fan", 0.0437, float("nan"))

    def test_compute_dcf_raises_on_inf_measured(self, cal_file: Path) -> None:
        svc = CalibrationService(cal_file)
        with pytest.raises(ValueError, match="positive finite"):
            svc.compute_dcf(80, "Full Fan", 0.0437, float("inf"))


class TestLookupDCF:
    def test_lookup_calibrated_entry(self, cal_file: Path) -> None:
        svc = CalibrationService(cal_file)
        assert svc.lookup_dcf(120, "Full Fan") == 1.034

    def test_lookup_uncalibrated_returns_none(self, cal_file: Path) -> None:
        svc = CalibrationService(cal_file)
        assert svc.lookup_dcf(80, "Full Fan") is None

    def test_lookup_missing_returns_none(self, cal_file: Path) -> None:
        svc = CalibrationService(cal_file)
        assert svc.lookup_dcf(999, "Unknown") is None


class TestApply:
    # norm_factor × mAs × dcf_used = 1.27e16 × 100 × 1.0 = 1.27e18 (combined factor)
    # Mock dose per chamber: 2.5e-20 Gy raw
    # CTDI_w = (2/3)*periph_avg + (1/3)*center, all scaled by calibration_factor
    # With 4 peripheral at 2.5e-20 and 1 center at 2.5e-20:
    # periph_avg = 2.5e-20 * 1.27e18 = 3.175e-2
    # center = 2.5e-20 * 1.27e18 = 3.175e-2
    # CTDI_w = (2/3)*3.175e-2 + (1/3)*3.175e-2 = 3.175e-2
    _MOCK_DOSE = 2.5e-20
    _EXPECTED_CTDI_W = 3.175e-2

    def _make_runfolder(
        self,
        tmp_path: Path,
        mAs: float = 100.0,
    ) -> Path:
        rf = tmp_path / "runfolder"
        rf.mkdir()
        metadata = {"norm_factor": 1.27e16, "mAs": mAs, "dcf_used": 1.0}
        (rf / "simulation_metadata.yaml").write_text(
            yaml.dump(metadata, default_flow_style=False)
        )
        (rf / "head_calibration_factor.txt").write_text("1.27e18\n")
        for position in ["Bottom", "Top", "Left", "Right", "Centre"]:
            for ftype in ["dtm", "tle", "dtw"]:
                (rf / "ChamberPlug{}_{}.csv".format(position, ftype)).write_text(
                    "2.5e-20"
                )
        return rf

    def test_apply_at_simulation_mAs(self, cal_file: Path, tmp_path: Path) -> None:
        svc = CalibrationService(cal_file)
        rf = self._make_runfolder(tmp_path, mAs=100.0)

        with patch.object(
            CTDICalculator, "_extract_dose_from_file", return_value=self._MOCK_DOSE
        ):
            results = svc.apply(rf, 120, "Full Fan")

        assert len(results) == 3
        # Only TLE result is calibrated
        tle_results = [r for r in results if r["scorer_type"] == "tle"]
        assert len(tle_results) == 1
        assert tle_results[0]["dcf_applied"] == 1.034
        assert tle_results[0]["mAs_ratio"] == 1.0
        expected_calibrated = self._EXPECTED_CTDI_W * 1.034
        assert abs(tle_results[0]["CTDI_w_calibrated"] - expected_calibrated) < 1e-12

        # Non-TLE results are uncalibrated
        non_tle = [r for r in results if r["scorer_type"] != "tle"]
        assert len(non_tle) == 2
        for r in non_tle:
            assert r["dcf_applied"] is None
            assert r["CTDI_w_calibrated"] is None
            assert r["note"] == "uncalibrated — secondary comparison"

    def test_apply_at_different_mAs(self, cal_file: Path, tmp_path: Path) -> None:
        svc = CalibrationService(cal_file)
        rf = self._make_runfolder(tmp_path, mAs=100.0)

        with patch.object(
            CTDICalculator, "_extract_dose_from_file", return_value=self._MOCK_DOSE
        ):
            results = svc.apply(rf, 120, "Full Fan", target_mAs=200.0)

        tle_results = [r for r in results if r["scorer_type"] == "tle"]
        assert len(tle_results) == 1
        assert tle_results[0]["mAs_ratio"] == 2.0
        expected_calibrated = self._EXPECTED_CTDI_W * 1.034 * 2.0
        assert abs(tle_results[0]["CTDI_w_calibrated"] - expected_calibrated) < 1e-12

    def test_apply_raises_on_missing_metadata(
        self, cal_file: Path, tmp_path: Path
    ) -> None:
        rf = tmp_path / "empty_runfolder"
        rf.mkdir()
        svc = CalibrationService(cal_file)
        with pytest.raises(FileNotFoundError, match="simulation_metadata.yaml"):
            svc.apply(rf, 120, "Full Fan")

    def test_apply_raises_on_uncalibrated_entry(
        self, cal_file: Path, tmp_path: Path
    ) -> None:
        svc = CalibrationService(cal_file)
        rf = self._make_runfolder(tmp_path)
        with pytest.raises(ValueError, match="No DCF calibrated"):
            svc.apply(rf, 80, "Full Fan")

    def test_apply_with_dtm_scorer_type(self, cal_file: Path, tmp_path: Path) -> None:
        """When scorer_type='dtm', DTM gets calibrated and TLE is uncalibrated."""
        svc = CalibrationService(cal_file)
        rf = self._make_runfolder(tmp_path, mAs=100.0)

        with patch.object(
            CTDICalculator, "_extract_dose_from_file", return_value=self._MOCK_DOSE
        ):
            results = svc.apply(rf, 120, "Full Fan", scorer_type="dtm")

        # DTM result is calibrated
        dtm_results = [r for r in results if r["scorer_type"] == "dtm"]
        assert len(dtm_results) == 1
        assert dtm_results[0]["dcf_applied"] == 1.034
        assert dtm_results[0]["CTDI_w_calibrated"] is not None

        # TLE result is uncalibrated
        tle_results = [r for r in results if r["scorer_type"] == "tle"]
        assert len(tle_results) == 1
        assert tle_results[0]["dcf_applied"] is None
        assert tle_results[0]["CTDI_w_calibrated"] is None
        assert tle_results[0]["note"] == "uncalibrated — secondary comparison"


if __name__ == "__main__":
    pytest.main([__file__])
