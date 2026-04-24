from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import List

from src.config import SimulationConfig

logger = logging.getLogger(__name__)


class SimulationMode(ABC):
    @abstractmethod
    def edit_main_file(self, config: SimulationConfig, lines: List[str]) -> None: ...

    @abstractmethod
    def edit_sub_file(self, config: SimulationConfig, lines: List[str]) -> None: ...

    @abstractmethod
    def get_sub_file_name(self, config: SimulationConfig) -> str: ...

    @abstractmethod
    def compute_histories(self, config: SimulationConfig) -> str: ...

    @abstractmethod
    def prepare_run(
        self,
        config: SimulationConfig,
        rundir: str,
        project_root: str,
    ) -> None: ...

    @abstractmethod
    def execute(
        self,
        config: SimulationConfig,
        rundir: str,
        project_root: str,
    ) -> None: ...
