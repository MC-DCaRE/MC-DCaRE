#!/usr/bin/env python3
"""
Generate Geant4 .material file from ICRP Publication 145 _media.dat.

This is a self-contained fallback script. The authoritative .material files
with organ-specific mappings are available in the Geant4 example zip.

Usage:
    python scripts/generate_material_from_media.py \
        data/P145/Phantom_data/MRCP_AM/MRCP_AM_media.dat \
        > data/P145/Phantom_data/MRCP_AM/MRCP_AM.material

Format:
    - _media.dat: Tissue compositions with element mass fractions (percentage)
    - .material: Geant4 material definitions with element IDs and mass fractions

Element mapping (Geant4 IDs):
    1000=H, 6000=C, 7000=N, 8000=O, 11000=Na, 12000=Mg,
    15000=P, 16000=S, 17000=Cl, 19000=K, 20000=Ca, 26000=Fe, 53000=I
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path

# Column mapping from _media.dat header to Geant4 element IDs
# _media.dat order: H(1), C(6), N(7), O(8), Na(11), Mg(12), P(15), S(16), Cl(17), K(19), Ca(20), Fe(26), I(53)
ELEMENT_COLUMNS = [
    (1000, 0),  # H, column 0 (after tissue number)
    (6000, 1),  # C, column 1
    (7000, 2),  # N, column 2
    (8000, 3),  # O, column 3
    (11000, 4),  # Na, column 4
    (12000, 5),  # Mg, column 5
    (15000, 6),  # P, column 6
    (16000, 7),  # S, column 7
    (17000, 8),  # Cl, column 8
    (19000, 9),  # K, column 9
    (20000, 10),  # Ca, column 10
    (26000, 11),  # Fe, column 11
    (53000, 12),  # I, column 12
]

logger = logging.getLogger(__name__)


def parse_media_dat(file_path: Path) -> list[dict[str, str | float]]:
    """
    Parse ICRP 145 _media.dat file.

    Args:
        file_path: Path to the _media.dat file

    Returns:
        List of dicts with tissue_name, density, and element composition
    """
    tissues = []
    with open(file_path, "r") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line or line.startswith("No.") or "Tissues to be used" in line:
            continue

        # Parse tissue line: tissue_number tissue_name H C N O ... density
        # Tissue names may contain spaces, so parse from the right: the last
        # 14 whitespace-separated fields are H..I (13 elements) + density.
        parts = re.split(r"\s+", line)
        if len(parts) < 16:  # Minimum: number + name + 13 elements + density
            continue

        density = float(parts[-1])
        # Element mass fractions are the 13 fields before the density
        element_values = parts[-14:-1]
        # Tissue number is parts[0]; tissue name is everything between
        tissue_number = parts[0]
        tissue_name = " ".join(parts[1:-14])

        element_fractions: dict[int, float] = {}
        for element_id, col_offset in ELEMENT_COLUMNS:
            mass_percent = element_values[col_offset]
            try:
                fraction = float(mass_percent) / 100.0
                if fraction > 0:
                    element_fractions[element_id] = fraction
            except ValueError:
                pass

        tissues.append(
            {
                "number": tissue_number,
                "name": tissue_name,
                "density": density,
                "elements": element_fractions,
            }
        )

    return tissues


def write_material_file(
    tissues: list[dict[str, str | float]], output_file: Path | None = None
) -> str:
    """
    Write Geant4 .material file.

    Args:
        tissues: List of tissue dictionaries from parse_media_dat
        output_file: Optional path to write output to

    Returns:
        The generated .material content as a string
    """
    lines = []

    material_id = 100  # Starting material ID (m100, m200, ...)

    for tissue in tissues:
        tissue_name = tissue["name"]
        density = tissue["density"]
        elements = tissue["elements"]

        # Material header (Geant4 syntax: negative = mass fraction)
        lines.append(f"C {tissue_name} {density} g/cm3")

        # Write element fractions (first element on the material ID line)
        sorted_elements = sorted(elements.items())
        first = True
        for element_id, fraction in sorted_elements:
            if first:
                lines.append(
                    f"m{material_id}     {element_id:6d}      {-fraction:8.3f}"
                )
                first = False
            else:
                lines.append(f"     {element_id:6d}      {-fraction:8.3f}")

        # Separator
        lines.append("C")
        lines.append("")

        material_id += 100  # Increment for next tissue

    content = "\n".join(lines)

    if output_file:
        with open(output_file, "w") as f:
            f.write(content)
        logger.info(f"Material file written to {output_file}")

    return content


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    parser = argparse.ArgumentParser(
        description="Generate Geant4 .material file from ICRP 145 _media.dat"
    )
    parser.add_argument("media_file", type=Path, help="Path to the _media.dat file")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output path for .material file (default: stdout)",
    )
    parser.add_argument(
        "-v",
        "--verify",
        type=Path,
        help="Verify output matches an existing .material file",
    )

    args = parser.parse_args()

    if not args.media_file.exists():
        logger.error(f"Media file not found: {args.media_file}")
        return 1

    tissues = parse_media_dat(args.media_file)
    logger.info(f"Parsed {len(tissues)} tissue definitions")

    if args.output:
        write_material_file(tissues, args.output)
    else:
        content = write_material_file(tissues)
        print(content)

    # Verify against existing file if requested
    if args.verify and args.verify.exists():
        generated = write_material_file(tissues)
        with open(args.verify, "r") as f:
            existing = f.read()

        if generated.strip() == existing.strip():
            logger.info("✓ Generated material matches the verification file")
        else:
            logger.warning("Generated material differs from verification file")
            logger.info(
                "This is expected: the verification file has organ-specific mappings"
            )
            logger.info("The generated file contains basic tissue definitions")
            return 0  # Not an error, just informational

    return 0


if __name__ == "__main__":
    sys.exit(main())
