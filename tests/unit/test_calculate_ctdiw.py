"""
Unit tests for calculate_ctdiw.py script.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import pandas as pd

from calculate_ctdiw import (
    extract_dose_from_file,
    find_chamber_files,
    calculate_ctdi_w,
    process_file_type,
    save_results,
    validate_runfolder,
    main,
)


class TestExtractDoseFromFile:
    def test_extract_dose_valid_file(self, tmp_path):
        file_content = """# TOPAS Version: 4.0
# Parameter File: /path/to/file.txt
# Results for scorer: ChamberPlugDose_dtm
# Scored in component: ChamberPlugTop
# DoseToWater ( Gy ) : Sum   
5.109993539420543e-10
"""
        file_path = tmp_path / "test_file.csv"
        file_path.write_text(file_content)

        dose = extract_dose_from_file(file_path)
        assert dose == 5.109993539420543e-10

    def test_extract_dose_file_not_found(self):
        dose = extract_dose_from_file(Path("nonexistent.csv"))
        assert dose is None

    def test_extract_dose_invalid_dose_format(self, tmp_path):
        file_content = """# TOPAS Version: 4.0
# Results for scorer: ChamberPlugDose_dtm
invalid_dose_value
"""
        file_path = tmp_path / "invalid_file.csv"
        file_path.write_text(file_content)

        dose = extract_dose_from_file(file_path)
        assert dose is None

    def test_extract_dose_empty_file(self, tmp_path):
        file_path = tmp_path / "empty_file.csv"
        file_path.write_text("")

        dose = extract_dose_from_file(file_path)
        assert dose is None


class TestFindChamberFiles:
    def test_find_all_files_exist(self, tmp_path):
        positions = ["Bottom", "Top", "Left", "Right", "Centre"]
        file_types = ["dtm", "tle"]

        for position in positions:
            for file_type in file_types:
                file_path = tmp_path / f"ChamberPlug{position}_{file_type}.csv"
                file_path.write_text("1.0e-10")

        chamber_files = find_chamber_files(tmp_path)

        assert len(chamber_files) == 2
        for file_type in file_types:
            assert len(chamber_files[file_type]) == 5
            for position in positions:
                assert position in chamber_files[file_type]

    def test_find_some_files_missing(self, tmp_path):
        (tmp_path / "ChamberPlugTop_dtm.csv").write_text("1.0e-10")
        (tmp_path / "ChamberPlugCentre_dtm.csv").write_text("2.0e-10")

        chamber_files = find_chamber_files(tmp_path)

        assert len(chamber_files["dtm"]) == 2
        assert "Top" in chamber_files["dtm"]
        assert "Centre" in chamber_files["dtm"]
        assert "Bottom" not in chamber_files["dtm"]


class TestCalculateCTDI_W:
    def test_calculate_ctdi_w_valid_data(self):
        peripheral_doses = [1.0e-10, 1.2e-10, 0.8e-10, 1.1e-10]
        center_dose = 2.0e-10

        ctdi_w = calculate_ctdi_w(peripheral_doses, center_dose)

        expected_peripheral_avg = sum(peripheral_doses) / len(peripheral_doses)
        expected_ctdi_w = (2 / 3) * expected_peripheral_avg + (1 / 3) * center_dose
        assert abs(ctdi_w - expected_ctdi_w) < 1e-15

    def test_calculate_ctdi_w_no_peripheral(self):
        ctdi_w = calculate_ctdi_w([], 1.0e-10)
        assert ctdi_w == 0.0

    def test_calculate_ctdi_w_no_center(self):
        ctdi_w = calculate_ctdi_w([1.0e-10, 1.2e-10], None)
        assert ctdi_w == 0.0


class TestProcessFileType:
    @patch("calculate_ctdiw.extract_dose_from_file")
    def test_process_file_type_success(self, mock_extract, tmp_path):
        mock_extract.side_effect = [
            1.0e-10,  # Bottom
            1.2e-10,  # Top
            0.8e-10,  # Left
            1.1e-10,  # Right
            2.0e-10,  # Centre
        ]

        chamber_files = {
            "Bottom": tmp_path / "ChamberPlugBottom_dtw.csv",
            "Top": tmp_path / "ChamberPlugTop_dtw.csv",
            "Left": tmp_path / "ChamberPlugLeft_dtw.csv",
            "Right": tmp_path / "ChamberPlugRight_dtw.csv",
            "Centre": tmp_path / "ChamberPlugCentre_dtw.csv",
        }

        result = process_file_type(chamber_files, "dtw")

        assert result is not None
        assert result["FileType"] == "dtw"
        assert (
            result["PeripheralDoseAverage"]
            == (1.0e-10 + 1.2e-10 + 0.8e-10 + 1.1e-10) / 4
        )
        assert result["CenterDose"] == 2.0e-10
        assert "CTDI_w" in result
        assert "Timestamp" in result

    @patch("calculate_ctdiw.extract_dose_from_file")
    def test_process_file_type_insufficient_data(self, mock_extract, tmp_path):
        mock_extract.return_value = None

        chamber_files = {
            "Bottom": tmp_path / "ChamberPlugBottom_dtw.csv",
            "Centre": tmp_path / "ChamberPlugCentre_dtw.csv",
        }

        result = process_file_type(chamber_files, "dtw")
        assert result is None


class TestSaveResults:
    def test_save_results_success(self, tmp_path):
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
        save_results(results, output_path)

        assert output_path.exists()

        df = pd.read_csv(output_path)
        assert len(df) == 1
        assert df.iloc[0]["FileType"] == "dtw"
        assert df.iloc[0]["CTDI_w"] == 1.333333e-10


class TestValidateRunfolder:
    def test_validate_valid_runfolder(self, tmp_path):
        (tmp_path / "ChamberPlugTop_dtm.csv").write_text("1.0e-10")

        validate_runfolder(tmp_path)

    def test_validate_nonexistent_runfolder(self):
        with pytest.raises(Exception):
            validate_runfolder(Path("nonexistent"))

    def test_validate_no_chamber_files(self, tmp_path):
        with pytest.raises(Exception):
            validate_runfolder(tmp_path)


class TestMain:
    @patch("calculate_ctdiw.find_chamber_files")
    @patch("calculate_ctdiw.process_file_type")
    @patch("calculate_ctdiw.save_results")
    @patch("calculate_ctdiw.validate_runfolder")
    @patch("calculate_ctdiw.extract_calibration_factor")
    def test_main_success(
        self,
        mock_calib,
        mock_validate,
        mock_save,
        mock_process,
        mock_find,
        tmp_path,
    ):
        mock_validate.return_value = None
        mock_calib.return_value = 1.0
        mock_find.return_value = {
            "dtm": {"Top": tmp_path / "ChamberPlugTop_dtm.csv"},
            "tle": {"Top": tmp_path / "ChamberPlugTop_tle.csv"},
        }
        mock_process.return_value = {
            "FileType": "dtm",
            "PeripheralDoseAverage": 1.0e-10,
            "CenterDose": 2.0e-10,
            "CTDI_w": 1.333333e-10,
            "Timestamp": "2024-01-01T12:00:00",
        }
        mock_save.return_value = None

        (tmp_path / "ChamberPlugTop_dtm.csv").write_text("1.0e-10")

        with patch("typer.Exit"):
            main(str(tmp_path), None)


if __name__ == "__main__":
    pytest.main([__file__])
