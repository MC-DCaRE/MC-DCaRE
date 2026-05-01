"""Jinja2-based rendering of TOPAS parameter file templates."""

from __future__ import annotations

import logging
import os
from typing import Dict

from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)


class TemplateRenderer:
    """Renders Jinja2 templates to produce TOPAS parameter files."""

    def __init__(self, boilerplates_dir: str, tmp_dir: str) -> None:
        self._tmp_dir: str = tmp_dir
        include_dir: str = os.path.join(boilerplates_dir, "TOPAS_includeFiles")
        search_paths: list = [boilerplates_dir]
        if os.path.isdir(include_dir):
            search_paths.append(include_dir)
        self._env: Environment = Environment(
            loader=FileSystemLoader(search_paths),
            keep_trailing_newline=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render(
        self, template_name: str, context: Dict[str, object], output_name: str
    ) -> str:
        """Render a Jinja2 template and write the result to ``tmp_dir/output_name``.

        Args:
            template_name: Filename of the ``.j2`` template in the boilerplates directory.
            context: Dictionary of template variables.
            output_name: Filename for the rendered output in ``tmp_dir``.

        Returns:
            The output file path.
        """
        template = self._env.get_template(template_name)
        rendered: str = template.render(**context)
        output_path: str = os.path.join(self._tmp_dir, output_name)
        os.makedirs(self._tmp_dir, exist_ok=True)
        with open(output_path, "w") as f:
            f.write(rendered)
        logger.info("Rendered %s -> %s", template_name, output_path)
        return output_path

    def render_string(self, template_string: str, context: Dict[str, object]) -> str:
        """Render a Jinja2 template from a raw string.

        Args:
            template_string: Jinja2 template content.
            context: Dictionary of template variables.

        Returns:
            The rendered string.
        """
        template = self._env.from_string(template_string)
        return template.render(**context)
