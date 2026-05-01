"""Manages TOPAS boilerplate template files and the tmp working directory."""

from __future__ import annotations

import logging
import os
import shutil

logger = logging.getLogger(__name__)


class BoilerplateManager:
    """Loads and resets TOPAS boilerplate templates into the tmp working directory."""

    def __init__(self, project_root: str) -> None:
        self.project_root: str = project_root
        self.boilerplates_dir: str = os.path.join(project_root, "src", "boilerplates")
        self.include_files_dir: str = os.path.join(
            self.boilerplates_dir, "TOPAS_includeFiles"
        )
        self.tmp_dir: str = os.path.join(project_root, "tmp")

    def reset_tmp(self) -> None:
        """Recreate the tmp directory with fresh copies of all boilerplate templates."""
        os.makedirs(self.tmp_dir, exist_ok=True)

        src = os.path.join(self.boilerplates_dir, "headsourcecode_boilerplate.txt")
        dst = os.path.join(self.tmp_dir, "headsourcecode.txt")
        shutil.copy(src, dst)

        src = os.path.join(self.include_files_dir, "patientDICOM.txt")
        dst = os.path.join(self.tmp_dir, "patientDICOM.txt")
        shutil.copy(src, dst)

        src = os.path.join(self.include_files_dir, "CTDIphantom_16.txt")
        dst = os.path.join(self.tmp_dir, "CTDIphantom_16.txt")
        shutil.copy(src, dst)

        src = os.path.join(self.include_files_dir, "CTDIphantom_32.txt")
        dst = os.path.join(self.tmp_dir, "CTDIphantom_32.txt")
        shutil.copy(src, dst)

        logger.info("Reset tmp directory from boilerplates")

    def get_headsource_path(self) -> str:
        """Return the path to the head source boilerplate in tmp."""
        return os.path.join(self.tmp_dir, "headsourcecode.txt")

    def get_include_file_path(self, name: str) -> str:
        """Return the path to a named include file in tmp."""
        return os.path.join(self.tmp_dir, name)

    def get_tmp_path(self, filename: str) -> str:
        """Return the full path for a file within the tmp directory."""
        return os.path.join(self.tmp_dir, filename)
