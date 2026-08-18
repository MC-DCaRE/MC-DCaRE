from __future__ import annotations

import os
import sys
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.template_renderer import TemplateRenderer


class TestRender:
    def test_renders_template_to_file(self, tmp_path: Any) -> None:
        tpl_dir = str(tmp_path / "templates")
        os.makedirs(tpl_dir)
        with open(os.path.join(tpl_dir, "test.j2"), "w") as f:
            f.write("key = {{ value }}\n")
        renderer = TemplateRenderer(tpl_dir, str(tmp_path / "out"))
        result = renderer.render("test.j2", {"value": "hello"}, "output.txt")
        assert os.path.isfile(result)
        with open(result) as f:
            assert f.read() == "key = hello\n"

    def test_creates_output_directory(self, tmp_path: Any) -> None:
        tpl_dir = str(tmp_path / "templates")
        os.makedirs(tpl_dir)
        with open(os.path.join(tpl_dir, "test.j2"), "w") as f:
            f.write("hello")
        out_dir = str(tmp_path / "nested" / "out")
        renderer = TemplateRenderer(tpl_dir, out_dir)
        renderer.render("test.j2", {}, "output.txt")
        assert os.path.isdir(out_dir)

    def test_conditional_rendering(self, tmp_path: Any) -> None:
        tpl_dir = str(tmp_path / "templates")
        os.makedirs(tpl_dir)
        with open(os.path.join(tpl_dir, "test.j2"), "w") as f:
            f.write("{% if enabled %}yes{% endif %}\n")
        renderer = TemplateRenderer(tpl_dir, str(tmp_path / "out"))
        result_true = renderer.render("test.j2", {"enabled": True}, "out1.txt")
        with open(result_true) as f:
            assert "yes" in f.read()
        result_false = renderer.render("test.j2", {"enabled": False}, "out2.txt")
        with open(result_false) as f:
            content = f.read()
            assert "yes" not in content


class TestRenderString:
    def test_renders_string_template(self, tmp_path: Any) -> None:
        tpl_dir = str(tmp_path / "templates")
        os.makedirs(tpl_dir)
        renderer = TemplateRenderer(tpl_dir, str(tmp_path / "out"))
        result = renderer.render_string("val = {{ x }}", {"x": "42"})
        assert result == "val = 42"

    def test_handles_conditional_in_string(self, tmp_path: Any) -> None:
        tpl_dir = str(tmp_path / "templates")
        os.makedirs(tpl_dir)
        renderer = TemplateRenderer(tpl_dir, str(tmp_path / "out"))
        result = renderer.render_string(
            "{% if flag %}on{% else %}off{% endif %}", {"flag": True}
        )
        assert result == "on"


class TestBowtieDispatch:
    """The head template must switch between the legacy CSG bow-tie and the
    TsCAD mesh bow-tie on the ``legacy_bowtie`` flag, per fan mode, and omit
    the bow-tie entirely when ``bowtie_enabled`` is False."""

    def _render_head(self, tmp_path: Any, context: dict) -> str:
        repo_root = os.path.join(os.path.dirname(__file__), "..", "..")
        tpl_dir = os.path.join(repo_root, "src", "boilerplates")
        renderer = TemplateRenderer(tpl_dir, str(tmp_path / "out"))
        # bowtie_enabled defaults on so existing dispatch tests exercise the
        # include; the no-bow-tie test overrides it explicitly.
        merged = {
            "bowtie_enabled": True,
            "bhf_mode": "geometric",
            "primary_mask_enabled": True,
            "source_angular_cutoff_x": "90.0 deg",
            "source_angular_cutoff_y": "90.0 deg",
        }
        merged.update(context)
        result = renderer.render("headsourcecode_boilerplate.j2", merged, "head.txt")
        with open(result) as f:
            return f.read()

    def test_legacy_bowtie_full_fan(self, tmp_path: Any) -> None:
        content = self._render_head(
            tmp_path, {"fan_mode": "Full Fan", "legacy_bowtie": True}
        )
        assert "includeFile = fullfan.txt" in content
        assert "bowtie_ff" not in content

    def test_tscad_bowtie_full_fan(self, tmp_path: Any) -> None:
        content = self._render_head(
            tmp_path, {"fan_mode": "Full Fan", "legacy_bowtie": False}
        )
        assert "includeFile = bowtie_ff.txt" in content

    def test_tscad_bowtie_half_fan(self, tmp_path: Any) -> None:
        content = self._render_head(
            tmp_path, {"fan_mode": "Half Fan", "legacy_bowtie": False}
        )
        assert "includeFile = bowtie_hf.txt" in content

    def test_no_bowtie_omits_include(self, tmp_path: Any) -> None:
        content = self._render_head(
            tmp_path,
            {"fan_mode": "Full Fan", "legacy_bowtie": True, "bowtie_enabled": False},
        )
        assert "fullfan.txt" not in content
        assert "bowtie_ff" not in content
        assert "halffan" not in content

    def test_bhf_thickness_substitutes(self, tmp_path: Any) -> None:
        content = self._render_head(
            tmp_path, {"fan_mode": "Full Fan", "bhf_thickness_mm": 0.89}
        )
        assert "HLZ=0.89 mm" in content or "HLZ = 0.89 mm" in content


