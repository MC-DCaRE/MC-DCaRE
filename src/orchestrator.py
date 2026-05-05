from __future__ import annotations

import logging
import os
from datetime import datetime

from src.config import SimulationConfig, quantity_unit_stripper
from src.boilerplate_manager import BoilerplateManager
from src.modes.base import SimulationMode
from src.modes.dicom_mode import DicomMode
from src.modes.ctdi_mode import CtdiMode
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

        renderer = self.boilerplate_manager.create_renderer()
        main_context = mode.build_main_context(config)
        renderer.render(mode.main_template_name, main_context, mode.main_output_name)

        sub_template_name: str = mode.get_sub_template_name(config)
        sub_output_name: str = mode.get_sub_file_name(config)
        sub_context = mode.build_sub_context(config)
        renderer.render(sub_template_name, sub_context, sub_output_name)

        voltage: float
        _: str
        voltage, _ = quantity_unit_stripper(config.imaging.anode_voltage)
        exposure, _ = quantity_unit_stripper(config.imaging.exposure)
        histories: str = mode.compute_histories(config)
        dose_calibration_factor: float = float(config.general.dose_calibration_factor)
        SpectrumGenerator.generate(
            voltage, exposure, histories, self.project_root, dose_calibration_factor
        )

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
