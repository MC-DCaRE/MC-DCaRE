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

    def test_to_tuple(self) -> None:
        q: Quantity = Quantity.parse("100 kV")
        assert q.to_tuple() == (100.0, "kV")


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

    def test_frozen(self) -> None:
        q: Quantity = Quantity(5.0, "mm")
        try:
            q.value = 10.0
            assert False, "Should have raised FrozenInstanceError"
        except AttributeError:
            pass


class TestQuantityBackwardCompat:
    def test_matches_old_quantity_unit_stripper(self) -> None:
        from src.config import quantity_unit_stripper

        for input_str in [
            "100 kV",
            "0.4 deg/s",
            "-5 mm",
            "9",
            "100",
        ]:
            old_result = quantity_unit_stripper(input_str)
            new_result = Quantity.parse(input_str).to_tuple()
            assert old_result == new_result, "Mismatch for " + input_str
