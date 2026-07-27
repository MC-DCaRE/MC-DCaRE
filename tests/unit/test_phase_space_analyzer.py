from __future__ import annotations

import os
import sys
from typing import Any

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.services.phase_space_analyzer import PhaseSpaceAnalyzer

FIXTURES = os.path.join(os.path.dirname(__file__), "..", "fixtures")
REAL_PHSP = os.path.join(FIXTURES, "topas_writebinary_example.phsp")


class TestPhaseSpaceAnalyzer:
    def test_analyze_synthetic_file(self, tmp_path: Any) -> None:
        phsp_path = str(tmp_path / "test.phsp")
        PhaseSpaceAnalyzer.create_synthetic_phsp(phsp_path, n_particles=1000)
        result = PhaseSpaceAnalyzer(phsp_path).analyze()
        assert result["particle_count"] == 1000
        # 60 keV round-trips through float32 MeV storage (~2e-7 rel error).
        assert result["mean_energy_keV"] == pytest.approx(60.0, abs=0.01)
        assert result["file_size_mb"] > 0
        assert result["particle_types"] == {"gamma": 1000}
        assert len(result["energy_spectrum"]["counts"]) == 100
        assert len(result["energy_spectrum"]["bin_edges"]) == 101

    def test_synthetic_writes_header_sibling(self, tmp_path: Any) -> None:
        phsp_path = str(tmp_path / "test.phsp")
        PhaseSpaceAnalyzer.create_synthetic_phsp(phsp_path, n_particles=10)
        # The .header sibling must exist so the file is self-describing.
        assert os.path.isfile(str(tmp_path / "test.header"))

    def test_histogram_counts_sum_to_particle_count(self, tmp_path: Any) -> None:
        phsp_path = str(tmp_path / "test.phsp")
        PhaseSpaceAnalyzer.create_synthetic_phsp(phsp_path, n_particles=500)
        result = PhaseSpaceAnalyzer(phsp_path).analyze()
        assert sum(result["energy_spectrum"]["counts"]) == 500
        assert sum(result["spatial_x"]["counts"]) == 500
        assert sum(result["spatial_y"]["counts"]) == 500
        assert sum(result["angular_dx"]["counts"]) == 500
        assert sum(result["angular_dy"]["counts"]) == 500

    def test_survival_fraction_with_metadata(self, tmp_path: Any) -> None:
        import yaml

        phsp_path = str(tmp_path / "test.phsp")
        PhaseSpaceAnalyzer.create_synthetic_phsp(phsp_path, n_particles=1000)
        meta_path = str(tmp_path / "simulation_metadata.yaml")
        with open(meta_path, "w") as f:
            yaml.dump({"total_histories": 10000}, f)
        result = PhaseSpaceAnalyzer(phsp_path, metadata_path=meta_path).analyze()
        assert result["survival_fraction"] == 0.1

    def test_survival_fraction_none_without_metadata(self, tmp_path: Any) -> None:
        phsp_path = str(tmp_path / "test.phsp")
        PhaseSpaceAnalyzer.create_synthetic_phsp(phsp_path, n_particles=100)
        result = PhaseSpaceAnalyzer(phsp_path).analyze()
        assert result["survival_fraction"] is None

    def test_survival_fraction_none_with_missing_metadata(self, tmp_path: Any) -> None:
        phsp_path = str(tmp_path / "test.phsp")
        PhaseSpaceAnalyzer.create_synthetic_phsp(phsp_path, n_particles=100)
        result = PhaseSpaceAnalyzer(
            phsp_path, metadata_path="/nonexistent/metadata.yaml"
        ).analyze()
        assert result["survival_fraction"] is None

    def test_empty_file_returns_zero_counts(self, tmp_path: Any) -> None:
        # An empty data file is valid (zero particles) even without a header.
        phsp_path = str(tmp_path / "empty.phsp")
        with open(phsp_path, "wb") as f:
            f.write(b"")
        result = PhaseSpaceAnalyzer(phsp_path).analyze()
        assert result["particle_count"] == 0
        assert result["mean_energy_keV"] == 0.0
        assert result["particle_types"] == {}

    def test_custom_bin_count(self, tmp_path: Any) -> None:
        phsp_path = str(tmp_path / "test.phsp")
        PhaseSpaceAnalyzer.create_synthetic_phsp(phsp_path, n_particles=100)
        result = PhaseSpaceAnalyzer(phsp_path, n_bins=50).analyze()
        assert len(result["energy_spectrum"]["counts"]) == 50

    def test_missing_header_raises(self, tmp_path: Any) -> None:
        # A non-empty data file without its .header sibling must fail loudly
        # rather than silently misparse bytes (the old 56-byte magic behavior).
        phsp_path = str(tmp_path / "noheader.phsp")
        with open(phsp_path, "wb") as f:
            f.write(b"\x00" * 340)  # 10 fake records, no header
        with pytest.raises(FileNotFoundError, match="header"):
            PhaseSpaceAnalyzer(phsp_path).analyze()

    def test_create_synthetic_returns_path(self, tmp_path: Any) -> None:
        phsp_path = str(tmp_path / "synth.phsp")
        result = PhaseSpaceAnalyzer.create_synthetic_phsp(phsp_path, 100)
        assert result == phsp_path
        assert os.path.isfile(phsp_path)
        # TOPAS default 10-field layout: 7 f4 + i4 + 2 flag bytes = 34 bytes.
        assert os.path.getsize(phsp_path) == 100 * 34


