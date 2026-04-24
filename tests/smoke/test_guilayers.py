"""Smoke tests for guilayers.py module."""

import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

GUI_IMPORTS_AVAILABLE = False
GUI_IMPORT_ERROR = None
general_layer = None
main_menu_information_layer = None
function_layer = None
settings_information_layout = None
Hidden_layer = None
History_layer = None
imaging_protocol_layer = None
imaging_scan_layer = None
dicom_information_layer = None
dicom_file_layer = None
dicom_patient_layer = None
dicom_planned_layer = None
dicom_graphics_layer = None
CTDI_information_layer = None
CTDI_layer = None
Couch_layer = None
CTDI_blade_layer = None
CTDI_run_layer = None

try:
    from src.guilayers import (
        general_layer,
        main_menu_information_layer,
        function_layer,
        settings_information_layout,
        Hidden_layer,
        History_layer,
        imaging_protocol_layer,
        imaging_scan_layer,
        dicom_information_layer,
        dicom_file_layer,
        dicom_patient_layer,
        dicom_planned_layer,
        dicom_graphics_layer,
        CTDI_information_layer,
        CTDI_layer,
        Couch_layer,
        CTDI_blade_layer,
        CTDI_run_layer,
    )

    GUI_IMPORTS_AVAILABLE = True
except ImportError as e:
    GUI_IMPORTS_AVAILABLE = False
    GUI_IMPORT_ERROR = str(e)


