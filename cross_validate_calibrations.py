"""Cross-validate calibration DCFs against all available run-folders.

For each run-folder with a matching (kV, fan_mode) DCF in calibration.example.yaml,
computes the raw CTDI-w (TLE scorer), applies the stored DCF, and compares the
calibrated result against the expected reference (mAs-scaled).

Usage:
    uv run python cross_validate_calibrations.py [--calibration calibration.example.yaml] \
        [--runfolder-dir runfolder] [--tolerance 10.0]
"""

from __future__ import annotations

import logging
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from rich.console import Console
from rich.table import Table

from src.services.calibration import CalibrationService
from src.services.ctdi_calculator import CTDICalculator, PRIMARY_SCORER

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
console = Console()

DEFAULT_CALIBRATION_PATH = "calibration.example.yaml"
DEFAULT_RUNFOLDER_DIR = "runfolder"


@dataclass
class CrossValidationResult:
    """Result of cross-validating a single run-folder against a DCF."""

    runfolder: str
    kV: int
    fan_mode: str
    exposure_mAs: float
    total_histories: int
    raw_Gy: float
    dcf_applied: float
    calibrated_mGy: float
    reference_mAs: float
    reference_ctdi_w_mGy: float
    expected_mGy: float
    error_pct: float
    pass_fail: str


def extract_runfolder_metadata(runfolder: Path) -> Optional[Dict]:
    """Extract kV, fan_mode, exposure_mAs, total_histories from metadata."""
    metadata_path = runfolder / "simulation_metadata.yaml"
    if not metadata_path.exists():
        return None
    try:
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = yaml.safe_load(f)
        if not isinstance(metadata, dict):
            return None

        spekpy = metadata.get("spekpy", {})
        kvp = spekpy.get("kvp")
        if kvp is None:
            return None

        fan_mode = metadata.get("fan_mode")
        if fan_mode is None:
            return None

        # Old format uses "mAs", new format uses "exposure_mAs"
        mAs = metadata.get("exposure_mAs") or metadata.get("mAs", 0.0)
        total_histories = metadata.get("total_histories", 0)

        return {
            "kV": int(kvp),
            "fan_mode": fan_mode,
            "exposure_mAs": float(mAs),
            "total_histories": int(total_histories),
        }
    except (KeyError, TypeError, ValueError, yaml.YAMLError):
        return None


