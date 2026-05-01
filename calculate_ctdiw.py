from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

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


if __name__ == "__main__":
    typer.run(main)
