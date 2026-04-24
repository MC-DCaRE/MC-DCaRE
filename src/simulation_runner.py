import logging
import os
import subprocess
import multiprocessing as mp
from typing import List, Tuple

logger = logging.getLogger(__name__)


class SimulationRunner:
    @staticmethod
    def run_topas(command: str, working_dir: str) -> None:
        logger.info("Running TOPAS: %s in %s", command, working_dir)
        subprocess.run(command, cwd=working_dir, shell=True)

    @staticmethod
    def run_dicom(topas_path: str, rundatadir: str) -> None:
        command = topas_path + " " + rundatadir + "/headsourcecode.txt"
        logger.info("Starting DICOM simulation")
        SimulationRunner.run_topas(command, rundatadir)

    @staticmethod
    def run_ctdi(
        topas_path: str,
        rundatadir: str,
        commands: List[Tuple[str, str]],
    ) -> None:
        logger.info("Starting CTDI simulation with %d commands", len(commands))
        with mp.Pool(processes=min(5, os.cpu_count() or 1)) as pool:
            pool.starmap(SimulationRunner.run_topas, commands)
