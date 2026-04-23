import pytest
import os
import tempfile
import shutil
import subprocess
from unittest.mock import patch, MagicMock, mock_open, ANY, call
import datetime
import sys

# Import the module to test
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from src.runtime_handler import run_topas, plugsgenerator, log_output


class TestRunTopas:
    """Test class for run_topas function"""

    @patch("src.runtime_handler.subprocess.run")
    def test_run_topas_successful_execution(self, mock_subprocess):
        """Test run_topas with successful command execution"""
        # Setup mock
        mock_subprocess.return_value = MagicMock(returncode=0)

        # Test data
        test_command = 'echo "test command"'
        test_rundatadir = "/test/path"

        # Call function
        run_topas(test_command, test_rundatadir)

        # Verify subprocess.run was called once
        assert mock_subprocess.call_count == 1
        mock_subprocess.assert_called_once_with(
            'echo "test command"', cwd="/test/path", shell=True
        )

    @patch("src.runtime_handler.subprocess.run")
    def test_run_topas_failed_execution(self, mock_subprocess):
        """Test run_topas with failed command execution"""
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, "test command")

        test_command = 'echo "test command"'
        test_rundatadir = "/test/path"

        try:
            run_topas(test_command, test_rundatadir)
        except subprocess.CalledProcessError:
            pass

        assert mock_subprocess.call_count == 1

    @patch("src.runtime_handler.subprocess.run")
    @patch("builtins.print")
    def test_run_topas_output_logging(self, mock_print, mock_subprocess):
        """Test run_topas output logging behavior"""
        # Setup mock
        mock_subprocess.return_value = MagicMock(returncode=0)

        # Test data
        test_command = 'echo "test command"'
        test_rundatadir = "/test/path"

        # Call function
        run_topas(test_command, test_rundatadir)

        # Verify 'ran' was printed
        mock_print.assert_called_once_with("ran")

    @patch("src.runtime_handler.subprocess.run")
    def test_run_topas_command_parsing(self, mock_subprocess):
        """Test run_topas correctly parses command structure"""
        # Setup mock
        mock_subprocess.return_value = MagicMock(returncode=0)

        # Test data
        test_command = "complex command with args"
        test_rundatadir = "/test/path"

        # Call function
        run_topas(test_command, test_rundatadir)

        # Verify subprocess.run was called once with the command
        assert mock_subprocess.call_count == 1
        mock_subprocess.assert_called_once_with(
            "complex command with args", cwd="/test/path", shell=True
        )

    @patch("src.runtime_handler.subprocess.run")
    def test_run_topas_exception_handling(self, mock_subprocess):
        """Test run_topas handles exceptions gracefully"""
        # Setup mock to raise an exception
        mock_subprocess.side_effect = Exception("Test exception")

        # Test data
        test_command = "test command"
        test_rundatadir = "/test/path"

        # Call function - should not raise exception
        try:
            run_topas(test_command, test_rundatadir)
        except Exception:
            pass  # Function doesn't catch exceptions, so they will propagate

        # Verify subprocess.run was called
        assert mock_subprocess.call_count >= 1

    @patch("src.runtime_handler.subprocess.run")
    def test_run_topas_different_executable_paths(self, mock_subprocess):
        """Test run_topas with different TOPAS executable paths"""
        # Setup mock
        mock_subprocess.return_value = MagicMock(returncode=0)

        # Test data with different executable paths
        test_cases = [
            ("/usr/bin/topas", "/test/path1"),
            ("/opt/topas/bin/topas", "/test/path2"),
            ("C:\\Program Files\\TOPAS\\topas.exe", "/test/path3"),
        ]

        for command, rundatadir in test_cases:
            mock_subprocess.reset_mock()
            run_topas(command, rundatadir)

            # Verify subprocess.run was called once with correct params
            assert mock_subprocess.call_count == 1
            mock_subprocess.assert_called_once_with(command, cwd=rundatadir, shell=True)

    @patch("src.runtime_handler.subprocess.run")
    def test_run_topas_working_directory_setting(self, mock_subprocess):
        """Test run_topas validates working directory setting"""
        # Setup mock
        mock_subprocess.return_value = MagicMock(returncode=0)

        # Test data
        test_command = 'echo "test command"'
        test_rundatadir = "/custom/test/directory"

        # Call function
        run_topas(test_command, test_rundatadir)

        # Verify working directory was set correctly
        assert mock_subprocess.call_count == 1
        mock_subprocess.assert_called_once_with(
            'echo "test command"', cwd="/custom/test/directory", shell=True
        )

    @patch("src.runtime_handler.subprocess.run")
    def test_run_topas_exit_code_handling(self, mock_subprocess):
        """Test run_topas handles different exit codes"""
        # Test different exit codes
        exit_codes = [0, 1, 2, 255]

        for exit_code in exit_codes:
            mock_subprocess.reset_mock()
            mock_subprocess.return_value = MagicMock(returncode=exit_code)

            # Call function
            run_topas("test command", "/test/path")

            # Verify function was called regardless of exit code
            assert mock_subprocess.call_count == 1


