"""CTDI phantom simulation mode."""

from __future__ import annotations

import logging
import os
from typing import Dict

from src.config import SimulationConfig
from src.fieldtobladeopening import fieldtobladeopening
from src.modes.base import SimulationMode
from src.models.quantity import Quantity
from src.simulation_runner import SimulationRunner
from src.template_renderer import TemplateRenderer

logger = logging.getLogger(__name__)

_PLUG_POSITIONS = [
    "ChamberPlugCentre",
    "ChamberPlugTop",
    "ChamberPlugBottom",
    "ChamberPlugLeft",
    "ChamberPlugRight",
]


def _compute_angle_values(
    rotation_direction: str, start_angle: Quantity
) -> Dict[str, object]:
    start_val = start_angle.value
    result: Dict[str, object] = {
        "rotation_direction": rotation_direction,
        "start_angle": str(start_angle),
        "start_angle_value": start_val,
    }
    if rotation_direction == "kV-kV":
        result["second_angle_value"] = start_val + 90.0
    else:
        result["second_angle_value"] = 0.0
    return result


class CtdiMode(SimulationMode):
    """Simulation mode for CTDI phantom dose measurements."""

    @property
    def main_template_name(self) -> str:
        return "headsourcecode_boilerplate.j2"

    @property
    def main_output_name(self) -> str:
        return "headsourcecode.txt"

    def build_main_context(self, config: SimulationConfig) -> Dict[str, object]:
        size_number: str = config.ctdi.phantom_size.split()[0]
        coll1: str = str(config.imaging.blade_x1)
        coll2: str = str(config.imaging.blade_x2)
        coll3: str = str(config.imaging.blade_y1)
        coll4: str = str(config.imaging.blade_y2)
        if config.ctdi.user_blade_enabled:
            blades = fieldtobladeopening(
                [
                    str(config.ctdi.user_field_x1),
                    str(config.ctdi.user_field_x2),
                    str(config.ctdi.user_field_y1),
                    str(config.ctdi.user_field_y2),
                ]
            )
            coll1, coll2, coll3, coll4 = blades
        return {
            "g4_data_directory": config.general.g4_data_directory,
            "seed": config.general.seed,
            "threads": config.general.threads,
            "histories": config.general.histories,
            "sequential_times": config.imaging.sequential_times,
            "timeline_end": str(config.imaging.timeline_end),
            "rotation_rate": str(config.imaging.rotation_rate),
            "start_angle": str(config.imaging.start_angle),
            "coll1_trans_y": coll1,
            "coll2_trans_y": coll2,
            "coll3_trans_x": coll3,
            "coll4_trans_x": coll4,
            "fan_mode": config.imaging.fan_mode,
            "graphics_enabled": config.ctdi.graphics_enabled,
            "simulation_type": "CTDI",
            "phantom_size": size_number,
            "patient_yaw": "0 deg",
            "patient_pitch": "0 deg",
            "patient_roll_value": 0.0,
            **_compute_angle_values(
                config.imaging.rotation_direction, config.imaging.start_angle
            ),
        }

    def build_sub_context(self, config: SimulationConfig) -> Dict[str, object]:
        return {
            "couch_enabled": config.ctdi.couch_enabled,
            "couch_width": str(config.ctdi.couch_width),
            "couch_thickness": str(config.ctdi.couch_thickness),
            "couch_length": str(config.ctdi.couch_length),
            "plug_positions": list(_PLUG_POSITIONS),
            "dose_to_medium_zbins": config.ctdi.dose_to_medium_zbins,
            "tle_zbins": config.ctdi.tle_zbins,
            "dose_to_water_zbins": config.ctdi.dose_to_water_zbins,
            "water_chamber_enabled": config.ctdi.water_chamber_enabled,
        }

    def get_sub_template_name(self, config: SimulationConfig) -> str:
        size_number = config.ctdi.phantom_size.split()[0]
        return "CTDIphantom_{}.j2".format(size_number)

    def get_sub_file_name(self, config: SimulationConfig) -> str:
        size_number = config.ctdi.phantom_size.split()[0]
        return "CTDIphantom_{}.txt".format(size_number)

    def compute_histories(self, config: SimulationConfig) -> str:
        return str(int(config.imaging.sequential_times) * int(config.general.histories))

    def prepare_run(
        self,
        config: SimulationConfig,
        rundir: str,
        project_root: str,
    ) -> None:
        self.copy_common_files(rundir, config, project_root)
        logger.info("Prepared CTDI run files in %s", rundir)

    def execute(
        self,
        config: SimulationConfig,
        rundir: str,
        project_root: str,
        detach: bool = False,
    ) -> None:
        param_file = self._generate_single_parameter_file(config, rundir, project_root)
        SimulationRunner.run_ctdi(
            config.general.topas_directory, rundir, param_file, detach=detach
        )

    def _generate_single_parameter_file(
        self,
        config: SimulationConfig,
        rundatadir: str,
        project_root: str,
    ) -> str:
        """Generate a single TOPAS parameter file scoring all 5 plug positions."""
        renderer = TemplateRenderer(
            os.path.join(project_root, "src", "boilerplates"),
            os.path.join(project_root, "tmp"),
        )
        sub_template = self.get_sub_template_name(config)
        headsource_path = os.path.join(project_root, "tmp", "headsourcecode.txt")
        with open(headsource_path, "r") as f:
            headsource_content = f.read()
        sub_context = self.build_sub_context(config)
        phantom_rendered = renderer.render_string(
            "{% include '" + sub_template + "' %}",
            sub_context,
        )
        combined = headsource_content + phantom_rendered
        output_file = os.path.join(rundatadir, "CTDI_all_positions.txt")
        with open(output_file, "w") as f:
            f.write(combined)
        return output_file
