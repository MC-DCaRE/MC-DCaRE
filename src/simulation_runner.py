import subprocess
import os
import multiprocessing as mp
from typing import List, Tuple


class SimulationRunner:
    @staticmethod
    def run_topas(command: str, working_dir: str) -> None:
        subprocess.run(command, cwd=working_dir, shell=True)
        print("ran")

    @staticmethod
    def run_dicom(topas_path: str, rundatadir: str) -> None:
        command = topas_path + " " + rundatadir + "/headsourcecode.txt"
        with mp.Pool(processes=min(5, os.cpu_count() or 1)) as pool:
            pool.starmap(SimulationRunner.run_topas, [(command, rundatadir)])

    @staticmethod
    def run_ctdi(
        topas_path: str,
        rundatadir: str,
        commands: List[Tuple[str, str]],
    ) -> None:
        with mp.Pool(processes=min(5, os.cpu_count() or 1)) as pool:
            pool.starmap(SimulationRunner.run_topas, commands)
