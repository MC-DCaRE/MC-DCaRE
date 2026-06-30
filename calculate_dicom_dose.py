#!/usr/bin/env python3
"""CLI for normalizing DICOM patient dose simulations.

Applies DCF normalization from calibration.yaml to the 3D dose grid
produced by DICOM mode TOPAS simulations. Supports partial scan dose
estimation via --target-mAs.

Usage:
    uv run python calculate_dicom_dose.py <runfolder> [options]

Examples:
    # Fully automatic (reads calibration.yaml + simulation_metadata.yaml)
    uv run python calculate_dicom_dose.py runfolder/2026-06-12_15-00-00/

    # Scale to a partial scan
    uv run python calculate_dicom_dose.py runfolder/2026-06-12_15-00-00/ \\
        --target-mAs 500
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.services.calibration import CalibrationService


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Normalize DICOM patient dose from TOPAS simulation output"
    )
    parser.add_argument(
        "runfolder",
        help="Path to the simulation runfolder",
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
        "--output",
        default=None,
        help="Output file for calibrated dose summary (default: stdout)",
    )
    args = parser.parse_args()

    runfolder = Path(args.runfolder)

    # Find dose CSV files in the runfolder
    dose_files = sorted(runfolder.glob("*_DOSE_*.csv"))
    if not dose_files:
        # Also try the bin format
        dose_files = sorted(runfolder.glob("*_DOSE_*.bin"))
    if not dose_files:
        print(f"ERROR: No dose output files found in {runfolder}", file=sys.stderr)
        sys.exit(1)

    # Set up calibration
    cal_path = Path(args.calibration)
    if not cal_path.exists():
        print(f"ERROR: {cal_path} not found", file=sys.stderr)
        sys.exit(1)

    try:
        cal_service = CalibrationService(cal_path)
        metadata = CalibrationService.read_metadata(runfolder)
    except Exception as e:
        print(f"ERROR: Could not read calibration or metadata: {e}", file=sys.stderr)
        sys.exit(1)

    kV = metadata.get("kV", 0)
    fan_mode = metadata.get("fan_mode", "")
    total_histories = metadata.get("total_histories", 0)
    exposure_mAs = metadata.get("exposure_mAs", 0.0)

    print("=== DICOM Dose Normalization ===")
    print(f"Runfolder: {runfolder}")
    print(f"kV: {kV}, Fan mode: {fan_mode}")
    print(f"Histories: {total_histories:,}, Simulated mAs: {exposure_mAs}")
    print()

    # Process each dose file
    for dose_file in dose_files:
        print(f"Processing: {dose_file.name}")

        # Read the dose CSV (TOPAS DoseToMedium format)
        with open(dose_file) as f:
            for _ in range(20):  # Skip header lines
                next(f)
            doses = []
            for line in f:
                if line.startswith("#") or not line.strip():
                    continue
                parts = line.strip().split(", ")
                if len(parts) >= 4:
                    doses.append(float(parts[-1]))

        if not doses:
            print("  WARNING: No dose data found")
            continue

        import numpy as np

        doses = np.array(doses)
        nonzero = doses[doses > 0]

        print(f"  Total voxels: {len(doses):,}")
        print(f"  Non-zero: {len(nonzero):,} ({100 * len(nonzero) / len(doses):.1f}%)")

        if len(nonzero) == 0:
            print("  WARNING: All doses are zero")
            continue

        # Apply normalization to each voxel
        # Use mean dose as representative for getting normalization constants
        mean_raw = float(np.mean(nonzero))
        norm = cal_service.normalize_dose(
            mean_raw,
            metadata,
            target_mAs=args.target_mAs,
            dcf_override=args.dcf,
        )

        scale = (
            norm.calibrated_Gy / mean_raw
            if norm.calibrated_Gy
            else norm.raw_Gy / mean_raw
        )
        calibrated_doses = doses * scale

        max_dose_mGy = float(np.max(calibrated_doses[doses > 0])) * 1000
        mean_dose_mGy = float(np.mean(calibrated_doses[doses > 0])) * 1000

        print(f"  DCF: {norm.dcf} (source: {norm.dcf_source})")
        print(f"  photons_per_mAs: {norm.photons_per_mAs:.4e}")
        print(f"  mAs used: {norm.mAs_used:.1f}")
        print(f"  Max dose: {max_dose_mGy:.4f} mGy")
        print(f"  Mean dose (non-zero): {mean_dose_mGy:.4f} mGy")
        print()

        # Write calibrated dose file
        if args.output:
            out_path = Path(args.output)
        else:
            out_path = dose_file.with_suffix(".calibrated.csv")

        with open(out_path, "w") as f:
            f.write("# Calibrated DICOM dose (DCF normalization)\n")
            f.write(f"# DCF: {norm.dcf} (source: {norm.dcf_source})\n")
            f.write(f"# photons_per_mAs: {norm.photons_per_mAs:.6e}\n")
            f.write(
                f"# mAs: {norm.mAs_used:.1f} (simulated: {norm.mAs_simulated:.1f})\n"
            )
            f.write("# Calibrated Dose (Gy)\n")
            for d in calibrated_doses:
                f.write(f"{d:.10e}\n")
            print(f"  Calibrated dose written to: {out_path}")

    print()
    print("=== Normalization complete ===")


if __name__ == "__main__":
    main()
