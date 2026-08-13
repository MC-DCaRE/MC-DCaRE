from __future__ import annotations

import math
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

from src.services.ctdi_benchmark import BenchmarkCalculator, BenchmarkResult, MSV_TO_GY


def _make_bench(tmp_path: Path, mAs: float = 100.0) -> BenchmarkCalculator:
    import yaml

    metadata = {
        "total_histories": 1000000,
        "exposure_mAs": mAs,
        "spectrum_fluence_photons_per_mAs": 2.34e8,
    }
    (tmp_path / "simulation_metadata.yaml").write_text(
        yaml.dump(metadata, default_flow_style=False)
    )
    for position in ["Bottom", "Top", "Left", "Right", "Centre"]:
        (tmp_path / "ChamberPlug{}_dtm.csv".format(position)).write_text("1.0e-10")
    return BenchmarkCalculator(tmp_path)


def _make_raw_result(
    raw_sum: float,
    scorer_type: str = "tle",
    is_primary: bool = True,
    total_histories: int = 1000000,
    exposure_mAs: float = 100.0,
    spectrum_fluence: float = 2.34e8,
) -> dict:
    return {
        "scorer_type": scorer_type,
        "is_primary": is_primary,
        "raw_sum": raw_sum,
        "peripheral_raw_sums": {},
        "center_raw_sum": raw_sum,
        "metadata": {
            "total_histories": total_histories,
            "exposure_mAs": exposure_mAs,
            "spectrum_fluence_photons_per_mAs": spectrum_fluence,
        },
    }


class TestBenchmarkResult:
    def test_frozen_dataclass(self) -> None:
        r = BenchmarkResult("dtm", 1e-10, 1.1e-10, -9.09, "PASS")
        assert r.file_type == "dtm"
        with pytest.raises(AttributeError):
            r.file_type = "tle"


class TestUnitConversion:
    def test_msv_to_gy_factor(self) -> None:
        assert MSV_TO_GY == 1e-3

    def test_reference_conversion(self, tmp_path: Path) -> None:
        bench = _make_bench(tmp_path)
        ref_mSv = 8.52
        photons_per_mAs = 2.34e8 * 1e6 / 100.0
        raw_sum = ref_mSv * MSV_TO_GY * 1e6 / (photons_per_mAs * 100.0)
        mock_results = [_make_raw_result(raw_sum)]

        with patch.object(bench.calculator, "validate"):
            with patch.object(bench.calculator, "calculate", return_value=mock_results):
                results = bench.compare(ref_mSv)

        assert len(results) == 1
        assert results[0].reference_ctdi_w_Gy == pytest.approx(8.52e-3)


class TestCompareWithinTolerance:
    def test_simulated_close_to_reference(self, tmp_path: Path) -> None:
        bench = _make_bench(tmp_path)
        ref_mSv = 10.0
        photons_per_mAs = 2.34e8 * 1e6 / 100.0
        raw_sum = ref_mSv * MSV_TO_GY * 1.05 * 1e6 / (photons_per_mAs * 100.0)
        mock_results = [_make_raw_result(raw_sum)]

        with patch.object(bench.calculator, "validate"):
            with patch.object(bench.calculator, "calculate", return_value=mock_results):
                results = bench.compare(ref_mSv, tolerance_pct=10.0)

        assert len(results) == 1
        assert results[0].pass_fail == "PASS"
        assert results[0].deviation_pct == pytest.approx(5.0)


class TestCompareOutsideTolerance:
    def test_simulated_far_from_reference(self, tmp_path: Path) -> None:
        bench = _make_bench(tmp_path)
        ref_mSv = 10.0
        photons_per_mAs = 2.34e8 * 1e6 / 100.0
        raw_sum = ref_mSv * MSV_TO_GY * 1.25 * 1e6 / (photons_per_mAs * 100.0)
        mock_results = [_make_raw_result(raw_sum)]

        with patch.object(bench.calculator, "validate"):
            with patch.object(bench.calculator, "calculate", return_value=mock_results):
                results = bench.compare(ref_mSv, tolerance_pct=10.0)

        assert len(results) == 1
        assert results[0].pass_fail == "FAIL"
        assert results[0].deviation_pct == pytest.approx(25.0)


class TestCompareNegativeDeviation:
    def test_simulated_below_reference(self, tmp_path: Path) -> None:
        bench = _make_bench(tmp_path)
        ref_mSv = 10.0
        photons_per_mAs = 2.34e8 * 1e6 / 100.0
        raw_sum = ref_mSv * MSV_TO_GY * 0.92 * 1e6 / (photons_per_mAs * 100.0)
        mock_results = [_make_raw_result(raw_sum)]

        with patch.object(bench.calculator, "validate"):
            with patch.object(bench.calculator, "calculate", return_value=mock_results):
                results = bench.compare(ref_mSv, tolerance_pct=10.0)

        assert results[0].pass_fail == "PASS"
        assert results[0].deviation_pct == pytest.approx(-8.0)


