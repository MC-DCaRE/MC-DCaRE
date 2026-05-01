"""CTDI phantom simulation mode."""

from __future__ import annotations

import logging
import os
from typing import List, Tuple

from src.config import SimulationConfig
from src.fieldtobladeopening import fieldtobladeopening
from src.modes.base import SimulationMode
from src.parameter_editor import ParameterEditor
from src.simulation_runner import SimulationRunner

logger = logging.getLogger(__name__)

_PLUG_POSITIONS = [
    "ChamberPlugCentre",
    "ChamberPlugTop",
    "ChamberPlugBottom",
    "ChamberPlugLeft",
    "ChamberPlugRight",
]


class CtdiMode(SimulationMode):
    """Simulation mode for CTDI phantom dose measurements."""

    def edit_main_file(self, config: SimulationConfig, lines: List[str]) -> None:
        s = ParameterEditor.string_index_replacement
        s("includeFile = patientDICOM.txt", lines)
        if not config.ctdi.graphics_enabled:
            s("Ts/UseQt", lines)
            s("s:Gr/ViewA/Type", lines)
            s("b:Gr/Enable", lines)
        if config.ctdi.user_blade_enabled:
            blades = fieldtobladeopening(
                [
                    config.ctdi.user_field_x1,
                    config.ctdi.user_field_x2,
                    config.ctdi.user_field_y1,
                    config.ctdi.user_field_y2,
                ]
            )
            s("dc:Ge/Coll1/TransY", lines, blades[0])
            s("dc:Ge/Coll2/TransY", lines, blades[1])
            s("dc:Ge/Coll3/TransX", lines, blades[2])
            s("dc:Ge/Coll4/TransX", lines, blades[3])
        if config.ctdi.phantom_size == "16 cm":
            s("includeFile = CTDIphantom_32.txt", lines)
        elif config.ctdi.phantom_size == "32 cm":
            s("includeFile = CTDIphantom_16.txt", lines)

    def edit_sub_file(self, config: SimulationConfig, lines: List[str]) -> None:
        """Edit the CTDI phantom sub-file with couch and scoring parameters."""
        s = ParameterEditor.string_index_replacement
        if not config.ctdi.couch_enabled:
            s('s:Ge/couch/Parent="couchgroup"', lines)
        s("d:Ge/couch/HLX", lines, config.ctdi.couch_width)
        s("d:Ge/couch/HLY", lines, config.ctdi.couch_thickness)
        s("d:Ge/couch/HLZ", lines, config.ctdi.couch_length)
        s("i:Sc/ChamberPlugDose_dtm/ZBins", lines, config.ctdi.dose_to_medium_zbins)
        s("i:Sc/ChamberPlugDose_tle/ZBins", lines, config.ctdi.tle_zbins)
        s("i:Sc/ChamberPlugDose_dtw/ZBins", lines, config.ctdi.dose_to_water_zbins)

    def get_sub_file_name(self, config: SimulationConfig) -> str:
        """Return the CTDI phantom include filename matching the configured size."""
        size_number = config.ctdi.phantom_size.split()[0]
        return "CTDIphantom_" + size_number + ".txt"

    def compute_histories(self, config: SimulationConfig) -> str:
        """Return the user-configured history count directly."""
        return config.general.histories

    def prepare_run(
        self,
        config: SimulationConfig,
        rundir: str,
        project_root: str,
    ) -> None:
        """Copy common include files into the CTDI run directory."""
        self.copy_common_files(rundir, config, project_root)
        logger.info("Prepared CTDI run files in %s", rundir)

    def execute(
        self,
        config: SimulationConfig,
        rundir: str,
        project_root: str,
    ) -> None:
        """Run TOPAS for each chamber plug position in parallel."""
        commands = self._generate_plug_files(
            config.ctdi.phantom_size,
            rundir,
            config.general.topas_directory,
            project_root,
        )
        SimulationRunner.run_ctdi(config.general.topas_directory, rundir, commands)

    @staticmethod
    def _generate_plug_files(
        phantom_size: str,
        rundatadir: str,
        topas_path: str,
        project_root: str,
    ) -> List[Tuple[List[str], str]]:
        """Generate per-plug-position TOPAS input files by combining head source and phantom boilerplates."""
        if phantom_size == "16 cm":
            phantom_tag = "ctdi16"
        elif phantom_size == "32 cm":
            phantom_tag = "ctdi32"
        else:
            phantom_tag = "ctdi16"

        if phantom_tag == "ctdi16":
            phantom_path = os.path.join(project_root, "tmp", "CTDIphantom_16.txt")
        else:
            phantom_path = os.path.join(project_root, "tmp", "CTDIphantom_32.txt")

        with open(phantom_path, "r") as f:
            phantom_content = f.read()

        headsource_path = os.path.join(project_root, "tmp", "headsourcecode.txt")
        with open(headsource_path, "r") as f:
            headsource_content = f.read()

        commands: List[Tuple[List[str], str]] = []
        for position in _PLUG_POSITIONS:
            combined = headsource_content + phantom_content
            combined = combined.replace("@@PLACEHOLDER@@", position)
            combined = combined.replace(
                "s:Ge/" + position + '/Material="PMMA"',
                "s:Ge/" + position + '/Material="Air"',
            )

            position_file = os.path.join(rundatadir, position + ".txt")
            with open(position_file, "w") as f:
                f.write(combined)

            commands.append(([topas_path, position_file], rundatadir))
        return commands
