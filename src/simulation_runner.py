"""Executes TOPAS Monte Carlo simulations as subprocesses."""

from __future__ import annotations

import logging
import os
import subprocess
import multiprocessing as mp
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)


class SimulationRunner:
    """Launches TOPAS processes for DICOM and CTDI simulation modes."""

    @staticmethod
    def run_topas(
        command: List[str],
        working_dir: str,
        log_path: Optional[str] = None,
    ) -> None:
        """Execute a single TOPAS command and check its return code.

        Args:
            command: TOPAS executable path and argument list.
            working_dir: Working directory for the subprocess.
            log_path: If provided, capture stdout+stderr to this file in real time.

        Raises:
            RuntimeError: If TOPAS exits with a non-zero return code.
        """
        logger.info("Running TOPAS: %s in %s", " ".join(command), working_dir)

        if log_path is not None:
            proc = subprocess.Popen(
                command,
                cwd=working_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            with open(log_path, "w") as log_file:
                if proc.stdout is not None:
                    for line in proc.stdout:
                        log_file.write(line)
                        log_file.flush()
                proc.wait()
            returncode = proc.returncode
        else:
            result = subprocess.run(command, cwd=working_dir)
            returncode = result.returncode

        if returncode != 0:
            logger.error("TOPAS exited with code %d: %s", returncode, command)
            raise RuntimeError(
                "TOPAS process failed with return code {}".format(returncode)
            )

    @staticmethod
    def run_dicom(topas_path: str, rundatadir: str) -> None:
        """Run a single DICOM patient simulation."""
        command: List[str] = [topas_path, rundatadir + "/headsourcecode.txt"]
        log_path = os.path.join(rundatadir, "topas_dicom.log")
        logger.info("Starting DICOM simulation")
        SimulationRunner.run_topas(command, rundatadir, log_path)

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
        logged_commands: List[Tuple[List[str], str, str]] = []
        for command, work_dir in commands:
            param_file = command[-1]
            basename = os.path.splitext(os.path.basename(param_file))[0]
            log_path = os.path.join(rundatadir, "topas_{}.log".format(basename))
            logged_commands.append((command, work_dir, log_path))
        with mp.Pool(processes=min(5, os.cpu_count() or 1)) as pool:
            pool.starmap(SimulationRunner.run_topas, logged_commands)
