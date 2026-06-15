from __future__ import annotations

import logging
import math
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from src.services.ctdi_benchmark import BenchmarkCalculator
from src.services.ctdi_calculator import CTDICalculator
from src.services.calibration import CalibrationService

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
console = Console()

app = typer.Typer()

DEFAULT_CALIBRATION_PATH = "calibration.yaml"


def _compute_raw_Gy(result: dict) -> float:
    """Compute raw Gy (norm_factor x mAs, no DCF) from a raw result dict."""
    metadata = result.get("metadata", {})
    total_histories = metadata.get("total_histories", 0)
    exposure_mAs = metadata.get("exposure_mAs", 0.0)
    spectrum_fluence = metadata.get("spectrum_fluence_photons_per_mAs")

    if spectrum_fluence and spectrum_fluence > 0 and total_histories > 0:
        norm_factor = spectrum_fluence / total_histories
    elif metadata.get("norm_factor"):
        norm_factor = metadata["norm_factor"]
    else:
        raise ValueError(
            "Cannot compute norm_factor: need either "
            "spectrum_fluence_photons_per_mAs or norm_factor in metadata"
        )

    raw_sum = result.get("raw_sum", 0.0)
    return raw_sum * norm_factor * exposure_mAs


@app.command()
def main(
    runfolder: str = typer.Argument(
        ..., help="Path to the runfolder containing ChamberPlug CSV files"
    ),
    output_file: Optional[str] = typer.Option(
        None, "--output", "-o", help="Output CSV filename"
    ),
    calibrated: bool = typer.Option(
        False, "--calibrated", help="Apply DCF from calibration.yaml"
    ),
    dcf: Optional[float] = typer.Option(
        None, "--dcf", help="Explicit DCF override (bypasses calibration.yaml)"
    ),
    target_mAs: Optional[float] = typer.Option(
        None, "--target-mAs", help="Rescale to specified mAs"
    ),
    calibration_yaml: str = typer.Option(
        DEFAULT_CALIBRATION_PATH,
        "--calibration-yaml",
        help="Path to calibration.yaml (default: calibration.yaml)",
    ),
    kV: Optional[int] = typer.Option(
        None, "--kV", help="Tube voltage in kV (required with --calibrated or --dcf)"
    ),
    fan_mode: Optional[str] = typer.Option(
        None,
        "--fan-mode",
        help="Fan mode (required with --calibrated or --dcf)",
    ),
) -> None:
    runfolder_path = Path(runfolder).resolve()
    try:
        calculator = CTDICalculator(runfolder_path)
    except (FileNotFoundError, ValueError) as exc:
        console.print("Error: {}".format(exc), style="red")
        raise typer.Exit(1)
    calculator.validate()

    if output_file is None:
        output_path = runfolder_path / "CTDIw_results.csv"
    else:
        output_path = Path(output_file).resolve()

    console.print("Processing runfolder: " + str(runfolder_path), style="blue")

    results = calculator.calculate()

    if not results:
        console.print("No results generated.", style="red")
        raise typer.Exit(1)

    calculator.save_results(results, output_path)

    console.print("\nResults Summary:", style="bold")
    for result in results:
        scorer = result["scorer_type"]
        try:
            raw_gy = _compute_raw_Gy(result)
            console.print(
                "  {}: CTDI_w_raw_Gy = {:.6e} Gy (norm_factor x mAs, no DCF)".format(
                    scorer, raw_gy
                ),
                style="cyan",
            )

            apply_dcf = calibrated or dcf is not None
            if apply_dcf:
                if kV is None or fan_mode is None:
                    console.print(
                        "  Error: --kV and --fan-mode required for DCF application",
                        style="red",
                    )
                    raise typer.Exit(1)

                calib_svc = CalibrationService(Path(calibration_yaml))
                norm_result = calib_svc.normalize(
                    result,
                    kV,
                    fan_mode,
                    target_mAs=target_mAs,
                    dcf_override=dcf,
                )
                calibrated_gy = norm_result["ctdi_w_calibrated_Gy"]
                dcf_source = norm_result["dcf_source"]
                dcf_val = norm_result["dcf_applied"]
                if calibrated_gy is not None:
                    console.print(
                        "  {}: CTDI_w_calibrated_Gy = {:.6e} Gy (DCF={} from {}, mAs={})".format(
                            scorer,
                            calibrated_gy,
                            dcf_val,
                            dcf_source,
                            norm_result["mAs_used"],
                        ),
                        style="green",
                    )
                else:
                    console.print(
                        "  {}: No DCF available for (kV={}, fan_mode={})".format(
                            scorer, kV, fan_mode
                        ),
                        style="yellow",
                    )
        except (ValueError, KeyError) as exc:
            console.print(
                "  {}: Error computing Gy: {}".format(scorer, exc), style="red"
            )


