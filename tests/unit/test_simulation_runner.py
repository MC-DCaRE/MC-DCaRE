from __future__ import annotations

import os
import sys
from unittest.mock import MagicMock, mock_open, patch
from typing import List, Tuple

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.simulation_runner import SimulationRunner


class TestRunTopas:
    @patch("src.simulation_runner.subprocess.run")
    def test_calls_subprocess_run_without_log_path(self, mock_run: MagicMock) -> None:
        mock_run.return_value.returncode = 0
        SimulationRunner.run_topas(["/topas", "file.txt"], "/working/dir")
        mock_run.assert_called_once_with(["/topas", "file.txt"], cwd="/working/dir")

    @patch("src.simulation_runner.subprocess.run")
    def test_does_not_print_after_execution(
        self, mock_run: MagicMock, capsys: object
    ) -> None:
        mock_run.return_value.returncode = 0
        SimulationRunner.run_topas(["command"], "dir")
        captured = capsys.readouterr()
        assert captured.out == ""

    @patch("src.simulation_runner.subprocess.run")
    def test_raises_on_nonzero_return_code(self, mock_run: MagicMock) -> None:
        mock_run.return_value.returncode = 1
        with pytest.raises(RuntimeError, match="return code 1"):
            SimulationRunner.run_topas(["bad_command"], "/dir")

    @patch("src.simulation_runner.subprocess.run")
    def test_succeeds_on_zero_return_code(self, mock_run: MagicMock) -> None:
        mock_run.return_value.returncode = 0
        SimulationRunner.run_topas(["command"], "/dir")

    @patch("src.simulation_runner.subprocess.Popen")
    def test_with_log_path_captures_output(self, mock_popen: MagicMock) -> None:
        mock_proc = MagicMock()
        mock_proc.stdout = iter(["line1\n", "line2\n"])
        mock_proc.wait.return_value = None
        mock_proc.returncode = 0
        mock_popen.return_value = mock_proc
        m = mock_open()
        with patch("builtins.open", m):
            SimulationRunner.run_topas(
                ["/topas", "file.txt"], "/dir", log_path="/dir/topas_test.log"
            )
        mock_popen.assert_called_once_with(
            ["/topas", "file.txt"],
            cwd="/dir",
            stdout=-1,
            stderr=-2,
            text=True,
        )

    @patch("src.simulation_runner.subprocess.Popen")
    def test_with_log_path_raises_on_failure(self, mock_popen: MagicMock) -> None:
        mock_proc = MagicMock()
        mock_proc.stdout = iter(["error\n"])
        mock_proc.wait.return_value = None
        mock_proc.returncode = 1
        mock_popen.return_value = mock_proc
        m = mock_open()
        with patch("builtins.open", m):
            with pytest.raises(RuntimeError, match="return code 1"):
                SimulationRunner.run_topas(
                    ["/topas", "file.txt"], "/dir", log_path="/dir/test.log"
                )


class TestRunDicom:
    @patch("src.simulation_runner.subprocess.Popen")
    def test_calls_popen_with_correct_command(self, mock_popen: MagicMock) -> None:
        mock_proc = MagicMock()
        mock_proc.stdout = iter([])
        mock_proc.wait.return_value = None
        mock_proc.returncode = 0
        mock_popen.return_value = mock_proc
        topas_path = "/usr/local/topas/bin/topas"
        rundatadir = "/runfolder/2024-01-01_12-00-00"
        m = mock_open()
        with patch("builtins.open", m):
            SimulationRunner.run_dicom(topas_path, rundatadir)
        expected_command = [topas_path, rundatadir + "/headsourcecode.txt"]
        mock_popen.assert_called_once_with(
            expected_command,
            cwd=rundatadir,
            stdout=-1,
            stderr=-2,
            text=True,
        )


class TestRunCtdi:
    @patch("src.simulation_runner.mp.Pool")
    def test_calls_run_topas_with_log_paths(self, mock_pool_class: MagicMock) -> None:
        mock_pool = MagicMock()
        mock_pool_class.return_value.__enter__ = MagicMock(return_value=mock_pool)
        mock_pool_class.return_value.__exit__ = MagicMock(return_value=False)

        topas_path = "/usr/local/topas/bin/topas"
        rundatadir = "/runfolder/2024-01-01_12-00-00"
        commands: List[Tuple[List[str], str]] = [
            (
                [topas_path, rundatadir + "/ChamberPlugCentre.txt"],
                rundatadir,
            ),
            (
                [topas_path, rundatadir + "/ChamberPlugTop.txt"],
                rundatadir,
            ),
        ]

        SimulationRunner.run_ctdi(topas_path, rundatadir, commands)

        expected_logged = [
            (
                [topas_path, rundatadir + "/ChamberPlugCentre.txt"],
                rundatadir,
                rundatadir + "/topas_ChamberPlugCentre.log",
            ),
            (
                [topas_path, rundatadir + "/ChamberPlugTop.txt"],
                rundatadir,
                rundatadir + "/topas_ChamberPlugTop.log",
            ),
        ]
        mock_pool.starmap.assert_called_once_with(
            SimulationRunner.run_topas, expected_logged
        )


if __name__ == "__main__":
    pytest.main([__file__])
