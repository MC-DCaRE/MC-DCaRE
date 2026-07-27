from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.models.quantity import Quantity


class TestQuantityParse:
    def test_splits_value_and_unit(self) -> None:
        q: Quantity = Quantity.parse("100 kV")
        assert q.value == 100.0
        assert q.unit == "kV"

    def test_raises_for_no_number(self) -> None:
        with pytest.raises(ValueError, match="No numeric value"):
            Quantity.parse("kV")

    def test_raises_for_empty_string(self) -> None:
        with pytest.raises(ValueError, match="No numeric value"):
            Quantity.parse("")

    def test_returns_empty_unit_for_no_unit(self) -> None:
        q: Quantity = Quantity.parse("100")
        assert q.value == 100.0
        assert q.unit == ""

    def test_handles_compound_units(self) -> None:
        q: Quantity = Quantity.parse("0.4 deg/s")
        assert q.value == 0.4
        assert q.unit == "deg/s"

    def test_handles_negative(self) -> None:
        q: Quantity = Quantity.parse("-5 mm")
        assert q.value == -5.0
        assert q.unit == "mm"

    def test_handles_integer_string(self) -> None:
        q: Quantity = Quantity.parse("9")
        assert q.value == 9.0
        assert q.unit == ""


class TestQuantityStr:
    def test_str_roundtrip(self) -> None:
        q: Quantity = Quantity(100.0, "kV")
        assert str(q) == "100 kV"

    def test_str_preserves_precision(self) -> None:
        q: Quantity = Quantity(6.175536078965273, "cm")
        assert str(q) == "6.175536078965273 cm"

    def test_str_strips_trailing_zeros(self) -> None:
        assert str(Quantity(100.0, "kV")) == "100 kV"
        assert str(Quantity(0.4, "deg/s")) == "0.4 deg/s"
        assert str(Quantity(5.0, "mm")) == "5 mm"

    def test_zero_value(self) -> None:
        assert str(Quantity(0.0, "mm")) == "0 mm"

    def test_negative_non_integer(self) -> None:
        assert str(Quantity(-0.5, "mm")) == "-0.5 mm"

    def test_parse_str_roundtrip(self) -> None:
        for val, unit in [(100.0, "kV"), (6.175536078965273, "cm"), (-5.0, "mm")]:
            q = Quantity(val, unit)
            assert Quantity.parse(str(q)) == q

    def test_frozen(self) -> None:
        q: Quantity = Quantity(5.0, "mm")
        try:
            q.value = 10.0
            assert False, "Should have raised FrozenInstanceError"
        except AttributeError:
            pass
