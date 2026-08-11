"""Tests for parallel worlds template rendering."""

from __future__ import annotations

import os
import sys
from typing import Any

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.template_renderer import TemplateRenderer

_PLUG_POSITIONS = [
    "ChamberPlugCentre",
    "ChamberPlugTop",
    "ChamberPlugBottom",
    "ChamberPlugLeft",
    "ChamberPlugRight",
]

_DEFAULT_CONTEXT: dict[str, object] = {
    "couch_enabled": False,
    "couch_width": "300. mm",
    "couch_thickness": "0.5 mm",
    "couch_length": "1500 mm",
    "plug_positions": _PLUG_POSITIONS,
    "dose_to_medium_zbins": "200",
    "tle_zbins": "150",
    "dose_to_water_zbins": "250",
}


@pytest.fixture
def boilerplates_dir(tmp_path: Any) -> str:
    """Set up a temporary boilerplates directory with the real templates."""
    src_boilerplates = os.path.join(
        os.path.dirname(__file__), "..", "..", "src", "boilerplates"
    )
    include_src = os.path.join(src_boilerplates, "TOPAS_includeFiles")
    include_dst = os.path.join(str(tmp_path), "TOPAS_includeFiles")
    os.makedirs(include_dst, exist_ok=True)

    # Copy the real template files
    for name in ["CTDIphantom_16.j2", "CTDIphantom_32.j2"]:
        src = os.path.join(include_src, name)
        dst = os.path.join(include_dst, name)
        with open(src, "r") as f:
            content = f.read()
        with open(dst, "w") as f:
            f.write(content)

    return str(tmp_path)


def _render_template(boilerplates_dir: str, template_name: str, context: dict) -> str:
    """Render a template and return the output string."""
    tmp_dir = os.path.join(os.path.dirname(boilerplates_dir), "tmp_out")
    os.makedirs(tmp_dir, exist_ok=True)
    renderer = TemplateRenderer(boilerplates_dir, tmp_dir)
    return renderer.render_string(
        "{% include 'TOPAS_includeFiles/" + template_name + "' %}",
        context,
    )


class TestCTDIPhantom16ParallelWorlds:
    def test_all_plugs_have_air_material(self, boilerplates_dir: str) -> None:
        rendered = _render_template(
            boilerplates_dir, "CTDIphantom_16.j2", _DEFAULT_CONTEXT
        )
        for position in _PLUG_POSITIONS:
            assert f'Ge/{position}/Material="Air"' in rendered, (
                f"{position} should have Air material"
            )

    def test_no_plug_has_pmma_material(self, boilerplates_dir: str) -> None:
        rendered = _render_template(
            boilerplates_dir, "CTDIphantom_16.j2", _DEFAULT_CONTEXT
        )
        for position in _PLUG_POSITIONS:
            assert f'Ge/{position}/Material="PMMA"' not in rendered, (
                f"{position} should NOT have PMMA material"
            )

    def test_all_plugs_have_parallel_world_name(self, boilerplates_dir: str) -> None:
        rendered = _render_template(
            boilerplates_dir, "CTDIphantom_16.j2", _DEFAULT_CONTEXT
        )
        for position in _PLUG_POSITIONS:
            assert f'Ge/{position}/ParallelWorldName="{position}"' in rendered, (
                f"{position} should have ParallelWorldName set"
            )

    def test_fifteen_scorers_defined(self, boilerplates_dir: str) -> None:
        rendered = _render_template(
            boilerplates_dir, "CTDIphantom_16.j2", _DEFAULT_CONTEXT
        )
        scorer_types = ["_tle", "_dtm", "_dtw"]
        for position in _PLUG_POSITIONS:
            for scorer_type in scorer_types:
                scorer_name = f"{position}{scorer_type}"
                assert f"Sc/{scorer_name}/Quantity" in rendered, (
                    f"Scorer {scorer_name} should be defined"
                )

    def test_output_file_names_match_convention(self, boilerplates_dir: str) -> None:
        rendered = _render_template(
            boilerplates_dir, "CTDIphantom_16.j2", _DEFAULT_CONTEXT
        )
        for position in _PLUG_POSITIONS:
            assert f'OutputFile="{position}_tle"' in rendered, (
                f"Missing OutputFile for {position}_tle"
            )
            assert f'OutputFile="{position}_dtm"' in rendered, (
                f"Missing OutputFile for {position}_dtm"
            )
            assert f'OutputFile="{position}_dtw"' in rendered, (
                f"Missing OutputFile for {position}_dtw"
            )

    def test_scorers_have_report_with_four_metrics(self, boilerplates_dir: str) -> None:
        rendered = _render_template(
            boilerplates_dir, "CTDIphantom_16.j2", _DEFAULT_CONTEXT
        )
        scorer_types = ["_tle", "_dtm", "_dtw"]
        expected_report = (
            'Report = 4 "Sum" "Histories" "Count_In_Bin" "Standard_Deviation"'
        )
        for position in _PLUG_POSITIONS:
            for scorer_type in scorer_types:
                scorer_name = f"{position}{scorer_type}"
                assert f"Sc/{scorer_name}/{expected_report}" in rendered, (
                    f"Scorer {scorer_name} should have Report with Sum, Histories, Count_In_Bin, Standard_Deviation"
                )

    def test_phantom_radius_is_80mm(self, boilerplates_dir: str) -> None:
        rendered = _render_template(
            boilerplates_dir, "CTDIphantom_16.j2", _DEFAULT_CONTEXT
        )
        assert "Ge/CTDI/RMax=80.0 mm" in rendered

    def test_peripheral_plug_offsets_correct(self, boilerplates_dir: str) -> None:
        rendered = _render_template(
            boilerplates_dir, "CTDIphantom_16.j2", _DEFAULT_CONTEXT
        )
        assert "Ge/ChamberPlugTop/TransY=-70.0 mm" in rendered
        assert "Ge/ChamberPlugBottom/TransY=70.0 mm" in rendered
        assert "Ge/ChamberPlugLeft/TransX=-70.0 mm" in rendered
        assert "Ge/ChamberPlugRight/TransX=70.0 mm" in rendered


