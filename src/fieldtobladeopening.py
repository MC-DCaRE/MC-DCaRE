"""Converts radiation field sizes to collimator blade opening positions."""

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
        return (field + 90.2972966781214) / 17.3699885452463

    def xbladeopening(field: float) -> float:
        return (field + 72.3986904761904) / 13.9904761904762

    blade_position_list: List[str] = []
    for count, field_str in enumerate(field_size_list):
        tokens = field_str.split()
        found_number = False
        for token in tokens:
            try:
                float(token)
                found_number = True
                break
            except ValueError:
                pass
        if not found_number:
            raise TypeError(
                "Field size must contain a numeric value, e.g. '14 cm'. Got: "
                + repr(field_str)
            )
        parsed = Quantity.parse(field_str)
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
