import sys
import os
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from src.config import SimulationConfig, GeneralConfig, ImagingConfig, CtdiConfig
from src.orchestrator import Orchestrator


def _make_dicom_config() -> SimulationConfig:
    return SimulationConfig(
        general=GeneralConfig(
            topas_directory="/topas/bin",
            histories="100000",
        ),
        imaging=ImagingConfig(
            simulation_type="DICOM",
            anode_voltage="100 kV",
            exposure="200 mAs",
            sequential_times="1000",
        ),
    )


def _make_ctdi_config() -> SimulationConfig:
    return SimulationConfig(
        general=GeneralConfig(
            topas_directory="/topas/bin",
            histories="100000",
        ),
        imaging=ImagingConfig(
            simulation_type="CTDI validation",
            anode_voltage="80 kV",
            exposure="50 mAs",
        ),
        ctdi=CtdiConfig(
            phantom_size="16 cm",
        ),
    )


@patch("src.orchestrator.SimulationRunner")
@patch("src.orchestrator.RunPreparer")
@patch("src.orchestrator.SpectrumGenerator")
@patch("src.orchestrator.ParameterEditor")
@patch("src.orchestrator.BoilerplateManager")
class TestRunDicomSimulation:
    def test_calls_reset_tmp(
        self,
        mock_bm_cls: MagicMock,
        mock_pe_cls: MagicMock,
        mock_sg_cls: MagicMock,
        mock_rp_cls: MagicMock,
        mock_sr_cls: MagicMock,
    ) -> None:
        config = _make_dicom_config()
        orch = Orchestrator("/project")

        with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
            mock_bm_cls.return_value.get_headsource_path.return_value = "/tmp/head.txt"
            mock_bm_cls.return_value.get_tmp_path.return_value = "/tmp/patientDICOM.txt"
            mock_rp_cls.return_value.prepare_dicom_run.return_value = "/rundir"
            orch.run_dicom_simulation(config)

        mock_bm_cls.return_value.reset_tmp.assert_called_once()

    def test_calls_edit_main_file(
        self,
        mock_bm_cls: MagicMock,
        mock_pe_cls: MagicMock,
        mock_sg_cls: MagicMock,
        mock_rp_cls: MagicMock,
        mock_sr_cls: MagicMock,
    ) -> None:
        config = _make_dicom_config()
        orch = Orchestrator("/project")

        with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
            mock_bm_cls.return_value.get_headsource_path.return_value = "/tmp/head.txt"
            mock_bm_cls.return_value.get_tmp_path.return_value = "/tmp/patientDICOM.txt"
            mock_rp_cls.return_value.prepare_dicom_run.return_value = "/rundir"
            orch.run_dicom_simulation(config)

        mock_pe_cls.return_value.edit_main_file.assert_called_once_with("/tmp/head.txt")

    def test_calls_edit_sub_file_with_patient_dicom(
        self,
        mock_bm_cls: MagicMock,
        mock_pe_cls: MagicMock,
        mock_sg_cls: MagicMock,
        mock_rp_cls: MagicMock,
        mock_sr_cls: MagicMock,
    ) -> None:
        config = _make_dicom_config()
        orch = Orchestrator("/project")

        with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
            mock_bm_cls.return_value.get_headsource_path.return_value = "/tmp/head.txt"
            mock_bm_cls.return_value.get_tmp_path.return_value = "/tmp/patientDICOM.txt"
            mock_rp_cls.return_value.prepare_dicom_run.return_value = "/rundir"
            orch.run_dicom_simulation(config)

        mock_pe_cls.return_value.edit_sub_file.assert_called_once_with(
            "/tmp/patientDICOM.txt"
        )

    def test_calls_spectrum_generator_with_correct_params(
        self,
        mock_bm_cls: MagicMock,
        mock_pe_cls: MagicMock,
        mock_sg_cls: MagicMock,
        mock_rp_cls: MagicMock,
        mock_sr_cls: MagicMock,
    ) -> None:
        config = _make_dicom_config()
        orch = Orchestrator("/project")

        with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
            mock_bm_cls.return_value.get_headsource_path.return_value = "/tmp/head.txt"
            mock_bm_cls.return_value.get_tmp_path.return_value = "/tmp/patientDICOM.txt"
            mock_rp_cls.return_value.prepare_dicom_run.return_value = "/rundir"
            orch.run_dicom_simulation(config)

        mock_sg_cls.generate.assert_called_once_with(
            100.0, 200.0, "100000000", "/project"
        )

    def test_calls_prepare_dicom_run(
        self,
        mock_bm_cls: MagicMock,
        mock_pe_cls: MagicMock,
        mock_sg_cls: MagicMock,
        mock_rp_cls: MagicMock,
        mock_sr_cls: MagicMock,
    ) -> None:
        config = _make_dicom_config()
        orch = Orchestrator("/project")

        with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
            mock_bm_cls.return_value.get_headsource_path.return_value = "/tmp/head.txt"
            mock_bm_cls.return_value.get_tmp_path.return_value = "/tmp/patientDICOM.txt"
            mock_rp_cls.return_value.prepare_dicom_run.return_value = "/rundir"
            orch.run_dicom_simulation(config)

        mock_rp_cls.return_value.prepare_dicom_run.assert_called_once_with(config)

    def test_calls_simulation_runner_run_dicom(
        self,
        mock_bm_cls: MagicMock,
        mock_pe_cls: MagicMock,
        mock_sg_cls: MagicMock,
        mock_rp_cls: MagicMock,
        mock_sr_cls: MagicMock,
    ) -> None:
        config = _make_dicom_config()
        orch = Orchestrator("/project")

        with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
            mock_bm_cls.return_value.get_headsource_path.return_value = "/tmp/head.txt"
            mock_bm_cls.return_value.get_tmp_path.return_value = "/tmp/patientDICOM.txt"
            mock_rp_cls.return_value.prepare_dicom_run.return_value = "/rundir"
            orch.run_dicom_simulation(config)

        mock_sr_cls.run_dicom.assert_called_once_with("/topas/bin", "/rundir")

    def test_returns_rundir(
        self,
        mock_bm_cls: MagicMock,
        mock_pe_cls: MagicMock,
        mock_sg_cls: MagicMock,
        mock_rp_cls: MagicMock,
        mock_sr_cls: MagicMock,
    ) -> None:
        config = _make_dicom_config()
        orch = Orchestrator("/project")

        with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
            mock_bm_cls.return_value.get_headsource_path.return_value = "/tmp/head.txt"
            mock_bm_cls.return_value.get_tmp_path.return_value = "/tmp/patientDICOM.txt"
            mock_rp_cls.return_value.prepare_dicom_run.return_value = "/rundir"
            result = orch.run_dicom_simulation(config)

        assert result == "/rundir"