def cross_validate(
    calibration_path: Path,
    runfolder_dir: Path,
    tolerance_pct: float = 10.0,
) -> List[CrossValidationResult]:
    """Run cross-validation across all run-folders."""
    calib_svc = CalibrationService(calibration_path)
    results: List[CrossValidationResult] = []

    runfolders = sorted([d for d in runfolder_dir.iterdir() if d.is_dir()])

    for rf in runfolders:
        meta = extract_runfolder_metadata(rf)
        if meta is None:
            logger.debug("Skipping %s: no usable metadata", rf.name)
            continue

        kV = meta["kV"]
        fan_mode = meta["fan_mode"]
        exposure_mAs = meta["exposure_mAs"]
        total_histories = meta["total_histories"]

        if exposure_mAs <= 0:
            logger.debug("Skipping %s: exposure_mAs=%s", rf.name, exposure_mAs)
            continue

        # Look up DCF
        dcf = calib_svc.lookup_dcf(kV, fan_mode)
        if dcf is None:
            logger.debug("Skipping %s: no DCF for (%d kV, %s)", rf.name, kV, fan_mode)
            continue

        # Look up reference values from calibration entry
        entry = calib_svc._calibration.find_entry(kV, fan_mode)
        if entry is None or entry.reference_ctdi_w_mGy is None:
            logger.debug(
                "Skipping %s: no reference CTDI-w for (%d kV, %s)",
                rf.name,
                kV,
                fan_mode,
            )
            continue

        reference_ctdi_w_mGy = entry.reference_ctdi_w_mGy
        reference_mAs = entry.reference_mAs

        if reference_mAs is None or reference_mAs <= 0:
            logger.debug(
                "Skipping %s: no reference_mAs for (%d kV, %s)",
                rf.name,
                kV,
                fan_mode,
            )
            continue

        # Compute raw CTDI-w (TLE scorer)
        try:
            calculator = CTDICalculator(rf)
            calc_results = calculator.calculate()
        except (FileNotFoundError, ValueError) as exc:
            logger.warning("Error processing %s: %s", rf.name, exc)
            continue

        # Find TLE result
        tle_result = None
        for cr in calc_results:
            if cr.get("scorer_type") == PRIMARY_SCORER:
                tle_result = cr
                break

        if tle_result is None:
            logger.warning("No TLE result in %s", rf.name)
            continue

        raw_sum = tle_result.get("raw_sum", 0.0)

        # Compute photons_per_mAs (constant for kV, independent of mAs and histories)
        result_metadata = tle_result.get("metadata", {})
        th = result_metadata.get("total_histories", 0)
        spectrum_fluence = result_metadata.get("spectrum_fluence_photons_per_mAs")
        old_norm = result_metadata.get("norm_factor")

        if spectrum_fluence and spectrum_fluence > 0 and exposure_mAs > 0:
            photons_per_mAs = spectrum_fluence * th / exposure_mAs
        elif old_norm:
            photons_per_mAs = old_norm * th
        else:
            logger.warning("Cannot compute photons_per_mAs for %s", rf.name)
            continue

        raw_Gy = raw_sum * photons_per_mAs * exposure_mAs
        calibrated_Gy = raw_Gy * dcf
        calibrated_mGy = calibrated_Gy * 1000.0  # DCF converts Gy→Gy

        # Expected: reference scaled by mAs ratio
        mAs_ratio = exposure_mAs / reference_mAs
        expected_mGy = reference_ctdi_w_mGy * mAs_ratio

        if expected_mGy > 0:
            error_pct = (calibrated_mGy - expected_mGy) / expected_mGy * 100
        else:
            error_pct = float("inf")

        status = "PASS" if abs(error_pct) <= tolerance_pct else "FAIL"

        results.append(
            CrossValidationResult(
                runfolder=rf.name,
                kV=kV,
                fan_mode=fan_mode,
                exposure_mAs=exposure_mAs,
                total_histories=total_histories,
                raw_Gy=raw_Gy,
                dcf_applied=dcf,
                calibrated_mGy=calibrated_mGy,
                reference_mAs=reference_mAs,
                reference_ctdi_w_mGy=reference_ctdi_w_mGy,
                expected_mGy=expected_mGy,
                error_pct=error_pct,
                pass_fail=status,
            )
        )

    return results


def format_report(results: List[CrossValidationResult]) -> str:
    """Format results as a Rich table."""
    if not results:
        return "No cross-validation results (no matching run-folders found)."

    table = Table(title="Cross-Validation: Calibration DCF Consistency")
    table.add_column("Runfolder", style="cyan", max_width=28)
    table.add_column("kV", justify="right")
    table.add_column("Fan", justify="center")
    table.add_column("Run mAs", justify="right")
    table.add_column("Histories", justify="right")
    table.add_column("Raw Gy", justify="right")
    table.add_column("DCF", justify="right")
    table.add_column("Cal. mGy", justify="right")
    table.add_column("Exp. mGy", justify="right")
    table.add_column("Err %", justify="right")
    table.add_column("Status", justify="center")

    for r in results:
        err_style = "bold red" if r.pass_fail == "FAIL" else "bold green"
        table.add_row(
            r.runfolder,
            str(r.kV),
            "FF" if "Full" in r.fan_mode else "HF",
            "{:.1f}".format(r.exposure_mAs),
            "{:.0e}".format(r.total_histories),
            "{:.4e}".format(r.raw_Gy),
            "{:.2f}".format(r.dcf_applied),
            "{:.3f}".format(r.calibrated_mGy),
            "{:.3f}".format(r.expected_mGy),
            "{:+.2f}".format(r.error_pct),
            "[{}]{}[/]".format(err_style, r.pass_fail),
        )

    return table


