from __future__ import annotations

import os
import sys
from typing import Any
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.modes.ctdi_mode import CtdiMode

MAIN_FILE_CONTENT = (
    's:Ts/G4DataDirectory = "/root/G4Data"\n'
    'i:Tf/NumberOfSequentialTimes = "1000"\n'
    'd:Tf/TimelineEnd = "501.0 s"\n'
    'd:Tf/Rotate/Rate = "0.4 deg/s"\n'
    'd:Tf/Rotate/StartValue = "0 deg"\n'
    'i:Ts/Seed = "9"\n'
    'i:Ts/NumberOfThreads = "1"\n'
    'i:So/beam/NumberOfHistoriesInRun = "100000"\n'
    'dc:Ge/Coll1/TransY = "6.175536078965273 cm"\n'
    'dc:Ge/Coll2/TransY = "-6.175536078965273 cm"\n'
    'dc:Ge/Coll3/TransX = "5.814471115800571 cm"\n'
    'dc:Ge/Coll4/TransX = "-5.814471115800571 cm"\n'
    "includeFile = halffan.txt\n"
    "includeFile = CTDIphantom_16.txt\n"
    "includeFile = CTDIphantom_32.txt\n"
    'sv:Ph/Default/LayeredMassGeometryWorlds = "some value"\n'
    'Ts/UseQt = "true"\n'
    's:Gr/ViewA/Type = "some type"\n'
    'b:Gr/Enable = "true"\n'
    "includeFile = patientDICOM.txt\n"
)

CTDI_SUB_FILE_CONTENT = (
    's:Ge/couch/Parent="couchgroup"\n'
    "d:Ge/couch/HLX=260. mm\n"
    "d:Ge/couch/HLY= 0.4 mm\n"
    "d:Ge/couch/HLZ= 1000 mm\n"
    "i:Sc/ChamberPlugDose_dtm/ZBins=100\n"
    "i:Sc/ChamberPlugDose_tle/ZBins=100\n"
    "i:Sc/ChamberPlugDose_dtw/ZBins=100\n"
)


