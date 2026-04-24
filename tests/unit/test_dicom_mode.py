import os
import sys
from typing import Any
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.config import (
    CtdiConfig,
    DicomConfig,
    GeneralConfig,
    ImagingConfig,
    SimulationConfig,
)
from src.modes.dicom_mode import DicomMode


MAIN_FILE_CONTENT = (
    's:Ts/G4DataDirectory = "/root/G4Data"\n'
    'i:Tf/NumberOfSequentialTimes = "1000"\n'
    'd:Tf/TimelineEnd = "501.0 s"\n'
    'd:Tf/Rotate/Rate = "0.4 deg/s"\n'
    'd:Tf/Rotate/StartValue = "0 deg"\n'
    'i:Ts/Seed = "9"\n'
    'i:Ts/NumberOfThreads = "1"\n'
    'i:So/beam/NumberOfHistoriesInRun = "100000"\n'
    'dc:Ge/Coll1/TransY = "6.175536078965273 cm"\n'
    'dc:Ge/Coll2/TransY = "-6.175536078965273 cm"\n'
    'dc:Ge/Coll3/TransX = "5.814471115800571 cm"\n'
    'dc:Ge/Coll4/TransX = "-5.814471115800571 cm"\n'
    "includeFile = halffan.txt\n"
    "includeFile = CTDIphantom_16.txt\n"
    "includeFile = CTDIphantom_32.txt\n"
    'sv:Ph/Default/LayeredMassGeometryWorlds = "some value"\n'
    'Ts/UseQt = "true"\n'
    's:Gr/ViewA/Type = "some type"\n'
    'b:Gr/Enable = "true"\n'
    "includeFile = patientDICOM.txt\n"
)

DICOM_SUB_FILE_CONTENT = (
    'd:Ge/patrotation/yaw = "0. deg"\n'
    's:Ge/Patient/DicomDirectory = "/sampledicom/setA"\n'
    'dc:Ge/IsocenterX = "0 mm"\n'
    'dc:Ge/IsocenterY = "0 mm"\n'
    'dc:Ge/IsocenterZ = "0 mm"\n'
    'dc:Ge/Patient/UserTransX = "0. mm"\n'
    'dc:Ge/Patient/UserTransY = "0. mm"\n'
    'dc:Ge/Patient/UserTransZ = "0. mm"\n'
    's:Sc/DoseOnRTGrid100kz17/OutputFile = "output"\n'
)


def _make_dicom_config(**overrides: Any) -> SimulationConfig:
    general_kw = {}
    imaging_kw = {}
    dicom_kw = {}
    ctdi_kw = {}
    for k, v in overrides.items():
        if k in GeneralConfig.__dataclass_fields__:
            general_kw[k] = v
        elif k in ImagingConfig.__dataclass_fields__:
            imaging_kw[k] = v
        elif k in DicomConfig.__dataclass_fields__:
            dicom_kw[k] = v
        elif k in CtdiConfig.__dataclass_fields__:
            ctdi_kw[k] = v
    return SimulationConfig(
        general=GeneralConfig(**general_kw),
        imaging=ImagingConfig(**imaging_kw),
        dicom=DicomConfig(**dicom_kw),
        ctdi=CtdiConfig(**ctdi_kw),
    )


class TestEditMainFile:
    def test_blanks_ctdi_phantom_includes(self) -> None:
        mode = DicomMode()
        config = _make_dicom_config()
        lines = MAIN_FILE_CONTENT.splitlines(True)
        mode.edit_main_file(config, lines)
        for line in lines:
            assert not line.startswith("includeFile = CTDIphantom_16.txt"), (
                "CTDIphantom_16.txt include should be blanked"
            )
            assert not line.startswith("includeFile = CTDIphantom_32.txt"), (
                "CTDIphantom_32.txt include should be blanked"
            )

    def test_blanks_layered_mass_geometry(self) -> None:
        mode = DicomMode()
        config = _make_dicom_config()
        lines = MAIN_FILE_CONTENT.splitlines(True)
        mode.edit_main_file(config, lines)
        for line in lines:
            assert not line.startswith("sv:Ph/Default/LayeredMassGeometryWorlds"), (
                "LayeredMassGeometryWorlds should be blanked"
            )

    def test_blanks_graphics_when_disabled(self) -> None:
        mode = DicomMode()
        config = _make_dicom_config(graphics_enabled=False)
        lines = MAIN_FILE_CONTENT.splitlines(True)
        mode.edit_main_file(config, lines)
        for line in lines:
            assert not line.startswith("Ts/UseQt"), (
                "Ts/UseQt should be blanked when graphics disabled"
            )
            assert not line.startswith("s:Gr/ViewA/Type"), (
                "s:Gr/ViewA/Type should be blanked when graphics disabled"
            )
            assert not line.startswith("b:Gr/Enable"), (
                "b:Gr/Enable should be blanked when graphics disabled"
            )

    def test_keeps_graphics_when_enabled(self) -> None:
        mode = DicomMode()
        config = _make_dicom_config(graphics_enabled=True)
        lines = MAIN_FILE_CONTENT.splitlines(True)
        mode.edit_main_file(config, lines)
        assert any(line.startswith("Ts/UseQt") for line in lines), (
            "Ts/UseQt should remain when graphics enabled"
        )
        assert any(line.startswith("s:Gr/ViewA/Type") for line in lines), (
            "s:Gr/ViewA/Type should remain when graphics enabled"
        )
        assert any(line.startswith("b:Gr/Enable") for line in lines), (
            "b:Gr/Enable should remain when graphics enabled"
        )


