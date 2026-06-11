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
            assert f'Ge/{position}_water/Material="Water"' in rendered, (
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
            assert f'Ge/{position}_water/Material="Water"' in rendered, (
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
