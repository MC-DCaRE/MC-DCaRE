from __future__ import annotations

import logging
import os
import shutil
from datetime import datetime

from src.config import SimulationConfig
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

    def create_runfolder(self) -> str:
        """Create and return a timestamped runfolder directory."""
        return self._create_runfolder()

    @staticmethod
    def _copy_config_yaml(rundir: str, config: SimulationConfig) -> None:
        """Copy the source config YAML into the runfolder for provenance.

        If *config* was not loaded from a YAML file (e.g. built from GUI
        values or programmatically), the copy is silently skipped.

        Args:
            rundir: Path to the runfolder destination.
            config: The simulation configuration whose source path to copy.
        """
        src: str | None = config.config_yaml_path
        if src is None:
            logger.debug("No config YAML path recorded; skipping copy")
            return
        if not os.path.isfile(src):
            logger.warning("Config YAML source not found: %s", src)
            return
        dest: str = os.path.join(rundir, os.path.basename(src))
        try:
            shutil.copy2(src, dest)
            logger.info("Copied config YAML to %s", dest)
        except OSError as exc:
            logger.warning("Failed to copy config YAML to runfolder: %s", exc)

    def run(
        self, config: SimulationConfig, dry_run: bool = False, detach: bool = False
    ) -> str:
        rundir: str = self._create_runfolder()
        self.run_with_runfolder(rundir, config, dry_run=dry_run, detach=detach)
        return rundir

    def run_with_runfolder(
        self,
        rundir: str,
        config: SimulationConfig,
        dry_run: bool = False,
        detach: bool = False,
    ) -> None:
        """Execute the full simulation pipeline using an existing runfolder."""
        mode: SimulationMode = self._get_mode(config)
        self.boilerplate_manager.reset_tmp()

        logger.info("Runfolder: %s", rundir)
        self._copy_config_yaml(rundir, config)

        renderer = self.boilerplate_manager.create_renderer()
        main_context = mode.build_main_context(config)
        renderer.render(mode.main_template_name, main_context, mode.main_output_name)

        sub_template_name: str = mode.get_sub_template_name(config)
        sub_output_name: str = mode.get_sub_file_name(config)
        sub_context = mode.build_sub_context(config)
        renderer.render(sub_template_name, sub_context, sub_output_name)

        voltage: float = config.imaging.anode_voltage.value
        exposure: float = config.imaging.exposure.value
        histories: str = mode.compute_histories(config)
        dose_calibration_factor: float = float(config.general.dose_calibration_factor)
        SpectrumGenerator.generate(
            voltage,
            exposure,
            histories,
            self.project_root,
            dose_calibration_factor,
            fan_mode=config.imaging.fan_mode,
            seed=int(config.general.seed),
            threads=int(config.general.threads),
        )

        mode.prepare_run(config, rundir, self.project_root)

        if not dry_run:
            mode.execute(config, rundir, self.project_root, detach=detach)

        logger.info("Run completed in %s", rundir)

    def run_dicom_simulation(self, config: SimulationConfig) -> str:
        return self.run(config, dry_run=False)

    def run_ctdi_simulation(self, config: SimulationConfig) -> str:
        return self.run(config, dry_run=False)

    def prepare_only(self, config: SimulationConfig) -> str:
        return self.run(config, dry_run=True)
