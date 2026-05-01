"""Physical quantity value-object pairing a numeric magnitude with a unit string.

Exports :class:`Quantity`, a frozen dataclass used throughout the simulation
pipeline to represent TOPAS parameter values such as ``"100 kV"`` or
``"0.4 deg/s"``.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Tuple

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Quantity:
    """Immutable physical quantity with a numeric value and unit string."""

    value: float
    unit: str

    @classmethod
    def parse(cls, string_value: str) -> Quantity:
        """Parse a ``"<number> <unit>"`` string into a Quantity.

        Args:
            string_value: Space-separated value and unit, e.g. ``"100 kV"``.

        Returns:
            A new Quantity with the parsed value and unit.

        Raises:
            ValueError: If no numeric token is found in *string_value*.
        """
        parsed_value: float = 0.0
        parsed_unit: str = ""
        found_number = False
        for token in string_value.split():
            try:
                parsed_value = float(token)
                found_number = True
            except ValueError:
                parsed_unit = token
        if not found_number:
            raise ValueError("No numeric value found in {!r}".format(string_value))
        return cls(parsed_value, parsed_unit)

    def __str__(self) -> str:
        """Format as ``"<value> <unit>"`` using compact ``g`` notation."""
        return "{} {}".format(format(self.value, "g"), self.unit)

    def to_tuple(self) -> Tuple[float, str]:
        """Return the ``(value, unit)`` pair as a plain tuple."""
        return (self.value, self.unit)
