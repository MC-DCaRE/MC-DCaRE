from __future__ import annotations

import logging
import math
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from src.services.ctdi_benchmark import BenchmarkCalculator
from src.services.ctdi_calculator import CTDICalculator

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
console = Console()

app = typer.Typer()


@app.command()
def main(
    runfolder: str = typer.Argument(
        ..., help="Path to the runfolder containing ChamberPlug CSV files"
    ),
    output_file: Optional[str] = typer.Option(
        None, "--output", "-o", help="Output CSV filename"
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
        console.print(
            "  "
            + result["FileType"]
            + ": CTDI_w = "
            + format(result["CTDI_w"], ".6e")
            + " Gy",
            style="cyan",
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

    console.print("\nRecommended dose_calibration_factor by scorer:", style="yellow")
    primary_factor = None
    for r in results:
        cal_factor = BenchmarkCalculator.compute_calibration_factor(
            r.simulated_ctdi_w_Gy, r.reference_ctdi_w_Gy
        )
        if math.isnan(cal_factor):
            console.print("  {}: N/A (simulated dose is zero)".format(r.file_type))
        else:
            console.print("  {}: {:.4f}".format(r.file_type, cal_factor))
            if primary_factor is None:
                primary_factor = cal_factor
    if primary_factor is not None:
        console.print(
            "\nUse the primary scorer value in your config YAML:\n"
            "  general:\n"
            '    dose_calibration_factor: "{:.4f}"'.format(primary_factor),
            style="yellow",
        )
    else:
        console.print(
            "\nCould not compute a calibration factor: all scorers reported zero dose.",
            style="red",
        )

    if not all_pass:
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
