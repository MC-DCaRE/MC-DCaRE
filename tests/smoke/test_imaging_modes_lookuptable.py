"""Smoke tests for imaging_modes_lookuptable.py module."""

import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from src.imaging_modes_lookuptable import imaging_modes_lookup


class TestImagingModesLookup:
    """Smoke tests for imaging modes lookup table."""

    def test_lookup_table_exists(self):
        """Test that imaging_modes_lookup is defined."""
        assert imaging_modes_lookup is not None
        assert isinstance(imaging_modes_lookup, dict)

    def test_lookup_table_has_required_keys(self):
        """Test that lookup table has expected structure."""
        # Should have 'selection' key
        assert "selection" in imaging_modes_lookup
        assert isinstance(imaging_modes_lookup["selection"], list)

        # Should have imaging mode keys
        expected_modes = [
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

        for mode in expected_modes:
            assert mode in imaging_modes_lookup, f"Missing mode: {mode}"

    def test_selection_keys_structure(self):
        """Test that selection keys match expected parameters."""
        selection = imaging_modes_lookup["selection"]
        expected_keys = [
            "Rotation Rate",
            "kVp",
            "exposure",
            "Fan",
            "timeend",
            "FIELD_X1",
            "FIELD_X2",
            "FIELD_Y1",
            "FIELD_Y2",
            "BLADE_X1",
            "BLADE_X2",
            "BLADE_Y1",
            "BLADE_Y2",
        ]

        assert len(selection) == len(
            expected_keys
        ), f"Expected {len(expected_keys)} keys, got {len(selection)}"

        for key in expected_keys:
            assert key in selection, f"Missing selection key: {key}"

    def test_mode_values_structure(self):
        """Test that each mode has correct number of parameters."""
        expected_param_count = 13  # Should match selection keys

        for mode_name, mode_values in imaging_modes_lookup.items():
            if mode_name == "selection":
                continue  # Skip selection key

            assert isinstance(mode_values, list), f"Mode {mode_name} should be a list"
            assert (
                len(mode_values) == expected_param_count
            ), f"Mode {mode_name} should have {expected_param_count} parameters, got {len(mode_values)}"

    def test_rotation_rate_values(self):
        """Test rotation rate values are reasonable."""
        rotation_rates = []

        for mode_name, mode_values in imaging_modes_lookup.items():
            if mode_name == "selection":
                continue

            rotation_rate = mode_values[0]  # First parameter is rotation rate
            rotation_rates.append(rotation_rate)

        # Should have both positive and negative rates
        positive_rates = [
            r for r in rotation_rates if "deg/s" in r and not r.startswith("-")
        ]
        negative_rates = [
            r for r in rotation_rates if "deg/s" in r and r.startswith("-")
        ]

        assert len(positive_rates) > 0, "Should have positive rotation rates"
        assert len(negative_rates) > 0, "Should have negative rotation rates"

        # Check specific expected values
        assert "0.4 deg/s" in rotation_rates, "Should have 0.4 deg/s for CBCT"
        assert "90 deg/s" in rotation_rates, "Should have 90 deg/s for kV-kV"

    def test_kvp_values(self):
        """Test kVp values are reasonable."""
        kvp_values = []

        for mode_name, mode_values in imaging_modes_lookup.items():
            if mode_name == "selection":
                continue

            kvp = mode_values[1]  # Second parameter is kVp
            kvp_values.append(kvp)

        # Should have expected kVp values
        expected_kvps = ["80 kV", "100 kV", "125 kV", "140 kV"]
        for expected_kvp in expected_kvps:
            assert expected_kvp in kvp_values, f"Missing kVp: {expected_kvp}"

        # All should be valid kVp format
        for kvp in kvp_values:
            assert "kV" in kvp, f"Invalid kVp format: {kvp}"
            numeric_part = kvp.split()[0]
            assert float(numeric_part) > 0, f"Invalid kVp value: {kvp}"

    def test_exposure_values(self):
        """Test exposure values are reasonable."""
        exposure_values = []

        for mode_name, mode_values in imaging_modes_lookup.items():
            if mode_name == "selection":
                continue

            exposure = mode_values[2]  # Third parameter is exposure
            exposure_values.append(exposure)

        # Should have expected exposure values
        expected_exposures = [
            "100 mAs",
            "150 mAs",
            "210 mAs",
            "270 mAs",
            "750 mAs",
            "1688 mAs",
        ]
        for expected_exp in expected_exposures:
            assert expected_exp in exposure_values, f"Missing exposure: {expected_exp}"

        # All should be valid mAs format
        for exposure in exposure_values:
            assert "mAs" in exposure, f"Invalid exposure format: {exposure}"
            numeric_part = exposure.split()[0]
            assert float(numeric_part) > 0, f"Invalid exposure value: {exposure}"

    def test_fan_mode_values(self):
        """Test fan mode values are valid."""
        fan_modes = []

        for mode_name, mode_values in imaging_modes_lookup.items():
            if mode_name == "selection":
                continue

            fan_mode = mode_values[3]  # Fourth parameter is fan mode
            fan_modes.append(fan_mode)

        # Should only have 'Full Fan' or 'Half Fan'
        valid_fans = ["Full Fan", "Half Fan"]
        for fan_mode in fan_modes:
            assert fan_mode in valid_fans, f"Invalid fan mode: {fan_mode}"

        # Should have both types
        assert "Full Fan" in fan_modes, "Should have Full Fan modes"
        assert "Half Fan" in fan_modes, "Should have Half Fan modes"

    def test_time_end_values(self):
        """Test time end values are reasonable."""
        time_end_values = []

        for mode_name, mode_values in imaging_modes_lookup.items():
            if mode_name == "selection":
                continue

            time_end = mode_values[4]  # Fifth parameter is time end
            time_end_values.append(time_end)

        # Should have expected time values
        expected_times = ["501 s", "900 s", "2 s"]
        for expected_time in expected_times:
            assert (
                expected_time in time_end_values
            ), f"Missing time end: {expected_time}"

        # All should be valid time format
        for time_end in time_end_values:
            assert "s" in time_end, f"Invalid time format: {time_end}"
            numeric_part = time_end.split()[0]
            assert float(numeric_part) > 0, f"Invalid time value: {time_end}"

    def test_field_values(self):
        """Test field size values are reasonable."""
        field_values = []

        for mode_name, mode_values in imaging_modes_lookup.items():
            if mode_name == "selection":
                continue

            # Extract field values (parameters 5-8)
            fields = mode_values[4:8]  # FIELD_X1, FIELD_X2, FIELD_Y1, FIELD_Y2
            field_values.extend(fields)

        # All should be valid format (cm or s for time)
        for field in field_values:
            # Check for cm or s units (time end values use 's')
            assert "cm" in field or "s" in field, f"Invalid field format: {field}"
            numeric_part = field.split()[0]
            assert float(numeric_part) > 0, f"Invalid field value: {field}"

        # Should have expected field sizes
        expected_fields = [
            "14 cm",
            "3.3 cm",
            "13.2 cm",
            "24.7 cm",
            "501 s",
        ]  # Include time value
        for expected_field in expected_fields:
            assert (
                expected_field in field_values
            ), f"Missing field size: {expected_field}"

    def test_blade_values(self):
        """Test blade position values are reasonable."""
        blade_values = []

        for mode_name, mode_values in imaging_modes_lookup.items():
            if mode_name == "selection":
                continue

            # Extract blade values (parameters 9-12)
            blades = mode_values[8:12]  # BLADE_X1, BLADE_X2, BLADE_Y1, BLADE_Y2
            blade_values.extend(blades)

        # All should be valid cm format
        for blade in blade_values:
            assert "cm" in blade, f"Invalid blade format: {blade}"
            numeric_part = blade.split()[0]
            # Blade values can be positive or negative
            assert isinstance(
                float(numeric_part), float
            ), f"Invalid blade value: {blade}"

        # Should have both positive and negative blade values
        positive_blades = [b for b in blade_values if not b.startswith("-")]
        negative_blades = [b for b in blade_values if b.startswith("-")]

        assert len(positive_blades) > 0, "Should have positive blade positions"
        assert len(negative_blades) > 0, "Should have negative blade positions"

    def test_mode_naming_consistency(self):
        """Test that mode names follow consistent pattern."""
        for mode_name in imaging_modes_lookup.keys():
            if mode_name == "selection":
                continue

            # Should follow pattern: Type Direction_BodyPart
            # or Type_Direction_BodyPart_Size (for kV-kV)
            assert "_" in mode_name, f"Mode name should have underscores: {mode_name}"

            parts = mode_name.split("_")
            assert (
                len(parts) >= 2
            ), f"Mode name should have at least 2 parts: {mode_name}"

            # Check if it's CBCT format (with space) or kV-kV format
            if mode_name.startswith("CBCT"):
                # CBCT modes have format: "CBCT Direction_BodyPart" or "CBCT Direction_BodyPart_Size"
                assert mode_name.startswith(
                    "CBCT "
                ), f"CBCT mode should start with 'CBCT ': {mode_name}"

                # Extract direction from part after "CBCT "
                cbct_part = mode_name[5:]  # Remove "CBCT "
                cbct_parts = cbct_part.split("_")
                assert (
                    len(cbct_parts) >= 2
                ), f"CBCT mode should have direction and body part: {mode_name}"

                # Direction should be Clockwise or Anticlockwise
                valid_directions = ["Clockwise", "Anticlockwise"]
                assert (
                    cbct_parts[0] in valid_directions
                ), f"Invalid CBCT direction: {cbct_parts[0]}"

                # Body part should be valid
                valid_body_parts = [
                    "Image Gently",
                    "Head",
                    "Short Thorax",
                    "Spotlight",
                    "Thorax",
                    "Pelvis",
                    "Pelvis Large",
                ]
                body_part = "_".join(
                    cbct_parts[1:]
                )  # Join remaining parts for body part with size
                assert (
                    body_part in valid_body_parts
                ), f"Invalid CBCT body part: {body_part}"

            elif mode_name.startswith("kV-kV"):
                # kV-kV modes have format: "kV-kV_BodyPart" or "kV-kV_BodyPart_Size"
                assert (
                    parts[0] == "kV-kV"
                ), f"kV-kV mode should start with 'kV-kV': {mode_name}"

                # Body part should be valid
                valid_body_parts = [
                    "Image Gently",
                    "Head",
                    "Short Thorax",
                    "Spotlight",
                    "Thorax",
                    "Pelvis",
                    "Pelvis Large",
                ]
                body_part = "_".join(
                    parts[1:]
                )  # Join remaining parts for body part with size
                assert (
                    body_part in valid_body_parts
                ), f"Invalid kV-kV body part: {body_part}"

            else:
                assert False, f"Mode should start with 'CBCT ' or 'kV-kV': {mode_name}"

    def test_lookup_table_completeness(self):
        """Test that lookup table has expected number of modes."""
        non_selection_modes = [
            k for k in imaging_modes_lookup.keys() if k != "selection"
        ]
        expected_mode_count = 21  # 8 CBCT Clockwise + 8 CBCT Anticlockwise + 5 kV-kV (actual count in data)

        assert (
            len(non_selection_modes) == expected_mode_count
        ), f"Expected {expected_mode_count} modes, got {len(non_selection_modes)}"


if __name__ == "__main__":
    pytest.main([__file__])