class TestCTDIPhantom32ParallelWorlds:
    def test_all_plugs_have_air_material(self, boilerplates_dir: str) -> None:
        rendered = _render_template(
            boilerplates_dir, "CTDIphantom_32.j2", _DEFAULT_CONTEXT
        )
        for position in _PLUG_POSITIONS:
            assert f'Ge/{position}/Material="Air"' in rendered, (
                f"{position} should have Air material"
            )

    def test_no_plug_has_pmma_material(self, boilerplates_dir: str) -> None:
        rendered = _render_template(
            boilerplates_dir, "CTDIphantom_32.j2", _DEFAULT_CONTEXT
        )
        for position in _PLUG_POSITIONS:
            assert f'Ge/{position}/Material="PMMA"' not in rendered, (
                f"{position} should NOT have PMMA material"
            )

    def test_all_plugs_have_parallel_world_name(self, boilerplates_dir: str) -> None:
        rendered = _render_template(
            boilerplates_dir, "CTDIphantom_32.j2", _DEFAULT_CONTEXT
        )
        for position in _PLUG_POSITIONS:
            assert f'Ge/{position}/ParallelWorldName="{position}"' in rendered, (
                f"{position} should have ParallelWorldName set"
            )

    def test_fifteen_scorers_defined(self, boilerplates_dir: str) -> None:
        rendered = _render_template(
            boilerplates_dir, "CTDIphantom_32.j2", _DEFAULT_CONTEXT
        )
        scorer_types = ["_tle", "_dtm", "_dtw"]
        for position in _PLUG_POSITIONS:
            for scorer_type in scorer_types:
                scorer_name = f"{position}{scorer_type}"
                assert f"Sc/{scorer_name}/Quantity" in rendered, (
                    f"Scorer {scorer_name} should be defined"
                )

    def test_output_file_names_match_convention(self, boilerplates_dir: str) -> None:
        rendered = _render_template(
            boilerplates_dir, "CTDIphantom_32.j2", _DEFAULT_CONTEXT
        )
        for position in _PLUG_POSITIONS:
            assert f'OutputFile="{position}_tle"' in rendered, (
                f"Missing OutputFile for {position}_tle"
            )
            assert f'OutputFile="{position}_dtm"' in rendered, (
                f"Missing OutputFile for {position}_dtm"
            )
            assert f'OutputFile="{position}_dtw"' in rendered, (
                f"Missing OutputFile for {position}_dtw"
            )

    def test_scorers_have_report_with_four_metrics(self, boilerplates_dir: str) -> None:
        rendered = _render_template(
            boilerplates_dir, "CTDIphantom_32.j2", _DEFAULT_CONTEXT
        )
        scorer_types = ["_tle", "_dtm", "_dtw"]
        expected_report = (
            'Report = 4 "Sum" "Histories" "Count_In_Bin" "Standard_Deviation"'
        )
        for position in _PLUG_POSITIONS:
            for scorer_type in scorer_types:
                scorer_name = f"{position}{scorer_type}"
                assert f"Sc/{scorer_name}/{expected_report}" in rendered, (
                    f"Scorer {scorer_name} should have Report with Sum, Histories, Count_In_Bin, Standard_Deviation"
                )

    def test_phantom_radius_is_160mm(self, boilerplates_dir: str) -> None:
        rendered = _render_template(
            boilerplates_dir, "CTDIphantom_32.j2", _DEFAULT_CONTEXT
        )
        assert "Ge/CTDI/RMax=160.0 mm" in rendered

    def test_peripheral_plug_offsets_correct(self, boilerplates_dir: str) -> None:
        rendered = _render_template(
            boilerplates_dir, "CTDIphantom_32.j2", _DEFAULT_CONTEXT
        )
        assert "Ge/ChamberPlugTop/TransY=-150.0 mm" in rendered
        assert "Ge/ChamberPlugBottom/TransY=150.0 mm" in rendered
        assert "Ge/ChamberPlugLeft/TransX=-150.0 mm" in rendered
        assert "Ge/ChamberPlugRight/TransX=150.0 mm" in rendered


