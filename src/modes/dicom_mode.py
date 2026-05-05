"""DICOM patient simulation mode."""

from __future__ import annotations

import logging
import os
import shutil
from typing import Dict

from src.config import SimulationConfig
from src.modes.base import SimulationMode
from src.simulation_runner import SimulationRunner

logger = logging.getLogger(__name__)


class DicomMode(SimulationMode):
    """Simulation mode for patient DICOM dose calculations."""

    @property
    def main_template_name(self) -> str:
        return "headsourcecode_boilerplate.j2"

    @property
    def main_output_name(self) -> str:
        return "headsourcecode.txt"

    def build_main_context(self, config: SimulationConfig) -> Dict[str, object]:
        return {
            "g4_data_directory": config.general.g4_data_directory,
            "seed": config.general.seed,
            "threads": config.general.threads,
            "histories": config.general.histories,
            "sequential_times": config.imaging.sequential_times,
            "timeline_end": config.imaging.timeline_end,
            "rotation_rate": config.imaging.rotation_rate,
            "start_angle": config.imaging.start_angle,
            "coll1_trans_y": config.imaging.blade_x1,
            "coll2_trans_y": config.imaging.blade_x2,
            "coll3_trans_x": config.imaging.blade_y1,
            "coll4_trans_x": config.imaging.blade_y2,
            "fan_mode": config.imaging.fan_mode,
            "graphics_enabled": config.dicom.graphics_enabled,
            "simulation_type": "DICOM",
            "phantom_size": "",
        }

    def build_sub_context(
        self, config: SimulationConfig
    ) -> Dict[str, object]:
        output_filename = "{}_{}_{}_{}_DOSE_PTV".format(
            config.dicom.patient_id,
            config.imaging.rotation_direction,
            config.imaging.imaging_mode,
            config.imaging.start_angle,
        )
        return {
            "patient_yaw": config.dicom.patient_yaw,
            "dicom_directory": config.dicom.dicom_directory,
            "isocenter_x": config.dicom.isocenter_x,
            "isocenter_y": config.dicom.isocenter_y,
            "isocenter_z": config.dicom.isocenter_z,
            "patient_shift_x": config.dicom.patient_shift_x,
            "patient_shift_y": config.dicom.patient_shift_y,
            "patient_shift_z": config.dicom.patient_shift_z,
            "output_filename": output_filename,
        }

    def get_sub_file_name(self, config: SimulationConfig) -> str:
        return "patientDICOM.txt"

    def get_sub_template_name(self, config: SimulationConfig) -> str:
        return "patientDICOM.j2"

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
        self.copy_common_files(rundir, config, project_root)
        shutil.copy(
            os.path.join(project_root, "tmp", self.get_sub_file_name(config)),
            rundir,
        )
        logger.info("Prepared DICOM run files in %s", rundir)

    def execute(
        self,
        config: SimulationConfig,
        rundir: str,
        project_root: str,
    ) -> None:
        SimulationRunner.run_dicom(config.general.topas_directory, rundir)
