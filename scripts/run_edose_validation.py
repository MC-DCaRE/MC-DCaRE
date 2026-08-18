#!/usr/bin/env python3
"""Effective-dose validation across all CBCT protocols with reference doses.

For each protocol in data/protocol_reference_table.yaml with a non-null
dose_mSv reference, runs the voxelized ICRP 145 MRCP-AM phantom at 5M total
histories (33334 x 150 sequential times), computes the DCF-calibrated
effective dose (TLE scorer), and tabulates simulated vs reference dose.

Usage:
    uv run python scripts/run_edose_validation.py [--threads 20] [--dry-run]
"""

from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

import yaml

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

from run_full_calibration import (  # noqa: E402
    PROJECT_ROOT,
    load_and_patch_config,
    run_simulation,
    run_topas,
    swap_voxel_phantom,
    write_temp_config,
)

REFERENCE_TABLE = PROJECT_ROOT / "data" / "protocol_reference_table.yaml"
PHANTOM_CONFIG = "configs/phantom_pelvis_mrcp_am.yaml"
OUTPUT_BASE = "edose_validation_runs"
ROTATION = "CBCT Anticlockwise"

# 5M total histories, rotational sampling matched to the production runs
HIST_PER_SEQ = "33334"  # x 150 sequential times = 5,000,100 total

# Region isocenters (mm, phantom frame) from MRCP-AM organ centroids -- the
# same placement the 2026-08-13 phase-space replay study used
# (docs/validation_results/README.md). The beam aims at world Z=0, so the
# phantom is shifted DOWN by the isocenter to bring the target region in.
ISOCENTER_Z_MM = {
    "4D Spotlight": 460,
    "4D Thorax": 460,
    "Abdo Spotlight": 200,
    "Abdomen": 200,
    "Breast 360": 460,
    "Extremity Spotlight": -200,
    "Head": 795,
    "Head and Shoulders": 600,
    "Head SRS": 795,
    "Pelvis": 0,
    "Pelvis Spotlight": 0,
    "SBRT Spine": 300,
    "Thorax": 460,
    "Thorax Spotlight": 460,
}

# Baseline Z placement baked into the static swapped phantomVoxel.txt
VOXEL_BASELINE_TRANSZ_CM = 0.64


def apply_isocenter(rundir: str, iso_z_mm: float) -> None:
    """Shift the swapped voxel phantom so iso_z_mm sits at the beam plane.

    The static ``phantomVoxel.txt`` hardcodes ``Ge/Phantom/TransZ`` (config
    ``phantom.trans_z`` is ignored on the voxel-swap path), so the runfolder
    file is patched directly: TransZ = baseline - iso_z_mm/10 (cm).
    """
    voxel_file = Path(rundir) / "phantomVoxel.txt"
    new_z = VOXEL_BASELINE_TRANSZ_CM - iso_z_mm / 10.0
    content = voxel_file.read_text()
    patched = re.sub(
        r"d:Ge/Phantom/TransZ = [-\d.]+ cm",
        f"d:Ge/Phantom/TransZ = {new_z:.3f} cm",
        content,
        count=1,
    )
    if patched == content:
        raise RuntimeError(f"TransZ line not found in {voxel_file}")
    voxel_file.write_text(patched)
    print(f"    Isocenter Z = {iso_z_mm:.0f} mm (TransZ -> {new_z:.3f} cm)")


def load_protocols() -> List[Dict]:
    """Return protocols from the reference table that have a reference E."""
    with open(REFERENCE_TABLE) as f:
        data = yaml.safe_load(f)
    return [p for p in data["protocols"] if p.get("dose_mSv") is not None]


def compute_effective_dose(rundir: str) -> Optional[float]:
    """Run calculate_phantom_dose.py and parse the effective dose (mSv)."""
    result = subprocess.run(
        [
            sys.executable,
            "calculate_phantom_dose.py",
            rundir,
            "--dose-file",
            "phantom_tle.csv",
            "--voxel-grid",
            str(PROJECT_ROOT / "test_voxel_output" / "mrcp_am" / "mrcp_am_voxels.npy"),
            "--calibration",
            str(PROJECT_ROOT / "calibration.yaml"),
            "--output",
            str(Path(rundir) / "organ_doses.csv"),
        ],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
    )
    if result.returncode != 0:
        print(f"    ERROR: calculate_phantom_dose failed:\n{result.stderr[:500]}")
        return None
    for line in result.stdout.splitlines():
        if line.startswith("EFFECTIVE DOSE"):
            match = re.search(r"([\d.]+)\s*mSv", line)
            if match:
                return float(match.group(1))
    print(f"    WARNING: no effective dose in report:\n{result.stdout[:300]}")
    return None