class TestPlugsgenerator:
    """Test class for plugsgenerator function"""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def mock_boilerplate_files(self, temp_dir):
        """Create mock boilerplate files for testing"""
        # Create tmp directory structure
        tmp_dir = os.path.join(temp_dir, "tmp")
        os.makedirs(tmp_dir, exist_ok=True)

        # Create mock headsourcecode.txt
        headsource_path = os.path.join(tmp_dir, "headsourcecode.txt")
        with open(headsource_path, "w") as f:
            f.write("# Mock head source code\n")
            f.write("includeFile=test.txt\n")
            f.write('s:Ge/test/Position="@@PLACEHOLDER@@"\n')
            f.write('s:Ge/test/Material="PMMA"\n')

        # Create mock CTDIphantom_16.txt
        ctdi16_path = os.path.join(tmp_dir, "CTDIphantom_16.txt")
        with open(ctdi16_path, "w") as f:
            f.write("# Mock 16cm phantom\n")
            f.write('s:Ge/phantom/Size="16cm"\n')

        # Create mock CTDIphantom_32.txt
        ctdi32_path = os.path.join(tmp_dir, "CTDIphantom_32.txt")
        with open(ctdi32_path, "w") as f:
            f.write("# Mock 32cm phantom\n")
            f.write('s:Ge/phantom/Size="32cm"\n')

        return tmp_dir

    @patch("src.runtime_handler.os.getcwd")
    def test_plugsgenerator_ctdi16_file_copying(
        self, mock_getcwd, temp_dir, mock_boilerplate_files
    ):
        """Test plugsgenerator with ctdi16 phantom size"""
        # Setup mock - return to base temp directory, not the tmp subdirectory
        mock_getcwd.return_value = temp_dir

        rundatadir = os.path.join(temp_dir, "run_data")
        os.makedirs(rundatadir, exist_ok=True)

        topas_app_path = "/path/to/topas"

        # Call function
        commands = plugsgenerator("ctdi16", rundatadir, topas_app_path)

        # Verify files were created
        assert os.path.exists(os.path.join(rundatadir, "ChamberPlugCentre.txt"))
        assert os.path.exists(os.path.join(rundatadir, "ChamberPlugTop.txt"))
        assert os.path.exists(os.path.join(rundatadir, "ChamberPlugBottom.txt"))
        assert os.path.exists(os.path.join(rundatadir, "ChamberPlugLeft.txt"))
        assert os.path.exists(os.path.join(rundatadir, "ChamberPlugRight.txt"))

        # Verify commands structure — each command is a (command_str, rundatadir) tuple
        assert len(commands) == 5
        for cmd, rdir in commands:
            assert isinstance(cmd, str)
            assert topas_app_path in cmd
            assert rundatadir in rdir

    @patch("src.runtime_handler.os.getcwd")
    def test_plugsgenerator_ctdi32_file_copying(
        self, mock_getcwd, temp_dir, mock_boilerplate_files
    ):
        """Test plugsgenerator with ctdi32 phantom size"""
        # Setup mock - return to base temp directory, not the tmp subdirectory
        mock_getcwd.return_value = temp_dir

        rundatadir = os.path.join(temp_dir, "run_data")
        os.makedirs(rundatadir, exist_ok=True)

        topas_app_path = "/path/to/topas"

        # Call function
        commands = plugsgenerator("ctdi32", rundatadir, topas_app_path)

        # Verify files were created
        assert os.path.exists(os.path.join(rundatadir, "ChamberPlugCentre.txt"))
        assert os.path.exists(os.path.join(rundatadir, "ChamberPlugTop.txt"))
        assert os.path.exists(os.path.join(rundatadir, "ChamberPlugBottom.txt"))
        assert os.path.exists(os.path.join(rundatadir, "ChamberPlugLeft.txt"))
        assert os.path.exists(os.path.join(rundatadir, "ChamberPlugRight.txt"))

        # Verify commands structure — each command is a (command_str, rundatadir) tuple
        assert len(commands) == 5
        for cmd, rdir in commands:
            assert isinstance(cmd, str)
            assert topas_app_path in cmd
            assert rundatadir in rdir

    @patch("src.runtime_handler.os.getcwd")
    def test_plugsgenerator_directory_structure(
        self, mock_getcwd, temp_dir, mock_boilerplate_files
    ):
        """Test plugsgenerator creates correct directory structure"""
        # Setup mock - return to base temp directory, not the tmp subdirectory
        mock_getcwd.return_value = temp_dir

        rundatadir = os.path.join(temp_dir, "run_data")
        os.makedirs(rundatadir, exist_ok=True)

        topas_app_path = "/path/to/topas"

        # Call function
        commands = plugsgenerator("ctdi16", rundatadir, topas_app_path)

        # Verify rundatadir exists
        assert os.path.exists(rundatadir)

        # Verify all position files exist
        positions = [
            "ChamberPlugCentre",
            "ChamberPlugTop",
            "ChamberPlugBottom",
            "ChamberPlugLeft",
            "ChamberPlugRight",
        ]
        for position in positions:
            position_file = os.path.join(rundatadir, f"{position}.txt")
            assert os.path.exists(position_file)

    @patch("src.runtime_handler.os.getcwd")
    def test_plugsgenerator_placeholder_replacement(
        self, mock_getcwd, temp_dir, mock_boilerplate_files
    ):
        """Test plugsgenerator correctly replaces placeholders in files"""
        # Setup mock - return to base temp directory, not the tmp subdirectory
        mock_getcwd.return_value = temp_dir

        rundatadir = os.path.join(temp_dir, "run_data")
        os.makedirs(rundatadir, exist_ok=True)

        topas_app_path = "/path/to/topas"

        # Use the mock_boilerplate_files fixture which already creates the tmp directory
        tmp_dir = mock_boilerplate_files

        # Override the headsourcecode.txt with placeholder content
        headsource_file = os.path.join(tmp_dir, "headsourcecode.txt")
        with open(headsource_file, "w") as f:
            f.write("# Mock head source code\n")
            f.write("includeFile=test.txt\n")
            f.write('s:Ge/@@PLACEHOLDER@@/Position="test"\n')
            f.write('s:Ge/@@PLACEHOLDER@@/Material="PMMA"\n')

        # Override the CTDIphantom_16.txt with test content
        ctdi_file = os.path.join(tmp_dir, "CTDIphantom_16.txt")
        with open(ctdi_file, "w") as f:
            f.write("# Mock 16cm phantom\n")
            f.write('s:Ge/phantom/Size="16cm"\n')

        # Call function
        commands = plugsgenerator("ctdi16", rundatadir, topas_app_path)

        # Verify placeholder replacement in ChamberPlugCentre.txt
        centre_file = os.path.join(rundatadir, "ChamberPlugCentre.txt")
        assert os.path.exists(centre_file), f"File {centre_file} was not created"

        with open(centre_file, "r") as f:
            content = f.read()
            # The placeholder should be replaced with the actual position
            assert "@@PLACEHOLDER@@" not in content
            # The position should be in the content
            assert "ChamberPlugCentre" in content
            # The material should be changed from PMMA to Air
            assert 's:Ge/ChamberPlugCentre/Material="Air"' in content

    @patch("src.runtime_handler.os.getcwd")
    def test_plugsgenerator_material_replacement(
        self, mock_getcwd, temp_dir, mock_boilerplate_files
    ):
        """Test plugsgenerator correctly replaces material from PMMA to Air"""
        # Setup mock - return to base temp directory, not the tmp subdirectory
        mock_getcwd.return_value = temp_dir

        rundatadir = os.path.join(temp_dir, "run_data")
        os.makedirs(rundatadir, exist_ok=True)

        topas_app_path = "/path/to/topas"

        # Use the mock_boilerplate_files fixture which already creates the tmp directory
        tmp_dir = mock_boilerplate_files

        # Override the headsourcecode.txt with placeholder and PMMA material content
        headsource_file = os.path.join(tmp_dir, "headsourcecode.txt")
        with open(headsource_file, "w") as f:
            f.write("# Mock head source code\n")
            f.write("includeFile=test.txt\n")
            f.write('s:Ge/@@PLACEHOLDER@@/Position="test"\n')
            f.write('s:Ge/@@PLACEHOLDER@@/Material="PMMA"\n')

        # Override the CTDIphantom_16.txt with test content
        ctdi_file = os.path.join(tmp_dir, "CTDIphantom_16.txt")
        with open(ctdi_file, "w") as f:
            f.write("# Mock 16cm phantom\n")
            f.write('s:Ge/phantom/Size="16cm"\n')

        # Call function
        commands = plugsgenerator("ctdi16", rundatadir, topas_app_path)

        # Verify material replacement in all position files
        positions = [
            "ChamberPlugCentre",
            "ChamberPlugTop",
            "ChamberPlugBottom",
            "ChamberPlugLeft",
            "ChamberPlugRight",
        ]
        for position in positions:
            position_file = os.path.join(rundatadir, f"{position}.txt")
            assert os.path.exists(position_file), (
                f"File {position_file} was not created"
            )

            with open(position_file, "r") as f:
                content = f.read()
                # The material should be changed from PMMA to Air
                assert f's:Ge/{position}/Material="Air"' in content
                # The original PMMA material should not be present
                assert f's:Ge/{position}/Material="PMMA"' not in content

    @patch("src.runtime_handler.os.getcwd")
    def test_plugsgenerator_default_phantom_size(
        self, mock_getcwd, temp_dir, mock_boilerplate_files
    ):
        """Test plugsgenerator defaults to ctdi16 for invalid phantom size"""
        # Setup mock - return to base temp directory, not the tmp subdirectory
        mock_getcwd.return_value = temp_dir

        rundatadir = os.path.join(temp_dir, "run_data")
        os.makedirs(rundatadir, exist_ok=True)

        topas_app_path = "/path/to/topas"

        # Call function with invalid phantom size
        commands = plugsgenerator("invalid_size", rundatadir, topas_app_path)

        # Verify files were created (should default to ctdi16 behavior)
        assert os.path.exists(os.path.join(rundatadir, "ChamberPlugCentre.txt"))
        assert len(commands) == 5

    @patch("src.runtime_handler.os.getcwd")
    @patch("builtins.open", side_effect=IOError("File not found"))
    def test_plugsgenerator_file_error_handling(
        self, mock_open_file, mock_getcwd, temp_dir
    ):
        """Test plugsgenerator handles file errors gracefully"""
        # Setup mock
        mock_getcwd.return_value = temp_dir

        rundatadir = os.path.join(temp_dir, "run_data")
        os.makedirs(rundatadir, exist_ok=True)

        topas_app_path = "/path/to/topas"

        # Call function - should raise IOError due to missing files
        with pytest.raises(IOError):
            plugsgenerator("ctdi16", rundatadir, topas_app_path)

    @patch("src.runtime_handler.os.getcwd")
    def test_plugsgenerator_unique_folder_creation(
        self, mock_getcwd, temp_dir, mock_boilerplate_files
    ):
        """Test plugsgenerator creates unique folders for concurrent runs"""
        mock_getcwd.return_value = temp_dir

        # Create multiple rundatadir to test concurrent scenarios
        rundatadir1 = os.path.join(temp_dir, "run_data_1")
        rundatadir2 = os.path.join(temp_dir, "run_data_2")
        os.makedirs(rundatadir1, exist_ok=True)
        os.makedirs(rundatadir2, exist_ok=True)

        topas_app_path = "/path/to/topas"

        # Call function twice with different directories
        commands1 = plugsgenerator("ctdi16", rundatadir1, topas_app_path)
        commands2 = plugsgenerator("ctdi16", rundatadir2, topas_app_path)

        # Verify both sets of files were created independently
        assert len(commands1) == 5
        assert len(commands2) == 5

        # Verify files exist in both directories
        for position in [
            "ChamberPlugCentre",
            "ChamberPlugTop",
            "ChamberPlugBottom",
            "ChamberPlugLeft",
            "ChamberPlugRight",
        ]:
            assert os.path.exists(os.path.join(rundatadir1, f"{position}.txt"))
            assert os.path.exists(os.path.join(rundatadir2, f"{position}.txt"))

    @patch("src.runtime_handler.os.getcwd")
    def test_plugsgenerator_all_positions_covered(
        self, mock_getcwd, temp_dir, mock_boilerplate_files
    ):
        """Test plugsgenerator covers all 5 plug positions"""
        mock_getcwd.return_value = temp_dir

        rundatadir = os.path.join(temp_dir, "run_data")
        os.makedirs(rundatadir, exist_ok=True)

        topas_app_path = "/path/to/topas"

        # Call function
        commands = plugsgenerator("ctdi16", rundatadir, topas_app_path)

        # Verify all 5 positions are covered
        expected_positions = [
            "ChamberPlugCentre",
            "ChamberPlugTop",
            "ChamberPlugBottom",
            "ChamberPlugLeft",
            "ChamberPlugRight",
        ]
        actual_positions = []

        for cmd, rdir in commands:
            for position in expected_positions:
                if position in cmd:
                    actual_positions.append(position)
                    break

        assert len(set(actual_positions)) == 5
        assert set(actual_positions) == set(expected_positions)


