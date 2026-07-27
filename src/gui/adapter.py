"""Adapter between FreeSimpleGUI value dicts and SimulationConfig.

Translates between the ``-UPPERCASE_KEY-`` patterned GUI element keys
and the typed dataclass fields of :class:`SimulationConfig`.  Keeps the
config module free of GUI-specific imports.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from src.config import (
    CtdiConfig,
    DicomConfig,
    GeneralConfig,
    ImagingConfig,
    PhantomConfig,
    SimulationConfig,
)
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
    PATIENT_PITCH,
    PATIENT_ROLL,
    PATIENT_YAW,
    PHANTOM_COUCH_ENABLED,
    PHANTOM_COUCH_LENGTH,
    PHANTOM_COUCH_THICKNESS,
    PHANTOM_COUCH_WIDTH,
    PHANTOM_DATA_DIR,
    PHANTOM_GRAPHICS,
    PHANTOM_ROT_X,
    PHANTOM_ROT_Y,
    PHANTOM_ROT_Z,
    PHANTOM_SEX,
    PHANTOM_TRANS_X,
    PHANTOM_TRANS_Y,
    PHANTOM_TRANS_Z,
    ROTATION_RATE,
    SCAN_TYPE,
    SEED,
    SEQ_TIMES,
    SHIFT_X,
    SHIFT_Y,
    SHIFT_Z,
    SIM_TYPE,
    START_ANGLE,
    THREADS,
    TIMELINE_END,
    TOPAS_DIR,
    TLE_ZBINS,
    TUBE_VOLTAGE,
)


def _parse_bool(value: object) -> bool:
    """Coerce a GUI value to bool.

    Handles actual bools, string representations, and integers.
    """
    if isinstance(value, bool):
        return value
    return str(value).lower() in ("true", "1", "yes")


# (section_name, field_name, gui_key, default_value)
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
    ("dicom", "patient_shift_x", SHIFT_X, "0 mm"),
    ("dicom", "patient_shift_y", SHIFT_Y, "0 mm"),
    ("dicom", "patient_shift_z", SHIFT_Z, "0 mm"),
    ("dicom", "patient_yaw", PATIENT_YAW, "0 deg"),
    ("dicom", "patient_pitch", PATIENT_PITCH, "0 deg"),
    ("dicom", "patient_roll", PATIENT_ROLL, "0 deg"),
    ("dicom", "graphics_enabled", DICOM_GRAPHICS, False),
    ("ctdi", "phantom_size", CTDI_PHANTOM, "16 cm"),
    ("ctdi", "dose_to_medium_zbins", DTM_ZBINS, "100"),
    ("ctdi", "tle_zbins", TLE_ZBINS, "100"),
    ("ctdi", "dose_to_water_zbins", DTW_ZBINS, "100"),
    ("ctdi", "couch_enabled", COUCH_ENABLED, True),
    ("ctdi", "couch_width", COUCH_WIDTH, "260 mm"),
    ("ctdi", "couch_thickness", COUCH_THICKNESS, "0.4 mm"),
    ("ctdi", "couch_length", COUCH_LENGTH, "1000 mm"),
    ("ctdi", "user_blade_enabled", CTDI_USER_BLADE, False),
    ("ctdi", "user_field_x1", CTDI_FIELD_X1, "14 cm"),
    ("ctdi", "user_field_x2", CTDI_FIELD_X2, "14 cm"),
    ("ctdi", "user_field_y1", CTDI_FIELD_Y1, "10.7 cm"),
    ("ctdi", "user_field_y2", CTDI_FIELD_Y2, "10.7 cm"),
    ("ctdi", "graphics_enabled", CTDI_GRAPHICS, False),
    ("phantom", "phantom_data_directory", PHANTOM_DATA_DIR, "data/P145/Phantom_data"),
    ("phantom", "phantom_sex", PHANTOM_SEX, "AM"),
    ("phantom", "trans_x", PHANTOM_TRANS_X, "0.0 cm"),
    ("phantom", "trans_y", PHANTOM_TRANS_Y, "0.0 cm"),
    ("phantom", "trans_z", PHANTOM_TRANS_Z, "0.0 cm"),
    ("phantom", "rot_x", PHANTOM_ROT_X, "90.0 deg"),
    ("phantom", "rot_y", PHANTOM_ROT_Y, "0.0 deg"),
    ("phantom", "rot_z", PHANTOM_ROT_Z, "0.0 deg"),
    ("phantom", "couch_enabled", PHANTOM_COUCH_ENABLED, True),
    ("phantom", "couch_width", PHANTOM_COUCH_WIDTH, "260 mm"),
    ("phantom", "couch_thickness", PHANTOM_COUCH_THICKNESS, "0.4 mm"),
    ("phantom", "couch_length", PHANTOM_COUCH_LENGTH, "1000 mm"),
    ("phantom", "graphics_enabled", PHANTOM_GRAPHICS, False),
]

_BOOL_FIELDS: Dict[str, str] = {}
for _section, _field, _key, _default in _PLACEHOLDER_MAP:
    if isinstance(_default, bool):
        _BOOL_FIELDS[(_section + "." + _field)] = _key


def gui_to_config(values: Dict[str, Any]) -> SimulationConfig:
    """Build a :class:`SimulationConfig` from a FreeSimpleGUI values dict.

    Args:
        values: Mapping of GUI element keys to user-entered values.
    """
    sections: Dict[str, Dict[str, Any]] = {
        "general": {},
        "imaging": {},
        "dicom": {},
        "ctdi": {},
        "phantom": {},
    }
    for section_name, field_name, key, default in _PLACEHOLDER_MAP:
        raw: Any = values.get(key, default)
        bool_key: str = section_name + "." + field_name
        if bool_key in _BOOL_FIELDS:
            sections[section_name][field_name] = _parse_bool(raw)
        else:
            sections[section_name][field_name] = raw
    return SimulationConfig(
        general=GeneralConfig(**sections["general"]),
        imaging=ImagingConfig(**sections["imaging"]),
        dicom=DicomConfig(**sections["dicom"]),
        ctdi=CtdiConfig(**sections["ctdi"]),
        phantom=PhantomConfig(**sections["phantom"]),
    )
