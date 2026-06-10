"""Abstract base class for simulation mode strategies."""

from __future__ import annotations

import logging
import os
import shutil
from abc import ABC, abstractmethod
from typing import Dict

from src.config import SimulationConfig

logger = logging.getLogger(__name__)


class SimulationMode(ABC):
    """Strategy interface for CTDI and DICOM simulation modes."""

    @property
    @abstractmethod
    def main_template_name(self) -> str:
        """Return the Jinja2 template filename for the main TOPAS file."""
        ...

    @property
    @abstractmethod
    def main_output_name(self) -> str:
        """Return the output filename for the rendered main TOPAS file."""
        ...

    @abstractmethod
    def build_main_context(self, config: SimulationConfig) -> Dict[str, object]:
        """Build the template context dict for the main TOPAS file."""
        ...

    @abstractmethod
    def build_sub_context(self, config: SimulationConfig) -> Dict[str, object]:
        """Build the template context dict for the sub-include file."""
        ...

    @abstractmethod
    def get_sub_file_name(self, config: SimulationConfig) -> str:
        """Return the filename of the sub-include file for this mode."""
        ...

    @abstractmethod
    def get_sub_template_name(self, config: SimulationConfig) -> str:
        """Return the Jinja2 template filename for the sub-include file."""
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
        shutil.copy(
            os.path.join(project_root, "tmp", "ConvertedTopasFile.txt"),
            rundatadir,
        )
        shutil.copy(
            os.path.join(project_root, "tmp", "head_calibration_factor.txt"),
            rundatadir,
        )
        shutil.copy(
            os.path.join(project_root, "tmp", "simulation_metadata.yaml"),
            rundatadir,
        )
        fan_mode = config.imaging.fan_mode
        if fan_mode == "Full Fan":
            shutil.copy(os.path.join(include_dir, "fullfan.txt"), rundatadir)
        elif fan_mode == "Half Fan":
            shutil.copy(os.path.join(include_dir, "halffan.txt"), rundatadir)
