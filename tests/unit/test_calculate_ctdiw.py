from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
import pandas as pd
import yaml

from src.services.ctdi_calculator import CTDICalculator, PRIMARY_SCORER


def _make_cal(
    tmp_path: Path, histories: int = 1000000, mAs: float = 100.0
) -> CTDICalculator:
    metadata = {
        "total_histories": histories,
        "exposure_mAs": mAs,
        "spectrum_fluence_photons_per_mAs": 2.34e8,
    }
    (tmp_path / "simulation_metadata.yaml").write_text(
        yaml.dump(metadata, default_flow_style=False)
    )
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

        assert len(chamber_files) == 4
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
        assert result["scorer_type"] == "dtw"
        assert result["is_primary"] is False
        assert result["raw_sum"] == pytest.approx(
            (2 / 3) * (1.0e-10 + 1.2e-10 + 0.8e-10 + 1.1e-10) / 4 + (1 / 3) * 2.0e-10
        )
        assert result["peripheral_raw_sums"]["Bottom"] == 1.0e-10
        assert result["peripheral_raw_sums"]["Top"] == 1.2e-10
        assert result["peripheral_raw_sums"]["Left"] == 0.8e-10
        assert result["peripheral_raw_sums"]["Right"] == 1.1e-10
        assert result["center_raw_sum"] == 2.0e-10

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
                "scorer_type": "dtw",
                "is_primary": False,
                "raw_sum": 1.333333e-10,
                "peripheral_raw_sums": {
                    "Bottom": 1.0e-10,
                    "Top": 1.2e-10,
                    "Left": 0.8e-10,
                    "Right": 1.1e-10,
                },
                "center_raw_sum": 2.0e-10,
                "metadata": {
                    "total_histories": 1000000,
                    "exposure_mAs": 100.0,
                },
            }
        ]

        output_path = tmp_path / "test_results.csv"
        calc = _make_cal(tmp_path)
        calc.save_results(results, output_path)

        assert output_path.exists()

        df = pd.read_csv(output_path)
        assert len(df) == 1
        assert df.iloc[0]["scorer_type"] == "dtw"
        assert df.iloc[0]["raw_sum"] == 1.333333e-10


class TestValidate:
    def test_validate_valid_runfolder(self, tmp_path: Path) -> None:
        metadata = {
            "total_histories": 1000000,
            "exposure_mAs": 100.0,
            "spectrum_fluence_photons_per_mAs": 2.34e8,
        }
        (tmp_path / "simulation_metadata.yaml").write_text(
            yaml.dump(metadata, default_flow_style=False)
        )
        (tmp_path / "ChamberPlugTop_dtm.csv").write_text("1.0e-10")

        calc = CTDICalculator(tmp_path)
        calc.validate()

    def test_validate_nonexistent_runfolder(self) -> None:
        with pytest.raises(FileNotFoundError, match="No metadata found"):
            CTDICalculator(Path("nonexistent"))

    def test_validate_no_chamber_files(self, tmp_path: Path) -> None:
        metadata = {
            "total_histories": 1000000,
            "exposure_mAs": 100.0,
            "spectrum_fluence_photons_per_mAs": 2.34e8,
        }
        (tmp_path / "simulation_metadata.yaml").write_text(
            yaml.dump(metadata, default_flow_style=False)
        )
        calc = CTDICalculator(tmp_path)
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
        assert results[0]["scorer_type"] == "dtm"
        assert results[0]["is_primary"] is False
        assert results[1]["scorer_type"] == "tle"
        assert results[1]["is_primary"] is True
        assert results[2]["scorer_type"] == "dtw"
        assert results[2]["is_primary"] is False

        # Verify metadata is attached
        for r in results:
            assert "metadata" in r
            assert r["metadata"]["total_histories"] == 1000000
            assert r["metadata"]["exposure_mAs"] == 100.0
            assert r["metadata"]["spectrum_fluence_photons_per_mAs"] == 2.34e8
            # No CTDI_w at top level
            assert "CTDI_w" not in r


class TestCalculateWaterChamber:
    def test_calculate_includes_water_results(self, tmp_path: Path) -> None:
        positions = ["Bottom", "Top", "Left", "Right", "Centre"]
        for position in positions:
            for ftype in ["dtm", "tle", "dtw", "water_dtm"]:
                (tmp_path / "ChamberPlug{}_{}.csv".format(position, ftype)).write_text(
                    "1.0e-10"
                )

        calc = _make_cal(tmp_path)

        with patch.object(
            calc,
            "_extract_dose_from_file",
            return_value=1.0e-10,
        ):
            results = calc.calculate()

        scorer_types = [r["scorer_type"] for r in results]
        assert "water_dtm" in scorer_types
        water_result = [r for r in results if r["scorer_type"] == "water_dtm"][0]
        assert water_result["is_primary"] is False

    def test_calculate_without_water_files(self, tmp_path: Path) -> None:
        positions = ["Bottom", "Top", "Left", "Right", "Centre"]
        for position in positions:
            for ftype in ["dtm", "tle", "dtw"]:
                (tmp_path / "ChamberPlug{}_{}.csv".format(position, ftype)).write_text(
                    "1.0e-10"
                )

        calc = _make_cal(tmp_path)

        with patch.object(
            calc,
            "_extract_dose_from_file",
            return_value=1.0e-10,
        ):
            results = calc.calculate()

        scorer_types = [r["scorer_type"] for r in results]
        assert "water_dtm" not in scorer_types
        assert len(results) == 3


