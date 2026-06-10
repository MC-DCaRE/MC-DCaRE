"""Generates X-ray spectrum definitions via SpekPy for TOPAS beam sources."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone

import numpy as np
import spekpy as sp
import yaml

logger = logging.getLogger(__name__)


class SpectrumGenerator:
    """Creates SpekPy X-ray spectra and writes TOPAS-compatible spectrum files."""

    @staticmethod
    def generate(
        anode_voltage: float,
        exposure: float,
        histories: str,
        project_root: str,
        dose_calibration_factor: float = 1.0,
        fan_mode: str = "",
        seed: int = 9,
        threads: int = 1,
    ) -> None:
        """Generate a kV spectrum and write calibration factor and TOPAS spectrum files.

        Args:
            anode_voltage: Tube voltage in kV.
            exposure: Tube current-time product in mAs.
            histories: Number of primary histories as a string.
            project_root: Root directory of the MC-DCaRE project (output goes to tmp/).
            dose_calibration_factor: Multiplicative correction factor. Default 1.0
                (post-hoc calibration applied after simulation).
            fan_mode: Fan mode string ("Full Fan" or "Half Fan").
            seed: Random seed for reproducibility.
            threads: Number of simulation threads.
        """
        logger.info(
            "Generating spectrum: %f kV, %f mAs, %s histories",
            anode_voltage,
            exposure,
            histories,
        )
        # SpekPy energy bin width: dk=0.2 keV (finer spectral resolution than default 0.5 keV).
        # No SpekPy filtration is applied; filtration is modeled in TOPAS geometry
        # (0.7 mm Ti beam hardening filter, bowtie filter).
        s = sp.Spek(
            kvp=anode_voltage,
            th=14,
            mas=exposure,
            dk=0.2,
            z=0.1,
        )

        summary_of_inputs: str = s.state.get_current_state_str(
            "full", s.get_std_results()
        )
        karr, spkarr = s.get_spectrum(edges=False, diff=False)
        no_particles: float = 4 * np.pi * 0.1**2 * s.get_flu()

        if exposure <= 0:
            raise ValueError("exposure (mAs) must be positive, got %s" % exposure)
        if int(histories) <= 0:
            raise ValueError("histories must be positive, got %s" % histories)

        # Per-mAs normalization factor (independent of mAs due to SpekPy linearity).
        norm_factor: float = no_particles / (int(histories) * exposure)

        # Combined calibration factor for backward-compatible head_calibration_factor.txt.
        calib_factor: float = norm_factor * exposure * dose_calibration_factor

        # Write structured simulation metadata.
        metadata: dict = {
            "norm_factor": norm_factor,
            "mAs": exposure,
            "total_histories": int(histories),
            "dcf_used": dose_calibration_factor,
            "spekpy": {
                "kvp": anode_voltage,
                "th": 14,
                "dk": 0.2,
                "z": 0.1,
                "mas": exposure,
                "version": sp.__version__,
            },
            "fan_mode": fan_mode,
            "seed": seed,
            "threads": threads,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        metadata_path = os.path.join(project_root, "tmp", "simulation_metadata.yaml")
        with open(metadata_path, "w", encoding="utf-8") as f:
            yaml.dump(metadata, f, default_flow_style=False, sort_keys=False)
        logger.info("Simulation metadata written to %s", metadata_path)

        # Write backward-compatible head_calibration_factor.txt.
        calib_path = os.path.join(project_root, "tmp", "head_calibration_factor.txt")
        with open(calib_path, "w", encoding="utf-8") as f:
            f.write("%.10e" % calib_factor)
            f.write("\nMultiply dose by the factor above to get absolute dose \n")
            f.write("The number of histories in this run was: " + histories + "\n")
            f.write("Calibration factor = Number of particles/Histories\n")
            f.write("\n")
            f.write(summary_of_inputs)

        normalised_spec = spkarr / s.get_flu()

        normalised_spec_trimmed: list = []
        for i in normalised_spec:
            if i > 0.000001:
                normalised_spec_trimmed.append(float(format(i, ".6f")))
            else:
                normalised_spec_trimmed.append(0)

        weighted_fluence = np.asarray(normalised_spec_trimmed)
        energy_spectrum = karr
        energy_str = np.array2string(
            energy_spectrum, separator=" ", suppress_small=True
        )[1:-1]
        weight_str = np.array2string(
            weighted_fluence, separator=" ", suppress_small=True
        )[1:-1]
        converted_file: str = (
            "dv:So/beam/BeamEnergySpectrumValues = "
            + str(energy_spectrum.size)
            + "\n "
            + energy_str
            + " keV \n"
            + "\n uv:So/beam/BeamEnergySpectrumWeights = "
            + str(weighted_fluence.size)
            + "\n "
            + weight_str
        )

        spectrum_path = os.path.join(project_root, "tmp", "ConvertedTopasFile.txt")
        with open(spectrum_path, "w", encoding="utf-8") as f:
            f.write(converted_file)

        logger.info("Spectrum files written to %s/tmp/", project_root)
