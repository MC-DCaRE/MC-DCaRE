"""ICRP 145 reference phantom simulation mode."""

from __future__ import annotations

import logging
import os
import shutil
from typing import Dict

from src.config import SimulationConfig
from src.modes.base import SimulationMode
from src.simulation_runner import SimulationRunner

logger = logging.getLogger(__name__)


class PhantomMode(SimulationMode):
    """Simulation mode for ICRP 145 tetrahedral-mesh reference phantom dose calculations."""

    @property
    def main_template_name(self) -> str:
        return "headsourcecode_boilerplate.j2"

    @property
    def main_output_name(self) -> str:
        return "headsourcecode.txt"

    def build_main_context(self, config: SimulationConfig) -> Dict[str, object]:
        start_val = config.imaging.start_angle.value
        second_angle = (
            start_val + 90.0 if config.imaging.rotation_direction == "kV-kV" else 0.0
        )
        return {
            "g4_data_directory": config.general.g4_data_directory,
            "seed": config.general.seed,
            "threads": config.general.threads,
            "histories": config.general.histories,
            "sequential_times": config.imaging.sequential_times,
            "timeline_end": str(config.imaging.timeline_end),
            "rotation_rate": str(config.imaging.rotation_rate),
            "start_angle": str(config.imaging.start_angle),
            "coll1_trans_y": str(config.imaging.blade_x1),
            "coll2_trans_y": str(config.imaging.blade_x2),
            "coll3_trans_x": str(config.imaging.blade_y1),
            "coll4_trans_x": str(config.imaging.blade_y2),
            "fan_mode": config.imaging.fan_mode,
            "graphics_enabled": config.phantom.graphics_enabled,
            "simulation_type": "ICRP145",
            "phantom_size": "",
            "patient_yaw": str(config.dicom.patient_yaw),
            "patient_pitch": str(config.dicom.patient_pitch),
            "patient_roll_value": config.dicom.patient_roll.value,
            "rotation_direction": config.imaging.rotation_direction,
            "start_angle_value": start_val,
            "second_angle_value": second_angle,
        }

    def build_sub_context(self, config: SimulationConfig) -> Dict[str, object]:
        output_filename = "{}_{}_{}_{}_PHANTOM_DOSE".format(
            "MRCP_{}".format(config.phantom.phantom_sex),
            config.imaging.rotation_direction,
            config.imaging.imaging_mode,
            str(config.imaging.start_angle),
        )
        # Couch top Y position: phantom posterior minus a small gap
        # The phantom native Y range is approximately ±14 cm; after rotation
        # the posterior surface sits near the negative-Y side. The couch top
        # is placed just below it (TransY = posterior - couch half-thickness).
        trans_y_val = config.phantom.trans_y.value
        couch_thickness_val = config.phantom.couch_thickness.value
        couch_trans_y = "{} cm".format(trans_y_val - 14.0 - couch_thickness_val / 10.0)
        return {
            "phantom_data_directory": config.phantom.phantom_data_directory,
            "phantom_sex": config.phantom.phantom_sex,
            "trans_x": str(config.phantom.trans_x),
            "trans_y": str(config.phantom.trans_y),
            "trans_z": str(config.phantom.trans_z),
            "rot_x": str(config.phantom.rot_x),
            "rot_y": str(config.phantom.rot_y),
            "rot_z": str(config.phantom.rot_z),
            "couch_enabled": config.phantom.couch_enabled,
            "couch_width": str(config.phantom.couch_width),
            "couch_thickness": str(config.phantom.couch_thickness),
            "couch_length": str(config.phantom.couch_length),
            "couch_trans_y": couch_trans_y,
            "output_filename": output_filename,
        }

    def get_sub_file_name(self, config: SimulationConfig) -> str:
        return "phantomICRP145.txt"

    def get_sub_template_name(self, config: SimulationConfig) -> str:
        return "phantomICRP145.j2"

    def compute_histories(self, config: SimulationConfig) -> str:
        return str(int(config.imaging.sequential_times) * int(config.general.histories))

    def prepare_run(
        self,
        config: SimulationConfig,
        rundir: str,
        project_root: str,
    ) -> None:
        shutil.copy(os.path.join(project_root, "tmp", "headsourcecode.txt"), rundir)
        self.copy_common_files(rundir, config, project_root)
        shutil.copy(
            os.path.join(project_root, "tmp", self.get_sub_file_name(config)),
            rundir,
        )
        logger.info("Prepared ICRP 145 phantom run files in %s", rundir)

    def execute(
        self,
        config: SimulationConfig,
        rundir: str,
        project_root: str,
        detach: bool = False,
    ) -> None:
        SimulationRunner.run_phantom(
            config.general.topas_directory, rundir, detach=detach
        )
