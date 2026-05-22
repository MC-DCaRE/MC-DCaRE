"""Simulation configuration dataclasses and serialisation helpers.

Defines the configuration hierarchy (:class:`GeneralConfig`, :class:`ImagingConfig`,
:class:`DicomConfig`, :class:`CtdiConfig`) composed inside :class:`SimulationConfig`,
with round-trip support for YAML files and FreeSimpleGUI value dicts.

Dimensional fields (lengths, angles, voltages) are stored as :class:`Quantity` objects.
String values passed to constructors are automatically parsed into ``Quantity``.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Tuple, Type

import yaml

from src.models.enums import FanMode, PhantomSize, RotationDirection, SimulationType
from src.models.keys import (
    BLADE_X1,
    BLADE_X2,
    BLADE_Y1,
    BLADE_Y2,
    COUCH_ENABLED,
    COUCH_LENGTH,
    COUCH_THICKNESS,
    COUCH_WIDTH,
    CTDI_FIELD_X1,
    CTDI_FIELD_X2,
    CTDI_FIELD_Y1,
    CTDI_FIELD_Y2,
    CTDI_GRAPHICS,
    CTDI_PHANTOM,
    CTDI_USER_BLADE,
    DICOM_DIR,
    DICOM_GRAPHICS,
    DICOM_RP,
    DTM_ZBINS,
    DTW_ZBINS,
    EXPOSURE,
    FAN_MODE,
    FIELD_X1,
    FIELD_X2,
    FIELD_Y1,
    FIELD_Y2,
    G4_DATA_DIR,
    HISTORIES,
    IMAGING_MODE,
    ISO_X,
    ISO_Y,
    ISO_Z,
    PATIENT_ID,
    PATIENT_YAW,
    ROTATION_RATE,
    SCAN_TYPE,
    SEED,
    SEQ_TIMES,
    SHIFT_X,
    SHIFT_Y,
    SHIFT_Z,
    SIM_TYPE,
    THREADS,
    TIMELINE_END,
    TIME_VERBOSITY,
    TOPAS_DIR,
    TLE_ZBINS,
    TUBE_VOLTAGE,
    START_ANGLE,
)
from src.models.quantity import Quantity

logger = logging.getLogger(__name__)

_PLACEHOLDER_MAP: List[Tuple[str, str, str, Any]] = [
    ("general", "g4_data_directory", G4_DATA_DIR, ""),
    ("general", "topas_directory", TOPAS_DIR, ""),
    ("general", "seed", SEED, "9"),
    ("general", "threads", THREADS, "1"),
    ("general", "histories", HISTORIES, "100000"),
    ("imaging", "simulation_type", SIM_TYPE, "DICOM"),
    ("imaging", "start_angle", START_ANGLE, "0 deg"),
    ("imaging", "rotation_direction", SCAN_TYPE, "CBCT Clockwise"),
    ("imaging", "anode_voltage", TUBE_VOLTAGE, "100 kV"),
    ("imaging", "exposure", EXPOSURE, "100 mAs"),
    ("imaging", "fan_mode", FAN_MODE, "Full Fan"),
    ("imaging", "imaging_mode", IMAGING_MODE, "Image Gently"),
    ("imaging", "rotation_rate", ROTATION_RATE, "0.4 deg/s"),
    ("imaging", "timeline_end", TIMELINE_END, "501.0 s"),
    ("imaging", "sequential_times", SEQ_TIMES, "1000"),
    ("imaging", "time_verbosity", TIME_VERBOSITY, "0"),
    ("imaging", "field_x1", FIELD_X1, "14 cm"),
    ("imaging", "field_x2", FIELD_X2, "14 cm"),
    ("imaging", "field_y1", FIELD_Y1, "10.7 cm"),
    ("imaging", "field_y2", FIELD_Y2, "10.7 cm"),
    ("imaging", "blade_x1", BLADE_X1, "6.175536078965273 cm"),
    ("imaging", "blade_x2", BLADE_X2, "-6.175536078965273 cm"),
    ("imaging", "blade_y1", BLADE_Y1, "5.814471115800571 cm"),
    ("imaging", "blade_y2", BLADE_Y2, "-5.814471115800571 cm"),
    ("dicom", "dicom_directory", DICOM_DIR, "/sampledicom/setA"),
    ("dicom", "dicom_rp_file", DICOM_RP, "/sampledicom/RP.sample.dcm"),
    ("dicom", "patient_id", PATIENT_ID, ""),
    ("dicom", "isocenter_x", ISO_X, "0 mm"),
    ("dicom", "isocenter_y", ISO_Y, "0 mm"),
    ("dicom", "isocenter_z", ISO_Z, "0 mm"),
    ("dicom", "patient_shift_x", SHIFT_X, "0. mm"),
    ("dicom", "patient_shift_y", SHIFT_Y, "0. mm"),
    ("dicom", "patient_shift_z", SHIFT_Z, "0. mm"),
    ("dicom", "patient_yaw", PATIENT_YAW, "0. deg"),
    ("dicom", "graphics_enabled", DICOM_GRAPHICS, False),
    ("ctdi", "phantom_size", CTDI_PHANTOM, "16 cm"),
    ("ctdi", "dose_to_medium_zbins", DTM_ZBINS, "100"),
    ("ctdi", "tle_zbins", TLE_ZBINS, "100"),
    ("ctdi", "dose_to_water_zbins", DTW_ZBINS, "100"),
    ("ctdi", "couch_enabled", COUCH_ENABLED, True),
    ("ctdi", "couch_width", COUCH_WIDTH, "260. mm"),
    ("ctdi", "couch_thickness", COUCH_THICKNESS, "0.4 mm"),
    ("ctdi", "couch_length", COUCH_LENGTH, "1000 mm"),
    ("ctdi", "user_blade_enabled", CTDI_USER_BLADE, False),
    ("ctdi", "user_field_x1", CTDI_FIELD_X1, "14 cm"),
    ("ctdi", "user_field_x2", CTDI_FIELD_X2, "14 cm"),
    ("ctdi", "user_field_y1", CTDI_FIELD_Y1, "10.7 cm"),
    ("ctdi", "user_field_y2", CTDI_FIELD_Y2, "10.7 cm"),
    ("ctdi", "graphics_enabled", CTDI_GRAPHICS, False),
]

_BOOL_FIELDS: Dict[str, str] = {}
for _section, _field, _key, _default in _PLACEHOLDER_MAP:
    if isinstance(_default, bool):
        _BOOL_FIELDS[(_section + "." + _field)] = _key

# Dimensional field names per section (used for string→Quantity auto-parsing).
_IMAGING_Q_FIELDS = (
    "start_angle",
    "rotation_rate",
    "timeline_end",
    "anode_voltage",
    "exposure",
    "field_x1",
    "field_x2",
    "field_y1",
    "field_y2",
    "blade_x1",
    "blade_x2",
    "blade_y1",
    "blade_y2",
)
_DICOM_Q_FIELDS = (
    "isocenter_x",
    "isocenter_y",
    "isocenter_z",
    "patient_shift_x",
    "patient_shift_y",
    "patient_shift_z",
    "patient_yaw",
)
_CTDI_Q_FIELDS = (
    "couch_width",
    "couch_thickness",
    "couch_length",
    "user_field_x1",
    "user_field_x2",
    "user_field_y1",
    "user_field_y2",
)


def _parse_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).lower() in ("true", "1", "yes")


def _q(val: float, unit: str) -> Any:
    """Create a Quantity-typed dataclass field with a default value."""
    return field(default_factory=lambda: Quantity(val, unit))


def _coerce_quantities(obj: Any, field_names: Tuple[str, ...]) -> None:
    """Parse string values to Quantity in-place on a frozen dataclass."""
    for name in field_names:
        val = getattr(obj, name)
        if isinstance(val, str):
            object.__setattr__(obj, name, Quantity.parse(val))


@dataclass(frozen=True)
class GeneralConfig:
    """TOPAS runtime and environment settings."""

    g4_data_directory: str = ""
    topas_directory: str = ""
    seed: str = "9"
    threads: str = "1"
    histories: str = "100000"
    dose_calibration_factor: str = "1.0"
    log_filename: str = "simulation.log"


@dataclass(frozen=True)
class ImagingConfig:
    """kV imaging beam and collimator parameters."""

    simulation_type: str = "DICOM"
    start_angle: Quantity = _q(0.0, "deg")
    rotation_direction: str = "CBCT Clockwise"
    anode_voltage: Quantity = _q(100.0, "kV")
    exposure: Quantity = _q(100.0, "mAs")
    fan_mode: str = "Full Fan"
    imaging_mode: str = "Image Gently"
    rotation_rate: Quantity = _q(0.4, "deg/s")
    timeline_end: Quantity = _q(501.0, "s")
    sequential_times: str = "1000"
    time_verbosity: str = "0"
    field_x1: Quantity = _q(14.0, "cm")
    field_x2: Quantity = _q(14.0, "cm")
    field_y1: Quantity = _q(10.7, "cm")
    field_y2: Quantity = _q(10.7, "cm")
    blade_x1: Quantity = _q(6.175536078965273, "cm")
    blade_x2: Quantity = _q(-6.175536078965273, "cm")
    blade_y1: Quantity = _q(5.814471115800571, "cm")
    blade_y2: Quantity = _q(-5.814471115800571, "cm")

    def __post_init__(self) -> None:
        _coerce_quantities(self, _IMAGING_Q_FIELDS)


@dataclass(frozen=True)
class DicomConfig:
    """DICOM patient and plan parameters for patient-specific simulations."""

    dicom_directory: str = "/sampledicom/setA"
    dicom_rp_file: str = "/sampledicom/RP.sample.dcm"
    patient_id: str = ""
    isocenter_x: Quantity = _q(0.0, "mm")
    isocenter_y: Quantity = _q(0.0, "mm")
    isocenter_z: Quantity = _q(0.0, "mm")
    patient_shift_x: Quantity = _q(0.0, "mm")
    patient_shift_y: Quantity = _q(0.0, "mm")
    patient_shift_z: Quantity = _q(0.0, "mm")
    patient_yaw: Quantity = _q(0.0, "deg")
    graphics_enabled: bool = False

    def __post_init__(self) -> None:
        _coerce_quantities(self, _DICOM_Q_FIELDS)


@dataclass(frozen=True)
class CtdiConfig:
    """CTDI phantom, couch, scoring, and user-blade parameters."""

    phantom_size: str = "16 cm"
    dose_to_medium_zbins: str = "100"
    tle_zbins: str = "100"
    dose_to_water_zbins: str = "100"
    couch_enabled: bool = True
    couch_width: Quantity = _q(260.0, "mm")
    couch_thickness: Quantity = _q(0.4, "mm")
    couch_length: Quantity = _q(1000.0, "mm")
    user_blade_enabled: bool = False
    user_field_x1: Quantity = _q(14.0, "cm")
    user_field_x2: Quantity = _q(14.0, "cm")
    user_field_y1: Quantity = _q(10.7, "cm")
    user_field_y2: Quantity = _q(10.7, "cm")
    graphics_enabled: bool = False

    def __post_init__(self) -> None:
        _coerce_quantities(self, _CTDI_Q_FIELDS)


@dataclass(frozen=True)
class SimulationConfig:
    """Top-level configuration composing general, imaging, DICOM, and CTDI sections."""

    general: GeneralConfig = field(default_factory=GeneralConfig)
    imaging: ImagingConfig = field(default_factory=ImagingConfig)
    dicom: DicomConfig = field(default_factory=DicomConfig)
    ctdi: CtdiConfig = field(default_factory=CtdiConfig)
    config_yaml_path: str | None = field(default=None, repr=False)

    def validate(self) -> None:
        """Check enum fields, integer-valued string fields, and dimensional fields.

        Raises:
            ValueError: If any field contains an invalid value.
        """
        self._validate_enum_field(
            "simulation_type",
            self.imaging.simulation_type,
            SimulationType,
        )
        self._validate_enum_field("fan_mode", self.imaging.fan_mode, FanMode)
        self._validate_enum_field(
            "rotation_direction",
            self.imaging.rotation_direction,
            RotationDirection,
        )
        self._validate_enum_field("phantom_size", self.ctdi.phantom_size, PhantomSize)
        for name, value in [
            ("seed", self.general.seed),
            ("threads", self.general.threads),
            ("histories", self.general.histories),
            ("sequential_times", self.imaging.sequential_times),
            ("time_verbosity", self.imaging.time_verbosity),
            ("dose_to_medium_zbins", self.ctdi.dose_to_medium_zbins),
            ("tle_zbins", self.ctdi.tle_zbins),
            ("dose_to_water_zbins", self.ctdi.dose_to_water_zbins),
        ]:
            try:
                int(value)
            except (ValueError, TypeError):
                raise ValueError(
                    "Config field '{}' must be an integer, got {!r}".format(name, value)
                )
        try:
            calib_val = float(self.general.dose_calibration_factor)
        except (ValueError, TypeError):
            raise ValueError(
                "Config field 'dose_calibration_factor' must be a float, got {!r}".format(
                    self.general.dose_calibration_factor
                )
            )
        if calib_val <= 0:
            raise ValueError(
                "Config field 'dose_calibration_factor' must be positive, got {}".format(
                    calib_val
                )
            )
        if not 40 <= self.imaging.anode_voltage.value <= 150:
            raise ValueError(
                "Anode voltage must be 40-150 kV, got {}".format(
                    self.imaging.anode_voltage.value
                )
            )
        if self.imaging.exposure.value <= 0:
            raise ValueError(
                "Exposure must be positive, got {}".format(self.imaging.exposure.value)
            )

    @staticmethod
    def _validate_enum_field(field_name: str, value: str, enum_cls: Type[Enum]) -> None:
        valid = [e.value for e in enum_cls]
        if value not in valid:
            raise ValueError(
                "Config field '{}' must be one of {}, got {!r}".format(
                    field_name, valid, value
                )
            )

    def to_dict(self) -> Dict[str, str]:
        """Flatten all sections to a ``{GUI_KEY: value}`` dictionary."""
        result: Dict[str, str] = {}
        for section_name, field_name, key, _default in _PLACEHOLDER_MAP:
            section = getattr(self, section_name)
            value = getattr(section, field_name)
            result[key] = str(value)
        return result

    def to_yaml(self, path: str) -> None:
        """Serialise the full configuration to a YAML file."""
        data: Dict[str, Any] = {}
        for section_name in ("general", "imaging", "dicom", "ctdi"):
            section = getattr(self, section_name)
            section_data: Dict[str, Any] = {}
            for f_name in section.__dataclass_fields__:
                val = getattr(section, f_name)
                section_data[f_name] = str(val) if isinstance(val, Quantity) else val
            data[section_name] = section_data
        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    @classmethod
    def from_yaml(cls, path: str) -> "SimulationConfig":
        """Load and validate a SimulationConfig from a YAML file.

        Args:
            path: Filesystem path to the YAML config.

        Returns:
            A validated SimulationConfig instance.

        Raises:
            ValueError: If the YAML content is not a mapping or fails validation.
        """
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            raise ValueError(
                "YAML config must be a mapping, got {}".format(type(data).__name__)
            )
        config = cls(
            general=GeneralConfig(**data.get("general", {})),
            imaging=ImagingConfig(**data.get("imaging", {})),
            dicom=DicomConfig(**data.get("dicom", {})),
            ctdi=CtdiConfig(**data.get("ctdi", {})),
            config_yaml_path=os.path.abspath(path),
        )
        config.validate()
        return config

    @classmethod
    def from_gui_values(cls, values: Dict[str, str]) -> "SimulationConfig":
        """Construct a SimulationConfig from a FreeSimpleGUI values dict.

        Args:
            values: Mapping of GUI element keys to user-entered values.
        """
        sections: Dict[str, Dict[str, Any]] = {
            "general": {},
            "imaging": {},
            "dicom": {},
            "ctdi": {},
        }
        for section_name, field_name, key, default in _PLACEHOLDER_MAP:
            raw: Any = values.get(key, default)
            bool_key: str = section_name + "." + field_name
            if bool_key in _BOOL_FIELDS:
                sections[section_name][field_name] = _parse_bool(raw)
            else:
                sections[section_name][field_name] = raw
        return cls(
            general=GeneralConfig(**sections["general"]),
            imaging=ImagingConfig(**sections["imaging"]),
            dicom=DicomConfig(**sections["dicom"]),
            ctdi=CtdiConfig(**sections["ctdi"]),
        )

    @classmethod
    def defaults(cls) -> "SimulationConfig":
        """Return a default config.

        Priority for G4/TOPAS paths: ``config.yaml`` in CWD, then environment
        variables ``G4DATA_DIR``/``TOPAS_DIR``, then ``/root/`` fallbacks.
        """
        g4_dir: str = ""
        topas_dir: str = ""
        config_path = os.path.join(os.getcwd(), "config.yaml")
        if os.path.isfile(config_path):
            try:
                file_config = cls.from_yaml(config_path)
                g4_dir = file_config.general.g4_data_directory
                topas_dir = file_config.general.topas_directory
            except Exception:
                logger.warning("Failed to load config.yaml, using env/fallback")
        if not g4_dir:
            g4_dir = os.environ.get("G4DATA_DIR", "/root/G4Data")
        if not topas_dir:
            topas_dir = os.environ.get("TOPAS_DIR", "/root/topas/bin/topas")
        return cls(
            general=GeneralConfig(
                g4_data_directory=g4_dir,
                topas_directory=topas_dir,
            ),
            imaging=ImagingConfig(),
            dicom=DicomConfig(),
            ctdi=CtdiConfig(),
        )


def quantity_unit_stripper(string_value: str) -> Tuple[float, str]:
    """Parse a quantity string into a ``(float, unit)`` tuple."""

    return Quantity.parse(string_value).to_tuple()