class TestWaterChamberEnabled:
    """Tests for water_chamber_enabled=true template rendering."""

    def _water_context(self) -> dict[str, object]:
        ctx = dict(_DEFAULT_CONTEXT)
        ctx["water_chamber_enabled"] = True
        return ctx

    # --- 16cm phantom ---

    def test_16cm_water_volumes_present(self, boilerplates_dir: str) -> None:
        rendered = _render_template(
            boilerplates_dir, "CTDIphantom_16.j2", self._water_context()
        )
        for position in _PLUG_POSITIONS:
            assert f'Ge/{position}_water/Material="G4_WATER"' in rendered, (
                f"{position}_water should have Water material"
            )

    def test_16cm_water_scorers_present(self, boilerplates_dir: str) -> None:
        rendered = _render_template(
            boilerplates_dir, "CTDIphantom_16.j2", self._water_context()
        )
        for position in _PLUG_POSITIONS:
            assert f"Sc/{position}_water_dtm/Quantity" in rendered, (
                f"Scorer {position}_water_dtm should be defined"
            )

    def test_16cm_water_output_files(self, boilerplates_dir: str) -> None:
        rendered = _render_template(
            boilerplates_dir, "CTDIphantom_16.j2", self._water_context()
        )
        for position in _PLUG_POSITIONS:
            assert f'OutputFile="{position}_water_dtm"' in rendered, (
                f"Missing OutputFile for {position}_water_dtm"
            )

    def test_16cm_water_plug_offsets_70mm(self, boilerplates_dir: str) -> None:
        rendered = _render_template(
            boilerplates_dir, "CTDIphantom_16.j2", self._water_context()
        )
        assert "Ge/ChamberPlugTop_water/TransY=-70.0 mm" in rendered
        assert "Ge/ChamberPlugBottom_water/TransY=70.0 mm" in rendered
        assert "Ge/ChamberPlugLeft_water/TransX=-70.0 mm" in rendered
        assert "Ge/ChamberPlugRight_water/TransX=70.0 mm" in rendered

    # --- 32cm phantom ---

    def test_32cm_water_volumes_present(self, boilerplates_dir: str) -> None:
        rendered = _render_template(
            boilerplates_dir, "CTDIphantom_32.j2", self._water_context()
        )
        for position in _PLUG_POSITIONS:
            assert f'Ge/{position}_water/Material="G4_WATER"' in rendered, (
                f"{position}_water should have Water material"
            )

    def test_32cm_water_scorers_present(self, boilerplates_dir: str) -> None:
        rendered = _render_template(
            boilerplates_dir, "CTDIphantom_32.j2", self._water_context()
        )
        for position in _PLUG_POSITIONS:
            assert f"Sc/{position}_water_dtm/Quantity" in rendered, (
                f"Scorer {position}_water_dtm should be defined"
            )

    def test_32cm_water_plug_offsets_150mm(self, boilerplates_dir: str) -> None:
        rendered = _render_template(
            boilerplates_dir, "CTDIphantom_32.j2", self._water_context()
        )
        assert "Ge/ChamberPlugTop_water/TransY=-150.0 mm" in rendered
        assert "Ge/ChamberPlugBottom_water/TransY=150.0 mm" in rendered
        assert "Ge/ChamberPlugLeft_water/TransX=-150.0 mm" in rendered
        assert "Ge/ChamberPlugRight_water/TransX=150.0 mm" in rendered

    # --- disabled (default) ---

    def test_no_water_when_disabled(self, boilerplates_dir: str) -> None:
        ctx = dict(_DEFAULT_CONTEXT)
        ctx["water_chamber_enabled"] = False
        rendered = _render_template(boilerplates_dir, "CTDIphantom_16.j2", ctx)
        assert "ChamberPlugCentre_water" not in rendered
        assert "_water_dtm" not in rendered


