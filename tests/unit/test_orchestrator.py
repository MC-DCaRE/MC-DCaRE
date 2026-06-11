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
        config = make_config(simulation_type="CTDI", phantom_size="16 cm")
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
            100.0,
            200.0,
            "100000000",
            "/project",
            1.0,
            fan_mode="Full Fan",
            seed=9,
            threads=1,
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
            simulation_type="CTDI",
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
            simulation_type="CTDI",
            topas_directory="/topas/bin",
            histories="100000",
            anode_voltage="80 kV",
            exposure="50 mAs",
            sequential_times="1000",
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
            80.0,
            50.0,
            "100000000",
            "/project",
            1.0,
            fan_mode="Full Fan",
            seed=9,
            threads=1,
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
            simulation_type="CTDI",
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
            100.0,
            200.0,
            "100000000",
            "/project",
            1.0523,
            fan_mode="Full Fan",
            seed=9,
            threads=1,
        )


class TestCopyConfigYaml:
    def test_copies_when_path_set(self, tmp_path: Any, make_config: Any) -> None:
        src_file = tmp_path / "source_config.yaml"
        src_file.write_text("general:\n  seed: '42'\n")
        rundir = str(tmp_path / "runfolder")
        os.makedirs(rundir)
        config = make_config(config_yaml_path=str(src_file))
        Orchestrator._copy_config_yaml(rundir, config)
        dest = os.path.join(rundir, "source_config.yaml")
        assert os.path.isfile(dest)
        assert open(dest).read() == src_file.read_text()

    def test_skips_when_path_is_none(self, tmp_path: Any, make_config: Any) -> None:
        rundir = str(tmp_path / "runfolder")
        os.makedirs(rundir)
        config = make_config()
        assert config.config_yaml_path is None
        Orchestrator._copy_config_yaml(rundir, config)
        assert os.listdir(rundir) == []

    def test_skips_when_source_missing(self, tmp_path: Any, make_config: Any) -> None:
        rundir = str(tmp_path / "runfolder")
        os.makedirs(rundir)
        config = make_config(config_yaml_path="/nonexistent/path.yaml")
        Orchestrator._copy_config_yaml(rundir, config)
        assert os.listdir(rundir) == []

    def test_preserves_timestamps(self, tmp_path: Any, make_config: Any) -> None:
        src_file = tmp_path / "cfg.yaml"
        src_file.write_text("general:\n")
        rundir = str(tmp_path / "runfolder")
        os.makedirs(rundir)
        config = make_config(config_yaml_path=str(src_file))
        Orchestrator._copy_config_yaml(rundir, config)
        dest = os.path.join(rundir, "cfg.yaml")
        src_stat = os.stat(str(src_file))
        dest_stat = os.stat(dest)
        assert abs(src_stat.st_mtime - dest_stat.st_mtime) < 1

    @patch("src.orchestrator.SpectrumGenerator")
    @patch("src.orchestrator.BoilerplateManager")
    def test_run_with_runfolder_copies_config(
        self,
        mock_bm_cls: MagicMock,
        mock_sg_cls: MagicMock,
        tmp_path: Any,
        make_config: Any,
    ) -> None:
        src_file = tmp_path / "sim.yaml"
        src_file.write_text("general:\n  seed: '7'\n")
        rundir = str(tmp_path / "runfolder")
        os.makedirs(rundir)
        config = make_config(
            simulation_type="DICOM",
            config_yaml_path=str(src_file),
        )
        mock_renderer = MagicMock()
        mock_bm_cls.return_value.create_renderer.return_value = mock_renderer
        orch = Orchestrator("/project")
        with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
            with patch.object(DicomMode, "prepare_run"):
                with patch.object(DicomMode, "execute"):
                    orch.run_with_runfolder(rundir, config)
        assert os.path.isfile(os.path.join(rundir, "sim.yaml"))


