"""Abstract base class for simulation mode strategies."""

from __future__ import annotations

import logging
import os
import shutil
from abc import ABC, abstractmethod
from typing import List

from src.config import SimulationConfig

logger = logging.getLogger(__name__)


class SimulationMode(ABC):
    """Strategy interface for CTDI and DICOM simulation modes."""

    @abstractmethod
    def edit_main_file(self, config: SimulationConfig, lines: List[str]) -> None:
        """Edit the main TOPAS boilerplate lines for this mode."""
        ...

    @abstractmethod
    def edit_sub_file(self, config: SimulationConfig, lines: List[str]) -> None:
        """Edit the sub-include TOPAS boilerplate lines for this mode."""
        ...

    @abstractmethod
    def get_sub_file_name(self, config: SimulationConfig) -> str:
        """Return the filename of the sub-include file for this mode."""
        ...

    @abstractmethod
    def compute_histories(self, config: SimulationConfig) -> str:
        """Compute the number of histories to simulate."""
        ...

    @abstractmethod
    def prepare_run(
        self,
        config: SimulationConfig,
        rundir: str,
        project_root: str,
    ) -> None:
        """Copy required files into the run directory before execution."""
        ...

    @abstractmethod
    def execute(
        self,
        config: SimulationConfig,
        rundir: str,
        project_root: str,
    ) -> None:
        """Run the simulation for this mode."""
        ...

    @staticmethod
    def copy_common_files(
        rundatadir: str, config: SimulationConfig, project_root: str
    ) -> None:
        """Copy shared include files (spectrum, calibration, bowtie) into the run data directory."""
        include_dir = os.path.join(
            project_root, "src", "boilerplates", "TOPAS_includeFiles"
        )
        shutil.copy(os.path.join(include_dir, "Muen.dat"), rundatadir)
        shutil.copy(os.path.join(include_dir, "NbParticlesInTime.txt"), rundatadir)
        shutil.copy(
            os.path.join(project_root, "tmp", "ConvertedTopasFile.txt"),
            rundatadir,
        )
        shutil.copy(
            os.path.join(project_root, "tmp", "head_calibration_factor.txt"),
            rundatadir,
        )
        fan_mode = config.imaging.fan_mode
        if fan_mode == "Full Fan":
            shutil.copy(os.path.join(include_dir, "fullfan.txt"), rundatadir)
        elif fan_mode == "Half Fan":
            shutil.copy(os.path.join(include_dir, "halffan.txt"), rundatadir)