@patch("src.orchestrator.SimulationRunner")
@patch("src.orchestrator.RunPreparer")
@patch("src.orchestrator.SpectrumGenerator")
@patch("src.orchestrator.ParameterEditor")
@patch("src.orchestrator.BoilerplateManager")
class TestRunCtdiSimulation:
    def test_calls_reset_tmp(
        self,
        mock_bm_cls: MagicMock,
        mock_pe_cls: MagicMock,
        mock_sg_cls: MagicMock,
        mock_rp_cls: MagicMock,
        mock_sr_cls: MagicMock,
    ) -> None:
        config = _make_ctdi_config()
        orch = Orchestrator("/project")

        with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
            mock_bm_cls.return_value.get_headsource_path.return_value = "/tmp/head.txt"
            mock_bm_cls.return_value.get_tmp_path.return_value = (
                "/tmp/CTDIphantom_16.txt"
            )
            mock_rp_cls.return_value.prepare_ctdi_run.return_value = "/rundir"
            mock_rp_cls.return_value._generate_plug_files.return_value = []
            orch.run_ctdi_simulation(config)

        mock_bm_cls.return_value.reset_tmp.assert_called_once()

    def test_calls_edit_main_file(
        self,
        mock_bm_cls: MagicMock,
        mock_pe_cls: MagicMock,
        mock_sg_cls: MagicMock,
        mock_rp_cls: MagicMock,
        mock_sr_cls: MagicMock,
    ) -> None:
        config = _make_ctdi_config()
        orch = Orchestrator("/project")

        with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
            mock_bm_cls.return_value.get_headsource_path.return_value = "/tmp/head.txt"
            mock_bm_cls.return_value.get_tmp_path.return_value = (
                "/tmp/CTDIphantom_16.txt"
            )
            mock_rp_cls.return_value.prepare_ctdi_run.return_value = "/rundir"
            mock_rp_cls.return_value._generate_plug_files.return_value = []
            orch.run_ctdi_simulation(config)

        mock_pe_cls.return_value.edit_main_file.assert_called_once_with("/tmp/head.txt")

    def test_calls_edit_sub_file_with_phantom_file(
        self,
        mock_bm_cls: MagicMock,
        mock_pe_cls: MagicMock,
        mock_sg_cls: MagicMock,
        mock_rp_cls: MagicMock,
        mock_sr_cls: MagicMock,
    ) -> None:
        config = _make_ctdi_config()
        orch = Orchestrator("/project")

        with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
            mock_bm_cls.return_value.get_headsource_path.return_value = "/tmp/head.txt"
            mock_bm_cls.return_value.get_tmp_path.return_value = (
                "/tmp/CTDIphantom_16.txt"
            )
            mock_rp_cls.return_value.prepare_ctdi_run.return_value = "/rundir"
            mock_rp_cls.return_value._generate_plug_files.return_value = []
            orch.run_ctdi_simulation(config)

        mock_pe_cls.return_value.edit_sub_file.assert_called_once_with(
            "/tmp/CTDIphantom_16.txt"
        )

    def test_calls_spectrum_generator(
        self,
        mock_bm_cls: MagicMock,
        mock_pe_cls: MagicMock,
        mock_sg_cls: MagicMock,
        mock_rp_cls: MagicMock,
        mock_sr_cls: MagicMock,
    ) -> None:
        config = _make_ctdi_config()
        orch = Orchestrator("/project")

        with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
            mock_bm_cls.return_value.get_headsource_path.return_value = "/tmp/head.txt"
            mock_bm_cls.return_value.get_tmp_path.return_value = (
                "/tmp/CTDIphantom_16.txt"
            )
            mock_rp_cls.return_value.prepare_ctdi_run.return_value = "/rundir"
            mock_rp_cls.return_value._generate_plug_files.return_value = []
            orch.run_ctdi_simulation(config)

        mock_sg_cls.generate.assert_called_once_with(80.0, 50.0, "100000", "/project")

    def test_calls_prepare_ctdi_run(
        self,
        mock_bm_cls: MagicMock,
        mock_pe_cls: MagicMock,
        mock_sg_cls: MagicMock,
        mock_rp_cls: MagicMock,
        mock_sr_cls: MagicMock,
    ) -> None:
        config = _make_ctdi_config()
        orch = Orchestrator("/project")

        with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
            mock_bm_cls.return_value.get_headsource_path.return_value = "/tmp/head.txt"
            mock_bm_cls.return_value.get_tmp_path.return_value = (
                "/tmp/CTDIphantom_16.txt"
            )
            mock_rp_cls.return_value.prepare_ctdi_run.return_value = "/rundir"
            mock_rp_cls.return_value._generate_plug_files.return_value = []
            orch.run_ctdi_simulation(config)

        mock_rp_cls.return_value.prepare_ctdi_run.assert_called_once_with(config)

    def test_calls_generate_plug_files_with_topas_path(
        self,
        mock_bm_cls: MagicMock,
        mock_pe_cls: MagicMock,
        mock_sg_cls: MagicMock,
        mock_rp_cls: MagicMock,
        mock_sr_cls: MagicMock,
    ) -> None:
        config = _make_ctdi_config()
        orch = Orchestrator("/project")

        with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
            mock_bm_cls.return_value.get_headsource_path.return_value = "/tmp/head.txt"
            mock_bm_cls.return_value.get_tmp_path.return_value = (
                "/tmp/CTDIphantom_16.txt"
            )
            mock_rp_cls.return_value.prepare_ctdi_run.return_value = "/rundir"
            mock_rp_cls.return_value._generate_plug_files.return_value = []
            orch.run_ctdi_simulation(config)

        mock_rp_cls.return_value._generate_plug_files.assert_called_once_with(
            "16 cm", "/rundir", "/topas/bin"
        )

    def test_calls_simulation_runner_run_ctdi(
        self,
        mock_bm_cls: MagicMock,
        mock_pe_cls: MagicMock,
        mock_sg_cls: MagicMock,
        mock_rp_cls: MagicMock,
        mock_sr_cls: MagicMock,
    ) -> None:
        config = _make_ctdi_config()
        orch = Orchestrator("/project")
        commands = [("cmd1", "/rundir")]

        with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
            mock_bm_cls.return_value.get_headsource_path.return_value = "/tmp/head.txt"
            mock_bm_cls.return_value.get_tmp_path.return_value = (
                "/tmp/CTDIphantom_16.txt"
            )
            mock_rp_cls.return_value.prepare_ctdi_run.return_value = "/rundir"
            mock_rp_cls.return_value._generate_plug_files.return_value = commands
            orch.run_ctdi_simulation(config)

        mock_sr_cls.run_ctdi.assert_called_once_with("/topas/bin", "/rundir", commands)

    def test_returns_rundir(
        self,
        mock_bm_cls: MagicMock,
        mock_pe_cls: MagicMock,
        mock_sg_cls: MagicMock,
        mock_rp_cls: MagicMock,
        mock_sr_cls: MagicMock,
    ) -> None:
        config = _make_ctdi_config()
        orch = Orchestrator("/project")

        with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
            mock_bm_cls.return_value.get_headsource_path.return_value = "/tmp/head.txt"
            mock_bm_cls.return_value.get_tmp_path.return_value = (
                "/tmp/CTDIphantom_16.txt"
            )
            mock_rp_cls.return_value.prepare_ctdi_run.return_value = "/rundir"
            mock_rp_cls.return_value._generate_plug_files.return_value = []
            result = orch.run_ctdi_simulation(config)

        assert result == "/rundir"


