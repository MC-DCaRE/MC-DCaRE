from __future__ import annotations

import os
import sys
from typing import Any
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from src.modes.dicom_mode import DicomMode
from src.modes.ctdi_mode import CtdiMode
from src.orchestrator import Orchestrator


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


class TestRunDicomSimulation:
    @patch("src.orchestrator.SpectrumGenerator")
    @patch("src.orchestrator.BoilerplateManager")
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
        mock_renderer = MagicMock()
        mock_bm_cls.return_value.create_renderer.return_value = mock_renderer
        mock_bm_cls.return_value.reset_tmp.return_value = None
        orch = Orchestrator("/project")
        with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
            with patch.object(orch, "_create_runfolder", return_value="/rundir"):
                with patch.object(DicomMode, "prepare_run"):
                    with patch.object(DicomMode, "execute"):
                        orch.run_dicom_simulation(config)
        mock_bm_cls.return_value.reset_tmp.assert_called_once()

    @patch("src.orchestrator.SpectrumGenerator")
    @patch("src.orchestrator.BoilerplateManager")
    def test_calls_spectrum_generator(
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
        mock_renderer = MagicMock()
        mock_bm_cls.return_value.create_renderer.return_value = mock_renderer
        orch = Orchestrator("/project")
        with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
            with patch.object(orch, "_create_runfolder", return_value="/rundir"):
                with patch.object(DicomMode, "prepare_run"):
                    with patch.object(DicomMode, "execute"):
                        orch.run_dicom_simulation(config)
        mock_sg_cls.generate.assert_called_once_with(
            100.0, 200.0, "100000000", "/project", 1.0
        )

    @patch("src.orchestrator.SpectrumGenerator")
    @patch("src.orchestrator.BoilerplateManager")
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
        mock_renderer = MagicMock()
        mock_bm_cls.return_value.create_renderer.return_value = mock_renderer
        orch = Orchestrator("/project")
        with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
            with patch.object(orch, "_create_runfolder", return_value="/rundir"):
                with patch.object(DicomMode, "prepare_run"):
                    with patch.object(DicomMode, "execute"):
                        result = orch.run_dicom_simulation(config)
        assert result == "/rundir"


class TestRunCtdiSimulation:
    @patch("src.orchestrator.SpectrumGenerator")
    @patch("src.orchestrator.BoilerplateManager")
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
        mock_renderer = MagicMock()
        mock_bm_cls.return_value.create_renderer.return_value = mock_renderer
        orch = Orchestrator("/project")
        with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
            with patch.object(orch, "_create_runfolder", return_value="/rundir"):
                with patch.object(CtdiMode, "prepare_run"):
                    with patch.object(CtdiMode, "execute"):
                        orch.run_ctdi_simulation(config)
        mock_bm_cls.return_value.reset_tmp.assert_called_once()

    @patch("src.orchestrator.SpectrumGenerator")
    @patch("src.orchestrator.BoilerplateManager")
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
        mock_renderer = MagicMock()
        mock_bm_cls.return_value.create_renderer.return_value = mock_renderer
        orch = Orchestrator("/project")
        with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
            with patch.object(orch, "_create_runfolder", return_value="/rundir"):
                with patch.object(CtdiMode, "prepare_run"):
                    with patch.object(CtdiMode, "execute"):
                        orch.run_ctdi_simulation(config)
        mock_sg_cls.generate.assert_called_once_with(
            80.0, 50.0, "100000", "/project", 1.0
        )


class TestPrepareOnly:
    @patch("src.orchestrator.SpectrumGenerator")
    @patch("src.orchestrator.BoilerplateManager")
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
        mock_renderer = MagicMock()
        mock_bm_cls.return_value.create_renderer.return_value = mock_renderer
        orch = Orchestrator("/project")
        with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
            with patch.object(orch, "_create_runfolder", return_value="/rundir"):
                with patch.object(DicomMode, "prepare_run"):
                    with patch.object(DicomMode, "execute") as mock_execute:
                        orch.prepare_only(config)
                    mock_execute.assert_not_called()

    @patch("src.orchestrator.SpectrumGenerator")
    @patch("src.orchestrator.BoilerplateManager")
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
        mock_renderer = MagicMock()
        mock_bm_cls.return_value.create_renderer.return_value = mock_renderer
        orch = Orchestrator("/project")
        with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
            with patch.object(orch, "_create_runfolder", return_value="/rundir"):
                with patch.object(CtdiMode, "prepare_run"):
                    result = orch.prepare_only(config)
        assert result == "/rundir"


class TestOrchestratorCalibrationFactor:
    @patch("src.orchestrator.SpectrumGenerator")
    @patch("src.orchestrator.BoilerplateManager")
    def test_passes_calibration_factor(
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
            dose_calibration_factor="1.0523",
        )
        mock_renderer = MagicMock()
        mock_bm_cls.return_value.create_renderer.return_value = mock_renderer
        orch = Orchestrator("/project")
        with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
            with patch.object(orch, "_create_runfolder", return_value="/rundir"):
                with patch.object(DicomMode, "prepare_run"):
                    with patch.object(DicomMode, "execute"):
                        orch.run(config)
        mock_sg_cls.generate.assert_called_once_with(
            100.0, 200.0, "100000000", "/project", 1.0523
        )