@pytest.mark.skipif(
    not os.path.isfile(REAL_PHSP),
    reason="Real TOPAS phase space fixture not installed",
)
class TestRealTopasFixture:
    """Independent ground-truth tests against a real TOPAS Binary file.

    The fixture (``tests/fixtures/topas_writebinary_example.phsp``) was
    produced by running the TOPAS ``WriteBinary`` example: 1000-history
    169.23 MeV proton beam into a water box, scored on the upstream face.
    The header reports 1031 scored particles (1000 proton + 28 e- + 2 gamma
    + 1 neutron). These values are independent of this codebase.
    """

    def test_particle_count_matches_header(self) -> None:
        result = PhaseSpaceAnalyzer(REAL_PHSP).analyze()
        assert result["particle_count"] == 1031

    def test_particle_types_match_header(self) -> None:
        result = PhaseSpaceAnalyzer(REAL_PHSP).analyze()
        assert result["particle_types"] == {
            "proton": 1000,
            "electron": 28,
            "gamma": 2,
            "neutron": 1,
        }

    def test_energy_is_in_kev_not_mev(self) -> None:
        # Beam energy is 169.23 MeV. If we forgot the MeV->keV conversion the
        # mean would be ~169; with the conversion it is ~169000.
        result = PhaseSpaceAnalyzer(REAL_PHSP).analyze()
        assert 150000.0 < result["mean_energy_keV"] < 175000.0

    def test_std_energy_nonzero(self) -> None:
        # Real scored particles have a spread of energies (independent check
        # that replaces the old circular raw-float64 std test).
        result = PhaseSpaceAnalyzer(REAL_PHSP).analyze()
        assert result["std_energy_keV"] > 0

    def test_histograms_have_requested_bins(self) -> None:
        result = PhaseSpaceAnalyzer(REAL_PHSP, n_bins=50).analyze()
        assert len(result["energy_spectrum"]["counts"]) == 50
        assert sum(result["energy_spectrum"]["counts"]) == 1031

    def test_survival_fraction_with_metadata(self, tmp_path: Any) -> None:
        import yaml

        meta = str(tmp_path / "simulation_metadata.yaml")
        with open(meta, "w") as f:
            yaml.dump({"total_histories": 1000}, f)
        result = PhaseSpaceAnalyzer(REAL_PHSP, metadata_path=meta).analyze()
        assert result["survival_fraction"] == pytest.approx(1.031)
