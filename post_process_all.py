#!/usr/bin/env python3
"""Post-process per-protocol replays with CORRECT exposure from reference table.

Writes results to runfolder/effective_dose_comparison.csv.
"""
from __future__ import annotations

import csv
import re
import subprocess
from datetime import datetime
from pathlib import Path
import yaml

ROOT = Path("/home/bchcphysics/Github/MC-DCaRE")
GRID = ROOT / "test_voxel_output/mrcp_am/mrcp_am_voxels_fine.npy"
OUTPUT_CSV = ROOT / "runfolder/effective_dose_comparison.csv"

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


def run_cli(protocol: str, target_mAs: float) -> tuple[float, float, str]:
    """Run CLI with --target-mAs, return (effective_dose_mSv, dcf_used, scoring_mAs)."""
    slug = protocol.lower().replace(" ", "_")
    rf = ROOT / "runfolder" / f"replay_{slug}"
    csv_path = rf / "organ_dose_tle.csv"
    if not csv_path.exists():
        return (-1.0, "", 0.0)
    result = subprocess.run(
        ["uv", "run", "python", "calculate_phantom_dose.py", f"{rf}/",
         "--dose-file", "organ_dose_tle.csv",
         "--voxel-grid", str(GRID),
         "--scorer-type", "tle",
         "--target-mAs", str(target_mAs)],
        capture_output=True, text=True, cwd=str(ROOT), timeout=300,
    )
    eff = -1.0
    for line in result.stdout.split("\n"):
        m = re.match(r"\s*EFFECTIVE DOSE\s+(\S+)\s+mSv", line)
        if m:
            eff = float(m.group(1))
    # Read scoring mAs from metadata
    meta_path = rf / "simulation_metadata.yaml"
    scoring_mas = 0.0
    if meta_path.exists():
        with open(meta_path) as f:
            scoring_mas = yaml.safe_load(f).get("exposure_mAs", 0.0)
    return (eff, "", scoring_mas)


def main() -> None:
    rows = []

    print("=" * 95)
    print(f"  {'Protocol':<25} {'kV':>3} {'Fan':>3} {'mAs':>8} {'E_MC':>8} {'E_ref':>7} {'Diff':>22}")
    print("  " + "-" * 92)

    for name in PROTOCOLS:
        mAs = EXPOSURE[name]
        kv, fan = KVF[name]
        eff, _, scoring_mas = run_cli(name, mAs)
        ref = REFS.get(name)

        if eff < 0:
            ref_str = f"{ref:.1f}" if ref else "-"
            print(f"  {name:<25} {kv:>3} {fan:>3} {mAs:>8.1f} {'N/A':>8} {ref_str:>7}")
            rows.append({
                "protocol": name, "kV": kv, "fan": fan, "target_mAs": mAs,
                "scoring_mAs": scoring_mas, "E_MC_mSv": "", "E_ref_mSv": ref if ref else "",
                "diff_mSv": "", "diff_pct": "", "within_50pct": "",
            })
            continue

        diff_str = ""
        diff_val = ""
        pct_val = ""
        within = ""
        if ref is not None:
            diff = eff - ref
            pct = 100 * diff / ref if ref > 0 else 0
            ok = abs(diff) <= 3.0 and abs(pct) <= 50
            diff_str = f"{diff:+.2f} ({pct:+.0f}%) {'✓' if ok else '✗'}"
            diff_val = f"{diff:.2f}"
            pct_val = f"{pct:.0f}"
            within = "YES" if ok else "NO"

        ref_str = f"{ref:.1f}" if ref else "-"
        print(f"  {name:<25} {kv:>3} {fan:>3} {mAs:>8.1f} {eff:>8.2f} {ref_str:>7} {diff_str:>22}")

        rows.append({
            "protocol": name, "kV": kv, "fan": fan, "target_mAs": mAs,
            "scoring_mAs": scoring_mas, "E_MC_mSv": f"{eff:.2f}",
            "E_ref_mSv": ref if ref else "", "diff_mSv": diff_val,
            "diff_pct": pct_val, "within_50pct": within,
        })

    # Write CSV
    OUTPUT_CSV.parent.mkdir(exist_ok=True)
    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "protocol", "kV", "fan", "target_mAs", "scoring_mAs",
            "E_MC_mSv", "E_ref_mSv", "diff_mSv", "diff_pct", "within_50pct",
        ])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    print(f"\n  Results written to: {OUTPUT_CSV}")

    # Summary
    refs = [(r["E_MC_mSv"], r["E_ref_mSv"]) for r in rows
            if r["E_ref_mSv"] != "" and r["E_MC_mSv"] != ""]
    if refs:
        w3 = sum(1 for e, r in refs if abs(float(e) - float(r)) <= 3.0)
        w50 = sum(1 for e, r in refs if float(r) > 0 and abs(float(e) - float(r)) / float(r) <= 0.5)
        print(f"\n  Summary ({len(refs)} protocols with references):")
        print(f"    Within ±3 mSv: {w3}/{len(refs)}")
        print(f"    Within ±50%:   {w50}/{len(refs)}")


if __name__ == "__main__":
    main()
