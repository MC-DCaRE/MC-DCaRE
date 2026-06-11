"""Simulation configuration dataclasses and serialisation helpers.

Defines the configuration hierarchy (:class:`GeneralConfig`, :class:`ImagingConfig`,
:class:`DicomConfig`, :class:`CtdiConfig`) composed inside :class:`SimulationConfig`,
with round-trip support for YAML files.

Dimensional fields (lengths, angles, voltages) are stored as :class:`Quantity` objects.
String values passed to constructors are automatically parsed into ``Quantity``.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Tuple, Type

import yaml

from src.models.enums import FanMode, PhantomSize, RotationDirection, SimulationType
from src.models.quantity import Quantity

logger = logging.getLogger(__name__)

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
    "patient_pitch",
    "patient_roll",
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


def _q(val: float, unit: str) -> Any:
    """Create a Quantity-typed dataclass field with a default value.

    Returns ``Any`` because :func:`dataclasses.field` returns ``Field[Any]``
    which mypy cannot reconcile with the ``Quantity`` type annotation at the
    class-body level.  The field annotation (``Quantity``) governs static
    type-checking; the default_factory provides the runtime value.
    """
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
    patient_pitch: Quantity = _q(0.0, "deg")
    patient_roll: Quantity = _q(0.0, "deg")
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
    water_chamber_enabled: bool = False

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
