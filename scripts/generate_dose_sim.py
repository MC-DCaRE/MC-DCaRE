#!/usr/bin/env python3
"""
Generate dose simulation TOPAS files from the pipeline.
Creates two versions: quick test (100 histories) and proper run (full histories).
"""

from __future__ import annotations

import os
import sys
import shutil
import re
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")

from src.config import (
    CtdiConfig, DicomConfig, GeneralConfig, ImagingConfig,
    PhantomConfig, SimulationConfig,
)
from src.orchestrator import Orchestrator


def _mock_generate(voltage, exposure, histories, project_root,
                   dose_calibration_factor=1.0, **kwargs):
    tmp_dir = os.path.join(project_root, "tmp")
    os.makedirs(tmp_dir, exist_ok=True)
    # Write proper TOPAS spectrum parameters (100 keV monoenergetic approximation)
    with open(os.path.join(tmp_dir, "ConvertedTopasFile.txt"), "w") as f:
        f.write("# Mock spectrum - 100 keV narrow band\n")
        f.write("dv:So/beam/BeamEnergySpectrumValues = 2\n 30.0 110.0 keV\n\n")
        f.write("uv:So/beam/BeamEnergySpectrumWeights = 2\n 1.0 1.0\n")
    with open(os.path.join(tmp_dir, "head_calibration_factor.txt"), "w") as f:
        f.write("1.0\n")
    with open(os.path.join(tmp_dir, "simulation_metadata.yaml"), "w") as f:
        f.write("total_histories: 1000000\nexposure_mAs: 100\nspectrum_fluence_photons_per_mAs: 2.34e8\n")


def create_water_box_phantom(rundir: str) -> str:
    """Create a water box phantom matching Omed bounding box."""
    phantom_file = os.path.join(rundir, "phantomVoxel.txt")
    with open(phantom_file, "w") as f:
        f.write("# Water box phantom (Omed bounding box)\n\n")
        f.write('s:Ge/Phantom/Type = "TsBox"\n')
        f.write('s:Ge/Phantom/Parent = "World"\n')
        f.write('s:Ge/Phantom/Material = "G4_WATER"\n')
        f.write("d:Ge/Phantom/HLX = 51.0 cm\n")
        f.write("d:Ge/Phantom/HLY = 28.5 cm\n")
        f.write("d:Ge/Phantom/HLZ = 68.0 cm\n")
        f.write("d:Ge/Phantom/TransX = 2.0 cm\n")
        f.write("d:Ge/Phantom/TransY = -0.5 cm\n")
        f.write("d:Ge/Phantom/TransZ = 18.0 cm\n")
        f.write("d:Ge/Phantom/RotX = 0.0 deg\n")
        f.write("d:Ge/Phantom/RotY = 0.0 deg\n")
        f.write("d:Ge/Phantom/RotZ = 0.0 deg\n")
        f.write('s:Ge/Phantom/Color = "yellow"\n\n')
        f.write("# Dose scorer\n")
        f.write('s:Sc/PhantomDose/Quantity = "DoseToMedium"\n')
        f.write('s:Sc/PhantomDose/Component = "Phantom"\n')
        f.write('s:Sc/PhantomDose/OutputFile = "phantom_dose"\n')
        f.write('s:Sc/PhantomDose/IfOutputFileAlreadyExists = "Overwrite"\n')
    return phantom_file


def make_dose_file(head_file, output_file, histories, gantry_angle=0.0):
    """Create a dose simulation TOPAS file."""
    with open(head_file, "r") as f:
        content = f.read()

    # Replace phantom include
    content = content.replace("includeFile = phantomICRP145.txt",
                              "includeFile = phantomVoxel.txt")
    content = content.replace("i:Ts/ParameterizationErrorMaxReports = 5\n", "")

    # Set histories and threads
    content = re.sub(r"i:So/beam/NumberOfHistoriesInRun = \d+",
                     f"i:So/beam/NumberOfHistoriesInRun = {histories}", content)
    content = re.sub(r"i:Ts/NumberOfThreads = \d+",
                     "i:Ts/NumberOfThreads = 1", content)

    # Fixed gantry angle
    content = re.sub(r"d:Tf/Rotate/Rate = [\d.]+",
                     "d:Tf/Rotate/Rate = 0.0", content)
    content = re.sub(r"d:Tf/Rotate/StartValue = [\d.]+",
                     f"d:Tf/Rotate/StartValue = {gantry_angle}", content)
    content = re.sub(r"i:Tf/NumberOfSequentialTimes = \d+",
                     "i:Tf/NumberOfSequentialTimes = 1", content)
    content = re.sub(r"d:Tf/TimelineEnd = [\d.]+",
                     "d:Tf/TimelineEnd = 1.0", content)

    # Remove graphics
    lines = content.split("\n")
    filtered = [l for l in lines
                if not any(k in l for k in ["Gr/ViewA", "Gr/Enable", "Gr/Color",
                                            "Ts/UseQt", "Ts/ShowCPUTime"])]
    content = "\n".join(filtered)

    with open(output_file, "w") as f:
        f.write(content)


