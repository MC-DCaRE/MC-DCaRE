from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
import pandas as pd

from src.services.ctdi_calculator import CTDICalculator


def _make_cal(tmp_path: Path) -> CTDICalculator:
    (tmp_path / "head_calibration_factor.txt").write_text("1.0\n")
    return CTDICalculator(tmp_path)


class TestExtractDoseFromFile:
    def test_extract_dose_valid_file(self, tmp_path: Path) -> None:
        file_content = """# TOPAS Version: 4.0
# Parameter File: /path/to/file.txt
# Results for scorer: ChamberPlugDose_dtm
# Scored in component: ChamberPlugTop
# DoseToWater ( Gy ) : Sum   
5.109993539420543e-10
"""
        file_path = tmp_path / "test_file.csv"
        file_path.write_text(file_content)

        calc = _make_cal(tmp_path)
        dose = calc._extract_dose_from_file(file_path)
        assert dose == 5.109993539420543e-10

    def test_extract_dose_file_not_found(self, tmp_path: Path) -> None:
        calc = _make_cal(tmp_path)
        dose = calc._extract_dose_from_file(Path("nonexistent.csv"))
        assert dose is None

    def test_extract_dose_invalid_dose_format(self, tmp_path: Path) -> None:
        file_content = """# TOPAS Version: 4.0
# Results for scorer: ChamberPlugDose_dtm
invalid_dose_value
"""
        file_path = tmp_path / "invalid_file.csv"
        file_path.write_text(file_content)

        calc = _make_cal(tmp_path)
        dose = calc._extract_dose_from_file(file_path)
        assert dose is None

    def test_extract_dose_empty_file(self, tmp_path: Path) -> None:
        file_path = tmp_path / "empty_file.csv"
        file_path.write_text("")

        calc = _make_cal(tmp_path)
        dose = calc._extract_dose_from_file(file_path)
        assert dose is None


class TestFindChamberFiles:
    def test_find_all_files_exist(self, tmp_path: Path) -> None:
        positions = ["Bottom", "Top", "Left", "Right", "Centre"]
        file_types = ["dtm", "tle", "dtw"]

        for position in positions:
            for file_type in file_types:
                file_path = tmp_path / "ChamberPlug{}_{}.csv".format(
                    position, file_type
                )
                file_path.write_text("1.0e-10")

        calc = _make_cal(tmp_path)
        chamber_files = calc._find_chamber_files()

        assert len(chamber_files) == 3
        for file_type in file_types:
            assert len(chamber_files[file_type]) == 5
            for position in positions:
                assert position in chamber_files[file_type]

    def test_find_some_files_missing(self, tmp_path: Path) -> None:
        (tmp_path / "ChamberPlugTop_dtm.csv").write_text("1.0e-10")
        (tmp_path / "ChamberPlugCentre_dtm.csv").write_text("2.0e-10")

        calc = _make_cal(tmp_path)
        chamber_files = calc._find_chamber_files()

        assert len(chamber_files["dtm"]) == 2
        assert "Top" in chamber_files["dtm"]
        assert "Centre" in chamber_files["dtm"]
        assert "Bottom" not in chamber_files["dtm"]


class TestCalculateCTDI_W:
    def test_calculate_ctdi_w_valid_data(self) -> None:
        peripheral_doses = [1.0e-10, 1.2e-10, 0.8e-10, 1.1e-10]
        center_dose = 2.0e-10

        ctdi_w = CTDICalculator.calculate_ctdi_w(peripheral_doses, center_dose)

        expected_peripheral_avg = sum(peripheral_doses) / len(peripheral_doses)
        expected_ctdi_w = (2 / 3) * expected_peripheral_avg + (1 / 3) * center_dose
        assert abs(ctdi_w - expected_ctdi_w) < 1e-15

    def test_calculate_ctdi_w_no_peripheral(self) -> None:
        ctdi_w = CTDICalculator.calculate_ctdi_w([], 1.0e-10)
        assert ctdi_w == 0.0

    def test_calculate_ctdi_w_zero_center(self) -> None:
        ctdi_w = CTDICalculator.calculate_ctdi_w([1.0e-10, 1.2e-10], 0.0)
        expected_avg = (1.0e-10 + 1.2e-10) / 2
        expected = (2 / 3) * expected_avg + (1 / 3) * 0.0
        assert abs(ctdi_w - expected) < 1e-25


