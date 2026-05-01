"""Executes TOPAS Monte Carlo simulations as subprocesses."""

from __future__ import annotations

import logging
import os
import subprocess
import multiprocessing as mp
from typing import List, Tuple

logger = logging.getLogger(__name__)


class SimulationRunner:
    """Launches TOPAS processes for DICOM and CTDI simulation modes."""

    @staticmethod
    def run_topas(command: List[str], working_dir: str) -> None:
        """Execute a single TOPAS command and check its return code.

        Args:
            command: TOPAS executable path and argument list.
            working_dir: Working directory for the subprocess.

        Raises:
            RuntimeError: If TOPAS exits with a non-zero return code.
        """
        logger.info("Running TOPAS: %s in %s", " ".join(command), working_dir)
        result = subprocess.run(command, cwd=working_dir)
        if result.returncode != 0:
            logger.error("TOPAS exited with code %d: %s", result.returncode, command)
            raise RuntimeError(
                "TOPAS process failed with return code {}".format(result.returncode)
            )

    @staticmethod
    def run_dicom(topas_path: str, rundatadir: str) -> None:
        """Run a single DICOM patient simulation."""
        command: List[str] = [topas_path, rundatadir + "/headsourcecode.txt"]
        logger.info("Starting DICOM simulation")
        SimulationRunner.run_topas(command, rundatadir)

    @staticmethod
    def run_ctdi(
        topas_path: str,
        rundatadir: str,
        commands: List[Tuple[List[str], str]],
    ) -> None:
        """Run CTDI simulations for each chamber plug position in parallel.

        Args:
            topas_path: Path to the TOPAS executable.
            rundatadir: Run data directory for outputs.
            commands: List of (command, working_dir) tuples, one per plug position.
        """
        logger.info("Starting CTDI simulation with %d commands", len(commands))
        with mp.Pool(processes=min(5, os.cpu_count() or 1)) as pool:
            pool.starmap(SimulationRunner.run_topas, commands)