# Minimal main-template context (variables consumed by
# headsourcecode_boilerplate.j2 / ctdi_phsp_replay.j2).
_MAIN_CTX_BASE: dict[str, object] = {
    "g4_data_directory": "/G4Data",
    "seed": "9",
    "threads": "1",
    "histories": "100000",
    "sequential_times": "10",
    "timeline_end": "1 s",
    "rotation_rate": "360 deg/s",
    "start_angle": "0 deg",
    "coll1_trans_y": "6.0 cm",
    "coll2_trans_y": "-6.0 cm",
    "coll3_trans_x": "5.8 cm",
    "coll4_trans_x": "-5.8 cm",
    "fan_mode": "Full Fan",
    "graphics_enabled": False,
    "phantom_size": "32",
    "patient_yaw": "0 deg",
    "patient_pitch": "0 deg",
    "patient_roll_value": 0.0,
    "rotation_direction": "CBCT Clockwise",
    "start_angle_value": 0.0,
    "second_angle_value": 0.0,
}


def _lmg_line(rendered: str) -> str:
    """Extract the LayeredMassGeometryWorlds line from a rendered template."""
    for line in rendered.splitlines():
        if "LayeredMassGeometryWorlds" in line:
            return line.strip()
    raise AssertionError("No LayeredMassGeometryWorlds line in rendered output")


class TestLayeredMassGeometryWorldsRegistration:
    """Water parallel worlds have material (G4_WATER), so TOPAS requires them
    in LayeredMassGeometryWorlds -- otherwise the run segfaults with
    "Parallel world X has material, but this world not specified". This
    guards the conditional LMG list in the main templates."""

    def test_off_mode_lists_5_air_worlds_when_water_disabled(
        self, tmp_path: Any
    ) -> None:
        renderer = TemplateRenderer(_boilerplates_dir(), str(tmp_path / "tmp"))
        ctx = dict(_MAIN_CTX_BASE, simulation_type="CTDI", water_chamber_enabled=False)
        rendered = renderer.render_string(
            "{% include 'headsourcecode_boilerplate.j2' %}", ctx
        )
        line = _lmg_line(rendered)
        assert line.startswith("sv:Ph/Default/LayeredMassGeometryWorlds = 5 ")
        for pos in _PLUG_POSITIONS:
            assert f'"{pos}"' in line
        assert "_water" not in line

    def test_off_mode_lists_10_worlds_when_water_enabled(self, tmp_path: Any) -> None:
        renderer = TemplateRenderer(_boilerplates_dir(), str(tmp_path / "tmp"))
        ctx = dict(_MAIN_CTX_BASE, simulation_type="CTDI", water_chamber_enabled=True)
        rendered = renderer.render_string(
            "{% include 'headsourcecode_boilerplate.j2' %}", ctx
        )
        line = _lmg_line(rendered)
        assert line.startswith("sv:Ph/Default/LayeredMassGeometryWorlds = 10 ")
        # Air worlds first, water worlds last (water takes precedence -- TOPAS
        # resolves overlap by list order, last wins).
        for pos in _PLUG_POSITIONS:
            assert f'"{pos}"' in line
            assert f'"{pos}_water"' in line
        # Water worlds listed after air worlds (precedence: last wins).
        air_idx = line.index('"ChamberPlugCentre"')
        water_idx = line.index('"ChamberPlugCentre_water"')
        assert water_idx > air_idx

    def test_replay_mode_lists_10_worlds_when_water_enabled(
        self, tmp_path: Any
    ) -> None:
        renderer = TemplateRenderer(_boilerplates_dir(), str(tmp_path / "tmp"))
        ctx = dict(
            _MAIN_CTX_BASE,
            phase_space_file="beam_exit_phsp",
            phase_space_multiple_use="5",
            water_chamber_enabled=True,
        )
        rendered = renderer.render_string("{% include 'ctdi_phsp_replay.j2' %}", ctx)
        line = _lmg_line(rendered)
        assert line.startswith("sv:Ph/Default/LayeredMassGeometryWorlds = 10 ")
        assert '"ChamberPlugCentre_water"' in line

    def test_replay_mode_lists_5_worlds_when_water_disabled(
        self, tmp_path: Any
    ) -> None:
        renderer = TemplateRenderer(_boilerplates_dir(), str(tmp_path / "tmp"))
        ctx = dict(
            _MAIN_CTX_BASE,
            phase_space_file="beam_exit_phsp",
            phase_space_multiple_use="5",
            water_chamber_enabled=False,
        )
        rendered = renderer.render_string("{% include 'ctdi_phsp_replay.j2' %}", ctx)
        line = _lmg_line(rendered)
        assert line.startswith("sv:Ph/Default/LayeredMassGeometryWorlds = 5 ")
        assert "_water" not in line


def _boilerplates_dir() -> str:
    return os.path.join(os.path.dirname(__file__), "..", "..", "src", "boilerplates")