class TestProcessFileType:
    def test_process_file_type_success(self, tmp_path: Path) -> None:
        calc = _make_cal(tmp_path)

        chamber_files = {
            "Bottom": tmp_path / "ChamberPlugBottom_dtw.csv",
            "Top": tmp_path / "ChamberPlugTop_dtw.csv",
            "Left": tmp_path / "ChamberPlugLeft_dtw.csv",
            "Right": tmp_path / "ChamberPlugRight_dtw.csv",
            "Centre": tmp_path / "ChamberPlugCentre_dtw.csv",
        }

        with patch.object(
            calc,
            "_extract_dose_from_file",
            side_effect=[1.0e-10, 1.2e-10, 0.8e-10, 1.1e-10, 2.0e-10],
        ):
            result = calc._process_file_type(chamber_files, "dtw")

        assert result is not None
        assert result["FileType"] == "dtw"
        assert (
            result["PeripheralDoseAverage"]
            == (1.0e-10 + 1.2e-10 + 0.8e-10 + 1.1e-10) / 4
        )
        assert result["CenterDose"] == 2.0e-10
        assert "CTDI_w" in result
        assert "Timestamp" in result

    def test_process_file_type_insufficient_data(self, tmp_path: Path) -> None:
        calc = _make_cal(tmp_path)

        chamber_files = {
            "Bottom": tmp_path / "ChamberPlugBottom_dtw.csv",
            "Centre": tmp_path / "ChamberPlugCentre_dtw.csv",
        }

        with patch.object(calc, "_extract_dose_from_file", return_value=None):
            result = calc._process_file_type(chamber_files, "dtw")

        assert result is None


class TestSaveResults:
    def test_save_results_success(self, tmp_path: Path) -> None:
        results = [
            {
                "FileType": "dtw",
                "PeripheralDoseAverage": 1.0e-10,
                "CenterDose": 2.0e-10,
                "CTDI_w": 1.333333e-10,
                "Timestamp": "2024-01-01T12:00:00",
            }
        ]

        output_path = tmp_path / "test_results.csv"
        calc = _make_cal(tmp_path)
        calc.save_results(results, output_path)

        assert output_path.exists()

        df = pd.read_csv(output_path)
        assert len(df) == 1
        assert df.iloc[0]["FileType"] == "dtw"
        assert df.iloc[0]["CTDI_w"] == 1.333333e-10


class TestValidate:
    def test_validate_valid_runfolder(self, tmp_path: Path) -> None:
        (tmp_path / "ChamberPlugTop_dtm.csv").write_text("1.0e-10")

        calc = _make_cal(tmp_path)
        calc.validate()

    def test_validate_nonexistent_runfolder(self) -> None:
        with pytest.raises(FileNotFoundError, match="Calibration file not found"):
            CTDICalculator(Path("nonexistent"))

    def test_validate_no_chamber_files(self, tmp_path: Path) -> None:
        calc = _make_cal(tmp_path)
        with pytest.raises(ValueError):
            calc.validate()


class TestCalculate:
    def test_calculate_with_mocked_files(self, tmp_path: Path) -> None:
        for position in ["Bottom", "Top", "Left", "Right", "Centre"]:
            for file_type in ["dtm", "tle", "dtw"]:
                (
                    tmp_path / "ChamberPlug{}_{}.csv".format(position, file_type)
                ).write_text("1.0e-10")

        calc = _make_cal(tmp_path)

        with patch.object(
            calc,
            "_extract_dose_from_file",
            return_value=1.0e-10,
        ):
            results = calc.calculate()

        assert len(results) == 3
        assert results[0]["FileType"] == "dtm"
        assert results[1]["FileType"] == "tle"
        assert results[2]["FileType"] == "dtw"


class TestExtractCalibrationFactor:
    def test_calibration_file_present(self, tmp_path: Path) -> None:
        (tmp_path / "head_calibration_factor.txt").write_text("2.5\n")

        calc = CTDICalculator(tmp_path)
        assert calc.calibration_factor == 2.5

    def test_calibration_file_missing(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError, match="Calibration file not found"):
            CTDICalculator(tmp_path)

    def test_calibration_file_comment_only(self, tmp_path: Path) -> None:
        (tmp_path / "head_calibration_factor.txt").write_text("# comment\n")

        with pytest.raises(ValueError, match="No calibration factor"):
            CTDICalculator(tmp_path)


if __name__ == "__main__":
    pytest.main([__file__])
