import os
import re
import sys
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.run_preparer import RunPreparer
from src.config import SimulationConfig


class TestCreateRunfolder:
    def test_creates_directory_under_runfolder(self, tmp_path: object) -> None:
        preparer = RunPreparer(str(tmp_path))
        rundatadir = preparer._create_runfolder()
        assert os.path.isdir(rundatadir)
        assert rundatadir.startswith(os.path.join(str(tmp_path), "runfolder"))

    def test_directory_name_matches_timestamp_format(self, tmp_path: object) -> None:
        preparer = RunPreparer(str(tmp_path))
        rundatadir = preparer._create_runfolder()
        dirname = os.path.basename(rundatadir)
        assert re.match(r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}", dirname)


class TestCopyCommonFiles:
    def test_copies_converted_topas_file(self, tmp_path: object) -> None:
        preparer = RunPreparer(str(tmp_path))
        config = SimulationConfig()
        rundatadir = str(tmp_path / "rundata")
        os.makedirs(rundatadir)
        os.makedirs(os.path.join(str(tmp_path), "tmp"), exist_ok=True)

        converted_src = os.path.join(str(tmp_path), "tmp", "ConvertedTopasFile.txt")
        with open(converted_src, "w") as f:
            f.write("test")

        with patch("src.run_preparer.shutil.copy") as mock_copy:
            preparer._copy_common_files(rundatadir, config)
            mock_copy.assert_any_call(converted_src, rundatadir)

    def test_copies_calibration_file(self, tmp_path: object) -> None:
        preparer = RunPreparer(str(tmp_path))
        config = SimulationConfig()
        rundatadir = str(tmp_path / "rundata")
        os.makedirs(rundatadir)
        os.makedirs(os.path.join(str(tmp_path), "tmp"), exist_ok=True)

        calib_src = os.path.join(str(tmp_path), "tmp", "head_calibration_factor.txt")
        with open(calib_src, "w") as f:
            f.write("test")

        with patch("src.run_preparer.shutil.copy") as mock_copy:
            preparer._copy_common_files(rundatadir, config)
            mock_copy.assert_any_call(calib_src, rundatadir)

    def test_copies_fullfan_for_full_fan_mode(self, tmp_path: object) -> None:
        preparer = RunPreparer(str(tmp_path))
        config = SimulationConfig()
        config.imaging.fan_mode = "Full Fan"
        rundatadir = str(tmp_path / "rundata")
        os.makedirs(rundatadir)

        include_dir = os.path.join(
            str(tmp_path), "src", "boilerplates", "TOPAS_includeFiles"
        )
        fullfan_src = os.path.join(include_dir, "fullfan.txt")

        with patch("src.run_preparer.shutil.copy") as mock_copy:
            preparer._copy_common_files(rundatadir, config)
            mock_copy.assert_any_call(fullfan_src, rundatadir)

    def test_copies_halffan_for_half_fan_mode(self, tmp_path: object) -> None:
        preparer = RunPreparer(str(tmp_path))
        config = SimulationConfig()
        config.imaging.fan_mode = "Half Fan"
        rundatadir = str(tmp_path / "rundata")
        os.makedirs(rundatadir)

        include_dir = os.path.join(
            str(tmp_path), "src", "boilerplates", "TOPAS_includeFiles"
        )
        halffan_src = os.path.join(include_dir, "halffan.txt")

        with patch("src.run_preparer.shutil.copy") as mock_copy:
            preparer._copy_common_files(rundatadir, config)
            mock_copy.assert_any_call(halffan_src, rundatadir)


