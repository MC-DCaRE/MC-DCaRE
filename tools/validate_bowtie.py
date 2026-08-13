"""CLI: compare a scored bow-tie profile against measured RaySafe data.

Usage::

    python tools/validate_bowtie.py \\
        --measured "research/2023 - CBCT Dose PCXMC/New results Oct 2023 (Spotlight, Raysafe X2) - fixed spotlight.xlsx" \\
        --mode-group 0 \\
        --mc-profile runfolder/profile.csv \\
        --output-csv bowtie_validation.csv \\
        --output-png bowtie_validation.png
"""

from __future__ import annotations

import argparse
import logging

from src.services.bowtie_validator import (
    compare_profiles,
    load_mc_profile,
    load_measured_profile,
)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
    parser = argparse.ArgumentParser(
        description="Validate the bow-tie profile vs measured data"
    )
    parser.add_argument("--measured", required=True, help="RaySafe workbook (.xlsx)")
    parser.add_argument(
        "--mode-group", type=int, default=0, help="Mode 4-col group index (0=Head)"
    )
    parser.add_argument(
        "--mc-profile", required=True, help="MC profile CSV (position_cm, dose)"
    )
    parser.add_argument("--output-csv", default="bowtie_validation.csv")
    parser.add_argument("--output-png", default="bowtie_validation.png")
    args = parser.parse_args()

    measured = load_measured_profile(args.measured, mode_group=args.mode_group)
    mc = load_mc_profile(args.mc_profile)
    result = compare_profiles(
        measured, mc, output_csv=args.output_csv, output_png=args.output_png
    )
    print("RMS misfit (peak-normalised): %.4f" % result["rms_misfit"])


if __name__ == "__main__":
    main()
