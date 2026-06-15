"""Calibration data model for per-machine dose calibration factors.

Exports :class:`CalibrationEntry` and :class:`MachineCalibration`, frozen
dataclasses that represent a single (kV, fan_mode) calibration measurement
and a per-machine collection of such entries, respectively. Supports
round-trip YAML serialization via :meth:`MachineCalibration.from_yaml` and
:meth:`MachineCalibration.to_yaml`.
"""

from __future__ import annotations

import logging
import os
import tempfile
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CalibrationEntry:
    """A single (kV, fan_mode) calibration measurement entry."""

    kV: int
    fan_mode: str
    reference_mAs: float
    measured_ctdi_w_mGy: Optional[float] = None
    dcf: Optional[float] = None
    reference_protocol: Optional[str] = None
    reference_ctdi_w_mGy: Optional[float] = None
    date: Optional[str] = None
    note: Optional[str] = None

    def __post_init__(self) -> None:
        for name in ("measured_ctdi_w_mGy", "dcf", "reference_ctdi_w_mGy"):
            val = getattr(self, name)
            if val is not None and not isinstance(val, (int, float)):
                raise TypeError(
                    "%s must be numeric, got %s" % (name, type(val).__name__)
                )


@dataclass(frozen=True)
class MachineCalibration:
    """Per-machine calibration data, keyed by (kV, fan_mode) entries."""

    machine: str
    date_calibrated: str
    calibrations: tuple[CalibrationEntry, ...] = field(default_factory=tuple)

    @classmethod
    def from_yaml(cls, path: Path) -> MachineCalibration:
        """Load calibration data from a YAML file.

        Args:
            path: Path to the YAML file.

        Returns:
            A new MachineCalibration populated from the file.

        Raises:
            FileNotFoundError: If the YAML file does not exist.
            ValueError: If duplicate (kV, fan_mode) entries are found.
        """
        yaml_path = Path(path)
        raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError(
                "Invalid calibration YAML: expected mapping, got %s"
                % type(raw).__name__
            )
        if "calibrations" not in raw:
            raise ValueError("Invalid calibration YAML: missing 'calibrations' key")
        entries = [CalibrationEntry(**e) for e in raw["calibrations"]]

        # Validate no duplicate keys
        keys = [(e.kV, e.fan_mode) for e in entries]
        counts = Counter(keys)
        duplicates = [k for k, c in counts.items() if c > 1]
        if duplicates:
            raise ValueError("Duplicate (kV, fan_mode) entries found: %s" % duplicates)

        return cls(
            machine=raw["machine"],
            date_calibrated=raw["date_calibrated"],
            calibrations=tuple(entries),
        )

    def to_yaml(self, path: Path) -> None:
        """Write calibration data to a YAML file.

        Args:
            path: Destination file path.
        """
        data = {
            "machine": self.machine,
            "date_calibrated": self.date_calibrated,
            "calibrations": [
                {
                    "kV": e.kV,
                    "fan_mode": e.fan_mode,
                    "reference_mAs": e.reference_mAs,
                    "measured_ctdi_w_mGy": e.measured_ctdi_w_mGy,
                    "dcf": e.dcf,
                    "reference_protocol": e.reference_protocol,
                    "reference_ctdi_w_mGy": e.reference_ctdi_w_mGy,
                    "date": e.date,
                    "note": e.note,
                }
                for e in self.calibrations
            ],
        }
        content = yaml.dump(data, default_flow_style=False, sort_keys=False)
        dest = Path(path)
        fd, tmp_path = tempfile.mkstemp(
            dir=str(dest.parent), prefix=dest.name + ".tmp", suffix=".yaml"
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(content)
            os.replace(tmp_path, str(dest))
        except BaseException:
            os.unlink(tmp_path) if os.path.exists(tmp_path) else None
            raise
        logger.info("Calibration data written to %s", path)

    def find_entry(self, kV: int, fan_mode: str) -> Optional[CalibrationEntry]:
        """Find a calibration entry by (kV, fan_mode).

        Args:
            kV: Tube voltage in kV.
            fan_mode: Fan mode string, e.g. ``"Full Fan"`` or ``"Half Fan"``.

        Returns:
            The matching CalibrationEntry, or None if not found.
        """
        for entry in self.calibrations:
            if entry.kV == kV and entry.fan_mode == fan_mode:
                return entry
        return None