class TestGeneratePlugFiles:
    def test_generates_five_position_files(self, tmp_path: object) -> None:
        preparer = RunPreparer(str(tmp_path))
        rundatadir = str(tmp_path / "rundata")
        os.makedirs(rundatadir)
        os.makedirs(os.path.join(str(tmp_path), "tmp"), exist_ok=True)

        head_src = os.path.join(str(tmp_path), "tmp", "headsourcecode.txt")
        with open(head_src, "w") as f:
            f.write('@@PLACEHOLDER@@ s:Ge/@@PLACEHOLDER@@/Material="PMMA"')

        phantom_src = os.path.join(str(tmp_path), "tmp", "CTDIphantom_16.txt")
        with open(phantom_src, "w") as f:
            f.write("phantom content")

        commands = preparer._generate_plug_files("16 cm", rundatadir, "/custom/topas")
        assert len(commands) == 5

    def test_commands_use_provided_topas_path(self, tmp_path: object) -> None:
        preparer = RunPreparer(str(tmp_path))
        rundatadir = str(tmp_path / "rundata")
        os.makedirs(rundatadir)
        os.makedirs(os.path.join(str(tmp_path), "tmp"), exist_ok=True)

        with open(os.path.join(str(tmp_path), "tmp", "headsourcecode.txt"), "w") as f:
            f.write("head")
        with open(os.path.join(str(tmp_path), "tmp", "CTDIphantom_16.txt"), "w") as f:
            f.write("phantom")

        topas_path = "/my/custom/topas/bin/topas"
        commands = preparer._generate_plug_files("16 cm", rundatadir, topas_path)
        for cmd, wd in commands:
            assert cmd.startswith(topas_path + " ")

    def test_replaces_placeholders_in_content(self, tmp_path: object) -> None:
        preparer = RunPreparer(str(tmp_path))
        rundatadir = str(tmp_path / "rundata")
        os.makedirs(rundatadir)
        os.makedirs(os.path.join(str(tmp_path), "tmp"), exist_ok=True)

        with open(os.path.join(str(tmp_path), "tmp", "headsourcecode.txt"), "w") as f:
            f.write('@@PLACEHOLDER@@ s:Ge/@@PLACEHOLDER@@/Material="PMMA"')
        with open(os.path.join(str(tmp_path), "tmp", "CTDIphantom_16.txt"), "w") as f:
            f.write("phantom")

        preparer._generate_plug_files("16 cm", rundatadir, "/topas")

        centre_file = os.path.join(rundatadir, "ChamberPlugCentre.txt")
        assert os.path.exists(centre_file)
        with open(centre_file, "r") as f:
            content = f.read()
        assert "@@PLACEHOLDER@@" not in content
        assert "ChamberPlugCentre" in content
        assert 'Material="Air"' in content


class TestPrepareDicomRun:
    @patch("src.run_preparer.shutil.copy")
    def test_creates_runfolder_and_copies_dicom_files(
        self, mock_copy: MagicMock, tmp_path: object
    ) -> None:
        preparer = RunPreparer(str(tmp_path))
        config = SimulationConfig()
        config.imaging.fan_mode = "Full Fan"

        rundatadir = preparer.prepare_dicom_run(config)

        assert os.path.isdir(rundatadir)

        include_dir = os.path.join(
            str(tmp_path), "src", "boilerplates", "TOPAS_includeFiles"
        )
        mock_copy.assert_any_call(
            os.path.join(str(tmp_path), "tmp", "headsourcecode.txt"),
            rundatadir,
        )
        mock_copy.assert_any_call(
            os.path.join(include_dir, "HUtoMaterialSchneider.txt"),
            rundatadir,
        )
        mock_copy.assert_any_call(
            os.path.join(str(tmp_path), "tmp", "patientDICOM.txt"),
            rundatadir,
        )


class TestPrepareCtdiRun:
    @patch("src.run_preparer.shutil.copy")
    def test_creates_runfolder_and_copies_ctdi_files(
        self, mock_copy: MagicMock, tmp_path: object
    ) -> None:
        preparer = RunPreparer(str(tmp_path))
        config = SimulationConfig()
        config.imaging.fan_mode = "Full Fan"

        rundatadir = preparer.prepare_ctdi_run(config)

        assert os.path.isdir(rundatadir)

        include_dir = os.path.join(
            str(tmp_path), "src", "boilerplates", "TOPAS_includeFiles"
        )
        mock_copy.assert_any_call(
            os.path.join(include_dir, "Muen.dat"),
            rundatadir,
        )
        mock_copy.assert_any_call(
            os.path.join(include_dir, "NbParticlesInTime.txt"),
            rundatadir,
        )
        mock_copy.assert_any_call(
            os.path.join(str(tmp_path), "tmp", "ConvertedTopasFile.txt"),
            rundatadir,
        )
        mock_copy.assert_any_call(
            os.path.join(str(tmp_path), "tmp", "head_calibration_factor.txt"),
            rundatadir,
        )


if __name__ == "__main__":
    pytest.main([__file__])
