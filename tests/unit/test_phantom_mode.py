from __future__ import annotations

import os
import sys
from typing import Any
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.modes.phantom_mode import PhantomMode


class TestBuildMainContext:
    def test_sets_simulation_type_to_icrp145(self, make_config: Any) -> None:
        mode = PhantomMode()
        config = make_config(simulation_type="ICRP145")
        ctx = mode.build_main_context(config)
        assert ctx["simulation_type"] == "ICRP145"

    def test_graphics_disabled(self, make_config: Any) -> None:
        mode = PhantomMode()
        config = make_config()
        ctx = mode.build_main_context(config)
        assert ctx["graphics_enabled"] is False

    def test_graphics_enabled(self) -> None:
        from src.config import PhantomConfig, SimulationConfig

        mode = PhantomMode()
        config = SimulationConfig(phantom=PhantomConfig(graphics_enabled=True))
        ctx = mode.build_main_context(config)
        assert ctx["graphics_enabled"] is True

    def test_rotation_direction_in_context(self, make_config: Any) -> None:
        mode = PhantomMode()
        config = make_config(rotation_direction="CBCT Clockwise")
        ctx = mode.build_main_context(config)
        assert ctx["rotation_direction"] == "CBCT Clockwise"

    def test_kvk_angle_values_in_context(self, make_config: Any) -> None:
        mode = PhantomMode()
        config = make_config(rotation_direction="kV-kV", start_angle="0 deg")
        ctx = mode.build_main_context(config)
        assert ctx["rotation_direction"] == "kV-kV"
        assert ctx["start_angle_value"] == 0.0
        assert ctx["second_angle_value"] == 90.0

    def test_phantom_size_is_empty(self, make_config: Any) -> None:
        mode = PhantomMode()
        config = make_config()
        ctx = mode.build_main_context(config)
        assert ctx["phantom_size"] == ""


class TestBuildSubContext:
    def test_phantom_directory(self, make_config: Any) -> None:
        mode = PhantomMode()
        config = make_config(phantom_data_directory="/data/P145/Phantom_data")
        ctx = mode.build_sub_context(config)
        assert ctx["phantom_directory"].endswith("/data/P145/Phantom_data/MRCP_AM")

    def test_phantom_name_defaults_to_mrcp_sex(self, make_config: Any) -> None:
        mode = PhantomMode()
        config = make_config(phantom_sex="AM")
        ctx = mode.build_sub_context(config)
        assert ctx["phantom_name"] == "MRCP_AM"

    def test_phantom_name_override(self, make_config: Any) -> None:
        mode = PhantomMode()
        config = make_config(phantom_name="Omed")
        ctx = mode.build_sub_context(config)
        assert ctx["phantom_name"] == "Omed"

    def test_trans_offsets(self, make_config: Any) -> None:
        mode = PhantomMode()
        config = make_config(
            trans_x="1.0 cm",
            trans_y="2.0 cm",
            trans_z="3.0 cm",
        )
        ctx = mode.build_sub_context(config)
        assert ctx["trans_x"] == "1 cm"
        assert ctx["trans_y"] == "2 cm"
        assert ctx["trans_z"] == "3 cm"

    def test_rot_offsets(self, make_config: Any) -> None:
        mode = PhantomMode()
        config = make_config(
            rot_x="90.0 deg",
            rot_y="5.0 deg",
            rot_z="10.0 deg",
        )
        ctx = mode.build_sub_context(config)
        assert ctx["rot_x"] == "90 deg"
        assert ctx["rot_y"] == "5 deg"
        assert ctx["rot_z"] == "10 deg"

    def test_couch_params(self, make_config: Any) -> None:
        mode = PhantomMode()
        config = make_config(
            couch_enabled=True,
            couch_width="260 mm",
            couch_thickness="0.4 mm",
            couch_length="1000 mm",
        )
        ctx = mode.build_sub_context(config)
        assert ctx["couch_enabled"] is True
        assert ctx["couch_width"] == "260 mm"
        assert ctx["couch_thickness"] == "0.4 mm"
        assert ctx["couch_length"] == "1000 mm"

    def test_builds_output_filename(self, make_config: Any) -> None:
        mode = PhantomMode()
        config = make_config(
            phantom_name="MRCP_AM",
            rotation_direction="CW",
            imaging_mode="Head",
            start_angle="90 deg",
        )
        ctx = mode.build_sub_context(config)
        assert ctx["output_filename"] == "MRCP_AM_CW_Head_90 deg_PHANTOM_DOSE"

    def test_icrp_materials_empty_when_no_organs(self, make_config: Any) -> None:
        mode = PhantomMode()
        config = make_config()
        ctx = mode.build_sub_context(config)
        assert ctx["icrp_materials"] == ""

    def test_icrp_materials_single_organ(self, make_config: Any) -> None:
        mode = PhantomMode()
        config = make_config(organ_scoring_ids="Liver")
        ctx = mode.build_sub_context(config)
        assert ctx["icrp_materials"] == '1 "Liver"'

    def test_icrp_materials_multiple_organs(self, make_config: Any) -> None:
        mode = PhantomMode()
        config = make_config(organ_scoring_ids="Liver, Brain, Thyroid")
        ctx = mode.build_sub_context(config)
        assert ctx["icrp_materials"] == '3 "Liver" "Brain" "Thyroid"'

    def test_icrp_materials_strips_whitespace(self, make_config: Any) -> None:
        mode = PhantomMode()
        config = make_config(organ_scoring_ids=" Liver , Brain ")
        ctx = mode.build_sub_context(config)
        assert ctx["icrp_materials"] == '2 "Liver" "Brain"'


