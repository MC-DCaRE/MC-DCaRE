import os
import shutil


class BoilerplateManager:
    def __init__(self, project_root: str) -> None:
        self.project_root = project_root
        self.boilerplates_dir = os.path.join(project_root, "src", "boilerplates")
        self.include_files_dir = os.path.join(
            self.boilerplates_dir, "TOPAS_includeFiles"
        )
        self.tmp_dir = os.path.join(project_root, "tmp")

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

    def get_headsource_path(self) -> str:
        return os.path.join(self.tmp_dir, "headsourcecode.txt")

    def get_include_file_path(self, name: str) -> str:
        return os.path.join(self.tmp_dir, name)

    def get_tmp_path(self, filename: str) -> str:
        return os.path.join(self.tmp_dir, filename)
