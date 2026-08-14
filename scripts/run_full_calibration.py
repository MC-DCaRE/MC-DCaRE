#!/usr/bin/env python3
"""
Full calibration, verification, and phantom dose pipeline.

Runs:
  1. All 6 CTDI calibrations (180M histories each: 5M x 36 sequential)
  2. Verification CBCT (150M histories: 1M x 150 sequential, different seed)
  3. ICRP 145 phantom (150M histories: 1M x 150 sequential)
  4. Post-processing: DCF computation, CTDIw, organ doses, effective dose

Usage:
    python run_full_calibration.py                    # Full run
    python run_full_calibration.py --dry-run          # Generate configs only
    python run_full_calibration.py --skip-calibration  # Skip phase 1
    python run_full_calibration.py --threads 10        # Override thread count
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Machine paths (override via environment or CLI)
G4_DATA = os.environ.get("G4DATA_DIR", "/opt/topas/GEANT4/G4DATA")
TOPAS_BIN = os.environ.get("TOPAS_DIR", "/opt/topas/TOPAS/OpenTOPAS-install/bin/topas")

# History counts
# Calibration uses 5M x 36 = 180M histories per protocol, matching the
# 2026-08-11 production DCFs these replace (apples-to-apples at the TsCAD bow-
# tie). Verify/phantom use 1M x 150 = 150M.
CAL_HISTORIES = "5000000"       # per sequential time (calibration)
CAL_SEQUENTIAL = "36"           # 5M x 36 = 180M total (rotational CTDI, 10 deg)
VERIFY_HISTORIES = "1000000"   # per sequential time (verification)
VERIFY_SEQUENTIAL = "150"      # 1M x 150 = 150M total

# Calibration configs and reference CTDIw values
CALIBRATIONS = [
    {
        "config": "configs/cal_80kv_ff_image-gently.yaml",
        "name": "80 kV Full Fan (Image Gently)",
        "kV": 80,
        "fan_mode": "Full Fan",
        "ref_ctdiw_mGy": 0.9,
    },
    {
        "config": "configs/cal_100kv_ff_head.yaml",
        "name": "100 kV Full Fan (Head)",
        "kV": 100,
        "fan_mode": "Full Fan",
        "ref_ctdiw_mGy": 3.2,
    },
    {
        "config": "configs/cal_125kv_ff_pelvis-spotlight.yaml",
        "name": "125 kV Full Fan (Pelvis Spotlight)",
        "kV": 125,
        "fan_mode": "Full Fan",
        "ref_ctdiw_mGy": 12.3,
    },
    {
        "config": "configs/cal_125kv_hf_pelvis.yaml",
        "name": "125 kV Half Fan (Pelvis)",
        "kV": 125,
        "fan_mode": "Half Fan",
        "ref_ctdiw_mGy": 15.9,
    },
    {
        "config": "configs/cal_140kv_ff.yaml",
        "name": "140 kV Full Fan",
        "kV": 140,
        "fan_mode": "Full Fan",
        "ref_ctdiw_mGy": None,  # no reference
    },
    {
        "config": "configs/cal_140kv_hf_pelvis-large.yaml",
        "name": "140 kV Half Fan (Pelvis Large)",
        "kV": 140,
        "fan_mode": "Half Fan",
        "ref_ctdiw_mGy": 37.1,
    },
]

# Verification protocol (uses the same protocol as the phantom run)
VERIFY_CONFIG = {
    "config": "configs/xval_125kv_hf_pelvis_seed42.yaml",
    "name": "Verification: 125 kV HF Pelvis (seed=42)",
    "kV": 125,
    "fan_mode": "Half Fan",
}

# Phantom protocol
PHANTOM_CONFIG = "configs/phantom_pelvis_mrcp_am.yaml"
PHANTOM_NAME = "125 kV HF Pelvis MRCP-AM"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_and_patch_config(
    config_path: str,
    overrides: Dict[str, Dict[str, str]],
) -> Dict:
    """Load a YAML config and apply overrides per section."""
    with open(PROJECT_ROOT / config_path) as f:
        data = yaml.safe_load(f)

    for section, values in overrides.items():
        data.setdefault(section, {})
        data[section].update(values)

    return data


def write_temp_config(data: Dict, name: str) -> Path:
    """Write a config dict to a temp file and return the path."""
    out = PROJECT_ROOT / "tmp" / f"run_full_{name}.yaml"
    out.parent.mkdir(exist_ok=True)
    with open(out, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    return out


def run_simulation(config_path: Path, output_base: str = "runfolder", dry_run: bool = False) -> str:
    """Run a simulation via the orchestrator. Returns the runfolder path.

    Args:
        config_path: Path to the YAML config file.
        output_base: Subdirectory under project root for runfolders
            (e.g. "calibration_runs", "verification_runs").
        dry_run: If True, only generate files without running TOPAS.
    """
    from datetime import datetime

    from src.config import SimulationConfig
    from src.orchestrator import Orchestrator

    config = SimulationConfig.from_yaml(str(config_path))
    orch = Orchestrator(str(PROJECT_ROOT))

    # Create runfolder in the specified base directory
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    rundir = str(PROJECT_ROOT / output_base / timestamp)

    if dry_run:
        os.makedirs(rundir, exist_ok=True)
        orch.run_with_runfolder(rundir, config, dry_run=True)
        print(f"  [DRY RUN] Runfolder: {rundir}")
        return rundir

    os.makedirs(rundir, exist_ok=True)
    orch.run_with_runfolder(rundir, config, dry_run=False)
    print(f"  Runfolder: {rundir}")
    return rundir


def swap_voxel_phantom(rundir: str) -> None:
    """Copy voxelized phantom files into a runfolder."""
    voxel_src = PROJECT_ROOT / "test_voxel_output" / "mrcp_am"
    rundir_path = Path(rundir)

    for fname in ["phantomVoxel.txt", "icrp_materials.txt"]:
        src = voxel_src / fname
        if src.exists():
            shutil.copy(src, rundir_path / fname)

    # Patch headsourcecode.txt to use phantomVoxel.txt
    head_file = rundir_path / "headsourcecode.txt"
    if head_file.exists():
        content = head_file.read_text()
        content = content.replace(
            "includeFile = phantomICRP145.txt",
            "includeFile = phantomVoxel.txt",
        )
        content = content.replace(
            "i:Ts/ParameterizationErrorMaxReports = 5\n", ""
        )
        if 'QuitIfOverlapDetected' not in content:
            content += '\nb:Ge/QuitIfOverlapDetected = "False"\n'
        head_file.write_text(content)

    print(f"  Swapped voxelized phantom into {rundir}")


def run_topas(rundir: str, dry_run: bool = False) -> int:
    """Run TOPAS in the runfolder."""
    import subprocess

    head_file = Path(rundir) / "headsourcecode.txt"
    if not head_file.exists():
        # Try CTDI_all_positions.txt for CTDI mode
        head_file = Path(rundir) / "CTDI_all_positions.txt"
    if not head_file.exists():
        print(f"  ERROR: No TOPAS parameter file found in {rundir}")
        return 1

    if dry_run:
        print(f"  [DRY RUN] Would run: topas {head_file.name}")
        return 0

    print(f"  Running TOPAS: {head_file.name}")
    t0 = time.time()
    result = subprocess.run(
        [TOPAS_BIN, head_file.name],
        cwd=rundir,
        timeout=86400,
    )
    elapsed = time.time() - t0
    print(f"  TOPAS completed in {elapsed:.0f}s ({elapsed / 60:.1f} min), exit={result.returncode}")
    return result.returncode


# ---------------------------------------------------------------------------
# Phase implementations
# ---------------------------------------------------------------------------

def ensure_calibration_yaml() -> Path:
    """Ensure calibration.yaml exists for storing DCFs.

    Creates an EMPTY calibration.yaml if it doesn't exist (does NOT copy
    from calibration.example.yaml, which has pre-filled example DCFs).
    DCFs are added incrementally as each calibration run completes.
    """
    cal_path = PROJECT_ROOT / "calibration.yaml"
    if not cal_path.exists():
        with open(cal_path, "w") as f:
            f.write("machine: TrueBeam\n")
            f.write("date_calibrated: '2026-07-01'\n")
            f.write("calibrations: []\n")
        print(f"  Created empty calibration.yaml")
    return cal_path


def has_ctdi_output(rundir: str) -> bool:
    """Check if a CTDI runfolder has output files."""
    p = Path(rundir)
    return any(p.glob("ChamberPlug*_tle.csv"))


def has_phantom_output(rundir: str) -> bool:
    """Check if a phantom runfolder has output files."""
    return (Path(rundir) / "phantom_dose.csv").exists()


def phase1_calibration(threads: str, dry_run: bool, resume: bool) -> Dict:
    """Phase 1: Run all CTDI calibrations and compute DCFs."""
    print("\n" + "=" * 70)
    print("  PHASE 1: CTDI Calibration (6 protocols, 180M histories each)")
    print("=" * 70)

    # Ensure calibration.yaml exists before we start
    cal_path = ensure_calibration_yaml()

    results = []

    for cal in CALIBRATIONS:
        print(f"\n--- {cal['name']} ---")

        # Skip if DCF already exists (resume support)
        if resume and cal["ref_ctdiw_mGy"] is not None:
            try:
                from src.services.calibration import CalibrationService

                cal_service = CalibrationService(cal_path)
                existing_dcf = cal_service.lookup_dcf(cal["kV"], cal["fan_mode"])
                if existing_dcf is not None:
                    print(f"  DCF already exists: {existing_dcf:.6e} (skipping)")
                    results.append({**cal, "rundir": "cached", "status": "cached", "dcf": existing_dcf})
                    continue
                else:
                    print(f"  No existing DCF, will run")
            except Exception as e:
                print(f"  Resume check failed ({e}), will run")

        overrides = {
            "general": {
                "g4_data_directory": G4_DATA,
                "topas_directory": TOPAS_BIN,
                "threads": threads,
                "histories": CAL_HISTORIES,
                "dose_calibration_factor": "1.0",
            },
            "imaging": {
                "sequential_times": CAL_SEQUENTIAL,
            },
        }

        data = load_and_patch_config(cal["config"], overrides)
        temp_path = write_temp_config(data, f"cal_{cal['kV']}_{cal['fan_mode'].replace(' ', '')}")

        if dry_run:
            print(f"  Config: {temp_path}")
            rundir = run_simulation(temp_path, "calibration_runs", dry_run=True)
            results.append({**cal, "rundir": rundir, "status": "dry_run"})
            continue

        # Run simulation (with error recovery)
        try:
            rundir = run_simulation(temp_path, "calibration_runs", dry_run=False)
            rc = run_topas(rundir)
        except Exception as e:
            print(f"  ERROR: Simulation failed: {e}")
            results.append({**cal, "rundir": "N/A", "status": "failed", "error": str(e)})
            time.sleep(10)  # Allow OS cleanup before next run
            continue

        if rc != 0:
            print(f"  WARNING: TOPAS returned {rc}")
            results.append({**cal, "rundir": rundir, "status": "failed"})
            time.sleep(10)
            continue

        # Compute DCF
        if cal["ref_ctdiw_mGy"] is not None:
            try:
                from src.services.calibration import CalibrationService
                from src.services.ctdi_calculator import CTDICalculator

                cal_service = CalibrationService(cal_path)
                calc = CTDICalculator(Path(rundir))
                raw_results = calc.calculate()
                primary = [r for r in raw_results if r.get("scorer_type") == "tle"]
                if primary:
                    # Normalize to get ctdi_w_raw_Gy (raw_sum * photons_per_mAs * mAs)
                    norm = cal_service.normalize(
                        primary[0], cal["kV"], cal["fan_mode"]
                    )
                    dcf = cal_service.compute_dcf(
                        cal["kV"],
                        cal["fan_mode"],
                        norm["ctdi_w_raw_Gy"],
                        cal["ref_ctdiw_mGy"],
                        force=True,
                    )
                    print(f"  Raw CTDIw: {norm['ctdi_w_raw_Gy']:.4e} Gy")
                    print(f"  DCF computed: {dcf:.6e}")
                    results.append({**cal, "rundir": rundir, "status": "ok", "dcf": dcf})
                else:
                    print(f"  WARNING: No TLE scorer found")
                    results.append({**cal, "rundir": rundir, "status": "no_tle"})
            except Exception as e:
                print(f"  WARNING: DCF computation failed: {e}")
                results.append({**cal, "rundir": rundir, "status": "dcf_failed"})
        else:
            print(f"  No reference CTDIw (skipping DCF)")
            results.append({**cal, "rundir": rundir, "status": "no_ref"})

        # Allow OS cleanup between heavy runs
        time.sleep(10)

    return {"phase": "calibration", "results": results}


def phase2_verification(threads: str, dry_run: bool, resume: bool) -> Dict:
    """Phase 2: Verification CBCT run with different seed."""
    print("\n" + "=" * 70)
    print("  PHASE 2: Verification CBCT (125 kV HF Pelvis, seed=42, 150M)")
    print("=" * 70)

    overrides = {
        "general": {
            "g4_data_directory": G4_DATA,
            "topas_directory": TOPAS_BIN,
            "threads": threads,
            "histories": VERIFY_HISTORIES,
            "seed": "42",
            "dose_calibration_factor": "1.0",
        },
        "imaging": {
            "sequential_times": VERIFY_SEQUENTIAL,
        },
    }

    data = load_and_patch_config(VERIFY_CONFIG["config"], overrides)
    temp_path = write_temp_config(data, "verify_pelvis")

    if dry_run:
        print(f"  Config: {temp_path}")
        rundir = run_simulation(temp_path, "verification_runs", dry_run=True)
        return {"phase": "verification", "rundir": rundir, "status": "dry_run"}

    # Resume check
    if resume:
        existing = sorted(Path(PROJECT_ROOT / "verification_runs").glob("*/ChamberPlug*_tle.csv"))
        if existing:
            rundir = str(existing[0].parent)
            print(f"  Existing output found, reusing: {rundir}")
            # Still compute CTDIw
            try:
                cal_path = PROJECT_ROOT / "calibration.yaml"
                if cal_path.exists():
                    import subprocess as sp

                    result = sp.run(
                        [sys.executable, "calculate_ctdiw.py", rundir, "--calibrated"],
                        capture_output=True, text=True, cwd=str(PROJECT_ROOT),
                    )
                    return {"phase": "verification", "rundir": rundir, "status": "cached",
                            "ctdiw": result.stdout}
            except Exception as e:
                print(f"  WARNING: CTDIw calculation failed: {e}")
            return {"phase": "verification", "rundir": rundir, "status": "cached"}

    try:
        rundir = run_simulation(temp_path, "verification_runs", dry_run=False)
        time.sleep(10)  # Cleanup between phases
        rc = run_topas(rundir)
    except Exception as e:
        print(f"  ERROR: {e}")
        return {"phase": "verification", "rundir": "N/A", "status": "failed", "error": str(e)}

    status = "ok" if rc == 0 else "failed"

    # Compute CTDIw
    ctdiw_result = None
    if rc == 0:
        try:
            cal_path = PROJECT_ROOT / "calibration.yaml"
            if cal_path.exists():
                import subprocess as sp

                result = sp.run(
                    [
                        sys.executable,
                        "calculate_ctdiw.py",
                        rundir,
                        "--calibrated",
                    ],
                    capture_output=True,
                    text=True,
                    cwd=str(PROJECT_ROOT),
                )
                ctdiw_result = result.stdout
                print(f"  CTDIw:\n{ctdiw_result[:500]}")
        except Exception as e:
            print(f"  WARNING: CTDIw calculation failed: {e}")

    return {"phase": "verification", "rundir": rundir, "status": status, "ctdiw": ctdiw_result}


def phase3_phantom(threads: str, dry_run: bool, resume: bool) -> Dict:
    """Phase 3: ICRP 145 phantom run."""
    print("\n" + "=" * 70)
    print("  PHASE 3: ICRP 145 Phantom (125 kV HF Pelvis MRCP-AM, 150M)")
    print("=" * 70)

    overrides = {
        "general": {
            "g4_data_directory": G4_DATA,
            "topas_directory": TOPAS_BIN,
            "threads": threads,
            "histories": VERIFY_HISTORIES,
            "dose_calibration_factor": "1.0",
        },
        "imaging": {
            "sequential_times": VERIFY_SEQUENTIAL,
        },
    }

    data = load_and_patch_config(PHANTOM_CONFIG, overrides)
    temp_path = write_temp_config(data, "phantom_pelvis")

    if dry_run:
        print(f"  Config: {temp_path}")
        rundir = run_simulation(temp_path, "phantom_runs", dry_run=True)
        swap_voxel_phantom(rundir)
        return {"phase": "phantom", "rundir": rundir, "status": "dry_run"}

    # Resume check
    if resume:
        existing = sorted(Path(PROJECT_ROOT / "phantom_runs").glob("*/phantom_dose.csv"))
        if existing:
            rundir = str(existing[0].parent)
            print(f"  Existing output found, reusing: {rundir}")
            try:
                cal_path = PROJECT_ROOT / "calibration.yaml"
                if not cal_path.exists():
                    cal_path = PROJECT_ROOT / "calibration.example.yaml"
                import subprocess as sp

                result = sp.run(
                    [sys.executable, "calculate_phantom_dose.py", rundir,
                     "--calibration", str(cal_path),
                     "--output", str(Path(rundir) / "organ_doses.csv")],
                    capture_output=True, text=True, cwd=str(PROJECT_ROOT),
                )
                return {"phase": "phantom", "rundir": rundir, "status": "cached",
                        "dose_report": result.stdout}
            except Exception as e:
                print(f"  WARNING: Dose calculation failed: {e}")
            return {"phase": "phantom", "rundir": rundir, "status": "cached"}

    try:
        # Dry-run to generate files, swap phantom BEFORE TOPAS runs
        rundir = run_simulation(temp_path, "phantom_runs", dry_run=True)
        swap_voxel_phantom(rundir)
        time.sleep(5)
        # Now run TOPAS manually (the dry-run only generated files)
        rc = run_topas(rundir)
    except Exception as e:
        print(f"  ERROR: {e}")
        return {"phase": "phantom", "rundir": "N/A", "status": "failed", "error": str(e)}

    status = "ok" if rc == 0 else "failed"

    # Compute organ doses and effective dose
    dose_result = None
    if rc == 0:
        try:
            cal_path = PROJECT_ROOT / "calibration.yaml"
            if not cal_path.exists():
                cal_path = PROJECT_ROOT / "calibration.example.yaml"

            import subprocess as sp

            result = sp.run(
                [
                    sys.executable,
                    "calculate_phantom_dose.py",
                    rundir,
                    "--calibration",
                    str(cal_path),
                    "--output",
                    str(Path(rundir) / "organ_doses.csv"),
                ],
                capture_output=True,
                text=True,
                cwd=str(PROJECT_ROOT),
            )
            dose_result = result.stdout
            print(f"  Organ doses and effective dose computed")
        except Exception as e:
            print(f"  WARNING: Dose calculation failed: {e}")

    return {"phase": "phantom", "rundir": rundir, "status": status, "dose_report": dose_result}


def phase4_report(cal_results: Dict, verify_results: Dict, phantom_results: Dict) -> None:
    """Phase 4: Report all values."""
    print("\n" + "=" * 70)
    print("  PHASE 4: Summary Report")
    print("=" * 70)

    # Calibration results
    print("\n--- Calibration DCFs ---")
    print(f"{'Protocol':<35} {'kV':>4} {'Fan':>10} {'Ref mGy':>8} {'DCF':>14} {'Status':>8}")
    print("-" * 83)
    for r in cal_results.get("results", []):
        dcf = r.get("dcf", "N/A")
        dcf_str = f"{dcf:.6e}" if isinstance(dcf, float) else str(dcf)
        ref = r.get("ref_ctdiw_mGy", "N/A")
        ref_str = f"{ref}" if ref else "N/A"
        print(
            f"{r['name']:<35} {r['kV']:>4} {r['fan_mode']:>10} "
            f"{ref_str:>8} {dcf_str:>14} {r.get('status', '?'):>8}"
        )

    # Verification results
    print("\n--- Verification CBCT ---")
    v = verify_results
    print(f"  Protocol: {VERIFY_CONFIG['name']}")
    print(f"  Runfolder: {v.get('rundir', 'N/A')}")
    print(f"  Status: {v.get('status', '?')}")
    if v.get("ctdiw"):
        for line in v["ctdiw"].split("\n")[:10]:
            print(f"  {line}")

    # Phantom results
    print("\n--- ICRP 145 Phantom ---")
    p = phantom_results
    print(f"  Protocol: {PHANTOM_NAME}")
    print(f"  Runfolder: {p.get('rundir', 'N/A')}")
    print(f"  Status: {p.get('status', '?')}")
    if p.get("dose_report"):
        for line in p["dose_report"].split("\n")[:20]:
            print(f"  {line}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    global G4_DATA, TOPAS_BIN

    parser = argparse.ArgumentParser(
        description="Full calibration, verification, and phantom dose pipeline"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate configs and dry-run only (no TOPAS execution)",
    )
    parser.add_argument(
        "--skip-calibration",
        action="store_true",
        help="Skip phase 1 (use existing calibration.yaml)",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Skip phases with existing output (calibration DCFs, CTDI CSVs, dose CSVs)",
    )
    parser.add_argument(
        "--threads",
        default="20",
        help="Number of TOPAS threads (default: 20)",
    )
    parser.add_argument(
        "--g4-data",
        default=G4_DATA,
        help=f"Geant4 data directory (default: {G4_DATA})",
    )
    parser.add_argument(
        "--topas",
        default=TOPAS_BIN,
        help=f"TOPAS binary path (default: {TOPAS_BIN})",
    )
    args = parser.parse_args()

    G4_DATA = args.g4_data
    TOPAS_BIN = args.topas

    print("=" * 70)
    print("  MC-DCaRE Full Calibration Pipeline")
    print("=" * 70)
    print(f"  G4 Data:    {G4_DATA}")
    print(f"  TOPAS:      {TOPAS_BIN}")
    print(f"  Threads:    {args.threads}")
    print(f"  Dry run:    {args.dry_run}")
    print(f"  Skip calib: {args.skip_calibration}")
    print(f"  Resume:     {args.resume}")

    t0 = time.time()

    # Phase 1: Calibration
    cal_results = {"results": []}
    if not args.skip_calibration:
        cal_results = phase1_calibration(args.threads, args.dry_run, args.resume)
    else:
        print("\n  Skipping Phase 1 (using existing calibration.yaml)")

    # Phase 2: Verification
    verify_results = phase2_verification(args.threads, args.dry_run, args.resume)

    # Phase 3: Phantom
    phantom_results = phase3_phantom(args.threads, args.dry_run, args.resume)

    # Phase 4: Report
    phase4_report(cal_results, verify_results, phantom_results)

    elapsed = time.time() - t0
    print(f"\n{'=' * 70}")
    print(f"  Total elapsed: {elapsed:.0f}s ({elapsed / 60:.1f} min)")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()