class TestEditMainFile:
    def test_blanks_patient_dicom_include(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config()
        lines = MAIN_FILE_CONTENT.splitlines(True)
        mode.edit_main_file(config, lines)
        for line in lines:
            assert not line.startswith(
                "includeFile = patientDICOM.txt"
            ), "patientDICOM.txt include should be blanked"

    def test_blanks_graphics_when_disabled(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(graphics_enabled=False)
        lines = MAIN_FILE_CONTENT.splitlines(True)
        mode.edit_main_file(config, lines)
        for line in lines:
            assert not line.startswith(
                "Ts/UseQt"
            ), "Ts/UseQt should be blanked when graphics disabled"
            assert not line.startswith(
                "s:Gr/ViewA/Type"
            ), "s:Gr/ViewA/Type should be blanked when graphics disabled"
            assert not line.startswith(
                "b:Gr/Enable"
            ), "b:Gr/Enable should be blanked when graphics disabled"

    def test_replaces_blade_positions_when_user_blade_enabled(
        self, make_config: Any
    ) -> None:
        mode = CtdiMode()
        config = make_config(
            user_blade_enabled=True,
            user_field_x1="10 cm",
            user_field_x2="10 cm",
            user_field_y1="10 cm",
            user_field_y2="10 cm",
        )
        lines = MAIN_FILE_CONTENT.splitlines(True)
        with patch(
            "src.modes.ctdi_mode.fieldtobladeopening",
            return_value=["5.0 cm", "-5.0 cm", "4.0 cm", "-4.0 cm"],
        ):
            mode.edit_main_file(config, lines)
        assert "dc:Ge/Coll1/TransY = 5.0 cm\n" in lines
        assert "dc:Ge/Coll2/TransY = -5.0 cm\n" in lines
        assert "dc:Ge/Coll3/TransX = 4.0 cm\n" in lines
        assert "dc:Ge/Coll4/TransX = -4.0 cm\n" in lines

    def test_blanks_wrong_phantom_for_16cm(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(phantom_size="16 cm")
        lines = MAIN_FILE_CONTENT.splitlines(True)
        mode.edit_main_file(config, lines)
        for line in lines:
            assert not line.startswith(
                "includeFile = CTDIphantom_32.txt"
            ), "CTDIphantom_32.txt include should be blanked for 16 cm phantom"
        assert any(
            line.startswith("includeFile = CTDIphantom_16.txt") for line in lines
        ), "CTDIphantom_16.txt include should remain for 16 cm phantom"

    def test_blanks_wrong_phantom_for_32cm(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(phantom_size="32 cm")
        lines = MAIN_FILE_CONTENT.splitlines(True)
        mode.edit_main_file(config, lines)
        for line in lines:
            assert not line.startswith(
                "includeFile = CTDIphantom_16.txt"
            ), "CTDIphantom_16.txt include should be blanked for 32 cm phantom"
        assert any(
            line.startswith("includeFile = CTDIphantom_32.txt") for line in lines
        ), "CTDIphantom_32.txt include should remain for 32 cm phantom"


class TestEditSubFile:
    def test_blanks_couch_parent_when_disabled(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(couch_enabled=False)
        lines = CTDI_SUB_FILE_CONTENT.splitlines(True)
        mode.edit_sub_file(config, lines)
        for line in lines:
            assert (
                's:Ge/couch/Parent="couchgroup"' not in line
            ), "couch Parent should be blanked when couch_enabled=False"

    def test_keeps_couch_parent_when_enabled(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(couch_enabled=True)
        lines = CTDI_SUB_FILE_CONTENT.splitlines(True)
        mode.edit_sub_file(config, lines)
        assert any(
            's:Ge/couch/Parent="couchgroup"' in line for line in lines
        ), "couch Parent should remain when couch_enabled=True"

    def test_replaces_couch_dimensions(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(
            couch_width="300. mm",
            couch_thickness="0.5 mm",
            couch_length="1500 mm",
        )
        lines = CTDI_SUB_FILE_CONTENT.splitlines(True)
        mode.edit_sub_file(config, lines)
        assert "d:Ge/couch/HLX = 300. mm\n" in lines
        assert "d:Ge/couch/HLY = 0.5 mm\n" in lines
        assert "d:Ge/couch/HLZ = 1500 mm\n" in lines

    def test_replaces_zbins(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(
            dose_to_medium_zbins="200",
            tle_zbins="150",
            dose_to_water_zbins="250",
        )
        lines = CTDI_SUB_FILE_CONTENT.splitlines(True)
        mode.edit_sub_file(config, lines)
        assert "i:Sc/ChamberPlugDose_dtm/ZBins = 200\n" in lines
        assert "i:Sc/ChamberPlugDose_tle/ZBins = 150\n" in lines
        assert "i:Sc/ChamberPlugDose_dtw/ZBins = 250\n" in lines


class TestGetSubFileName:
    def test_returns_16_phantom_for_16cm(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(phantom_size="16 cm")
        assert mode.get_sub_file_name(config) == "CTDIphantom_16.txt"

    def test_returns_32_phantom_for_32cm(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(phantom_size="32 cm")
        assert mode.get_sub_file_name(config) == "CTDIphantom_32.txt"


class TestComputeHistories:
    def test_returns_histories_directly(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(histories="50000")
        result = mode.compute_histories(config)
        assert result == "50000"


class TestExecute:
    def test_generates_plug_files_and_runs(self, make_config: Any) -> None:
        mode = CtdiMode()
        config = make_config(topas_directory="/topas/bin/topas")
        fake_commands = [("/topas/bin/topas /rundir/ChamberPlugCentre.txt", "/rundir")]
        with patch.object(
            CtdiMode, "_generate_plug_files", return_value=fake_commands
        ) as mock_gen, patch(
            "src.modes.ctdi_mode.SimulationRunner.run_ctdi"
        ) as mock_run:
            mode.execute(config, "/rundir", "/project")
            mock_gen.assert_called_once_with(
                "16 cm", "/rundir", "/topas/bin/topas", "/project"
            )
            mock_run.assert_called_once_with(
                "/topas/bin/topas", "/rundir", fake_commands
            )


class TestGeneratePlugFiles:
    def test_32cm_uses_32_phantom(self, tmp_path: object) -> None:
        rundatadir = str(tmp_path / "rundata")
        os.makedirs(rundatadir)
        os.makedirs(os.path.join(str(tmp_path), "tmp"), exist_ok=True)
        with open(os.path.join(str(tmp_path), "tmp", "headsourcecode.txt"), "w") as f:
            f.write('@@PLACEHOLDER@@ s:Ge/@@PLACEHOLDER@@/Material="PMMA"')
        with open(os.path.join(str(tmp_path), "tmp", "CTDIphantom_32.txt"), "w") as f:
            f.write("phantom32 content")
        with open(os.path.join(str(tmp_path), "tmp", "CTDIphantom_16.txt"), "w") as f:
            f.write("phantom16 content")
        commands = CtdiMode._generate_plug_files(
            "32 cm", rundatadir, "/topas", str(tmp_path)
        )
        assert len(commands) == 5
        with open(os.path.join(rundatadir, "ChamberPlugCentre.txt"), "r") as f:
            assert "phantom32 content" in f.read()

    def test_unknown_size_falls_back_to_16(self, tmp_path: object) -> None:
        rundatadir = str(tmp_path / "rundata")
        os.makedirs(rundatadir)
        os.makedirs(os.path.join(str(tmp_path), "tmp"), exist_ok=True)
        with open(os.path.join(str(tmp_path), "tmp", "headsourcecode.txt"), "w") as f:
            f.write("head")
        with open(os.path.join(str(tmp_path), "tmp", "CTDIphantom_16.txt"), "w") as f:
            f.write("phantom16 content")
        with open(os.path.join(str(tmp_path), "tmp", "CTDIphantom_32.txt"), "w") as f:
            f.write("phantom32 content")
        CtdiMode._generate_plug_files("40 cm", rundatadir, "/topas", str(tmp_path))
        with open(os.path.join(rundatadir, "ChamberPlugCentre.txt"), "r") as f:
            assert "phantom16 content" in f.read()

    def test_replaces_material_with_air(self, tmp_path: object) -> None:
        rundatadir = str(tmp_path / "rundata")
        os.makedirs(rundatadir)
        os.makedirs(os.path.join(str(tmp_path), "tmp"), exist_ok=True)
        with open(os.path.join(str(tmp_path), "tmp", "headsourcecode.txt"), "w") as f:
            f.write('s:Ge/ChamberPlugCentre/Material="PMMA"')
        with open(os.path.join(str(tmp_path), "tmp", "CTDIphantom_16.txt"), "w") as f:
            f.write("")
        CtdiMode._generate_plug_files("16 cm", rundatadir, "/topas", str(tmp_path))
        with open(os.path.join(rundatadir, "ChamberPlugCentre.txt"), "r") as f:
            content = f.read()
        assert 'Material="Air"' in content
        assert 'Material="PMMA"' not in content
