from __future__ import annotations

import os
import sys
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.template_renderer import TemplateRenderer


_PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
_BOILERPLATES_DIR = os.path.join(_PROJECT_ROOT, "src", "boilerplates")


def _make_renderer(tmp_path: Any) -> TemplateRenderer:
    return TemplateRenderer(_BOILERPLATES_DIR, str(tmp_path / "tmp"))


# Minimal main context with all variables consumed by headsourcecode_boilerplate.j2
_MAIN_CTX = {
    "g4_data_directory": "/G4Data",
    "seed": "9",
    "threads": "1",
    "histories": "100000",
    "sequential_times": "1000",
    "timeline_end": "501.0 s",
    "rotation_rate": "0.4 deg/s",
    "start_angle": "0 deg",
    "coll1_trans_y": "6.0 cm",
    "coll2_trans_y": "-6.0 cm",
    "coll3_trans_x": "5.8 cm",
    "coll4_trans_x": "-5.8 cm",
    "fan_mode": "Full Fan",
    "graphics_enabled": False,
    "phantom_size": "",
    "patient_yaw": "0 deg",
    "patient_pitch": "0 deg",
    "patient_roll_value": 0.0,
    "rotation_direction": "CBCT Clockwise",
    "start_angle_value": 0.0,
    "second_angle_value": 0.0,
}

# Minimal sub context for phantomICRP145.j2
_PHANTOM_SUB_CTX_AM = {
    "phantom_data_directory": "data/P145/Phantom_data",
    "phantom_sex": "AM",
    "trans_x": "0.0 cm",
    "trans_y": "0.0 cm",
    "trans_z": "0.0 cm",
    "rot_x": "90.0 deg",
    "rot_y": "0.0 deg",
    "rot_z": "0.0 deg",
    "couch_enabled": True,
    "couch_width": "260 mm",
    "couch_thickness": "0.4 mm",
    "couch_length": "1000 mm",
    "couch_trans_y": "-14.04 cm",
    "output_filename": "MRCP_AM_test_PHANTOM_DOSE",
}


class TestPhantomIncludeTemplate:
    def test_renders_tetgeom_type(self, tmp_path: Any) -> None:
        renderer = _make_renderer(tmp_path)
        result = renderer.render(
            "phantomICRP145.j2", _PHANTOM_SUB_CTX_AM, "phantom.txt"
        )
        with open(result) as f:
            content = f.read()
        assert 'Type = "TsTetGeom"' in content

    def test_phantom_parented_to_world(self, tmp_path: Any) -> None:
        renderer = _make_renderer(tmp_path)
        result = renderer.render(
            "phantomICRP145.j2", _PHANTOM_SUB_CTX_AM, "phantom.txt"
        )
        with open(result) as f:
            content = f.read()
        # Phantom component must declare Parent = "World"
        assert 'Ge/Phantom/Parent = "World"' in content

    def test_am_sex_selection(self, tmp_path: Any) -> None:
        renderer = _make_renderer(tmp_path)
        result = renderer.render(
            "phantomICRP145.j2", _PHANTOM_SUB_CTX_AM, "phantom.txt"
        )
        with open(result) as f:
            content = f.read()
        assert "MRCP_AM.node" in content
        assert "MRCP_AM.ele" in content
        assert "MRCP_AM.material" in content

    def test_af_sex_selection(self, tmp_path: Any) -> None:
        ctx = dict(_PHANTOM_SUB_CTX_AM, phantom_sex="AF")
        renderer = _make_renderer(tmp_path)
        result = renderer.render("phantomICRP145.j2", ctx, "phantom.txt")
        with open(result) as f:
            content = f.read()
        assert "MRCP_AF.node" in content
        assert "MRCP_AF.ele" in content
        assert "MRCP_AF.material" in content

    def test_tetgeom_scorer_present(self, tmp_path: Any) -> None:
        renderer = _make_renderer(tmp_path)
        result = renderer.render(
            "phantomICRP145.j2", _PHANTOM_SUB_CTX_AM, "phantom.txt"
        )
        with open(result) as f:
            content = f.read()
        assert 'Quantity = "TsTetGeomScorer"' in content
        assert 'Component = "Phantom"' in content

    def test_couch_parent_chain_resolves_to_world(self, tmp_path: Any) -> None:
        renderer = _make_renderer(tmp_path)
        result = renderer.render(
            "phantomICRP145.j2", _PHANTOM_SUB_CTX_AM, "phantom.txt"
        )
        with open(result) as f:
            content = f.read()
        # couchgroup parented to World, couch parented to couchgroup
        assert 'phantomcouchgroup/Parent = "World"' in content
        assert 'phantomcouch/Parent = "phantomcouchgroup"' in content

    def test_couch_configurable_dimensions(self, tmp_path: Any) -> None:
        ctx = dict(
            _PHANTOM_SUB_CTX_AM,
            couch_width="300 mm",
            couch_thickness="0.5 mm",
            couch_length="1200 mm",
        )
        renderer = _make_renderer(tmp_path)
        result = renderer.render("phantomICRP145.j2", ctx, "phantom.txt")
        with open(result) as f:
            content = f.read()
        assert "300 mm" in content
        assert "0.5 mm" in content
        assert "1200 mm" in content


class TestMainTemplatePhantomInclude:
    def test_includes_phantom_for_icrp145(self, tmp_path: Any) -> None:
        ctx = dict(_MAIN_CTX, simulation_type="ICRP145")
        renderer = _make_renderer(tmp_path)
        result = renderer.render("headsourcecode_boilerplate.j2", ctx, "main.txt")
        with open(result) as f:
            content = f.read()
        assert "includeFile = phantomICRP145.txt" in content

    def test_no_phantom_include_for_dicom(self, tmp_path: Any) -> None:
        ctx = dict(_MAIN_CTX, simulation_type="DICOM")
        renderer = _make_renderer(tmp_path)
        result = renderer.render("headsourcecode_boilerplate.j2", ctx, "main.txt")
        with open(result) as f:
            content = f.read()
        assert "phantomICRP145" not in content

    def test_no_phantom_include_for_ctdi(self, tmp_path: Any) -> None:
        ctx = dict(_MAIN_CTX, simulation_type="CTDI")
        renderer = _make_renderer(tmp_path)
        result = renderer.render("headsourcecode_boilerplate.j2", ctx, "main.txt")
        with open(result) as f:
            content = f.read()
        assert "phantomICRP145" not in content
