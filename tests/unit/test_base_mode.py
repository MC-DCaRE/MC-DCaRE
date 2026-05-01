from __future__ import annotations

import os
import sys
from typing import Any

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.config import ImagingConfig, SimulationConfig
from src.modes.base import SimulationMode


@pytest.fixture
def fake_project(tmp_path: Any) -> Any:
    include_dir = os.path.join(
        str(tmp_path), "src", "boilerplates", "TOPAS_includeFiles"
    )
    tmp_dir = os.path.join(str(tmp_path), "tmp")
    os.makedirs(include_dir)
    os.makedirs(tmp_dir)

    for name in ["Muen.dat", "NbParticlesInTime.txt"]:
        with open(os.path.join(include_dir, name), "w") as f:
            f.write(name + " content\n")

    for name in ["fullfan.txt", "halffan.txt"]:
        with open(os.path.join(include_dir, name), "w") as f:
            f.write(name + " content\n")

    for name in ["ConvertedTopasFile.txt", "head_calibration_factor.txt"]:
        with open(os.path.join(tmp_dir, name), "w") as f:
            f.write(name + " content\n")

    return tmp_path


class TestCopyCommonFiles:
    def _run(
        self,
        fake_project: Any,
        config: SimulationConfig,
    ) -> str:
        rundir = os.path.join(str(fake_project), "rundir")
        os.makedirs(rundir, exist_ok=True)
        SimulationMode.copy_common_files(rundir, config, str(fake_project))
        return rundir

    def test_copies_muen_dat(self, fake_project: Any) -> None:
        config = SimulationConfig()
        rundir = self._run(fake_project, config)
        assert os.path.isfile(os.path.join(rundir, "Muen.dat"))

    def test_copies_nb_particles(self, fake_project: Any) -> None:
        config = SimulationConfig()
        rundir = self._run(fake_project, config)
        assert os.path.isfile(os.path.join(rundir, "NbParticlesInTime.txt"))

    def test_copies_converted_topas(self, fake_project: Any) -> None:
        config = SimulationConfig()
        rundir = self._run(fake_project, config)
        assert os.path.isfile(os.path.join(rundir, "ConvertedTopasFile.txt"))

    def test_copies_calibration_factor(self, fake_project: Any) -> None:
        config = SimulationConfig()
        rundir = self._run(fake_project, config)
        assert os.path.isfile(os.path.join(rundir, "head_calibration_factor.txt"))

    def test_copies_fullfan_for_full_fan(self, fake_project: Any) -> None:
        config = SimulationConfig(
            imaging=ImagingConfig(fan_mode="Full Fan"),
        )
        rundir = self._run(fake_project, config)
        assert os.path.isfile(os.path.join(rundir, "fullfan.txt"))

    def test_copies_halffan_for_half_fan(self, fake_project: Any) -> None:
        config = SimulationConfig(
            imaging=ImagingConfig(fan_mode="Half Fan"),
        )
        rundir = self._run(fake_project, config)
        assert os.path.isfile(os.path.join(rundir, "halffan.txt"))

    def test_no_fan_file_for_unknown_mode(self, fake_project: Any) -> None:
        config = SimulationConfig(
            imaging=ImagingConfig(fan_mode="Unknown Mode"),
        )
        rundir = self._run(fake_project, config)
        assert not os.path.isfile(os.path.join(rundir, "fullfan.txt"))
        assert not os.path.isfile(os.path.join(rundir, "halffan.txt"))
        assert os.path.isfile(os.path.join(rundir, "Muen.dat"))
        assert os.path.isfile(os.path.join(rundir, "NbParticlesInTime.txt"))
        assert os.path.isfile(os.path.join(rundir, "ConvertedTopasFile.txt"))
        assert os.path.isfile(os.path.join(rundir, "head_calibration_factor.txt"))
