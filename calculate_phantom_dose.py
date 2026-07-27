#!/usr/bin/env python3
"""CLI for computing organ and effective dose from phantom mode simulations.

Automatically applies DCF normalization from calibration.yaml (the same
calibration database used for CTDI mode). Supports three scorer types
(TLE, DoseToWater, DoseToMedium) via ``--scorer-type``, and partial scan
dose estimation via ``--target-mAs``.

Usage:
    uv run python calculate_phantom_dose.py <runfolder> [options]

Examples:
    # Default scorer type is dtm (matches TsTetGeomScorer/DoseToMedium output)
    uv run python calculate_phantom_dose.py runfolder/2026-07-02_05-19-13/

    # DoseToWater scorer
    uv run python calculate_phantom_dose.py runfolder/2026-07-02_05-19-13/ \\
        --scorer-type dtw

    # Scale to a partial scan (500 mAs instead of simulated 1074)
    uv run python calculate_phantom_dose.py runfolder/2026-07-02_05-19-13/ \\
        --target-mAs 500

    # Manual DCF override
    uv run python calculate_phantom_dose.py runfolder/2026-07-02_05-19-13/ \\
        --dcf 1.634e-03
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from src.services.calibration import CalibrationService
from src.services.phantom_dose_calculator import PhantomDoseCalculator


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute organ and effective dose from phantom simulation output"
    )
    parser.add_argument(
        "runfolder",
        help="Path to the simulation runfolder containing phantom_dose.csv",
    )
    parser.add_argument(
        "--calibration",
        default="calibration.yaml",
        help="Path to calibration.yaml (default: calibration.yaml)",
    )
    parser.add_argument(
        "--target-mAs",
        type=float,
        default=None,
        help="Scale dose to this mAs (for partial scans)",
    )
    parser.add_argument(
        "--dcf",
        type=float,
        default=None,
        help="DCF override (skips calibration.yaml lookup)",
    )
    parser.add_argument(
        "--scorer-type",
        default="dtm",
        choices=["tle", "dtw", "dtm"],
        help="Scorer type for DCF lookup (default: dtm, matching the "
        "phantom TsTetGeomScorer/DoseToMedium output)",
    )
    parser.add_argument(
        "--dose-file",
        default=None,
        help="Override dose CSV filename (default: auto-detect from scorer-type)",
    )
    parser.add_argument(
        "--voxel-grid",
        default=None,
        help="Path to the .npy material ID grid (default: auto-detect)",
    )
    parser.add_argument(
        "--material-file",
        default=None,
        help="Path to the ICRP 145 .material file (default: auto-detect)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output CSV path for organ dose table",
    )
    args = parser.parse_args()

    runfolder = Path(args.runfolder)

    # Phantom mode emits a single TsTetGeomScorer/DoseToMedium file
    # (phantom_dose.csv); --dose-file overrides the filename if needed.
    dose_csv = runfolder / (args.dose_file or "phantom_dose.csv")
    if not dose_csv.exists():
        print(f"ERROR: {dose_csv} not found", file=sys.stderr)
        sys.exit(1)

    project_root = Path(__file__).parent
    voxel_grid = (
        Path(args.voxel_grid)
        if args.voxel_grid
        else project_root / "test_voxel_output" / "mrcp_am" / "mrcp_am_voxels.npy"
    )
    material_file = (
        Path(args.material_file)
        if args.material_file
        else project_root
        / "data"
        / "P145"
        / "Phantom_data"
        / "MRCP_AM"
        / "MRCP_AM.material"
    )

    for p, desc in [(voxel_grid, "voxel grid"), (material_file, "material file")]:
        if not p.exists():
            print(f"ERROR: {desc} not found: {p}", file=sys.stderr)
            sys.exit(1)

    # Set up calibration service
    cal_service: CalibrationService | None = None
    metadata: dict | None = None
    cal_path = Path(args.calibration)

    if cal_path.exists():
        try:
            cal_service = CalibrationService(cal_path)
            metadata = CalibrationService.read_metadata(runfolder)
            print(f"Calibration: {cal_path}")
            print(f"  kV={metadata.get('kV')}, fan_mode={metadata.get('fan_mode')}")
        except Exception as e:
            print(f"WARNING: Could not load calibration: {e}", file=sys.stderr)
            cal_service = None
    else:
        print(
            f"WARNING: {cal_path} not found, returning uncalibrated doses",
            file=sys.stderr,
        )

    # Calculate
    calc = PhantomDoseCalculator(dose_csv, voxel_grid, material_file)
    result = calc.calculate(
        calibration_service=cal_service,
        metadata=metadata,
        target_mAs=args.target_mAs,
        dcf_override=args.dcf,
        scorer_type=args.scorer_type,
    )

    # Print report
    print(calc.format_report(result))

    # Optionally save organ dose CSV with DCF provenance columns
    if args.output:
        norm = result.normalization
        dcf_val = norm.dcf if norm is not None else None
        dcf_source = norm.dcf_source if norm is not None else "none"
        with open(args.output, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "organ",
                    "icrp103_tissue",
                    "n_voxels",
                    "mean_mGy",
                    "std_mGy",
                    "sem_pct",
                    "dcf",
                    "dcf_source",
                ]
            )
            for r in result.organ_results:
                writer.writerow(
                    [
                        r.organ_name,
                        r.icrp103_tissue,
                        r.n_voxels,
                        f"{r.mean_dose_mGy:.6f}",
                        f"{r.std_dose_mGy:.6f}",
                        f"{r.sem_percent:.1f}",
                        dcf_val,
                        dcf_source,
                    ]
                )
        print(f"\nOrgan dose table saved to: {args.output}")


if __name__ == "__main__":
    main()
