"""Phase 2: compare scored MC bow-tie profiles against the measured RaySafe data.

Reads the Phase 1 manifest (label -> profile CSV), loads the measured Head Full
Fan cross-plane profile from the RaySafe workbook, and for each MC profile
computes the peak-normalised RMS misfit + CAX dose ratio and emits a comparison
CSV + matplotlib PNG. Prints a summary table.

Usage::

    python tools/tabulate_bowtie_validation.py \\
        --manifest artifacts/bowtie_validation/manifest.tsv \\
        --measured "research/2023 - CBCT Dose PCXMC/New results Oct 2023 (Spotlight, Raysafe X2) - fixed spotlight.xlsx" \\
        --outdir artifacts/bowtie_validation
"""

from __future__ import annotations

import argparse
import csv
import logging
import os

import numpy as np

from src.services.bowtie_validator import (
    Profile,
    _normalise,
    compare_profiles,
    load_mc_profile,
    load_measured_profile,
)

logger = logging.getLogger(__name__)

MEASURED = (
    "research/2023 - CBCT Dose PCXMC/"
    "New results Oct 2023 (Spotlight, Raysafe X2) - fixed spotlight.xlsx"
)


def _cax_dose(profile: Profile) -> float:
    """Dose at the position nearest X=0 (central axis)."""
    if profile.position_cm.size == 0:
        return float("nan")
    i = int(np.argmin(np.abs(profile.position_cm)))
    return float(profile.dose[i])


def _read_manifest(path: str) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    with open(path) as f:
        reader = csv.DictReader(f, delimiter="\t")
        for r in reader:
            if r.get("profile_csv"):
                rows.append((r["label"], r["runfolder"], r["profile_csv"]))
    return rows


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
    parser = argparse.ArgumentParser(description="Tabulate bow-tie profile validation")
    parser.add_argument(
        "--manifest", default="artifacts/bowtie_validation/manifest.tsv"
    )
    parser.add_argument("--measured", default=MEASURED)
    parser.add_argument("--mode-group", type=int, default=0, help="0=Head FF")
    parser.add_argument("--outdir", default="artifacts/bowtie_validation")
    args = parser.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    measured = load_measured_profile(args.measured, mode_group=args.mode_group)
    meas_cax = _cax_dose(measured)
    meas_cax_hvl = float(measured.hvl_mmAl[np.argmin(np.abs(measured.position_cm))])
    print(
        "Measured %s: %d pts, CAX dose=%.3g, CAX HVL=%.3f mmAl"
        % (measured.label, measured.position_cm.size, meas_cax, meas_cax_hvl)
    )

    entries = _read_manifest(args.manifest)
    ff_entries = [e for e in entries if e[0].endswith("_ff")]

    results = []
    for label, _rundir, prof_csv in ff_entries:
        mc = load_mc_profile(prof_csv)
        out_csv = os.path.join(args.outdir, "compare_%s.csv" % label)
        out_png = os.path.join(args.outdir, "compare_%s.png" % label)
        res = compare_profiles(measured, mc, output_csv=out_csv, output_png=out_png)
        # Central-region (|X|<=10 cm) RMS -- the bow-tie-shaped core, less
        # affected by the wide-field extrafocal shelf at the far edges.
        import numpy as _np

        mc_on = _np.interp(measured.position_cm, mc.position_cm, _normalise(mc.dose))
        meas_n = _normalise(measured.dose)
        mask = _np.abs(measured.position_cm) <= 10.0
        rms_central = (
            float(_np.sqrt(_np.mean((mc_on[mask] - meas_n[mask]) ** 2)))
            if mask.any()
            else float("nan")
        )
        results.append((label, res["rms_misfit"], rms_central, _cax_dose(mc)))

    _overlay(measured, ff_entries, args.outdir, args.manifest)

    print("\n" + "=" * 70)
    print("BOW-TIE Z-PROFILE VALIDATION vs measured Head FF (peak-normalised)")
    print("=" * 70)
    print(
        "%-14s %10s %12s %14s" % ("bow-tie", "RMS(all)", "RMS(|X|<=10)", "MC CAX dose")
    )
    for label, rms, rms_c, mc_cax in results:
        print("%-14s %10.4f %12.4f %14.3e" % (label, rms, rms_c, mc_cax))
    print(
        "\nLower RMS = closer to measured. RMS(|X|<=10) isolates the bow-tie core\n"
        "from the wide-field extrafocal shelf at the far edges."
    )


def _overlay(measured: Profile, entries: list, outdir: str, manifest: str) -> None:
    """Draw all FF profiles + measured on one peak-normalised axes."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(
        measured.position_cm,
        _normalise(measured.dose),
        "k*-",
        label="measured (RaySafe Head FF)",
        ms=8,
    )
    styles = {"tscad_ff": "s-", "legacy_ff": "^-", "nobtie_ff": "d--"}
    for label, _rundir, prof_csv in entries:
        if not label.endswith("_ff"):
            continue
        mc = load_mc_profile(prof_csv)
        ax.plot(
            mc.position_cm,
            _normalise(mc.dose),
            styles.get(label, "o-"),
            label=label,
            ms=3,
            lw=1.2,
        )
    ax.set_xlabel("Lateral position (cm)")
    ax.set_ylabel("Dose (peak-normalised)")
    ax.set_title("Bow-tie cross-plane profile: measured vs MC (Z axis, wide field)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(-18, 18)
    fig.tight_layout()
    fig.savefig(os.path.join(outdir, "overlay_all.png"), dpi=120)
    plt.close(fig)


if __name__ == "__main__":
    main()