def make_tetgeom_dose_file(head_file, output_file, histories, gantry_angle=0.0):
    """Create a dose simulation TOPAS file using TsTetGeom (not voxelized)."""
    with open(head_file, "r") as f:
        content = f.read()

    # Keep phantomICRP145.txt (TsTetGeom)
    # Add parameterization error limit
    if "ParameterizationErrorMaxReports" not in content:
        content += "\ni:Ts/ParameterizationErrorMaxReports = 5\n"

    # Set histories and threads (single thread for MT-safe scoring)
    content = re.sub(r"i:So/beam/NumberOfHistoriesInRun = \d+",
                     f"i:So/beam/NumberOfHistoriesInRun = {histories}", content)
    content = re.sub(r"i:Ts/NumberOfThreads = \d+",
                     "i:Ts/NumberOfThreads = 1", content)

    # Fixed gantry angle
    content = re.sub(r"d:Tf/Rotate/Rate = [\d.]+",
                     "d:Tf/Rotate/Rate = 0.0", content)
    content = re.sub(r"d:Tf/Rotate/StartValue = [\d.]+",
                     f"d:Tf/Rotate/StartValue = {gantry_angle}", content)
    content = re.sub(r"i:Tf/NumberOfSequentialTimes = \d+",
                     "i:Tf/NumberOfSequentialTimes = 1", content)
    content = re.sub(r"d:Tf/TimelineEnd = [\d.]+",
                     "d:Tf/TimelineEnd = 1.0", content)

    # Remove graphics
    lines = content.split("\n")
    filtered = [l for l in lines
                if not any(k in l for k in ["Gr/ViewA", "Gr/Enable", "Gr/Color",
                                            "Ts/UseQt", "Ts/ShowCPUTime"])]
    content = "\n".join(filtered)

    with open(output_file, "w") as f:
        f.write(content)


def main():
    project_root = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/..")

    config = SimulationConfig(
        general=GeneralConfig(
            g4_data_directory="/opt/topas/GEANT4/G4DATA",
            topas_directory="/opt/topas/TOPAS/OpenTOPAS-install/bin/topas",
            seed="42", threads="1", histories="100",
        ),
        imaging=ImagingConfig(
            simulation_type="ICRP145",
            start_angle="0 deg", rotation_direction="CBCT Clockwise",
            anode_voltage="100 kV", exposure="100 mAs",
            fan_mode="Full Fan", imaging_mode="Image Gently",
            rotation_rate="0.4 deg/s", timeline_end="1.0 s",
            sequential_times="1",
            blade_x1="6.175536078965273 cm",
            blade_x2="-6.175536078965273 cm",
            blade_y1="5.814471115800571 cm",
            blade_y2="-5.814471115800571 cm",
        ),
        dicom=DicomConfig(), ctdi=CtdiConfig(),
        phantom=PhantomConfig(
            phantom_data_directory=os.path.join(project_root, "data/P145/Phantom_data"),
            phantom_sex="AM", phantom_name="Omed",
            organ_scoring_ids="Blood",
        ),
    )

    print("Running dry-run pipeline...")
    with patch("src.orchestrator.SpectrumGenerator.generate", side_effect=_mock_generate):
        rundir = Orchestrator(project_root).run(config, dry_run=True)

    head_file = os.path.join(rundir, "headsourcecode.txt")
    if not os.path.isfile(head_file):
        head_file = os.path.join(project_root, "tmp", "headsourcecode.txt")

    create_water_box_phantom(rundir)

    dose_dir = os.path.join(project_root, "test_voxel_visualizations", "dose_sim")
    os.makedirs(dose_dir, exist_ok=True)

    # Quick test: 100 histories (voxelized)
    make_dose_file(head_file, os.path.join(dose_dir, "dose_quick.topas"), 100)
    print("Created dose_quick.topas (100 histories)")

    # Proper run: 100000 histories (voxelized)
    make_dose_file(head_file, os.path.join(dose_dir, "dose_full.topas"), 100000)
    print("Created dose_full.topas (100,000 histories)")

    # TsTetGeom run: 100000 histories (tetrahedral phantom, full beamline)
    make_tetgeom_dose_file(head_file, os.path.join(dose_dir, "dose_tetgeom.topas"), 100000)
    print("Created dose_tetgeom.topas (100,000 histories, TsTetGeom)")

    # Copy supporting files
    for fname in ["phantomVoxel.txt", "fullfan.txt", "ConvertedTopasFile.txt",
                  "head_calibration_factor.txt", "Muen.dat"]:
        src = os.path.join(rundir, fname)
        if os.path.isfile(src):
            shutil.copy(src, os.path.join(dose_dir, fname))
    tmp_dir = os.path.join(project_root, "tmp")
    for fname in ["fullfan.txt", "ConvertedTopasFile.txt", "head_calibration_factor.txt"]:
        src_tmp = os.path.join(tmp_dir, fname)
        if os.path.isfile(src_tmp) and not os.path.isfile(os.path.join(dose_dir, fname)):
            shutil.copy(src_tmp, os.path.join(dose_dir, fname))

    print(f"\nFiles created in: {dose_dir}")


if __name__ == "__main__":
    main()