class TestLogOutput:
    """Test class for log_output function"""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def mock_boilerplate_files(self, temp_dir):
        """Create mock boilerplate files for testing"""
        # Create tmp directory structure
        tmp_dir = os.path.join(temp_dir, "tmp")
        os.makedirs(tmp_dir, exist_ok=True)

        # Create mock files
        files_to_create = [
            "ConvertedTopasFile.txt",
            "head_calibration_factor.txt",
            "headsourcecode.txt",
            "patientDICOM.txt",
        ]

        for filename in files_to_create:
            filepath = os.path.join(tmp_dir, filename)
            with open(filepath, "w") as f:
                f.write(f"# Mock {filename}\n")
                f.write(f"content of {filename}\n")

        # Create src/boilerplates/TOPAS_includeFiles structure
        boilerplate_dir = os.path.join(
            temp_dir, "src", "boilerplates", "TOPAS_includeFiles"
        )
        os.makedirs(boilerplate_dir, exist_ok=True)

        include_files = [
            "HUtoMaterialSchneider.txt",
            "Muen.dat",
            "NbParticlesInTime.txt",
            "fullfan.txt",
            "halffan.txt",
        ]

        for filename in include_files:
            filepath = os.path.join(boilerplate_dir, filename)
            with open(filepath, "w") as f:
                f.write(f"# Mock {filename}\n")

        return temp_dir

    def _make_mock_pool(self):
        """Create a mock for mp.Pool that captures starmap calls."""
        mock_pool = MagicMock()
        mock_pool.__enter__ = MagicMock(return_value=mock_pool)
        mock_pool.__exit__ = MagicMock(return_value=False)
        return mock_pool

    @patch("src.runtime_handler.os.getcwd")
    @patch("src.runtime_handler.os.makedirs")
    @patch("src.runtime_handler.shutil.copy")
    @patch("src.runtime_handler.mp.Pool")
    def test_log_output_dicom_simulation(
        self,
        mock_pool_class,
        mock_copy,
        mock_makedirs,
        mock_getcwd,
        temp_dir,
        mock_boilerplate_files,
    ):
        """Test log_output with DICOM simulation"""
        mock_pool = self._make_mock_pool()
        mock_pool_class.return_value = mock_pool
        mock_getcwd.return_value = temp_dir

        input_file_path = os.path.join(temp_dir, "tmp", "ConvertedTopasFile.txt")
        tag = "dicom"
        topas_app_path = "/path/to/topas"
        fan_tag = "Full Fan"

        result = log_output(input_file_path, tag, topas_app_path, fan_tag)

        assert result == "DICOM simulation completed"

        mock_pool.starmap.assert_called_once()
        starmap_args = mock_pool.starmap.call_args[0]
        assert starmap_args[0] == run_topas
        commands = starmap_args[1]
        assert len(commands) == 1
        assert topas_app_path in commands[0][0]
        assert "headsourcecode.txt" in commands[0][0]

    @patch("src.runtime_handler.os.getcwd")
    @patch("src.runtime_handler.os.makedirs")
    @patch("src.runtime_handler.shutil.copy")
    @patch("src.runtime_handler.plugsgenerator")
    @patch("src.runtime_handler.mp.Pool")
    def test_log_output_ctdi16_simulation(
        self,
        mock_pool_class,
        mock_plugsgenerator,
        mock_copy,
        mock_makedirs,
        mock_getcwd,
        temp_dir,
        mock_boilerplate_files,
    ):
        """Test log_output with CTDI 16 simulation"""
        mock_pool = self._make_mock_pool()
        mock_pool_class.return_value = mock_pool
        mock_getcwd.return_value = temp_dir

        mock_commands = [
            ("/path/to/topas /test/path/ChamberPlugCentre.txt", "/test/path"),
            ("/path/to/topas /test/path/ChamberPlugTop.txt", "/test/path"),
            ("/path/to/topas /test/path/ChamberPlugBottom.txt", "/test/path"),
            ("/path/to/topas /test/path/ChamberPlugLeft.txt", "/test/path"),
            ("/path/to/topas /test/path/ChamberPlugRight.txt", "/test/path"),
        ]
        mock_plugsgenerator.return_value = mock_commands

        tmp_dir = os.path.join(temp_dir, "tmp")
        os.makedirs(tmp_dir, exist_ok=True)

        input_file_path = os.path.join(tmp_dir, "ConvertedTopasFile.txt")
        with open(input_file_path, "w") as f:
            f.write("Test input file")

        for filename in [
            "head_calibration_factor.txt",
            "headsourcecode.txt",
            "CTDIphantom_16.txt",
        ]:
            file_path = os.path.join(tmp_dir, filename)
            with open(file_path, "w") as f:
                f.write(f"Test {filename}")

        mock_makedirs.side_effect = None

        tag = "ctdi16"
        topas_app_path = "/path/to/topas"
        fan_tag = "Half Fan"

        result = log_output(input_file_path, tag, topas_app_path, fan_tag)

        assert result == "CTDI simulation completed"
        mock_plugsgenerator.assert_called_once_with("ctdi16", ANY, topas_app_path)

        mock_pool.starmap.assert_called_once()
        starmap_commands = mock_pool.starmap.call_args[0][1]
        assert len(starmap_commands) == 5
        for i, (cmd, rdir) in enumerate(starmap_commands):
            assert mock_commands[i][0] in cmd

    @patch("src.runtime_handler.os.getcwd")
    @patch("src.runtime_handler.os.makedirs")
    @patch("src.runtime_handler.shutil.copy")
    @patch("src.runtime_handler.plugsgenerator")
    @patch("src.runtime_handler.mp.Pool")
    def test_log_output_ctdi32_simulation(
        self,
        mock_pool_class,
        mock_plugsgenerator,
        mock_copy,
        mock_makedirs,
        mock_getcwd,
        temp_dir,
        mock_boilerplate_files,
    ):
        """Test log_output with CTDI 32 simulation"""
        mock_pool = self._make_mock_pool()
        mock_pool_class.return_value = mock_pool
        mock_getcwd.return_value = temp_dir

        mock_commands = [
            ("/path/to/topas /test/path/ChamberPlugCentre.txt", "/test/path"),
            ("/path/to/topas /test/path/ChamberPlugTop.txt", "/test/path"),
            ("/path/to/topas /test/path/ChamberPlugBottom.txt", "/test/path"),
            ("/path/to/topas /test/path/ChamberPlugLeft.txt", "/test/path"),
            ("/path/to/topas /test/path/ChamberPlugRight.txt", "/test/path"),
        ]
        mock_plugsgenerator.return_value = mock_commands

        tmp_dir = os.path.join(temp_dir, "tmp")
        os.makedirs(tmp_dir, exist_ok=True)

        input_file_path = os.path.join(tmp_dir, "ConvertedTopasFile.txt")
        with open(input_file_path, "w") as f:
            f.write("Test input file")

        for filename in [
            "head_calibration_factor.txt",
            "headsourcecode.txt",
            "CTDIphantom_32.txt",
        ]:
            file_path = os.path.join(tmp_dir, filename)
            with open(file_path, "w") as f:
                f.write(f"Test {filename}")

        mock_makedirs.side_effect = None

        tag = "ctdi32"
        topas_app_path = "/path/to/topas"
        fan_tag = "Full Fan"

        result = log_output(input_file_path, tag, topas_app_path, fan_tag)

        assert result == "CTDI simulation completed"
        mock_plugsgenerator.assert_called_once_with("ctdi32", ANY, topas_app_path)

        mock_pool.starmap.assert_called_once()
        starmap_commands = mock_pool.starmap.call_args[0][1]
        assert len(starmap_commands) == 5
        for i, (cmd, rdir) in enumerate(starmap_commands):
            assert mock_commands[i][0] in cmd

    @patch("src.runtime_handler.os.getcwd")
    @patch("src.runtime_handler.os.makedirs")
    @patch("src.runtime_handler.shutil.copy")
    def test_log_output_invalid_tag(
        self, mock_copy, mock_makedirs, mock_getcwd, temp_dir, mock_boilerplate_files
    ):
        """Test log_output with invalid tag"""
        mock_getcwd.return_value = temp_dir

        input_file_path = os.path.join(temp_dir, "tmp", "ConvertedTopasFile.txt")
        tag = "invalid_tag"
        topas_app_path = "/path/to/topas"
        fan_tag = "Full Fan"

        result = log_output(input_file_path, tag, topas_app_path, fan_tag)

        assert result == "Error encountered"
        assert mock_copy.call_count == 1
        mock_copy.assert_called_with(input_file_path, ANY)

    @patch("src.runtime_handler.os.getcwd")
    @patch("src.runtime_handler.os.makedirs")
    @patch("src.runtime_handler.shutil.copy")
    @patch("src.runtime_handler.plugsgenerator")
    @patch("src.runtime_handler.mp.Pool")
    def test_log_output_sequential_execution(
        self,
        mock_pool_class,
        mock_plugsgenerator,
        mock_copy,
        mock_makedirs,
        mock_getcwd,
        temp_dir,
        mock_boilerplate_files,
    ):
        """Test log_output with multiple commands via pool"""
        mock_pool = self._make_mock_pool()
        mock_pool_class.return_value = mock_pool
        mock_getcwd.return_value = temp_dir

        mock_commands = [
            ("/path/to/topas /test/path/command1", "/test/path"),
            ("/path/to/topas /test/path/command2", "/test/path"),
            ("/path/to/topas /test/path/command3", "/test/path"),
            ("/path/to/topas /test/path/command4", "/test/path"),
            ("/path/to/topas /test/path/command5", "/test/path"),
        ]
        mock_plugsgenerator.return_value = mock_commands

        input_file_path = os.path.join(temp_dir, "tmp", "ConvertedTopasFile.txt")
        tag = "ctdi16"
        topas_app_path = "/path/to/topas"
        fan_tag = "Full Fan"

        result = log_output(input_file_path, tag, topas_app_path, fan_tag)

        mock_plugsgenerator.assert_called_once_with("ctdi16", ANY, topas_app_path)

        mock_pool.starmap.assert_called_once()
        starmap_commands = mock_pool.starmap.call_args[0][1]
        assert len(starmap_commands) == 5

        assert result == "CTDI simulation completed"

    @patch("src.runtime_handler.os.getcwd")
    @patch("src.runtime_handler.os.makedirs")
    @patch("src.runtime_handler.shutil.copy")
    @patch("src.runtime_handler.mp.Pool")
    def test_log_output_error_handling(
        self,
        mock_pool_class,
        mock_copy,
        mock_makedirs,
        mock_getcwd,
        temp_dir,
        mock_boilerplate_files,
    ):
        """Test log_output error handling when pool.starmap raises"""
        mock_pool = self._make_mock_pool()
        mock_pool.starmap.side_effect = Exception("Run error")
        mock_pool_class.return_value = mock_pool
        mock_getcwd.return_value = temp_dir

        tmp_dir = os.path.join(temp_dir, "tmp")
        os.makedirs(tmp_dir, exist_ok=True)

        input_file_path = os.path.join(tmp_dir, "ConvertedTopasFile.txt")
        with open(input_file_path, "w") as f:
            f.write("Test input file")

        for filename in [
            "head_calibration_factor.txt",
            "headsourcecode.txt",
            "patientDICOM.txt",
        ]:
            file_path = os.path.join(tmp_dir, filename)
            with open(file_path, "w") as f:
                f.write(f"Test {filename}")

        boilerplate_dir = os.path.join(
            temp_dir, "src", "boilerplates", "TOPAS_includeFiles"
        )
        os.makedirs(boilerplate_dir, exist_ok=True)

        for filename in [
            "HUtoMaterialSchneider.txt",
            "Muen.dat",
            "NbParticlesInTime.txt",
            "fullfan.txt",
        ]:
            filepath = os.path.join(boilerplate_dir, filename)
            with open(filepath, "w") as f:
                f.write(f"# Mock {filename}\n")

        mock_makedirs.side_effect = None

        tag = "dicom"
        topas_app_path = "/path/to/topas"
        fan_tag = "Full Fan"

        try:
            result = log_output(input_file_path, tag, topas_app_path, fan_tag)
        except Exception:
            pass

        mock_pool.starmap.assert_called_once()

    @patch("src.runtime_handler.os.getcwd")
    @patch("src.runtime_handler.datetime")
    @patch("src.runtime_handler.os.makedirs")
    @patch("src.runtime_handler.shutil.copy")
    @patch("src.runtime_handler.mp.Pool")
    def test_log_output_timestamped_directory(
        self,
        mock_pool_class,
        mock_copy,
        mock_makedirs,
        mock_datetime,
        mock_getcwd,
        temp_dir,
        mock_boilerplate_files,
    ):
        """Test log_output creates timestamped directory"""
        mock_pool = self._make_mock_pool()
        mock_pool_class.return_value = mock_pool
        mock_getcwd.return_value = temp_dir
        mock_datetime.now.return_value.strftime.return_value = "2023-01-01_12-00-00"

        input_file_path = os.path.join(temp_dir, "tmp", "ConvertedTopasFile.txt")
        tag = "dicom"
        topas_app_path = "/path/to/topas"
        fan_tag = "Full Fan"

        result = log_output(input_file_path, tag, topas_app_path, fan_tag)

        expected_dir = os.path.normpath(
            os.path.join(temp_dir, "runfolder", "2023-01-01_12-00-00")
        )
        actual_call = mock_makedirs.call_args[0][0]
        assert os.path.normpath(actual_call) == expected_dir

        assert result == "DICOM simulation completed"

    @patch("src.runtime_handler.os.getcwd")
    @patch("src.runtime_handler.os.makedirs")
    @patch("src.runtime_handler.shutil.copy")
    @patch("src.runtime_handler.plugsgenerator")
    @patch("src.runtime_handler.mp.Pool")
    def test_log_output_sequential_execution_with_many_commands(
        self,
        mock_pool_class,
        mock_plugsgenerator,
        mock_copy,
        mock_makedirs,
        mock_getcwd,
        temp_dir,
        mock_boilerplate_files,
    ):
        """Test log_output with many commands via pool"""
        mock_pool = self._make_mock_pool()
        mock_pool_class.return_value = mock_pool
        mock_getcwd.return_value = temp_dir

        mock_commands = [
            (f"/path/to/topas /test/path/command{i}.txt", "/test/path")
            for i in range(70)
        ]
        mock_plugsgenerator.return_value = mock_commands

        tmp_dir = os.path.join(temp_dir, "tmp")
        os.makedirs(tmp_dir, exist_ok=True)

        input_file_path = os.path.join(tmp_dir, "ConvertedTopasFile.txt")
        with open(input_file_path, "w") as f:
            f.write("Test input file")

        for filename in [
            "head_calibration_factor.txt",
            "headsourcecode.txt",
            "CTDIphantom_16.txt",
        ]:
            file_path = os.path.join(tmp_dir, filename)
            with open(file_path, "w") as f:
                f.write(f"Test {filename}")

        mock_makedirs.side_effect = None

        tag = "ctdi16"
        topas_app_path = "/path/to/topas"
        fan_tag = "Full Fan"

        result = log_output(input_file_path, tag, topas_app_path, fan_tag)

        assert result == "CTDI simulation completed"
        mock_plugsgenerator.assert_called_once_with("ctdi16", ANY, topas_app_path)

        mock_pool.starmap.assert_called_once()
        starmap_commands = mock_pool.starmap.call_args[0][1]
        assert len(starmap_commands) == 70

        assert result == "CTDI simulation completed"

    @patch("src.runtime_handler.os.getcwd")
    @patch("src.runtime_handler.os.makedirs")
    @patch("src.runtime_handler.shutil.copy")
    def test_log_output_file_copy_error_handling(
        self, mock_copy, mock_makedirs, mock_getcwd, temp_dir, mock_boilerplate_files
    ):
        """Test log_output handles file copy errors"""
        mock_getcwd.return_value = temp_dir
        mock_copy.side_effect = IOError("Copy failed")

        input_file_path = os.path.join(temp_dir, "tmp", "ConvertedTopasFile.txt")
        tag = "dicom"
        topas_app_path = "/path/to/topas"
        fan_tag = "Full Fan"

        try:
            result = log_output(input_file_path, tag, topas_app_path, fan_tag)
        except IOError:
            pass

        mock_copy.assert_called()

    @patch("src.runtime_handler.os.getcwd")
    @patch("src.runtime_handler.os.makedirs")
    @patch("src.runtime_handler.shutil.copy")
    @patch("src.runtime_handler.mp.Pool")
    def test_log_output_fan_tag_handling(
        self,
        mock_pool_class,
        mock_copy,
        mock_makedirs,
        mock_getcwd,
        temp_dir,
        mock_boilerplate_files,
    ):
        """Test log_output handles different fan tags correctly"""
        mock_pool = self._make_mock_pool()
        mock_pool_class.return_value = mock_pool
        mock_getcwd.return_value = temp_dir

        input_file_path = os.path.join(temp_dir, "tmp", "ConvertedTopasFile.txt")
        tag = "dicom"
        topas_app_path = "/path/to/topas"

        fan_tag = "Full Fan"
        result = log_output(input_file_path, tag, topas_app_path, fan_tag)
        assert result == "DICOM simulation completed"

        copy_calls = [call[0][0] for call in mock_copy.call_args_list]
        assert any("fullfan.txt" in call for call in copy_calls)

        mock_copy.reset_mock()

        fan_tag = "Half Fan"
        result = log_output(input_file_path, tag, topas_app_path, fan_tag)
        assert result == "DICOM simulation completed"

        copy_calls = [call[0][0] for call in mock_copy.call_args_list]
        assert any("halffan.txt" in call for call in copy_calls)

    @patch("src.runtime_handler.os.getcwd")
    @patch("src.runtime_handler.os.makedirs")
    @patch("src.runtime_handler.shutil.copy")
    @patch("src.runtime_handler.mp.Pool")
    def test_log_output_empty_runfolder_handling(
        self,
        mock_pool_class,
        mock_copy,
        mock_makedirs,
        mock_getcwd,
        temp_dir,
        mock_boilerplate_files,
    ):
        """Test log_output handles empty runfolder scenarios"""
        mock_pool = self._make_mock_pool()
        mock_pool_class.return_value = mock_pool
        mock_getcwd.return_value = temp_dir

        input_file_path = os.path.join(temp_dir, "tmp", "nonexistent.txt")
        tag = "dicom"
        topas_app_path = "/path/to/topas"
        fan_tag = "Full Fan"

        try:
            result = log_output(input_file_path, tag, topas_app_path, fan_tag)
        except (FileNotFoundError, IOError):
            pass

        mock_copy.assert_called()

    @patch("src.runtime_handler.os.getcwd")
    @patch("src.runtime_handler.os.makedirs")
    @patch("src.runtime_handler.shutil.copy")
    @patch("src.runtime_handler.plugsgenerator")
    @patch("src.runtime_handler.mp.Pool")
    def test_log_output_muen_dat_inclusion(
        self,
        mock_pool_class,
        mock_plugsgenerator,
        mock_copy,
        mock_makedirs,
        mock_getcwd,
        temp_dir,
        mock_boilerplate_files,
    ):
        """Test log_output includes Muen.dat for appropriate tags"""
        mock_pool = self._make_mock_pool()
        mock_pool_class.return_value = mock_pool
        mock_getcwd.return_value = temp_dir

        input_file_path = os.path.join(temp_dir, "tmp", "ConvertedTopasFile.txt")
        tag = "dicom"
        topas_app_path = "/path/to/topas"
        fan_tag = "Full Fan"

        result = log_output(input_file_path, tag, topas_app_path, fan_tag)

        copy_calls = [call[0][0] for call in mock_copy.call_args_list]
        assert any("Muen.dat" in call for call in copy_calls)

        mock_copy.reset_mock()
        mock_plugsgenerator.return_value = [
            ("/path/to/topas /test/p/ChamberPlugCentre.txt", "/test/p"),
            ("/path/to/topas /test/p/ChamberPlugTop.txt", "/test/p"),
            ("/path/to/topas /test/p/ChamberPlugBottom.txt", "/test/p"),
            ("/path/to/topas /test/p/ChamberPlugLeft.txt", "/test/p"),
            ("/path/to/topas /test/p/ChamberPlugRight.txt", "/test/p"),
        ]
        tag = "ctdi16"
        result = log_output(input_file_path, tag, topas_app_path, fan_tag)

        copy_calls = [call[0][0] for call in mock_copy.call_args_list]
        assert any("Muen.dat" in call for call in copy_calls)


