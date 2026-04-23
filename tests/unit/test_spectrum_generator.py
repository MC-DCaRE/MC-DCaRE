import os
import sys
import numpy as np
import pytest
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
        os.makedirs(os.path.join(str(tmp_path), "tmp"), exist_ok=True)
        SpectrumGenerator.generate(100.0, 10.0, "100000", str(tmp_path))
        mock_sp.Spek.assert_called_once_with(kvp=100.0, th=14, mas=10.0, dk=0.2, z=0.1)

    @patch("src.spectrum_generator.sp")
    def test_creates_calibration_factor_file(
        self, mock_sp: MagicMock, tmp_path: object
    ) -> None:
        mock_sp.Spek.return_value = MockSpek()
        os.makedirs(os.path.join(str(tmp_path), "tmp"), exist_ok=True)
        SpectrumGenerator.generate(100.0, 10.0, "100000", str(tmp_path))
        calib_path = os.path.join(str(tmp_path), "tmp", "head_calibration_factor.txt")
        assert os.path.exists(calib_path)

    @patch("src.spectrum_generator.sp")
    def test_creates_converted_topas_file(
        self, mock_sp: MagicMock, tmp_path: object
    ) -> None:
        mock_sp.Spek.return_value = MockSpek()
        os.makedirs(os.path.join(str(tmp_path), "tmp"), exist_ok=True)
        SpectrumGenerator.generate(100.0, 10.0, "100000", str(tmp_path))
        converted_path = os.path.join(str(tmp_path), "tmp", "ConvertedTopasFile.txt")
        assert os.path.exists(converted_path)

    @patch("src.spectrum_generator.sp")
    def test_calibration_factor_content_has_multiply_message(
        self, mock_sp: MagicMock, tmp_path: object
    ) -> None:
        mock_sp.Spek.return_value = MockSpek()
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
        os.makedirs(os.path.join(str(tmp_path), "tmp"), exist_ok=True)
        SpectrumGenerator.generate(100.0, 10.0, "100000", str(tmp_path))
        converted_path = os.path.join(str(tmp_path), "tmp", "ConvertedTopasFile.txt")
        with open(converted_path, "r") as f:
            content = f.read()
        assert "keV" in content


if __name__ == "__main__":
    pytest.main([__file__])
