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
    PhantomConfig,
    SimulationConfig,
)
from src.orchestrator import Orchestrator


def _mock_generate(
    voltage: float,
    exposure: float,
    histories: str,
    project_root: str,
    dose_calibration_factor: float = 1.0,
    **kwargs: object,
) -> None:
    tmp_dir = os.path.join(project_root, "tmp")
    with open(os.path.join(tmp_dir, "ConvertedTopasFile.txt"), "w") as f:
        f.write("mock spectrum\n")
    with open(os.path.join(tmp_dir, "head_calibration_factor.txt"), "w") as f:
        f.write("1.0\n")
    with open(os.path.join(tmp_dir, "simulation_metadata.yaml"), "w") as f:
        f.write(
            "total_histories: 100000\nexposure_mAs: 100\nspectrum_fluence_photons_per_mAs: 2.34e8\n"
        )


@pytest.fixture
def fake_project(tmp_path: Any) -> Any:
    project_root: str = str(tmp_path)

    boilerplates_dir: str = os.path.join(project_root, "src", "boilerplates")
    include_dir: str = os.path.join(boilerplates_dir, "TOPAS_includeFiles")
    os.makedirs(include_dir)

    head_template: str = (
        "includeFile=ConvertedTopasFile.txt\n"
        "{% if fan_mode == 'Full Fan' %}includeFile = fullfan.txt\n{% endif %}"
        "{% if fan_mode == 'Half Fan' %}includeFile = halffan.txt\n{% endif %}"
        "{% if simulation_type == 'DICOM' %}includeFile = patientDICOM.txt\n{% endif %}"
        "{% if simulation_type == 'CTDI' %}sv:Ph/Default/LayeredMassGeometryWorlds = 5"
        ' "ChamberPlugCentre" "ChamberPlugTop" "ChamberPlugBottom" "ChamberPlugLeft" "ChamberPlugRight"\n{% endif %}'
        "{% if simulation_type == 'ICRP145' %}{% if use_voxel_phantom %}includeFile = phantomVoxel.txt\n{% else %}includeFile = phantomICRP145.txt\n{% endif %}{% endif %}"
        "i:Ts/Seed = {{ seed }}\n"
        "i:Ts/NumberOfThreads = {{ threads }}\n"
        's:Ts/G4DataDirectory = "{{ g4_data_directory }}"\n'
        "i:So/beam/NumberOfHistoriesInRun = {{ histories }}\n"
        "i:Tf/NumberOfSequentialTimes = {{ sequential_times }}\n"
        "d:Tf/TimelineEnd = {{ timeline_end }}\n"
        "d:Tf/Rotate/Rate = {{ rotation_rate }}\n"
        "d:Tf/Rotate/StartValue = {{ start_angle }}\n"
        "dc:Ge/Coll1/TransY = {{ coll1_trans_y }}\n"
        "dc:Ge/Coll2/TransY = {{ coll2_trans_y }}\n"
        "dc:Ge/Coll3/TransX = {{ coll3_trans_x }}\n"
        "dc:Ge/Coll4/TransX = {{ coll4_trans_x }}\n"
        "dc:Ge/Rotation/RotX= {{ patient_pitch }}\n"
        "d:Ge/patrotation/yaw= {{ patient_yaw }}\n"
        "dc:Ge/Rotation/RotY= 180. deg + Ge/patrotation/yaw\n"
        "dc:Ge/Rotation/RotZ= Tf/Rotate/Value + {{ patient_roll_value }} deg\n"
        '{% if graphics_enabled %}Ts/UseQt="True"\n'
        's:Gr/ViewA/Type="OpenGL"\n'
        'b:Gr/Enable="T"\n{% endif %}'
    )
    with open(
        os.path.join(boilerplates_dir, "headsourcecode_boilerplate.j2"), "w"
    ) as f:
        f.write(head_template)

    dicom_template: str = (
        "includeFile= HUtoMaterialSchneider.txt\n"
        's:Ge/Patient/DicomDirectory = "{{ dicom_directory }}"\n'
        "d:Ge/Patient/RotX = {{ patient_pitch }}\n"
        "d:Ge/Patient/RotZ = {{ patient_yaw }}\n"
        "dc:Ge/IsocenterX = {{ isocenter_x }}\n"
        "dc:Ge/IsocenterY = {{ isocenter_y }}\n"
        "dc:Ge/IsocenterZ = {{ isocenter_z }}\n"
        "dc:Ge/Patient/UserTransX = {{ patient_shift_x }}\n"
        "dc:Ge/Patient/UserTransY = {{ patient_shift_y }}\n"
        "dc:Ge/Patient/UserTransZ = {{ patient_shift_z }}\n"
        's:Sc/DoseOnRTGrid100kz17/OutputFile = "{{ output_filename }}"\n'
    )
    with open(os.path.join(include_dir, "patientDICOM.j2"), "w") as f:
        f.write(dicom_template)

    ctdi_16_template: str = (
        "{% if couch_enabled %}#couch\n"
        's:Ge/couchgroup/Type="Group"\n'
        's:Ge/couchgroup/Parent="World"\n'
        's:Ge/couch/Type="TsBox"\n'
        "d:Ge/couch/HLX = {{ couch_width }}\n"
        "d:Ge/couch/HLY = {{ couch_thickness }}\n"
        "d:Ge/couch/HLZ = {{ couch_length }}\n"
        "{% endif %}"
        "{% for position in plug_positions %}"
        "i:Sc/{{ position }}_dtm/ZBins={{ dose_to_medium_zbins }}\n"
        "i:Sc/{{ position }}_tle/ZBins={{ tle_zbins }}\n"
        "i:Sc/{{ position }}_dtw/ZBins={{ dose_to_water_zbins }}\n"
        's:Sc/{{ position }}_tle/Component="{{ position }}"\n'
        "{% endfor %}"
    )
    with open(os.path.join(include_dir, "CTDIphantom_16.j2"), "w") as f:
        f.write(ctdi_16_template)

    with open(os.path.join(include_dir, "CTDIphantom_32.j2"), "w") as f:
        f.write(ctdi_16_template)

    phantom_template: str = (
        's:Ge/phantomcouchgroup/Type="Group"\n'
        's:Ge/phantomcouchgroup/Parent="World"\n'
        "{% if couch_enabled %}"
        's:Ge/phantomcouch/Type="TsBox"\n'
        "d:Ge/phantomcouch/HLX = {{ couch_width }}\n"
        "d:Ge/phantomcouch/HLY = {{ couch_thickness }}\n"
        "d:Ge/phantomcouch/HLZ = {{ couch_length }}\n"
        "{% endif %}"
        's:Ge/Phantom/Type="TsTetGeom"\n'
        's:Ge/Phantom/Parent="World"\n'
        's:Ge/Phantom/PhantomDirectory = "{{ phantom_directory }}/"\n'
        's:Ge/Phantom/NodeFile = "{{ phantom_name }}.node"\n'
        's:Ge/Phantom/EleFile = "{{ phantom_name }}.ele"\n'
        's:Sc/PhantomDose/Quantity = "TsTetGeomScorer"\n'
        's:Sc/PhantomDose/OutputFile = "{{ output_filename }}"\n'
    )
    with open(os.path.join(include_dir, "phantomICRP145.j2"), "w") as f:
        f.write(phantom_template)

    for name in [
        "fullfan.txt",
        "halffan.txt",
        "Muen.dat",
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
                patient_pitch="2.0 deg",
                patient_roll="-5.0 deg",
                graphics_enabled=False,
            ),
            ctdi=CtdiConfig(),
        )

        with patch(
            "src.orchestrator.SpectrumGenerator.generate", side_effect=_mock_generate
        ):
            rundir: str = Orchestrator(project_root).run(config, dry_run=True)

        assert os.path.isdir(rundir)
        assert os.path.normpath(rundir).startswith(
            os.path.normpath(os.path.join(project_root, "runfolder"))
        )

        head_in_tmp: str = os.path.join(project_root, "tmp", "headsourcecode.txt")
        with open(head_in_tmp) as f:
            head_content: str = f.read()
        assert "i:Ts/Seed = 42\n" in head_content
        assert "i:Ts/NumberOfThreads = 4\n" in head_content
        assert 's:Ts/G4DataDirectory = "/test/g4data"\n' in head_content
        assert "includeFile = halffan.txt" not in head_content
        assert "includeFile = fullfan.txt" in head_content
        assert "sv:Ph/Default/LayeredMassGeometryWorlds" not in head_content
        assert "Ts/UseQt" not in head_content
        assert "includeFile = patientDICOM.txt" in head_content
        assert "dc:Ge/Rotation/RotX= 2 deg\n" in head_content
        assert "d:Ge/patrotation/yaw= 10 deg\n" in head_content
        assert "dc:Ge/Rotation/RotZ= Tf/Rotate/Value + -5.0 deg\n" in head_content

        sub_in_tmp: str = os.path.join(project_root, "tmp", "patientDICOM.txt")
        with open(sub_in_tmp) as f:
            sub_content: str = f.read()
        assert 's:Ge/Patient/DicomDirectory = "/test/dicom/patient"\n' in sub_content
        assert "d:Ge/Patient/RotX = 2 deg\n" in sub_content
        assert "d:Ge/Patient/RotZ = 10 deg\n" in sub_content
        assert "dc:Ge/IsocenterX = 10 mm\n" in sub_content
        assert "dc:Ge/IsocenterY = 20 mm\n" in sub_content
        assert "dc:Ge/IsocenterZ = 30 mm\n" in sub_content
        assert "dc:Ge/Patient/UserTransX = 1 mm\n" in sub_content
        assert "dc:Ge/Patient/UserTransY = 2 mm\n" in sub_content
        assert "dc:Ge/Patient/UserTransZ = 3 mm\n" in sub_content
        assert "TEST001_CBCT Clockwise_Image Gently_0 deg_DOSE_PTV" in sub_content

        with open(os.path.join(rundir, "headsourcecode.txt")) as f:
            rundir_head: str = f.read()
        assert "i:Ts/Seed = 42\n" in rundir_head

        for fname in [
            "headsourcecode.txt",
            "patientDICOM.txt",
            "HUtoMaterialSchneider.txt",
            "Muen.dat",
            "ConvertedTopasFile.txt",
            "head_calibration_factor.txt",
            "simulation_metadata.yaml",
            "fullfan.txt",
        ]:
            assert os.path.isfile(os.path.join(rundir, fname)), "Missing: " + fname

        assert not os.path.isfile(os.path.join(rundir, "halffan.txt"))

        # Verify metadata format
        meta_path = os.path.join(rundir, "simulation_metadata.yaml")
        with open(meta_path) as f:
            import yaml

            meta = yaml.safe_load(f)
        assert "total_histories" in meta
        assert "exposure_mAs" in meta
        assert "spectrum_fluence_photons_per_mAs" in meta


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
                simulation_type="CTDI",
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
        assert os.path.normpath(rundir).startswith(
            os.path.normpath(os.path.join(project_root, "runfolder"))
        )

        head_in_tmp: str = os.path.join(project_root, "tmp", "headsourcecode.txt")
        with open(head_in_tmp) as f:
            head_content: str = f.read()
        assert "i:Ts/Seed = 42\n" in head_content
        assert "includeFile = halffan.txt" not in head_content
        assert "includeFile = patientDICOM.txt" not in head_content
        assert "Ts/UseQt" not in head_content
        assert "sv:Ph/Default/LayeredMassGeometryWorlds" in head_content
        assert "dc:Ge/Rotation/RotX= 0 deg\n" in head_content
        assert "d:Ge/patrotation/yaw= 0 deg\n" in head_content
        assert "dc:Ge/Rotation/RotZ= Tf/Rotate/Value + 0.0 deg\n" in head_content

        ctdi_sub: str = os.path.join(project_root, "tmp", "CTDIphantom_16.txt")
        with open(ctdi_sub) as f:
            sub_content: str = f.read()
        assert "d:Ge/couch/HLX = 300 mm\n" in sub_content
        assert "d:Ge/couch/HLY = 1 mm\n" in sub_content
        assert "d:Ge/couch/HLZ = 1500 mm\n" in sub_content
        assert "i:Sc/ChamberPlugCentre_dtm/ZBins=200\n" in sub_content
        assert "i:Sc/ChamberPlugCentre_tle/ZBins=50\n" in sub_content
        assert "i:Sc/ChamberPlugCentre_dtw/ZBins=150\n" in sub_content
        assert "i:Sc/ChamberPlugTop_dtm/ZBins=200\n" in sub_content
        assert "i:Sc/ChamberPlugTop_tle/ZBins=50\n" in sub_content

        for fname in [
            "Muen.dat",
            "ConvertedTopasFile.txt",
            "head_calibration_factor.txt",
            "simulation_metadata.yaml",
            "fullfan.txt",
        ]:
            assert os.path.isfile(os.path.join(rundir, fname)), "Missing: " + fname

        assert not os.path.isfile(os.path.join(rundir, "headsourcecode.txt"))
        assert not os.path.isfile(os.path.join(rundir, "halffan.txt"))
        assert not os.path.isfile(os.path.join(rundir, "patientDICOM.txt"))


