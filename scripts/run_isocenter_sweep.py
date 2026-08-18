#!/usr/bin/env python3
"""Pelvis isocenter sensitivity study.

Tests whether the pelvis effective-dose gap vs literature (3.04 mSv here vs
7.05 mSv Abuhaimed 2018 EGSnrc MC at the same technique) is explained by
craniocaudal isocenter placement. Re-runs the Pelvis protocol (125 kV HF,
1074 mAs, 5M histories) at +-20 / +-40 mm shifts around the baseline
isocenter and reports E plus the partial-irradiation tissue HTs (colon,
bone marrow) and prostate/testes organ doses.

Usage:
    uv run python scripts/run_isocenter_sweep.py [--shifts -40,-20,20,40]
"""

from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

import pandas as pd

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

from run_edose_validation import (  # noqa: E402
    HIST_PER_SEQ,
    OUTPUT_BASE,
    PHANTOM_CONFIG,
    apply_isocenter,
    compute_effective_dose,
    load_and_patch_config,
    render_dose_cubes,
    run_simulation,
    run_topas,
    swap_voxel_phantom,
    write_temp_config,
)

PELVIS_ISO_MM = 0.0
PROTOCOL = {
    "name": "Pelvis",
    "kV": 125,
    "fan": "Half Fan",
    "exposure_mAs": 1074.0,
    "dose_mSv": 4.2,
}


def tissue_ht(df: pd.DataFrame, tissue: str) -> float:
    """Arithmetic organ-mean HT for one ICRP 103 tissue (calculator default)."""
    sub = df[df["icrp103_tissue"] == tissue]
    return float(sub["mean_mGy"].mean()) if len(sub) else 0.0


def organ_dose(df: pd.DataFrame, pattern: str) -> float:
    sub = df[df["organ"].str.contains(pattern, case=False, regex=True)]
    return float(sub["mean_mGy"].mean()) if len(sub) else float("nan")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--shifts",
        default="-40,-20,20,40",
        help="Comma-separated isocenter shifts in mm (default -40,-20,20,40)",
    )
    parser.add_argument(
        "--hist-per-seq",
        default=HIST_PER_SEQ,
        help="Histories per sequential time (default 33334 = 5M total)",
    )
    args = parser.parse_args()
    shifts = [float(s) for s in args.shifts.split(",")]

    print("=" * 70)
    print("  Pelvis isocenter sensitivity (125 kV HF, 1074 mAs, 5M hist)")
    print("=" * 70)

    rows: List[Dict] = []
    for shift in shifts:
        iso = PELVIS_ISO_MM + shift
        print(f"\n[shift {shift:+.0f} mm -> iso {iso:.0f} mm]")
        overrides = {
            "general": {"threads": "20", "histories": args.hist_per_seq},
            "imaging": {
                "rotation_direction": "CBCT Anticlockwise",
                "imaging_mode": PROTOCOL["name"],
                "exposure": f"{PROTOCOL['exposure_mAs']} mAs",
                "sequential_times": "150",
            },
        }
        data = load_and_patch_config(PHANTOM_CONFIG, overrides)
        temp_path = write_temp_config(data, f"isosweep_{int(shift):+d}")

        try:
            rundir = run_simulation(temp_path, OUTPUT_BASE, dry_run=True)
            swap_voxel_phantom(rundir)
            apply_isocenter(rundir, iso)
            rc = run_topas(rundir)
            if rc != 0:
                print(f"    TOPAS failed (rc={rc})")
                continue
            out_csv = Path(rundir) / "organ_doses.csv"
            result = subprocess.run(
                [
                    sys.executable,
                    "calculate_phantom_dose.py",
                    rundir,
                    "--dose-file",
                    "phantom_tle.csv",
                    "--voxel-grid",
                    "test_voxel_output/mrcp_am/mrcp_am_voxels.npy",
                    "--calibration",
                    "calibration.yaml",
                    "--output",
                    str(out_csv),
                ],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                print(f"    post-processing failed:\n{result.stderr[-400:]}")
                continue
            df = pd.read_csv(out_csv)
            e = compute_effective_dose(rundir)
            if e is None:
                continue
            render_dose_cubes(rundir)
        except Exception as e_:  # noqa: BLE001
            print(f"    ERROR: {e_}")
            continue

        row = {
            "shift_mm": shift,
            "iso_mm": iso,
            "e_sim_mSv": round(e, 3),
            "ht_colon_mGy": round(tissue_ht(df, "colon"), 2),
            "ht_marrow_mGy": round(tissue_ht(df, "bone_marrow"), 2),
            "ht_remainder_mGy": round(tissue_ht(df, "remainder"), 2),
            "prostate_mGy": round(organ_dose(df, r"^Prostate$"), 2),
            "testes_mGy": round(organ_dose(df, r"^Testis_"), 2),
            "rundir": rundir,
        }
        rows.append(row)
        print(
            f"    E={row['e_sim_mSv']:.2f} colon={row['ht_colon_mGy']:.1f} "
            f"marrow={row['ht_marrow_mGy']:.1f} prostate={row['prostate_mGy']:.1f} "
            f"testes={row['testes_mGy']:.1f}"
        )

    out_dir = Path(OUTPUT_BASE)
    out_dir.mkdir(exist_ok=True)
    with open(out_dir / "isocenter_sensitivity_pelvis.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print("\nBaseline (shift 0) reference: edose_validation_runs Pelvis run")
    print("Literature anchors: Abuhaimed 2018 male V2.5 -- E 7.05, colon 12.96,")
    print("marrow(RBM whole body) 15.09, prostate 39.28, testes 4.74 mGy")


if __name__ == "__main__":
    main()
