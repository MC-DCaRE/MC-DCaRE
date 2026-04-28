from __future__ import annotations

import os
import sys
from typing import Any
from unittest.mock import MagicMock, mock_open, patch


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from src.modes.dicom_mode import DicomMode
from src.modes.ctdi_mode import CtdiMode
from src.orchestrator import Orchestrator


MAIN_FILE_CONTENT: str = (
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

SUB_FILE_CONTENT: str = (
    'd:Ge/patrotation/yaw = "0. deg"\n'
    's:Ge/Patient/DicomDirectory = "/sampledicom/setA"\n'
    'dc:Ge/IsocenterX = "0 mm"\n'
    'dc:Ge/IsocenterY = "0 mm"\n'
    'dc:Ge/IsocenterZ = "0 mm"\n'
    'dc:Ge/Patient/UserTransX = "0. mm"\n'
    'dc:Ge/Patient/UserTransY = "0. mm"\n'
    'dc:Ge/Patient/UserTransZ = "0. mm"\n'
    's:Sc/DoseOnRTGrid100kz17/OutputFile = "output"\n'
    's:Ge/couch/Parent = "couchgroup"\n'
    'd:Ge/couch/HLX = "260. mm"\n'
    'd:Ge/couch/HLY = "0.4 mm"\n'
    'd:Ge/couch/HLZ = "1000 mm"\n'
    'i:Sc/ChamberPlugDose_dtm/ZBins = "100"\n'
    'i:Sc/ChamberPlugDose_tle/ZBins = "100"\n'
    'i:Sc/ChamberPlugDose_dtw/ZBins = "100"\n'
)


class TestGetMode:
    def test_returns_dicom_mode_for_dicom(self, make_config: Any) -> None:
        config = make_config(simulation_type="DICOM")
        orch = Orchestrator("/project")
        mode = orch._get_mode(config)
        assert isinstance(mode, DicomMode)

    def test_returns_ctdi_mode_for_ctdi(self, make_config: Any) -> None:
        config = make_config(simulation_type="CTDI validation", phantom_size="16 cm")
        orch = Orchestrator("/project")
        mode = orch._get_mode(config)
        assert isinstance(mode, CtdiMode)

    def test_unknown_type_returns_ctdi_mode(self, make_config: Any) -> None:
        config = make_config(simulation_type="Unknown")
        orch = Orchestrator("/project")
        mode = orch._get_mode(config)
        assert isinstance(mode, CtdiMode)


class TestApplyCommonEdits:
    def test_replaces_g4_directory(self, make_config: Any) -> None:
        config = make_config(
            simulation_type="DICOM", g4_data_directory="/custom/g4data"
        )
        orch = Orchestrator("/project")
        lines = MAIN_FILE_CONTENT.splitlines(keepends=True)
        orch._apply_common_edits(config, lines)
        content = "".join(lines)
        assert '/custom/g4data"' in content

    def test_replaces_seed_threads_histories(self, make_config: Any) -> None:
        config = make_config(
            simulation_type="DICOM",
            seed="99",
            threads="8",
            histories="2000000",
        )
        orch = Orchestrator("/project")
        lines = MAIN_FILE_CONTENT.splitlines(keepends=True)
        orch._apply_common_edits(config, lines)
        content = "".join(lines)
        assert "i:Ts/Seed = 99\n" in content
        assert "i:Ts/NumberOfThreads = 8\n" in content
        assert "i:So/beam/NumberOfHistoriesInRun = 2000000\n" in content

    def test_removes_halffan_for_full_fan_mode(self, make_config: Any) -> None:
        config = make_config(simulation_type="DICOM", fan_mode="Full Fan")
        orch = Orchestrator("/project")
        lines = MAIN_FILE_CONTENT.splitlines(keepends=True)
        orch._apply_common_edits(config, lines)
        content = "".join(lines)
        assert "includeFile = halffan.txt\n" not in content


@patch("src.orchestrator.SpectrumGenerator")
@patch("src.orchestrator.BoilerplateManager")
class TestRunDicomSimulation:
    def test_calls_reset_tmp(
        self,
        mock_bm_cls: MagicMock,
        mock_sg_cls: MagicMock,
        make_config: Any,
    ) -> None:
        config = make_config(
            simulation_type="DICOM",
            topas_directory="/topas/bin",
            histories="100000",
            anode_voltage="100 kV",
            exposure="200 mAs",
            sequential_times="1000",
            graphics_enabled=False,
        )
        orch = Orchestrator("/project")
        with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
            mock_bm_cls.return_value.get_headsource_path.return_value = "/tmp/head.txt"
            mock_bm_cls.return_value.get_tmp_path.return_value = "/tmp/patientDICOM.txt"
            with patch("builtins.open", mock_open(read_data=MAIN_FILE_CONTENT)):
                with patch.object(orch, "_create_runfolder", return_value="/rundir"):
                    with patch.object(DicomMode, "prepare_run"):
                        with patch.object(DicomMode, "execute"):
                            orch.run_dicom_simulation(config)
        mock_bm_cls.return_value.reset_tmp.assert_called_once()

    def test_calls_spectrum_generator_with_correct_params(
        self,
        mock_bm_cls: MagicMock,
        mock_sg_cls: MagicMock,
        make_config: Any,
    ) -> None:
        config = make_config(
            simulation_type="DICOM",
            topas_directory="/topas/bin",
            histories="100000",
            anode_voltage="100 kV",
            exposure="200 mAs",
            sequential_times="1000",
            graphics_enabled=False,
        )
        orch = Orchestrator("/project")
        with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
            mock_bm_cls.return_value.get_headsource_path.return_value = "/tmp/head.txt"
            mock_bm_cls.return_value.get_tmp_path.return_value = "/tmp/patientDICOM.txt"
            with patch("builtins.open", mock_open(read_data=MAIN_FILE_CONTENT)):
                with patch.object(orch, "_create_runfolder", return_value="/rundir"):
                    with patch.object(DicomMode, "prepare_run"):
                        with patch.object(DicomMode, "execute"):
                            orch.run_dicom_simulation(config)
        mock_sg_cls.generate.assert_called_once_with(
            100.0, 200.0, "100000000", "/project"
        )

    def test_returns_rundir(
        self,
        mock_bm_cls: MagicMock,
        mock_sg_cls: MagicMock,
        make_config: Any,
    ) -> None:
        config = make_config(
            simulation_type="DICOM",
            topas_directory="/topas/bin",
            histories="100000",
            anode_voltage="100 kV",
            exposure="200 mAs",
            sequential_times="1000",
            graphics_enabled=False,
        )
        orch = Orchestrator("/project")
        with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
            mock_bm_cls.return_value.get_headsource_path.return_value = "/tmp/head.txt"
            mock_bm_cls.return_value.get_tmp_path.return_value = "/tmp/patientDICOM.txt"
            with patch("builtins.open", mock_open(read_data=MAIN_FILE_CONTENT)):
                with patch.object(orch, "_create_runfolder", return_value="/rundir"):
                    with patch.object(DicomMode, "prepare_run"):
                        with patch.object(DicomMode, "execute"):
                            result = orch.run_dicom_simulation(config)
        assert result == "/rundir"


@patch("src.orchestrator.SpectrumGenerator")
@patch("src.orchestrator.BoilerplateManager")
class TestRunCtdiSimulation:
    def test_calls_reset_tmp(
        self,
        mock_bm_cls: MagicMock,
        mock_sg_cls: MagicMock,
        make_config: Any,
    ) -> None:
        config = make_config(
            simulation_type="CTDI validation",
            topas_directory="/topas/bin",
            histories="100000",
            anode_voltage="80 kV",
            exposure="50 mAs",
            phantom_size="16 cm",
        )
        orch = Orchestrator("/project")
        with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
            mock_bm_cls.return_value.get_headsource_path.return_value = "/tmp/head.txt"
            mock_bm_cls.return_value.get_tmp_path.return_value = (
                "/tmp/CTDIphantom_16.txt"
            )
            with patch("builtins.open", mock_open(read_data=MAIN_FILE_CONTENT)):
                with patch.object(orch, "_create_runfolder", return_value="/rundir"):
                    with patch.object(CtdiMode, "prepare_run"):
                        with patch.object(CtdiMode, "execute"):
                            orch.run_ctdi_simulation(config)
        mock_bm_cls.return_value.reset_tmp.assert_called_once()

    def test_calls_spectrum_generator(
        self,
        mock_bm_cls: MagicMock,
        mock_sg_cls: MagicMock,
        make_config: Any,
    ) -> None:
        config = make_config(
            simulation_type="CTDI validation",
            topas_directory="/topas/bin",
            histories="100000",
            anode_voltage="80 kV",
            exposure="50 mAs",
            phantom_size="16 cm",
        )
        orch = Orchestrator("/project")
        with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
            mock_bm_cls.return_value.get_headsource_path.return_value = "/tmp/head.txt"
            mock_bm_cls.return_value.get_tmp_path.return_value = (
                "/tmp/CTDIphantom_16.txt"
            )
            with patch("builtins.open", mock_open(read_data=MAIN_FILE_CONTENT)):
                with patch.object(orch, "_create_runfolder", return_value="/rundir"):
                    with patch.object(CtdiMode, "prepare_run"):
                        with patch.object(CtdiMode, "execute"):
                            orch.run_ctdi_simulation(config)
        mock_sg_cls.generate.assert_called_once_with(80.0, 50.0, "100000", "/project")

    def test_returns_rundir(
        self,
        mock_bm_cls: MagicMock,
        mock_sg_cls: MagicMock,
        make_config: Any,
    ) -> None:
        config = make_config(
            simulation_type="CTDI validation",
            topas_directory="/topas/bin",
            histories="100000",
            anode_voltage="80 kV",
            exposure="50 mAs",
            phantom_size="16 cm",
        )
        orch = Orchestrator("/project")
        with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
            mock_bm_cls.return_value.get_headsource_path.return_value = "/tmp/head.txt"
            mock_bm_cls.return_value.get_tmp_path.return_value = (
                "/tmp/CTDIphantom_16.txt"
            )
            with patch("builtins.open", mock_open(read_data=MAIN_FILE_CONTENT)):
                with patch.object(orch, "_create_runfolder", return_value="/rundir"):
                    with patch.object(CtdiMode, "prepare_run"):
                        with patch.object(CtdiMode, "execute"):
                            result = orch.run_ctdi_simulation(config)
        assert result == "/rundir"


@patch("src.orchestrator.SpectrumGenerator")
@patch("src.orchestrator.BoilerplateManager")
class TestPrepareOnly:
    def test_does_not_call_execute(
        self,
        mock_bm_cls: MagicMock,
        mock_sg_cls: MagicMock,
        make_config: Any,
    ) -> None:
        config = make_config(
            simulation_type="DICOM",
            topas_directory="/topas/bin",
            histories="100000",
            anode_voltage="100 kV",
            exposure="200 mAs",
            sequential_times="1000",
            graphics_enabled=False,
        )
        orch = Orchestrator("/project")
        with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
            mock_bm_cls.return_value.get_headsource_path.return_value = "/tmp/head.txt"
            mock_bm_cls.return_value.get_tmp_path.return_value = "/tmp/patientDICOM.txt"
            with patch("builtins.open", mock_open(read_data=MAIN_FILE_CONTENT)):
                with patch.object(orch, "_create_runfolder", return_value="/rundir"):
                    with patch.object(DicomMode, "prepare_run"):
                        with patch.object(DicomMode, "execute") as mock_execute:
                            orch.prepare_only(config)
                        mock_execute.assert_not_called()

    def test_returns_rundir(
        self,
        mock_bm_cls: MagicMock,
        mock_sg_cls: MagicMock,
        make_config: Any,
    ) -> None:
        config = make_config(
            simulation_type="CTDI validation",
            topas_directory="/topas/bin",
            histories="100000",
            anode_voltage="80 kV",
            exposure="50 mAs",
            phantom_size="16 cm",
        )
        orch = Orchestrator("/project")
        with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
            mock_bm_cls.return_value.get_headsource_path.return_value = "/tmp/head.txt"
            mock_bm_cls.return_value.get_tmp_path.return_value = (
                "/tmp/CTDIphantom_16.txt"
            )
            with patch("builtins.open", mock_open(read_data=MAIN_FILE_CONTENT)):
                with patch.object(orch, "_create_runfolder", return_value="/rundir"):
                    with patch.object(CtdiMode, "prepare_run"):
                        result = orch.prepare_only(config)
        assert result == "/rundir"
