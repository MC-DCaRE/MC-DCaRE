import os
import sys
from unittest.mock import patch, MagicMock
from typing import List, Tuple

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.simulation_runner import SimulationRunner


class TestRunTopas:
    @patch("src.simulation_runner.subprocess.run")
    def test_calls_subprocess_run_with_correct_args(self, mock_run: MagicMock) -> None:
        SimulationRunner.run_topas("/topas bin/topas file.txt", "/working/dir")
        mock_run.assert_called_once_with(
            "/topas bin/topas file.txt", cwd="/working/dir", shell=True
        )

    @patch("src.simulation_runner.subprocess.run")
    def test_does_not_print_after_execution(
        self, mock_run: MagicMock, capsys: object
    ) -> None:
        SimulationRunner.run_topas("command", "dir")
        captured = capsys.readouterr()
        assert captured.out == ""


class TestRunDicom:
    @patch("src.simulation_runner.subprocess.run")
    def test_calls_run_topas_with_correct_command(self, mock_run: MagicMock) -> None:
        topas_path = "/usr/local/topas/bin/topas"
        rundatadir = "/runfolder/2024-01-01_12-00-00"

        SimulationRunner.run_dicom(topas_path, rundatadir)

        expected_command = topas_path + " " + rundatadir + "/headsourcecode.txt"
        mock_run.assert_called_once_with(expected_command, cwd=rundatadir, shell=True)


class TestRunCtdi:
    @patch("src.simulation_runner.mp.Pool")
    def test_calls_run_topas_for_each_command(self, mock_pool_class: MagicMock) -> None:
        mock_pool = MagicMock()
        mock_pool_class.return_value.__enter__ = MagicMock(return_value=mock_pool)
        mock_pool_class.return_value.__exit__ = MagicMock(return_value=False)

        topas_path = "/usr/local/topas/bin/topas"
        rundatadir = "/runfolder/2024-01-01_12-00-00"
        commands: List[Tuple[str, str]] = [
            (
                topas_path + " " + rundatadir + "/ChamberPlugCentre.txt",
                rundatadir,
            ),
            (
                topas_path + " " + rundatadir + "/ChamberPlugTop.txt",
                rundatadir,
            ),
            (
                topas_path + " " + rundatadir + "/ChamberPlugBottom.txt",
                rundatadir,
            ),
        ]

        SimulationRunner.run_ctdi(topas_path, rundatadir, commands)

        mock_pool.starmap.assert_called_once_with(SimulationRunner.run_topas, commands)


if __name__ == "__main__":
    pytest.main([__file__])
