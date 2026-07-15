#!/usr/bin/env python3
"""
Regenerate voxelized phantom with real ICRP tissue materials.
Parses MRCP_AM.material, creates TOPAS material definitions, and
generates phantomVoxel.txt with proper material assignments.
"""

from __future__ import annotations

import numpy as np
import os
import sys

# Z number to element name mapping (TOPAS requires full names)
Z_TO_NAME = {
    1000: "Hydrogen", 2000: "Helium", 6000: "Carbon", 7000: "Nitrogen",
    8000: "Oxygen", 9000: "Fluorine", 11000: "Sodium", 12000: "Magnesium",
    13000: "Aluminum", 14000: "Silicon", 15000: "Phosphorus", 16000: "Sulfur",
    17000: "Chlorine", 19000: "Potassium", 20000: "Calcium", 26000: "Iron",
    27000: "Cobalt", 29000: "Copper", 30000: "Zinc", 53000: "Iodine",
    79000: "Gold", 82000: "Lead",
}


def parse_material_file(filepath: str) -> dict[int, dict]:
    """Parse ICRP material file. Returns dict: material_id -> {name, density, components}."""
    materials = {}
    current_name = ""
    current_density = 0.0
    current_id = None
    current_elements = []

    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            if line.startswith("C "):
                # Save previous material
                if current_id is not None:
                    materials[current_id] = {
                        "name": current_name,
                        "density": current_density,
                        "elements": current_elements[:],
                    }
                # Start new material
                # Format: "C <organ_name> <density> g/cm3"
                parts = line.split()
                current_name = parts[1]
                current_density = float(parts[2])
                current_id = None
                current_elements = []
            elif line == "C":
                # End of material block
                if current_id is not None:
                    materials[current_id] = {
                        "name": current_name,
                        "density": current_density,
                        "elements": current_elements[:],
                    }
                current_id = None
            elif line.startswith("m") and not line.startswith("m g"):
                # Material definition: "m<id>     <Z>      <-fraction>"
                parts = line.split()
                mat_id_str = parts[0][1:]  # Remove 'm'
                try:
                    current_id = int(mat_id_str)
                except ValueError:
                    continue
                # First element on same line
                z = int(parts[1])
                frac = abs(float(parts[2]))  # Remove negative sign
                current_elements.append((z, frac))
            elif current_id is not None and len(line) > 0 and line[0].isdigit():
                # Continuation line: "     <Z>      <-fraction>"
                parts = line.split()
                if len(parts) >= 2:
                    z = int(parts[0])
                    frac = abs(float(parts[1]))
                    current_elements.append((z, frac))

    # Save last material
    if current_id is not None:
        materials[current_id] = {
            "name": current_name,
            "density": current_density,
            "elements": current_elements[:],
        }

    return materials


def generate_topas_materials(materials: dict[int, dict], output_file: str):
    """Write TOPAS material definitions."""
    with open(output_file, "w") as f:
        f.write("# ICRP 145 MRCP-AM tissue material definitions\n")
        f.write(f"# {len(materials)} materials\n\n")

        for mat_id in sorted(materials.keys()):
            mat = materials[mat_id]
            mat_name = f"ICRP_{mat_id}"

            # Get element symbols and fractions
            names = []
            fracs = []
            for z, frac in mat["elements"]:
                name = Z_TO_NAME.get(z)
                if name is None:
                    print(f"  WARNING: Unknown Z={z} in material {mat_id} ({mat['name']})")
                    continue
                names.append(name)
                fracs.append(frac)

            if not names:
                continue

            n = len(names)
            comp_str = " ".join(f'"{nm}"' for nm in names)
            frac_str = " ".join(f"{fr:.6f}" for fr in fracs)
            f.write(f"# {mat['name']} (ID={mat_id}, density={mat['density']} g/cm3)\n")
            f.write(f'sv:Ma/{mat_name}/Components = {n} {comp_str}\n')
            f.write(f'uv:Ma/{mat_name}/Fractions = {n} {frac_str}\n')
            f.write(f'd:Ma/{mat_name}/Density = {mat["density"]} g/cm3\n\n')

    print(f"  Wrote {len(materials)} material definitions to {output_file}")


