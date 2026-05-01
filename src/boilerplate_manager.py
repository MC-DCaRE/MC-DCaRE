"""Manages TOPAS boilerplate templates and the tmp working directory."""

from __future__ import annotations

import logging
import os

from src.template_renderer import TemplateRenderer

logger = logging.getLogger(__name__)


class BoilerplateManager:
    """Loads and manages TOPAS Jinja2 templates and the tmp working directory."""

    def __init__(self, project_root: str) -> None:
        self.project_root: str = project_root
        self.boilerplates_dir: str = os.path.join(project_root, "src", "boilerplates")
        self.include_files_dir: str = os.path.join(
            self.boilerplates_dir, "TOPAS_includeFiles"
        )
        self.tmp_dir: str = os.path.join(project_root, "tmp")

    def reset_tmp(self) -> None:
        """Recreate the tmp directory for a fresh simulation run."""
        os.makedirs(self.tmp_dir, exist_ok=True)
        logger.info("Reset tmp directory")

    def create_renderer(self) -> TemplateRenderer:
        """Create a TemplateRenderer configured for this project's boilerplates."""
        return TemplateRenderer(self.boilerplates_dir, self.tmp_dir)

    def get_headsource_path(self) -> str:
        """Return the path to the head source file in tmp."""
        return os.path.join(self.tmp_dir, "headsourcecode.txt")

    def get_include_file_path(self, name: str) -> str:
        """Return the path to a named include file in tmp."""
        return os.path.join(self.tmp_dir, name)

    def get_tmp_path(self, filename: str) -> str:
        """Return the full path for a file within the tmp directory."""
        return os.path.join(self.tmp_dir, filename)
