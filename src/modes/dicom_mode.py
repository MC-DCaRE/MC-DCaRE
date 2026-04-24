from __future__ import annotations

import logging
import os
import shutil
from typing import List

from src.config import SimulationConfig
from src.modes.base import SimulationMode
from src.parameter_editor import ParameterEditor
from src.simulation_runner import SimulationRunner

logger = logging.getLogger(__name__)


class DicomMode(SimulationMode):
    def edit_main_file(self, config: SimulationConfig, lines: List[str]) -> None:
        s = ParameterEditor.string_index_replacement
        s("includeFile = CTDIphantom_16.txt", lines)
        s("includeFile = CTDIphantom_32.txt", lines)
        s("sv:Ph/Default/LayeredMassGeometryWorlds", lines)
        if not config.dicom.graphics_enabled:
            s("Ts/UseQt", lines)
            s("s:Gr/ViewA/Type", lines)
            s("b:Gr/Enable", lines)

    def edit_sub_file(self, config: SimulationConfig, lines: List[str]) -> None:
        s = ParameterEditor.string_index_replacement
        s("d:Ge/patrotation/yaw", lines, config.dicom.patient_yaw)
        s(
            "s:Ge/Patient/DicomDirectory",
            lines,
            '"' + config.dicom.dicom_directory + '"',
        )
        s("dc:Ge/IsocenterX", lines, config.dicom.isocenter_x)
        s("dc:Ge/IsocenterY", lines, config.dicom.isocenter_y)
        s("dc:Ge/IsocenterZ", lines, config.dicom.isocenter_z)
        s("dc:Ge/Patient/UserTransX", lines, config.dicom.patient_shift_x)
        s("dc:Ge/Patient/UserTransY", lines, config.dicom.patient_shift_y)
        s("dc:Ge/Patient/UserTransZ", lines, config.dicom.patient_shift_z)
        s(
            "s:Sc/DoseOnRTGrid100kz17/OutputFile",
            lines,
            '"'
            + config.dicom.patient_id
            + "_"
            + config.imaging.rotation_direction
            + "_"
            + config.imaging.imaging_mode
            + "_"
            + config.imaging.start_angle
            + "_DOSE_PTV"
            + '"',
        )

    def get_sub_file_name(self, config: SimulationConfig) -> str:
        return "patientDICOM.txt"

    def compute_histories(self, config: SimulationConfig) -> str:
        return str(int(config.imaging.sequential_times) * int(config.general.histories))

    def prepare_run(
        self,
        config: SimulationConfig,
        rundir: str,
        project_root: str,
    ) -> None:
        include_dir = os.path.join(
            project_root, "src", "boilerplates", "TOPAS_includeFiles"
        )
        shutil.copy(os.path.join(project_root, "tmp", "headsourcecode.txt"), rundir)
        shutil.copy(os.path.join(include_dir, "HUtoMaterialSchneider.txt"), rundir)
        self._copy_common_files(rundir, config, project_root)
        shutil.copy(
            os.path.join(project_root, "tmp", self.get_sub_file_name(config)),
            rundir,
        )
        logger.info("Prepared DICOM run files in %s", rundir)

    @staticmethod
    def _copy_common_files(
        rundatadir: str, config: SimulationConfig, project_root: str
    ) -> None:
        include_dir = os.path.join(
            project_root, "src", "boilerplates", "TOPAS_includeFiles"
        )
        shutil.copy(os.path.join(include_dir, "Muen.dat"), rundatadir)
        shutil.copy(os.path.join(include_dir, "NbParticlesInTime.txt"), rundatadir)
        shutil.copy(
            os.path.join(project_root, "tmp", "ConvertedTopasFile.txt"),
            rundatadir,
        )
        shutil.copy(
            os.path.join(project_root, "tmp", "head_calibration_factor.txt"),
            rundatadir,
        )
        fan_mode = config.imaging.fan_mode
        if fan_mode == "Full Fan":
            shutil.copy(os.path.join(include_dir, "fullfan.txt"), rundatadir)
        elif fan_mode == "Half Fan":
            shutil.copy(os.path.join(include_dir, "halffan.txt"), rundatadir)

    def execute(
        self,
        config: SimulationConfig,
        rundir: str,
        project_root: str,
    ) -> None:
        SimulationRunner.run_dicom(config.general.topas_directory, rundir)
