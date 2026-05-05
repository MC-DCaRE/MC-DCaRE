from __future__ import annotations

import os
import sys
from unittest.mock import MagicMock, mock_open, patch

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
    @patch("src.simulation_runner.SimulationRunner.validate_topas_binary")
    def test_calls_popen_with_correct_command(
        self, mock_validate: MagicMock, mock_popen: MagicMock
    ) -> None:
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
        mock_validate.assert_called_once_with(topas_path)
        expected_command = [topas_path, rundatadir + "/headsourcecode.txt"]
        mock_popen.assert_called_once_with(
            expected_command,
            cwd=rundatadir,
            stdout=-1,
            stderr=-2,
            text=True,
        )


class TestRunCtdi:
    @patch("src.simulation_runner.subprocess.Popen")
    @patch("src.simulation_runner.SimulationRunner.validate_topas_binary")
    def test_calls_run_topas_with_single_command(
        self, mock_validate: MagicMock, mock_popen: MagicMock
    ) -> None:
        mock_proc = MagicMock()
        mock_proc.stdout = iter([])
        mock_proc.wait.return_value = None
        mock_proc.returncode = 0
        mock_popen.return_value = mock_proc
        topas_path = "/usr/local/topas/bin/topas"
        rundatadir = "/runfolder/2024-01-01_12-00-00"
        param_file = rundatadir + "/CTDI_all_positions.txt"
        m = mock_open()
        with patch("builtins.open", m):
            SimulationRunner.run_ctdi(topas_path, rundatadir, param_file)
        mock_validate.assert_called_once_with(topas_path)
        expected_command = [topas_path, param_file]
        mock_popen.assert_called_once_with(
            expected_command,
            cwd=rundatadir,
            stdout=-1,
            stderr=-2,
            text=True,
        )


class TestValidateTopasBinary:
    @patch("src.simulation_runner.os.access", return_value=True)
    @patch("src.simulation_runner.os.path.isfile", return_value=True)
    @patch("src.simulation_runner.os.path.exists", return_value=True)
    def test_passes_for_valid_binary(
        self,
        mock_exists: MagicMock,
        mock_isfile: MagicMock,
        mock_access: MagicMock,
    ) -> None:
        SimulationRunner.validate_topas_binary("/usr/local/topas/bin/topas")
        mock_exists.assert_called_once_with("/usr/local/topas/bin/topas")
        mock_isfile.assert_called_once_with("/usr/local/topas/bin/topas")
        mock_access.assert_called_once_with(
            "/usr/local/topas/bin/topas", os.X_OK
        )

    @patch("src.simulation_runner.os.path.exists", return_value=False)
    def test_raises_file_not_found_when_path_missing(
        self, mock_exists: MagicMock
    ) -> None:
        with pytest.raises(FileNotFoundError, match="TOPAS binary not found"):
            SimulationRunner.validate_topas_binary("/nonexistent/topas")

    @patch("src.simulation_runner.os.path.isfile", return_value=False)
    @patch("src.simulation_runner.os.path.exists", return_value=True)
    def test_raises_file_not_found_when_not_a_file(
        self, mock_exists: MagicMock, mock_isfile: MagicMock
    ) -> None:
        with pytest.raises(FileNotFoundError, match="not a regular file"):
            SimulationRunner.validate_topas_binary("/some/directory")

    @patch("src.simulation_runner.os.access", return_value=False)
    @patch("src.simulation_runner.os.path.isfile", return_value=True)
    @patch("src.simulation_runner.os.path.exists", return_value=True)
    def test_raises_permission_error_when_not_executable(
        self,
        mock_exists: MagicMock,
        mock_isfile: MagicMock,
        mock_access: MagicMock,
    ) -> None:
        with pytest.raises(PermissionError, match="not executable"):
            SimulationRunner.validate_topas_binary("/topas/noexec")


class TestExitCode127:
    @patch("src.simulation_runner.subprocess.run")
    def test_exit_code_127_raises_with_actionable_message(
        self, mock_run: MagicMock
    ) -> None:
        mock_run.return_value.returncode = 127
        with pytest.raises(RuntimeError, match="command not found") as exc_info:
            SimulationRunner.run_topas(["/bad/topas", "file.txt"], "/dir")
        error_msg = str(exc_info.value)
        assert "chmod +x" in error_msg
        assert "ldd" in error_msg
        assert "/bad/topas file.txt" in error_msg

    @patch("src.simulation_runner.subprocess.Popen")
    def test_exit_code_127_with_log_path_raises_with_actionable_message(
        self, mock_popen: MagicMock
    ) -> None:
        mock_proc = MagicMock()
        mock_proc.stdout = iter(["error\n"])
        mock_proc.wait.return_value = None
        mock_proc.returncode = 127
        mock_popen.return_value = mock_proc
        m = mock_open()
        with patch("builtins.open", m):
            with pytest.raises(RuntimeError, match="command not found") as exc_info:
                SimulationRunner.run_topas(
                    ["/bad/topas", "file.txt"], "/dir", log_path="/dir/test.log"
                )
        error_msg = str(exc_info.value)
        assert "chmod +x" in error_msg
        assert "ldd" in error_msg

    @patch("src.simulation_runner.subprocess.run")
    def test_other_nonzero_exit_code_keeps_generic_message(
        self, mock_run: MagicMock
    ) -> None:
        mock_run.return_value.returncode = 42
        with pytest.raises(RuntimeError, match="return code 42") as exc_info:
            SimulationRunner.run_topas(["/topas", "file.txt"], "/dir")
        # Should NOT contain the exit code 127 specific guidance
        assert "command not found" not in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__])
