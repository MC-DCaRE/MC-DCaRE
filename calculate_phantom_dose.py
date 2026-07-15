#!/usr/bin/env python3
"""CLI for computing organ and effective dose from phantom mode simulations.

Usage:
    uv run python calculate_phantom_dose.py <runfolder> [options]

Examples:
    # Compute with CTDIw anchoring
    uv run python calculate_phantom_dose.py runfolder/2026-06-30_13-04-13/ \\
        --ctdiw 15.9

    # Without absolute calibration (raw doses only)
    uv run python calculate_phantom_dose.py runfolder/2026-06-30_13-04-13/
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

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
        "--ctdiw",
        type=float,
        default=None,
        help="Measured CTDIw in mGy for absolute dose anchoring",
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

    # Auto-detect file paths
    dose_csv = runfolder / "phantom_dose.csv"
    if not dose_csv.exists():
        print(f"ERROR: {dose_csv} not found", file=sys.stderr)
        sys.exit(1)

    # Try to find voxel grid and material file
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

    if not voxel_grid.exists():
        print(f"ERROR: Voxel grid not found: {voxel_grid}", file=sys.stderr)
        sys.exit(1)
    if not material_file.exists():
        print(f"ERROR: Material file not found: {material_file}", file=sys.stderr)
        sys.exit(1)

    # Calculate
    calc = PhantomDoseCalculator(dose_csv, voxel_grid, material_file)
    result = calc.calculate(ctdiw_mGy=args.ctdiw)

    # Print report
    print(calc.format_report(result))

    # Optionally save organ dose CSV
    if args.output:
        import csv

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
                    ]
                )
        print(f"\nOrgan dose table saved to: {args.output}")


if __name__ == "__main__":
    main()