def render_dose_cubes(rundir: str) -> List[str]:
    """Render TLE + DTM dose-cube views into the runfolder (diagnostics).

    TLE shows fluence/kerma structure; DTM shows actual deposition -- the
    pair was decisive for diagnosing the collimator leak (uniform TLE with
    DTM glow at head/feet). Failures are logged, never fatal.
    """
    sys.path.insert(0, str(PROJECT_ROOT / "tools"))
    from render_dose_cube import render

    paths: List[str] = []
    for dose_file in ("phantom_tle.csv", "phantom_dtm.csv"):
        try:
            paths.append(str(render(Path(rundir), dose_file)))
        except Exception as e:  # noqa: BLE001
            print(f"    WARNING: render {dose_file} failed: {e}")
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--threads", default="20", help="TOPAS threads (default 20)")
    parser.add_argument(
        "--hist-per-seq",
        default=HIST_PER_SEQ,
        help=f"Histories per sequential time (default {HIST_PER_SEQ} = 5M total)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Generate only")
    parser.add_argument(
        "--no-render",
        action="store_true",
        help="Skip dose-cube PNG rendering (default renders TLE + DTM)",
    )
    args = parser.parse_args()

    protocols = load_protocols()
    print("=" * 70)
    print(f"  Effective-Dose Validation ({len(protocols)} protocols, 5M histories)")
    print("=" * 70)

    rows: List[Dict] = []
    t0 = time.time()
    for i, p in enumerate(protocols, 1):
        name = p["name"]
        print(f"\n[{i}/{len(protocols)}] {name} ({p['kV']} kV, {p['fan']})")
        overrides = {
            "general": {"threads": args.threads, "histories": args.hist_per_seq},
            "imaging": {
                "rotation_direction": ROTATION,
                "imaging_mode": name,
                "exposure": f"{p['exposure_mAs']} mAs",
                "sequential_times": "150",
            },
        }
        data = load_and_patch_config(PHANTOM_CONFIG, overrides)
        temp_path = write_temp_config(
            data, f"edose_{re.sub(r'[^a-z0-9]+', '_', name.lower())}"
        )

        try:
            rundir = run_simulation(temp_path, OUTPUT_BASE, dry_run=True)
            swap_voxel_phantom(rundir)
            apply_isocenter(rundir, ISOCENTER_Z_MM[name])
            if args.dry_run:
                print(f"    [DRY RUN] {rundir}")
                continue
            rc = run_topas(rundir)
            if rc != 0:
                rows.append({"protocol": name, "status": "topas_failed", **_meta(p)})
                continue
            e_sim = compute_effective_dose(rundir)
            if not args.no_render:
                render_dose_cubes(rundir)
        except Exception as e:  # noqa: BLE001
            print(f"    ERROR: {e}")
            rows.append({"protocol": name, "status": f"error: {e}", **_meta(p)})
            continue

        if e_sim is None:
            rows.append({"protocol": name, "status": "no_result", **_meta(p)})
            continue
        e_ref = float(p["dose_mSv"])
        diff = (e_sim - e_ref) / e_ref * 100 if e_ref > 0 else float("nan")
        rows.append(
            {
                "protocol": name,
                "status": "ok",
                **_meta(p),
                "e_sim_mSv": round(e_sim, 3),
                "e_ref_mSv": e_ref,
                "diff_pct": round(diff, 1),
                "rundir": rundir,
            }
        )
        print(f"    E_sim = {e_sim:.2f} mSv vs E_ref = {e_ref:.1f} mSv ({diff:+.1f}%)")

    _write_report(rows, args.dry_run)
    print(f"\nTotal elapsed: {(time.time() - t0) / 60:.1f} min")


def _meta(p: Dict) -> Dict:
    return {
        "kV": p["kV"],
        "fan": "Half Fan" if "LFOV" in p["fan"] else "Full Fan",
        "mAs": p["exposure_mAs"],
    }


def _write_report(rows: List[Dict], dry_run: bool) -> None:
    out_dir = PROJECT_ROOT / OUTPUT_BASE
    csv_path = out_dir / "validation_results.csv"
    if not dry_run and rows:
        out_dir.mkdir(exist_ok=True)
        # Fixed fieldnames: failure rows carry fewer keys than ok rows; an
        # ok-first derivation crashes on the first mixed-shape sweep.
        fieldnames = [
            "protocol",
            "status",
            "kV",
            "fan",
            "mAs",
            "e_sim_mSv",
            "e_ref_mSv",
            "diff_pct",
            "rundir",
        ]
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"\nCSV: {csv_path}")

    print("\n| Protocol | kV | Fan | mAs | E_sim (mSv) | E_ref (mSv) | Diff |")
    print("|---|---|---|---|---|---|---|")
    for r in rows:
        if r.get("status") == "ok":
            print(
                f"| {r['protocol']} | {r['kV']} | {r['fan']} | {r['mAs']} "
                f"| {r['e_sim_mSv']:.2f} | {r['e_ref_mSv']:.1f} | {r['diff_pct']:+.1f}% |"
            )
        else:
            print(
                f"| {r['protocol']} | {r['kV']} | {r['fan']} | {r['mAs']} | - | - | {r['status']} |"
            )


if __name__ == "__main__":
    main()
