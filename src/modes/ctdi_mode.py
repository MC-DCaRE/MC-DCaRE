"""CTDI phantom simulation mode."""

from __future__ import annotations

import logging
import os
import shutil
from typing import Dict

from src.config import SimulationConfig
from src.fieldtobladeopening import fieldtobladeopening
from src.modes.base import SimulationMode, _compute_angle_values
from src.services.phase_space_analyzer import header_path_for
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


class CtdiMode(SimulationMode):
    """Simulation mode for CTDI phantom dose measurements.

    Supports three phase_space_mode values:
      - ``"off"``: standard direct-beam pipeline (default).
      - ``"score"``: generate a phase space file from the beam line.
      - ``"replay"``: replay a phase space file onto the phantom.
    """

    @property
    def main_template_name(self) -> str:
        return "headsourcecode_boilerplate.j2"

    @property
    def main_output_name(self) -> str:
        return "headsourcecode.txt"

    def _get_phase_space_mode(self, config: SimulationConfig) -> str:
        """Return the phase space mode string from config."""
        return config.ctdi.phase_space_mode

    def _get_main_template(self, config: SimulationConfig) -> str:
        """Select the main template based on phase_space_mode."""
        mode = self._get_phase_space_mode(config)
        if mode == "score":
            return "ctdi_phsp_score.j2"
        if mode == "replay":
            return "ctdi_phsp_replay.j2"
        return "headsourcecode_boilerplate.j2"

    def _get_main_output(self, config: SimulationConfig) -> str:
        """Select the main output filename based on phase_space_mode."""
        mode = self._get_phase_space_mode(config)
        if mode == "score":
            return "ctdi_phsp_score.txt"
        if mode == "replay":
            return "ctdi_phsp_replay.txt"
        return "headsourcecode.txt"

    def build_main_context(self, config: SimulationConfig) -> Dict[str, object]:
        mode = self._get_phase_space_mode(config)

        # Replay mode: no collimators, no beam line, PhaseSpace source params.
        if mode == "replay":
            size_number: str = config.ctdi.phantom_size.split()[0]
            return {
                "g4_data_directory": config.general.g4_data_directory,
                "seed": config.general.seed,
                "threads": config.general.threads,
                "sequential_times": config.imaging.sequential_times,
                "timeline_end": str(config.imaging.timeline_end),
                "rotation_rate": str(config.imaging.rotation_rate),
                "start_angle": str(config.imaging.start_angle),
                "graphics_enabled": config.ctdi.graphics_enabled,
                "phantom_size": size_number,
                "patient_yaw": "0 deg",
                "patient_pitch": "0 deg",
                "patient_roll_value": 0.0,
                "phase_space_file": os.path.splitext(
                    os.path.basename(config.ctdi.phase_space_file)
                )[0],
                "phase_space_multiple_use": config.ctdi.phase_space_multiple_use,
                # Needed so the main template can add the water parallel
                # worlds to LayeredMassGeometryWorlds when enabled (parallel
                # worlds with material MUST be listed or TOPAS segfaults).
                "water_chamber_enabled": config.ctdi.water_chamber_enabled,
                **_compute_angle_values(
                    config.imaging.rotation_direction, config.imaging.start_angle
                ),
            }

        # Base context shared by off and score modes (beam line geometry).
        size_number = config.ctdi.phantom_size.split()[0]
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

        base_context: Dict[str, object] = {
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
            "legacy_bowtie": config.imaging.legacy_bowtie,
            "graphics_enabled": config.ctdi.graphics_enabled,
            "simulation_type": "CTDI",
            "phantom_size": size_number,
            "bhf_thickness_mm": config.imaging.bhf_thickness_mm,
            "patient_yaw": "0 deg",
            "patient_pitch": "0 deg",
            "patient_roll_value": 0.0,
            # Needed so the main template can add the water parallel worlds to
            # LayeredMassGeometryWorlds when enabled (parallel worlds with
            # material MUST be listed or TOPAS segfaults).
            "water_chamber_enabled": config.ctdi.water_chamber_enabled,
            **_compute_angle_values(
                config.imaging.rotation_direction, config.imaging.start_angle
            ),
        }

        return base_context

    def build_sub_context(self, config: SimulationConfig) -> Dict[str, object]:
        mode = self._get_phase_space_mode(config)
        if mode == "score":
            # No phantom in scoring mode.
            return {}
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
        mode = self._get_phase_space_mode(config)
        if mode == "score":
            return ""
        size_number = config.ctdi.phantom_size.split()[0]
        return "CTDIphantom_{}.j2".format(size_number)

    def get_sub_file_name(self, config: SimulationConfig) -> str:
        mode = self._get_phase_space_mode(config)
        if mode == "score":
            return ""
        size_number = config.ctdi.phantom_size.split()[0]
        return "CTDIphantom_{}.txt".format(size_number)

    def compute_histories(self, config: SimulationConfig) -> str:
        mode = self._get_phase_space_mode(config)
        if mode == "replay":
            # Histories come from the phase space file, not config.
            # Return 0 as placeholder; actual count determined post-run.
            return "0"
        return str(int(config.imaging.sequential_times) * int(config.general.histories))

    def prepare_run(
        self,
        config: SimulationConfig,
        rundir: str,
        project_root: str,
    ) -> None:
        mode = self._get_phase_space_mode(config)
        if mode == "score":
            # Score mode: copy spectrum + calibration + bowtie (same as direct).
            self.copy_common_files(rundir, config, project_root)
            # Create phase_space output subdirectory.
            phsp_dir = os.path.join(rundir, "phase_space")
            os.makedirs(phsp_dir, exist_ok=True)
            logger.info("Prepared scoring run in %s (phase_space mode)", rundir)
        elif mode == "replay":
            # Replay mode: copy Muen.dat (TLE needs it) + phase_space file + metadata.
            include_dir = os.path.join(
                project_root, "src", "boilerplates", "TOPAS_includeFiles"
            )
            shutil.copy(os.path.join(include_dir, "Muen.dat"), rundir)
            # Copy phase space file to runfolder, plus its .header sibling.
            # TOPAS Binary format is self-describing via the header; the
            # PhaseSpace source requires both files together.
            phsp_src = config.ctdi.phase_space_file
            shutil.copy(phsp_src, rundir)
            header_src = header_path_for(phsp_src)
            if os.path.isfile(header_src):
                shutil.copy(header_src, rundir)
            else:
                logger.warning(
                    "Phase space header not found alongside %s; TOPAS replay "
                    "may fail to read the file",
                    phsp_src,
                )
            logger.info("Prepared replay run in %s", rundir)
        else:
            self.copy_common_files(rundir, config, project_root)
            logger.info("Prepared CTDI run files in %s", rundir)

    def execute(
        self,
        config: SimulationConfig,
        rundir: str,
        project_root: str,
        detach: bool = False,
    ) -> None:
        mode = self._get_phase_space_mode(config)
        if mode == "score":
            param_file = self._generate_scoring_parameter_file(
                config, rundir, project_root
            )
            SimulationRunner.run_ctdi(
                config.general.topas_directory, rundir, param_file, detach=detach
            )
        elif mode == "replay":
            param_file = self._generate_replay_parameter_file(
                config, rundir, project_root
            )
            SimulationRunner.run_ctdi(
                config.general.topas_directory, rundir, param_file, detach=detach
            )
        else:
            param_file = self._generate_single_parameter_file(
                config, rundir, project_root
            )
            SimulationRunner.run_ctdi(
                config.general.topas_directory, rundir, param_file, detach=detach
            )

    def _generate_scoring_parameter_file(
        self,
        config: SimulationConfig,
        rundatadir: str,
        project_root: str,
    ) -> str:
        """Generate a single TOPAS parameter file for phase space scoring."""
        renderer = TemplateRenderer(
            os.path.join(project_root, "src", "boilerplates"),
            os.path.join(project_root, "tmp"),
        )
        template = self._get_main_template(config)
        output = self._get_main_output(config)
        context = self.build_main_context(config)
        renderer.render(template, context, output)

        rendered_path = os.path.join(project_root, "tmp", output)
        output_file = os.path.join(rundatadir, "CTDI_phsp_score.txt")
        with open(rendered_path, "r", encoding="utf-8") as f:
            content = f.read()
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)
        return output_file

    def _generate_replay_parameter_file(
        self,
        config: SimulationConfig,
        rundatadir: str,
        project_root: str,
    ) -> str:
        """Generate a single TOPAS parameter file for phase space replay + phantom."""
        renderer = TemplateRenderer(
            os.path.join(project_root, "src", "boilerplates"),
            os.path.join(project_root, "tmp"),
        )
        template = self._get_main_template(config)
        output = self._get_main_output(config)
        context = self.build_main_context(config)
        renderer.render(template, context, output)

        # Concatenate replay template with phantom include.
        replay_path = os.path.join(project_root, "tmp", self._get_main_output(config))
        with open(replay_path, "r", encoding="utf-8") as f:
            replay_content = f.read()

        sub_template = self.get_sub_template_name(config)
        sub_context = self.build_sub_context(config)
        phantom_rendered = renderer.render_string(
            "{% include '" + sub_template + "' %}",
            sub_context,
        )
        combined = replay_content + phantom_rendered
        output_file = os.path.join(rundatadir, "CTDI_phsp_replay.txt")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(combined)
        return output_file

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
        with open(headsource_path, "r", encoding="utf-8") as f:
            headsource_content = f.read()
        sub_context = self.build_sub_context(config)
        phantom_rendered = renderer.render_string(
            "{% include '" + sub_template + "' %}",
            sub_context,
        )
        combined = headsource_content + phantom_rendered
        output_file = os.path.join(rundatadir, "CTDI_all_positions.txt")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(combined)
        return output_file
