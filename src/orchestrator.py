from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import List

from src.config import SimulationConfig, quantity_unit_stripper
from src.boilerplate_manager import BoilerplateManager
from src.modes.base import SimulationMode
from src.modes.dicom_mode import DicomMode
from src.modes.ctdi_mode import CtdiMode
from src.parameter_editor import ParameterEditor
from src.spectrum_generator import SpectrumGenerator

logger = logging.getLogger(__name__)


class Orchestrator:
    def __init__(self, project_root: str) -> None:
        self.project_root: str = project_root
        self.boilerplate_manager: BoilerplateManager = BoilerplateManager(project_root)

    def _get_mode(self, config: SimulationConfig) -> SimulationMode:
        if config.imaging.simulation_type == "DICOM":
            return DicomMode()
        return CtdiMode()

    def _apply_common_edits(self, config: SimulationConfig, lines: List[str]) -> None:
        s = ParameterEditor.string_index_replacement
        s(
            "s:Ts/G4DataDirectory",
            lines,
            '"' + config.general.g4_data_directory + '"',
        )
        s(
            "i:Tf/NumberOfSequentialTimes",
            lines,
            config.imaging.sequential_times,
        )
        s("d:Tf/TimelineEnd", lines, config.imaging.timeline_end)
        s("d:Tf/Rotate/Rate", lines, config.imaging.rotation_rate)
        s(
            "d:Tf/Rotate/StartValue",
            lines,
            config.imaging.start_angle,
        )
        s("i:Ts/Seed", lines, config.general.seed)
        s("i:Ts/NumberOfThreads", lines, config.general.threads)
        s(
            "i:So/beam/NumberOfHistoriesInRun",
            lines,
            config.general.histories,
        )
        s("dc:Ge/Coll1/TransY", lines, config.imaging.blade_x1)
        s("dc:Ge/Coll2/TransY", lines, config.imaging.blade_x2)
        s("dc:Ge/Coll3/TransX", lines, config.imaging.blade_y1)
        s("dc:Ge/Coll4/TransX", lines, config.imaging.blade_y2)
        if config.imaging.fan_mode == "Full Fan":
            s("includeFile = halffan.txt", lines)
        elif config.imaging.fan_mode == "Half Fan":
            s("includeFile = fullfan.txt", lines)

    def _create_runfolder(self) -> str:
        rundatadir: str = os.path.join(
            self.project_root + "/runfolder",
            datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
        )
        os.makedirs(rundatadir)
        return rundatadir

    def run(self, config: SimulationConfig, dry_run: bool = False) -> str:
        mode: SimulationMode = self._get_mode(config)
        self.boilerplate_manager.reset_tmp()

        main_path: str = self.boilerplate_manager.get_headsource_path()
        with open(main_path, "r") as f:
            lines: List[str] = f.readlines()
        self._apply_common_edits(config, lines)
        mode.edit_main_file(config, lines)
        with open(main_path, "w") as f:
            f.writelines(lines)

        sub_file: str = self.boilerplate_manager.get_tmp_path(
            mode.get_sub_file_name(config)
        )
        with open(sub_file, "r") as f:
            lines = f.readlines()
        mode.edit_sub_file(config, lines)
        with open(sub_file, "w") as f:
            f.writelines(lines)

        voltage: float
        _: str
        voltage, _ = quantity_unit_stripper(config.imaging.anode_voltage)
        exposure, _ = quantity_unit_stripper(config.imaging.exposure)
        histories: str = mode.compute_histories(config)
        SpectrumGenerator.generate(voltage, exposure, histories, self.project_root)

        rundir: str = self._create_runfolder()
        mode.prepare_run(config, rundir, self.project_root)

        if not dry_run:
            mode.execute(config, rundir, self.project_root)

        logger.info("Run completed in %s", rundir)
        return rundir

    def run_dicom_simulation(self, config: SimulationConfig) -> str:
        return self.run(config, dry_run=False)

    def run_ctdi_simulation(self, config: SimulationConfig) -> str:
        return self.run(config, dry_run=False)

    def prepare_only(self, config: SimulationConfig) -> str:
        return self.run(config, dry_run=True)
