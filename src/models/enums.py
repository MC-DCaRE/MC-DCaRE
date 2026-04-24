from __future__ import annotations

from enum import Enum


class SimulationType(str, Enum):
    DICOM = "DICOM"
    CTDI = "CTDI validation"


class FanMode(str, Enum):
    FULL = "Full Fan"
    HALF = "Half Fan"


class RotationDirection(str, Enum):
    CW = "CBCT Clockwise"
    CCW = "CBCT Anticlockwise"
    KV_KV = "kV-kV"
