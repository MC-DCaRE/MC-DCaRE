from __future__ import annotations

import os
import sys
from typing import Any
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.modes.ctdi_mode import CtdiMode


class TestBuildMainContext:
    def test_sets_simulation_type_to_ctdi(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config()
        ctx = mode.build_main_context(config)
        assert ctx["simulation_type"] == "CTDI"

    def test_extracts_phantom_size_number(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(phantom_size="32 cm")
        ctx = mode.build_main_context(config)
        assert ctx["phantom_size"] == "32"

    def test_blade_positions_default_to_config(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config()
        ctx = mode.build_main_context(config)
        assert ctx["coll1_trans_y"] == config.imaging.blade_x1
        assert ctx["coll2_trans_y"] == config.imaging.blade_x2

    def test_blade_positions_overridden_when_user_blade(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(
            user_blade_enabled=True,
            user_field_x1="10 cm",
            user_field_x2="10 cm",
            user_field_y1="10 cm",
            user_field_y2="10 cm",
        )
        with patch(
            "src.modes.ctdi_mode.fieldtobladeopening",
            return_value=["5.0 cm", "-5.0 cm", "4.0 cm", "-4.0 cm"],
        ):
            ctx = mode.build_main_context(config)
        assert ctx["coll1_trans_y"] == "5.0 cm"
        assert ctx["coll3_trans_x"] == "4.0 cm"

    def test_graphics_enabled_in_context(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(graphics_enabled=False)
        ctx = mode.build_main_context(config)
        assert ctx["graphics_enabled"] is False


class TestBuildSubContext:
    def test_couch_enabled_in_context(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(couch_enabled=False)
        ctx = mode.build_sub_context(config, plug_position="ChamberPlugCentre")
        assert ctx["couch_enabled"] is False

    def test_couch_dimensions_in_context(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(
            couch_width="300. mm",
            couch_thickness="0.5 mm",
            couch_length="1500 mm",
        )
        ctx = mode.build_sub_context(config, plug_position="ChamberPlugCentre")
        assert ctx["couch_width"] == "300. mm"
        assert ctx["couch_thickness"] == "0.5 mm"
        assert ctx["couch_length"] == "1500 mm"

    def test_zbins_in_context(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(
            dose_to_medium_zbins="200",
            tle_zbins="150",
            dose_to_water_zbins="250",
        )
        ctx = mode.build_sub_context(config, plug_position="ChamberPlugCentre")
        assert ctx["dose_to_medium_zbins"] == "200"
        assert ctx["tle_zbins"] == "150"
        assert ctx["dose_to_water_zbins"] == "250"

    def test_active_plug_has_air_material(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config()
        ctx = mode.build_sub_context(config, plug_position="ChamberPlugCentre")
        assert ctx["plug_material_centre"] == "Air"
        assert ctx["plug_material_top"] == "PMMA"

    def test_plug_position_in_context(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config()
        ctx = mode.build_sub_context(config, plug_position="ChamberPlugTop")
        assert ctx["plug_position"] == "ChamberPlugTop"
        assert ctx["plug_material_top"] == "Air"
        assert ctx["plug_material_centre"] == "PMMA"


class TestGetSubFileName:
    def test_returns_16_phantom_for_16cm(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(phantom_size="16 cm")
        assert mode.get_sub_file_name(config) == "CTDIphantom_16.txt"

    def test_returns_32_phantom_for_32cm(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(phantom_size="32 cm")
        assert mode.get_sub_file_name(config) == "CTDIphantom_32.txt"


class TestGetSubTemplateName:
    def test_returns_16_template_for_16cm(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(phantom_size="16 cm")
        assert mode.get_sub_template_name(config) == "CTDIphantom_16.j2"

    def test_returns_32_template_for_32cm(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(phantom_size="32 cm")
        assert mode.get_sub_template_name(config) == "CTDIphantom_32.j2"


class TestComputeHistories:
    def test_returns_histories_directly(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(histories="50000")
        result = mode.compute_histories(config)
        assert result == "50000"


class TestExecute:
    def test_generates_plug_files_and_runs(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(topas_directory="/topas/bin/topas")
        fake_commands = [("/topas/bin/topas /rundir/ChamberPlugCentre.txt", "/rundir")]
        with patch.object(
            CtdiMode, "_generate_plug_files", return_value=fake_commands
        ) as mock_gen, patch(
            "src.modes.ctdi_mode.SimulationRunner.run_ctdi"
        ) as mock_run:
            mode.execute(config, "/rundir", "/project")
            mock_gen.assert_called_once_with(config, "/rundir", "/project")
            mock_run.assert_called_once_with(
                "/topas/bin/topas", "/rundir", fake_commands
            )


class TestGeneratePlugFiles:
    def test_generates_five_plug_files(
        self, tmp_path: object, make_config: Any
    ) -> None:
        project_root = str(tmp_path)
        boilerplates_dir = os.path.join(project_root, "src", "boilerplates")
        include_dir = os.path.join(boilerplates_dir, "TOPAS_includeFiles")
        os.makedirs(include_dir)
        os.makedirs(os.path.join(project_root, "tmp"), exist_ok=True)
        with open(os.path.join(boilerplates_dir, "CTDIphantom_16.j2"), "w") as f:
            f.write('Component="{{ plug_position }}"\n')
        with open(
            os.path.join(
                project_root, "src", "boilerplates", "headsourcecode_boilerplate.j2"
            ),
            "w",
        ) as f:
            f.write("head\n")
        with open(os.path.join(project_root, "tmp", "headsourcecode.txt"), "w") as f:
            f.write("head\n")
        rundatadir = str(tmp_path / "rundata")
        os.makedirs(rundatadir)
        config = make_config(phantom_size="16 cm")
        mode = CtdiMode()
        commands = mode._generate_plug_files(config, rundatadir, project_root)
        assert len(commands) == 5
        with open(os.path.join(rundatadir, "ChamberPlugCentre.txt")) as f:
            content = f.read()
        assert "head" in content
        assert "ChamberPlugCentre" in content
