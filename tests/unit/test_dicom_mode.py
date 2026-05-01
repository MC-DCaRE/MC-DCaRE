from __future__ import annotations

import os
import sys
from typing import Any
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.modes.dicom_mode import DicomMode
from tests.unit.shared import DICOM_SUB_FILE_CONTENT, MAIN_FILE_CONTENT


class TestEditMainFile:
    def test_blanks_ctdi_phantom_includes(self, make_config: Any) -> None:
        mode = DicomMode()
        config = make_config()
        lines = MAIN_FILE_CONTENT.splitlines(True)
        mode.edit_main_file(config, lines)
        for line in lines:
            assert not line.startswith(
                "includeFile = CTDIphantom_16.txt"
            ), "CTDIphantom_16.txt include should be blanked"
            assert not line.startswith(
                "includeFile = CTDIphantom_32.txt"
            ), "CTDIphantom_32.txt include should be blanked"

    def test_blanks_layered_mass_geometry(self, make_config: Any) -> None:
        mode = DicomMode()
        config = make_config()
        lines = MAIN_FILE_CONTENT.splitlines(True)
        mode.edit_main_file(config, lines)
        for line in lines:
            assert not line.startswith(
                "sv:Ph/Default/LayeredMassGeometryWorlds"
            ), "LayeredMassGeometryWorlds should be blanked"

    def test_blanks_graphics_when_disabled(self, make_config: Any) -> None:
        mode = DicomMode()
        config = make_config(graphics_enabled=False)
        lines = MAIN_FILE_CONTENT.splitlines(True)
        mode.edit_main_file(config, lines)
        for line in lines:
            assert not line.startswith(
                "Ts/UseQt"
            ), "Ts/UseQt should be blanked when graphics disabled"
            assert not line.startswith(
                "s:Gr/ViewA/Type"
            ), "s:Gr/ViewA/Type should be blanked when graphics disabled"
            assert not line.startswith(
                "b:Gr/Enable"
            ), "b:Gr/Enable should be blanked when graphics disabled"

    def test_keeps_graphics_when_enabled(self, make_config: Any) -> None:
        mode = DicomMode()
        config = make_config(graphics_enabled=True)
        lines = MAIN_FILE_CONTENT.splitlines(True)
        mode.edit_main_file(config, lines)
        assert any(
            line.startswith("Ts/UseQt") for line in lines
        ), "Ts/UseQt should remain when graphics enabled"
        assert any(
            line.startswith("s:Gr/ViewA/Type") for line in lines
        ), "s:Gr/ViewA/Type should remain when graphics enabled"
        assert any(
            line.startswith("b:Gr/Enable") for line in lines
        ), "b:Gr/Enable should remain when graphics enabled"


class TestEditSubFile:
    def test_replaces_patient_yaw(self, make_config: Any) -> None:
        mode = DicomMode()
        config = make_config(patient_yaw="90. deg")
        lines = DICOM_SUB_FILE_CONTENT.splitlines(True)
        mode.edit_sub_file(config, lines)
        assert "d:Ge/patrotation/yaw = 90. deg\n" in lines

    def test_replaces_dicom_directory(self, make_config: Any) -> None:
        mode = DicomMode()
        config = make_config(dicom_directory="/new/dicom/path")
        lines = DICOM_SUB_FILE_CONTENT.splitlines(True)
        mode.edit_sub_file(config, lines)
        assert 's:Ge/Patient/DicomDirectory = "/new/dicom/path"\n' in lines

    def test_replaces_isocenter(self, make_config: Any) -> None:
        mode = DicomMode()
        config = make_config(
            isocenter_x="10 mm",
            isocenter_y="20 mm",
            isocenter_z="30 mm",
        )
        lines = DICOM_SUB_FILE_CONTENT.splitlines(True)
        mode.edit_sub_file(config, lines)
        assert "dc:Ge/IsocenterX = 10 mm\n" in lines
        assert "dc:Ge/IsocenterY = 20 mm\n" in lines
        assert "dc:Ge/IsocenterZ = 30 mm\n" in lines

    def test_replaces_patient_shifts(self, make_config: Any) -> None:
        mode = DicomMode()
        config = make_config(
            patient_shift_x="1.5 mm",
            patient_shift_y="2.5 mm",
            patient_shift_z="3.5 mm",
        )
        lines = DICOM_SUB_FILE_CONTENT.splitlines(True)
        mode.edit_sub_file(config, lines)
        assert "dc:Ge/Patient/UserTransX = 1.5 mm\n" in lines
        assert "dc:Ge/Patient/UserTransY = 2.5 mm\n" in lines
        assert "dc:Ge/Patient/UserTransZ = 3.5 mm\n" in lines

    def test_replaces_output_filename(self, make_config: Any) -> None:
        mode = DicomMode()
        config = make_config(
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
    def test_returns_patient_dicom_txt(self, make_config: Any) -> None:
        mode = DicomMode()
        config = make_config()
        assert mode.get_sub_file_name(config) == "patientDICOM.txt"


class TestComputeHistories:
    def test_multiplies_sequential_times_by_histories(self, make_config: Any) -> None:
        mode = DicomMode()
        config = make_config(sequential_times="1000", histories="100000")
        result = mode.compute_histories(config)
        assert result == "100000000"


class TestPrepareRun:
    def test_copies_required_files(self, make_config: Any) -> None:
        mode = DicomMode()
        config = make_config(fan_mode="Full Fan")
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
    def test_calls_simulation_runner(self, make_config: Any) -> None:
        mode = DicomMode()
        config = make_config(topas_directory="/topas/bin/topas")
        with patch("src.modes.dicom_mode.SimulationRunner.run_dicom") as mock_run:
            mode.execute(config, "/rundir", "/project")
            mock_run.assert_called_once_with("/topas/bin/topas", "/rundir")