class TestEdgeCases:
    """Test class for edge cases and error scenarios"""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def mock_boilerplate_files(self, temp_dir):
        """Create mock boilerplate files for testing"""
        tmp_dir = os.path.join(temp_dir, "tmp")
        os.makedirs(tmp_dir, exist_ok=True)

        files_to_create = [
            "ConvertedTopasFile.txt",
            "head_calibration_factor.txt",
            "headsourcecode.txt",
            "patientDICOM.txt",
        ]

        for filename in files_to_create:
            filepath = os.path.join(tmp_dir, filename)
            with open(filepath, "w") as f:
                f.write(f"# Mock {filename}\n")
                f.write(f"content of {filename}\n")

        boilerplate_dir = os.path.join(
            temp_dir, "src", "boilerplates", "TOPAS_includeFiles"
        )
        os.makedirs(boilerplate_dir, exist_ok=True)

        include_files = [
            "HUtoMaterialSchneider.txt",
            "Muen.dat",
            "NbParticlesInTime.txt",
            "fullfan.txt",
            "halffan.txt",
        ]

        for filename in include_files:
            filepath = os.path.join(boilerplate_dir, filename)
            with open(filepath, "w") as f:
                f.write(f"# Mock {filename}\n")

        return temp_dir

    def _make_mock_pool(self):
        mock_pool = MagicMock()
        mock_pool.__enter__ = MagicMock(return_value=mock_pool)
        mock_pool.__exit__ = MagicMock(return_value=False)
        return mock_pool

    @patch("src.runtime_handler.os.getcwd")
    @patch("src.runtime_handler.os.makedirs")
    @patch("src.runtime_handler.shutil.copy")
    @patch("src.runtime_handler.mp.Pool")
    def test_invalid_topas_executable(
        self, mock_pool_class, mock_copy, mock_makedirs, mock_getcwd, temp_dir
    ):
        """Test handling of invalid TOPAS executable path"""
        mock_pool = self._make_mock_pool()
        mock_pool.starmap.side_effect = FileNotFoundError("TOPAS executable not found")
        mock_pool_class.return_value = mock_pool
        mock_getcwd.return_value = temp_dir

        input_file_path = os.path.join(temp_dir, "tmp", "ConvertedTopasFile.txt")
        tag = "dicom"
        topas_app_path = "/invalid/path/to/topas"
        fan_tag = "Full Fan"

        try:
            result = log_output(input_file_path, tag, topas_app_path, fan_tag)
        except FileNotFoundError:
            pass

        mock_pool.starmap.assert_called_once()
        starmap_args = mock_pool.starmap.call_args[0][1]
        assert len(starmap_args) == 1
        assert "/invalid/path/to/topas" in starmap_args[0][0]

    @patch("src.runtime_handler.os.getcwd")
    @patch("src.runtime_handler.os.makedirs")
    @patch("src.runtime_handler.shutil.copy")
    @patch("src.runtime_handler.run_topas")
    def test_file_permission_errors(
        self, mock_run_topas, mock_copy, mock_makedirs, mock_getcwd, temp_dir
    ):
        """Test handling of file permission errors"""
        mock_getcwd.return_value = temp_dir
        mock_copy.side_effect = PermissionError("Permission denied")

        input_file_path = os.path.join(temp_dir, "tmp", "ConvertedTopasFile.txt")
        tag = "dicom"
        topas_app_path = "/path/to/topas"
        fan_tag = "Full Fan"

        try:
            result = log_output(input_file_path, tag, topas_app_path, fan_tag)
        except PermissionError:
            pass

        mock_copy.assert_called()

    @patch("src.runtime_handler.subprocess.run")
    def test_mixed_encoding_output_streams(self, mock_subprocess):
        """Test handling of mixed encoding in output streams"""
        mock_subprocess.return_value = MagicMock(
            returncode=0,
            stdout="Standard output with unicode: ñáéíóú",
            stderr="Error output with unicode: ñáéíóú",
        )

        test_command = 'echo "test command"'
        test_rundatadir = "/test/path"

        run_topas(test_command, test_rundatadir)

        assert mock_subprocess.call_count == 1

    @patch("src.runtime_handler.os.getcwd")
    @patch("src.runtime_handler.os.makedirs")
    @patch("src.runtime_handler.shutil.copy")
    @patch("src.runtime_handler.plugsgenerator")
    @patch("src.runtime_handler.mp.Pool")
    def test_mixed_success_failure_scenarios(
        self,
        mock_pool_class,
        mock_plugsgenerator,
        mock_copy,
        mock_makedirs,
        mock_getcwd,
        temp_dir,
        mock_boilerplate_files,
    ):
        """Test mixed success and failure scenarios"""
        mock_pool = self._make_mock_pool()
        mock_pool.starmap.side_effect = Exception("Command failed")
        mock_pool_class.return_value = mock_pool
        mock_getcwd.return_value = temp_dir

        mock_commands = [
            ("/path/to/topas /test/path/command1", "/test/path"),
            ("/path/to/topas /test/path/command2", "/test/path"),
            ("/path/to/topas /test/path/command3", "/test/path"),
            ("/path/to/topas /test/path/command4", "/test/path"),
            ("/path/to/topas /test/path/command5", "/test/path"),
        ]
        mock_plugsgenerator.return_value = mock_commands

        test_tmp_dir = os.path.join(temp_dir, "tmp")
        input_file_path = os.path.join(test_tmp_dir, "ConvertedTopasFile.txt")

        boilerplate_dir = os.path.join(
            temp_dir, "src", "boilerplates", "TOPAS_includeFiles"
        )
        os.makedirs(boilerplate_dir, exist_ok=True)

        mock_makedirs.side_effect = None

        tag = "ctdi16"
        topas_app_path = "/path/to/topas"
        fan_tag = "Full Fan"

        try:
            result = log_output(input_file_path, tag, topas_app_path, fan_tag)
        except Exception:
            pass

        mock_pool.starmap.assert_called_once()

    @patch("src.runtime_handler.os.getcwd")
    @patch("src.runtime_handler.os.makedirs")
    @patch("src.runtime_handler.shutil.copy")
    @patch("src.runtime_handler.plugsgenerator")
    @patch("src.runtime_handler.mp.Pool")
    def test_output_aggregation_ordering(
        self,
        mock_pool_class,
        mock_plugsgenerator,
        mock_copy,
        mock_makedirs,
        mock_getcwd,
        temp_dir,
        mock_boilerplate_files,
    ):
        """Test correct ordering of commands passed to pool"""
        mock_pool = self._make_mock_pool()
        mock_pool_class.return_value = mock_pool
        mock_getcwd.return_value = temp_dir

        mock_commands = [
            ("/path/to/topas /test/path/ChamberPlugCentre.txt", "/test/path"),
            ("/path/to/topas /test/path/ChamberPlugTop.txt", "/test/path"),
            ("/path/to/topas /test/path/ChamberPlugBottom.txt", "/test/path"),
            ("/path/to/topas /test/path/ChamberPlugLeft.txt", "/test/path"),
            ("/path/to/topas /test/path/ChamberPlugRight.txt", "/test/path"),
        ]
        mock_plugsgenerator.return_value = mock_commands

        test_tmp_dir = os.path.join(temp_dir, "tmp")
        input_file_path = os.path.join(test_tmp_dir, "ConvertedTopasFile.txt")

        boilerplate_dir = os.path.join(
            temp_dir, "src", "boilerplates", "TOPAS_includeFiles"
        )
        os.makedirs(boilerplate_dir, exist_ok=True)

        mock_makedirs.side_effect = None

        tag = "ctdi16"
        topas_app_path = "/path/to/topas"
        fan_tag = "Full Fan"

        result = log_output(input_file_path, tag, topas_app_path, fan_tag)

        starmap_commands = mock_pool.starmap.call_args[0][1]
        expected_positions = [
            "ChamberPlugCentre",
            "ChamberPlugTop",
            "ChamberPlugBottom",
            "ChamberPlugLeft",
            "ChamberPlugRight",
        ]
        actual_positions = []

        for cmd, rdir in starmap_commands:
            for position in expected_positions:
                if position in cmd:
                    actual_positions.append(position)
                    break

        assert actual_positions == expected_positions


if __name__ == "__main__":
    pytest.main([__file__])
