"""Converts radiation field sizes to collimator blade opening positions.

Geometric demagnification: the kV jaw blades sit 11.7 cm downstream of the
source (``Ge/CollimatorsVertical/TransY``) and the isocenter is at 100 cm
(``Ge/BeamPosition/TransY = -1000 mm``), so a field edge of F cm at the
isocenter projects to a blade edge at F x 11.7/100 cm from the central axis.

The previous affine fits (``blade = (field + 90.3)/17.4`` etc., regressed
from service-mode readouts) produced openings 4-8x too wide: the 2026-08-18
patient-plane fluence-slab diagnostic (``tools/run_fluence_slab.py``, run
``edose_validation_runs/2026-08-18_12-16-10``) measured only 23.2% of the
pelvis-mode kerma inside the intended X/Z field, with a +-50 cm effective
fan -- the blades were physically clear of the beam instead of shaping it.
Full-fan blade tuple is (14, 14, 10.7, 10.7) mm and half-fan is
(24.7, 3.3, 10.7, 10.7) mm at the isocenter.
"""

from __future__ import annotations

import logging
from typing import List

from src.models.quantity import Quantity

logger = logging.getLogger(__name__)

# kV collimator geometry (see headsourcecode_boilerplate.j2)
BLADE_SOURCE_DISTANCE_CM = 11.7  # Ge/CollimatorsVertical/TransY
SOURCE_ISOCENTER_DISTANCE_CM = 100.0  # |Ge/BeamPosition/TransY|

# Field-to-blade demagnification: blade edge = field edge x SDD/SAD
BLADE_DEMAGNIFICATION = BLADE_SOURCE_DISTANCE_CM / SOURCE_ISOCENTER_DISTANCE_CM


def fieldtobladeopening(field_size_list: List[str]) -> List[str]:
    """Convert four field-size strings to collimator blade opening positions.

    Args:
        field_size_list: Four field-size strings in order
            [x1, x2, y1, y2], each with a numeric value and unit (e.g. ``"14 cm"``).

    Returns:
        Four blade-opening strings with sign indicating direction
        (x1/y1 positive, x2/y2 negative), matching the Coll1..Coll4
        TransY/TransX template slots.
    """

    def bladeopening(field: float) -> float:
        """Convert field size at isocenter (cm) to blade edge position (cm)."""
        return field * BLADE_DEMAGNIFICATION

    blade_position_list: List[str] = []
    for count, field_str in enumerate(field_size_list):
        try:
            parsed = Quantity.parse(field_str)
        except ValueError:
            raise TypeError(
                "Field size must contain a numeric value, e.g. '14 cm'. Got: "
                + repr(field_str)
            )
        if parsed.unit not in ("cm", "mm", "m", "CM", "MM", "M"):
            raise ValueError(
                "Unsupported unit '{}'. Expected cm, mm, or m.".format(parsed.unit)
            )
        if parsed.unit.lower() == "mm":
            parsed = Quantity(parsed.value / 10, "cm")
        elif parsed.unit.lower() == "m":
            parsed = Quantity(parsed.value * 100, "cm")
        if count == 0:
            blade_position_float = bladeopening(parsed.value)
        elif count == 1:
            blade_position_float = bladeopening(parsed.value) * -1
        elif count == 2:
            blade_position_float = bladeopening(parsed.value)
        else:
            blade_position_float = bladeopening(parsed.value) * -1
        blade_position_list.append(str(blade_position_float) + " " + parsed.unit)

    return blade_position_list


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info(fieldtobladeopening(["2 cm", "2 cm", "16 cm", "16 cm"]))
    logger.info(fieldtobladeopening(["10 cm", "10 cm", "10 cm", "10 cm"]))
