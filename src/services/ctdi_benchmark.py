"""CTDI-w benchmark comparison against measured reference values."""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List

import pandas as pd

from src.services.ctdi_calculator import CTDICalculator, PRIMARY_SCORER

logger = logging.getLogger(__name__)

MSV_TO_GY = 1e-3


@dataclass(frozen=True)
class BenchmarkResult:
    """Comparison between simulated and reference CTDI-w for one scorer type."""

    file_type: str
    simulated_ctdi_w_Gy: float
    reference_ctdi_w_Gy: float
    deviation_pct: float
    pass_fail: str


class BenchmarkCalculator:
    """Compares CTDICalculator output against a measured reference value."""

    def __init__(self, runfolder: Path) -> None:
        self.runfolder = runfolder
        self.calculator = CTDICalculator(runfolder)

    def compare(
        self, reference_mSv: float, tolerance_pct: float = 10.0
    ) -> List[BenchmarkResult]:
        """Compute simulated CTDI-w and compare against a reference in mSv.

        Uses the normalization pipeline to compute raw Gy
        (norm_factor x mAs, no DCF) from raw Sum values.
        Only TLE (primary) scorer results are benchmarked by default.
        Other scorer types are skipped.

        Args:
            reference_mSv: Measured CTDI-w reference value in mSv.
            tolerance_pct: Acceptable percentage deviation (default 10%).

        Returns:
            One BenchmarkResult for the primary (TLE) scorer, if present.

        Raises:
            ValueError: If reference_mSv is zero or negative.
        """
        if reference_mSv <= 0:
            raise ValueError(
                "Reference CTDI-w must be positive, got {}".format(reference_mSv)
            )

        reference_Gy = reference_mSv * MSV_TO_GY
        logger.info("Reference: %.4f mSv = %.6e Gy", reference_mSv, reference_Gy)

        self.calculator.validate()
        calc_results = self.calculator.calculate()

        if not calc_results:
            logger.error("No CTDI-w results from calculator")
            return []

        metadata = calc_results[0].get("metadata", {}) if calc_results else {}
        total_histories = metadata.get("total_histories", 0)
        exposure_mAs = metadata.get("exposure_mAs", 0.0)
        spectrum_fluence = metadata.get("spectrum_fluence_photons_per_mAs")

        if spectrum_fluence and spectrum_fluence > 0 and total_histories > 0:
            norm_factor = spectrum_fluence / total_histories
        else:
            norm_factor = self.calculator.simulation_metadata.get("norm_factor", 1.0) if self.calculator.simulation_metadata else 1.0

        benchmark_results: List[BenchmarkResult] = []
        for calc_result in calc_results:
            if calc_result.get("scorer_type") != PRIMARY_SCORER:
                logger.info(
                    "Skipping non-primary scorer %s in benchmark",
                    calc_result.get("scorer_type", ""),
                )
                continue

            raw_sum = calc_result.get("raw_sum", 0.0)
            simulated_Gy = raw_sum * norm_factor * exposure_mAs

            deviation = (simulated_Gy - reference_Gy) / reference_Gy * 100
            status = "PASS" if abs(deviation) <= tolerance_pct else "FAIL"

            result = BenchmarkResult(
                file_type=calc_result.get("scorer_type", ""),
                simulated_ctdi_w_Gy=simulated_Gy,
                reference_ctdi_w_Gy=reference_Gy,
                deviation_pct=deviation,
                pass_fail=status,
            )
            benchmark_results.append(result)
            logger.info(
                "%s: simulated=%.6e Gy, reference=%.6e Gy, deviation=%.2f%%, status=%s",
                result.file_type,
                result.simulated_ctdi_w_Gy,
                result.reference_ctdi_w_Gy,
                result.deviation_pct,
                result.pass_fail,
            )

        return benchmark_results

    @staticmethod
    def compute_calibration_factor(simulated_Gy: float, reference_Gy: float) -> float:
        """Compute the dose calibration factor from a benchmark result.

        Args:
            simulated_Gy: Simulated CTDI-w in Gy.
            reference_Gy: Measured CTDI-w reference in Gy.

        Returns:
            The ratio reference/simulated to use as ``dose_calibration_factor``.
            Returns ``float('nan')`` if simulated_Gy is zero or negative.

        Raises:
            ValueError: If reference_Gy is zero or negative.
        """
        if reference_Gy <= 0:
            raise ValueError(
                "Reference CTDI-w must be positive, got {}".format(reference_Gy)
            )
        if simulated_Gy <= 0:
            return float("nan")
        return reference_Gy / simulated_Gy

    @staticmethod
    def format_report(results: List[BenchmarkResult]) -> str:
        """Format benchmark results as a human-readable table."""
        if not results:
            return "No benchmark results."

        header = "{:<10} {:<20} {:<20} {:<12} {:<8}".format(
            "FileType",
            "Simulated (Gy)",
            "Reference (Gy)",
            "Deviation%",
            "Status",
        )
        separator = "-" * len(header)
        lines = [header, separator]
        for r in results:
            lines.append(
                "{:<10} {:<20.6e} {:<20.6e} {:<12.2f} {:<8}".format(
                    r.file_type,
                    r.simulated_ctdi_w_Gy,
                    r.reference_ctdi_w_Gy,
                    r.deviation_pct,
                    r.pass_fail,
                )
            )
        return "\n".join(lines)

    @staticmethod
    def save_report(results: List[BenchmarkResult], output_path: Path) -> None:
        """Save benchmark results to CSV."""
        df = pd.DataFrame([asdict(r) for r in results])
        df.to_csv(output_path, index=False)
        logger.info("Benchmark report saved to: %s", output_path)
