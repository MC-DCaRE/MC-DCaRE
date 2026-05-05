from __future__ import annotations

import os
import sys
import tempfile
from typing import Any, Dict

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.config import (
    GeneralConfig,
    SimulationConfig,
    quantity_unit_stripper,
)


class TestQuantityUnitStripper:
    def test_splits_value_and_unit(self) -> None:
        result: tuple = quantity_unit_stripper("100 kV")
        assert result == (100.0, "kV")

    def test_raises_for_no_number(self) -> None:
        with pytest.raises(ValueError, match="No numeric value"):
            quantity_unit_stripper("kV")

    def test_returns_empty_unit_for_no_unit(self) -> None:
        result: tuple = quantity_unit_stripper("100")
        assert result == (100.0, "")

    def test_handles_compound_units(self) -> None:
        result: tuple = quantity_unit_stripper("0.4 deg/s")
        assert result == (0.4, "deg/s")

    def test_handles_negative(self) -> None:
        result: tuple = quantity_unit_stripper("-5 mm")
        assert result == (-5.0, "mm")


class TestSimulationConfigDefaults:
    def test_defaults_returns_config_with_env_vars(
        self, tmp_path: Any, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("G4DATA_DIR", "/custom/g4data")
        monkeypatch.setenv("TOPAS_DIR", "/custom/topas")
        config: SimulationConfig = SimulationConfig.defaults()
        assert config.general.g4_data_directory == "/custom/g4data"
        assert config.general.topas_directory == "/custom/topas"

    def test_defaults_general_has_nonempty_fields(self) -> None:
        config: SimulationConfig = SimulationConfig.defaults()
        assert config.general.g4_data_directory != ""
        assert config.general.topas_directory != ""
        assert config.general.seed != ""
        assert config.general.threads != ""
        assert config.general.histories != ""
        assert config.general.dose_calibration_factor != ""

    def test_defaults_imaging_fan_mode_is_valid(self) -> None:
        config: SimulationConfig = SimulationConfig.defaults()
        assert config.imaging.fan_mode in ("Full Fan", "Half Fan")

    def test_defaults_dicom_coordinates_are_zero(self) -> None:
        config: SimulationConfig = SimulationConfig.defaults()
        assert config.dicom.isocenter_x == "0 mm"
        assert config.dicom.isocenter_y == "0 mm"
        assert config.dicom.isocenter_z == "0 mm"
        assert config.dicom.patient_shift_x == "0. mm"
        assert config.dicom.patient_shift_y == "0. mm"
        assert config.dicom.patient_shift_z == "0. mm"

    def test_defaults_ctdi_couch_enabled_is_true(self) -> None:
        config: SimulationConfig = SimulationConfig.defaults()
        assert config.ctdi.couch_enabled is True

    def test_defaults_reads_config_yaml_over_env(
        self, tmp_path: Any, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("G4DATA_DIR", "/env/g4data")
        monkeypatch.setenv("TOPAS_DIR", "/env/topas")
        config_yaml = tmp_path / "config.yaml"
        config_yaml.write_text(
            "general:\n"
            "  g4_data_directory: /from/file/g4data\n"
            "  topas_directory: /from/file/topas\n"
        )
        config: SimulationConfig = SimulationConfig.defaults()
        assert config.general.g4_data_directory == "/from/file/g4data"
        assert config.general.topas_directory == "/from/file/topas"

    def test_defaults_falls_back_to_env_when_no_config_yaml(
        self, tmp_path: Any, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("G4DATA_DIR", "/env/g4data")
        monkeypatch.setenv("TOPAS_DIR", "/env/topas")
        config: SimulationConfig = SimulationConfig.defaults()
        assert config.general.g4_data_directory == "/env/g4data"
        assert config.general.topas_directory == "/env/topas"


class TestSimulationConfigYamlRoundTrip:
    def test_to_yaml_and_from_yaml_roundtrip(self) -> None:
        config: SimulationConfig = SimulationConfig.defaults()
        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False, mode="w") as f:
            path: str = f.name
        try:
            config.to_yaml(path)
            loaded: SimulationConfig = SimulationConfig.from_yaml(path)
            assert loaded.general.g4_data_directory == config.general.g4_data_directory
            assert loaded.general.seed == config.general.seed
            assert loaded.imaging.fan_mode == config.imaging.fan_mode
            assert loaded.ctdi.phantom_size == config.ctdi.phantom_size
            assert loaded.dicom.graphics_enabled == config.dicom.graphics_enabled
        finally:
            os.unlink(path)

    def test_from_yaml_missing_sections_uses_defaults(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False, mode="w") as f:
            f.write("general:\n  seed: '42'\n")
            path: str = f.name
        try:
            loaded: SimulationConfig = SimulationConfig.from_yaml(path)
            assert loaded.general.seed == "42"
            assert loaded.general.threads == "1"
            assert loaded.imaging.fan_mode == "Full Fan"
            assert loaded.ctdi.phantom_size == "16 cm"
        finally:
            os.unlink(path)


class TestSimulationConfigFromGuiValues:
    def test_creates_config_from_gui_dict(self) -> None:
        values: Dict[str, str] = {
            "-G4_DATA_DIR-": "/g4",
            "-TOPAS_DIR-": "/topas",
            "-SEED-": "42",
            "-THREADS-": "4",
            "-HISTORIES-": "500000",
            "-SIM_TYPE-": "CTDI validation",
            "-START_ANGLE-": "90 deg",
            "-SCAN_TYPE-": "CBCT Counter-Clockwise",
            "-TUBE_VOLTAGE-": "80 kV",
            "-EXPOSURE-": "200 mAs",
            "-FAN_MODE-": "Half Fan",
            "-IMAGING_MODE-": "Standard",
            "-ROTATION_RATE-": "0.6 deg/s",
            "-TIMELINE_END-": "600.0 s",
            "-SEQ_TIMES-": "2000",
            "-TIME_VERBOSITY-": "1",
            "-FIELD_X1-": "10 cm",
            "-FIELD_X2-": "10 cm",
            "-FIELD_Y1-": "5 cm",
            "-FIELD_Y2-": "5 cm",
            "-BLADE_X1-": "3.0 cm",
            "-BLADE_X2-": "-3.0 cm",
            "-BLADE_Y1-": "2.0 cm",
            "-BLADE_Y2-": "-2.0 cm",
            "-DICOM_DIR-": "/dicom/path",
            "-DICOM_RP-": "/dicom/rp.dcm",
            "-PATIENT_ID-": "PAT001",
            "-ISO_X-": "1.0 mm",
            "-ISO_Y-": "2.0 mm",
            "-ISO_Z-": "3.0 mm",
            "-SHIFT_X-": "0.5 mm",
            "-SHIFT_Y-": "0.5 mm",
            "-SHIFT_Z-": "0.5 mm",
            "-PATIENT_YAW-": "90. deg",
            "-DICOM_GRAPHICS-": "False",
            "-CTDI_PHANTOM-": "32 cm",
            "-DTM_ZBINS-": "200",
            "-TLE_ZBINS-": "200",
            "-DTW_ZBINS-": "200",
            "-COUCH_ENABLED-": "False",
            "-COUCH_WIDTH-": "300. mm",
            "-COUCH_THICKNESS-": "0.5 mm",
            "-COUCH_LENGTH-": "1200 mm",
            "-CTDI_USER_BLADE-": "True",
            "-CTDI_FIELD_X1-": "12 cm",
            "-CTDI_FIELD_X2-": "12 cm",
            "-CTDI_FIELD_Y1-": "8 cm",
            "-CTDI_FIELD_Y2-": "8 cm",
            "-CTDI_GRAPHICS-": "True",
        }
        config: SimulationConfig = SimulationConfig.from_gui_values(values)
        assert config.general.g4_data_directory == "/g4"
        assert config.general.seed == "42"
        assert config.imaging.simulation_type == "CTDI validation"
        assert config.imaging.fan_mode == "Half Fan"
        assert config.dicom.patient_id == "PAT001"
        assert config.ctdi.phantom_size == "32 cm"
        assert config.ctdi.user_blade_enabled is True
        assert config.ctdi.graphics_enabled is True
        assert config.ctdi.couch_enabled is False

    def test_boolean_fields_from_true_string(self) -> None:
        values: Dict[str, str] = {
            "-DICOM_GRAPHICS-": "True",
            "-COUCH_ENABLED-": "True",
            "-CTDI_USER_BLADE-": "True",
            "-CTDI_GRAPHICS-": "True",
        }
        config: SimulationConfig = SimulationConfig.from_gui_values(values)
        assert config.dicom.graphics_enabled is True
        assert config.ctdi.couch_enabled is True
        assert config.ctdi.user_blade_enabled is True
        assert config.ctdi.graphics_enabled is True

    def test_missing_keys_use_defaults(self) -> None:
        config: SimulationConfig = SimulationConfig.from_gui_values({})
        assert config.general.seed == "9"
        assert config.general.threads == "1"
        assert config.imaging.fan_mode == "Full Fan"
        assert config.ctdi.phantom_size == "16 cm"
        assert config.dicom.dicom_directory == "/sampledicom/setA"


class TestSimulationConfigToDict:
    def test_to_dict_has_all_expected_keys(self) -> None:
        config: SimulationConfig = SimulationConfig.defaults()
        d: Dict[str, str] = config.to_dict()
        assert "-G4_DATA_DIR-" in d
        assert "-TOPAS_DIR-" in d
        assert "-SEED-" in d
        assert "-THREADS-" in d
        assert "-HISTORIES-" in d
        assert "-SIM_TYPE-" in d
        assert "-FAN_MODE-" in d
        assert "-CTDI_PHANTOM-" in d
        assert "-COUCH_ENABLED-" in d

    def test_to_dict_values_match_config_fields(self) -> None:
        config: SimulationConfig = SimulationConfig.defaults()
        d: Dict[str, str] = config.to_dict()
        assert d["-SEED-"] == config.general.seed
        assert d["-THREADS-"] == config.general.threads
        assert d["-HISTORIES-"] == config.general.histories
        assert d["-FAN_MODE-"] == config.imaging.fan_mode
        assert d["-CTDI_PHANTOM-"] == config.ctdi.phantom_size


class TestParseBool:
    def test_true_bool_is_true(self) -> None:
        from src.config import _parse_bool

        assert _parse_bool(True) is True

    def test_true_string_is_true(self) -> None:
        from src.config import _parse_bool

        assert _parse_bool("True") is True

    def test_false_bool_is_false(self) -> None:
        from src.config import _parse_bool

        assert _parse_bool(False) is False

    def test_false_string_is_false(self) -> None:
        from src.config import _parse_bool

        assert _parse_bool("False") is False

    def test_integer_one_is_true(self) -> None:
        from src.config import _parse_bool

        assert _parse_bool(1) is True

    def test_integer_zero_is_false(self) -> None:
        from src.config import _parse_bool

        assert _parse_bool(0) is False

    def test_empty_string_is_false(self) -> None:
        from src.config import _parse_bool

        assert _parse_bool("") is False

    def test_lowercase_true_is_true(self) -> None:
        from src.config import _parse_bool

        assert _parse_bool("true") is True


class TestDoseCalibrationFactor:
    def test_default_value(self) -> None:
        config = SimulationConfig()
        assert config.general.dose_calibration_factor == "1.0"

    def test_yaml_roundtrip(self) -> None:
        config = SimulationConfig(
            general=GeneralConfig(dose_calibration_factor="1.0523")
        )
        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False, mode="w") as f:
            path: str = f.name
        try:
            config.to_yaml(path)
            loaded = SimulationConfig.from_yaml(path)
            assert loaded.general.dose_calibration_factor == "1.0523"
        finally:
            os.unlink(path)

    def test_invalid_string_raises(self) -> None:
        config = SimulationConfig(
            general=GeneralConfig(dose_calibration_factor="not_a_number")
        )
        with pytest.raises(ValueError, match="must be a float"):
            config.validate()

    def test_negative_raises(self) -> None:
        config = SimulationConfig(general=GeneralConfig(dose_calibration_factor="-0.5"))
        with pytest.raises(ValueError, match="must be positive"):
            config.validate()

    def test_zero_raises(self) -> None:
        config = SimulationConfig(general=GeneralConfig(dose_calibration_factor="0"))
        with pytest.raises(ValueError, match="must be positive"):
            config.validate()

    def test_valid_positive_passes(self) -> None:
        config = SimulationConfig(general=GeneralConfig(dose_calibration_factor="1.05"))
        config.validate()

    def test_default_passes_validation(self) -> None:
        config = SimulationConfig()
        config.validate()