class TestGetSubFileName:
    def test_returns_phantom_icrp145_txt(self, make_config: Any) -> None:
        mode = PhantomMode()
        config = make_config()
        assert mode.get_sub_file_name(config) == "phantomICRP145.txt"


class TestGetSubTemplateName:
    def test_returns_phantom_icrp145_j2(self, make_config: Any) -> None:
        mode = PhantomMode()
        config = make_config()
        assert mode.get_sub_template_name(config) == "phantomICRP145.j2"


class TestComputeHistories:
    def test_multiplies_sequential_time_by_histories(self, make_config: Any) -> None:
        mode = PhantomMode()
        config = make_config(sequential_times="1000", histories="100000")
        result = mode.compute_histories(config)
        assert result == "100000000"


class TestPrepareRun:
    def test_copies_required_files(self, make_config: Any) -> None:
        mode = PhantomMode()
        config = make_config(fan_mode="Full Fan")
        with patch("src.modes.phantom_mode.shutil.copy") as mock_copy:
            mode.prepare_run(config, "/rundir", "/project")
            assert mock_copy.call_count == 7
            mock_copy.assert_any_call("/project/tmp/headsourcecode.txt", "/rundir")
            mock_copy.assert_any_call("/project/tmp/phantomICRP145.txt", "/rundir")
            mock_copy.assert_any_call(
                "/project/src/boilerplates/TOPAS_includeFiles/fullfan.txt",
                "/rundir",
            )

    def test_does_not_copy_dicom_artifacts(self, make_config: Any) -> None:
        mode = PhantomMode()
        config = make_config()
        with patch("src.modes.phantom_mode.shutil.copy") as mock_copy:
            mode.prepare_run(config, "/rundir", "/project")
            for call in mock_copy.call_args_list:
                assert "HUtoMaterialSchneider" not in str(call)


class TestExecute:
    def test_calls_simulation_runner(self, make_config: Any) -> None:
        mode = PhantomMode()
        config = make_config(topas_directory="/topas/bin/topas")
        with patch("src.modes.phantom_mode.SimulationRunner.run_phantom") as mock_run:
            mode.execute(config, "/rundir", "/project")
            mock_run.assert_called_once_with(
                "/topas/bin/topas", "/rundir", detach=False
            )