@patch("src.orchestrator.SimulationRunner")
@patch("src.orchestrator.RunPreparer")
@patch("src.orchestrator.SpectrumGenerator")
@patch("src.orchestrator.ParameterEditor")
@patch("src.orchestrator.BoilerplateManager")
class TestPrepareOnly:
    def test_dicom_mode_preparers_without_running(
        self,
        mock_bm_cls: MagicMock,
        mock_pe_cls: MagicMock,
        mock_sg_cls: MagicMock,
        mock_rp_cls: MagicMock,
        mock_sr_cls: MagicMock,
    ) -> None:
        config = _make_dicom_config()
        orch = Orchestrator("/project")

        with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
            mock_bm_cls.return_value.get_headsource_path.return_value = "/tmp/head.txt"
            mock_bm_cls.return_value.get_tmp_path.return_value = "/tmp/patientDICOM.txt"
            mock_rp_cls.return_value.prepare_dicom_run.return_value = "/rundir"
            result = orch.prepare_only(config)

        mock_rp_cls.return_value.prepare_dicom_run.assert_called_once_with(config)
        assert result == "/rundir"

    def test_ctdi_mode_preparers_without_running(
        self,
        mock_bm_cls: MagicMock,
        mock_pe_cls: MagicMock,
        mock_sg_cls: MagicMock,
        mock_rp_cls: MagicMock,
        mock_sr_cls: MagicMock,
    ) -> None:
        config = _make_ctdi_config()
        orch = Orchestrator("/project")

        with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
            mock_bm_cls.return_value.get_headsource_path.return_value = "/tmp/head.txt"
            mock_bm_cls.return_value.get_tmp_path.return_value = (
                "/tmp/CTDIphantom_16.txt"
            )
            mock_rp_cls.return_value.prepare_ctdi_run.return_value = "/rundir"
            result = orch.prepare_only(config)

        mock_rp_cls.return_value.prepare_ctdi_run.assert_called_once_with(config)
        assert result == "/rundir"

    def test_does_not_call_simulation_runner(
        self,
        mock_bm_cls: MagicMock,
        mock_pe_cls: MagicMock,
        mock_sg_cls: MagicMock,
        mock_rp_cls: MagicMock,
        mock_sr_cls: MagicMock,
    ) -> None:
        dicom_config = _make_dicom_config()
        ctdi_config = _make_ctdi_config()
        orch = Orchestrator("/project")

        with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
            mock_bm_cls.return_value.get_headsource_path.return_value = "/tmp/head.txt"
            mock_bm_cls.return_value.get_tmp_path.return_value = "/tmp/patientDICOM.txt"
            mock_rp_cls.return_value.prepare_dicom_run.return_value = "/rundir"
            mock_rp_cls.return_value.prepare_ctdi_run.return_value = "/rundir"

            orch.prepare_only(dicom_config)

            mock_bm_cls.return_value.get_tmp_path.return_value = (
                "/tmp/CTDIphantom_16.txt"
            )
            orch.prepare_only(ctdi_config)

        mock_sr_cls.run_dicom.assert_not_called()
        mock_sr_cls.run_ctdi.assert_not_called()
