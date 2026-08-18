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
from dataclasses import dataclass, field, fields
from enum import Enum
from typing import Any, Dict, Tuple, Type

import yaml

from src.models.enums import FanMode, PhantomSize, RotationDirection, SimulationType
from src.models.imaging_mode import IMAGING_MODES, ImagingMode
from src.models.quantity import Quantity

logger = logging.getLogger(__name__)


def _filter_known_fields(dataclass_cls: type, data: Dict[str, Any]) -> Dict[str, Any]:
    """Drop YAML keys that are not fields of *dataclass_cls*.

    Lets :meth:`SimulationConfig.from_yaml` ignore removed/legacy keys
    (e.g. ``time_verbosity``, ``dose_calibration_factor``) so old config
    files keep loading instead of raising ``TypeError``.
    """
    known = {f.name for f in fields(dataclass_cls)}
    unknown = [k for k in data if k not in known]
    if unknown:
        logger.warning(
            "Ignoring unknown %s keys: %s",
            dataclass_cls.__name__,
            ", ".join(unknown),
        )
    return {k: v for k, v in data.items() if k in known}


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
_PHANTOM_Q_FIELDS = (
    "trans_x",
    "trans_y",
    "trans_z",
    "rot_x",
    "rot_y",
    "rot_z",
    "couch_width",
    "couch_thickness",
    "couch_length",
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
    filtration_mode: str = "hybrid"
    bhf_thickness_mm: float = 0.89
    bhf_mode: str = "geometric"
    legacy_bowtie: bool = False
    bowtie_enabled: bool = True
    imaging_mode: str = "Image Gently"
    rotation_rate: Quantity = _q(0.4, "deg/s")
    timeline_end: Quantity = _q(501.0, "s")
    sequential_times: str = "1000"
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
        if self.filtration_mode not in ("hybrid", "geometric"):
            raise ValueError(
                "imaging.filtration_mode must be 'hybrid' or 'geometric', got %r"
                % self.filtration_mode
            )
        if self.bhf_thickness_mm < 0:
            raise ValueError(
                "imaging.bhf_thickness_mm must be non-negative, got %s"
                "(0 removes the Ti beam-hardening filter: Ti-out bracketing)"
                % self.bhf_thickness_mm
            )
        if self.bhf_mode not in ("geometric", "spekpy"):
            raise ValueError(
                "imaging.bhf_mode must be 'geometric' or 'spekpy', got %r "
                "(geometric: physical Ti TsBox in the beam line; spekpy: Ti "
                "folded into the SpekPy source spectrum, no TsBox)" % self.bhf_mode
            )
        if self.bhf_mode == "spekpy" and self.bhf_thickness_mm <= 0:
            raise ValueError(
                "imaging.bhf_mode='spekpy' requires bhf_thickness_mm > 0 "
                "(use bhf_mode='geometric' with thickness 0 for no filter)"
            )


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
    validate_bowtie: bool = False
    phase_space_mode: str = "off"
    phase_space_file: str = ""
    phase_space_multiple_use: int = 1

    def __post_init__(self) -> None:
        _coerce_quantities(self, _CTDI_Q_FIELDS)


@dataclass(frozen=True)
class PhantomConfig:
    """ICRP reference phantom placement, couch, and organ-scoring parameters.

    Phantom selection resolves from ``phantom_age`` (adult | 0y | 1y | 5y | 10y
    | 15y), ``phantom_sex`` (AM | AF), and ``phantom_size_percentile``
    (10 | 50 | 90) via :meth:`resolve_phantom_name`. An explicit ``phantom_name``
    overrides the resolver.
    """

    phantom_data_directory: str = "data/P145/Phantom_data"
    phantom_voxel_directory: str = "data/P145/voxelized"
    phantom_sex: str = "AM"
    phantom_age: str = "adult"
    phantom_size_percentile: int = 50
    phantom_voxel_size_mm: float = 5.0
    use_voxel_phantom: bool = True
    phantom_name: str = ""
    trans_x: Quantity = _q(0.0, "cm")
    trans_y: Quantity = _q(0.0, "cm")
    trans_z: Quantity = _q(0.0, "cm")
    rot_x: Quantity = _q(90.0, "deg")
    rot_y: Quantity = _q(0.0, "deg")
    rot_z: Quantity = _q(0.0, "deg")
    couch_enabled: bool = True
    couch_width: Quantity = _q(260.0, "mm")
    couch_thickness: Quantity = _q(0.4, "mm")
    couch_length: Quantity = _q(1000.0, "mm")
    graphics_enabled: bool = False
    organ_scoring_ids: str = ""
    phase_space_mode: str = "off"
    phase_space_file: str = ""
    phase_space_multiple_use: int = 1
    phase_space_component: str = "Rotation"
    phase_space_filter_z: float = 0.0

    def __post_init__(self) -> None:
        _coerce_quantities(self, _PHANTOM_Q_FIELDS)
        if self.phantom_sex not in ("AM", "AF"):
            raise ValueError(
                "phantom.phantom_sex must be 'AM' or 'AF', got %r" % self.phantom_sex
            )
        if self.phantom_age not in ("adult", "0y", "1y", "5y", "10y", "15y"):
            raise ValueError(
                "phantom.phantom_age must be adult/0y/1y/5y/10y/15y, got %r"
                % self.phantom_age
            )
        if self.phantom_size_percentile not in (10, 50, 90):
            raise ValueError(
                "phantom.phantom_size_percentile must be 10/50/90, got %s"
                % self.phantom_size_percentile
            )
        if self.phantom_voxel_size_mm <= 0:
            raise ValueError(
                "phantom.phantom_voxel_size_mm must be positive, got %s"
                % self.phantom_voxel_size_mm
            )

    def resolve_phantom_name(self) -> str:
        """Resolve the phantom name from age/sex/percentile.

        ``phantom_name`` (if set) overrides; otherwise the name is built as
        ``MRCP_{sex}`` (adult), ``MRCP_{sex}_{age}`` (paediatric), with a
        ``_p{percentile}`` suffix for non-50th-percentile size-library members.
        """
        if self.phantom_name:
            return self.phantom_name
        name = "MRCP_{}".format(self.phantom_sex)
        if self.phantom_age != "adult":
            name += "_{}".format(self.phantom_age)
        if self.phantom_size_percentile != 50:
            name += "_p{}".format(self.phantom_size_percentile)
        return name

    def resolve_voxel_directory(self) -> str:
        """Resolve the voxelized-phantom directory for the resolved name."""
        return os.path.join(
            self.phantom_voxel_directory,
            "{}_{}mm".format(
                self.resolve_phantom_name(), "%g" % self.phantom_voxel_size_mm
            ),
        )


# Mode field → config dict key mapping for _resolve_imaging_mode().
# (ImagingMode attribute, target dict key, target dict: "imaging" or "ctdi")
# dose_factor, fan_detail, no_projections, proj_increment, acquisition_time,
# and ctdiw_reference are intentionally excluded — metadata only, no config
# field to populate yet.
_RESOLVE_FIELD_MAP: list[tuple[str, str, str]] = [
    ("voltage", "anode_voltage", "imaging"),
    ("ctdi_phantom", "phantom_size", "ctdi"),
    ("start_angle", "start_angle", "imaging"),
    ("rotation_rate", "rotation_rate", "imaging"),
    ("timeline_end", "timeline_end", "imaging"),
    ("fan_mode", "fan_mode", "imaging"),
    ("field_x1", "field_x1", "imaging"),
    ("field_x2", "field_x2", "imaging"),
    ("field_y1", "field_y1", "imaging"),
    ("field_y2", "field_y2", "imaging"),
    ("blade_x1", "blade_x1", "imaging"),
    ("blade_x2", "blade_x2", "imaging"),
    ("blade_y1", "blade_y1", "imaging"),
    ("blade_y2", "blade_y2", "imaging"),
    ("exposure", "exposure", "imaging"),
]


def _resolve_imaging_mode(
    imaging_data: dict, ctdi_data: dict | None = None
) -> tuple[dict, dict]:
    """Auto-populate imaging/CTDI fields from protocol name lookup.

    Composites ``rotation_direction + "_" + imaging_mode`` into a key for
    :data:`IMAGING_MODES`, then fills absent/empty fields in *imaging_data*
    and *ctdi_data* from the resolved mode.  Explicit YAML values always win
    over mode defaults.

    Skips resolution when direction or mode is absent/empty (backward compat),
    or when direction is kV-kV (those configs carry all beam parameters
    explicitly).

    Args:
        imaging_data: Raw ``imaging`` section from YAML.
        ctdi_data: Raw ``ctdi`` section from YAML, or None.

    Returns:
        Modified ``(imaging_data, ctdi_data)`` dicts.

    Raises:
        ValueError: If the composed key does not match any mode.
    """
    if ctdi_data is None:
        ctdi_data = {}

    direction = (imaging_data.get("rotation_direction") or "").strip()
    if not direction:
        # No direction (None or empty) — skip resolution (backward compat).
        return imaging_data, ctdi_data

    if direction.startswith("kV-kV"):
        # kV-kV configs carry all beam parameters explicitly; skip resolution.
        return imaging_data, ctdi_data

    mode_name = (imaging_data.get("imaging_mode") or "").strip()
    if not mode_name:
        # No mode (None or empty) — skip resolution (backward compat).
        return imaging_data, ctdi_data

    key = "{}_{}".format(direction, mode_name)
    if key not in IMAGING_MODES:
        valid = sorted(IMAGING_MODES.keys())
        raise ValueError(
            "No imaging mode found for key {!r}. Valid keys: {}".format(key, valid)
        )

    mode: ImagingMode = IMAGING_MODES[key]

    for mode_attr, target_key, target_dict in _RESOLVE_FIELD_MAP:
        target = imaging_data if target_dict == "imaging" else ctdi_data
        yaml_val = target.get(target_key)
        if yaml_val is None or yaml_val == "":
            target[target_key] = getattr(mode, mode_attr)

    return imaging_data, ctdi_data


@dataclass(frozen=True)
class SimulationConfig:
    """Top-level configuration composing general, imaging, DICOM, CTDI, and phantom sections."""

    general: GeneralConfig = field(default_factory=GeneralConfig)
    imaging: ImagingConfig = field(default_factory=ImagingConfig)
    dicom: DicomConfig = field(default_factory=DicomConfig)
    ctdi: CtdiConfig = field(default_factory=CtdiConfig)
    phantom: PhantomConfig = field(default_factory=PhantomConfig)
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
        # Phase space validation only applies to CTDI simulation type.
        if self.imaging.simulation_type == "CTDI":
            valid_phase_space_modes = ("off", "score", "replay")
            if self.ctdi.phase_space_mode not in valid_phase_space_modes:
                raise ValueError(
                    "phase_space_mode must be one of {}, got {!r}".format(
                        valid_phase_space_modes, self.ctdi.phase_space_mode
                    )
                )
            if self.ctdi.phase_space_mode == "replay":
                if not self.ctdi.phase_space_file:
                    raise ValueError(
                        "phase_space_file is required when phase_space_mode is 'replay'"
                    )
                if not os.path.isfile(self.ctdi.phase_space_file):
                    raise ValueError(
                        "phase_space_file does not exist: {}".format(
                            self.ctdi.phase_space_file
                        )
                    )
            if self.ctdi.phase_space_multiple_use < 1:
                raise ValueError(
                    "phase_space_multiple_use must be >= 1, got {}".format(
                        self.ctdi.phase_space_multiple_use
                    )
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
        for section_name in ("general", "imaging", "dicom", "ctdi", "phantom"):
            section = getattr(self, section_name)
            section_data: Dict[str, Any] = {}
            for f_name in section.__dataclass_fields__:
                val = getattr(section, f_name)
                section_data[f_name] = str(val) if isinstance(val, Quantity) else val
            data[section_name] = section_data
        with open(path, "w", encoding="utf-8") as f:
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
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            raise ValueError(
                "YAML config must be a mapping, got {}".format(type(data).__name__)
            )
        imaging_data = data.get("imaging", {})
        ctdi_data = data.get("ctdi", {})
        imaging_data, ctdi_data = _resolve_imaging_mode(imaging_data, ctdi_data)
        config = cls(
            general=GeneralConfig(
                **_filter_known_fields(GeneralConfig, data.get("general", {}))
            ),
            imaging=ImagingConfig(**_filter_known_fields(ImagingConfig, imaging_data)),
            dicom=DicomConfig(
                **_filter_known_fields(DicomConfig, data.get("dicom", {}))
            ),
            ctdi=CtdiConfig(**_filter_known_fields(CtdiConfig, ctdi_data)),
            phantom=PhantomConfig(
                **_filter_known_fields(PhantomConfig, data.get("phantom", {}))
            ),
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
            except (yaml.YAMLError, OSError, ValueError):
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
            phantom=PhantomConfig(),
        )
