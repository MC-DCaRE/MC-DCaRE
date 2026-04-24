import logging
import os
import shutil

logger = logging.getLogger(__name__)


class BoilerplateManager:
    def __init__(self, project_root: str) -> None:
        self.project_root: str = project_root
        self.boilerplates_dir: str = os.path.join(project_root, "src", "boilerplates")
        self.include_files_dir: str = os.path.join(
            self.boilerplates_dir, "TOPAS_includeFiles"
        )
        self.tmp_dir: str = os.path.join(project_root, "tmp")

    def reset_tmp(self) -> None:
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
        return os.path.join(self.tmp_dir, "headsourcecode.txt")

    def get_include_file_path(self, name: str) -> str:
        return os.path.join(self.tmp_dir, name)

    def get_tmp_path(self, filename: str) -> str:
        return os.path.join(self.tmp_dir, filename)