class TestPrimaryMaskToggle:
    """The head template must render the primary-collimator mask volumes only
    when ``primary_mask_enabled`` is True (mask-off A/B experiments)."""

    def test_mask_present_by_default(self, tmp_path: Any) -> None:
        renderer, content = _render_head_with_mask(tmp_path, True)
        assert "Ge/PrimaryMaskTop/Type" in content
        assert "Ge/PrimaryMaskRight/TransX" in content

    def test_mask_omitted_when_disabled(self, tmp_path: Any) -> None:
        renderer, content = _render_head_with_mask(tmp_path, False)
        assert "PrimaryMask" not in content


def _render_head_with_mask(tmp_path: Any, enabled: bool, aperture: bool = False) -> Any:
    repo_root = os.path.join(os.path.dirname(__file__), "..", "..")
    tpl_dir = os.path.join(repo_root, "src", "boilerplates")
    renderer = TemplateRenderer(tpl_dir, str(tmp_path / "out"))
    result = renderer.render(
        "headsourcecode_boilerplate.j2",
        {
            "fan_mode": "Full Fan",
            "legacy_bowtie": False,
            "bowtie_enabled": True,
            "bhf_mode": "geometric",
            "housing_aperture_enabled": aperture,
            "primary_mask_enabled": enabled,
            "source_angular_cutoff_x": "15.0 deg",
            "source_angular_cutoff_y": "12.0 deg",
        },
        "head.txt",
    )
    with open(result) as f:
        return renderer, f.read()


class TestHousingApertureToggle:
    """The head template must render the upstream tube-housing aperture only
    when ``housing_aperture_enabled`` is True (Phase 8 production fix)."""

    def test_aperture_present_when_enabled(self, tmp_path: Any) -> None:
        renderer, content = _render_head_with_mask(tmp_path, False, aperture=True)
        assert "Ge/HousingApertureTop/Type" in content
        assert "Ge/HousingApertureRight/TransX" in content

    def test_aperture_omitted_when_disabled(self, tmp_path: Any) -> None:
        renderer, content = _render_head_with_mask(tmp_path, False, aperture=False)
        assert "HousingAperture" not in content


class TestSourceAngularCutoff:
    """The head template must substitute the configurable source cone cutoff
    (housing-equivalent collimation experiments)."""

    def test_default_cutoff_rendered(self, tmp_path: Any) -> None:
        _, content = _render_head_with_mask(tmp_path, True)
        assert "BeamAngularCutoffX = 15.0 deg" in content
        assert "BeamAngularCutoffY = 12.0 deg" in content


class TestBhfGating:
    """The Ti BHF TsBox must be gated on thickness AND bhf_mode='geometric';
    bhf_mode='spekpy' folds the Ti into the spectrum and omits the box."""

    def _render_score(self, tmp_path: Any, **over: object) -> str:
        repo_root = os.path.join(os.path.dirname(__file__), "..", "..")
        renderer = TemplateRenderer(
            os.path.join(repo_root, "src", "boilerplates"), str(tmp_path / "out")
        )
        ctx: dict = {"bhf_thickness_mm": 0.89, "bhf_mode": "geometric"}
        ctx.update(over)
        result = renderer.render("ctdi_phsp_score.j2", ctx, "score.txt")
        with open(result) as f:
            return f.read()

    def test_geometric_mode_renders_bhf(self, tmp_path: Any) -> None:
        content = self._render_score(tmp_path)
        assert "Ge/BeamHardeningFilter/HLZ" in content

    def test_spekpy_mode_omits_bhf(self, tmp_path: Any) -> None:
        content = self._render_score(tmp_path, bhf_mode="spekpy")
        assert "Ge/BeamHardeningFilter/HLZ" not in content

    def test_zero_thickness_omits_bhf(self, tmp_path: Any) -> None:
        content = self._render_score(tmp_path, bhf_thickness_mm=0.0)
        assert "Ge/BeamHardeningFilter/HLZ" not in content


class TestHvlMapGating:
    """validate_bowtie_hvlmap switches the profile scorer between the plain
    80-bin Z profile and the energy-resolved 40x150 wedge map."""

    def _render_score(self, tmp_path: Any, **over: object) -> str:
        repo_root = os.path.join(os.path.dirname(__file__), "..", "..")
        renderer = TemplateRenderer(
            os.path.join(repo_root, "src", "boilerplates"), str(tmp_path / "out")
        )
        ctx: dict = {
            "bhf_thickness_mm": 0.89,
            "bhf_mode": "geometric",
            "validate_bowtie": True,
        }
        ctx.update(over)
        result = renderer.render("ctdi_phsp_score.j2", ctx, "score.txt")
        with open(result) as f:
            return f.read()

    def test_hvlmap_adds_energy_binning(self, tmp_path: Any) -> None:
        content = self._render_score(tmp_path, hvlmap=True)
        assert "Sc/BowtieProfile/EBins" in content
        assert "Sc/BowtieProfile/ZBins        = 40" in content

    def test_default_profile_is_plain_z(self, tmp_path: Any) -> None:
        content = self._render_score(tmp_path, hvlmap=False)
        assert "Sc/BowtieProfile/EBins" not in content
        assert "Sc/BowtieProfile/ZBins        = 80" in content
