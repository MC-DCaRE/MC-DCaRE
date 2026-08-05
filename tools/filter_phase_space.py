"""Filter a TOPAS phase-space file to particles within a Z-field range.

The PhspSurface (100cm x 100cm) captures scattered photons far outside the
beam field. For phantom replay, filter to the primary beam field to avoid
depositing spurious dose in non-target anatomy.

Usage:
    python tools/filter_phase_space.py \\
        --input beam_exit_phsp.phsp \\
        --output beam_exit_phsp_filtered.phsp \\
        --z-max 8.0
"""

from __future__ import annotations

import argparse
import logging
import os
import struct

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

RECORD_SIZE = 34  # 7 x f4 + i4 + 2 x byte


def filter_phase_space(input_path: str, output_path: str, z_max_cm: float) -> int:
    """Filter particles with |Z| <= z_max_cm. Returns count of kept particles."""
    kept = 0
    total = 0

    with open(input_path, "rb") as fin, open(output_path, "wb") as fout:
        while True:
            data = fin.read(RECORD_SIZE)
            if len(data) < RECORD_SIZE:
                break
            total += 1
            # Z is the 3rd float (index 2) in the record
            z = struct.unpack_from("<f", data, 8)[0]
            if abs(z) <= z_max_cm:
                fout.write(data)
                kept += 1

    logger.info(
        "Filtered %s -> %s: %d / %d particles kept (%.1f%%), z_max=%.1f cm",
        input_path,
        output_path,
        kept,
        total,
        100.0 * kept / total if total else 0,
        z_max_cm,
    )
    return kept


def update_header(header_path: str, n_particles: int) -> None:
    """Update the .header file with new particle counts."""
    if not os.path.exists(header_path):
        logger.warning("Header file %s not found, skipping update", header_path)
        return

    with open(header_path) as f:
        content = f.read()

    for old_prefix in [
        "Number of Original Histories:",
        "Number of Original Histories that Reached Phase Space:",
        "Number of Scored Particles:",
    ]:
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if line.strip().startswith(old_prefix):
                lines[i] = f"{old_prefix} {n_particles}"
        content = "\n".join(lines)

    with open(header_path, "w") as f:
        f.write(content)
    logger.info("Updated %s with %d particles", header_path, n_particles)


def main():
    parser = argparse.ArgumentParser(
        description="Filter TOPAS phase-space file to Z-field range"
    )
    parser.add_argument("--input", required=True, help="Input .phsp file")
    parser.add_argument("--output", required=True, help="Output .phsp file")
    parser.add_argument(
        "--z-max",
        type=float,
        default=8.0,
        help="Maximum |Z| in cm (default: 8.0)",
    )
    args = parser.parse_args()

    kept = filter_phase_space(args.input, args.output, args.z_max)

    header_in = os.path.splitext(args.input)[0] + ".header"
    header_out = os.path.splitext(args.output)[0] + ".header"
    if os.path.exists(header_in):
        import shutil

        shutil.copy(header_in, header_out)
        update_header(header_out, kept)


if __name__ == "__main__":
    main()
