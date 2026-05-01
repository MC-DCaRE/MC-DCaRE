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