@app.command()
def benchmark(
    runfolder: str = typer.Argument(
        ...,
        help="Path to the runfolder containing ChamberPlug CSV files",
    ),
    reference: float = typer.Option(
        ...,
        "--reference",
        "-r",
        help="Measured CTDI-w reference value in mSv",
    ),
    tolerance: float = typer.Option(
        10.0,
        "--tolerance",
        "-t",
        help="Acceptable percentage deviation (default: 10%)",
    ),
    output_file: Optional[str] = typer.Option(
        None, "--output", "-o", help="Output CSV filename for benchmark report"
    ),
    calibration_yaml: str = typer.Option(
        DEFAULT_CALIBRATION_PATH,
        "--calibration-yaml",
        help="Path to calibration.yaml (default: calibration.yaml)",
    ),
    kV: Optional[int] = typer.Option(
        None,
        "--kV",
        help="Tube voltage in kV (writes DCF to calibration.yaml if provided)",
    ),
    fan_mode: Optional[str] = typer.Option(
        None, "--fan-mode", help="Fan mode (required with --kV)"
    ),
) -> None:
    runfolder_path = Path(runfolder).resolve()
    try:
        bench = BenchmarkCalculator(runfolder_path)
    except (FileNotFoundError, ValueError) as exc:
        console.print("Error: {}".format(exc), style="red")
        raise typer.Exit(1)

    console.print(
        "Benchmarking runfolder: {} against {:.4f} mSv (tolerance: {:.1f}%)".format(
            runfolder_path, reference, tolerance
        ),
        style="blue",
    )

    try:
        results = bench.compare(reference, tolerance)
    except ValueError as exc:
        console.print("Error: {}".format(exc), style="red")
        raise typer.Exit(1)

    if not results:
        console.print("No benchmark results generated.", style="red")
        raise typer.Exit(1)

    if output_file is not None:
        output_path = Path(output_file).resolve()
        BenchmarkCalculator.save_report(results, output_path)
        console.print("Report saved to: {}".format(output_path), style="green")

    console.print("\nBenchmark Report:", style="bold")
    console.print(BenchmarkCalculator.format_report(results))

    all_pass = all(r.pass_fail == "PASS" for r in results)
    if all_pass:
        console.print("\nAll comparisons PASS.", style="bold green")
    else:
        console.print("\nSome comparisons FAIL.", style="bold red")

    console.print("\nRecommended DCF by scorer:", style="yellow")
    primary_factor = None
    for r in results:
        cal_factor = BenchmarkCalculator.compute_calibration_factor(
            r.simulated_ctdi_w_Gy, r.reference_ctdi_w_Gy
        )
        if math.isnan(cal_factor):
            console.print("  {}: N/A (simulated dose is zero)".format(r.file_type))
        else:
            console.print("  {}: {:.6e}".format(r.file_type, cal_factor))
            if primary_factor is None:
                primary_factor = cal_factor

    # Write DCF to calibration.yaml if kV and fan_mode provided
    if (
        kV is not None
        and fan_mode is not None
        and primary_factor is not None
        and not math.isnan(primary_factor)
    ):
        try:
            calib_svc = CalibrationService(Path(calibration_yaml))
            dcf_value = calib_svc.compute_dcf(
                kV, fan_mode, primary_factor, reference, force=True
            )
            console.print(
                "\nDCF written to {}: ({}, {}) -> {:.6f}".format(
                    calibration_yaml, kV, fan_mode, dcf_value
                ),
                style="green",
            )
        except (ValueError, FileNotFoundError) as exc:
            console.print(
                "\nCould not write DCF to {}: {}".format(calibration_yaml, exc),
                style="red",
            )

    if not all_pass:
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