def print_summary(results: List[CrossValidationResult], tolerance_pct: float) -> None:
    """Print per-(kV, fan_mode) summary statistics."""
    console.print("\n[bold]Per-Configuration Summary:[/bold]\n")

    # Group by (kV, fan_mode)
    groups: Dict[tuple, List[CrossValidationResult]] = {}
    for r in results:
        key = (r.kV, r.fan_mode)
        groups.setdefault(key, []).append(r)

    for (kV, fan_mode), group in sorted(groups.items()):
        fan_short = "FF" if "Full" in fan_mode else "HF"
        dcf = group[0].dcf_applied
        ref_mGy = group[0].reference_ctdi_w_mGy
        ref_mAs = group[0].reference_mAs
        errors = [r.error_pct for r in group]

        n_pass = sum(1 for e in errors if abs(e) <= tolerance_pct)
        n_fail = len(errors) - n_pass
        max_err = max(abs(e) for e in errors)
        avg_err = sum(errors) / len(errors)
        std_err = (
            math.sqrt(sum((e - avg_err) ** 2 for e in errors) / len(errors))
            if len(errors) > 1
            else 0.0
        )

        status = (
            "[bold green]ALL PASS[/bold green]"
            if n_fail == 0
            else ("[bold red]{}/{} FAIL[/bold red]".format(n_fail, len(errors)))
        )

        console.print(
            "  {} kV {} (DCF={:.2f}, ref={:.1f} mGy @ {:.0f} mAs): "
            "{} runs, avg err={:+.3f}%, std={:.3f}%, max={:.3f}% — {}".format(
                kV,
                fan_short,
                dcf,
                ref_mGy,
                ref_mAs,
                len(errors),
                avg_err,
                std_err,
                max_err,
                status,
            )
        )

    total_pass = sum(1 for r in results if r.pass_fail == "PASS")
    total_fail = len(results) - total_pass
    console.print(
        "\n[bold]Total: {}/{} PASS, {}/{} FAIL (tolerance: {:.1f}%)[/bold]".format(
            total_pass,
            len(results),
            total_fail,
            len(results),
            tolerance_pct,
        )
    )


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Cross-validate calibration DCFs against run-folders"
    )
    parser.add_argument(
        "--calibration",
        "-c",
        default=DEFAULT_CALIBRATION_PATH,
        help="Path to calibration YAML file (default: {})".format(
            DEFAULT_CALIBRATION_PATH
        ),
    )
    parser.add_argument(
        "--runfolder-dir",
        "-r",
        default=DEFAULT_RUNFOLDER_DIR,
        help="Directory containing run-folders (default: {})".format(
            DEFAULT_RUNFOLDER_DIR
        ),
    )
    parser.add_argument(
        "--tolerance",
        "-t",
        type=float,
        default=10.0,
        help="Tolerance in percent (default: 10.0)",
    )
    args = parser.parse_args()

    calibration_path = Path(args.calibration)
    runfolder_dir = Path(args.runfolder_dir)

    if not calibration_path.exists():
        console.print(
            "Error: calibration file not found: {}".format(calibration_path),
            style="red",
        )
        sys.exit(1)

    if not runfolder_dir.exists():
        console.print(
            "Error: runfolder directory not found: {}".format(runfolder_dir),
            style="red",
        )
        sys.exit(1)

    console.print(
        "Cross-validating DCFs from [cyan]{}[/cyan] against [cyan]{}[/cyan]\n".format(
            calibration_path,
            runfolder_dir,
        )
    )

    results = cross_validate(calibration_path, runfolder_dir, args.tolerance)

    if not results:
        console.print(
            "No matching run-folders found. "
            "Ensure run-folders have simulation_metadata.yaml with kV and fan_mode.",
            style="yellow",
        )
        sys.exit(1)

    console.print(format_report(results))
    print_summary(results, args.tolerance)


if __name__ == "__main__":
    main()
