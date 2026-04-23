"""Smoke tests for defaultvalues.py module."""

import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from src.defaultvalues import (
    default_G4_Directory,
    default_TOPAS_Directory,
    default_Seed,
    default_Threads,
    default_Histories,
    default_DICOM_Directory,
    default_DICOM_RP_file,
    default_DICOM_TRANS_X,
    default_DICOM_TRANS_Y,
    default_DICOM_TRANS_Z,
    default_DICOM_ROT_X,
    default_DICOM_ROT_Y,
    default_DICOM_ROT_Z,
    default_DICOM_ISOCENTER_X,
    default_DICOM_ISOCENTER_Y,
    default_DICOM_ISOCENTER_Z,
    default_DTM_Zbins,
    default_TLE_Zbins,
    default_DTW_Zbins,
    default_COUCH_HLZ,
    default_COUCH_HLY,
    default_COUCH_HLX,
    default_TIME_SEQ_TIME,
    default_TIME_VERBOSITY,
    default_TIME_TIME_END,
    default_TIME_ROT_FUNC,
    default_TIME_ROT_RATE,
    default_TIME_ROT_START,
    default_TIME_ROT_HISTORY,
    default_FAN_MODE,
    default_FIELD_X1,
    default_FIELD_X2,
    default_FIELD_Y1,
    default_FIELD_Y2,
    default_BLADE_X1,
    default_BLADE_X2,
    default_BLADE_Y1,
    default_BLADE_Y2,
    default_IMAGE_START_ANGLE,
    default_IMAGE_VOLTAGE,
    default_EXPOSURE,
)


