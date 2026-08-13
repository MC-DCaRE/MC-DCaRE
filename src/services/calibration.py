"""Dose calibration service for post-hoc CTDI correction.

Computes, persists, and applies dose calibration factors (DCF) keyed by
``(kV, fan_mode)``.  Wraps :class:`CTDICalculator` to produce calibrated
CTDI-w results with optional mAs scaling. Also provides geometry-agnostic
:meth:`normalize_dose` for phantom and DICOM dose calibration.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.models.calibration import CalibrationEntry, MachineCalibration
from src.services.ctdi_calculator import CTDICalculator, PRIMARY_SCORER

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class NormalizedDose:
    """Result of applying DCF normalization to a raw dose value.

    Attributes:
        raw_Gy: Dose scaled by photons_per_mAs x mAs (no DCF applied).
        calibrated_Gy: Dose after DCF multiplication, or None if no DCF found.
        dcf: The DCF value applied, or None.
        dcf_source: Where the DCF came from: ``"calibration.yaml"``,
            ``"override"``, or ``"none"``.
        photons_per_mAs: kV-dependent constant (spectrum_fluence x
            total_histories / exposure_mAs).
        mAs_used: The mAs value used for scaling (target_mAs or
            mAs_simulated).
        mAs_simulated: The mAs used in the original simulation.
    """

    raw_Gy: float
    calibrated_Gy: Optional[float]
    dcf: Optional[float]
    dcf_source: str
    photons_per_mAs: float
    mAs_used: float
    mAs_simulated: float


def compute_photons_per_mAs(metadata: Dict[str, Any]) -> float:
    """Compute the kV-dependent photons-per-mAs beam constant.

    ``photons_per_mAs = spectrum_fluence * N_scoring / exposure_mAs``,
    falling back to ``norm_factor * N_scoring`` for legacy metadata that
    lacks ``spectrum_fluence_photons_per_mAs``.

    ``N_scoring`` is read from ``metadata["total_histories"]``. This is the
    number of histories the scoring run used to calibrate
    ``spectrum_fluence`` (= ``no_particles / N_scoring``), so it is a fixed
    property of the beam model, not of the current run. Because
    ``spectrum_fluence`` carries ``1 / N_scoring`` and this function
    multiplies by ``N_scoring``, the result collapses to
    ``no_particles / exposure_mAs`` -- the real photon count per mAs for
    the beam -- regardless of source type (direct beam or phase-space
    replay). Replay metadata must therefore keep
    ``spectrum_fluence_photons_per_mAs`` at the scoring-run value (the
    ``M x R`` scaling is handled by :func:`raw_absolute_dose_Gy` via
    ``N_scorer_active_histories``).

    Raises:
        ValueError: If ``total_histories`` (N_scoring) is missing/non-positive,
            or if neither ``spectrum_fluence`` nor ``norm_factor`` is usable.
    """
    n_scoring = metadata.get("total_histories", 0)
    exposure_mAs = metadata.get("exposure_mAs", 0.0)
    spectrum_fluence = metadata.get("spectrum_fluence_photons_per_mAs")
    if n_scoring <= 0:
        raise ValueError(
            "Cannot compute photons_per_mAs: total_histories (N_scoring) "
            "must be positive, got %s" % n_scoring
        )
    if spectrum_fluence is not None and spectrum_fluence > 0 and exposure_mAs > 0:
        return float(spectrum_fluence) * float(n_scoring) / float(exposure_mAs)
    norm_factor = metadata.get("norm_factor")
    if norm_factor:
        return float(norm_factor) * float(n_scoring)
    raise ValueError(
        "Cannot compute photons_per_mAs: need either "
        "spectrum_fluence_photons_per_mAs or norm_factor in metadata"
    )


def raw_absolute_dose_Gy(
    raw_sum: float,
    photons_per_mAs: float,
    n_scorer_active_histories: float,
    mAs_used: float,
) -> float:
    """Convert a TOPAS Sum (total accumulated) dose to absolute Gy (no DCF).

    Canonical normalization formula::

        raw_absolute_Gy
            = (raw_sum / n_scorer_active_histories) * photons_per_mAs * mAs_used

    ``raw_sum`` is the TOPAS Sum accumulated across all histories; dividing
    by ``n_scorer_active_histories`` (the actual number of histories the
    scorer accumulated over, as reported in the CSV
    ``Histories_with_Scorer_Active`` column) yields the per-history mean,
    which is then scaled to absolute dose via the kV-dependent
    ``photons_per_mAs`` and the scan ``mAs_used``. Using the CSV value
    (rather than ``total_histories`` from metadata) auto-scales for every
    source type: direct beam (``R x histories_per_run``), phase-space
    replay (``N_phsp x M x R``), and any combination. This is the single
    source of truth for raw-dose scaling; ``normalize_dose`` and every
    post-processing CLI routes through it.

    Raises:
        ValueError: If ``n_scorer_active_histories`` is not positive.
    """
    if n_scorer_active_histories <= 0:
        raise ValueError(
            "n_scorer_active_histories must be positive, got %s"
            % n_scorer_active_histories
        )
    return (raw_sum / n_scorer_active_histories) * photons_per_mAs * mAs_used


class CalibrationService:
    """Compute, lookup, and apply dose calibration factors.

    Supports per-scorer DCFs (tle, dtw, dtm, water_dtm). The ``scorer_type``
    parameter on lookup and normalization methods selects which DCF
    to use, defaulting to ``"tle"`` (Track Length Estimator).
    """

    # Map scorer_type strings to CalibrationEntry field names
    _DCF_FIELDS = {
        "tle": "dcf_tle",
        "dtw": "dcf_dtw",
        "dtm": "dcf_dtm",
        "water_dtm": "dcf_water_dtm",
    }

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
        scorer_type: str = "tle",
    ) -> float:
        """Compute DCF and write back to calibration.yaml.

        Args:
            kV: Tube voltage in kV.
            fan_mode: Fan mode string.
            simulated_ctdi_w_Gy: CTDI-w from simulation in Gray.
            measured_ctdi_w_mGy: Reference CTDI-w from measurement in mGy.
            force: Allow overwriting an existing DCF.
            scorer_type: Which scorer's DCF to compute (``"tle"``,
                ``"dtw"``, or ``"dtm"``).

        Returns:
            The computed DCF value.

        Raises:
            ValueError: No matching entry, or entry already has a DCF
                and *force* is False.
        """
        dcf_field = self._DCF_FIELDS.get(scorer_type, "dcf_tle")

        entry = self._calibration.find_entry(kV, fan_mode)
        if entry is None:
            raise ValueError("No calibration entry for (%d, %s)" % (kV, fan_mode))
        existing_dcf = getattr(entry, dcf_field)
        if existing_dcf is not None and not force:
            raise ValueError(
                "Entry (%d, %s) already has %s=%.6f; use force=True to overwrite"
                % (kV, fan_mode, dcf_field, existing_dcf)
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

        if existing_dcf is not None:
            logger.info(
                "Overwriting %s for (%d, %s): %.6e -> %.6e",
                dcf_field,
                kV,
                fan_mode,
                existing_dcf,
                dcf,
            )

        # Rebuild calibration with updated entry (frozen dataclass).
        updated_entries = []
        for e in self._calibration.calibrations:
            if e.kV == kV and e.fan_mode == fan_mode:
                kwargs = {
                    "kV": e.kV,
                    "fan_mode": e.fan_mode,
                    "reference_mAs": e.reference_mAs,
                    "measured_ctdi_w_mGy": measured_ctdi_w_mGy,
                    "dcf_tle": e.dcf_tle,
                    "dcf_dtw": e.dcf_dtw,
                    "dcf_dtm": e.dcf_dtm,
                    "dcf_water_dtm": e.dcf_water_dtm,
                    "reference_protocol": e.reference_protocol,
                    "reference_ctdi_w_mGy": e.reference_ctdi_w_mGy,
                    "date": e.date,
                    "note": e.note,
                }
                kwargs[dcf_field] = dcf
                updated_entries.append(CalibrationEntry(**kwargs))
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
        logger.info("DCF computed for (%d, %s): %.6e", kV, fan_mode, dcf)
        return dcf

    def lookup_dcf(
        self, kV: int, fan_mode: str, scorer_type: str = "tle"
    ) -> Optional[float]:
        """Return DCF for (kV, fan_mode, scorer_type), or None if not calibrated."""
        entry = self._calibration.find_entry(kV, fan_mode)
        if entry is None:
            return None
        dcf_field = self._DCF_FIELDS.get(scorer_type, "dcf_tle")
        return getattr(entry, dcf_field, None)

    @staticmethod
    def read_metadata(runfolder: Path) -> Dict[str, Any]:
        """Read simulation_metadata.yaml from a runfolder.

        Returns a dict with keys: total_histories, exposure_mAs,
        spectrum_fluence_photons_per_mAs, kV (from spekpy.kvp),
        fan_mode.
        """
        import yaml

        meta_path = runfolder / "simulation_metadata.yaml"
        if not meta_path.exists():
            raise FileNotFoundError(
                "simulation_metadata.yaml not found in %s" % runfolder
            )
        with open(meta_path) as f:
            metadata: Dict[str, Any] = dict(yaml.safe_load(f))

        # Flatten spekpy sub-dict for convenience
        spekpy = metadata.get("spekpy", {})
        metadata.setdefault("kV", int(spekpy.get("kvp", 0)))
        return metadata

    def normalize_dose(
        self,
        raw_dose_Gy: float,
        metadata: Dict[str, Any],
        kV: Optional[int] = None,
        fan_mode: Optional[str] = None,
        target_mAs: Optional[float] = None,
        dcf_override: Optional[float] = None,
        scorer_type: str = "tle",
    ) -> NormalizedDose:
        """Apply photons_per_mAs x mAs x DCF to any raw dose value.

        Geometry-agnostic normalization. Works for CTDI, phantom, or
        DICOM dose. The same DCF from calibration.yaml is applied
        regardless of phantom geometry.

        Normalization formula::

            photons_per_mAs = spectrum_fluence * N_scoring / exposure_mAs
            raw_absolute_Gy
                = (raw_dose / n_scorer_active_histories) * photons_per_mAs * mAs
            calibrated_Gy = raw_absolute_Gy * DCF

        ``n_scorer_active_histories`` is the actual scorer-active history
        count (from the TOPAS CSV ``Histories_with_Scorer_Active`` column),
        read from ``metadata["n_scorer_active_histories"]``. When absent
        (e.g. legacy metadata or scorers that do not emit the column), it
        falls back to ``metadata["total_histories"]`` so direct-beam
        simulations -- where the two are equal -- keep working.

        Args:
            raw_dose_Gy: TOPAS Sum (total accumulated dose across all
                histories) in Gy.
            metadata: Dict from :meth:`read_metadata` or
                ``CTDICalculator.calculate`` result.
            kV: Tube voltage. If None, read from metadata.
            fan_mode: Fan mode string. If None, read from metadata.
            target_mAs: Scan mAs to scale to. If None, uses simulated mAs.
            dcf_override: DCF to use instead of calibration.yaml lookup.
            scorer_type: Which scorer's DCF to use (``"tle"``, ``"dtw"``,
                or ``"dtm"``). Defaults to ``"tle"``.

        Returns:
            :class:`NormalizedDose` with full provenance.

        Raises:
            ValueError: If metadata is missing required fields.
        """
        n_scoring = metadata.get("total_histories", 0)
        exposure_mAs = metadata.get("exposure_mAs", 0.0)
        n_scorer_active = metadata.get("n_scorer_active_histories") or n_scoring

        if n_scoring <= 0 or exposure_mAs <= 0:
            raise ValueError(
                "Cannot normalize: invalid metadata "
                "(total_histories=%s, exposure_mAs=%s)" % (n_scoring, exposure_mAs)
            )
        if n_scorer_active <= 0:
            raise ValueError(
                "Cannot normalize: n_scorer_active_histories must be positive, "
                "got %s" % n_scorer_active
            )

        photons_per_mAs = compute_photons_per_mAs(metadata)

        mAs_simulated = exposure_mAs
        mAs_used = target_mAs if target_mAs is not None else mAs_simulated

        # Convert TOPAS Sum (total accumulated) to per-history mean using the
        # actual scorer-active history count from the CSV, then scale to
        # absolute Gy via photons_per_mAs x mAs. Routes through the canonical
        # helper so there is one normalization formula shared with the CLI
        # post-processing scripts.
        raw_absolute_Gy = raw_absolute_dose_Gy(
            raw_dose_Gy, photons_per_mAs, n_scorer_active, mAs_used
        )

        # DCF lookup
        resolved_kV = (
            kV or metadata.get("kV") or metadata.get("spekpy", {}).get("kvp", 0)
            if isinstance(metadata.get("spekpy"), dict)
            else kV or metadata.get("kV", 0)
        )
        resolved_kV = int(resolved_kV) if resolved_kV else 0
        resolved_fan = fan_mode or metadata.get("fan_mode", "")
        dcf: Optional[float] = dcf_override
        dcf_source = "none"

        if dcf_override is not None:
            dcf_source = "override"
        else:
            dcf_candidate = self.lookup_dcf(resolved_kV, resolved_fan, scorer_type)
            if dcf_candidate is not None:
                dcf = dcf_candidate
                dcf_source = "calibration.yaml"

        calibrated_Gy = raw_absolute_Gy * dcf if dcf is not None else None

        return NormalizedDose(
            raw_Gy=raw_absolute_Gy,
            calibrated_Gy=calibrated_Gy,
            dcf=dcf,
            dcf_source=dcf_source,
            photons_per_mAs=photons_per_mAs,
            mAs_used=mAs_used,
            mAs_simulated=mAs_simulated,
        )

    def normalize(
        self,
        raw_result: Dict,
        kV: int,
        fan_mode: str,
        target_mAs: Optional[float] = None,
        dcf_override: Optional[float] = None,
        scorer_type: str = "tle",
    ) -> Dict:
        """Apply full normalization pipeline to a single raw result.

        Computes CTDI-w in Gy by converting the TOPAS per-history dose to
        physical dose via photon scaling, then applying the DCF. Returns a
        dict with full provenance of all normalization steps.

        Normalization formula:
            photons_per_mAs = spectrum_fluence * N_scoring / mAs_simulated
            CTDI_w_raw_Gy
                = (raw_ctdi_w / n_scorer_active_histories) * photons_per_mAs * mAs_used
            CTDI_w_calibrated_Gy = CTDI_w_raw_Gy * DCF

        photons_per_mAs is the beam constant ``no_particles / mAs`` (the
        ``N_scoring`` in ``spectrum_fluence`` cancels the multiply), so it
        depends only on kV and tube geometry. ``n_scorer_active_histories``
        (read from the result metadata, populated by CTDICalculator from
        the CSV ``Histories_with_Scorer_Active`` column) auto-scales the
        per-history mean for direct-beam and phase-space-replay sources.

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
            - ``photons_per_mAs``
            - ``scorer_type``
            - ``is_primary``

        Raises:
            ValueError: If metadata is missing required fields.
        """
        raw_ctdi_w = raw_result.get("raw_sum", 0.0)
        if not math.isfinite(raw_ctdi_w):
            raise ValueError("raw_sum is not finite: %s" % raw_ctdi_w)

        metadata = raw_result.get("metadata", {})
        norm = self.normalize_dose(
            raw_ctdi_w,
            metadata,
            kV=kV,
            fan_mode=fan_mode,
            target_mAs=target_mAs,
            dcf_override=dcf_override,
            scorer_type=scorer_type,
        )

        return {
            "ctdi_w_calibrated_Gy": norm.calibrated_Gy,
            "ctdi_w_raw_Gy": norm.raw_Gy,
            "dcf_applied": norm.dcf,
            "dcf_source": norm.dcf_source if norm.dcf_source != "none" else None,
            "mAs_used": norm.mAs_used,
            "mAs_simulated": norm.mAs_simulated,
            "photons_per_mAs": norm.photons_per_mAs,
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
                    result,
                    kV,
                    fan_mode,
                    target_mAs=target_mAs,
                    scorer_type=scorer_type,
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
