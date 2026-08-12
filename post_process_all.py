#!/usr/bin/env python3
"""Post-process per-protocol replays with CORRECT exposure from reference table."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path
import yaml

ROOT = Path("/home/bchcphysics/Github/MC-DCaRE")
GRID = ROOT / "test_voxel_output/mrcp_am/mrcp_am_voxels_fine.npy"

# Load reference table
with open(ROOT / "data/protocol_reference_table.yaml") as f:
    ref_data = yaml.safe_load(f)

REFS = {}
EXPOSURE = {}
KVF = {}
for p in ref_data["protocols"]:
    name = p["name"]
    if p["dose_mSv"] is not None:
        REFS[name] = p["dose_mSv"]
    EXPOSURE[name] = p["exposure_mAs"]
    fan = "HF" if "LFOV" in p["fan"] or "Half" in p["fan"] else "FF"
    KVF[name] = (p["kV"], fan)

PROTOCOLS = [p["name"] for p in ref_data["protocols"]]


def run_cli(protocol: str, target_mAs: float) -> float:
    slug = protocol.lower().replace(" ", "_")
    rf = ROOT / "runfolder" / f"replay_{slug}"
    csv = rf / "organ_dose_tle.csv"
    if not csv.exists():
        return -1.0
    result = subprocess.run(
        ["uv", "run", "python", "calculate_phantom_dose.py", f"{rf}/",
         "--dose-file", "organ_dose_tle.csv",
         "--voxel-grid", str(GRID),
         "--scorer-type", "tle",
         "--target-mAs", str(target_mAs)],
        capture_output=True, text=True, cwd=str(ROOT), timeout=300,
    )
    for line in result.stdout.split("\n"):
        m = re.match(r"\s*EFFECTIVE DOSE\s+(\S+)\s+mSv", line)
        if m:
            return float(m.group(1))
    return -1.0


def main() -> None:
    print("=" * 95)
    print(f"  {'Protocol':<25} {'kV':>3} {'Fan':>3} {'mAs':>8} {'E_MC':>8} {'E_ref':>7} {'Diff':>22}")
    print("  " + "-" * 92)

    results = []
    for name in PROTOCOLS:
        mAs = EXPOSURE[name]
        kv, fan = KVF[name]
        eff = run_cli(name, mAs)
        ref = REFS.get(name)

        if eff < 0:
            ref_str = f"{ref:.1f}" if ref else "-"
            print(f"  {name:<25} {kv:>3} {fan:>3} {mAs:>8.1f} {'N/A':>8} {ref_str:>7}")
            continue

        diff_str = ""
        if ref is not None:
            diff = eff - ref
            pct = 100 * diff / ref if ref > 0 else 0
            ok = " ✓" if (abs(diff) <= 3.0 and abs(pct) <= 50) else " ✗"
            diff_str = f"{diff:+.2f} ({pct:+.0f}%){ok}"

        ref_str = f"{ref:.1f}" if ref else "-"
        print(f"  {name:<25} {kv:>3} {fan:>3} {mAs:>8.1f} {eff:>8.2f} {ref_str:>7} {diff_str:>22}")
        results.append((name, eff, ref))

    refs = [(r[1], r[2]) for r in results if r[2] is not None]
    if refs:
        print(f"\n  Summary ({len(refs)} protocols with references):")
        w3 = sum(1 for e, r in refs if abs(e - r) <= 3.0)
        w50 = sum(1 for e, r in refs if r > 0 and abs(e - r) / r <= 0.5)
        print(f"    Within ±3 mSv: {w3}/{len(refs)}")
        print(f"    Within ±50%:   {w50}/{len(refs)}")


if __name__ == "__main__":
    main()
