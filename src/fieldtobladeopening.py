"""Converts radiation field sizes to collimator blade opening positions.

Linear calibration coefficients derived from the TrueBeam kV collimator values
recorded in ``research/2023 - CBCT Mode Standardisation/TrueBeamCBCTmodes.xlsx``
(TB4.1 July25 sheet) and corroborated by the per-mode service screenshots in the
same collection (CST / OBK / PL LA3-LA5 sites). Full-fan blade tuple is
(14, 14, 10.7, 10.7) mm and half-fan is (24.7, 3.3, 10.7, 10.7) mm.
"""

from __future__ import annotations

import logging
from typing import List

from src.models.quantity import Quantity

logger = logging.getLogger(__name__)


def fieldtobladeopening(field_size_list: List[str]) -> List[str]:
    """Convert four field-size strings to collimator blade opening positions.

    Args:
        field_size_list: Four field-size strings in order
            [x1, x2, y1, y2], each with a numeric value and unit (e.g. ``"14 cm"``).

    Returns:
        Four blade-opening strings with sign indicating direction.

    Raises:
        TypeError: If a field-size string does not contain a numeric value.
    """

    def ybladeopening(field: float) -> float:
        """Convert field size (cm) to Y-blade opening position (cm).

        Linear calibration: blade = (field + 90.297) / 17.370
        """
        return (field + 90.2972966781214) / 17.3699885452463

    def xbladeopening(field: float) -> float:
        """Convert field size (cm) to X-blade opening position (cm).

        Linear calibration: blade = (field + 72.399) / 13.990
        """
        return (field + 72.3986904761904) / 13.9904761904762

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
            blade_position_float = xbladeopening(parsed.value)
        elif count == 1:
            blade_position_float = xbladeopening(parsed.value) * -1
        elif count == 2:
            blade_position_float = ybladeopening(parsed.value)
        else:
            blade_position_float = ybladeopening(parsed.value) * -1
        blade_position_list.append(str(blade_position_float) + " " + parsed.unit)

    return blade_position_list


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info(fieldtobladeopening(["2 cm", "2 cm", "16 cm", "16 cm"]))
    logger.info(fieldtobladeopening(["10 cm", "10 cm", "10 cm", "10 cm"]))
