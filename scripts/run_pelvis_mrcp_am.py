#!/usr/bin/env python3
"""
Run full MRCP-AM pelvis simulation with voxelized phantom.
Does dry run, swaps in voxelized phantom, runs with real spectrum.
"""

from __future__ import annotations

import os
import sys
import shutil
import re
import subprocess
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")

from src.config import SimulationConfig
from src.orchestrator import Orchestrator


def main():
    project_root = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/..")
    config_path = os.path.join(project_root, "configs", "phantom_pelvis_mrcp_am.yaml")

    config = SimulationConfig.from_yaml(config_path)

    print(f"=== MRCP-AM Pelvis Simulation ===")
    print(f"Histories: {int(config.general.histories):,}")
    print(f"Threads: {config.general.threads}")
    print(f"Imaging mode: {config.imaging.imaging_mode}")
    print(f"Rotation: {config.imaging.rotation_direction}")
    print(f"Exposure: {config.imaging.exposure}")
    print()

    # Step 1: Dry run to generate TOPAS files with real spectrum
    print("=== Step 1: Dry run pipeline ===")
    orch = Orchestrator(project_root)
    rundir = orch.run(config, dry_run=True)
    print(f"Runfolder: {rundir}")

    # Step 2: Copy voxelized phantom and swap include
    print("\n=== Step 2: Swap in voxelized phantom ===")
    voxel_src = os.path.join(project_root, "test_voxel_output", "mrcp_am", "phantomVoxel.txt")
    phantom_dst = os.path.join(rundir, "phantomVoxel.txt")
    shutil.copy(voxel_src, phantom_dst)
    print(f"Copied voxelized phantom to {phantom_dst}")

    # Fix materials (replace ICRP materials with G4_WATER for now)
    with open(phantom_dst, "r") as f:
        content = f.read()
    for mat in ['G4_ADIPOSE_TISSUE_ICRP', 'G4_BLADDER_ICRP', 'G4_BLOOD_ICRP',
                'G4_BONE_COMPACT_ICRU', 'G4_BRAIN_ICRP', 'G4_CARTILAGE_ICRP',
                'G4_INTESTINE_ICRP', 'G4_KIDNEY_ICRP', 'G4_LIVER_ICRP',
                'G4_LUNG_ICRP', 'G4_MUSCLE_ICRP', 'G4_PANCREAS_ICRP',
                'G4_SKIN_ICRP', 'G4_SPLEEN_ICRP', 'G4_STOMACH_ICRP', 'G4_THYROID_ICRP']:
        content = content.replace(f'"{mat}"', '"G4_WATER"')
    with open(phantom_dst, "w") as f:
        f.write(content)

    # Step 3: Modify headsourcecode.txt
    print("\n=== Step 3: Modify TOPAS files ===")
    head_file = os.path.join(rundir, "headsourcecode.txt")
    with open(head_file, "r") as f:
        head_content = f.read()

    # Replace phantom include
    head_content = head_content.replace(
        "includeFile = phantomICRP145.txt",
        "includeFile = phantomVoxel.txt"
    )

    # Remove TsTetGeom-specific parameter
    head_content = head_content.replace(
        "i:Ts/ParameterizationErrorMaxReports = 5\n", ""
    )

    # Disable overlap check
    head_content += '\nb:Ge/QuitIfOverlapDetected = "False"\n'

    with open(head_file, "w") as f:
        f.write(head_content)
    print(f"Modified {head_file}")

    # Step 4: Run TOPAS
    print(f"\n=== Step 4: Run TOPAS simulation ===")
    print(f"Histories: {int(config.general.histories):,}")
    print(f"Threads: {config.general.threads}")
    print(f"TOPAS: {config.general.topas_directory}")
    print()

    topas_bin = config.general.topas_directory
    log_file = os.path.join(rundir, "simulation.log")

    t0 = time.time()
    result = subprocess.run(
        [topas_bin, "headsourcecode.txt"],
        cwd=rundir,
        capture_output=False,
        timeout=86400,  # 24 hour max
    )

    elapsed = time.time() - t0
    hours = elapsed / 3600
    print(f"\n=== Complete ===")
    print(f"Elapsed: {elapsed:.0f}s ({hours:.1f}h)")
    print(f"Exit code: {result.returncode}")
    print(f"Runfolder: {rundir}")

    # Check for dose output
    for f in os.listdir(rundir):
        if f.endswith(".csv") and "dose" in f.lower():
            fpath = os.path.join(rundir, f)
            size = os.path.getsize(fpath)
            print(f"Output: {f} ({size} bytes)")

    return rundir


if __name__ == "__main__":
    rundir = main()
    print(f"\nResults in: {rundir}")