class TestReadMetadata:
    def test_reads_new_metadata(self, tmp_path: Path) -> None:
        metadata = {
            "total_histories": 500000,
            "exposure_mAs": 200.0,
            "spectrum_fluence_photons_per_mAs": 1.5e8,
        }
        (tmp_path / "simulation_metadata.yaml").write_text(
            yaml.dump(metadata, default_flow_style=False)
        )

        calc = CTDICalculator(tmp_path)
        assert calc.total_histories == 500000
        assert calc.exposure_mAs == 200.0
        assert calc.simulation_metadata is not None

    def test_reads_old_metadata(self, tmp_path: Path) -> None:
        metadata = {
            "norm_factor": 1.27e16,
            "mAs": 100.0,
            "dcf_used": 1.0,
            "total_histories": 100000000,
        }
        (tmp_path / "simulation_metadata.yaml").write_text(
            yaml.dump(metadata, default_flow_style=False)
        )

        calc = CTDICalculator(tmp_path)
        assert calc.total_histories == 100000000
        assert calc.exposure_mAs == 100.0
        assert calc.simulation_metadata is not None

    def test_falls_back_to_head_calibration_factor(self, tmp_path: Path) -> None:
        (tmp_path / "head_calibration_factor.txt").write_text(
            "2.5\n"
            "Multiply dose by the factor above to get absolute dose\n"
            "The number of histories in this run was: 500000\n"
        )

        calc = CTDICalculator(tmp_path)
        assert calc.total_histories == 500000
        assert calc.exposure_mAs == 0.0
        assert calc.simulation_metadata is None

    def test_prefers_yaml_over_legacy_file(self, tmp_path: Path) -> None:
        metadata = {
            "total_histories": 100000,
            "exposure_mAs": 50.0,
            "spectrum_fluence_photons_per_mAs": 2.34e8,
        }
        (tmp_path / "simulation_metadata.yaml").write_text(
            yaml.dump(metadata, default_flow_style=False)
        )
        (tmp_path / "head_calibration_factor.txt").write_text(
            "999.0\nThe number of histories in this run was: 200000\n"
        )

        calc = CTDICalculator(tmp_path)
        assert calc.total_histories == 100000
        assert calc.exposure_mAs == 50.0
        assert calc.simulation_metadata is not None

    def test_raises_when_no_metadata(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError, match="No metadata found"):
            CTDICalculator(tmp_path)

    def test_falls_back_on_malformed_yaml(self, tmp_path: Path) -> None:
        (tmp_path / "simulation_metadata.yaml").write_text("not a mapping\n")
        (tmp_path / "head_calibration_factor.txt").write_text(
            "3.0\nThe number of histories in this run was: 300000\n"
        )

        calc = CTDICalculator(tmp_path)
        assert calc.total_histories == 300000


