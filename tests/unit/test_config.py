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
from src.gui.adapter import config_to_gui, gui_to_config
from src.models.quantity import Quantity


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
        assert config.dicom.isocenter_x == Quantity(0.0, "mm")
        assert config.dicom.isocenter_y == Quantity(0.0, "mm")
        assert config.dicom.isocenter_z == Quantity(0.0, "mm")
        assert config.dicom.patient_shift_x == Quantity(0.0, "mm")
        assert config.dicom.patient_shift_y == Quantity(0.0, "mm")
        assert config.dicom.patient_shift_z == Quantity(0.0, "mm")
        assert config.dicom.patient_yaw == Quantity(0.0, "deg")
        assert config.dicom.patient_pitch == Quantity(0.0, "deg")
        assert config.dicom.patient_roll == Quantity(0.0, "deg")

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

    def test_yaml_roundtrip_preserves_nondefault_quantities(
        self, tmp_path: Any
    ) -> None:
        from src.config import CtdiConfig, DicomConfig, ImagingConfig

        config = SimulationConfig(
            imaging=ImagingConfig(anode_voltage="80 kV", start_angle="45 deg"),
            dicom=DicomConfig(
                isocenter_x="10.5 mm",
                patient_pitch="2 deg",
                patient_roll="-5 deg",
            ),
            ctdi=CtdiConfig(couch_width="300 mm"),
        )
        path = str(tmp_path / "test_roundtrip.yaml")
        config.to_yaml(path)
        loaded = SimulationConfig.from_yaml(path)
        assert loaded.imaging.anode_voltage == Quantity(80.0, "kV")
        assert loaded.imaging.start_angle == Quantity(45.0, "deg")
        assert loaded.dicom.isocenter_x == Quantity(10.5, "mm")
        assert loaded.dicom.patient_pitch == Quantity(2.0, "deg")
        assert loaded.dicom.patient_roll == Quantity(-5.0, "deg")
        assert loaded.ctdi.couch_width == Quantity(300.0, "mm")