class TestICRP145DryRunPipeline:
    def test_full_phantom_pipeline(self, fake_project: Any) -> None:
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
                simulation_type="ICRP145",
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
            ctdi=CtdiConfig(),
            phantom=PhantomConfig(
                phantom_data_directory="/test/phantom_data",
                phantom_sex="AM",
                trans_x="0.0 cm",
                rot_x="90.0 deg",
                couch_enabled=True,
                graphics_enabled=False,
            ),
        )

        with patch(
            "src.orchestrator.SpectrumGenerator.generate", side_effect=_mock_generate
        ):
            rundir: str = Orchestrator(project_root).run(config, dry_run=True)

        assert os.path.isdir(rundir)

        head_in_tmp: str = os.path.join(project_root, "tmp", "headsourcecode.txt")
        with open(head_in_tmp) as f:
            head_content: str = f.read()
        # Voxel path is the default -> head includes phantomVoxel.txt.
        assert "includeFile = phantomVoxel.txt" in head_content
        assert "includeFile = patientDICOM.txt" not in head_content
        assert "sv:Ph/Default/LayeredMassGeometryWorlds" not in head_content

        # The orchestrator must NOT render the (broken) TsTetGeom template when
        # use_voxel_phantom is True: phantomICRP145.txt is absent from tmp/.
        assert not os.path.isfile(
            os.path.join(project_root, "tmp", "phantomICRP145.txt")
        )

        for fname in [
            "headsourcecode.txt",
            "Muen.dat",
            "ConvertedTopasFile.txt",
            "head_calibration_factor.txt",
            "simulation_metadata.yaml",
            "fullfan.txt",
        ]:
            assert os.path.isfile(os.path.join(rundir, fname)), "Missing: " + fname

        assert not os.path.isfile(os.path.join(rundir, "patientDICOM.txt"))
        assert not os.path.isfile(os.path.join(rundir, "HUtoMaterialSchneider.txt"))

    def test_legacy_tetmesh_phantom_pipeline(self, fake_project: Any) -> None:
        """The legacy TsTetGeom path is still selectable via use_voxel_phantom=False."""
        project_root: str = str(fake_project)
        config: SimulationConfig = SimulationConfig(
            general=GeneralConfig(
                topas_directory="/test/topas",
                histories="100",
            ),
            imaging=ImagingConfig(
                simulation_type="ICRP145",
                fan_mode="Full Fan",
                imaging_mode="Pelvis",
                anode_voltage="125 kV",
                exposure="100 mAs",
                start_angle="0 deg",
                rotation_rate="0.4 deg/s",
                timeline_end="501.0 s",
                sequential_times="1000",
                blade_x1="6.175536078965273 cm",
                blade_x2="-6.175536078965273 cm",
                blade_y1="5.814471115800571 cm",
                blade_y2="-5.814471115800571 cm",
            ),
            dicom=DicomConfig(),
            ctdi=CtdiConfig(),
            phantom=PhantomConfig(
                phantom_data_directory="/test/phantom_data",
                phantom_sex="AM",
                use_voxel_phantom=False,
                trans_x="0.0 cm",
                rot_x="90.0 deg",
                couch_enabled=True,
                graphics_enabled=False,
            ),
        )

        with patch(
            "src.orchestrator.SpectrumGenerator.generate", side_effect=_mock_generate
        ):
            Orchestrator(project_root).run(config, dry_run=True)

        head_in_tmp = os.path.join(project_root, "tmp", "headsourcecode.txt")
        with open(head_in_tmp) as f:
            head_content = f.read()
        assert "includeFile = phantomICRP145.txt" in head_content

        sub_in_tmp = os.path.join(project_root, "tmp", "phantomICRP145.txt")
        with open(sub_in_tmp) as f:
            sub_content = f.read()
        assert 'Type="TsTetGeom"' in sub_content
        assert "MRCP_AM.node" in sub_content