class TestCompareScorers:
    def _make_results(
        self,
        tle_raw: float = 1.0e-10,
        dtm_raw: float = 0.9e-10,
        dtw_raw: float = 1.1e-10,
    ) -> list[dict]:
        return [
            {
                "scorer_type": "tle",
                "is_primary": True,
                "raw_sum": tle_raw,
                "peripheral_raw_sums": {
                    "Bottom": tle_raw * 0.8,
                    "Top": tle_raw * 0.8,
                    "Left": tle_raw * 0.8,
                    "Right": tle_raw * 0.8,
                },
                "center_raw_sum": tle_raw * 1.4,
                "metadata": {"total_histories": 1000000, "exposure_mAs": 100.0},
            },
            {
                "scorer_type": "dtm",
                "is_primary": False,
                "raw_sum": dtm_raw,
                "peripheral_raw_sums": {
                    "Bottom": dtm_raw * 0.8,
                    "Top": dtm_raw * 0.8,
                    "Left": dtm_raw * 0.8,
                    "Right": dtm_raw * 0.8,
                },
                "center_raw_sum": dtm_raw * 1.4,
                "metadata": {"total_histories": 1000000, "exposure_mAs": 100.0},
            },
            {
                "scorer_type": "dtw",
                "is_primary": False,
                "raw_sum": dtw_raw,
                "peripheral_raw_sums": {
                    "Bottom": dtw_raw * 0.8,
                    "Top": dtw_raw * 0.8,
                    "Left": dtw_raw * 0.8,
                    "Right": dtw_raw * 0.8,
                },
                "center_raw_sum": dtw_raw * 1.4,
                "metadata": {"total_histories": 1000000, "exposure_mAs": 100.0},
            },
        ]

    def test_compare_scorers_full_comparison(self, tmp_path: Path) -> None:
        calc = _make_cal(tmp_path)
        results = self._make_results()
        comparison = calc.compare_scorers(results)

        assert "tle_vs_dtm_ratio" in comparison
        assert "tle_vs_dtw_ratio" in comparison
        assert "systematic_note" in comparison

        assert comparison["tle_vs_dtm_ratio"]["overall"] == pytest.approx(1.0 / 0.9)
        assert comparison["tle_vs_dtw_ratio"]["overall"] == pytest.approx(1.0 / 1.1)

    def test_compare_scorers_per_position_ratios(self, tmp_path: Path) -> None:
        calc = _make_cal(tmp_path)
        results = self._make_results()
        comparison = calc.compare_scorers(results)

        dtm_ratio = comparison["tle_vs_dtm_ratio"]
        assert "peripheral_avg" in dtm_ratio
        assert "center" in dtm_ratio

    def test_compare_scorers_raises_on_tle_only(self, tmp_path: Path) -> None:
        calc = _make_cal(tmp_path)
        results = [
            {
                "scorer_type": "tle",
                "is_primary": True,
                "raw_sum": 1.0e-10,
                "peripheral_raw_sums": {},
                "center_raw_sum": 1.0e-10,
                "metadata": {"total_histories": 1000000, "exposure_mAs": 100.0},
            }
        ]
        with pytest.raises(ValueError, match="at least one analogue scorer"):
            calc.compare_scorers(results)

    def test_compare_scorers_raises_on_no_tle(self, tmp_path: Path) -> None:
        calc = _make_cal(tmp_path)
        results = [
            {
                "scorer_type": "dtm",
                "is_primary": False,
                "raw_sum": 1.0e-10,
                "peripheral_raw_sums": {},
                "center_raw_sum": 1.0e-10,
                "metadata": {"total_histories": 1000000, "exposure_mAs": 100.0},
            }
        ]
        with pytest.raises(ValueError, match="must contain TLE"):
            calc.compare_scorers(results)

    def test_compare_scorers_tle_plus_dtm_only(self, tmp_path: Path) -> None:
        calc = _make_cal(tmp_path)
        results = [
            {
                "scorer_type": "tle",
                "is_primary": True,
                "raw_sum": 1.0e-10,
                "peripheral_raw_sums": {
                    "Bottom": 0.8e-10,
                    "Top": 0.8e-10,
                    "Left": 0.8e-10,
                    "Right": 0.8e-10,
                },
                "center_raw_sum": 1.4e-10,
                "metadata": {"total_histories": 1000000, "exposure_mAs": 100.0},
            },
            {
                "scorer_type": "dtm",
                "is_primary": False,
                "raw_sum": 0.9e-10,
                "peripheral_raw_sums": {
                    "Bottom": 0.7e-10,
                    "Top": 0.7e-10,
                    "Left": 0.7e-10,
                    "Right": 0.7e-10,
                },
                "center_raw_sum": 1.3e-10,
                "metadata": {"total_histories": 1000000, "exposure_mAs": 100.0},
            },
        ]
        comparison = calc.compare_scorers(results)
        assert "tle_vs_dtm_ratio" in comparison
        assert "tle_vs_dtw_ratio" not in comparison


class TestScorerTypeFields:
    def test_primary_scorer_constant(self) -> None:
        assert PRIMARY_SCORER == "tle"

    def test_process_file_type_tle_is_primary(self, tmp_path: Path) -> None:
        calc = _make_cal(tmp_path)
        chamber_files = {
            "Bottom": tmp_path / "ChamberPlugBottom_tle.csv",
            "Top": tmp_path / "ChamberPlugTop_tle.csv",
            "Left": tmp_path / "ChamberPlugLeft_tle.csv",
            "Right": tmp_path / "ChamberPlugRight_tle.csv",
            "Centre": tmp_path / "ChamberPlugCentre_tle.csv",
        }
        with patch.object(
            calc,
            "_extract_dose_from_file",
            side_effect=[1.0e-10, 1.2e-10, 0.8e-10, 1.1e-10, 2.0e-10],
        ):
            result = calc._process_file_type(chamber_files, "tle")

        assert result is not None
        assert result["scorer_type"] == "tle"
        assert result["is_primary"] is True

    def test_process_file_type_dtm_not_primary(self, tmp_path: Path) -> None:
        calc = _make_cal(tmp_path)
        chamber_files = {
            "Bottom": tmp_path / "ChamberPlugBottom_dtm.csv",
            "Top": tmp_path / "ChamberPlugTop_dtm.csv",
            "Left": tmp_path / "ChamberPlugLeft_dtm.csv",
            "Right": tmp_path / "ChamberPlugRight_dtm.csv",
            "Centre": tmp_path / "ChamberPlugCentre_dtm.csv",
        }
        with patch.object(
            calc,
            "_extract_dose_from_file",
            side_effect=[1.0e-10, 1.2e-10, 0.8e-10, 1.1e-10, 2.0e-10],
        ):
            result = calc._process_file_type(chamber_files, "dtm")

        assert result is not None
        assert result["scorer_type"] == "dtm"
        assert result["is_primary"] is False


