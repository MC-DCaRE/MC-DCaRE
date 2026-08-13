"""Compare three bow-tie configurations at equal histories (5M).

Runs (each 5M histories x 8 sequential times):
  1. legacy  -- CSG trapezoid bow-tie (legacy_bowtie=true)
  2. new     -- TsCAD STL, Rotation parent @ 18 cm SDD (the fix)
  3. old     -- TsCAD STL, collimator-bay parent @ TransZ=38.5 mm (the broken
                placement; overlaps Coll1, so QuitIfOverlapDetected=False)

Prints a Centre/Top/Bottom/Left/Right TLE comparison table. Restores
bowtie_ff.txt and headsourcecode_boilerplate.j2 afterwards.
"""
from __future__ import annotations

import csv
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.abspath(os.path.dirname(__file__))
BOWTIE = os.path.join(ROOT, "src/boilerplates/TOPAS_includeFiles/bowtie_ff.txt")
HEAD = os.path.join(ROOT, "src/boilerplates/headsourcecode_boilerplate.j2")
CONFIG_DIR = os.path.join(ROOT, "configs")

NEW_BOWTIE = """\
# [new placement -- restored by compare script]
s:Ge/BowtieFilter/Type = "TsCAD"
s:Ge/BowtieFilter/Parent = "Rotation"
s:Ge/BowtieFilter/Material = "G4_Al"
s:Ge/BowtieFilter/InputFile = "fullfan"
s:Ge/BowtieFilter/FileFormat = "stl"
d:Ge/BowtieFilter/Units = 1.0 mm
d:Ge/BowtieFilter/TransX = 0.0 mm
d:Ge/BowtieFilter/TransY = Ge/BeamPosition/TransY + 18.0 cm
d:Ge/BowtieFilter/TransZ = 0.0 mm
d:Ge/BowtieFilter/RotX = 0. deg
d:Ge/BowtieFilter/RotY = 0. deg
dc:Ge/BowtieFilter/RotZ = -90. deg
s:Ge/BowtieFilter/DrawingStyle = "Wireframe"
"""

OLD_BOWTIE = """\
# [old placement -- collimator bay, overlaps Coll1]
b:Ge/QuitIfOverlapDetected = "False"
s:Ge/BowtieFilter/Type = "TsCAD"
s:Ge/BowtieFilter/Parent = "CollimatorsHorizontal"
s:Ge/BowtieFilter/Material = "G4_Al"
s:Ge/BowtieFilter/InputFile = "fullfan"
s:Ge/BowtieFilter/FileFormat = "stl"
d:Ge/BowtieFilter/Units = 1.0 mm
d:Ge/BowtieFilter/TransX = 0.0 mm
d:Ge/BowtieFilter/TransY = 0.0 mm
d:Ge/BowtieFilter/TransZ = 38.5 mm
d:Ge/BowtieFilter/RotX = 0. deg
d:Ge/BowtieFilter/RotY = 0. deg
dc:Ge/BowtieFilter/RotZ = -90. deg
s:Ge/BowtieFilter/DrawingStyle = "Wireframe"
"""

LEGACY_CFG = """\
general:
  g4_data_directory: /opt/topas/GEANT4/G4DATA
  topas_directory: /opt/topas/TOPAS/OpenTOPAS-install/bin/topas
  seed: '9'
  threads: '20'
  histories: '5000000'
  log_filename: simulation.log
imaging:
  simulation_type: CTDI
  rotation_direction: CBCT Clockwise
  imaging_mode: Head
  fan_mode: Full Fan
  sequential_times: '8'
  legacy_bowtie: true
ctdi:
  dose_to_medium_zbins: '100'
  tle_zbins: '100'
  dose_to_water_zbins: '100'
  couch_enabled: true
  couch_width: 260 mm
  couch_thickness: 0.4 mm
  couch_length: 1000 mm
  user_blade_enabled: false
  graphics_enabled: false
"""

TSCAD_CFG = LEGACY_CFG.replace("legacy_bowtie: true", "legacy_bowtie: false")


def run_sim(label: str, config_path: str) -> str:
    print(f"\n=== {label}: running ===", flush=True)
    os.chdir(ROOT)
    res = subprocess.run(
        ["uv", "run", "python", "run_simulation.py", "run", config_path],
        capture_output=True, text=True, cwd=ROOT, timeout=5400,
    )
    m = re.search(r"(runfolder/\S+)", res.stdout + res.stderr)
    rundir = os.path.join(ROOT, m.group(1)) if m else ""
    print(f"{label}: done -> {rundir}", flush=True)
    return rundir


def tle_sum(rundir: str, plug: str) -> float:
    path = os.path.join(rundir, f"ChamberPlug{plug}_tle.csv")
    if not os.path.isfile(path):
        return float("nan")
    total = 0.0
    with open(path) as f:
        for row in csv.reader(f):
            if len(row) > 3 and row[3] and not row[3].startswith("#"):
                try:
                    total += float(row[3])
                except ValueError:
                    pass
    return total


def main() -> None:
    backup_bowtie = open(BOWTIE).read()
    backup_head = open(HEAD).read()
    results: dict[str, dict[str, float]] = {}

    try:
        # Configs
        leg_cfg = os.path.join(CONFIG_DIR, "_cmp_legacy_5m.yaml")
        tsc_cfg = os.path.join(CONFIG_DIR, "_cmp_tscad_5m.yaml")
        open(leg_cfg, "w").write(LEGACY_CFG)
        open(tsc_cfg, "w").write(TSCAD_CFG)

        # 1. Legacy
        rd = run_sim("legacy", leg_cfg)
        results["legacy"] = {p: tle_sum(rd, p) for p in
                             ["Centre", "Top", "Bottom", "Left", "Right"]}

        # 2. New TsCAD (current bowtie_ff.txt = new placement)
        open(BOWTIE, "w").write(NEW_BOWTIE)
        rd = run_sim("new", tsc_cfg)
        results["new"] = {p: tle_sum(rd, p) for p in
                          ["Centre", "Top", "Bottom", "Left", "Right"]}

        # 3. Old TsCAD (collimator-bay placement)
        open(BOWTIE, "w").write(OLD_BOWTIE)
        rd = run_sim("old", tsc_cfg)
        results["old"] = {p: tle_sum(rd, p) for p in
                          ["Centre", "Top", "Bottom", "Left", "Right"]}
    finally:
        open(BOWTIE, "w").write(backup_bowtie)
        open(HEAD, "w").write(backup_head)
        print("\n[restored bowtie_ff.txt and headsourcecode_boilerplate.j2]")

    plugs = ["Centre", "Top", "Bottom", "Left", "Right"]
    print("\n" + "=" * 64)
    print("BOW-TIE COMPARISON @ 5M histories (TLE Sum, arbitrary units)")
    print("=" * 64)
    print(f"{'Plug':<10}{'legacy':>14}{'new(18cm)':>14}{'old(bay)':>14}")
    for p in plugs:
        print(f"{p:<10}{results['legacy'][p]:>14.3e}{results['new'][p]:>14.3e}"
              f"{results['old'][p]:>14.3e}")
    # Symmetry check
    print("\nTop/Bottom ratio (should be ~1.0):")
    for k in ("legacy", "new", "old"):
        tb = results[k]["Top"] / results[k]["Bottom"] if results[k]["Bottom"] else float("inf")
        print(f"  {k:<8}{tb:.3f}")


if __name__ == "__main__":
    main()
