"""Phantom dose calculator for ICRP 145 voxelized phantom simulations.

Post-processes TOPAS ``DoseToMedium`` output from a voxelized MRCP-AM/AF
phantom into per-organ dose and ICRP 103 effective dose.

The calculator reads the 3D voxel dose grid, maps each voxel to an organ
using the voxelization material grid, computes mean organ doses, and
applies DCF normalization from :class:`CalibrationService` (the same
calibration database used for CTDI mode). ICRP 103 tissue weighting
factors are then applied for effective dose.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

from src.models.icrp103 import (
    ORDERED_TISSUES,
    TISSUE_WEIGHTING_FACTORS,
    map_organ_to_remainder_category,
    map_organ_to_tissue,
)
from src.services.calibration import CalibrationService, NormalizedDose
from src.services.ctdi_calculator import extract_scorer_histories

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class OrganDoseResult:
    """Dose result for a single organ."""

    organ_name: str
    n_voxels: int
    mean_dose_mGy: float
    std_dose_mGy: float
    sem_percent: float
    icrp103_tissue: str


@dataclass(frozen=True)
class TissueDoseResult:
    """Aggregated dose for an ICRP 103 tissue category."""

    tissue: str
    weighting_factor: float
    ht_mGy: float
    contribution_mSv: float
    source_organs: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class EffectiveDoseResult:
    """Full effective dose calculation result."""

    effective_dose_mSv: float
    tissue_results: List[TissueDoseResult]
    organ_results: List[OrganDoseResult]
    normalization: Optional[NormalizedDose]


class PhantomDoseCalculator:
    """Post-processes voxelized phantom dose output into organ and effective dose.

    The calculator implements a three-step pipeline:

    1. **Voxel-to-organ mapping**: Each voxel in the dose grid is matched to
       an organ using the material ID grid from the voxelization step.
    2. **DCF normalization**: Per-history organ doses are converted to
       absolute dose using the same :class:`CalibrationService` DCF as CTDI
       mode. The formula is::

           photons_per_mAs = spectrum_fluence * N_scoring / exposure_mAs
           absolute_Gy
               = (raw_Gy / n_scorer_active_histories) * photons_per_mAs * mAs * DCF

       ``n_scorer_active_histories`` is read from the dose CSV's
       ``Histories_with_Scorer_Active`` column (falling back to
       ``total_histories`` when absent), so the same DCF applies to CTDI,
       phantom, and DICOM simulations.
    3. **ICRP 103 effective dose**: Organ doses are mapped to ICRP 103 tissue
       categories, mean tissue doses are computed, and tissue weighting
       factors are applied.

    Args:
        dose_csv_path: Path to the TOPAS ``phantom_dose.csv`` output.
        voxel_grid_path: Path to the ``.npy`` material ID grid from
            voxelization (see :mod:`scripts.voxelize_mrcp_am_fast`).
        material_file_path: Path to the ICRP 145 ``.material`` file.
    """

    def __init__(
        self,
        dose_csv_path: str | Path,
        voxel_grid_path: str | Path,
        material_file_path: str | Path,
    ) -> None:
        self.dose_csv_path = Path(dose_csv_path)
        self.voxel_grid_path = Path(voxel_grid_path)
        self.material_file_path = Path(material_file_path)

        self._grid: Optional[np.ndarray] = None
        self._materials: Optional[Dict[int, str]] = None
        self._organ_doses: Optional[Dict[str, List[float]]] = None

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    @property
    def grid(self) -> np.ndarray:
        """Material ID grid from voxelization."""
        if self._grid is None:
            self._grid = np.load(self.voxel_grid_path)
        return self._grid

    @property
    def materials(self) -> Dict[int, str]:
        """Mapping from material ID to organ name."""
        if self._materials is None:
            self._materials = self._parse_material_file()
        return self._materials

    def _parse_material_file(self) -> Dict[int, str]:
        """Parse the ICRP 145 ``.material`` file into an ID-to-name dict."""
        result: Dict[int, str] = {}
        current_organ = "Unknown"
        with open(self.material_file_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("C "):
                    parts = line.split(None, 2)
                    if len(parts) >= 2:
                        current_organ = parts[1]
                elif line.startswith("m") and not line.startswith("m g"):
                    parts = line.split()
                    if parts:
                        try:
                            result[int(parts[0][1:])] = current_organ
                        except ValueError:
                            pass
        logger.info(
            "Parsed %d material definitions from %s",
            len(result),
            self.material_file_path,
        )
        return result

    def _load_dose_data(self) -> Dict[str, List[float]]:
        """Load dose CSV and group voxel doses by organ name.

        Returns a dict mapping organ name to a list of per-voxel doses
        (in Gy, raw per-history values from TOPAS). Voxels with zero
        dose are **included** so that organ means are unbiased. DTM
        (collision-based) produces zero for voxels with no interaction;
        excluding them inflates the mean (selection bias). Including
        them makes DTM converge to TLE within ~4% under CPE.

        Voxels whose material ID is not in the .material file (e.g. ID 0
        for air/outside-body regions) are skipped, as are out-of-bounds
        indices and the sentinel mat_id == -1.
        """
        grid = self.grid
        materials = self.materials
        organ_doses: Dict[str, List[float]] = {}

        with open(self.dose_csv_path) as f:
            for line in f:
                if line.startswith("#") or not line.strip():
                    continue
                parts = line.strip().split(", ")
                if len(parts) < 4:
                    continue
                ix, iy, iz = int(parts[0]), int(parts[1]), int(parts[2])
                dose = float(parts[3])
                if ix >= grid.shape[0] or iy >= grid.shape[1] or iz >= grid.shape[2]:
                    continue
                mat_id = int(grid[ix, iy, iz])
                if mat_id == -1 or mat_id not in materials:
                    continue  # outside phantom body or unmapped (air)
                organ = materials[mat_id]
                organ_doses.setdefault(organ, []).append(dose)

        logger.info("Loaded dose data: %d organs", len(organ_doses))
        return organ_doses

    @property
    def organ_doses(self) -> Dict[str, List[float]]:
        """Raw per-voxel TOPAS Sum values keyed by organ name (total accumulated Gy)."""
        if self._organ_doses is None:
            self._organ_doses = self._load_dose_data()
        return self._organ_doses

    # ------------------------------------------------------------------
    # Dose calculation
    # ------------------------------------------------------------------

    def calculate(
        self,
        calibration_service: Optional[CalibrationService] = None,
        metadata: Optional[Dict] = None,
        target_mAs: Optional[float] = None,
        dcf_override: Optional[float] = None,
        scorer_type: str = "tle",
        remainder_convention: str = "all-organs",
    ) -> EffectiveDoseResult:
        """Compute organ doses and ICRP 103 effective dose with DCF normalization.

        Args:
            calibration_service: :class:`CalibrationService` for DCF lookup.
                If None, raw per-history doses are returned uncalibrated.
            metadata: Simulation metadata dict (from
                :meth:`CalibrationService.read_metadata`). Required if
                calibration_service is provided.
            target_mAs: Scan mAs to scale to (for partial scans). If None,
                uses the simulated mAs from metadata.
            dcf_override: DCF to use instead of calibration.yaml lookup.
            scorer_type: Which scorer's DCF to use (``"tle"``, ``"dtw"``,
                or ``"dtm"``). Defaults to ``"tle"``. Both TLE (dcf_tle)
                and DTM (dcf_water_dtm) DCFs are CTDI-derived and
                transferable to the phantom.
            remainder_convention: ``"all-organs"`` (default, historical)
                takes the arithmetic mean over every remainder-tagged
                organ; ``"icrp103"`` maps organs onto the 14 ICRP 103
                remainder categories first (category mean, then arithmetic
                mean over categories, with the >10 mSv update rule).

        Returns:
            :class:`EffectiveDoseResult` with full provenance.
        """
        # Compute normalization factor
        norm: Optional[NormalizedDose] = None
        scale_to_mGy = 1.0  # default: raw Gy -> raw mGy (no calibration)

        if calibration_service is not None and metadata is not None:
            # Inject the scorer-active history count (from the TOPAS CSV
            # Histories_with_Scorer_Active column) so normalize_dose divides
            # by the actual accumulated histories rather than metadata
            # total_histories. This auto-scales for phase-space replay
            # (N_phsp x M x R) and direct-beam (R x histories_per_run)
            # sources. NOTE: phantom DoseToMedium CSVs emitted by the current
            # TsTetGeomScorer/TsDicomPatient scorers only output Sum (no
            # Histories column), so this returns None for those runs and
            # normalize_dose falls back to total_histories -- correct for
            # direct-beam phantom sims but NOT for phase-space replay
            # (where total_histories != N_phsp x M x R). A warning is logged
            # in that case.
            n_scorer_active = extract_scorer_histories(self.dose_csv_path)
            norm_metadata: Dict = dict(metadata)
            if n_scorer_active is not None:
                norm_metadata["n_scorer_active_histories"] = n_scorer_active
            elif "n_scorer_active_histories" not in metadata:
                logger.warning(
                    "Phantom dose CSV %s has no Histories_with_Scorer_Active "
                    "column; falling back to metadata total_histories=%s for "
                    "normalization. This is correct for direct-beam phantom "
                    "sims but NOT for phase-space replay.",
                    self.dose_csv_path,
                    metadata.get("total_histories"),
                )
            # Use a representative organ dose to get the normalization constants
            # (the scale factor is the same for all organs since it's per-history).
            # Pick the organ with the highest mean to avoid organs whose mean is
            # zero (far-from-beam organs at low history counts may have all-zero
            # DTM voxels, which would cause division-by-zero).
            representative_dose = max(
                float(np.mean(doses)) for doses in self.organ_doses.values()
            )
            norm = calibration_service.normalize_dose(
                representative_dose,
                norm_metadata,
                target_mAs=target_mAs,
                dcf_override=dcf_override,
                scorer_type=scorer_type,
            )
            # scale_to_mGy converts raw per-history Gy to calibrated mGy
            if norm.calibrated_Gy is not None:
                scale_to_mGy = (
                    norm.calibrated_Gy / representative_dose * 1000
                )  # Gy -> mGy
            else:
                scale_to_mGy = norm.raw_Gy / representative_dose * 1000

        # Compute organ doses
        organ_results: List[OrganDoseResult] = []
        for organ, doses in self.organ_doses.items():
            n = len(doses)
            scaled_mGy = [d * scale_to_mGy for d in doses]
            mean_mGy = float(np.mean(scaled_mGy))
            std_mGy = float(np.std(scaled_mGy))
            sem_pct = (std_mGy / np.sqrt(n) / mean_mGy * 100) if mean_mGy > 0 else 0.0
            organ_results.append(
                OrganDoseResult(
                    organ_name=organ,
                    n_voxels=n,
                    mean_dose_mGy=mean_mGy,
                    std_dose_mGy=std_mGy,
                    sem_percent=sem_pct,
                    icrp103_tissue=map_organ_to_tissue(organ),
                )
            )
        organ_results.sort(key=lambda r: r.mean_dose_mGy, reverse=True)

        # Aggregate by ICRP 103 tissue
        tissue_doses: Dict[str, List[float]] = {}
        for result in organ_results:
            tissue = result.icrp103_tissue
            tissue_doses.setdefault(tissue, []).append(result.mean_dose_mGy)

        remainder_organs = [
            r.organ_name for r in organ_results if r.icrp103_tissue == "remainder"
        ]

        if remainder_convention == "icrp103":
            ht_remainder, remainder_detail = self._icrp103_remainder(
                tissue_doses, organ_results
            )
        elif remainder_convention == "all-organs":
            ht_remainder = (
                float(np.mean(tissue_doses.get("remainder", [0])))
                if tissue_doses.get("remainder")
                else 0.0
            )
        else:
            raise ValueError(
                f"unknown remainder_convention '{remainder_convention}' "
                "(expected 'all-organs' or 'icrp103')"
            )

        # Compute effective dose
        tissue_results: List[TissueDoseResult] = []
        effective_dose = 0.0
        for tissue in ORDERED_TISSUES:
            wT = TISSUE_WEIGHTING_FACTORS[tissue]
            if tissue == "remainder":
                ht = ht_remainder
                source = remainder_organs
            else:
                ht = (
                    float(np.mean(tissue_doses.get(tissue, [0])))
                    if tissue_doses.get(tissue)
                    else 0.0
                )
                source = [
                    r.organ_name for r in organ_results if r.icrp103_tissue == tissue
                ]
            contribution = wT * ht
            effective_dose += contribution
            tissue_results.append(
                TissueDoseResult(
                    tissue=tissue,
                    weighting_factor=wT,
                    ht_mGy=ht,
                    contribution_mSv=contribution,
                    source_organs=source,
                )
            )

        return EffectiveDoseResult(
            effective_dose_mSv=effective_dose,
            tissue_results=tissue_results,
            organ_results=organ_results,
            normalization=norm,
        )

    # ------------------------------------------------------------------
    # ICRP 103 remainder aggregation
    # ------------------------------------------------------------------

    @staticmethod
    def _icrp103_remainder(
        tissue_doses: Dict[str, List[float]],
        organ_results: List[OrganDoseResult],
    ) -> tuple[float, Dict[str, float]]:
        """ICRP 103 remainder HT: category mean, then mean over categories.

        Organs tagged ``remainder`` by :func:`map_organ_to_tissue` are
        further mapped to the 14 ICRP 103 remainder categories
        (:func:`map_organ_to_remainder_category`). Each category's dose is
        the arithmetic mean of its organ mean doses; the remainder HT is
        the arithmetic mean over the categories present (13 for a male
        phantom; ``uterus/cervix`` is absent).

        The ICRP 103 single-tissue update rule (assigning a separate wT
        when one remainder category exceeds 10 mSv) is NOT applied --
        the published MC benchmarks (Abuhaimed 2018 et al.) use the
        simple category mean.

        Args:
            tissue_doses: Organ mean doses keyed by ICRP 103 tissue tag.
            organ_results: Per-organ dose results (for name -> category).

        Returns:
            Tuple of (remainder HT in mGy, per-category HT dict).
        """
        del tissue_doses  # organ_results already carries everything needed
        category_doses: Dict[str, List[float]] = {}
        for r in organ_results:
            if r.icrp103_tissue != "remainder":
                continue
            category = map_organ_to_remainder_category(r.organ_name)
            if category is None:
                continue
            category_doses.setdefault(category, []).append(r.mean_dose_mGy)
        category_means = {
            cat: float(np.mean(v)) for cat, v in category_doses.items() if v
        }
        if not category_means:
            return 0.0, {}
        ht = float(np.mean(list(category_means.values())))
        logger.info(
            "ICRP 103 remainder: %d categories, HT = %.3f mGy",
            len(category_means),
            ht,
        )
        return ht, category_means

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    @staticmethod
    def format_report(result: EffectiveDoseResult) -> str:
        """Format an :class:`EffectiveDoseResult` as a human-readable string."""
        lines: List[str] = []
        lines.append("=" * 75)
        lines.append("ICRP 145 Phantom Dose Report")
        if result.normalization is not None:
            n = result.normalization
            lines.append(f"Normalization: DCF from {n.dcf_source}")
            lines.append(f"  DCF: {n.dcf}")
            lines.append(f"  photons_per_mAs: {n.photons_per_mAs:.4e}")
            lines.append(f"  mAs: {n.mAs_used:.1f} (simulated: {n.mAs_simulated:.1f})")
        else:
            lines.append("Normalization: none (raw per-history doses)")
        lines.append("=" * 75)

        # Tissue table
        lines.append("")
        lines.append(
            f"{'ICRP 103 Tissue':<20} {'wT':>5} {'HT (mGy)':>10} {'wT*HT (mSv)':>12}"
        )
        lines.append("-" * 50)
        for tr in result.tissue_results:
            lines.append(
                f"{tr.tissue:<20} {tr.weighting_factor:>5.2f} "
                f"{tr.ht_mGy:>10.3f} {tr.contribution_mSv:>12.4f}"
            )
        lines.append("-" * 50)
        lines.append(
            f"{'EFFECTIVE DOSE':<20} {'':>5} {'':>10} "
            f"{result.effective_dose_mSv:>12.2f} mSv"
        )

        # Organ table (top 20)
        lines.append("")
        lines.append(f"{'Organ':<42} {'Vox':>5} {'Dose (mGy)':>11} {'SEM%':>6}")
        lines.append("-" * 68)
        for r in result.organ_results[:20]:
            lines.append(
                f"{r.organ_name:<42} {r.n_voxels:>5} "
                f"{r.mean_dose_mGy:>11.3f} {r.sem_percent:>5.1f}%"
            )
        if len(result.organ_results) > 20:
            lines.append(f"... and {len(result.organ_results) - 20} more organs")

        return "\n".join(lines)
