import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.models.imaging_mode import (
    IMAGING_MODES,
    ImagingMode,
    BACKWARD_COMPAT_LOOKUP,
)


class TestImagingModeDataclass:
    def test_field_access(self) -> None:
        mode: ImagingMode = IMAGING_MODES["CBCT Clockwise_Image Gently"]
        assert mode.voltage == "80 kV"
        assert mode.exposure == "100 mAs"
        assert mode.fan_mode == "Full Fan"
        assert mode.timeline_end == "501 s"

    def test_frozen(self) -> None:
        mode: ImagingMode = IMAGING_MODES["CBCT Clockwise_Head"]
        try:
            mode.voltage = "999 kV"
            assert False, "Should have raised FrozenInstanceError"
        except AttributeError:
            pass

    def test_as_tuple_length(self) -> None:
        mode: ImagingMode = IMAGING_MODES["CBCT Clockwise_Head"]
        t = mode.as_tuple()
        assert len(t) == 13


class TestImagingModesLookup:
    def test_all_expected_keys_present(self) -> None:
        expected_keys = [
            "CBCT Clockwise_Image Gently",
            "CBCT Clockwise_Head",
            "CBCT Clockwise_Short Thorax",
            "CBCT Clockwise_Spotlight",
            "CBCT Clockwise_Thorax",
            "CBCT Clockwise_Pelvis",
            "CBCT Clockwise_Pelvis Large",
            "CBCT Anticlockwise_Image Gently",
            "CBCT Anticlockwise_Head",
            "CBCT Anticlockwise_Short Thorax",
            "CBCT Anticlockwise_Spotlight",
            "CBCT Anticlockwise_Thorax",
            "CBCT Anticlockwise_Pelvis",
            "CBCT Anticlockwise_Pelvis Large",
            "kV-kV_Image Gently",
            "kV-kV_Head",
            "kV-kV_Short Thorax",
            "kV-kV_Spotlight",
            "kV-kV_Thorax",
            "kV-kV_Pelvis",
            "kV-kV_Pelvis Large",
        ]
        for key in expected_keys:
            assert key in IMAGING_MODES, "Missing key: " + key

    def test_backward_compat_lookup_matches_old_format(self) -> None:
        from src.imaging_modes_lookuptable import imaging_modes_lookup

        for key in BACKWARD_COMPAT_LOOKUP:
            if key == "selection":
                continue
            assert key in imaging_modes_lookup
            old_list = imaging_modes_lookup[key]
            new_list = BACKWARD_COMPAT_LOOKUP[key]
            assert old_list == new_list, "Mismatch for key: " + key

    def test_kv_kv_modes_have_correct_timeline(self) -> None:
        mode: ImagingMode = IMAGING_MODES["kV-kV_Head"]
        assert mode.timeline_end == "2 s"
        assert mode.rotation_rate == "90 deg/s"

    def test_half_fan_modes(self) -> None:
        for name in ["Thorax", "Pelvis", "Pelvis Large"]:
            mode: ImagingMode = IMAGING_MODES[
                "CBCT Clockwise_" + name
            ]
            assert mode.fan_mode == "Half Fan", (
                "Expected Half Fan for " + name
            )
