from __future__ import annotations

import os
import sys
from typing import Any


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.services.phase_space_analyzer import PhaseSpaceAnalyzer


class TestPhaseSpaceAnalyzer:
    def test_analyze_synthetic_file(self, tmp_path: Any) -> None:
        phsp_path = str(tmp_path / "test.phsp")
        PhaseSpaceAnalyzer.create_synthetic_phsp(phsp_path, n_particles=1000)
        analyzer = PhaseSpaceAnalyzer(phsp_path)
        result = analyzer.analyze()
        assert result["particle_count"] == 1000
        assert result["mean_energy_keV"] == 60.0
        assert result["file_size_mb"] > 0
        assert result["particle_types"] == {"gamma": 1000}
        assert len(result["energy_spectrum"]["counts"]) == 100
        assert len(result["energy_spectrum"]["bin_edges"]) == 101

    def test_histogram_counts_sum_to_particle_count(self, tmp_path: Any) -> None:
        phsp_path = str(tmp_path / "test.phsp")
        PhaseSpaceAnalyzer.create_synthetic_phsp(phsp_path, n_particles=500)
        analyzer = PhaseSpaceAnalyzer(phsp_path)
        result = analyzer.analyze()
        assert sum(result["energy_spectrum"]["counts"]) == 500
        assert sum(result["spatial_x"]["counts"]) == 500
        assert sum(result["angular_dx"]["counts"]) == 500

    def test_survival_fraction_with_metadata(self, tmp_path: Any) -> None:
        import yaml

        phsp_path = str(tmp_path / "test.phsp")
        PhaseSpaceAnalyzer.create_synthetic_phsp(phsp_path, n_particles=1000)
        meta_path = str(tmp_path / "simulation_metadata.yaml")
        with open(meta_path, "w") as f:
            yaml.dump({"total_histories": 10000}, f)
        analyzer = PhaseSpaceAnalyzer(phsp_path, metadata_path=meta_path)
        result = analyzer.analyze()
        assert result["survival_fraction"] == 0.1

    def test_survival_fraction_none_without_metadata(self, tmp_path: Any) -> None:
        phsp_path = str(tmp_path / "test.phsp")
        PhaseSpaceAnalyzer.create_synthetic_phsp(phsp_path, n_particles=100)
        analyzer = PhaseSpaceAnalyzer(phsp_path)
        result = analyzer.analyze()
        assert result["survival_fraction"] is None

    def test_survival_fraction_none_with_missing_metadata(self, tmp_path: Any) -> None:
        phsp_path = str(tmp_path / "test.phsp")
        PhaseSpaceAnalyzer.create_synthetic_phsp(phsp_path, n_particles=100)
        analyzer = PhaseSpaceAnalyzer(
            phsp_path, metadata_path="/nonexistent/metadata.yaml"
        )
        result = analyzer.analyze()
        assert result["survival_fraction"] is None

    def test_empty_file_returns_zero_counts(self, tmp_path: Any) -> None:
        phsp_path = str(tmp_path / "empty.phsp")
        with open(phsp_path, "wb") as f:
            f.write(b"")
        analyzer = PhaseSpaceAnalyzer(phsp_path)
        result = analyzer.analyze()
        assert result["particle_count"] == 0
        assert result["mean_energy_keV"] == 0.0
        assert result["particle_types"] == {}

    def test_custom_bin_count(self, tmp_path: Any) -> None:
        phsp_path = str(tmp_path / "test.phsp")
        PhaseSpaceAnalyzer.create_synthetic_phsp(phsp_path, n_particles=100)
        analyzer = PhaseSpaceAnalyzer(phsp_path, n_bins=50)
        result = analyzer.analyze()
        assert len(result["energy_spectrum"]["counts"]) == 50

    def test_std_energy_nonzero_for_varied_energies(self, tmp_path: Any) -> None:
        import numpy as np

        phsp_path = str(tmp_path / "test.phsp")
        n = 500
        rng = np.random.default_rng(123)
        records = np.zeros((n, 7), dtype=np.float64)
        records[:, 5] = rng.uniform(20, 100, n)  # varied energies
        records.tofile(phsp_path)
        analyzer = PhaseSpaceAnalyzer(phsp_path)
        result = analyzer.analyze()
        assert result["std_energy_keV"] > 0
        assert 40 < result["mean_energy_keV"] < 80

    def test_create_synthetic_returns_path(self, tmp_path: Any) -> None:
        phsp_path = str(tmp_path / "synth.phsp")
        result = PhaseSpaceAnalyzer.create_synthetic_phsp(phsp_path, 100)
        assert result == phsp_path
        assert os.path.isfile(phsp_path)
        assert os.path.getsize(phsp_path) == 100 * 56  # 56 bytes per record
