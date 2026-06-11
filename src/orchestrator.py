from __future__ import annotations

import logging
import os
import shutil
from datetime import datetime

import yaml

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

    @staticmethod
    def _write_replay_metadata(
        rundir: str,
        scoring_metadata_path: str,
        phase_space_multiple_use: int,
    ) -> None:
        """Copy scoring metadata to replay runfolder with adjusted norm_factor.

        Reads the scoring run's simulation_metadata.yaml, divides norm_factor
        by PhaseSpaceMultipleUse, and writes the result to the replay runfolder.
        """
        with open(scoring_metadata_path, "r", encoding="utf-8") as f:
            metadata = yaml.safe_load(f)
        if not isinstance(metadata, dict):
            raise ValueError("Invalid metadata file: %s" % scoring_metadata_path)
        original_norm = metadata.get("norm_factor", 0.0)
        metadata["norm_factor"] = original_norm / phase_space_multiple_use
        metadata["phase_space_multiple_use"] = phase_space_multiple_use
        metadata["phase_space_source"] = scoring_metadata_path
        dest_path = os.path.join(rundir, "simulation_metadata.yaml")
        with open(dest_path, "w", encoding="utf-8") as f:
            yaml.dump(metadata, f, default_flow_style=False, sort_keys=False)
        logger.info(
            "Wrote replay metadata: norm_factor=%.6e (original=%.6e / M=%d)",
            metadata["norm_factor"],
            original_norm,
            phase_space_multiple_use,
        )

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

        phase_space_mode = self._get_phase_space_mode(config)

        if phase_space_mode == "score":
            self._run_score_mode(rundir, config, mode, dry_run, detach)
        elif phase_space_mode == "replay":
            self._run_replay_mode(rundir, config, mode, dry_run, detach)
        else:
            self._run_off_mode(rundir, config, mode, dry_run, detach)

        logger.info("Run completed in %s", rundir)

    def _get_phase_space_mode(self, config: SimulationConfig) -> str:
        """Extract phase_space_mode from config (only CTDI mode supports it)."""
        if config.imaging.simulation_type == "CTDI":
            return config.ctdi.phase_space_mode
        return "off"

    def _run_off_mode(
        self,
        rundir: str,
        config: SimulationConfig,
        mode: SimulationMode,
        dry_run: bool,
        detach: bool,
    ) -> None:
        """Standard direct-beam pipeline (unchanged from original)."""
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

    def _run_score_mode(
        self,
        rundir: str,
        config: SimulationConfig,
        mode: SimulationMode,
        dry_run: bool,
        detach: bool,
    ) -> None:
        """Phase space scoring pipeline."""
        ctdi_mode = mode
        assert isinstance(ctdi_mode, CtdiMode)

        # Score mode still needs spectrum for the beam source.
        voltage: float = config.imaging.anode_voltage.value
        exposure: float = config.imaging.exposure.value
        histories: str = ctdi_mode.compute_histories(config)
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

        ctdi_mode.prepare_run(config, rundir, self.project_root)

        if not dry_run:
            ctdi_mode.execute(config, rundir, self.project_root, detach=detach)

            # Post-process: run PhaseSpaceAnalyzer on output.
            from src.services.phase_space_analyzer import PhaseSpaceAnalyzer

            phsp_file = os.path.join(rundir, "beam_exit_phsp.phsp")
            metadata_path = os.path.join(
                self.project_root, "tmp", "simulation_metadata.yaml"
            )
            if os.path.isfile(phsp_file):
                analyzer = PhaseSpaceAnalyzer(
                    phsp_file,
                    metadata_path=metadata_path
                    if os.path.isfile(metadata_path)
                    else None,
                )
                stats = analyzer.analyze()
                stats_path = os.path.join(rundir, "phase_space", "beam_statistics.yaml")
                with open(stats_path, "w", encoding="utf-8") as f:
                    yaml.dump(stats, f, default_flow_style=False, sort_keys=False)
                logger.info("Phase space statistics written to %s", stats_path)

                # Move .phsp file to phase_space subdirectory.
                dest = os.path.join(rundir, "phase_space", "beam_exit_phsp.phsp")
                shutil.move(phsp_file, dest)
                logger.info("Moved phase space file to %s", dest)

                # Copy metadata to phase_space/ so replay can find it.
                if os.path.isfile(metadata_path):
                    metadata_dest = os.path.join(
                        rundir, "phase_space", "simulation_metadata.yaml"
                    )
                    shutil.copy2(metadata_path, metadata_dest)
                    logger.info("Copied metadata to %s", metadata_dest)

    def _run_replay_mode(
        self,
        rundir: str,
        config: SimulationConfig,
        mode: SimulationMode,
        dry_run: bool,
        detach: bool,
    ) -> None:
        """Phase space replay pipeline."""
        ctdi_mode = mode
        assert isinstance(ctdi_mode, CtdiMode)

        # Replay mode: NO SpectrumGenerator.

        # Prepare run: copies Muen.dat + phase space file.
        ctdi_mode.prepare_run(config, rundir, self.project_root)

        # Copy scoring run's metadata with adjusted norm_factor.
        # The scoring pipeline copies simulation_metadata.yaml into the
        # same directory as the .phsp file (phase_space/ subdirectory).
        phsp_dir = os.path.dirname(config.ctdi.phase_space_file)
        scoring_metadata = os.path.join(phsp_dir, "simulation_metadata.yaml")
        if not os.path.isfile(scoring_metadata):
            # Fallback: check the runfolder root (older scoring runs).
            parent_dir = os.path.dirname(phsp_dir)
            scoring_metadata = os.path.join(parent_dir, "simulation_metadata.yaml")
        if os.path.isfile(scoring_metadata):
            self._write_replay_metadata(
                rundir,
                scoring_metadata,
                config.ctdi.phase_space_multiple_use,
            )
        else:
            logger.warning(
                "No scoring metadata found for phase space file; "
                "calibration may be incorrect"
            )

        if not dry_run:
            ctdi_mode.execute(config, rundir, self.project_root, detach=detach)

    def run_dicom_simulation(self, config: SimulationConfig) -> str:
        return self.run(config, dry_run=False)

    def run_ctdi_simulation(self, config: SimulationConfig) -> str:
        return self.run(config, dry_run=False)

    def prepare_only(self, config: SimulationConfig) -> str:
        return self.run(config, dry_run=True)
