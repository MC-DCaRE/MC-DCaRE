"""Regenerate the gitignored ``data/`` assets on a fresh clone.

Everything under ``data/`` is gitignored (large reference datasets). This
script rebuilds the assets that MC-DCaRE needs at runtime, automating what can
be automated and printing exact commands for the license-gated manual downloads.

Subcommands::

    uv run python tools/setup_data.py nist            # NIST HVL coefficient table
    uv run python tools/setup_data.py bowtie          # processed bow-tie STLs
    uv run python tools/setup_data.py phantom-mesh    # print ICRP download steps
    uv run python tools/setup_data.py phantom-voxel   # voxelize staged meshes
    uv run python tools/setup_data.py all             # orchestrate everything

See ``docs/data_regeneration.md`` for the full fresh-clone procedure.
"""

from __future__ import annotations

import argparse
import logging
import os
import subprocess
import sys

logger = logging.getLogger(__name__)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

# NIST XCOM mass attenuation / energy-absorption coefficients (cm^2/g) for HVL
# folding. Source: NIST XCOM Photon Cross Sections Database
# (https://physics.nist.gov/PhysRefData/Xcom). These are public reference data;
# verify against the NIST source. Columns: Energy_MeV  mu_en/rho_air  mu/rho_Al.
_NIST_HVL_TABLE = """\
# NIST XCOM mass attenuation / energy-absorption coefficients for HVL folding.
# Source: NIST XCOM Photon Cross Sections Database (physics.nist.gov/PhysRefData/Xcom).
# Values are cm^2/g. Energies in MeV. Verify against the NIST source before
# production use; these cover the diagnostic kV range (10-150 keV).
#
# Columns: Energy_MeV   mu_en/rho_air   mu/rho_Aluminium
0.010    4.642    26.23
0.015    1.294     7.955
0.020    0.5501    3.441
0.030    0.1535    1.128
0.040    0.06683   0.5685
0.050    0.0403    0.3681
0.060    0.0286    0.2778
0.080    0.01962   0.2018
0.100    0.01649   0.1704
0.125    0.01478   0.1488
0.150    0.01394   0.1378
"""

# ICRP electronic supplements (license: free for non-commercial research).
_ICRP_P145_ADULT_URL = (
    "https://journals.sagepub.com/doi/suppl/10.1177/ANIB_49_3 "
    "(P145 Electronic files.zip -- adult MRCP-AM/AF mesh)"
)
_ICRP_P156_PAED_URL = (
    "https://www.icrp.org/docs/P156%20Electronic%20files.zip "
    "(P156 Electronic files.zip -- paediatric MRCPs, ~12 GB)"
)


def _run(cmd: list[str]) -> int:
    logger.info("Running: %s", " ".join(cmd))
    return subprocess.call(cmd, cwd=PROJECT_ROOT)


def setup_nist() -> None:
    """Write data/nist/hvl_coefficients.dat from NIST XCOM reference values."""
    out_dir = os.path.join(DATA_DIR, "nist")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "hvl_coefficients.dat")
    with open(path, "w") as f:
        f.write(_NIST_HVL_TABLE)
    logger.info("Wrote NIST HVL coefficient table -> %s", path)


def setup_bowtie() -> None:
    """Regenerate the processed bow-tie STLs from the Inbum source STL.

    Outputs go to src/boilerplates/TOPAS_includeFiles/ (tracked), not data/.
    """
    tool = os.path.join(PROJECT_ROOT, "tools", "process_bowtie_stl.py")
    src = os.path.join(
        PROJECT_ROOT, "research", "Monte Carlo Stuff from Inbum", "bowtie.stl"
    )
    if not os.path.isfile(tool):
        logger.warning(
            "tools/process_bowtie_stl.py not found -- on the develop-bowtie-"
            "spectrum-validation branch. Merge it first."
        )
        return
    if not os.path.isfile(src):
        logger.warning("Source STL not found: %s", src)
        return
    out = os.path.join(PROJECT_ROOT, "src", "boilerplates", "TOPAS_includeFiles")
    rc = _run(
        [
            sys.executable,
            tool,
            "--input",
            src,
            "--output-dir",
            out,
            "--decimate-eps",
            "0.6",
        ]
    )
    if rc == 0:
        logger.info("Bow-tie STLs regenerated in %s", out)


