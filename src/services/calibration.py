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
from src.services.ctdi_calculator import CTDICalculator, PRIMARY_SCORER

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

    def normalize(
        self,
        raw_result: Dict,
        kV: int,
        fan_mode: str,
        target_mAs: Optional[float] = None,
        dcf_override: Optional[float] = None,
    ) -> Dict:
        """Apply full normalization pipeline to a single raw result.

        Computes CTDI-w in Gy by applying norm_factor, mAs scaling, and
        DCF. Returns a dict with full provenance of all normalization
        steps.

        Normalization formula:
            norm_factor = spectrum_fluence / total_histories
            CTDI_w_raw_Gy = raw_ctdi_w * norm_factor * mAs_used
            CTDI_w_calibrated_Gy = CTDI_w_raw_Gy * DCF

        Args:
            raw_result: A single result dict from
                :meth:`CTDICalculator.calculate()`.
            kV: Tube voltage in kV.
            fan_mode: Fan mode string.
            target_mAs: Optional mAs to rescale to. If None, uses
                metadata exposure_mAs.
            dcf_override: Optional DCF override. If None, looks up
                from calibration.yaml.

        Returns:
            Dict with keys:
            - ``ctdi_w_calibrated_Gy``
            - ``ctdi_w_raw_Gy``
            - ``dcf_applied`` (float or None)
            - ``dcf_source`` (``"calibration.yaml"``, ``"override"``, or None)
            - ``mAs_used``
            - ``mAs_simulated``
            - ``norm_factor``
            - ``scorer_type``
            - ``is_primary``

        Raises:
            ValueError: If metadata is missing required fields.
        """
        metadata = raw_result.get("metadata", {})
        total_histories = metadata.get("total_histories", 0)
        exposure_mAs = metadata.get("exposure_mAs", 0.0)

        if total_histories <= 0 or exposure_mAs <= 0:
            raise ValueError(
                "Cannot normalize: invalid metadata "
                "(total_histories=%s, exposure_mAs=%s)"
                % (total_histories, exposure_mAs)
            )

        # Compute photons_per_mAs (constant for kV, independent of mAs and histories).
        spectrum_fluence = metadata.get("spectrum_fluence_photons_per_mAs")
        if spectrum_fluence is not None and spectrum_fluence > 0:
            photons_per_mAs = spectrum_fluence * total_histories / exposure_mAs
        elif metadata.get("norm_factor"):
            photons_per_mAs = metadata["norm_factor"] * total_histories
        else:
            raise ValueError(
                "Cannot compute photons_per_mAs: need either "
                "spectrum_fluence_photons_per_mAs or norm_factor in metadata"
            )

        mAs_simulated = exposure_mAs
        mAs_used = target_mAs if target_mAs is not None else mAs_simulated

        raw_ctdi_w = raw_result.get("raw_sum", 0.0)
        if not math.isfinite(raw_ctdi_w):
            raise ValueError("raw_sum is not finite: %s" % raw_ctdi_w)

        # raw Gy: per_history_dose x photons_per_mAs x mAs (no DCF)
        ctdi_w_raw_Gy = raw_ctdi_w * photons_per_mAs * mAs_used

        # DCF lookup
        dcf: Optional[float] = dcf_override
        dcf_source: Optional[str] = None
        if dcf_override is not None:
            dcf_source = "override"
        else:
            dcf_candidate = self.lookup_dcf(kV, fan_mode)
            if dcf_candidate is not None:
                dcf = dcf_candidate
                dcf_source = "calibration.yaml"

        ctdi_w_calibrated_Gy = ctdi_w_raw_Gy * dcf if dcf is not None else None

        return {
            "ctdi_w_calibrated_Gy": ctdi_w_calibrated_Gy,
            "ctdi_w_raw_Gy": ctdi_w_raw_Gy,
            "dcf_applied": dcf,
            "dcf_source": dcf_source,
            "mAs_used": mAs_used,
            "mAs_simulated": mAs_simulated,
            "photons_per_mAs": photons_per_mAs,
            "scorer_type": raw_result.get("scorer_type"),
            "is_primary": raw_result.get("is_primary", False),
        }

    def apply(
        self,
        runfolder: Path,
        kV: int,
        fan_mode: str,
        target_mAs: Optional[float] = None,
        scorer_type: str = PRIMARY_SCORER,
    ) -> List[Dict]:
        """Full calibration pipeline: CTDICalculator -> normalize -> DCF.

        Only results matching *scorer_type* (default ``"tle"``) receive
        the DCF and mAs correction.  All other scorer types are returned
        uncalibrated with ``"dcf_applied": null`` and a ``"note"`` field.

        Args:
            runfolder: Path to the simulation runfolder.
            kV: Tube voltage in kV.
            fan_mode: Fan mode string.
            target_mAs: Optional mAs to scale to. If None, uses simulation mAs.
            scorer_type: Which scorer type to calibrate (default ``"tle"``).

        Returns:
            List of result dicts with calibrated CTDI-w values.

        Raises:
            FileNotFoundError: If simulation_metadata.yaml is missing.
            ValueError: If CTDICalculator returns empty results.
        """
        calculator = CTDICalculator(runfolder)

        results = calculator.calculate()
        if not results:
            raise ValueError("CTDICalculator returned empty results for %s" % runfolder)

        calibrated: List[Dict] = []
        for result in results:
            if result.get("scorer_type") == scorer_type:
                norm_result = self.normalize(
                    result, kV, fan_mode, target_mAs=target_mAs
                )
                calibrated.append(
                    {
                        **result,
                        "CTDI_w_calibrated": norm_result["ctdi_w_calibrated_Gy"],
                        "CTDI_w_raw": norm_result["ctdi_w_raw_Gy"],
                        "dcf_applied": norm_result["dcf_applied"],
                        "mAs_ratio": norm_result["mAs_used"]
                        / norm_result["mAs_simulated"]
                        if norm_result["mAs_simulated"] > 0
                        else 1.0,
                    }
                )
            else:
                calibrated.append(
                    {
                        **result,
                        "CTDI_w_calibrated": None,
                        "CTDI_w_raw": None,
                        "dcf_applied": None,
                        "mAs_ratio": 1.0,
                        "note": "uncalibrated — secondary comparison",
                    }
                )
        return calibrated
