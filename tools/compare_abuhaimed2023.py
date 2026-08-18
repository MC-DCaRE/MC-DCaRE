"""Compare MC-DCaRE effective dose per 100 mAs against Abuhaimed & Martin 2023.

Reads the edose sweep summary (``edose_validation_runs/validation_results.csv``
with columns protocol, mAs, e_sim_mSv, ...), normalizes each protocol to
mSv/100 mAs, and compares the chest- and pelvis-class protocols against the
BMI-library benchmarks in ``data/literature/abuhaimed2023_tables.yaml``
(all-size averages; full BMI classes are in the file for future size-specific
work). When per-run ``organ_doses.csv`` files exist (post-recalibration
sweeps), ``--organ-csv <runfolder>`` adds the organ-level table.

Usage::

    python tools/compare_abuhaimed2023.py \
        --sweep edose_validation_runs/validation_results.csv
"""

from __future__ import annotations

import argparse
import csv
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)

TABLE = PROJECT_ROOT / "data" / "literature" / "abuhaimed2023_tables.yaml"

# Protocol -> benchmark scan class. Primary comparators are the default
# techniques closest to the paper's default scans; the rest are context rows.
_SCAN_CLASS = {
    "Thorax": "chest",
    "4D Thorax": "chest",
    "Pelvis": "pelvis",
    "Pelvis Large": "pelvis",
    "Pelvis Spotlight": "pelvis",
    "Abdo Spotlight": "pelvis",
}
_PRIMARY = {"Thorax", "Pelvis"}


def per_100mAs(e_mSv: float, mAs: float) -> float:
    return e_mSv / mAs * 100.0


def compare_effective(sweep_csv: Path) -> List[Dict[str, object]]:
    with open(TABLE, encoding="utf-8") as f:
        table = yaml.safe_load(f)
    lit = {
        cls: table[cls]["effective_dose_mSv_per_100mAs"][-1]  # "All"
        for cls in ("chest", "pelvis")
    }
    rows: List[Dict[str, object]] = []
    with open(sweep_csv, newline="") as f:
        for r in csv.DictReader(f):
            proto = r["protocol"]
            if proto not in _SCAN_CLASS or r.get("status") != "ok":
                continue
            ours = per_100mAs(float(r["e_sim_mSv"]), float(r["mAs"]))
            cls = _SCAN_CLASS[proto]
            rows.append(
                {
                    "protocol": proto,
                    "class": cls,
                    "ours_mSv_per_100mAs": round(ours, 3),
                    "lit_mSv_per_100mAs": lit[cls],
                    "ratio": round(ours / lit[cls], 2),
                    "primary": proto in _PRIMARY,
                }
            )
    return rows


def _norm(name: str) -> str:
    """Normalise organ/tissue names for matching (case, underscores, hyphens)."""
    return name.strip().lower().replace("_", " ").replace("-", " ")


def compare_organs(
    organ_csv: Path, scan_class: str, mAs: float
) -> Optional[List[Dict[str, object]]]:
    """Organ-level per-100 mAs table (needs a surviving organ_doses.csv)."""
    if not organ_csv.exists():
        return None
    with open(TABLE, encoding="utf-8") as f:
        table = yaml.safe_load(f)
    lit = table[scan_class]
    ours: Dict[str, List[float]] = {}
    with open(organ_csv, newline="") as f:
        for r in csv.DictReader(f):
            tissue = r.get("icrp103_tissue") or r.get("tissue")
            if not tissue:
                continue
            ours.setdefault(_norm(tissue), []).append(float(r["mean_mGy"]))
    rows: List[Dict[str, object]] = []
    for organ, vals in lit.items():
        if organ == "effective_dose_mSv_per_100mAs":
            continue
        doses = ours.get(_norm(organ))
        if not doses:
            continue
        o = sum(doses) / len(doses) / mAs * 100.0
        rows.append(
            {
                "organ": organ,
                "ours_mGy_per_100mAs": round(o, 3),
                "lit_mGy_per_100mAs": vals[-1],
                "ratio": round(o / vals[-1], 2) if vals[-1] else float("nan"),
            }
        )
    return rows


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sweep",
        default=str(PROJECT_ROOT / "edose_validation_runs" / "validation_results.csv"),
    )
    parser.add_argument(
        "--organ-csv", default="", help="optional organ_doses.csv for the organ table"
    )
    parser.add_argument("--scan-class", choices=["chest", "pelvis"], default="pelvis")
    parser.add_argument("--organ-mAs", type=float, default=1074.0)
    args = parser.parse_args()

    rows = compare_effective(Path(args.sweep))
    if not rows:
        logger.error("no comparable protocols in %s", args.sweep)
        sys.exit(1)

    print("\nEffective dose per 100 mAs vs Abuhaimed & Martin 2023 (All-size):")
    print("  NB: our sweep predates the blade fix + fluence anchor (stale E);")
    print("  re-run the sweep post-recalibration for final numbers.\n")
    print("  %-18s %-7s %12s %10s %7s" % ("protocol", "class", "ours", "lit", "ratio"))
    for r in sorted(rows, key=lambda x: (not x["primary"], x["class"], x["protocol"])):
        star = "*" if r["primary"] else " "
        print(
            "%s %-18s %-7s %12.3f %10.2f %7.2f"
            % (
                star,
                r["protocol"],
                r["class"],
                r["ours_mSv_per_100mAs"],
                r["lit_mSv_per_100mAs"],
                r["ratio"],
            )
        )
    print("\n  (* = default-technique primary comparator; others are context.)")

    if args.organ_csv:
        organ_rows = compare_organs(
            Path(args.organ_csv), args.scan_class, args.organ_mAs
        )
        if organ_rows:
            print("\nOrgan dose per 100 mAs (%s, ours vs lit All):" % args.scan_class)
            for r in sorted(organ_rows, key=lambda x: -x["ratio"]):
                print(
                    "  %-18s %10.3f %10.2f %7.2f"
                    % (
                        r["organ"],
                        r["ours_mGy_per_100mAs"],
                        r["lit_mGy_per_100mAs"],
                        r["ratio"],
                    )
                )


if __name__ == "__main__":
    main()