def setup_phantom_mesh() -> None:
    """Print the ICRP download + staging steps (manual; license-gated)."""
    mesh_root = os.path.join(DATA_DIR, "P145", "Phantom_data")
    print("\n=== ICRP mesh download (manual) ===\n")
    print("1. Adult mesh (ICRP 145, MRCP-AM/AF):")
    print("   URL:", _ICRP_P145_ADULT_URL)
    print("2. Paediatric mesh (ICRP 156, ages 0/1/5/10/15 y x M/F):")
    print("   URL:", _ICRP_P156_PAED_URL)
    print(
        "\nUnzip each into data/P145/Phantom_data/ so directories are named to "
        "match PhantomConfig.resolve_phantom_name():"
    )
    print("   MRCP_AM  MRCP_AF                  (adult, ICRP 145)")
    print("   MRCP_AM_0y MRCP_AF_0y ... MRCP_AF_15y   (paediatric, ICRP 156)")
    print(
        "\nEach directory must contain <name>.node, <name>.ele, <name>.material "
        "(TetGen format). If only .obj ships, retetrahedralize: tetgen -pAY <name>.poly"
    )
    print("\nTarget mesh root:", mesh_root)
    print("Then run: uv run python tools/setup_data.py phantom-voxel\n")


def _expected_phantom_names() -> list[str]:
    names = ["MRCP_AM", "MRCP_AF"]
    for age in ("0y", "1y", "5y", "10y", "15y"):
        for sex in ("AM", "AF"):
            names.append("MRCP_%s_%s" % (sex, age))
    return names


def setup_phantom_voxel(voxel_size_cm: float = 0.5) -> None:
    """Voxelize every staged mesh in data/P145/Phantom_data/ into data/P145/voxelized/."""
    tool = os.path.join(PROJECT_ROOT, "tools", "voxelize_phantom.py")
    mesh_root = os.path.join(DATA_DIR, "P145", "Phantom_data")
    if not os.path.isdir(mesh_root):
        logger.warning(
            "Mesh root %s does not exist -- run 'phantom-mesh' first.", mesh_root
        )
        setup_phantom_mesh()
        return

    staged = [
        d for d in os.listdir(mesh_root) if os.path.isdir(os.path.join(mesh_root, d))
    ]
    if not staged:
        logger.warning("No staged meshes in %s -- run 'phantom-mesh' first.", mesh_root)
        setup_phantom_mesh()
        return

    count = 0
    for name in staged:
        # Skip the single-organ test mesh and MC example dirs.
        node = os.path.join(mesh_root, name, "%s.node" % name)
        if not os.path.isfile(node):
            logger.info("Skipping %s (no %s.node)", name, name)
            continue
        out = os.path.join(
            DATA_DIR, "P145", "voxelized", "%s_%gmm" % (name, voxel_size_cm * 10)
        )
        logger.info("Voxelizing %s -> %s", name, out)
        rc = _run(
            [
                sys.executable,
                tool,
                "--input",
                os.path.join(mesh_root, name),
                "--output",
                out,
                "--name",
                name,
                "--voxel-size",
                str(voxel_size_cm),
            ]
        )
        if rc == 0:
            count += 1
        else:
            logger.warning("Voxelization failed for %s (rc=%d)", name, rc)
    logger.info("Voxelized %d phantom(s) at %g mm.", count, voxel_size_cm * 10)


def setup_all() -> None:
    """Run everything automatable; print manual steps for downloads."""
    setup_nist()
    setup_bowtie()
    # Voxelization auto-discovers staged meshes; prints download steps if none.
    setup_phantom_voxel()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
    parser = argparse.ArgumentParser(description="Regenerate gitignored data/ assets.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("nist", help="write data/nist/hvl_coefficients.dat")
    sub.add_parser("bowtie", help="regenerate processed bow-tie STLs")
    sub.add_parser("phantom-mesh", help="print ICRP mesh download steps")
    pvox = sub.add_parser("phantom-voxel", help="voxelize staged phantom meshes")
    pvox.add_argument(
        "--voxel-size-cm",
        type=float,
        default=0.5,
        help="voxel size in cm (default 0.5=5mm)",
    )
    sub.add_parser("all", help="run all automatable steps")
    args = parser.parse_args()

    if args.cmd == "nist":
        setup_nist()
    elif args.cmd == "bowtie":
        setup_bowtie()
    elif args.cmd == "phantom-mesh":
        setup_phantom_mesh()
    elif args.cmd == "phantom-voxel":
        setup_phantom_voxel(args.voxel_size_cm)
    elif args.cmd == "all":
        setup_all()


if __name__ == "__main__":
    main()