def regenerate_voxel_phantom(
    grid_path: str,
    origin_path: str,
    materials: dict[int, dict],
    voxel_size: float,
    output_file: str,
    materials_file: str,
):
    """Regenerate phantomVoxel.txt with real ICRP material names."""
    grid = np.load(grid_path)
    origin = np.load(origin_path)
    nx, ny, nz = grid.shape

    print(f"  Grid: {nx} x {ny} x {nz} = {np.prod(grid.shape)} voxels")
    print(f"  Voxel size: {voxel_size} cm")

    # Build VoxelMaterials vector
    print("  Building material vector...")
    mat_names = []
    for iz in range(nz):
        for iy in range(ny):
            for ix in range(nx):
                mat_id = int(grid[ix, iy, iz])
                if mat_id == -1:
                    mat_names.append("Air")
                else:
                    mat_names.append(f"ICRP_{mat_id}")

    total = len(mat_names)

    hlx = nx * voxel_size / 2.0
    hly = ny * voxel_size / 2.0
    hlz = nz * voxel_size / 2.0
    cx = float(origin[0]) + nx * voxel_size / 2.0
    cy = float(origin[1]) + ny * voxel_size / 2.0
    cz = float(origin[2]) + nz * voxel_size / 2.0

    with open(output_file, "w") as f:
        f.write("# Voxelized MRCP-AM phantom with real ICRP materials\n")
        f.write(f"# Voxel size: {voxel_size} cm ({voxel_size*10} mm)\n")
        f.write(f"# Grid: {nx} x {ny} x {nz} = {total} voxels\n\n")

        # Include material definitions
        f.write(f'includeFile = {os.path.basename(materials_file)}\n\n')

        # Phantom geometry
        f.write('s:Ge/Phantom/Type = "TsBox"\n')
        f.write('s:Ge/Phantom/Parent = "World"\n')
        f.write('s:Ge/Phantom/Material = "G4_WATER"\n')
        f.write(f"d:Ge/Phantom/HLX = {hlx:.2f} cm\n")
        f.write(f"d:Ge/Phantom/HLY = {hly:.2f} cm\n")
        f.write(f"d:Ge/Phantom/HLZ = {hlz:.2f} cm\n")
        f.write(f"d:Ge/Phantom/TransX = {cx:.2f} cm\n")
        f.write(f"d:Ge/Phantom/TransY = {cy:.2f} cm\n")
        f.write(f"d:Ge/Phantom/TransZ = {cz:.2f} cm\n")
        f.write("d:Ge/Phantom/RotX = 0.0 deg\n")
        f.write("d:Ge/Phantom/RotY = 0.0 deg\n")
        f.write("d:Ge/Phantom/RotZ = 0.0 deg\n")
        f.write('s:Ge/Phantom/Color = "yellow"\n\n')

        # Voxel divisions
        f.write(f"i:Ge/Phantom/XBins = {nx}\n")
        f.write(f"i:Ge/Phantom/YBins = {ny}\n")
        f.write(f"i:Ge/Phantom/ZBins = {nz}\n")

        # VoxelMaterials
        f.write(f"sv:Ge/Phantom/VoxelMaterials = {total}")
        for name in mat_names:
            f.write(f' "{name}"')
        f.write("\n\n")

        # Scorer
        f.write('s:Sc/PhantomDose/Quantity = "DoseToMedium"\n')
        f.write('s:Sc/PhantomDose/Component = "Phantom"\n')
        f.write('s:Sc/PhantomDose/OutputFile = "phantom_dose"\n')
        f.write('s:Sc/PhantomDose/IfOutputFileAlreadyExists = "Overwrite"\n')

    fsize = os.path.getsize(output_file)
    print(f"  File size: {fsize / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    project_root = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/..")
    phantom_dir = os.path.join(project_root, "data/P145/Phantom_data/MRCP_AM")
    output_dir = os.path.join(project_root, "test_voxel_output/mrcp_am")
    voxel_size = 1.0  # cm

    # Parse materials
    print("Parsing ICRP material file...")
    materials = parse_material_file(os.path.join(phantom_dir, "MRCP_AM.material"))
    print(f"  Parsed {len(materials)} materials")

    # Check for unknown Z numbers
    unknown_z = set()
    for mat_id, mat in materials.items():
        for z, _ in mat["elements"]:
            if z not in Z_TO_NAME:
                unknown_z.add(z)
    if unknown_z:
        print(f"  WARNING: Unknown Z numbers: {unknown_z}")

    # Generate TOPAS material definitions
    print("\nGenerating TOPAS material definitions...")
    materials_file = os.path.join(output_dir, "icrp_materials.txt")
    generate_topas_materials(materials, materials_file)

    # Regenerate voxel phantom
    print("\nRegenerating voxelized phantom...")
    phantom_file = os.path.join(output_dir, "phantomVoxel.txt")
    regenerate_voxel_phantom(
        os.path.join(output_dir, "mrcp_am_voxels.npy"),
        os.path.join(output_dir, "mrcp_am_origin.npy"),
        materials,
        voxel_size,
        phantom_file,
        materials_file,
    )

    print(f"\nDone! Files in: {output_dir}")
    print(f"  icrp_materials.txt - TOPAS material definitions")
    print(f"  phantomVoxel.txt   - Voxelized phantom with real materials")