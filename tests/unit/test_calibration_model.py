from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.models.calibration import CalibrationEntry, MachineCalibration


def _sample_yaml(
    machine: str = "TrueBeam-SN1234",
    date: str = "2026-06-10",
    entries: str = "",
) -> str:
    """Build a minimal calibration YAML string."""
    return (
        "machine: '{machine}'\ndate_calibrated: '{date}'\ncalibrations:\n{entries}"
    ).format(machine=machine, date=date, entries=entries)


_SAMPLE_ENTRIES = (
    "  - kV: 120\n"
    "    fan_mode: 'Full Fan'\n"
    "    reference_mAs: 100.0\n"
    "    measured_ctdi_w_mGy: 45.2\n"
    "    dcf: 1.034\n"
    "  - kV: 80\n"
    "    fan_mode: 'Full Fan'\n"
    "    reference_mAs: 100.0\n"
    "    measured_ctdi_w_mGy: null\n"
    "    dcf: null\n"
)


class TestCalibrationEntry:
    def test_fields_populated(self) -> None:
        e = CalibrationEntry(kV=120, fan_mode="Full Fan", reference_mAs=100.0)
        assert e.kV == 120
        assert e.fan_mode == "Full Fan"
        assert e.reference_mAs == 100.0
        assert e.measured_ctdi_w_mGy is None
        assert e.dcf is None

    def test_frozen(self) -> None:
        e = CalibrationEntry(kV=120, fan_mode="Full Fan", reference_mAs=100.0)
        with pytest.raises(AttributeError):
            e.kV = 100  # type: ignore[misc]

    def test_optional_fields_set(self) -> None:
        e = CalibrationEntry(
            kV=120,
            fan_mode="Full Fan",
            reference_mAs=100.0,
            measured_ctdi_w_mGy=45.2,
            dcf=1.034,
        )
        assert e.measured_ctdi_w_mGy == 45.2
        assert e.dcf == 1.034

    def test_rejects_non_numeric_measured(self) -> None:
        with pytest.raises(TypeError, match="measured_ctdi_w_mGy must be numeric"):
            CalibrationEntry(
                kV=120,
                fan_mode="Full Fan",
                reference_mAs=100.0,
                measured_ctdi_w_mGy="not_a_number",
            )

    def test_rejects_non_numeric_dcf(self) -> None:
        with pytest.raises(TypeError, match="dcf must be numeric"):
            CalibrationEntry(
                kV=120,
                fan_mode="Full Fan",
                reference_mAs=100.0,
                dcf="bad",
            )


class TestFromYaml:
    def test_loads_valid_file(self, tmp_path: object) -> None:
        import pathlib

        p = pathlib.Path(str(tmp_path)) / "cal.yaml"
        p.write_text(_sample_yaml(entries=_SAMPLE_ENTRIES))
        mc = MachineCalibration.from_yaml(p)
        assert mc.machine == "TrueBeam-SN1234"
        assert mc.date_calibrated == "2026-06-10"
        assert len(mc.calibrations) == 2
        assert mc.calibrations[0].kV == 120
        assert mc.calibrations[0].dcf == 1.034
        assert mc.calibrations[1].dcf is None

    def test_duplicate_keys_raises(self, tmp_path: object) -> None:
        import pathlib

        p = pathlib.Path(str(tmp_path)) / "cal.yaml"
        dup_entries = (
            "  - kV: 120\n"
            "    fan_mode: 'Full Fan'\n"
            "    reference_mAs: 100.0\n"
            "  - kV: 120\n"
            "    fan_mode: 'Full Fan'\n"
            "    reference_mAs: 200.0\n"
        )
        p.write_text(_sample_yaml(entries=dup_entries))
        with pytest.raises(ValueError, match="Duplicate"):
            MachineCalibration.from_yaml(p)

    def test_missing_file_raises(self, tmp_path: object) -> None:
        import pathlib

        p = pathlib.Path(str(tmp_path)) / "nonexistent.yaml"
        with pytest.raises(FileNotFoundError):
            MachineCalibration.from_yaml(p)

    def test_empty_file_raises(self, tmp_path: object) -> None:
        import pathlib

        p = pathlib.Path(str(tmp_path)) / "empty.yaml"
        p.write_text("")
        with pytest.raises(ValueError, match="expected mapping"):
            MachineCalibration.from_yaml(p)

    def test_missing_calibrations_key_raises(self, tmp_path: object) -> None:
        import pathlib

        p = pathlib.Path(str(tmp_path)) / "no_cal.yaml"
        p.write_text("machine: 'TB1'\ndate_calibrated: '2026-01-01'\n")
        with pytest.raises(ValueError, match="missing 'calibrations' key"):
            MachineCalibration.from_yaml(p)


class TestToYaml:
    def test_round_trip(self, tmp_path: object) -> None:
        import pathlib

        p = pathlib.Path(str(tmp_path)) / "cal.yaml"
        p.write_text(_sample_yaml(entries=_SAMPLE_ENTRIES))
        original = MachineCalibration.from_yaml(p)

        out_path = pathlib.Path(str(tmp_path)) / "out.yaml"
        original.to_yaml(out_path)
        loaded = MachineCalibration.from_yaml(out_path)

        assert loaded.machine == original.machine
        assert loaded.date_calibrated == original.date_calibrated
        assert len(loaded.calibrations) == len(original.calibrations)
        for orig, load in zip(original.calibrations, loaded.calibrations):
            assert orig == load

    def test_null_fields_preserved(self, tmp_path: object) -> None:
        import pathlib

        p = pathlib.Path(str(tmp_path)) / "cal.yaml"
        mc = MachineCalibration(
            machine="TB1",
            date_calibrated="2026-01-01",
            calibrations=(
                CalibrationEntry(kV=80, fan_mode="Full Fan", reference_mAs=100.0),
            ),
        )
        mc.to_yaml(p)
        loaded = MachineCalibration.from_yaml(p)
        assert loaded.calibrations[0].measured_ctdi_w_mGy is None
        assert loaded.calibrations[0].dcf is None


class TestFindEntry:
    def _make_machine(self) -> MachineCalibration:
        return MachineCalibration(
            machine="TB1",
            date_calibrated="2026-01-01",
            calibrations=(
                CalibrationEntry(kV=120, fan_mode="Full Fan", reference_mAs=100.0),
                CalibrationEntry(kV=80, fan_mode="Full Fan", reference_mAs=100.0),
            ),
        )

    def test_returns_matching_entry(self) -> None:
        mc = self._make_machine()
        entry = mc.find_entry(120, "Full Fan")
        assert entry is not None
        assert entry.kV == 120

    def test_returns_none_for_missing(self) -> None:
        mc = self._make_machine()
        assert mc.find_entry(140, "Half Fan") is None

    def test_different_fan_mode_not_matched(self) -> None:
        mc = self._make_machine()
        assert mc.find_entry(120, "Half Fan") is None
