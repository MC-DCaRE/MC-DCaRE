"""Dose calibration service for post-hoc CTDI correction.

Computes, persists, and applies dose calibration factors (DCF) keyed by
``(kV, fan_mode)``.  Wraps :class:`CTDICalculator` to produce calibrated
CTDI-w results with optional mAs scaling.
"""

from __future__ import annotations

import logging
import math
from pathlib import Path
from typing import Dict, List, Optional

from src.models.calibration import CalibrationEntry, MachineCalibration
from src.services.ctdi_calculator import CTDICalculator

logger = logging.getLogger(__name__)


class CalibrationService:
    """Compute, lookup, and apply dose calibration factors."""

    def __init__(self, calibration_path: Path) -> None:
        self.calibration_path = Path(calibration_path)
        self._calibration = MachineCalibration.from_yaml(self.calibration_path)

    def compute_dcf(
        self,
        kV: int,
        fan_mode: str,
        simulated_ctdi_w_Gy: float,
        measured_ctdi_w_mGy: float,
        force: bool = False,
    ) -> float:
        """Compute DCF and write back to calibration.yaml.

        Args:
            kV: Tube voltage in kV.
            fan_mode: Fan mode string.
            simulated_ctdi_w_Gy: CTDI-w from simulation in Gray.
            measured_ctdi_w_mGy: Reference CTDI-w from measurement in mGy.
            force: Allow overwriting an existing DCF.

        Returns:
            The computed DCF value.

        Raises:
            ValueError: No matching entry, or entry already has a DCF
                and *force* is False.
        """
        entry = self._calibration.find_entry(kV, fan_mode)
        if entry is None:
            raise ValueError("No calibration entry for (%d, %s)" % (kV, fan_mode))
        if entry.dcf is not None and not force:
            raise ValueError(
                "Entry (%d, %s) already has DCF=%.6f; use force=True to overwrite"
                % (kV, fan_mode, entry.dcf)
            )

        if not math.isfinite(simulated_ctdi_w_Gy) or simulated_ctdi_w_Gy <= 0:
            raise ValueError(
                "simulated_ctdi_w_Gy must be a positive finite number, got %s"
                % simulated_ctdi_w_Gy
            )
        if not math.isfinite(measured_ctdi_w_mGy) or measured_ctdi_w_mGy <= 0:
            raise ValueError(
                "measured_ctdi_w_mGy must be a positive finite number, got %s"
                % measured_ctdi_w_mGy
            )

        reference_Gy = measured_ctdi_w_mGy * 1e-3
        dcf = reference_Gy / simulated_ctdi_w_Gy

        # Rebuild calibration with updated entry (frozen dataclass).
        updated_entries = []
        for e in self._calibration.calibrations:
            if e.kV == kV and e.fan_mode == fan_mode:
                updated_entries.append(
                    CalibrationEntry(
                        kV=e.kV,
                        fan_mode=e.fan_mode,
                        reference_mAs=e.reference_mAs,
                        measured_ctdi_w_mGy=measured_ctdi_w_mGy,
                        dcf=dcf,
                    )
                )
            else:
                updated_entries.append(e)

        new_calibration = MachineCalibration(
            machine=self._calibration.machine,
            date_calibrated=self._calibration.date_calibrated,
            calibrations=tuple(updated_entries),
        )
        # Persist before updating in-memory state to avoid divergence on write failure.
        new_calibration.to_yaml(self.calibration_path)
        self._calibration = new_calibration
        logger.info("DCF computed for (%d, %s): %.6f", kV, fan_mode, dcf)
        return dcf

    def lookup_dcf(self, kV: int, fan_mode: str) -> Optional[float]:
        """Return DCF for (kV, fan_mode), or None if not calibrated."""
        entry = self._calibration.find_entry(kV, fan_mode)
        if entry is None:
            return None
        return entry.dcf

    def apply(
        self,
        runfolder: Path,
        kV: int,
        fan_mode: str,
        target_mAs: Optional[float] = None,
    ) -> List[Dict]:
        """Full calibration pipeline: CTDICalculator -> DCF -> mAs scaling.

        Args:
            runfolder: Path to the simulation runfolder.
            kV: Tube voltage in kV.
            fan_mode: Fan mode string.
            target_mAs: Optional mAs to scale to. If None, uses simulation mAs.

        Returns:
            List of result dicts with calibrated CTDI-w values.

        Raises:
            FileNotFoundError: If simulation_metadata.yaml is missing.
            ValueError: If DCF is None or CTDICalculator returns empty results.
        """
        metadata_path = runfolder / "simulation_metadata.yaml"
        if not metadata_path.exists():
            raise FileNotFoundError(
                "simulation_metadata.yaml not found in %s" % runfolder
            )

        calculator = CTDICalculator(runfolder)
        if calculator.simulation_metadata is None:
            raise ValueError("Could not read simulation metadata from %s" % runfolder)
        try:
            sim_mAs: float = float(calculator.simulation_metadata["mAs"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(
                "Malformed simulation_metadata.yaml in %s: %s" % (runfolder, exc)
            ) from exc

        results = calculator.calculate()
        if not results:
            raise ValueError("CTDICalculator returned empty results for %s" % runfolder)

        dcf = self.lookup_dcf(kV, fan_mode)
        if dcf is None:
            raise ValueError("No DCF calibrated for (%d, %s)" % (kV, fan_mode))

        mAs_ratio = 1.0
        if target_mAs is not None and target_mAs != sim_mAs:
            mAs_ratio = target_mAs / sim_mAs

        calibrated: List[Dict] = []
        for result in results:
            calibrated.append(
                {
                    **result,
                    "CTDI_w_calibrated": result["CTDI_w"] * dcf * mAs_ratio,
                    "dcf_applied": dcf,
                    "mAs_ratio": mAs_ratio,
                }
            )
        return calibrated