class TestEditSubFile:
    def test_replaces_patient_yaw(self) -> None:
        mode = DicomMode()
        config = _make_dicom_config(patient_yaw="90. deg")
        lines = DICOM_SUB_FILE_CONTENT.splitlines(True)
        mode.edit_sub_file(config, lines)
        assert "d:Ge/patrotation/yaw = 90. deg\n" in lines

    def test_replaces_dicom_directory(self) -> None:
        mode = DicomMode()
        config = _make_dicom_config(dicom_directory="/new/dicom/path")
        lines = DICOM_SUB_FILE_CONTENT.splitlines(True)
        mode.edit_sub_file(config, lines)
        assert 's:Ge/Patient/DicomDirectory = "/new/dicom/path"\n' in lines

    def test_replaces_isocenter(self) -> None:
        mode = DicomMode()
        config = _make_dicom_config(
            isocenter_x="10 mm",
            isocenter_y="20 mm",
            isocenter_z="30 mm",
        )
        lines = DICOM_SUB_FILE_CONTENT.splitlines(True)
        mode.edit_sub_file(config, lines)
        assert "dc:Ge/IsocenterX = 10 mm\n" in lines
        assert "dc:Ge/IsocenterY = 20 mm\n" in lines
        assert "dc:Ge/IsocenterZ = 30 mm\n" in lines

    def test_replaces_patient_shifts(self) -> None:
        mode = DicomMode()
        config = _make_dicom_config(
            patient_shift_x="1.5 mm",
            patient_shift_y="2.5 mm",
            patient_shift_z="3.5 mm",
        )
        lines = DICOM_SUB_FILE_CONTENT.splitlines(True)
        mode.edit_sub_file(config, lines)
        assert "dc:Ge/Patient/UserTransX = 1.5 mm\n" in lines
        assert "dc:Ge/Patient/UserTransY = 2.5 mm\n" in lines
        assert "dc:Ge/Patient/UserTransZ = 3.5 mm\n" in lines

    def test_replaces_output_filename(self) -> None:
        mode = DicomMode()
        config = _make_dicom_config(
            patient_id="PAT001",
            rotation_direction="CW",
            imaging_mode="Head",
            start_angle="90 deg",
        )
        lines = DICOM_SUB_FILE_CONTENT.splitlines(True)
        mode.edit_sub_file(config, lines)
        expected = (
            's:Sc/DoseOnRTGrid100kz17/OutputFile = "PAT001_CW_Head_90 deg_DOSE_PTV"\n'
        )
        assert expected in lines


class TestGetSubFileName:
    def test_returns_patient_dicom_txt(self) -> None:
        mode = DicomMode()
        config = _make_dicom_config()
        assert mode.get_sub_file_name(config) == "patientDICOM.txt"


class TestComputeHistories:
    def test_multiplies_sequential_times_by_histories(self) -> None:
        mode = DicomMode()
        config = _make_dicom_config(sequential_times="1000", histories="100000")
        result = mode.compute_histories(config)
        assert result == "100000000"


class TestPrepareRun:
    def test_copies_required_files(self) -> None:
        mode = DicomMode()
        config = _make_dicom_config(fan_mode="Full Fan")
        with patch("src.modes.dicom_mode.shutil.copy") as mock_copy:
            mode.prepare_run(config, "/rundir", "/project")
            assert mock_copy.call_count == 8
            mock_copy.assert_any_call("/project/tmp/headsourcecode.txt", "/rundir")
            mock_copy.assert_any_call(
                "/project/src/boilerplates/TOPAS_includeFiles/HUtoMaterialSchneider.txt",
                "/rundir",
            )
            mock_copy.assert_any_call("/project/tmp/patientDICOM.txt", "/rundir")
            mock_copy.assert_any_call(
                "/project/src/boilerplates/TOPAS_includeFiles/fullfan.txt",
                "/rundir",
            )


class TestExecute:
    def test_calls_simulation_runner(self) -> None:
        mode = DicomMode()
        config = _make_dicom_config(topas_directory="/topas/bin/topas")
        with patch("src.modes.dicom_mode.SimulationRunner.run_dicom") as mock_run:
            mode.execute(config, "/rundir", "/project")
            mock_run.assert_called_once_with("/topas/bin/topas", "/rundir")
