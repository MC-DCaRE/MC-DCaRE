import logging
import os
import shutil
from datetime import datetime
from typing import List, Tuple

from src.config import SimulationConfig
from src.boilerplate_manager import BoilerplateManager

logger = logging.getLogger(__name__)


class RunPreparer:
    def __init__(self, project_root: str) -> None:
        self.project_root: str = project_root
        self.boilerplate_manager: BoilerplateManager = BoilerplateManager(project_root)

    def _create_runfolder(self) -> str:
        rundatadir: str = os.path.join(
            self.project_root + "/runfolder",
            datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
        )
        os.makedirs(rundatadir)
        logger.info("Created runfolder: %s", rundatadir)
        return rundatadir

    def _copy_common_files(self, rundatadir: str, config: SimulationConfig) -> None:
        path: str = self.project_root
        include_dir: str = os.path.join(
            path, "src", "boilerplates", "TOPAS_includeFiles"
        )

        shutil.copy(os.path.join(include_dir, "Muen.dat"), rundatadir)
        shutil.copy(
            os.path.join(include_dir, "NbParticlesInTime.txt"),
            rundatadir,
        )
        shutil.copy(path + "/tmp/ConvertedTopasFile.txt", rundatadir)
        shutil.copy(path + "/tmp/head_calibration_factor.txt", rundatadir)

        fan_mode: str = config.imaging.fan_mode
        if fan_mode == "Full Fan":
            shutil.copy(os.path.join(include_dir, "fullfan.txt"), rundatadir)
        elif fan_mode == "Half Fan":
            shutil.copy(os.path.join(include_dir, "halffan.txt"), rundatadir)

        logger.info("Copied common files to %s", rundatadir)

    def _generate_plug_files(
        self,
        phantom_size: str,
        rundatadir: str,
        topas_path: str,
    ) -> List[Tuple[str, str]]:
        path: str = self.project_root
        plugs_position: List[str] = [
            "ChamberPlugCentre",
            "ChamberPlugTop",
            "ChamberPlugBottom",
            "ChamberPlugLeft",
            "ChamberPlugRight",
        ]
        commands: List[Tuple[str, str]] = []

        if phantom_size == "16 cm":
            phantom_tag: str = "ctdi16"
        elif phantom_size == "32 cm":
            phantom_tag = "ctdi32"
        else:
            phantom_tag = "ctdi16"

        for position in plugs_position:
            with open(path + "/tmp/headsourcecode.txt", "r") as f:
                content1: str = f.read()

            if phantom_tag == "ctdi16":
                phantom_path: str = path + "/tmp/CTDIphantom_16.txt"
            elif phantom_tag == "ctdi32":
                phantom_path = path + "/tmp/CTDIphantom_32.txt"
            else:
                phantom_path = path + "/tmp/CTDIphantom_16.txt"

            with open(phantom_path, "r") as f:
                content2: str = f.read()

            combined: str = content1 + content2
            combined = combined.replace("@@PLACEHOLDER@@", position)
            combined = combined.replace(
                "s:Ge/" + position + '/Material="PMMA"',
                "s:Ge/" + position + '/Material="Air"',
            )

            position_file: str = rundatadir + "/" + position + ".txt"
            with open(position_file, "w") as f:
                f.write(combined)

            commands.append(
                (
                    topas_path + " " + rundatadir + "/" + position + ".txt",
                    rundatadir,
                )
            )
        logger.info(
            "Generated %d plug files for phantom %s",
            len(commands),
            phantom_size,
        )
        return commands

    def prepare_dicom_run(self, config: SimulationConfig) -> str:
        rundatadir: str = self._create_runfolder()
        path: str = self.project_root
        include_dir: str = os.path.join(
            path, "src", "boilerplates", "TOPAS_includeFiles"
        )

        shutil.copy(path + "/tmp/headsourcecode.txt", rundatadir)
        shutil.copy(
            os.path.join(include_dir, "HUtoMaterialSchneider.txt"),
            rundatadir,
        )
        self._copy_common_files(rundatadir, config)
        shutil.copy(path + "/tmp/patientDICOM.txt", rundatadir)

        logger.info("Prepared DICOM run in %s", rundatadir)
        return rundatadir

    def prepare_ctdi_run(self, config: SimulationConfig) -> str:
        rundatadir: str = self._create_runfolder()
        self._copy_common_files(rundatadir, config)

        logger.info("Prepared CTDI run in %s", rundatadir)
        return rundatadir
