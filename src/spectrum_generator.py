"""Generates X-ray spectrum definitions via SpekPy for TOPAS beam sources."""

from __future__ import annotations

import logging

import numpy as np
import spekpy as sp

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
    ) -> None:
        """Generate a kV spectrum and write calibration factor and TOPAS spectrum files.

        Args:
            anode_voltage: Tube voltage in kV.
            exposure: Tube current-time product in mAs.
            histories: Number of primary histories as a string.
            project_root: Root directory of the MC-DCaRE project (output goes to tmp/).
            dose_calibration_factor: Multiplicative correction factor derived from
                measurement-to-simulation CTDI-w ratio. Default 1.0 (no correction).
        """
        logger.info(
            "Generating spectrum: %f kV, %f mAs, %s histories",
            anode_voltage,
            exposure,
            histories,
        )
        # SpekPy inherent filtration: dk=0.2 mm Al equivalent.
        # TrueBeam GS-1542 tube spec lists 2.7 mm Al inherent filtration.
        # The 0.7 mm Ti filter is modeled separately in TOPAS geometry.
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

        calib_factor: float = (no_particles / int(histories)) * dose_calibration_factor
        import os

        calib_path = os.path.join(project_root, "tmp", "head_calibration_factor.txt")
        with open(calib_path, "w") as f:
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
        with open(spectrum_path, "w") as f:
            f.write(converted_file)

        logger.info("Spectrum files written to %s/tmp/", project_root)
