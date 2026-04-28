from __future__ import annotations

import os
import sys
from typing import Any
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.config import (
    CtdiConfig,
    DicomConfig,
    GeneralConfig,
    ImagingConfig,
    SimulationConfig,
)
from src.orchestrator import Orchestrator


def _mock_generate(
    voltage: float, exposure: float, histories: str, project_root: str
) -> None:
    tmp_dir = os.path.join(project_root, "tmp")
    with open(os.path.join(tmp_dir, "ConvertedTopasFile.txt"), "w") as f:
        f.write("mock spectrum\n")
    with open(os.path.join(tmp_dir, "head_calibration_factor.txt"), "w") as f:
        f.write("1.0\n")


@pytest.fixture
def fake_project(tmp_path: Any) -> Any:
    project_root: str = str(tmp_path)

    boilerplates_dir: str = os.path.join(project_root, "src", "boilerplates")
    include_dir: str = os.path.join(boilerplates_dir, "TOPAS_includeFiles")
    os.makedirs(include_dir)

    head_content: str = (
        's:Ts/G4DataDirectory="/root/G4Data"\n'
        "i:Tf/NumberOfSequentialTimes = 501\n"
        "d:Tf/TimelineEnd = 501 s\n"
        "d:Tf/Rotate/Rate = 0.4 deg/s\n"
        "d:Tf/Rotate/StartValue = 90 deg\n"
        "i:Ts/Seed=9\n"
        "i:Ts/NumberOfThreads=4\n"
        "i:So/beam/NumberOfHistoriesInRun = 20\n"
        "dc:Ge/Coll1/TransY=5.3 cm\n"
        "dc:Ge/Coll2/TransY=-5.3 cm\n"
        "dc:Ge/Coll3/TransX=5.3 cm\n"
        "dc:Ge/Coll4/TransX=-5.3 cm\n"
        "includeFile = fullfan.txt\n"
        "includeFile = halffan.txt\n"
        "includeFile = CTDIphantom_16.txt\n"
        "includeFile = CTDIphantom_32.txt\n"
        'sv:Ph/Default/LayeredMassGeometryWorlds = 5 "ChamberPlugCentre"\n'
        'Ts/UseQt="True"\n'
        's:Gr/ViewA/Type="OpenGL"\n'
        'b:Gr/Enable="T"\n'
        "includeFile = patientDICOM.txt\n"
    )
    with open(
        os.path.join(boilerplates_dir, "headsourcecode_boilerplate.txt"), "w"
    ) as f:
        f.write(head_content)

    dicom_sub: str = (
        "d:Ge/patrotation/yaw= 0 deg\n"
        's:Ge/Patient/DicomDirectory = "/root/nccs/Sample_dicom_file/"\n'
        "dc:Ge/IsocenterX = 0 mm\n"
        "dc:Ge/IsocenterY = 0 mm\n"
        "dc:Ge/IsocenterZ = 0 mm\n"
        "dc:Ge/Patient/UserTransX = 0 mm\n"
        "dc:Ge/Patient/UserTransY = 0 mm\n"
        "dc:Ge/Patient/UserTransZ = 0 mm\n"
        's:Sc/DoseOnRTGrid100kz17/OutputFile = "Dose_PTV"\n'
    )
    with open(os.path.join(include_dir, "patientDICOM.txt"), "w") as f:
        f.write(dicom_sub)

    ctdi_16: str = (
        's:Ge/couch/Parent="couchgroup"\n'
        "d:Ge/couch/HLX=260. mm\n"
        "d:Ge/couch/HLY= 0.4 mm\n"
        "d:Ge/couch/HLZ= 1000 mm\n"
        "i:Sc/ChamberPlugDose_dtm/ZBins=100\n"
        "i:Sc/ChamberPlugDose_tle/ZBins=100\n"
        "i:Sc/ChamberPlugDose_dtw/ZBins=100\n"
    )
    with open(os.path.join(include_dir, "CTDIphantom_16.txt"), "w") as f:
        f.write(ctdi_16)

    ctdi_32: str = (
        's:Ge/couch/Parent="couchgroup"\n'
        "d:Ge/couch/HLX=260. mm\n"
        "d:Ge/couch/HLY= 0.4 mm\n"
        "d:Ge/couch/HLZ= 1000 mm\n"
        "i:Sc/ChamberPlugDose_dtm/ZBins=100\n"
        "i:Sc/ChamberPlugDose_tle/ZBins=100\n"
        "i:Sc/ChamberPlugDose_dtw/ZBins=100\n"
    )
    with open(os.path.join(include_dir, "CTDIphantom_32.txt"), "w") as f:
        f.write(ctdi_32)

    for name in [
        "fullfan.txt",
        "halffan.txt",
        "Muen.dat",
        "NbParticlesInTime.txt",
        "HUtoMaterialSchneider.txt",
    ]:
        with open(os.path.join(include_dir, name), "w") as f:
            f.write(name + " content\n")

    return tmp_path


