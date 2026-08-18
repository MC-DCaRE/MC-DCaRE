#!/usr/bin/env python3
"""Compare MC-DCaRE organ doses against the Abuhaimed 2018 MC benchmarks.

Reads one of our organ_doses.csv files (PhantomDoseCalculator output),
aggregates to ICRP 103 tissue HTs with the calculator's arithmetic
organ-mean convention, and prints a side-by-side table against
data/literature_organ_benchmarks.yaml (EGSnrc/ICRP-male, V2.5 techniques
matched to this machine).

Usage:
    uv run python scripts/compare_literature.py Head edose_validation_runs/<ts>/organ_doses.csv
    uv run python scripts/compare_literature.py --all edose_validation_runs/
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BENCHMARK = PROJECT_ROOT / "data" / "literature_organ_benchmarks.yaml"

# Tissue tags excluded from the HT comparison (literature "lumped" rows and
# in-field-only rows without a whole-phantom counterpart)
_SKIP_TISSUES = {None, "remainder_lumped"}


def our_hts(df: pd.DataFrame) -> Dict[str, float]:
    """Arithmetic organ-mean HT per ICRP 103 tissue (calculator default)."""
    return {
        tissue: float(sub["mean_mGy"].mean())
        for tissue, sub in df.groupby("icrp103_tissue")
    }


def our_effective_dose(df: pd.DataFrame) -> float:
    """Recompute E with the calculator's convention (weights x tissue means)."""
    sys.path.insert(0, str(PROJECT_ROOT))
    from src.models.icrp103 import TISSUE_WEIGHTING_FACTORS

    hts = our_hts(df)
    return sum(w * hts.get(t, 0.0) for t, w in TISSUE_WEIGHTING_FACTORS.items())


def compare(protocol: str, organ_csv: Path, benchmarks: Dict) -> Optional[pd.DataFrame]:
    """Build the per-tissue comparison table for one protocol."""
    proto = benchmarks["protocols"].get(protocol)
    if proto is None:
        print(f"no literature benchmark for protocol '{protocol}'")
        return None
    df = pd.read_csv(organ_csv)
    hts = our_hts(df)

    rows: List[Dict] = []
    for entry in proto["organ_doses_mGy"]:
        tissue = entry.get("tissue")
        organ_regex = entry.get("organ_regex")
        if organ_regex:
            sub = df[df["organ"].str.contains(organ_regex, regex=True)]
            if not len(sub):
                continue
            ours = float(sub["mean_mGy"].mean())
            matched = f"{len(sub)} organs"
        elif tissue in _SKIP_TISSUES:
            continue
        else:
            ours = hts.get(tissue)
            matched = "tissue HT"
            if ours is None:
                continue
        lit = float(entry["dose_mGy"])
        ratio = ours / lit if lit > 0 else float("nan")
        rows.append(
            {
                "literature_organ": entry["literature_organ"],
                "ours_mGy": round(ours, 2),
                "abuhaimed_mGy": lit,
                "ratio": round(ratio, 2),
                "match": matched,
            }
        )
    return pd.DataFrame(rows).sort_values("ratio")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("protocol", help="Benchmark protocol: Head, Thorax or Pelvis")
    parser.add_argument(
        "organ_csv", type=Path, help="Our organ_doses.csv from a phantom run"
    )
    args = parser.parse_args()

    with open(BENCHMARK) as f:
        benchmarks = yaml.safe_load(f)
    proto = benchmarks["protocols"][args.protocol]

    table = compare(args.protocol, args.organ_csv, benchmarks)
    if table is None or table.empty:
        sys.exit(1)

    df = pd.read_csv(args.organ_csv)
    e_ours = our_effective_dose(df)
    e_lit = float(proto["effective_dose_mSv"])
    tech = f"{proto['kV']} kV, {proto['fan_mode']}, {proto['exposure_mAs']} mAs"

    print(f"\n=== {args.protocol} vs Abuhaimed 2018 (V2.5 male) ===")
    print(f"Literature technique: {tech}")
    print(
        f"Effective dose: ours {e_ours:.2f} mSv vs literature {e_lit:.2f} mSv"
        f" (ratio {e_ours / e_lit:.2f})\n"
    )
    with pd.option_context("display.max_rows", None, "display.width", 120):
        print(table.to_string(index=False))
    n = len(table)
    within = int(((table["ratio"] > 0.8) & (table["ratio"] < 1.25)).sum())
    print(f"\nTissues within +/-20% of literature: {within}/{n}")


if __name__ == "__main__":
    main()
