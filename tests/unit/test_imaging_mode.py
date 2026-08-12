from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.models.imaging_mode import (
    IMAGING_MODES,
    ImagingMode,
    _FF_BX1,
    _FF_BX2,
    _FF_BY1,
    _FF_BY2,
    _HF_BX1,
    _HF_BX2,
    _HF_BY1,
    _HF_BY2,
)


class TestImagingModeDataclass:
    def test_field_access(self) -> None:
        mode: ImagingMode = IMAGING_MODES["CBCT Clockwise_Image Gently"]
        assert mode.voltage == "80 kV"
        assert mode.exposure == "100.2 mAs"
        assert mode.fan_mode == "Full Fan"
        assert mode.timeline_end == "501 s"

    def test_frozen(self) -> None:
        mode: ImagingMode = IMAGING_MODES["CBCT Clockwise_Head"]
        try:
            mode.voltage = "999 kV"
            assert False, "Should have raised FrozenInstanceError"
        except AttributeError:
            pass

    def test_new_field_access(self) -> None:
        mode: ImagingMode = IMAGING_MODES["CBCT Clockwise_Head"]
        assert mode.ctdi_phantom == "16 cm"
        assert mode.dose_factor == "1.0"
        assert mode.start_angle == "0 deg"


class TestImagingModesLookup:
    def test_all_expected_keys_present(self) -> None:
        # Original 7 CBCT Clockwise
        expected_keys = [
            "CBCT Clockwise_Image Gently",
            "CBCT Clockwise_Head",
            "CBCT Clockwise_Short Thorax",
            "CBCT Clockwise_Spotlight",
            "CBCT Clockwise_Thorax",
            "CBCT Clockwise_Pelvis",
            "CBCT Clockwise_Pelvis Large",
            # Original 7 CBCT Anticlockwise
            "CBCT Anticlockwise_Image Gently",
            "CBCT Anticlockwise_Head",
            "CBCT Anticlockwise_Short Thorax",
            "CBCT Anticlockwise_Spotlight",
            "CBCT Anticlockwise_Thorax",
            "CBCT Anticlockwise_Pelvis",
            "CBCT Anticlockwise_Pelvis Large",
            # kV-kV (7)
            "kV-kV_Image Gently",
            "kV-kV_Head",
            "kV-kV_Short Thorax",
            "kV-kV_Spotlight",
            "kV-kV_Thorax",
            "kV-kV_Pelvis",
            "kV-kV_Pelvis Large",
            # New 13 CBCT Clockwise
            "CBCT Clockwise_4D Spotlight",
            "CBCT Clockwise_4D Thorax",
            "CBCT Clockwise_Abdomen",
            "CBCT Clockwise_Abdo Spotlight",
            "CBCT Clockwise_Breast 360",
            "CBCT Clockwise_Extremity Spotlight",
            "CBCT Clockwise_Head and Shoulders",
            "CBCT Clockwise_Head SRS",
            "CBCT Clockwise_Paediatric Body",
            "CBCT Clockwise_Paediatric Head",
            "CBCT Clockwise_Pelvis Spotlight",
            "CBCT Clockwise_SBRT Spine",
            "CBCT Clockwise_Thorax Spotlight",
            # New 13 CBCT Anticlockwise
            "CBCT Anticlockwise_4D Spotlight",
            "CBCT Anticlockwise_4D Thorax",
            "CBCT Anticlockwise_Abdomen",
            "CBCT Anticlockwise_Abdo Spotlight",
            "CBCT Anticlockwise_Breast 360",
            "CBCT Anticlockwise_Extremity Spotlight",
            "CBCT Anticlockwise_Head and Shoulders",
            "CBCT Anticlockwise_Head SRS",
            "CBCT Anticlockwise_Paediatric Body",
            "CBCT Anticlockwise_Paediatric Head",
            "CBCT Anticlockwise_Pelvis Spotlight",
            "CBCT Anticlockwise_SBRT Spine",
            "CBCT Anticlockwise_Thorax Spotlight",
        ]
        for key in expected_keys:
            assert key in IMAGING_MODES, "Missing key: " + key
        assert len(IMAGING_MODES) == 47

    def test_kv_kv_modes_have_n_a_for_new_fields(self) -> None:
        for name in [
            "Image Gently",
            "Head",
            "Short Thorax",
            "Spotlight",
            "Thorax",
            "Pelvis",
            "Pelvis Large",
        ]:
            mode: ImagingMode = IMAGING_MODES["kV-kV_" + name]
            assert mode.ctdi_phantom == "N/A", name + " ctdi_phantom"
            assert mode.dose_factor == "N/A", name + " dose_factor"
            assert mode.start_angle == "0 deg", name + " start_angle"
            assert mode.fan_detail == "N/A", name + " fan_detail"
            assert mode.no_projections == "N/A", name + " no_projections"
            assert mode.proj_increment == "N/A", name + " proj_increment"
            assert mode.acquisition_time == "N/A", name + " acquisition_time"
            assert mode.ctdiw_reference == "N/A", name + " ctdiw_reference"

    def test_kv_kv_modes_have_correct_timeline(self) -> None:
        mode: ImagingMode = IMAGING_MODES["kV-kV_Head"]
        assert mode.timeline_end == "2 s"
        assert mode.rotation_rate == "90 deg/s"

    def test_half_fan_modes(self) -> None:
        for name in ["Thorax", "Pelvis", "Pelvis Large"]:
            mode: ImagingMode = IMAGING_MODES["CBCT Clockwise_" + name]
            assert mode.fan_mode == "Half Fan", "Expected Half Fan for " + name

    def test_spotlight_blade_signs_match_full_fan(self) -> None:
        reference = IMAGING_MODES["CBCT Clockwise_Image Gently"]
        for key in ["CBCT Clockwise_Spotlight", "CBCT Anticlockwise_Spotlight"]:
            mode = IMAGING_MODES[key]
            assert mode.blade_x1 == reference.blade_x1, key + " blade_x1 mismatch"
            assert mode.blade_x2 == reference.blade_x2, key + " blade_x2 mismatch"
            assert mode.blade_y1 == reference.blade_y1, key + " blade_y1 mismatch"
            assert mode.blade_y2 == reference.blade_y2, key + " blade_y2 mismatch"

    def test_cbct_phantom_values_match_phantom_size_enum(self) -> None:
        from src.models.enums import PhantomSize

        valid = {e.value for e in PhantomSize}
        for key, mode in IMAGING_MODES.items():
            if key.startswith("kV-kV"):
                continue
            assert mode.ctdi_phantom in valid, "{} has invalid ctdi_phantom: {}".format(
                key, mode.ctdi_phantom
            )

    def test_all_cbct_modes_fan_blade_consistency(self) -> None:
        """Full Fan modes must use FF blades; Half Fan modes must use HF blades."""
        for key, mode in IMAGING_MODES.items():
            if key.startswith("kV-kV"):
                continue
            if mode.fan_mode == "Full Fan":
                assert mode.blade_x1 == _FF_BX1, (
                    "{} Full Fan has wrong blade_x1".format(key)
                )
                assert mode.blade_x2 == _FF_BX2, (
                    "{} Full Fan has wrong blade_x2".format(key)
                )
                assert mode.blade_y1 == _FF_BY1, (
                    "{} Full Fan has wrong blade_y1".format(key)
                )
                assert mode.blade_y2 == _FF_BY2, (
                    "{} Full Fan has wrong blade_y2".format(key)
                )
            elif mode.fan_mode == "Half Fan":
                assert mode.blade_x1 == _HF_BX1, (
                    "{} Half Fan has wrong blade_x1".format(key)
                )
                assert mode.blade_x2 == _HF_BX2, (
                    "{} Half Fan has wrong blade_x2".format(key)
                )
                assert mode.blade_y1 == _HF_BY1, (
                    "{} Half Fan has wrong blade_y1".format(key)
                )
                assert mode.blade_y2 == _HF_BY2, (
                    "{} Half Fan has wrong blade_y2".format(key)
                )
            else:
                pytest.fail("{} has unexpected fan_mode: {}".format(key, mode.fan_mode))
