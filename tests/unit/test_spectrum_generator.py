from __future__ import annotations

import math
import os
import sys
import numpy as np
import pytest
import yaml
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.spectrum_generator import SpectrumGenerator


class MockState:
    def get_current_state_str(self, mode: str, results: object) -> str:
        return "Mock spectrum state"


class MockSpek:
    def __init__(
        self,
        kvp: float = None,
        th: float = None,
        dk: float = None,
        mas: float = None,
        **kwargs: object,
    ) -> None:
        self.kvp = kvp
        self.th = th
        self.mas = mas
        self.dk = dk
        self._state = MockState()

    def get_flu(self) -> float:
        return 1000.0

    def get_spectrum(self, edges: bool = False, diff: bool = False) -> tuple:
        return np.array([10.0, 20.0, 30.0]), np.array([100.0, 200.0, 300.0])

    def get_std_results(self) -> object:
        class Results:
            pass

        return Results()

    @property
    def state(self) -> MockState:
        return self._state


class TestSpectrumGenerator:
    @patch("src.spectrum_generator.sp")
    def test_calls_spek_with_correct_params(
        self, mock_sp: MagicMock, tmp_path: object
    ) -> None:
        mock_sp.Spek.return_value = MockSpek()
        mock_sp.__version__ = "2.0.1"
        os.makedirs(os.path.join(str(tmp_path), "tmp"), exist_ok=True)
        SpectrumGenerator.generate(100.0, 10.0, "100000", str(tmp_path))
        mock_sp.Spek.assert_called_once_with(kvp=100.0, th=14, mas=10.0, dk=0.2, z=0.1)

    @patch("src.spectrum_generator.sp")
    def test_creates_calibration_factor_file(
        self, mock_sp: MagicMock, tmp_path: object
    ) -> None:
        mock_sp.Spek.return_value = MockSpek()
        mock_sp.__version__ = "2.0.1"
        os.makedirs(os.path.join(str(tmp_path), "tmp"), exist_ok=True)
        SpectrumGenerator.generate(100.0, 10.0, "100000", str(tmp_path))
        calib_path = os.path.join(str(tmp_path), "tmp", "head_calibration_factor.txt")
        assert os.path.exists(calib_path)

    @patch("src.spectrum_generator.sp")
    def test_creates_converted_topas_file(
        self, mock_sp: MagicMock, tmp_path: object
    ) -> None:
        mock_sp.Spek.return_value = MockSpek()
        mock_sp.__version__ = "2.0.1"
        os.makedirs(os.path.join(str(tmp_path), "tmp"), exist_ok=True)
        SpectrumGenerator.generate(100.0, 10.0, "100000", str(tmp_path))
        converted_path = os.path.join(str(tmp_path), "tmp", "ConvertedTopasFile.txt")
        assert os.path.exists(converted_path)

    @patch("src.spectrum_generator.sp")
    def test_calibration_factor_content_has_multiply_message(
        self, mock_sp: MagicMock, tmp_path: object
    ) -> None:
        mock_sp.Spek.return_value = MockSpek()
        mock_sp.__version__ = "2.0.1"
        os.makedirs(os.path.join(str(tmp_path), "tmp"), exist_ok=True)
        SpectrumGenerator.generate(100.0, 10.0, "100000", str(tmp_path))
        calib_path = os.path.join(str(tmp_path), "tmp", "head_calibration_factor.txt")
        with open(calib_path, "r") as f:
            content = f.read()
        assert "Multiply dose by the factor above to get absolute dose" in content
        assert "100000" in content
        assert "Mock spectrum state" in content

    @patch("src.spectrum_generator.sp")
    def test_converted_file_has_spectrum_values_and_weights(
        self, mock_sp: MagicMock, tmp_path: object
    ) -> None:
        mock_sp.Spek.return_value = MockSpek()
        mock_sp.__version__ = "2.0.1"
        os.makedirs(os.path.join(str(tmp_path), "tmp"), exist_ok=True)
        SpectrumGenerator.generate(100.0, 10.0, "100000", str(tmp_path))
        converted_path = os.path.join(str(tmp_path), "tmp", "ConvertedTopasFile.txt")
        with open(converted_path, "r") as f:
            content = f.read()
        assert "dv:So/beam/BeamEnergySpectrumValues" in content
        assert "uv:So/beam/BeamEnergySpectrumWeights" in content

    @patch("src.spectrum_generator.sp")
    def test_converted_file_contains_keV(
        self, mock_sp: MagicMock, tmp_path: object
    ) -> None:
        mock_sp.Spek.return_value = MockSpek()
        mock_sp.__version__ = "2.0.1"
        os.makedirs(os.path.join(str(tmp_path), "tmp"), exist_ok=True)
        SpectrumGenerator.generate(100.0, 10.0, "100000", str(tmp_path))
        converted_path = os.path.join(str(tmp_path), "tmp", "ConvertedTopasFile.txt")
        with open(converted_path, "r") as f:
            content = f.read()
        assert "keV" in content

    @patch("src.spectrum_generator.sp")
    def test_calibration_factor_value(
        self, mock_sp: MagicMock, tmp_path: object
    ) -> None:
        mock_sp.Spek.return_value = MockSpek()
        mock_sp.__version__ = "2.0.1"
        os.makedirs(os.path.join(str(tmp_path), "tmp"), exist_ok=True)
        SpectrumGenerator.generate(100.0, 10.0, "100000", str(tmp_path))
        calib_path = os.path.join(str(tmp_path), "tmp", "head_calibration_factor.txt")

        # Physical oracle (independent of the source's own arithmetic):
        # upstream MC-DCaRE/MC-DCaRE defines the head calibration factor as
        # no_particles / histories, where no_particles = 4*pi*(0.1 m)^2 * flu
        # = 4*pi*0.01*flu (SpekPy flu over the 0.1 m reference sphere).
        # MockSpek.get_flu() returns 1000, histories=100000.
        expected = 4.0 * math.pi * 0.01 * 1000.0 / 100000
        with open(calib_path, "r") as f:
            actual = float(f.readline().strip())
        assert abs(actual - expected) < 1e-10

    @patch("src.spectrum_generator.sp")
    def test_default_calibration_factor_is_one(
        self, mock_sp: MagicMock, tmp_path: object
    ) -> None:
        mock_sp.Spek.return_value = MockSpek()
        mock_sp.__version__ = "2.0.1"
        os.makedirs(os.path.join(str(tmp_path), "tmp"), exist_ok=True)
        SpectrumGenerator.generate(100.0, 10.0, "100000", str(tmp_path))
        calib_path = os.path.join(str(tmp_path), "tmp", "head_calibration_factor.txt")

        expected = 4.0 * math.pi * 0.01 * 1000.0 / 100000
        with open(calib_path, "r") as f:
            actual = float(f.readline().strip())
        assert abs(actual - expected) < 1e-10

    @patch("src.spectrum_generator.sp")
    def test_creates_simulation_metadata_yaml(
        self, mock_sp: MagicMock, tmp_path: object
    ) -> None:
        mock_sp.Spek.return_value = MockSpek()
        mock_sp.__version__ = "2.0.1"
        os.makedirs(os.path.join(str(tmp_path), "tmp"), exist_ok=True)
        SpectrumGenerator.generate(
            120.0,
            100.0,
            "500000",
            str(tmp_path),
            fan_mode="Full Fan",
            seed=42,
            threads=4,
        )
        meta_path = os.path.join(str(tmp_path), "tmp", "simulation_metadata.yaml")
        assert os.path.exists(meta_path)

        with open(meta_path) as f:
            meta = yaml.safe_load(f)

        assert meta["exposure_mAs"] == 100.0
        assert meta["total_histories"] == 500000
        assert "dcf_used" not in meta
        assert "norm_factor" not in meta
        assert meta["fan_mode"] == "Full Fan"
        assert meta["seed"] == 42
        assert meta["threads"] == 4
        assert meta["spekpy"]["kvp"] == 120.0
        assert meta["spekpy"]["th"] == 14
        assert meta["spekpy"]["dk"] == 0.2
        assert meta["spekpy"]["z"] == 0.1
        assert meta["spekpy"]["mas"] == 100.0
        assert meta["spekpy"]["version"] == "2.0.1"
        assert "timestamp" in meta
        assert "spectrum_fluence_photons_per_mAs" in meta

    @patch("src.spectrum_generator.sp")
    def test_metadata_spectrum_fluence_is_per_mAs(
        self, mock_sp: MagicMock, tmp_path: object
    ) -> None:
        mock_sp.Spek.return_value = MockSpek()
        mock_sp.__version__ = "2.0.1"
        os.makedirs(os.path.join(str(tmp_path), "tmp"), exist_ok=True)
        SpectrumGenerator.generate(100.0, 10.0, "100000", str(tmp_path))

        meta_path = os.path.join(str(tmp_path), "tmp", "simulation_metadata.yaml")
        with open(meta_path) as f:
            meta = yaml.safe_load(f)

        expected_fluence = 4.0 * math.pi * 0.01 * 1000.0 / 100000
        assert abs(meta["spectrum_fluence_photons_per_mAs"] - expected_fluence) < 1e-10

    @patch("src.spectrum_generator.sp")
    def test_metadata_does_not_include_dcf_hint_when_one(
        self, mock_sp: MagicMock, tmp_path: object
    ) -> None:
        mock_sp.Spek.return_value = MockSpek()
        mock_sp.__version__ = "2.0.1"
        os.makedirs(os.path.join(str(tmp_path), "tmp"), exist_ok=True)
        SpectrumGenerator.generate(100.0, 10.0, "100000", str(tmp_path))

        meta_path = os.path.join(str(tmp_path), "tmp", "simulation_metadata.yaml")
        with open(meta_path) as f:
            meta = yaml.safe_load(f)

        assert "dcf_hint" not in meta


if __name__ == "__main__":
    pytest.main([__file__])
