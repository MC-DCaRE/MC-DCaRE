"""ICRP 145 reference phantom simulation mode."""

from __future__ import annotations

import logging
import os
import shutil
from typing import Dict

from src.config import SimulationConfig
from src.modes.base import SimulationMode, _compute_angle_values
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
        return {
            "g4_data_directory": config.general.g4_data_directory,
            "seed": config.general.seed,
            "threads": config.general.threads,
            "histories": config.general.histories,
            "sequential_times": config.imaging.sequential_times,
            "timeline_end": str(config.imaging.timeline_end),
            "rotation_rate": str(config.imaging.rotation_rate),
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
            **_compute_angle_values(
                config.imaging.rotation_direction, config.imaging.start_angle
            ),
        }

    def build_sub_context(self, config: SimulationConfig) -> Dict[str, object]:
        phantom_name = config.phantom.phantom_name or "MRCP_{}".format(
            config.phantom.phantom_sex
        )
        output_filename = "{}_{}_{}_{}_PHANTOM_DOSE".format(
            phantom_name,
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

        # Parse organ_scoring_ids into TsTetGeomScorer ICRPMaterials vector format
        # Config stores comma-separated organ names; template needs: N "Organ1" "Organ2"
        organs = [
            o.strip() for o in config.phantom.organ_scoring_ids.split(",") if o.strip()
        ]
        if organs:
            icrp_materials = "{} {}".format(
                len(organs), " ".join(f'"{o}"' for o in organs)
            )
        else:
            icrp_materials = ""

        return {
            "phantom_directory": os.path.abspath(
                os.path.join(config.phantom.phantom_data_directory, phantom_name)
            ),
            "phantom_name": phantom_name,
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
            "icrp_materials": icrp_materials,
        }

    def get_sub_file_name(self, config: SimulationConfig) -> str:
        return "phantomICRP145.txt"

    def get_sub_template_name(self, config: SimulationConfig) -> str:
        return "phantomICRP145.j2"

    def compute_histories(self, config: SimulationConfig) -> str:
        if config.phantom.phase_space_mode == "replay":
            return str(int(config.phantom.phase_space_multiple_use) * 1000000)
        return str(int(config.imaging.sequential_times) * int(config.general.histories))

    def _get_phase_space_mode(self, config: SimulationConfig) -> str:
        return config.phantom.phase_space_mode

    def _generate_replay_parameter_file(
        self, config: SimulationConfig, rundir: str, project_root: str
    ) -> str:
        """Generate a PhaseSpace replay parameter file for the phantom mode.

        Uses the shared ``phsp_replay_core.j2`` include for World/Physics/
        Rotation/Source/TimeFeatures, then appends the phantom geometry and
        DoseToMedium scorer.
        """
        import os

        from src.template_renderer import TemplateRenderer

        renderer = TemplateRenderer(
            os.path.join(project_root, "src", "boilerplates"),
            os.path.join(project_root, "tmp"),
        )

        ctx = {
            "phase_space_file": config.phantom.phase_space_file,
            "phase_space_multiple_use": config.phantom.phase_space_multiple_use,
            "phase_space_component": config.phantom.phase_space_component,
            "seed": config.general.seed,
            "threads": config.general.threads,
            "g4_data_directory": config.general.g4_data_directory,
            "sequential_times": config.imaging.sequential_times,
            "timeline_end": str(config.imaging.timeline_end),
            "rotation_rate": str(config.imaging.rotation_rate),
            "rotation_direction": config.imaging.rotation_direction,
            "start_angle": str(config.imaging.start_angle),
            "patient_roll_value": config.dicom.patient_roll.value,
            "world_hlz": "2.0 m",
            **_compute_angle_values(
                config.imaging.rotation_direction, config.imaging.start_angle
            ),
        }

        output_file = os.path.join(rundir, "phantom_replay.txt")
        renderer.render("phsp_replay_core.j2", ctx, "phantom_replay_core.txt")

        core_path = os.path.join(project_root, "tmp", "phantom_replay_core.txt")

        sub_ctx = self.build_sub_context(config)
        sub_template = self.get_sub_template_name(config)
        sub_output = self.get_sub_file_name(config)
        renderer.render(sub_template, sub_ctx, sub_output)
        sub_path = os.path.join(project_root, "tmp", sub_output)

        with open(output_file, "w") as out:
            with open(core_path) as f:
                out.write(f.read())
            out.write("\n# Phantom geometry and scoring\n")
            with open(sub_path) as f:
                out.write(f.read())

        logger.info("Generated phantom replay parameter file: %s", output_file)
        return output_file

    def prepare_run(
        self,
        config: SimulationConfig,
        rundir: str,
        project_root: str,
    ) -> None:
        mode = self._get_phase_space_mode(config)
        if mode == "replay":
            phsp_file = config.phantom.phase_space_file
            if phsp_file:
                base = os.path.splitext(phsp_file)[0]
                for ext in (".phsp", ".header"):
                    src = base + ext
                    if os.path.exists(src):
                        shutil.copy(src, rundir)
                        logger.info("Copied %s to %s", src, rundir)
                    else:
                        logger.warning("Phase space file %s not found", src)
            self.copy_common_files(rundir, config, project_root)
            sub_path = os.path.join(project_root, "tmp", self.get_sub_file_name(config))
            if os.path.exists(sub_path):
                shutil.copy(sub_path, rundir)
            logger.info("Prepared phantom phase-space replay in %s", rundir)
        else:
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
