"""Executes TOPAS Monte Carlo simulations as subprocesses."""

from __future__ import annotations

import logging
import os
import subprocess
from typing import List, Optional

logger = logging.getLogger(__name__)

_PID_FILENAME = "topas.pid"


class SimulationRunner:
    """Launches TOPAS processes for DICOM and CTDI simulation modes."""

    @staticmethod
    def validate_topas_binary(topas_path: str) -> None:
        """Pre-flight validation of the TOPAS binary path.

        Checks that the binary exists, is a regular file, and is executable.
        This should be called before spawning multiprocessing pools so that
        configuration errors are caught early with a clear message.

        Args:
            topas_path: Path to the TOPAS executable.

        Raises:
            FileNotFoundError: If the binary does not exist or is not a file.
            PermissionError: If the binary is not executable.
        """
        if not os.path.exists(topas_path):
            raise FileNotFoundError(
                "TOPAS binary not found at: {}\n"
                "Please verify the topas_path in your configuration points to "
                "a valid TOPAS installation.".format(topas_path)
            )
        if not os.path.isfile(topas_path):
            raise FileNotFoundError(
                "TOPAS path is not a regular file: {}\n"
                "Please verify the topas_path points to the TOPAS executable "
                "binary, not a directory.".format(topas_path)
            )
        if not os.access(topas_path, os.X_OK):
            raise PermissionError(
                "TOPAS binary is not executable: {}\n"
                "Fix with: chmod +x {}\n"
                "If the binary is executable but still fails, check for missing "
                "shared libraries with: ldd {}".format(
                    topas_path, topas_path, topas_path
                )
            )

    @staticmethod
    def run_topas(
        command: List[str],
        working_dir: str,
        log_path: Optional[str] = None,
        timeout: int = 3600,
        detach: bool = False,
    ) -> None:
        """Execute a single TOPAS command and check its return code.

        Args:
            command: TOPAS executable path and argument list.
            working_dir: Working directory for the subprocess.
            log_path: If provided, capture stdout+stderr to this file in real time.
            timeout: Maximum execution time in seconds (default 1 hour).
            detach: If True, spawn in a new session and return immediately.
                Writes ``topas.pid`` to *working_dir* so the process can be
                monitored externally.

        Raises:
            RuntimeError: If TOPAS exits with a non-zero return code or times out.
        """
        logger.info("Running TOPAS: %s in %s", " ".join(command), working_dir)

        if detach:
            SimulationRunner._spawn_detached(command, working_dir, log_path)
            return

        if log_path is not None:
            proc = subprocess.Popen(
                command,
                cwd=working_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            with open(log_path, "w", encoding="utf-8") as log_file:
                if proc.stdout is not None:
                    for line in proc.stdout:
                        log_file.write(line)
                        log_file.flush()
                try:
                    proc.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    proc.terminate()
                    proc.wait(timeout=10)
                    raise RuntimeError(
                        "TOPAS process timed out after {}s".format(timeout)
                    )
            returncode = proc.returncode
        else:
            result = subprocess.run(command, cwd=working_dir)
            returncode = result.returncode

        if returncode != 0:
            logger.error("TOPAS exited with code %d: %s", returncode, command)
            if returncode == 127:
                raise RuntimeError(
                    "TOPAS process failed with return code 127 (command not found).\n"
                    "This typically means one of the following:\n"
                    "  - The TOPAS binary does not exist at the specified path\n"
                    "  - The binary lacks execute permission (run: chmod +x <path>)\n"
                    "  - Required shared libraries are missing (run: ldd <path>)\n"
                    "  - The dynamic linker / interpreter is missing\n"
                    "Command attempted: {}".format(" ".join(command))
                )
            raise RuntimeError(
                "TOPAS process failed with return code {}".format(returncode)
            )

    @staticmethod
    def _spawn_detached(
        command: List[str],
        working_dir: str,
        log_path: Optional[str] = None,
    ) -> None:
        """Spawn TOPAS in a new session, write PID file, and return."""
        log_dest = log_path or os.path.join(working_dir, "topas_detached.log")
        log_fh = open(log_dest, "w", encoding="utf-8")  # noqa: SIM115
        proc = subprocess.Popen(
            command,
            cwd=working_dir,
            stdout=log_fh,
            stderr=log_fh,
            start_new_session=True,
        )
        pid_path = os.path.join(working_dir, _PID_FILENAME)
        with open(pid_path, "w", encoding="utf-8") as f:
            f.write(str(proc.pid))
        logger.info("TOPAS detached (pid=%d). PID file: %s", proc.pid, pid_path)

    @staticmethod
    def is_running(working_dir: str) -> bool:
        """Check whether a detached TOPAS process is still running.

        Reads ``topas.pid`` from *working_dir* and checks if the process
        is alive.  Returns False if the PID file is missing or the process
        has exited.
        """
        pid_path = os.path.join(working_dir, _PID_FILENAME)
        if not os.path.isfile(pid_path):
            return False
        try:
            pid = int(open(pid_path, encoding="utf-8").read().strip())
        except (ValueError, OSError):
            return False
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        except PermissionError:
            return True
        return True

    @staticmethod
    def run_dicom(topas_path: str, rundatadir: str, detach: bool = False) -> None:
        """Run a single DICOM patient simulation."""
        SimulationRunner.validate_topas_binary(topas_path)
        command: List[str] = [
            topas_path,
            os.path.join(rundatadir, "headsourcecode.txt"),
        ]
        log_path = os.path.join(rundatadir, "topas_dicom.log")
        logger.info("Starting DICOM simulation")
        SimulationRunner.run_topas(command, rundatadir, log_path, detach=detach)

    @staticmethod
    def run_phantom(topas_path: str, rundatadir: str, detach: bool = False) -> None:
        """Run a single ICRP 145 phantom simulation."""
        SimulationRunner.validate_topas_binary(topas_path)
        command: List[str] = [
            topas_path,
            os.path.join(rundatadir, "headsourcecode.txt"),
        ]
        log_path = os.path.join(rundatadir, "topas_phantom.log")
        logger.info("Starting ICRP 145 phantom simulation")
        SimulationRunner.run_topas(command, rundatadir, log_path, detach=detach)

    @staticmethod
    def run_ctdi(
        topas_path: str,
        rundatadir: str,
        param_file: str,
        detach: bool = False,
    ) -> None:
        """Run a single CTDI simulation scoring all plug positions via parallel worlds.

        Args:
            topas_path: Path to the TOPAS executable.
            rundatadir: Run data directory for outputs.
            param_file: Path to the single TOPAS parameter file.
            detach: If True, spawn in background and return immediately.
        """
        SimulationRunner.validate_topas_binary(topas_path)
        command: List[str] = [topas_path, param_file]
        log_path = os.path.join(rundatadir, "topas_ctdi.log")
        logger.info("Starting CTDI simulation (parallel worlds)")
        SimulationRunner.run_topas(command, rundatadir, log_path, detach=detach)
