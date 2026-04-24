from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Tuple

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Quantity:
    value: float
    unit: str

    @classmethod
    def parse(cls, string_value: str) -> Quantity:
        parsed_value: float = 0.0
        parsed_unit: str = ""
        for token in string_value.split():
            try:
                parsed_value = float(token)
            except ValueError:
                parsed_unit = token
        return cls(parsed_value, parsed_unit)

    def __str__(self) -> str:
        return "{} {}".format(format(self.value, "g"), self.unit)

    def to_tuple(self) -> Tuple[float, str]:
        return (self.value, self.unit)
