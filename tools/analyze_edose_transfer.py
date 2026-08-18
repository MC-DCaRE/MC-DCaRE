#!/usr/bin/env python3
"""Phase-0 transfer analysis: new vs old beam model across the E-dose sweep.

For every completed protocol runfolder in edose_validation_runs/ (new beam
model: rectangular blades + primary masks + spekpy Ti + measured fluence
anchor, 2026-08-18 DCFs), computes the DCF-calibrated effective dose and
decomposes the new/old change into:

    E_ratio(new/old) = raw_phantom_ratio x DCF_ratio

with raw_phantom_ratio further divided by the fluence-anchor factor (the old
10:31 sweep predated the anchor) to isolate pure transport change.

Benchmarks against the trusted independent anchors only:
  - Abuhaimed & Martin 2023, all-size E per 100 mAs (chest 2.07, pelvis 1.19)
  - Abuhaimed 2018 Head EGSnrc MC (0.32 mSv @ 150.3 mAs -> 0.213/100 mAs)
  - Hauri 2017 pelvis TLD (5.4 mSv absolute, same technique family)
PCXMC manufacturer references are carried as a caveat column only.

Old-sweep E values and old DCFs are read from git history
(HEAD:edose_validation_runs/validation_results.csv, calibration.yaml at
0c0b2c5~1) -- both hardcoded with provenance below if git lookup fails.

Usage:
    uv run python tools/analyze_edose_transfer.py [--csv out.csv]
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.services.calibration import CalibrationService  # noqa: E402
from src.services.phantom_dose_calculator import (  # noqa: E402
    PhantomDoseCalculator,
)

VOXEL_GRID = PROJECT_ROOT / "test_voxel_output" / "mrcp_am" / "mrcp_am_voxels.npy"
MATERIAL = (
    PROJECT_ROOT / "data" / "P145" / "Phantom_data" / "MRCP_AM" / "MRCP_AM.material"
)
EDOSE_DIR = PROJECT_ROOT / "edose_validation_runs"
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
    "SBRT Spine": 0,
    "Thorax": 460,
    "Thorax Spotlight": 460,
}

# Old-sweep E (mSv) from HEAD:edose_validation_runs/validation_results.csv
# (2026-08-18 10:31-10:53 sweep: wedge blades, geometric 1.78 mm Ti, no anchor)
OLD_SWEEP_E_MSV: Dict[str, float] = {
    "4D Spotlight": 3.12,
    "4D Thorax": 5.09,
    "Abdo Spotlight": 1.21,
    "Abdomen": 3.23,
    "Breast 360": 0.68,
    "Extremity Spotlight": 0.23,
    "Head": 0.30,
    "Head and Shoulders": 2.19,
    "Head SRS": 1.06,
    "Pelvis": 3.04,
    "Pelvis Spotlight": 2.01,
    "SBRT Spine": 3.78,
    "Thorax": 2.04,
    "Thorax Spotlight": 1.26,
}
# Old dcf_tle (calibration.yaml at 0c0b2c5~1, calibrated 2026-08-14 model)
OLD_DCF_TLE: Dict[Tuple[int, str], float] = {
    (80, "Full Fan"): 0.10720,
    (100, "Full Fan"): 0.11837,
    (100, "Half Fan"): 0.15850,
    (125, "Full Fan"): 0.12002,
    (125, "Half Fan"): 0.16070,
    (140, "Half Fan"): 0.17572,
}
# Trusted independent anchors (see docstring for provenance)
ABUHAIMED_PER_100_MAS = {"chest": 2.07, "pelvis": 1.19}
HEAD_2018_MSV_PER_100_MAS = 0.32 / 150.3 * 100.0  # Abuhaimed 2018 EGSnrc
HAURI_PELVIS_MSV = 5.4
# Scan-class mapping; "!" flags imperfect field/technique comparability
PROTOCOL_CLASS: Dict[str, str] = {
    "4D Thorax": "chest",
    "Thorax": "chest",
    "Breast 360": "chest!",
    "SBRT Spine": "chest!",
    "Head and Shoulders": "chest!",
    "Thorax Spotlight": "chest!",
    "Pelvis": "pelvis",
    "Abdomen": "pelvis",
    "4D Spotlight": "pelvis!",
    "Pelvis Spotlight": "pelvis!",
    "Abdo Spotlight": "pelvis!",
}
PCXMC_REF_MSV: Dict[str, float] = {
    "4D Spotlight": 1.6,
    "4D Thorax": 3.3,
    "Abdo Spotlight": 1.2,
    "Abdomen": 2.8,
    "Breast 360": 0.2,
    "Extremity Spotlight": 0.5,
    "Head": 0.5,
    "Head and Shoulders": 0.3,
    "Head SRS": 1.8,
    "Pelvis": 4.2,
    "Pelvis Spotlight": 2.2,
    "SBRT Spine": 1.7,
    "Thorax": 1.3,
    "Thorax Spotlight": 0.7,
}


def load_anchor_factors() -> Dict[int, float]:
    data = yaml.safe_load(
        (PROJECT_ROOT / "data" / "measured" / "fluence_anchors.yaml").read_text()
    )
    return {int(a["kV"]): float(a["factor"]) for a in data["anchors"]}


def sweep_runs() -> List[Tuple[str, Path]]:
    """Completed new-model sweep runfolders as (protocol, path)."""
    runs = []
    for rd in sorted(EDOSE_DIR.glob("*/")):
        cfgs = list(rd.glob("run_full_edose_*.yaml"))
        if not cfgs or not (rd / "phantom_tle.csv").exists():
            continue
        if (rd / "phantom_tle.csv").stat().st_size == 0:
            continue
        slug = cfgs[0].stem.replace("run_full_edose_", "")
        name = " ".join(w.capitalize() for w in slug.split("_"))
        name = (
            name.replace("And Shoulders", "and Shoulders")
            .replace("Sbrt Spine", "SBRT Spine")
            .replace("4d", "4D")
            .replace("Head Srs", "Head SRS")
        )
        if slug == "pelvis_single":  # ad-hoc single-protocol re-runs
            continue
        runs.append((name, rd))
    return runs


def effective_dose(rd: Path) -> float:
    cs = CalibrationService(PROJECT_ROOT / "calibration.yaml")
    md = CalibrationService.read_metadata(rd)
    calc = PhantomDoseCalculator(rd / "phantom_tle.csv", VOXEL_GRID, MATERIAL)
    return calc.calculate(
        calibration_service=cs, metadata=md, scorer_type="tle"
    ).effective_dose_mSv


def new_dcf(kv: int, fan: str) -> float:
    cal = yaml.safe_load((PROJECT_ROOT / "calibration.yaml").read_text())
    for c in cal["calibrations"]:
        if c["kV"] == kv and c["fan_mode"] == fan:
            return float(c["dcf_tle"])
    raise KeyError(f"no new DCF for {kv} {fan}")


def pearson(xs: List[float], ys: List[float]) -> Optional[float]:
    if len(xs) < 3:
        return None
    x, y = np.asarray(xs), np.asarray(ys)
    if x.std() == 0 or y.std() == 0:
        return None
    return float(np.corrcoef(x, y)[0, 1])


def main() -> None:
    anchors = load_anchor_factors()
    rows = []
    for name, rd in sweep_runs():
        md = CalibrationService.read_metadata(rd)
        kv = int(float(md["spekpy"]["kvp"]))
        fan = md["fan_mode"]
        mas = float(md["exposure_mAs"])
        e_new = effective_dose(rd)
        dcf_new, dcf_old = new_dcf(kv, fan), OLD_DCF_TLE[(kv, fan)]
        anchor = anchors.get(kv, 1.0)
        e_old = OLD_SWEEP_E_MSV.get(name)
        # raw phantom ratio, anchor divided out (old sweep was unanchored)
        raw_ratio = (
            (e_new / e_old) * (dcf_old / dcf_new) / anchor if e_old else float("nan")
        )
        per100 = e_new / mas * 100.0
        cls = PROTOCOL_CLASS.get(name, "")
        abu = ABUHAIMED_PER_100_MAS.get(cls.rstrip("!"))
        if name in ("Head", "Head SRS"):
            abu = HEAD_2018_MSV_PER_100_MAS
        rows.append(
            {
                "protocol": name,
                "kV": kv,
                "fan": fan[:1],
                "mAs": mas,
                "E_new": e_new,
                "E_old": e_old,
                "E_ratio": e_new / e_old if e_old else float("nan"),
                "raw_ph_ratio": raw_ratio,
                "per100mAs": per100,
                "abu_class": cls or ("head2018" if abu else ""),
                "abu_ref": abu,
                "abu_ratio": per100 / abu if abu else float("nan"),
                "pcxmc_caveat": PCXMC_REF_MSV.get(name),
                "iso_z": ISOCENTER_Z_MM.get(name),
            }
        )

    hdr = (
        f"{'protocol':<21}{'kV':>4}{'f':>3}{'mAs':>7}{'E_new':>7}{'E_old':>7}"
        f"{'ratio':>7}{'raw_ph':>8}{'/100mAs':>8}{'abu':>6}{'abu_rat':>8}"
    )
    print(hdr)
    print("-" * len(hdr))
    for r in sorted(rows, key=lambda r: (r["kV"], r["fan"], -r["mAs"])):
        print(
            f"{r['protocol']:<21}{r['kV']:>4}{r['fan']:>3}{r['mAs']:>7.0f}"
            f"{r['E_new']:>7.2f}{r['E_old'] or float('nan'):>7.2f}"
            f"{r['E_ratio']:>7.2f}{r['raw_ph_ratio']:>8.2f}"
            f"{r['per100mAs']:>8.3f}{r['abu_ref'] or float('nan'):>6.2f}"
            f"{r['abu_ratio']:>8.2f}"
        )

    hf125 = [r for r in rows if r["kV"] == 125 and r["fan"] == "H"]
    ff125 = [r for r in rows if r["kV"] == 125 and r["fan"] == "F"]
    ff100 = [r for r in rows if r["kV"] == 100 and r["fan"] == "F"]
    for label, grp in (("125 HF", hf125), ("125 FF", ff125), ("100 FF", ff100)):
        rr = [r["raw_ph_ratio"] for r in grp if not np.isnan(r["raw_ph_ratio"])]
        if rr:
            print(
                f"\n{label}: raw_ph ratio range {min(rr):.2f}-{max(rr):.2f} "
                f"(spread {max(rr) / min(rr):.2f}x)"
            )
    z = [float(r["iso_z"]) for r in hf125 if r["iso_z"] is not None]
    v = [r["raw_ph_ratio"] for r in hf125 if r["iso_z"] is not None]
    r_iso = pearson(z, v)
    if r_iso is not None:
        print(
            f"125 HF raw_ph_ratio vs iso-Z Pearson r = {r_iso:+.2f} (H1/H2 signature)"
        )

    import argparse

    ap = argparse.ArgumentParser()
    ap.parse_args()
    out = EDOSE_DIR / "phase0_transfer.csv"
    import csv

    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
