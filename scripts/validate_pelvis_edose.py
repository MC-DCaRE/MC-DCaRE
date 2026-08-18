#!/usr/bin/env python3
"""Mask-off A/B experiment: does the primary-collimator mask explain the
E/CTDIw transfer drop? (Phase 2A of the beam-model hypothesis testing)

Runs, for one variant (baseline re-uses the production DCFs):
  1. CTDI calibration leg with the variant override (e.g. mask off) and a
     reduced history budget (hypothesis testing needs ratios, not precision).
  2. Variant DCF computed in-memory -- production calibration.yaml is NEVER
     modified by a variant run.
  3. Pelvis phantom leg with the same variant override, post-processed with
     the variant DCF (dcf_override), reported against the trusted anchors
     (Hauri 5.4 mSv, Abuhaimed 2023 pelvis 1.19 mSv/100 mAs).

Usage:
    uv run python scripts/validate_pelvis_edose.py --mask-off [--threads 20]
        [--cal-hist 100000] [--hist-per-seq 33334]
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Optional

SCRIPTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPTS_DIR.parent
sys.path.insert(0, str(SCRIPTS_DIR))
sys.path.insert(0, str(PROJECT_ROOT))

from run_edose_validation import (  # noqa: E402
    HIST_PER_SEQ,
    PHANTOM_CONFIG,
    ROTATION,
    load_and_patch_config,
    run_simulation,
    run_topas,
    swap_voxel_phantom,
    write_temp_config,
)
from run_full_calibration import ensure_calibration_yaml  # noqa: E402

KV, FAN, REF_CTDIW_MGY = 125, "Half Fan", 15.9
CAL_CONFIG = "configs/cal_125kv_hf_pelvis.yaml"
PROTOCOL = "Pelvis"
EXPOSURE_MAS = 1074
E_REF_PCXMC_MSV = 4.2
E_HAURI_MSV = 5.4
ABU_PELVIS_PER_100 = 1.19
VOXEL_GRID = PROJECT_ROOT / "test_voxel_output" / "mrcp_am" / "mrcp_am_voxels.npy"
MATERIAL = (
    PROJECT_ROOT / "data" / "P145" / "Phantom_data" / "MRCP_AM" / "MRCP_AM.material"
)


def compute_dcf_inmemory(cal_rundir: str) -> float:
    """Compute the variant DCF WITHOUT writing calibration.yaml."""
    from src.services.calibration import CalibrationService
    from src.services.ctdi_calculator import CTDICalculator

    cal_service = CalibrationService(ensure_calibration_yaml())
    raw = CTDICalculator(Path(cal_rundir)).calculate()
    primary = [r for r in raw if r.get("scorer_type") == "tle"]
    if not primary:
        raise RuntimeError("no TLE scorer results in %s" % cal_rundir)
    norm = cal_service.normalize(primary[0], KV, FAN)
    # normalize() returns ctdi_w_raw_Gy; reference is in mGy
    dcf = (REF_CTDIW_MGY / 1000.0) / norm["ctdi_w_raw_Gy"]
    print(f"  [variant] raw CTDIw: {norm['ctdi_w_raw_Gy']:.4e} Gy")
    print(f"  [variant] in-memory DCF: {dcf:.6e} (calibration.yaml untouched)")
    return dcf


def run_variant_cal(threads: str, cal_hist: str, imaging_over: Dict) -> str:
    data = load_and_patch_config(
        CAL_CONFIG,
        {
            "general": {"threads": threads, "histories": cal_hist},
            "imaging": imaging_over,
        },
    )
    temp_path = write_temp_config(data, "cal_variant_mask_ab")
    rundir = run_simulation(temp_path, "calibration_runs", dry_run=False)
    print(f"  [variant] cal leg done: {rundir}")
    return rundir


def run_phantom(
    threads: str, hist_per_seq: str, imaging_over: Dict, dcf: Optional[float]
) -> Dict[str, float]:
    overrides = {
        "general": {"threads": threads, "histories": hist_per_seq, "seed": "42"},
        "imaging": {
            "rotation_direction": ROTATION,
            "imaging_mode": PROTOCOL,
            "exposure": f"{EXPOSURE_MAS} mAs",
            "sequential_times": "150",
            **imaging_over,
        },
    }
    data = load_and_patch_config(PHANTOM_CONFIG, overrides)
    temp_path = write_temp_config(data, "edose_pelvis_variant")
    rundir = run_simulation(temp_path, "edose_validation_runs", dry_run=True)
    swap_voxel_phantom(rundir)
    t0 = time.time()
    rc = run_topas(rundir)
    if rc != 0:
        raise RuntimeError("phantom TOPAS run failed (rc=%d): %s" % (rc, rundir))
    print(
        f"  [variant] phantom run done in {(time.time() - t0) / 60:.1f} min: {rundir}"
    )
    cmd = [
        sys.executable,
        "calculate_phantom_dose.py",
        rundir,
        "--dose-file",
        "phantom_tle.csv",
        "--voxel-grid",
        str(VOXEL_GRID),
        "--calibration",
        str(PROJECT_ROOT / "calibration.yaml"),
        "--output",
        str(Path(rundir) / "organ_doses.csv"),
    ]
    if dcf is not None:
        cmd += ["--dcf", str(dcf)]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(PROJECT_ROOT))
    if result.returncode != 0:
        raise RuntimeError("calculate_phantom_dose failed: %s" % result.stderr[:400])
    for line in result.stdout.splitlines():
        if line.startswith("EFFECTIVE DOSE"):
            e = float(line.split()[-2])
            return {"e_mSv": e, "rundir": rundir}
    raise RuntimeError("no EFFECTIVE DOSE line in output")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mask-off", action="store_true")
    parser.add_argument(
        "--no-bowtie", action="store_true", help="bowtie_enabled=False (H2)"
    )
    parser.add_argument(
        "--bhf-geometric", action="store_true", help="bhf_mode=geometric (H3)"
    )
    parser.add_argument(
        "--no-aperture",
        action="store_true",
        help="housing_aperture_enabled=False (pre-Phase-8 baseline)",
    )
    parser.add_argument(
        "--cutoff-x", default=None, help="source_angular_cutoff_x in deg (e.g. 15.0)"
    )
    parser.add_argument(
        "--cutoff-y", default=None, help="source_angular_cutoff_y in deg (e.g. 12.0)"
    )
    parser.add_argument("--threads", default="20")
    parser.add_argument("--cal-hist", default="100000", help="cal leg histories/seq")
    parser.add_argument("--hist-per-seq", default=HIST_PER_SEQ)
    args = parser.parse_args()

    imaging_over: Dict = {}
    if args.mask_off:
        imaging_over["primary_mask_enabled"] = False
    if args.no_bowtie:
        imaging_over["bowtie_enabled"] = False
    if args.bhf_geometric:
        imaging_over["bhf_mode"] = "geometric"
    if args.no_aperture:
        imaging_over["housing_aperture_enabled"] = False
    if args.cutoff_x is not None:
        imaging_over["source_angular_cutoff_x"] = f"{args.cutoff_x} deg"
    if args.cutoff_y is not None:
        imaging_over["source_angular_cutoff_y"] = f"{args.cutoff_y} deg"
    flags = []
    if args.mask_off:
        flags.append("mask-off")
    if args.no_bowtie:
        flags.append("no-bowtie")
    if args.bhf_geometric:
        flags.append("bhf-geometric")
    if args.no_aperture:
        flags.append("no-aperture")
    if args.cutoff_x or args.cutoff_y:
        flags.append(f"cutoff {args.cutoff_x}/{args.cutoff_y} deg")
    label = " ".join(flags) if flags else "baseline"
    print(f"[1/3] {label} CTDI calibration leg ({args.cal_hist} hist/seq)")
    cal_rundir = run_variant_cal(args.threads, args.cal_hist, imaging_over)
    print("[2/3] variant DCF (in-memory)")
    dcf = compute_dcf_inmemory(cal_rundir)
    print(f"[3/3] {label} pelvis phantom leg ({EXPOSURE_MAS} mAs, 150 seq)")
    res = run_phantom(args.threads, args.hist_per_seq, imaging_over, dcf)
    e = res["e_mSv"]
    print(f"\n=== Pelvis effective dose ({label}) ===")
    print(f"  E = {e:.2f} mSv  (variant DCF {dcf:.4f})")
    print(f"  vs baseline-mask E 1.83 mSv (sweep)   : {100 * (e - 1.83) / 1.83:+.1f}%")
    print(
        f"  vs Hauri 2017 TLD 5.4 mSv             : {100 * (e - E_HAURI_MSV) / E_HAURI_MSV:+.1f}%"
    )
    print(
        f"  vs PCXMC 4.2 mSv (caveat)            : {100 * (e - E_REF_PCXMC_MSV) / E_REF_PCXMC_MSV:+.1f}%"
    )
    per100 = e / EXPOSURE_MAS * 100
    print(
        f"  per 100 mAs: {per100:.3f} mSv (Abuhaimed pelvis all-size {ABU_PELVIS_PER_100})"
    )
    print(f"  cal runfolder: {cal_rundir}")
    print(f"  phantom runfolder: {res['rundir']}")


if __name__ == "__main__":
    main()