class TestDicomDryRunPipeline:
    def test_full_dicom_pipeline(self, fake_project: Any) -> None:
        project_root: str = str(fake_project)
        config: SimulationConfig = SimulationConfig(
            general=GeneralConfig(
                g4_data_directory="/test/g4data",
                topas_directory="/test/topas",
                seed="42",
                threads="4",
                histories="100000",
            ),
            imaging=ImagingConfig(
                simulation_type="DICOM",
                start_angle="0 deg",
                rotation_direction="CBCT Clockwise",
                anode_voltage="80 kV",
                exposure="100 mAs",
                fan_mode="Full Fan",
                imaging_mode="Image Gently",
                rotation_rate="0.4 deg/s",
                timeline_end="501.0 s",
                sequential_times="1000",
                blade_x1="6.175536078965273 cm",
                blade_x2="-6.175536078965273 cm",
                blade_y1="5.814471115800571 cm",
                blade_y2="-5.814471115800571 cm",
            ),
            dicom=DicomConfig(
                dicom_directory="/test/dicom/patient",
                patient_id="TEST001",
                isocenter_x="10 mm",
                isocenter_y="20 mm",
                isocenter_z="30 mm",
                patient_shift_x="1.0 mm",
                patient_shift_y="2.0 mm",
                patient_shift_z="3.0 mm",
                patient_yaw="10.0 deg",
                graphics_enabled=False,
            ),
            ctdi=CtdiConfig(),
        )

        with patch(
            "src.orchestrator.SpectrumGenerator.generate", side_effect=_mock_generate
        ):
            rundir: str = Orchestrator(project_root).run(config, dry_run=True)

        assert os.path.isdir(rundir)
        assert rundir.startswith(os.path.join(project_root, "runfolder"))

        head_in_tmp: str = os.path.join(project_root, "tmp", "headsourcecode.txt")
        with open(head_in_tmp) as f:
            head_content: str = f.read()
        assert "i:Ts/Seed = 42\n" in head_content
        assert "i:Ts/NumberOfThreads = 4\n" in head_content
        assert 's:Ts/G4DataDirectory = "/test/g4data"\n' in head_content
        assert "includeFile = halffan.txt" not in head_content
        assert "includeFile = fullfan.txt" in head_content
        assert "includeFile = CTDIphantom_16.txt" not in head_content
        assert "includeFile = CTDIphantom_32.txt" not in head_content
        assert "sv:Ph/Default/LayeredMassGeometryWorlds" not in head_content
        assert "Ts/UseQt" not in head_content
        assert "s:Gr/ViewA/Type" not in head_content
        assert "b:Gr/Enable" not in head_content
        assert "includeFile = patientDICOM.txt" in head_content

        sub_in_tmp: str = os.path.join(project_root, "tmp", "patientDICOM.txt")
        with open(sub_in_tmp) as f:
            sub_content: str = f.read()
        assert "d:Ge/patrotation/yaw = 10.0 deg\n" in sub_content
        assert 's:Ge/Patient/DicomDirectory = "/test/dicom/patient"\n' in sub_content
        assert "dc:Ge/IsocenterX = 10 mm\n" in sub_content
        assert "dc:Ge/IsocenterY = 20 mm\n" in sub_content
        assert "dc:Ge/IsocenterZ = 30 mm\n" in sub_content
        assert "dc:Ge/Patient/UserTransX = 1.0 mm\n" in sub_content
        assert "dc:Ge/Patient/UserTransY = 2.0 mm\n" in sub_content
        assert "dc:Ge/Patient/UserTransZ = 3.0 mm\n" in sub_content
        assert "TEST001_CBCT Clockwise_Image Gently_0 deg_DOSE_PTV" in sub_content

        with open(os.path.join(rundir, "headsourcecode.txt")) as f:
            rundir_head: str = f.read()
        assert "i:Ts/Seed = 42\n" in rundir_head

        for fname in [
            "headsourcecode.txt",
            "patientDICOM.txt",
            "HUtoMaterialSchneider.txt",
            "Muen.dat",
            "NbParticlesInTime.txt",
            "ConvertedTopasFile.txt",
            "head_calibration_factor.txt",
            "fullfan.txt",
        ]:
            assert os.path.isfile(os.path.join(rundir, fname)), "Missing: " + fname

        assert not os.path.isfile(os.path.join(rundir, "halffan.txt"))


