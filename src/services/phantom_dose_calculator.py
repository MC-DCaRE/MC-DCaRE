"""Phantom dose calculator for ICRP 145 voxelized phantom simulations.

Post-processes TOPAS ``DoseToMedium`` output from a voxelized MRCP-AM/AF
phantom into per-organ dose and ICRP 103 effective dose.

The calculator reads the 3D voxel dose grid, maps each voxel to an organ
using the voxelization material grid, computes mean organ doses, and
applies CTDIw-anchored absolute calibration followed by ICRP 103 tissue
weighting.
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
    map_organ_to_tissue,
)

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
    ctdiw_mGy: Optional[float]
    scale_factor: float
    anchor_organs: List[str]


class PhantomDoseCalculator:
    """Post-processes voxelized phantom dose output into organ and effective dose.

    The calculator implements a three-step normalization pipeline:

    1. **Voxel-to-organ mapping**: Each voxel in the dose grid is matched to
       an organ using the material ID grid from the voxelization step.
    2. **CTDIw anchoring**: The mean dose to isocenter-region organs (pelvic
       bones, bladder, etc.) is anchored to the measured CTDIw, providing
       absolute dose calibration that accounts for the source model and
       scatter conditions.
    3. **ICRP 103 effective dose**: Organ doses are mapped to ICRP 103 tissue
       categories, mean tissue doses are computed, and tissue weighting
       factors are applied.

    Args:
        dose_csv_path: Path to the TOPAS ``phantom_dose.csv`` output.
        voxel_grid_path: Path to the ``.npy`` material ID grid from
            voxelization (see :mod:`scripts.voxelize_mrcp_am_fast`).
        material_file_path: Path to the ICRP 145 ``.material`` file.
    """

    # Organs used for CTDIw anchoring (isocenter-region pelvic organs)
    DEFAULT_ANCHOR_ORGANS = [
        "Pelvis_spongiosa",
        "Pelvis_cortical",
        "Sacrum_spongiosa",
        "Sacrum_cortical",
        "Urinary_bladder_wall_insensitive",
        "Urinary_bladder_content",
        "Rectum_wall",
        "Prostate",
    ]

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
        (in Gy, raw per-history values from TOPAS).
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
                if dose <= 0:
                    continue
                if ix >= grid.shape[0] or iy >= grid.shape[1] or iz >= grid.shape[2]:
                    continue
                mat_id = int(grid[ix, iy, iz])
                if mat_id == -1:
                    continue  # voxel outside phantom body
                organ = materials.get(mat_id, "Unknown")
                organ_doses.setdefault(organ, []).append(dose)

        logger.info("Loaded dose data: %d organs with non-zero dose", len(organ_doses))
        return organ_doses

    @property
    def organ_doses(self) -> Dict[str, List[float]]:
        """Raw per-voxel dose lists keyed by organ name (Gy per history)."""
        if self._organ_doses is None:
            self._organ_doses = self._load_dose_data()
        return self._organ_doses

    # ------------------------------------------------------------------
    # Dose calculation
    # ------------------------------------------------------------------

    def calculate(
        self,
        ctdiw_mGy: Optional[float] = None,
        anchor_organs: Optional[List[str]] = None,
    ) -> EffectiveDoseResult:
        """Compute organ doses and ICRP 103 effective dose.

        Args:
            ctdiw_mGy: Measured CTDIw in mGy for absolute dose anchoring.
                If ``None``, raw per-history doses are returned without
                absolute calibration.
            anchor_organs: Organ names to use as the isocenter anchor.
                Defaults to :attr:`DEFAULT_ANCHOR_ORGANS`.

        Returns:
            :class:`EffectiveDoseResult` with full provenance.
        """
        if anchor_organs is None:
            anchor_organs = self.DEFAULT_ANCHOR_ORGANS

        # Compute anchor scale factor
        if ctdiw_mGy is not None:
            anchor_raw = []
            for organ in anchor_organs:
                if organ in self.organ_doses:
                    anchor_raw.append(np.mean(self.organ_doses[organ]))
            if not anchor_raw:
                raise ValueError(
                    "None of the anchor organs found in dose data: %s" % anchor_organs
                )
            anchor_mean_Gy = float(np.mean(anchor_raw))
            scale = ctdiw_mGy / anchor_mean_Gy  # mGy per Gy of raw dose
        else:
            scale = 1.0

        # Compute organ doses
        organ_results: List[OrganDoseResult] = []
        for organ, doses in self.organ_doses.items():
            n = len(doses)
            scaled_mGy = [d * scale for d in doses]
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

        # Remainder: arithmetic mean of all remainder organ doses
        remainder_organs = [
            r.organ_name for r in organ_results if r.icrp103_tissue == "remainder"
        ]

        # Compute effective dose
        tissue_results: List[TissueDoseResult] = []
        effective_dose = 0.0
        for tissue in ORDERED_TISSUES:
            wT = TISSUE_WEIGHTING_FACTORS[tissue]
            if tissue == "remainder":
                ht = (
                    float(np.mean(tissue_doses.get("remainder", [0])))
                    if tissue_doses.get("remainder")
                    else 0.0
                )
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
            ctdiw_mGy=ctdiw_mGy,
            scale_factor=scale,
            anchor_organs=anchor_organs,
        )

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    @staticmethod
    def format_report(result: EffectiveDoseResult) -> str:
        """Format an :class:`EffectiveDoseResult` as a human-readable string."""
        lines: List[str] = []
        lines.append("=" * 75)
        lines.append("ICRP 145 Phantom Dose Report")
        if result.ctdiw_mGy is not None:
            lines.append(
                f"Absolute calibration: CTDIw-anchored ({result.ctdiw_mGy} mGy)"
            )
            lines.append(f"Anchor organs: {', '.join(result.anchor_organs[:4])}...")
            lines.append(f"Scale factor: {result.scale_factor:.4e}")
        else:
            lines.append("Absolute calibration: none (raw per-history doses)")
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
