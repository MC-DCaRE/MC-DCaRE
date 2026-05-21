import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.models.enums import SimulationType, FanMode, RotationDirection


class TestSimulationType:
    def test_dicom_value(self) -> None:
        assert SimulationType.DICOM == "DICOM"

    def test_ctdi_value(self) -> None:
        assert SimulationType.CTDI == "CTDI"

    def test_string_comparison(self) -> None:
        assert SimulationType.DICOM == "DICOM"
        assert "CTDI" == SimulationType.CTDI

    def test_is_str(self) -> None:
        assert isinstance(SimulationType.DICOM, str)


class TestFanMode:
    def test_full_value(self) -> None:
        assert FanMode.FULL == "Full Fan"

    def test_half_value(self) -> None:
        assert FanMode.HALF == "Half Fan"

    def test_string_comparison(self) -> None:
        assert FanMode.FULL == "Full Fan"


class TestRotationDirection:
    def test_cw_value(self) -> None:
        assert RotationDirection.CW == "CBCT Clockwise"

    def test_ccw_value(self) -> None:
        assert RotationDirection.CCW == "CBCT Anticlockwise"

    def test_kv_value(self) -> None:
        assert RotationDirection.KV_KV == "kV-kV"