class TestSimulationConfigFromGuiValues:
    def test_creates_config_from_gui_dict(self) -> None:
        values: Dict[str, str] = {
            "-G4_DATA_DIR-": "/g4",
            "-TOPAS_DIR-": "/topas",
            "-SEED-": "42",
            "-THREADS-": "4",
            "-HISTORIES-": "500000",
            "-SIM_TYPE-": "CTDI",
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
            "-PATIENT_PITCH-": "2 deg",
            "-PATIENT_ROLL-": "-5 deg",
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
        config: SimulationConfig = gui_to_config(values)
        assert config.general.g4_data_directory == "/g4"
        assert config.general.seed == "42"
        assert config.imaging.simulation_type == "CTDI"
        assert config.imaging.fan_mode == "Half Fan"
        assert config.dicom.patient_id == "PAT001"
        assert config.dicom.patient_yaw == Quantity(90.0, "deg")
        assert config.dicom.patient_pitch == Quantity(2.0, "deg")
        assert config.dicom.patient_roll == Quantity(-5.0, "deg")
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
        config: SimulationConfig = gui_to_config(values)
        assert config.dicom.graphics_enabled is True
        assert config.ctdi.couch_enabled is True
        assert config.ctdi.user_blade_enabled is True
        assert config.ctdi.graphics_enabled is True

    def test_missing_keys_use_defaults(self) -> None:
        config: SimulationConfig = gui_to_config({})
        assert config.general.seed == "9"
        assert config.general.threads == "1"
        assert config.imaging.fan_mode == "Full Fan"
        assert config.ctdi.phantom_size == "16 cm"
        assert config.dicom.dicom_directory == "/sampledicom/setA"


class TestConfigToGui:
    def test_config_to_gui_has_all_expected_keys(self) -> None:
        config: SimulationConfig = SimulationConfig.defaults()
        d: Dict[str, str] = config_to_gui(config)
        assert "-G4_DATA_DIR-" in d
        assert "-TOPAS_DIR-" in d
        assert "-SEED-" in d
        assert "-THREADS-" in d
        assert "-HISTORIES-" in d
        assert "-SIM_TYPE-" in d
        assert "-FAN_MODE-" in d
        assert "-CTDI_PHANTOM-" in d
        assert "-COUCH_ENABLED-" in d
        assert "-PATIENT_YAW-" in d
        assert "-PATIENT_PITCH-" in d
        assert "-PATIENT_ROLL-" in d

    def test_config_to_gui_values_match_config_fields(self) -> None:
        config: SimulationConfig = SimulationConfig.defaults()
        d: Dict[str, str] = config_to_gui(config)
        assert d["-SEED-"] == config.general.seed
        assert d["-THREADS-"] == config.general.threads
        assert d["-HISTORIES-"] == config.general.histories
        assert d["-FAN_MODE-"] == config.imaging.fan_mode
        assert d["-CTDI_PHANTOM-"] == config.ctdi.phantom_size
        assert d["-TUBE_VOLTAGE-"] == str(config.imaging.anode_voltage)
        assert d["-EXPOSURE-"] == str(config.imaging.exposure)
        assert d["-ISO_X-"] == str(config.dicom.isocenter_x)
        assert d["-COUCH_WIDTH-"] == str(config.ctdi.couch_width)


class TestParseBool:
    def test_true_bool_is_true(self) -> None:
        from src.gui.adapter import _parse_bool

        assert _parse_bool(True) is True

    def test_true_string_is_true(self) -> None:
        from src.gui.adapter import _parse_bool

        assert _parse_bool("True") is True

    def test_false_bool_is_false(self) -> None:
        from src.gui.adapter import _parse_bool

        assert _parse_bool(False) is False

    def test_false_string_is_false(self) -> None:
        from src.gui.adapter import _parse_bool

        assert _parse_bool("False") is False

    def test_integer_one_is_true(self) -> None:
        from src.gui.adapter import _parse_bool

        assert _parse_bool(1) is True

    def test_integer_zero_is_false(self) -> None:
        from src.gui.adapter import _parse_bool

        assert _parse_bool(0) is False

    def test_empty_string_is_false(self) -> None:
        from src.gui.adapter import _parse_bool

        assert _parse_bool("") is False

    def test_lowercase_true_is_true(self) -> None:
        from src.gui.adapter import _parse_bool

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


class TestConfigYamlPath:
    def test_from_yaml_stores_absolute_path(self, tmp_path: Any) -> None:
        config_file = tmp_path / "my_config.yaml"
        config_file.write_text(
            "general:\n  g4_data_directory: /g4\n  topas_directory: /topas\n"
        )
        config: SimulationConfig = SimulationConfig.from_yaml(str(config_file))
        assert config.config_yaml_path == os.path.abspath(str(config_file))

    def test_gui_to_config_has_no_yaml_path(self) -> None:
        config: SimulationConfig = gui_to_config({})
        assert config.config_yaml_path is None

    def test_defaults_is_none(
        self, tmp_path: Any, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)
        config: SimulationConfig = SimulationConfig.defaults()
        assert config.config_yaml_path is None

    def test_direct_construction_is_none(self) -> None:
        config = SimulationConfig()
        assert config.config_yaml_path is None


class TestQuantityCoercion:
    def test_imaging_coerces_strings(self) -> None:
        from src.config import ImagingConfig

        cfg = ImagingConfig(
            anode_voltage="80 kV", exposure="200 mAs", rotation_rate="0.6 deg/s"
        )
        assert cfg.anode_voltage == Quantity(80.0, "kV")
        assert cfg.exposure == Quantity(200.0, "mAs")
        assert cfg.rotation_rate == Quantity(0.6, "deg/s")

    def test_dicom_coerces_strings(self) -> None:
        from src.config import DicomConfig

        cfg = DicomConfig(
            isocenter_x="10 mm",
            patient_yaw="90 deg",
            patient_pitch="2 deg",
            patient_roll="-5 deg",
        )
        assert cfg.isocenter_x == Quantity(10.0, "mm")
        assert cfg.patient_yaw == Quantity(90.0, "deg")
        assert cfg.patient_pitch == Quantity(2.0, "deg")
        assert cfg.patient_roll == Quantity(-5.0, "deg")

    def test_ctdi_coerces_strings(self) -> None:
        from src.config import CtdiConfig

        cfg = CtdiConfig(couch_width="300 mm", user_field_x1="12 cm")
        assert cfg.couch_width == Quantity(300.0, "mm")
        assert cfg.user_field_x1 == Quantity(12.0, "cm")

    def test_quantity_inputs_pass_through(self) -> None:
        from src.config import ImagingConfig

        q = Quantity(80.0, "kV")
        cfg = ImagingConfig(anode_voltage=q)
        assert cfg.anode_voltage is q


class TestVoltageRangeValidation:
    def test_voltage_below_range_raises(self) -> None:
        from src.config import ImagingConfig

        config = SimulationConfig(imaging=ImagingConfig(anode_voltage="30 kV"))
        with pytest.raises(ValueError, match="40-150 kV"):
            config.validate()

    def test_voltage_above_range_raises(self) -> None:
        from src.config import ImagingConfig

        config = SimulationConfig(imaging=ImagingConfig(anode_voltage="200 kV"))
        with pytest.raises(ValueError, match="40-150 kV"):
            config.validate()

    def test_voltage_at_lower_bound_passes(self) -> None:
        from src.config import ImagingConfig

        config = SimulationConfig(imaging=ImagingConfig(anode_voltage="40 kV"))
        config.validate()

    def test_voltage_at_upper_bound_passes(self) -> None:
        from src.config import ImagingConfig

        config = SimulationConfig(imaging=ImagingConfig(anode_voltage="150 kV"))
        config.validate()


class TestExposureValidation:
    def test_negative_exposure_raises(self) -> None:
        from src.config import ImagingConfig

        config = SimulationConfig(imaging=ImagingConfig(exposure="-10 mAs"))
        with pytest.raises(ValueError, match="positive"):
            config.validate()

    def test_zero_exposure_raises(self) -> None:
        from src.config import ImagingConfig

        config = SimulationConfig(imaging=ImagingConfig(exposure="0 mAs"))
        with pytest.raises(ValueError, match="positive"):
            config.validate()

    def test_positive_exposure_passes(self) -> None:
        from src.config import ImagingConfig

        config = SimulationConfig(imaging=ImagingConfig(exposure="100 mAs"))
        config.validate()


class TestPhaseSpaceConfig:
    def test_default_mode_is_off(self) -> None:
        from src.config import CtdiConfig

        config = CtdiConfig()
        assert config.phase_space_mode == "off"
        assert config.phase_space_file == ""
        assert config.phase_space_multiple_use == 1

    def test_off_mode_passes_validation(self) -> None:
        from src.config import CtdiConfig

        config = SimulationConfig(ctdi=CtdiConfig(phase_space_mode="off"))
        config.validate()

    def test_score_mode_passes_validation(self) -> None:
        from src.config import CtdiConfig

        config = SimulationConfig(ctdi=CtdiConfig(phase_space_mode="score"))
        config.validate()

    def test_replay_without_file_raises(self) -> None:
        from src.config import CtdiConfig

        config = SimulationConfig(
            ctdi=CtdiConfig(phase_space_mode="replay", phase_space_file="")
        )
        with pytest.raises(ValueError, match="phase_space_file is required"):
            config.validate()

    def test_replay_with_nonexistent_file_raises(self) -> None:
        from src.config import CtdiConfig

        config = SimulationConfig(
            ctdi=CtdiConfig(
                phase_space_mode="replay",
                phase_space_file="/nonexistent/path.phsp",
            )
        )
        with pytest.raises(ValueError, match="does not exist"):
            config.validate()

    def test_replay_with_existing_file_passes(self, tmp_path: Any) -> None:
        from src.config import CtdiConfig

        phsp_file = tmp_path / "beam.phsp"
        phsp_file.write_bytes(b"\x00" * 100)
        config = SimulationConfig(
            ctdi=CtdiConfig(
                phase_space_mode="replay",
                phase_space_file=str(phsp_file),
            )
        )
        config.validate()

    def test_invalid_mode_raises(self) -> None:
        from src.config import CtdiConfig

        config = SimulationConfig(ctdi=CtdiConfig(phase_space_mode="invalid"))
        with pytest.raises(ValueError, match="phase_space_mode must be one of"):
            config.validate()

    def test_multiple_use_zero_raises(self) -> None:
        from src.config import CtdiConfig

        config = SimulationConfig(ctdi=CtdiConfig(phase_space_multiple_use=0))
        with pytest.raises(ValueError, match="phase_space_multiple_use must be >= 1"):
            config.validate()

    def test_multiple_use_negative_raises(self) -> None:
        from src.config import CtdiConfig

        config = SimulationConfig(ctdi=CtdiConfig(phase_space_multiple_use=-5))
        with pytest.raises(ValueError, match="phase_space_multiple_use must be >= 1"):
            config.validate()

    def test_yaml_roundtrip_phase_space(self) -> None:
        from src.config import CtdiConfig

        config = SimulationConfig(
            ctdi=CtdiConfig(
                phase_space_mode="score",
                phase_space_multiple_use=10,
            )
        )
        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False, mode="w") as f:
            path: str = f.name
        try:
            config.to_yaml(path)
            loaded = SimulationConfig.from_yaml(path)
            assert loaded.ctdi.phase_space_mode == "score"
            assert loaded.ctdi.phase_space_multiple_use == 10
            assert loaded.ctdi.phase_space_file == ""
        finally:
            os.unlink(path)
