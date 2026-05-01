from __future__ import annotations

import os
import sys
from typing import Any
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.modes.dicom_mode import DicomMode


class TestBuildMainContext:
    def test_sets_simulation_type_to_dicom(self, make_config: Any) -> None:
        mode = DicomMode()
        config = make_config()
        ctx = mode.build_main_context(config)
        assert ctx["simulation_type"] == "DICOM"

    def test_graphics_disabled(self, make_config: Any) -> None:
        mode = DicomMode()
        config = make_config(graphics_enabled=False)
        ctx = mode.build_main_context(config)
        assert ctx["graphics_enabled"] is False

    def test_graphics_enabled(self, make_config: Any) -> None:
        mode = DicomMode()
        config = make_config(graphics_enabled=True)
        ctx = mode.build_main_context(config)
        assert ctx["graphics_enabled"] is True


class TestBuildSubContext:
    def test_replaces_patient_yaw(self, make_config: Any) -> None:
        mode = DicomMode()
        config = make_config(patient_yaw="90. deg")
        ctx = mode.build_sub_context(config)
        assert ctx["patient_yaw"] == "90. deg"

    def test_replaces_dicom_directory(self, make_config: Any) -> None:
        mode = DicomMode()
        config = make_config(dicom_directory="/new/dicom/path")
        ctx = mode.build_sub_context(config)
        assert ctx["dicom_directory"] == "/new/dicom/path"

    def test_replaces_isocenter(self, make_config: Any) -> None:
        mode = DicomMode()
        config = make_config(
            isocenter_x="10 mm",
            isocenter_y="20 mm",
            isocenter_z="30 mm",
        )
        ctx = mode.build_sub_context(config)
        assert ctx["isocenter_x"] == "10 mm"
        assert ctx["isocenter_y"] == "20 mm"
        assert ctx["isocenter_z"] == "30 mm"

    def test_replaces_patient_shifts(self, make_config: Any) -> None:
        mode = DicomMode()
        config = make_config(
            patient_shift_x="1.5 mm",
            patient_shift_y="2.5 mm",
            patient_shift_z="3.5 mm",
        )
        ctx = mode.build_sub_context(config)
        assert ctx["patient_shift_x"] == "1.5 mm"
        assert ctx["patient_shift_y"] == "2.5 mm"
        assert ctx["patient_shift_z"] == "3.5 mm"

    def test_builds_output_filename(self, make_config: Any) -> None:
        mode = DicomMode()
        config = make_config(
            patient_id="PAT001",
            rotation_direction="CW",
            imaging_mode="Head",
            start_angle="90 deg",
        )
        ctx = mode.build_sub_context(config)
        assert ctx["output_filename"] == "PAT001_CW_Head_90 deg_DOSE_PTV"


class TestGetSubFileName:
    def test_returns_patient_dicom_txt(self, make_config: Any) -> None:
        mode = DicomMode()
        config = make_config()
        assert mode.get_sub_file_name(config) == "patientDICOM.txt"


class TestComputeHistories:
    def test_multiplies_sequential_time_by_histories(self, make_config: Any) -> None:
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
