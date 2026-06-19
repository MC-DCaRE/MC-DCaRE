"""Enumerations for simulation type, fan geometry, rotation direction, and phantom size.

Exports :class:`SimulationType`, :class:`FanMode`, :class:`RotationDirection`,
and :class:`PhantomSize`.  All enums inherit from ``str`` so their values can be
compared directly with user-facing strings from the GUI and YAML configs.
"""

from __future__ import annotations

from enum import Enum


class SimulationType(str, Enum):
    """Available simulation modes."""

    DICOM = "DICOM"
    CTDI = "CTDI"
    ICRP145 = "ICRP145"


class FanMode(str, Enum):
    """kV beam fan geometry."""

    FULL = "Full Fan"
    HALF = "Half Fan"


class RotationDirection(str, Enum):
    """Gantry rotation direction or kV-kV static pair."""

    CW = "CBCT Clockwise"
    CCW = "CBCT Anticlockwise"
    KV_KV = "kV-kV"


class PhantomSize(str, Enum):
    """CTDI phantom diameter."""

    CM_16 = "16 cm"
    CM_32 = "32 cm"