class TestDefaultValues:
    """Smoke tests for default values module."""

    def test_all_default_values_exist(self):
        """Test that all expected default values are defined."""
        # Test G4 and TOPAS defaults
        assert default_G4_Directory is not None
        assert default_TOPAS_Directory is not None
        assert default_Seed is not None
        assert default_Threads is not None
        assert default_Histories is not None

        # Test DICOM defaults
        assert default_DICOM_Directory is not None
        assert default_DICOM_RP_file is not None
        assert default_DICOM_TRANS_X is not None
        assert default_DICOM_TRANS_Y is not None
        assert default_DICOM_TRANS_Z is not None
        assert default_DICOM_ROT_X is not None
        assert default_DICOM_ROT_Y is not None
        assert default_DICOM_ROT_Z is not None
        assert default_DICOM_ISOCENTER_X is not None
        assert default_DICOM_ISOCENTER_Y is not None
        assert default_DICOM_ISOCENTER_Z is not None

        # Test bin defaults
        assert default_DTM_Zbins is not None
        assert default_TLE_Zbins is not None
        assert default_DTW_Zbins is not None

        # Test couch defaults
        assert default_COUCH_HLZ is not None
        assert default_COUCH_HLY is not None
        assert default_COUCH_HLX is not None

        # Test time defaults
        assert default_TIME_SEQ_TIME is not None
        assert default_TIME_VERBOSITY is not None
        assert default_TIME_TIME_END is not None
        assert default_TIME_ROT_FUNC is not None
        assert default_TIME_ROT_RATE is not None
        assert default_TIME_ROT_START is not None
        assert default_TIME_ROT_HISTORY is not None

        # Test field and blade defaults
        assert default_FAN_MODE is not None
        assert default_FIELD_X1 is not None
        assert default_FIELD_X2 is not None
        assert default_FIELD_Y1 is not None
        assert default_FIELD_Y2 is not None
        assert default_BLADE_X1 is not None
        assert default_BLADE_X2 is not None
        assert default_BLADE_Y1 is not None
        assert default_BLADE_Y2 is not None

        # Test imaging defaults
        assert default_IMAGE_START_ANGLE is not None
        assert default_IMAGE_VOLTAGE is not None
        assert default_EXPOSURE is not None

    def test_default_values_are_strings(self):
        """Test that default values are strings (as expected by GUI)."""
        string_defaults = [
            default_G4_Directory,
            default_TOPAS_Directory,
            default_Seed,
            default_Threads,
            default_Histories,
            default_DICOM_Directory,
            default_DICOM_RP_file,
            default_DICOM_TRANS_X,
            default_DICOM_TRANS_Y,
            default_DICOM_TRANS_Z,
            default_DICOM_ROT_X,
            default_DICOM_ROT_Y,
            default_DICOM_ROT_Z,
            default_DICOM_ISOCENTER_X,
            default_DICOM_ISOCENTER_Y,
            default_DICOM_ISOCENTER_Z,
            default_DTM_Zbins,
            default_TLE_Zbins,
            default_DTW_Zbins,
            default_COUCH_HLZ,
            default_COUCH_HLY,
            default_COUCH_HLX,
            default_TIME_SEQ_TIME,
            default_TIME_VERBOSITY,
            default_TIME_TIME_END,
            default_TIME_ROT_FUNC,
            default_TIME_ROT_RATE,
            default_TIME_ROT_START,
            default_TIME_ROT_HISTORY,
            default_FAN_MODE,
            default_FIELD_X1,
            default_FIELD_X2,
            default_FIELD_Y1,
            default_FIELD_Y2,
            default_BLADE_X1,
            default_BLADE_X2,
            default_BLADE_Y1,
            default_BLADE_Y2,
            default_IMAGE_START_ANGLE,
            default_IMAGE_VOLTAGE,
            default_EXPOSURE,
        ]

        for default_value in string_defaults:
            assert isinstance(default_value, str), (
                f"Expected string, got {type(default_value)}"
            )

    def test_default_values_have_reasonable_content(self):
        """Test that default values contain expected content."""
        # Test paths are non-empty strings
        assert isinstance(default_G4_Directory, str) and len(default_G4_Directory) > 0
        assert (
            isinstance(default_TOPAS_Directory, str)
            and len(default_TOPAS_Directory) > 0
        )
        assert "sampledicom" in default_DICOM_Directory
        assert ".dcm" in default_DICOM_RP_file

        # Test numeric values are reasonable
        assert int(default_Seed) >= 0
        assert int(default_Threads) > 0
        assert int(default_Histories) > 0
        assert int(default_DTM_Zbins) > 0
        assert int(default_TLE_Zbins) > 0
        assert int(default_DTW_Zbins) > 0

        # Test units are present where expected
        assert "mm" in default_COUCH_HLZ
        assert "mm" in default_COUCH_HLY
        assert "mm" in default_COUCH_HLX
        assert "s" in default_TIME_TIME_END
        assert "deg/s" in default_TIME_ROT_RATE
        assert "deg" in default_TIME_ROT_START
        assert "cm" in default_FIELD_X1
        assert "cm" in default_FIELD_X2
        assert "cm" in default_FIELD_Y1
        assert "cm" in default_FIELD_Y2
        assert "kV" in default_IMAGE_VOLTAGE
        assert "mAs" in default_EXPOSURE

    def test_fan_mode_is_valid(self):
        """Test that default fan mode is one of expected values."""
        valid_modes = ["Full Fan", "Half Fan"]
        assert default_FAN_MODE in valid_modes

    def test_coordinate_defaults_are_zero(self):
        """Test that coordinate defaults are zero."""
        zero_defaults = [
            default_DICOM_TRANS_X,
            default_DICOM_TRANS_Y,
            default_DICOM_TRANS_Z,
            default_DICOM_ROT_X,
            default_DICOM_ROT_Y,
            default_DICOM_ROT_Z,
            default_DICOM_ISOCENTER_X,
            default_DICOM_ISOCENTER_Y,
            default_DICOM_ISOCENTER_Z,
        ]

        for default_value in zero_defaults:
            # Extract numeric part (before space with unit)
            numeric_part = default_value.split()[0]
            assert float(numeric_part) == 0.0


if __name__ == "__main__":
    pytest.main([__file__])