class TestFindWaterChamberFiles:
    def test_find_water_chamber_files(self, tmp_path: Path) -> None:
        positions = ["Bottom", "Top", "Left", "Right", "Centre"]
        for position in positions:
            (tmp_path / "ChamberPlug{}_water_dtm.csv".format(position)).write_text(
                "1.0e-10"
            )

        calc = _make_cal(tmp_path)
        chamber_files = calc._find_chamber_files()

        assert "water_dtm" in chamber_files
        assert len(chamber_files["water_dtm"]) == 5
        for position in positions:
            assert position in chamber_files["water_dtm"]

    def test_water_chamber_files_absent_by_default(self, tmp_path: Path) -> None:
        positions = ["Bottom", "Top", "Left", "Right", "Centre"]
        for position in positions:
            for ftype in ["dtm", "tle", "dtw"]:
                (tmp_path / "ChamberPlug{}_{}.csv".format(position, ftype)).write_text(
                    "1.0e-10"
                )

        calc = _make_cal(tmp_path)
        chamber_files = calc._find_chamber_files()

        assert "water_dtm" in chamber_files
        assert len(chamber_files["water_dtm"]) == 0


class TestCompareScorersGuards:
    def test_duplicate_scorer_type_raises(self, tmp_path: Path) -> None:
        calc = _make_cal(tmp_path)
        results = [
            {
                "scorer_type": "tle",
                "is_primary": True,
                "raw_sum": 1.0e-10,
                "peripheral_raw_sums": {},
                "center_raw_sum": 1.0e-10,
                "metadata": {"total_histories": 1000000, "exposure_mAs": 100.0},
            },
            {
                "scorer_type": "dtm",
                "is_primary": False,
                "raw_sum": 0.9e-10,
                "peripheral_raw_sums": {},
                "center_raw_sum": 0.9e-10,
                "metadata": {"total_histories": 1000000, "exposure_mAs": 100.0},
            },
            {
                "scorer_type": "dtm",
                "is_primary": False,
                "raw_sum": 0.95e-10,
                "peripheral_raw_sums": {},
                "center_raw_sum": 0.95e-10,
                "metadata": {"total_histories": 1000000, "exposure_mAs": 100.0},
            },
        ]
        with pytest.raises(ValueError, match="Duplicate scorer_type"):
            calc.compare_scorers(results)

    def test_non_finite_tle_raw_raises(self, tmp_path: Path) -> None:
        calc = _make_cal(tmp_path)
        results = [
            {
                "scorer_type": "tle",
                "is_primary": True,
                "raw_sum": float("nan"),
                "peripheral_raw_sums": {},
                "center_raw_sum": 1.0e-10,
                "metadata": {"total_histories": 1000000, "exposure_mAs": 100.0},
            },
            {
                "scorer_type": "dtm",
                "is_primary": False,
                "raw_sum": 0.9e-10,
                "peripheral_raw_sums": {},
                "center_raw_sum": 0.9e-10,
                "metadata": {"total_histories": 1000000, "exposure_mAs": 100.0},
            },
        ]
        with pytest.raises(ValueError, match="not finite"):
            calc.compare_scorers(results)

    def test_non_finite_analogue_raw_raises(self, tmp_path: Path) -> None:
        calc = _make_cal(tmp_path)
        results = [
            {
                "scorer_type": "tle",
                "is_primary": True,
                "raw_sum": 1.0e-10,
                "peripheral_raw_sums": {},
                "center_raw_sum": 1.0e-10,
                "metadata": {"total_histories": 1000000, "exposure_mAs": 100.0},
            },
            {
                "scorer_type": "dtm",
                "is_primary": False,
                "raw_sum": float("inf"),
                "peripheral_raw_sums": {},
                "center_raw_sum": 0.9e-10,
                "metadata": {"total_histories": 1000000, "exposure_mAs": 100.0},
            },
        ]
        with pytest.raises(ValueError, match="not finite"):
            calc.compare_scorers(results)


if __name__ == "__main__":
    pytest.main([__file__])
