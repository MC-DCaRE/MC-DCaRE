"""Integration tests for phase space scoring and replay pipelines.

Dry-run tests that verify template rendering, config validation,
and metadata handling without requiring a live TOPAS installation.
"""

from __future__ import annotations

import os
import sys
from typing import Any

import pytest
import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.config import (
    CtdiConfig,
    GeneralConfig,
    ImagingConfig,
    SimulationConfig,
)
from src.orchestrator import Orchestrator


def _mock_generate(
    voltage: float,
    exposure: float,
    histories: str,
    project_root: str,
    dose_calibration_factor: float = 1.0,
    **kwargs: object,
) -> None:
    """Write mock spectrum and metadata files."""
    tmp_dir = os.path.join(project_root, "tmp")
    os.makedirs(tmp_dir, exist_ok=True)
    with open(os.path.join(tmp_dir, "ConvertedTopasFile.txt"), "w") as f:
        f.write("dv:So/beam/BeamEnergySpectrumValues = 1\n 60.0 keV\n")
    with open(os.path.join(tmp_dir, "head_calibration_factor.txt"), "w") as f:
        f.write("%.10e" % 1.0)
    metadata = {
        "norm_factor": 1.0e-10,
        "mAs": exposure,
        "total_histories": int(histories),
        "dcf_used": dose_calibration_factor,
    }
    with open(os.path.join(tmp_dir, "simulation_metadata.yaml"), "w") as f:
        yaml.dump(metadata, f)


class TestScoringPipelineDryRun:
    """Dry-run scoring mode: verify template renders with PhaseSpace scorer."""

    def test_score_template_renders_with_phsp_scorer(self, tmp_path: Any) -> None:
        project_root = str(tmp_path / "project")
        boilerplates = os.path.join(project_root, "src", "boilerplates")
        include_dir = os.path.join(boilerplates, "TOPAS_includeFiles")
        os.makedirs(include_dir)
        os.makedirs(os.path.join(project_root, "tmp"))
        rundir = str(tmp_path / "runfolder")
        os.makedirs(rundir)

        # Copy templates from actual source.
        import shutil

        real_boilerplates = os.path.join(
            os.path.dirname(__file__), "..", "..", "src", "boilerplates"
        )
        for tmpl in [
            "ctdi_phsp_score.j2",
            "headsourcecode_boilerplate.j2",
        ]:
            shutil.copy(
                os.path.join(real_boilerplates, tmpl),
                os.path.join(boilerplates, tmpl),
            )
        for data_file in ["Muen.dat", "fullfan.txt"]:
            shutil.copy(
                os.path.join(real_boilerplates, "TOPAS_includeFiles", data_file),
                os.path.join(include_dir, data_file),
            )

        config = SimulationConfig(
            general=GeneralConfig(
                g4_data_directory="/g4",
                topas_directory="/topas/bin",
                histories="10000",
                seed="42",
                threads="1",
            ),
            imaging=ImagingConfig(
                simulation_type="CTDI",
                anode_voltage="100 kV",
                exposure="100 mAs",
                sequential_times="100",
                fan_mode="Full Fan",
            ),
            ctdi=CtdiConfig(
                phantom_size="16 cm",
                phase_space_mode="score",
            ),
        )

        # Test rendering directly through the mode.
        from src.modes.ctdi_mode import CtdiMode

        mode = CtdiMode()
        param_file = mode._generate_scoring_parameter_file(config, rundir, project_root)

        assert os.path.isfile(param_file)
        with open(param_file) as f:
            content = f.read()

        # PhaseSpace scorer present.
        assert 'Quantity            = "PhaseSpace"' in content
        # KillAfterPhaseSpace set.
        assert "KillAfterPhaseSpace" in content
        # Phantom NOT present.
        assert "ChamberPlug" not in content
        assert "LayeredMassGeometryWorlds" not in content

    def test_replay_without_file_raises_validation(self, tmp_path: Any) -> None:
        config = SimulationConfig(
            imaging=ImagingConfig(simulation_type="CTDI"),
            ctdi=CtdiConfig(phase_space_mode="replay"),
        )
        with pytest.raises(ValueError, match="phase_space_file is required"):
            config.validate()