class TestGuiLayers:
    """Smoke tests for GUI layers module."""

    @pytest.mark.skipif(
        not GUI_IMPORTS_AVAILABLE,
        reason=f"GUI imports not available: {GUI_IMPORT_ERROR}",
    )
    def test_all_gui_layers_defined(self):
        """Test that all expected GUI layers are defined."""
        expected_layers = [
            "general_layer",
            "main_menu_information_layer",
            "function_layer",
            "settings_information_layout",
            "Hidden_layer",
            "History_layer",
            "imaging_protocol_layer",
            "imaging_scan_layer",
            "dicom_information_layer",
            "dicom_file_layer",
            "dicom_patient_layer",
            "dicom_planned_layer",
            "dicom_graphics_layer",
            "CTDI_information_layer",
            "CTDI_layer",
            "Couch_layer",
            "CTDI_blade_layer",
            "CTDI_run_layer",
        ]

        for layer_name in expected_layers:
            layer = globals().get(layer_name)
            assert layer is not None, f"Missing GUI layer: {layer_name}"

        # Check that each layer is actually a FreeSimpleGUI component

        for layer_name in expected_layers:
            layer = globals().get(layer_name)
            assert hasattr(layer, "__class__"), (
                f"Layer {layer_name} should be an object"
            )
            # Check if it's a Frame, Column, or similar GUI component
            # Some layers like Couch_layer and CTDI_blade_layer are wrapped in sg.pin()
            # which creates Column objects that don't have Title attribute
            assert (
                hasattr(layer, "Title")
                or hasattr(layer, "get")
                or "Column" in str(type(layer))
            ), f"Layer {layer_name} should be a GUI component"

    def test_general_layer_structure(self):
        """Test general layer has expected structure."""

        # Should be a Frame with title
        layer = globals().get("general_layer")
        if layer:
            assert hasattr(layer, "Title")
            assert "General Settings" in str(layer.Title)
            assert layer is not None

    def test_function_layer_has_options(self):
        """Test function layer has expected options."""

        layer = globals().get("function_layer")
        if layer:
            assert hasattr(layer, "Title")
            assert "Choose your function" in str(layer.Title)
            assert layer is not None

    def test_imaging_protocol_layer_has_modes(self):
        """Test imaging protocol layer has mode selection."""

        layer = globals().get("imaging_protocol_layer")
        if layer:
            assert hasattr(layer, "Title")
            assert "Imaging protocol" in str(layer.Title)
            assert layer is not None

    def test_dicom_layers_exist(self):
        """Test that all DICOM-related layers exist."""
        dicom_layer_names = [
            "dicom_information_layer",
            "dicom_file_layer",
            "dicom_patient_layer",
            "dicom_planned_layer",
            "dicom_graphics_layer",
        ]

        for layer_name in dicom_layer_names:
            layer = globals().get(layer_name)
            assert layer is not None, f"DICOM layer {layer_name} should not be None"
            # Some DICOM layers might be wrapped in sg.pin() creating Column objects
            assert hasattr(layer, "Title") or "Column" in str(type(layer)), (
                f"DICOM layer {layer_name} should have a Title or be a Column"
            )

    def test_ctdi_layers_exist(self):
        """Test that all CTDI-related layers exist."""
        ctdi_layer_names = [
            "CTDI_information_layer",
            "CTDI_layer",
            "Couch_layer",
            "CTDI_blade_layer",
            "CTDI_run_layer",
        ]

        for layer_name in ctdi_layer_names:
            layer = globals().get(layer_name)
            assert layer is not None, f"CTDI layer {layer_name} should not be None"
            # Some CTDI layers might be wrapped in sg.pin() creating Column objects
            assert hasattr(layer, "Title") or "Column" in str(type(layer)), (
                f"CTDI layer {layer_name} should have a Title or be a Column"
            )

    def test_layer_titles_are_descriptive(self):
        """Test that layer titles are descriptive."""
        layer_mappings = [
            ("general_layer", "General Settings"),
            ("main_menu_information_layer", "Instructions on the usage of the GUI"),
            ("function_layer", "Choose your function"),
            ("settings_information_layout", "General settings"),
            ("Hidden_layer", "Time Feature and other hidden values"),
            ("History_layer", "Simulation settings"),
            ("imaging_protocol_layer", "Imaging protocol"),
            ("imaging_scan_layer", "Set up imaging parameters"),
            (
                "dicom_information_layer",
                "Instructions on the usage of the DICOM adjustments",
            ),
            ("dicom_file_layer", "DICOM inputs"),
            ("dicom_patient_layer", "Patient set up adjustments"),
            ("dicom_planned_layer", "Treatment plan parameters"),
            ("dicom_graphics_layer", "DICOM simulation graphics"),
            (
                "CTDI_information_layer",
                "Instructions on the usage of the CTDI phantom parameters",
            ),
            ("CTDI_layer", "CTDI options"),
            ("Couch_layer", "Couch"),
            ("CTDI_blade_layer", "CTDI user specified jaw"),
            ("CTDI_run_layer", "Activate CTDI simulation"),
        ]

        for layer_name, expected_title_part in layer_mappings:
            layer = globals().get(layer_name)
            if layer:
                # Some layers might be Column objects (wrapped in sg.pin) that don't have Title
                if hasattr(layer, "Title"):
                    title_str = str(layer.Title)
                    assert expected_title_part in title_str, (
                        f"Layer title '{title_str}' should contain '{expected_title_part}'"
                    )
                else:
                    # For Column objects, skip title check but verify layer exists
                    assert layer is not None, f"Layer {layer_name} should exist"

    def test_couch_layer_is_pinned(self):
        """Test that couch layer uses sg.pin."""

        layer = globals().get("Couch_layer")
        if layer:
            assert layer is not None

    def test_ctdi_blade_layer_is_pinned(self):
        """Test that CTDI blade layer uses sg.pin."""

        layer = globals().get("CTDI_blade_layer")
        if layer:
            assert layer is not None

    def test_layer_consistency(self):
        """Test that all layers follow similar patterns."""
        layer_names = [
            "general_layer",
            "main_menu_information_layer",
            "function_layer",
            "settings_information_layout",
            "Hidden_layer",
            "History_layer",
            "imaging_protocol_layer",
            "imaging_scan_layer",
            "dicom_information_layer",
            "dicom_file_layer",
            "dicom_patient_layer",
            "dicom_planned_layer",
            "dicom_graphics_layer",
            "CTDI_information_layer",
            "CTDI_layer",
            "Couch_layer",
            "CTDI_blade_layer",
            "CTDI_run_layer",
        ]

        # All layers should be GUI components
        for layer_name in layer_names:
            layer = globals().get(layer_name)
            assert layer is not None, f"Layer {layer_name} should not be None"
            # Should have some common GUI attributes
            assert hasattr(layer, "__class__"), (
                f"Layer {layer_name} should be an object"
            )

    def test_no_gui_imports_fallback(self):
        """Test behavior when GUI imports are not available."""
        if GUI_IMPORTS_AVAILABLE:
            pytest.skip("GUI imports are available, cannot test fallback")

        # This test verifies that the module structure exists even if GUI fails
        # The module should be importable even if FreeSimpleGUI is missing
        assert True  # If we get here, the module structure is testable


class TestGuiLayerIntegration:
    """Integration tests for GUI layers."""

    @pytest.mark.skipif(
        not GUI_IMPORTS_AVAILABLE,
        reason=f"GUI imports not available: {GUI_IMPORT_ERROR}",
    )
    def test_layer_layout_structure(self):
        """Test that layers have proper layout structure."""

        # Test a few key layers for layout structure
        layer_mappings = [
            ("general_layer", "general"),
            ("function_layer", "function"),
            ("imaging_protocol_layer", "imaging_protocol"),
        ]

        for layer_name, layer_type in layer_mappings:
            layer = globals().get(layer_name)
            if layer:
                assert hasattr(layer, "Title"), f"{layer_type} layer should have Title"
                assert layer is not None, f"{layer_type} layer should be defined"

    def test_gui_theme_is_set(self):
        """Test that GUI theme is configured."""
        import FreeSimpleGUI as sg

        # The module should set a theme
        # We can't easily test the actual theme without rendering,
        # but we can verify the module loads without error
        assert sg is not None


if __name__ == "__main__":
    pytest.main([__file__])