class TestOrchestratorPhaseSpace:
    """Tests for phase space mode branching in Orchestrator."""

    @patch("src.orchestrator.SpectrumGenerator")
    @patch("src.orchestrator.BoilerplateManager")
    def test_score_mode_calls_spectrum_generator(
        self,
        mock_bm_cls: MagicMock,
        mock_sg_cls: MagicMock,
        make_config: Any,
    ) -> None:
        config = make_config(
            simulation_type="CTDI",
            topas_directory="/topas/bin",
            histories="100000",
            anode_voltage="80 kV",
            exposure="50 mAs",
            phantom_size="16 cm",
            phase_space_mode="score",
        )
        mock_renderer = MagicMock()
        mock_bm_cls.return_value.create_renderer.return_value = mock_renderer
        rundir = "/rundir"
        orch = Orchestrator("/project")
        with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
            with patch.object(CtdiMode, "prepare_run"):
                with patch.object(CtdiMode, "execute"):
                    orch.run_with_runfolder(rundir, config, dry_run=True)
        mock_sg_cls.generate.assert_called_once()

    @patch("src.orchestrator.SpectrumGenerator")
    @patch("src.orchestrator.BoilerplateManager")
    def test_replay_mode_skips_spectrum_generator(
        self,
        mock_bm_cls: MagicMock,
        mock_sg_cls: MagicMock,
        make_config: Any,
        tmp_path: Any,
    ) -> None:
        phsp_file = tmp_path / "beam.phsp"
        phsp_file.write_bytes(b"\x00" * 100)
        config = make_config(
            simulation_type="CTDI",
            topas_directory="/topas/bin",
            histories="100000",
            anode_voltage="80 kV",
            exposure="50 mAs",
            phantom_size="16 cm",
            phase_space_mode="replay",
            phase_space_file=str(phsp_file),
        )
        mock_renderer = MagicMock()
        mock_bm_cls.return_value.create_renderer.return_value = mock_renderer
        rundir = "/rundir"
        orch = Orchestrator("/project")
        with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
            with patch.object(CtdiMode, "prepare_run"):
                with patch.object(CtdiMode, "execute"):
                    orch.run_with_runfolder(rundir, config, dry_run=True)
        mock_sg_cls.generate.assert_not_called()

    @patch("src.orchestrator.SpectrumGenerator")
    @patch("src.orchestrator.BoilerplateManager")
    def test_score_mode_uses_score_template(
        self,
        mock_bm_cls: MagicMock,
        mock_sg_cls: MagicMock,
        make_config: Any,
    ) -> None:
        config = make_config(
            simulation_type="CTDI",
            topas_directory="/topas/bin",
            histories="100000",
            anode_voltage="80 kV",
            exposure="50 mAs",
            phantom_size="16 cm",
            phase_space_mode="score",
        )
        mock_renderer = MagicMock()
        mock_bm_cls.return_value.create_renderer.return_value = mock_renderer
        rundir = "/rundir"
        orch = Orchestrator("/project")
        with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
            with patch.object(CtdiMode, "prepare_run"):
                with patch.object(CtdiMode, "execute"):
                    orch.run_with_runfolder(rundir, config, dry_run=True)
        render_calls = mock_renderer.render.call_args_list
        template_names = [c[0][0] for c in render_calls]
        assert "ctdi_phsp_score.j2" in template_names

    @patch("src.orchestrator.SpectrumGenerator")
    @patch("src.orchestrator.BoilerplateManager")
    def test_replay_mode_uses_replay_template(
        self,
        mock_bm_cls: MagicMock,
        mock_sg_cls: MagicMock,
        make_config: Any,
        tmp_path: Any,
    ) -> None:
        phsp_file = tmp_path / "beam.phsp"
        phsp_file.write_bytes(b"\x00" * 100)
        config = make_config(
            simulation_type="CTDI",
            topas_directory="/topas/bin",
            histories="100000",
            anode_voltage="80 kV",
            exposure="50 mAs",
            phantom_size="16 cm",
            phase_space_mode="replay",
            phase_space_file=str(phsp_file),
        )
        mock_renderer = MagicMock()
        mock_bm_cls.return_value.create_renderer.return_value = mock_renderer
        rundir = "/rundir"
        orch = Orchestrator("/project")
        with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
            with patch.object(CtdiMode, "prepare_run"):
                with patch.object(CtdiMode, "execute"):
                    orch.run_with_runfolder(rundir, config, dry_run=True)
        render_calls = mock_renderer.render.call_args_list
        template_names = [c[0][0] for c in render_calls]
        assert "ctdi_phsp_replay.j2" in template_names

    def test_write_replay_metadata_adjusts_norm_factor(self, tmp_path: Any) -> None:
        metadata = {
            "norm_factor": 1.0e-10,
            "mAs": 100.0,
            "dcf_used": 1.0,
            "total_histories": 1000000,
        }
        meta_path = tmp_path / "simulation_metadata.yaml"
        import yaml

        with open(meta_path, "w") as f:
            yaml.dump(metadata, f)
        rundir = str(tmp_path / "run")
        os.makedirs(rundir)
        Orchestrator._write_replay_metadata(rundir, str(meta_path), 10)
        with open(os.path.join(rundir, "simulation_metadata.yaml")) as f:
            result = yaml.safe_load(f)
        assert abs(result["norm_factor"] - 1.0e-11) < 1e-20
        assert result["phase_space_multiple_use"] == 10