class TestCompareEdgeCases:
    def test_zero_reference_raises(self, tmp_path: Path) -> None:
        bench = _make_bench(tmp_path)
        with pytest.raises(ValueError, match="must be positive"):
            bench.compare(0.0)

    def test_negative_reference_raises(self, tmp_path: Path) -> None:
        bench = _make_bench(tmp_path)
        with pytest.raises(ValueError, match="must be positive"):
            bench.compare(-5.0)

    def test_no_calculator_results(self, tmp_path: Path) -> None:
        bench = _make_bench(tmp_path)
        with patch.object(bench.calculator, "validate"):
            with patch.object(bench.calculator, "calculate", return_value=[]):
                results = bench.compare(8.5)
        assert results == []

    def test_multiple_file_types_only_tle_benchmarked(self, tmp_path: Path) -> None:
        bench = _make_bench(tmp_path)
        ref_mSv = 10.0
        photons_per_mAs = 2.34e8 * 1e6 / 100.0
        raw_sum = ref_mSv * MSV_TO_GY * 0.97 * 1e6 / (photons_per_mAs * 100.0)
        mock_results = [
            _make_raw_result(raw_sum * 1.02, scorer_type="dtm", is_primary=False),
            _make_raw_result(raw_sum, scorer_type="tle", is_primary=True),
        ]

        with patch.object(bench.calculator, "validate"):
            with patch.object(bench.calculator, "calculate", return_value=mock_results):
                results = bench.compare(ref_mSv, tolerance_pct=5.0)

        # Only TLE is benchmarked
        assert len(results) == 1
        assert results[0].file_type == "tle"
        assert results[0].pass_fail == "PASS"


class TestFormatReport:
    def test_format_report_with_results(self) -> None:
        results = [
            BenchmarkResult("dtm", 8.52e-3, 8.50e-3, 0.24, "PASS"),
        ]
        report = BenchmarkCalculator.format_report(results)
        assert "dtm" in report
        assert "PASS" in report
        assert "FileType" in report

    def test_format_report_empty(self) -> None:
        report = BenchmarkCalculator.format_report([])
        assert report == "No benchmark results."


class TestSaveReport:
    def test_save_report_csv(self, tmp_path: Path) -> None:
        results = [
            BenchmarkResult("dtm", 8.52e-3, 8.50e-3, 0.24, "PASS"),
            BenchmarkResult("tle", 7.90e-3, 8.50e-3, -7.06, "PASS"),
        ]
        output_path = tmp_path / "benchmark.csv"
        BenchmarkCalculator.save_report(results, output_path)

        assert output_path.exists()
        df = pd.read_csv(output_path)
        assert len(df) == 2
        assert list(df.columns) == [
            "file_type",
            "simulated_ctdi_w_Gy",
            "reference_ctdi_w_Gy",
            "deviation_pct",
            "pass_fail",
        ]
        assert df.iloc[0]["pass_fail"] == "PASS"
        assert df.iloc[1]["pass_fail"] == "PASS"


class TestComputeCalibrationFactor:
    def test_returns_reference_over_simulated(self) -> None:
        factor = BenchmarkCalculator.compute_calibration_factor(8.0e-3, 8.5e-3)
        assert factor == pytest.approx(1.0625)

    def test_exact_match_returns_one(self) -> None:
        factor = BenchmarkCalculator.compute_calibration_factor(8.5e-3, 8.5e-3)
        assert factor == pytest.approx(1.0)

    def test_zero_simulated_returns_nan(self) -> None:
        result = BenchmarkCalculator.compute_calibration_factor(0.0, 8.5e-3)
        assert math.isnan(result)

    def test_negative_simulated_returns_nan(self) -> None:
        result = BenchmarkCalculator.compute_calibration_factor(-1e-3, 8.5e-3)
        assert math.isnan(result)

    def test_zero_reference_raises(self) -> None:
        with pytest.raises(ValueError, match="must be positive"):
            BenchmarkCalculator.compute_calibration_factor(8.0e-3, 0.0)

    def test_negative_reference_raises(self) -> None:
        with pytest.raises(ValueError, match="must be positive"):
            BenchmarkCalculator.compute_calibration_factor(8.0e-3, -1e-3)

    def test_simulated_above_reference(self) -> None:
        factor = BenchmarkCalculator.compute_calibration_factor(9.0e-3, 8.5e-3)
        assert factor == pytest.approx(8.5 / 9.0)


if __name__ == "__main__":
    pytest.main([__file__])