class TestCtdiDryRunPipeline:
    def test_full_ctdi_pipeline(self, fake_project: Any) -> None:
        project_root: str = str(fake_project)
        config: SimulationConfig = SimulationConfig(
            general=GeneralConfig(
                g4_data_directory="/test/g4data",
                topas_directory="/test/topas",
                seed="42",
                threads="4",
                histories="100000",
            ),
            imaging=ImagingConfig(
                simulation_type="CTDI validation",
                start_angle="0 deg",
                rotation_direction="CBCT Clockwise",
                anode_voltage="80 kV",
                exposure="100 mAs",
                fan_mode="Full Fan",
                imaging_mode="Image Gently",
                rotation_rate="0.4 deg/s",
                timeline_end="501.0 s",
                sequential_times="1000",
                blade_x1="6.175536078965273 cm",
                blade_x2="-6.175536078965273 cm",
                blade_y1="5.814471115800571 cm",
                blade_y2="-5.814471115800571 cm",
            ),
            dicom=DicomConfig(),
            ctdi=CtdiConfig(
                phantom_size="16 cm",
                dose_to_medium_zbins="200",
                tle_zbins="50",
                dose_to_water_zbins="150",
                couch_enabled=True,
                couch_width="300. mm",
                couch_thickness="1.0 mm",
                couch_length="1500 mm",
                user_blade_enabled=False,
                graphics_enabled=False,
            ),
        )

        with patch(
            "src.orchestrator.SpectrumGenerator.generate", side_effect=_mock_generate
        ):
            rundir: str = Orchestrator(project_root).run(config, dry_run=True)

        assert os.path.isdir(rundir)
        assert rundir.startswith(os.path.join(project_root, "runfolder"))

        head_in_tmp: str = os.path.join(project_root, "tmp", "headsourcecode.txt")
        with open(head_in_tmp) as f:
            head_content: str = f.read()
        assert "i:Ts/Seed = 42\n" in head_content
        assert "includeFile = halffan.txt" not in head_content
        assert "includeFile = patientDICOM.txt" not in head_content
        assert "includeFile = CTDIphantom_32.txt" not in head_content
        assert "includeFile = CTDIphantom_16.txt" in head_content
        assert "Ts/UseQt" not in head_content
        assert "s:Gr/ViewA/Type" not in head_content
        assert "b:Gr/Enable" not in head_content

        ctdi_sub: str = os.path.join(project_root, "tmp", "CTDIphantom_16.txt")
        with open(ctdi_sub) as f:
            sub_content: str = f.read()
        assert 's:Ge/couch/Parent="couchgroup"\n' in sub_content
        assert "d:Ge/couch/HLX = 300. mm\n" in sub_content
        assert "d:Ge/couch/HLY = 1.0 mm\n" in sub_content
        assert "d:Ge/couch/HLZ = 1500 mm\n" in sub_content
        assert "i:Sc/ChamberPlugDose_dtm/ZBins = 200\n" in sub_content
        assert "i:Sc/ChamberPlugDose_tle/ZBins = 50\n" in sub_content
        assert "i:Sc/ChamberPlugDose_dtw/ZBins = 150\n" in sub_content

        for fname in [
            "Muen.dat",
            "NbParticlesInTime.txt",
            "ConvertedTopasFile.txt",
            "head_calibration_factor.txt",
            "fullfan.txt",
        ]:
            assert os.path.isfile(os.path.join(rundir, fname)), "Missing: " + fname

        assert not os.path.isfile(os.path.join(rundir, "headsourcecode.txt"))
        assert not os.path.isfile(os.path.join(rundir, "halffan.txt"))
        assert not os.path.isfile(os.path.join(rundir, "patientDICOM.txt"))
