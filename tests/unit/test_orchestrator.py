from __future__ import annotations

import logging
import os
import sys
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from src.modes.dicom_mode import DicomMode
from src.modes.ctdi_mode import CtdiMode
from src.modes.phantom_mode import PhantomMode
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

    def test_returns_phantom_mode_for_icrp145(self, make_config: Any) -> None:
        config = make_config(simulation_type="ICRP145")
        orch = Orchestrator("/project")
        mode = orch._get_mode(config)
        assert isinstance(mode, PhantomMode)

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
                        orch.run(config, dry_run=False)
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
                        orch.run(config, dry_run=False)
        mock_sg_cls.generate.assert_called_once_with(
            100.0,
            200.0,
            "100000000",
            "/project",
            fan_mode="Full Fan",
            seed=9,
            threads=1,
            filtration_mode="hybrid",
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
                        result = orch.run(config, dry_run=False)
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
                        orch.run(config, dry_run=False)
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
                        orch.run(config, dry_run=False)
        mock_sg_cls.generate.assert_called_once_with(
            80.0,
            50.0,
            "100000000",
            "/project",
            fan_mode="Full Fan",
            seed=9,
            threads=1,
            filtration_mode="hybrid",
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

    def test_score_mode_selects_score_template(
        self,
        make_config: Any,
    ) -> None:
        config = make_config(
            simulation_type="CTDI",
            phantom_size="16 cm",
            phase_space_mode="score",
        )
        mode = CtdiMode()
        assert mode._get_main_template(config) == "ctdi_phsp_score.j2"

    def test_replay_mode_selects_replay_template(
        self,
        make_config: Any,
        tmp_path: Any,
    ) -> None:
        phsp_file = tmp_path / "beam.phsp"
        phsp_file.write_bytes(b"\x00" * 100)
        config = make_config(
            simulation_type="CTDI",
            phantom_size="16 cm",
            phase_space_mode="replay",
            phase_space_file=str(phsp_file),
        )
        mode = CtdiMode()
        assert mode._get_main_template(config) == "ctdi_phsp_replay.j2"

    def test_write_replay_metadata_preserves_norm_factor(self, tmp_path: Any) -> None:
        """Replay metadata must NOT divide norm_factor by M.

        The M x R scaling is now handled by raw_absolute_dose_Gy dividing by
        the scorer-active history count read from the CSV, so the scoring
        metadata is copied through unchanged.
        """
        metadata = {
            "norm_factor": 1.0e-10,
            "mAs": 100.0,
            "dcf_used": 1.0,
            "total_histories": 1000000,
        }
        meta_path = tmp_path / "simulation_metadata.yaml"

        with open(meta_path, "w") as f:
            yaml.dump(metadata, f)
        rundir = str(tmp_path / "run")
        os.makedirs(rundir)
        Orchestrator._write_replay_metadata(rundir, str(meta_path), 10)
        with open(os.path.join(rundir, "simulation_metadata.yaml")) as f:
            result = yaml.safe_load(f)
        assert abs(result["norm_factor"] - 1.0e-10) < 1e-20
        assert result["phase_space_multiple_use"] == 10

    def test_write_replay_metadata_preserves_spectrum_fluence(
        self, tmp_path: Any
    ) -> None:
        """New-format metadata: spectrum_fluence is preserved (NOT divided by M)."""
        metadata = {
            "total_histories": 1000000,
            "exposure_mAs": 100.0,
            "spectrum_fluence_photons_per_mAs": 2.34e8,
        }
        meta_path = tmp_path / "simulation_metadata.yaml"
        with open(meta_path, "w") as f:
            yaml.dump(metadata, f)
        rundir = str(tmp_path / "run")
        os.makedirs(rundir)
        Orchestrator._write_replay_metadata(rundir, str(meta_path), 10)
        with open(os.path.join(rundir, "simulation_metadata.yaml")) as f:
            result = yaml.safe_load(f)
        assert abs(result["spectrum_fluence_photons_per_mAs"] - 2.34e8) < 1.0
        assert "norm_factor" not in result
        assert result["phase_space_multiple_use"] == 10

    def test_write_replay_metadata_independent_of_M_and_R(self, tmp_path: Any) -> None:
        """spectrum_fluence must be identical regardless of M and R.

        The M x R scaling is absorbed by the scorer-active history count in
        raw_absolute_dose_Gy, so the replay metadata no longer divides
        spectrum_fluence. The value must be the scoring-run constant for
        every (M, R).
        """
        base = {
            "total_histories": 1000000,
            "exposure_mAs": 100.0,
            "spectrum_fluence_photons_per_mAs": 2.34e8,
        }

        def run(meta: dict, m: int, r: int) -> float:
            meta_path = tmp_path / ("meta_%d_%d.yaml" % (m, r))
            with open(meta_path, "w") as f:
                yaml.dump(meta, f)
            rundir = str(tmp_path / ("run_%d_%d" % (m, r)))
            os.makedirs(rundir)
            Orchestrator._write_replay_metadata(rundir, str(meta_path), m, r)
            with open(os.path.join(rundir, "simulation_metadata.yaml")) as f:
                out = yaml.safe_load(f)
            assert out["phase_space_sequential_times"] == r
            return out["spectrum_fluence_photons_per_mAs"]

        m5r1 = run(dict(base), 5, 1)
        m5r10 = run(dict(base), 5, 10)
        m1r1 = run(dict(base), 1, 1)
        # spectrum_fluence unchanged for all (M, R):
        for val in (m5r1, m5r10, m1r1):
            assert abs(val - 2.34e8) < 1.0

    def test_write_replay_metadata_rejects_invalid_file(self, tmp_path: Any) -> None:
        bad_path = tmp_path / "bad.yaml"
        bad_path.write_text("not a dict")
        rundir = str(tmp_path / "run")
        os.makedirs(rundir)
        with pytest.raises(ValueError, match="Invalid metadata file"):
            Orchestrator._write_replay_metadata(rundir, str(bad_path), 1)

    def test_write_replay_metadata_rejects_missing_fields(self, tmp_path: Any) -> None:
        meta_path = tmp_path / "simulation_metadata.yaml"
        with open(meta_path, "w") as f:
            yaml.dump({"mAs": 100.0}, f)
        rundir = str(tmp_path / "run")
        os.makedirs(rundir)
        with pytest.raises(ValueError, match="missing both"):
            Orchestrator._write_replay_metadata(rundir, str(meta_path), 1)

    def test_replay_metadata_found_alongside_phsp_file(self, tmp_path: Any) -> None:
        """Replay mode finds metadata in the same dir as the .phsp file."""
        phsp_dir = tmp_path / "phase_space"
        phsp_dir.mkdir()
        phsp_file = phsp_dir / "beam_exit_phsp.phsp"
        phsp_file.write_bytes(b"\x00" * 100)
        metadata = {"norm_factor": 2.0e-10, "mAs": 50.0, "dcf_used": 1.0}
        meta_path = phsp_dir / "simulation_metadata.yaml"
        with open(meta_path, "w") as f:
            yaml.dump(metadata, f)

        rundir = str(tmp_path / "run")
        os.makedirs(rundir)

        # Simulate what _run_replay_mode does: find metadata next to phsp.
        phsp_dir_str = str(phsp_dir)
        scoring_metadata = os.path.join(phsp_dir_str, "simulation_metadata.yaml")
        assert os.path.isfile(scoring_metadata)

        Orchestrator._write_replay_metadata(rundir, scoring_metadata, 5)
        with open(os.path.join(rundir, "simulation_metadata.yaml")) as f:
            result = yaml.safe_load(f)
        # norm_factor is preserved unchanged (M x R scaling now handled by
        # the scorer-active history count in raw_absolute_dose_Gy).
        assert abs(result["norm_factor"] - 2.0e-10) < 1e-20


class TestScoreModeNonDryRun:
    """Tests for _run_score_mode with dry_run=False (post-processing path)."""

    @patch("src.orchestrator.SpectrumGenerator")
    @patch("src.orchestrator.BoilerplateManager")
    def test_analyzes_phsp_and_writes_stats(
        self,
        mock_bm_cls: MagicMock,
        mock_sg_cls: MagicMock,
        tmp_path: Any,
        make_config: Any,
    ) -> None:
        """Non-dry-run score mode: analyzes .phsp, writes stats, moves file."""
        from src.services.phase_space_analyzer import PhaseSpaceAnalyzer

        project_root = str(tmp_path / "project")
        rundir = str(tmp_path / "run")
        os.makedirs(os.path.join(project_root, "tmp"))
        os.makedirs(rundir)
        os.makedirs(os.path.join(rundir, "phase_space"))

        # Create a fake .phsp output file (10 particles).
        PhaseSpaceAnalyzer.create_synthetic_phsp(
            os.path.join(rundir, "beam_exit_phsp.phsp"), 10
        )

        # Create fake metadata in tmp/.
        metadata = {
            "norm_factor": 1.0e-10,
            "mAs": 100.0,
            "total_histories": 1000,
            "dcf_used": 1.0,
        }
        with open(
            os.path.join(project_root, "tmp", "simulation_metadata.yaml"), "w"
        ) as f:
            yaml.dump(metadata, f)

        config = make_config(
            simulation_type="CTDI",
            phantom_size="16 cm",
            phase_space_mode="score",
        )
        mock_renderer = MagicMock()
        mock_bm_cls.return_value.create_renderer.return_value = mock_renderer
        orch = Orchestrator(project_root)
        with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
            with patch.object(CtdiMode, "prepare_run"):
                with patch.object(CtdiMode, "execute"):
                    orch.run_with_runfolder(rundir, config, dry_run=False)

        # Verify stats file written.
        stats_path = os.path.join(rundir, "phase_space", "beam_statistics.yaml")
        assert os.path.isfile(stats_path)
        with open(stats_path) as f:
            stats = yaml.safe_load(f)
        assert stats["particle_count"] == 10
        assert stats["mean_energy_keV"] == pytest.approx(60.0, abs=0.01)

        # Verify .phsp moved to phase_space/.
        assert os.path.isfile(
            os.path.join(rundir, "phase_space", "beam_exit_phsp.phsp")
        )
        assert not os.path.isfile(os.path.join(rundir, "beam_exit_phsp.phsp"))

        # Verify .header sibling moved alongside the .phsp (replay needs both).
        assert os.path.isfile(
            os.path.join(rundir, "phase_space", "beam_exit_phsp.header")
        )
        assert not os.path.isfile(os.path.join(rundir, "beam_exit_phsp.header"))

        # Verify metadata copied to phase_space/.
        assert os.path.isfile(
            os.path.join(rundir, "phase_space", "simulation_metadata.yaml")
        )

    @patch("src.orchestrator.SpectrumGenerator")
    @patch("src.orchestrator.BoilerplateManager")
    def test_no_phsp_file_skips_analysis(
        self,
        mock_bm_cls: MagicMock,
        mock_sg_cls: MagicMock,
        tmp_path: Any,
        make_config: Any,
    ) -> None:
        """Non-dry-run score mode: missing .phsp file skips all post-processing."""
        project_root = str(tmp_path / "project")
        rundir = str(tmp_path / "run")
        os.makedirs(os.path.join(project_root, "tmp"))
        os.makedirs(rundir)

        config = make_config(
            simulation_type="CTDI",
            phantom_size="16 cm",
            phase_space_mode="score",
        )
        mock_renderer = MagicMock()
        mock_bm_cls.return_value.create_renderer.return_value = mock_renderer
        orch = Orchestrator(project_root)
        with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
            with patch.object(CtdiMode, "prepare_run"):
                with patch.object(CtdiMode, "execute"):
                    # Should not raise.
                    orch.run_with_runfolder(rundir, config, dry_run=False)

        # No stats file written.
        assert not os.path.isfile(
            os.path.join(rundir, "phase_space", "beam_statistics.yaml")
        )

    @patch("src.orchestrator.SpectrumGenerator")
    @patch("src.orchestrator.BoilerplateManager")
    def test_no_metadata_still_analyzes(
        self,
        mock_bm_cls: MagicMock,
        mock_sg_cls: MagicMock,
        tmp_path: Any,
        make_config: Any,
    ) -> None:
        """Non-dry-run score mode: missing metadata → analyzer gets None."""
        from src.services.phase_space_analyzer import PhaseSpaceAnalyzer

        project_root = str(tmp_path / "project")
        rundir = str(tmp_path / "run")
        os.makedirs(os.path.join(project_root, "tmp"))
        os.makedirs(rundir)
        os.makedirs(os.path.join(rundir, "phase_space"))

        # Create .phsp but NO metadata.
        PhaseSpaceAnalyzer.create_synthetic_phsp(
            os.path.join(rundir, "beam_exit_phsp.phsp"), 5
        )

        config = make_config(
            simulation_type="CTDI",
            phantom_size="16 cm",
            phase_space_mode="score",
        )
        mock_renderer = MagicMock()
        mock_bm_cls.return_value.create_renderer.return_value = mock_renderer
        orch = Orchestrator(project_root)
        with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
            with patch.object(CtdiMode, "prepare_run"):
                with patch.object(CtdiMode, "execute"):
                    orch.run_with_runfolder(rundir, config, dry_run=False)

        # Stats file still written, but survival_fraction is None.
        stats_path = os.path.join(rundir, "phase_space", "beam_statistics.yaml")
        assert os.path.isfile(stats_path)
        with open(stats_path) as f:
            stats = yaml.safe_load(f)
        assert stats["particle_count"] == 5
        assert stats["survival_fraction"] is None


class TestReplayModeNonDryRun:
    """Tests for _run_replay_mode with dry_run=False."""

    @patch("src.orchestrator.SpectrumGenerator")
    @patch("src.orchestrator.BoilerplateManager")
    def test_calls_execute_when_not_dry_run(
        self,
        mock_bm_cls: MagicMock,
        mock_sg_cls: MagicMock,
        tmp_path: Any,
        make_config: Any,
    ) -> None:
        """Non-dry-run replay mode: calls ctdi_mode.execute()."""
        phsp_file = tmp_path / "beam.phsp"
        phsp_file.write_bytes(b"\x00" * 100)

        project_root = str(tmp_path / "project")
        rundir = str(tmp_path / "run")
        os.makedirs(os.path.join(project_root, "tmp"))
        os.makedirs(rundir)

        config = make_config(
            simulation_type="CTDI",
            phantom_size="16 cm",
            phase_space_mode="replay",
            phase_space_file=str(phsp_file),
        )
        mock_renderer = MagicMock()
        mock_bm_cls.return_value.create_renderer.return_value = mock_renderer
        orch = Orchestrator(project_root)
        with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
            with patch.object(CtdiMode, "prepare_run"):
                with patch.object(CtdiMode, "execute") as mock_execute:
                    orch.run_with_runfolder(rundir, config, dry_run=False)
        mock_execute.assert_called_once()

    @patch("src.orchestrator.SpectrumGenerator")
    @patch("src.orchestrator.BoilerplateManager")
    def test_skips_execute_when_dry_run(
        self,
        mock_bm_cls: MagicMock,
        mock_sg_cls: MagicMock,
        tmp_path: Any,
        make_config: Any,
    ) -> None:
        """Dry-run replay mode: does NOT call ctdi_mode.execute()."""
        phsp_file = tmp_path / "beam.phsp"
        phsp_file.write_bytes(b"\x00" * 100)

        project_root = str(tmp_path / "project")
        rundir = str(tmp_path / "run")
        os.makedirs(os.path.join(project_root, "tmp"))
        os.makedirs(rundir)

        config = make_config(
            simulation_type="CTDI",
            phantom_size="16 cm",
            phase_space_mode="replay",
            phase_space_file=str(phsp_file),
        )
        mock_renderer = MagicMock()
        mock_bm_cls.return_value.create_renderer.return_value = mock_renderer
        orch = Orchestrator(project_root)
        with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
            with patch.object(CtdiMode, "prepare_run"):
                with patch.object(CtdiMode, "execute") as mock_execute:
                    orch.run_with_runfolder(rundir, config, dry_run=True)
        mock_execute.assert_not_called()

    @patch("src.orchestrator.SpectrumGenerator")
    @patch("src.orchestrator.BoilerplateManager")
    def test_no_metadata_logs_warning(
        self,
        mock_bm_cls: MagicMock,
        mock_sg_cls: MagicMock,
        tmp_path: Any,
        make_config: Any,
        caplog: Any,
    ) -> None:
        """Replay mode with no metadata logs a warning."""
        phsp_file = tmp_path / "beam.phsp"
        phsp_file.write_bytes(b"\x00" * 100)

        project_root = str(tmp_path / "project")
        rundir = str(tmp_path / "run")
        os.makedirs(os.path.join(project_root, "tmp"))
        os.makedirs(rundir)

        config = make_config(
            simulation_type="CTDI",
            phantom_size="16 cm",
            phase_space_mode="replay",
            phase_space_file=str(phsp_file),
        )
        mock_renderer = MagicMock()
        mock_bm_cls.return_value.create_renderer.return_value = mock_renderer
        orch = Orchestrator(project_root)
        with caplog.at_level(logging.WARNING):
            with patch.object(orch, "boilerplate_manager", mock_bm_cls.return_value):
                with patch.object(CtdiMode, "prepare_run"):
                    with patch.object(CtdiMode, "execute"):
                        orch.run_with_runfolder(rundir, config, dry_run=True)
        assert any("No scoring metadata found" in msg for msg in caplog.messages), (
            "Expected warning about missing metadata"
        )


class TestGetPhaseSpaceModeForDicom:
    """Verify _get_phase_space_mode returns 'off' for non-CTDI types."""

    def test_returns_off_for_dicom(self, make_config: Any) -> None:
        config = make_config(
            simulation_type="DICOM",
            phase_space_mode="score",  # Even if set, should be ignored
        )
        orch = Orchestrator("/project")
        assert orch._get_phase_space_mode(config) == "off"

    def test_returns_mode_for_ctdi(self, make_config: Any) -> None:
        config = make_config(
            simulation_type="CTDI",
            phantom_size="16 cm",
            phase_space_mode="score",
        )
        orch = Orchestrator("/project")
        assert orch._get_phase_space_mode(config) == "score"