class TestReplayPipelineDryRun:
    """Dry-run replay mode: verify template renders with PhaseSpace source."""

    def test_replay_template_renders_with_phsp_source(self, tmp_path: Any) -> None:
        project_root = str(tmp_path / "project")
        boilerplates = os.path.join(project_root, "src", "boilerplates")
        include_dir = os.path.join(boilerplates, "TOPAS_includeFiles")
        os.makedirs(include_dir)
        os.makedirs(os.path.join(project_root, "tmp"))
        rundir = str(tmp_path / "runfolder")
        os.makedirs(rundir)

        import shutil

        real_boilerplates = os.path.join(
            os.path.dirname(__file__), "..", "..", "src", "boilerplates"
        )
        for tmpl in [
            "ctdi_phsp_replay.j2",
            "headsourcecode_boilerplate.j2",
        ]:
            shutil.copy(
                os.path.join(real_boilerplates, tmpl),
                os.path.join(boilerplates, tmpl),
            )
        for tmpl in ["CTDIphantom_16.j2", "CTDIphantom_32.j2"]:
            src = os.path.join(real_boilerplates, "TOPAS_includeFiles", tmpl)
            if os.path.isfile(src):
                shutil.copy(src, os.path.join(include_dir, tmpl))
        for data_file in ["Muen.dat"]:
            shutil.copy(
                os.path.join(real_boilerplates, "TOPAS_includeFiles", data_file),
                os.path.join(include_dir, data_file),
            )

        # Create fake phase space file.
        phsp_file = tmp_path / "beam.phsp"
        phsp_file.write_bytes(b"\x00" * 560)  # 10 particles

        config = SimulationConfig(
            general=GeneralConfig(
                g4_data_directory="/g4",
                topas_directory="/topas/bin",
                histories="10000",
                seed="42",
                threads="1",
            ),
            imaging=ImagingConfig(
                simulation_type="CTDI",
                anode_voltage="100 kV",
                exposure="100 mAs",
                sequential_times="100",
            ),
            ctdi=CtdiConfig(
                phantom_size="16 cm",
                phase_space_mode="replay",
                phase_space_file=str(phsp_file),
                phase_space_multiple_use=10,
            ),
        )

        # Test rendering directly through the mode.
        from src.modes.ctdi_mode import CtdiMode

        mode = CtdiMode()
        param_file = mode._generate_replay_parameter_file(config, rundir, project_root)

        assert os.path.isfile(param_file)
        with open(param_file) as f:
            content = f.read()

        # PhaseSpace source present.
        assert 'So/beam/Type                  = "PhaseSpace"' in content
        assert "PhaseSpaceMultipleUse" in content
        # No beam line geometry.
        assert "CollimatorsVertical" not in content
        assert "BeamHardeningFilter" not in content
        assert "Ge/BeamPosition" not in content

        # Phantom include should be present (CTDIphantom_16).
        assert "ChamberPlug" in content


class TestReplayMetadataAdjustment:
    """Verify replay metadata has norm_factor = original_norm_factor / M."""

    def test_replay_metadata_norm_factor_adjusted(self, tmp_path: Any) -> None:
        scoring_meta = {
            "norm_factor": 2.0e-10,
            "mAs": 200.0,
            "dcf_used": 1.034,
            "total_histories": 1000000,
        }
        meta_path = tmp_path / "simulation_metadata.yaml"
        with open(meta_path, "w") as f:
            yaml.dump(scoring_meta, f)

        rundir = tmp_path / "runfolder"
        rundir.mkdir()

        M = 5
        Orchestrator._write_replay_metadata(str(rundir), str(meta_path), M)

        with open(rundir / "simulation_metadata.yaml") as f:
            result = yaml.safe_load(f)

        assert abs(result["norm_factor"] - 2.0e-10 / M) < 1e-20
        assert result["mAs"] == 200.0
        assert result["dcf_used"] == 1.034
        assert result["phase_space_multiple_use"] == M
        assert result["phase_space_source"] == str(meta_path)

    def test_replay_calibrates_correctly(self, tmp_path: Any) -> None:
        """End-to-end: replay metadata produces correct calibration_factor."""
        from src.services.ctdi_calculator import CTDICalculator

        M = 10
        original_norm = 5.0e-10
        mAs = 100.0
        dcf = 1.0

        # Simulate what the orchestrator writes.
        rundir = tmp_path / "replay_run"
        rundir.mkdir()
        metadata = {
            "norm_factor": original_norm / M,
            "mAs": mAs,
            "dcf_used": dcf,
        }
        with open(rundir / "simulation_metadata.yaml", "w") as f:
            yaml.dump(metadata, f)

        calc = CTDICalculator(rundir)
        # calibration_factor = (original_norm / M) * mAs * dcf
        expected = original_norm / M * mAs * dcf
        assert abs(calc.calibration_factor - expected) < 1e-20
