from __future__ import annotations

import os
import sys
from typing import Any
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.modes.ctdi_mode import CtdiMode
from src.models.quantity import Quantity


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
        # Coll1/Coll2 shape world Z (slice axis) -> blade_y;
        # Coll3/Coll4 shape world X (fan axis) -> blade_x.
        assert ctx["coll1_trans_y"] == str(config.imaging.blade_y1)
        assert ctx["coll2_trans_y"] == str(config.imaging.blade_y2)
        # fan pair is negated (mirror: wide half-fan edge on world -X)
        assert ctx["coll3_trans_x"] == str(
            Quantity(-config.imaging.blade_x2.value, config.imaging.blade_x2.unit)
        )
        assert ctx["coll4_trans_x"] == str(
            Quantity(-config.imaging.blade_x1.value, config.imaging.blade_x1.unit)
        )

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
        # blades = [x1, x2, y1, y2]; y pair -> Coll1/Coll2 (world Z),
        # negated+mirrored x pair -> Coll3/Coll4 (world X, wide side on -X)
        assert ctx["coll1_trans_y"] == "4.0 cm"
        assert ctx["coll3_trans_x"] == "5 cm"
        assert ctx["coll4_trans_x"] == "-5 cm"

    def test_graphics_enabled_in_context(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(graphics_enabled=False)
        ctx = mode.build_main_context(config)
        assert ctx["graphics_enabled"] is False

    def test_water_chamber_disabled_by_default_in_main_context(
        self, make_config: Any
    ) -> None:
        mode = CtdiMode()
        config = make_config()
        ctx = mode.build_main_context(config)
        assert ctx["water_chamber_enabled"] is False

    def test_water_chamber_enabled_in_main_context(self, make_config: Any) -> None:
        # Must reach the main context so headsourcecode_boilerplate.j2 can add
        # the water parallel worlds to LayeredMassGeometryWorlds (parallel
        # worlds with material segfault TOPAS if not listed in LMG).
        mode = CtdiMode()
        config = make_config(water_chamber_enabled=True)
        ctx = mode.build_main_context(config)
        assert ctx["water_chamber_enabled"] is True

    def test_water_chamber_enabled_in_replay_main_context(
        self, make_config: Any
    ) -> None:
        mode = CtdiMode()
        config = make_config(
            phase_space_mode="replay",
            phase_space_file="/tmp/beam_exit_phsp.phsp",
            water_chamber_enabled=True,
        )
        ctx = mode.build_main_context(config)
        assert ctx["water_chamber_enabled"] is True

    def test_rotation_direction_in_context(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(rotation_direction="CBCT Clockwise")
        ctx = mode.build_main_context(config)
        assert ctx["rotation_direction"] == "CBCT Clockwise"
        assert ctx["start_angle_value"] == 0.0

    def test_kvk_angle_values_in_context(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(rotation_direction="kV-kV", start_angle="0 deg")
        ctx = mode.build_main_context(config)
        assert ctx["rotation_direction"] == "kV-kV"
        assert ctx["start_angle_value"] == 0.0
        assert ctx["second_angle_value"] == 90.0

    def test_kvk_angle_values_with_offset(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(rotation_direction="kV-kV", start_angle="45 deg")
        ctx = mode.build_main_context(config)
        assert ctx["start_angle_value"] == 45.0
        assert ctx["second_angle_value"] == 135.0


class TestBuildSubContext:
    def test_couch_enabled_in_context(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(couch_enabled=False)
        ctx = mode.build_sub_context(config)
        assert ctx["couch_enabled"] is False

    def test_couch_dimensions_in_context(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(
            couch_width="300. mm",
            couch_thickness="0.5 mm",
            couch_length="1500 mm",
        )
        ctx = mode.build_sub_context(config)
        assert ctx["couch_width"] == "300 mm"
        assert ctx["couch_thickness"] == "0.5 mm"
        assert ctx["couch_length"] == "1500 mm"

    def test_zbins_in_context(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(
            dose_to_medium_zbins="200",
            tle_zbins="150",
            dose_to_water_zbins="250",
        )
        ctx = mode.build_sub_context(config)
        assert ctx["dose_to_medium_zbins"] == "200"
        assert ctx["tle_zbins"] == "150"
        assert ctx["dose_to_water_zbins"] == "250"

    def test_plug_positions_list_in_context(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config()
        ctx = mode.build_sub_context(config)
        assert ctx["plug_positions"] == [
            "ChamberPlugCentre",
            "ChamberPlugTop",
            "ChamberPlugBottom",
            "ChamberPlugLeft",
            "ChamberPlugRight",
        ]

    def test_water_chamber_disabled_by_default(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config()
        ctx = mode.build_sub_context(config)
        assert ctx["water_chamber_enabled"] is False

    def test_water_chamber_enabled_in_context(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(water_chamber_enabled=True)
        ctx = mode.build_sub_context(config)
        assert ctx["water_chamber_enabled"] is True


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
        config = make_config(histories="50000", sequential_times="1000")
        result = mode.compute_histories(config)
        assert result == "50000000"

    def test_multiplies_sequential_times_by_histories(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(histories="2000", sequential_times="500")
        result = mode.compute_histories(config)
        assert result == "1000000"


class TestExecute:
    def test_generates_single_file_and_runs(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(topas_directory="/topas/bin/topas")
        with patch.object(
            CtdiMode,
            "_generate_single_parameter_file",
            return_value="/rundir/CTDI_all_positions.txt",
        ) as mock_gen, patch(
            "src.modes.ctdi_mode.SimulationRunner.run_ctdi"
        ) as mock_run:
            mode.execute(config, "/rundir", "/project")
            mock_gen.assert_called_once_with(config, "/rundir", "/project")
            mock_run.assert_called_once_with(
                "/topas/bin/topas",
                "/rundir",
                "/rundir/CTDI_all_positions.txt",
                detach=False,
            )


class TestGenerateSingleParameterFile:
    def test_generates_single_file_with_all_positions(
        self, tmp_path: object, make_config: Any
    ) -> None:
        project_root = str(tmp_path)
        boilerplates_dir = os.path.join(project_root, "src", "boilerplates")
        include_dir = os.path.join(boilerplates_dir, "TOPAS_includeFiles")
        os.makedirs(include_dir)
        os.makedirs(os.path.join(project_root, "tmp"), exist_ok=True)
        with open(os.path.join(boilerplates_dir, "CTDIphantom_16.j2"), "w") as f:
            f.write("{% for position in plug_positions %}{{ position }}\n{% endfor %}")
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
        result = mode._generate_single_parameter_file(config, rundatadir, project_root)
        assert result == os.path.join(rundatadir, "CTDI_all_positions.txt")
        with open(result) as f:
            content = f.read()
        assert "head" in content
        assert "ChamberPlugCentre" in content
        assert "ChamberPlugTop" in content
        assert "ChamberPlugBottom" in content
        assert "ChamberPlugLeft" in content
        assert "ChamberPlugRight" in content


class TestPhaseSpaceModeBranching:
    """Tests for phase_space_mode branching in CtdiMode."""

    def test_score_mode_selects_score_template(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(phase_space_mode="score")
        assert mode._get_main_template(config) == "ctdi_phsp_score.j2"

    def test_replay_mode_selects_replay_template(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(phase_space_mode="replay", phase_space_file="/fake.phsp")
        assert mode._get_main_template(config) == "ctdi_phsp_replay.j2"

    def test_off_mode_selects_default_template(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(phase_space_mode="off")
        assert mode._get_main_template(config) == "headsourcecode_boilerplate.j2"

    def test_score_mode_output_name(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(phase_space_mode="score")
        assert mode._get_main_output(config) == "ctdi_phsp_score.txt"

    def test_replay_mode_output_name(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(phase_space_mode="replay", phase_space_file="/fake.phsp")
        assert mode._get_main_output(config) == "ctdi_phsp_replay.txt"

    def test_score_mode_no_sub_template(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(phase_space_mode="score")
        assert mode.get_sub_template_name(config) == ""
        assert mode.get_sub_file_name(config) == ""

    def test_score_mode_empty_sub_context(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(phase_space_mode="score")
        ctx = mode.build_sub_context(config)
        assert ctx == {}

    def test_replay_mode_sub_context_has_phantom(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(phase_space_mode="replay", phase_space_file="/fake.phsp")
        ctx = mode.build_sub_context(config)
        assert "plug_positions" in ctx
        assert "couch_enabled" in ctx

    def test_replay_main_context_has_phase_space_params(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(
            phase_space_mode="replay",
            phase_space_file="/fake.phsp",
            phase_space_multiple_use=10,
        )
        ctx = mode.build_main_context(config)
        assert ctx["phase_space_file"] == "fake"
        assert ctx["phase_space_multiple_use"] == 10

    def test_replay_strips_only_last_extension(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(
            phase_space_mode="replay",
            phase_space_file="/path/to/run.beam.phsp",
        )
        ctx = mode.build_main_context(config)
        assert ctx["phase_space_file"] == "run.beam"

    def test_replay_no_extension_passes_through(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(
            phase_space_mode="replay",
            phase_space_file="/path/to/beamfile",
        )
        ctx = mode.build_main_context(config)
        assert ctx["phase_space_file"] == "beamfile"

    def test_replay_main_context_no_collimators(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(phase_space_mode="replay", phase_space_file="/fake.phsp")
        ctx = mode.build_main_context(config)
        assert "coll1_trans_y" not in ctx
        assert "fan_mode" not in ctx

    def test_score_mode_main_context_has_collimators(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(phase_space_mode="score")
        ctx = mode.build_main_context(config)
        assert "coll1_trans_y" in ctx
        assert "fan_mode" in ctx

    def test_score_mode_context_carries_bowtie_flags(self, make_config: Any) -> None:
        """validate_bowtie and bowtie_enabled reach the score template context."""
        mode = CtdiMode()
        config = make_config(phase_space_mode="score", validate_bowtie=True)
        ctx = mode.build_main_context(config)
        assert ctx["validate_bowtie"] is True
        assert ctx["bowtie_enabled"] is True

    def test_score_mode_context_bowtie_disabled(self, make_config: Any) -> None:
        """bowtie_enabled=False propagates (no-bow-tie baseline runs)."""
        mode = CtdiMode()
        config = make_config(phase_space_mode="score", bowtie_enabled=False)
        ctx = mode.build_main_context(config)
        assert ctx["bowtie_enabled"] is False
        assert ctx["validate_bowtie"] is False

    def test_score_mode_context_carries_primary_mask_flag(
        self, make_config: Any
    ) -> None:
        """primary_mask_enabled=True propagates (deprecated mask A/B)."""
        mode = CtdiMode()
        config = make_config(phase_space_mode="score", primary_mask_enabled=True)
        ctx = mode.build_main_context(config)
        assert ctx["primary_mask_enabled"] is True

    def test_score_mode_context_primary_mask_disabled(self, make_config: Any) -> None:
        """primary_mask_enabled=False is the deprecated-off default."""
        mode = CtdiMode()
        config = make_config(phase_space_mode="score", primary_mask_enabled=False)
        ctx = mode.build_main_context(config)
        assert ctx["primary_mask_enabled"] is False

    def test_score_mode_context_carries_housing_aperture_flag(
        self, make_config: Any
    ) -> None:
        """housing_aperture_enabled reaches the score template context."""
        mode = CtdiMode()
        config = make_config(phase_space_mode="score")
        ctx = mode.build_main_context(config)
        assert ctx["housing_aperture_enabled"] is True

    def test_score_mode_context_housing_aperture_disabled(
        self, make_config: Any
    ) -> None:
        """housing_aperture_enabled=False propagates (A/B experiments)."""
        mode = CtdiMode()
        config = make_config(phase_space_mode="score", housing_aperture_enabled=False)
        ctx = mode.build_main_context(config)
        assert ctx["housing_aperture_enabled"] is False

    def test_replay_compute_histories_returns_zero(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(phase_space_mode="replay", phase_space_file="/fake.phsp")
        assert mode.compute_histories(config) == "0"

    def test_score_prepare_run_creates_phase_space_dir(
        self, tmp_path: Any, make_config: Any
    ) -> None:
        mode = CtdiMode()
        config = make_config(phase_space_mode="score")
        rundir = str(tmp_path / "run")
        os.makedirs(rundir)
        # Create required files for copy_common_files.
        src_tmp = tmp_path / "project" / "tmp"
        src_tmp.mkdir(parents=True)
        (src_tmp / "ConvertedTopasFile.txt").write_text("spec")
        (src_tmp / "head_calibration_factor.txt").write_text("1.0")
        (src_tmp / "simulation_metadata.yaml").write_text("norm_factor: 1.0\n")
        include_dir = (
            tmp_path / "project" / "src" / "boilerplates" / "TOPAS_includeFiles"
        )
        include_dir.mkdir(parents=True)
        (include_dir / "Muen.dat").write_text("muen")
        # TsCAD is the default bow-tie: stage both legacy and STL assets so
        # copy_common_files succeeds regardless of legacy_bowtie.
        (include_dir / "fullfan.txt").write_text("bowtie")
        (include_dir / "bowtie_ff.txt").write_text("tscad")
        (include_dir / "fullfan.stl").write_text("stl")
        mode.prepare_run(config, rundir, str(tmp_path / "project"))
        assert os.path.isdir(os.path.join(rundir, "phase_space"))

    def test_replay_prepare_run_copies_phsp_file(
        self, tmp_path: Any, make_config: Any
    ) -> None:
        mode = CtdiMode()
        phsp = tmp_path / "beam.phsp"
        phsp.write_bytes(b"\x00" * 100)
        config = make_config(phase_space_mode="replay", phase_space_file=str(phsp))
        rundir = str(tmp_path / "run")
        os.makedirs(rundir)
        include_dir = (
            tmp_path / "project" / "src" / "boilerplates" / "TOPAS_includeFiles"
        )
        include_dir.mkdir(parents=True)
        (include_dir / "Muen.dat").write_text("muen")
        mode.prepare_run(config, rundir, str(tmp_path / "project"))
        assert os.path.isfile(os.path.join(rundir, "beam.phsp"))
        assert os.path.isfile(os.path.join(rundir, "Muen.dat"))
