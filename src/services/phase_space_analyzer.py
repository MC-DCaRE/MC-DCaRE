"""Phase space file analyzer for TOPAS Binary format .phsp files.

Reads IAEA-format Binary phase space files produced by TOPAS PhaseSpace
scorers and computes beam characterization statistics: particle count,
energy spectrum, spatial/angular distributions, survival fraction.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

import numpy as np
import yaml

logger = logging.getLogger(__name__)

# TOPAS Binary format: each particle record is 7 doubles (56 bytes).
# Fields: x, y, z, dx (direction cosine x), dy, energy, weight
# Particle type is inferred (all gammas for kV imaging).
_RECORD_SIZE = 56  # 7 * 8 bytes


class PhaseSpaceAnalyzer:
    """Analyzes TOPAS Binary format .phsp files for beam characterization.

    Args:
        phsp_path: Path to the Binary format .phsp file.
        metadata_path: Optional path to simulation_metadata.yaml for
            computing survival fraction.
        n_bins: Number of histogram bins for spectral distributions.
    """

    def __init__(
        self,
        phsp_path: str,
        metadata_path: Optional[str] = None,
        n_bins: int = 100,
    ) -> None:
        self.phsp_path = phsp_path
        self.metadata_path = metadata_path
        self.n_bins = n_bins

    def analyze(self) -> Dict[str, Any]:
        """Read and analyze the phase space file.

        Returns:
            Dict with beam characterization statistics.
        """
        file_size_mb = os.path.getsize(self.phsp_path) / (1024 * 1024)
        n_records = int(os.path.getsize(self.phsp_path) / _RECORD_SIZE)

        logger.info(
            "Analyzing %s: %.2f MB, %d particles",
            self.phsp_path,
            file_size_mb,
            n_records,
        )

        if n_records == 0:
            return self._empty_result(file_size_mb)

        # Read all particle records into numpy arrays.
        data = np.fromfile(self.phsp_path, dtype=np.float64)
        data = data.reshape(-1, 7)

        x = data[:, 0]
        y = data[:, 1]
        z = data[:, 2]  # noqa: F841 — available for future spatial analysis
        dx = data[:, 3]
        dy = data[:, 4]
        energy = data[:, 5]
        weight = data[:, 6]  # noqa: F841 — available for weighted statistics

        particle_count = len(data)

        # Energy statistics.
        mean_energy = float(np.mean(energy))
        std_energy = float(np.std(energy))

        # Histograms.
        energy_counts, energy_edges = np.histogram(energy, bins=self.n_bins)
        spatial_x_counts, spatial_x_edges = np.histogram(x, bins=self.n_bins)
        spatial_y_counts, spatial_y_edges = np.histogram(y, bins=self.n_bins)
        angular_dx_counts, angular_dx_edges = np.histogram(dx, bins=self.n_bins)
        angular_dy_counts, angular_dy_edges = np.histogram(dy, bins=self.n_bins)

        # Particle types — all gammas for kV imaging.
        particle_types: Dict[str, int] = {"gamma": particle_count}

        # Survival fraction.
        survival_fraction: Optional[float] = None
        if self.metadata_path and os.path.isfile(self.metadata_path):
            survival_fraction = self._compute_survival_fraction(
                particle_count, self.metadata_path
            )

        return {
            "particle_count": particle_count,
            "survival_fraction": survival_fraction,
            "mean_energy_keV": mean_energy,
            "std_energy_keV": std_energy,
            "energy_spectrum": {
                "bin_edges": energy_edges.tolist(),
                "counts": energy_counts.tolist(),
            },
            "spatial_x": {
                "bin_edges": spatial_x_edges.tolist(),
                "counts": spatial_x_counts.tolist(),
            },
            "spatial_y": {
                "bin_edges": spatial_y_edges.tolist(),
                "counts": spatial_y_counts.tolist(),
            },
            "angular_dx": {
                "bin_edges": angular_dx_edges.tolist(),
                "counts": angular_dx_counts.tolist(),
            },
            "angular_dy": {
                "bin_edges": angular_dy_edges.tolist(),
                "counts": angular_dy_counts.tolist(),
            },
            "particle_types": particle_types,
            "file_size_mb": file_size_mb,
        }

    def _compute_survival_fraction(
        self, particle_count: int, metadata_path: str
    ) -> Optional[float]:
        """Compute particle_count / original_histories from metadata."""
        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = yaml.safe_load(f)
            if isinstance(metadata, dict) and "total_histories" in metadata:
                histories = int(metadata["total_histories"])
                if histories > 0:
                    return particle_count / histories
        except (OSError, yaml.YAMLError, ValueError, TypeError) as exc:
            logger.warning("Failed to read metadata for survival fraction: %s", exc)
        return None

    @staticmethod
    def _empty_result(file_size_mb: float) -> Dict[str, Any]:
        """Return a result dict for an empty phase space file."""
        return {
            "particle_count": 0,
            "survival_fraction": None,
            "mean_energy_keV": 0.0,
            "std_energy_keV": 0.0,
            "energy_spectrum": {"bin_edges": [], "counts": []},
            "spatial_x": {"bin_edges": [], "counts": []},
            "spatial_y": {"bin_edges": [], "counts": []},
            "angular_dx": {"bin_edges": [], "counts": []},
            "angular_dy": {"bin_edges": [], "counts": []},
            "particle_types": {},
            "file_size_mb": file_size_mb,
        }

    @staticmethod
    def create_synthetic_phsp(
        path: str, n_particles: int, energy_keV: float = 60.0
    ) -> str:
        """Create a synthetic .phsp file for testing.

        Generates ``n_particles`` records with fixed energy and Gaussian
        spatial/angular distributions.

        Args:
            path: Output file path.
            n_particles: Number of particle records to generate.
            energy_keV: Fixed energy for all particles.

        Returns:
            The path written to.
        """
        rng = np.random.default_rng(42)
        records: np.ndarray = np.zeros((n_particles, 7), dtype=np.float64)
        records[:, 0] = rng.normal(0, 10.0, n_particles)  # x (mm)
        records[:, 1] = rng.normal(0, 10.0, n_particles)  # y (mm)
        records[:, 2] = rng.normal(0, 10.0, n_particles)  # z (mm)
        records[:, 3] = rng.normal(0, 0.1, n_particles)  # dx
        records[:, 4] = rng.normal(0, 0.1, n_particles)  # dy
        records[:, 5] = energy_keV  # energy
        records[:, 6] = 1.0  # weight

        records.tofile(path)
        logger.info(
            "Created synthetic .phsp file: %s (%d particles)", path, n_particles
        )
        return path
