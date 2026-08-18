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
        fan_mode: str = "",
        seed: int = 9,
        threads: int = 1,
        filtration_mode: str = "hybrid",
        bhf_thickness_mm: float = 0.89,
        bhf_mode: str = "geometric",
    ) -> None:
        """Generate a kV spectrum and write metadata and TOPAS spectrum files.

        Args:
            anode_voltage: Tube voltage in kV.
            exposure: Tube current-time product in mAs.
            histories: Number of primary histories as a string.
            project_root: Root directory of the MC-DCaRE project (output goes to tmp/).
            fan_mode: Fan mode string ("Full Fan" or "Half Fan").
            seed: Random seed for reproducibility.
            threads: Number of simulation threads.
            filtration_mode: Where uniform base filtration lives. ``"hybrid"``
                (default) folds the inherent (2.7 mm Al) and collimator-window
                (0.3 mm Al) filtration into the SpekPy spectrum for improved beam
                hardening; ``"geometric"`` applies no SpekPy filtration (the
                prior/legacy behaviour).
            bhf_thickness_mm: Ti beam-hardening-filter physical thickness in mm.
            bhf_mode: ``"geometric"`` (default) keeps the Ti BHF as a physical
                TsBox in the beam line (templates render it; note TOPAS HLZ is a
                HALF-length, so the box spans 2x this thickness along Z).
                ``"spekpy"`` folds the Ti into the source spectrum via
                ``s.filter("Ti", thickness)`` and the templates omit the TsBox,
                so mm means mm with no half-length ambiguity. Switching modes
                changes the beam spectrum and requires re-running the CTDI DCF
                calibration.
        """
        if filtration_mode not in ("hybrid", "geometric"):
            raise ValueError(
                "filtration_mode must be 'hybrid' or 'geometric', got %r"
                % filtration_mode
            )
        if bhf_mode not in ("geometric", "spekpy"):
            raise ValueError(
                "bhf_mode must be 'geometric' or 'spekpy', got %r" % bhf_mode
            )
        if bhf_mode == "spekpy" and bhf_thickness_mm <= 0:
            raise ValueError(
                "bhf_mode='spekpy' requires bhf_thickness_mm > 0, got %s"
                % bhf_thickness_mm
            )
        logger.info(
            "Generating spectrum: %f kV, %f mAs, %s histories "
            "(filtration=%s, bhf=%s mm %s)",
            anode_voltage,
            exposure,
            histories,
            filtration_mode,
            bhf_thickness_mm,
            bhf_mode,
        )
        s = sp.Spek(
            kvp=anode_voltage,
            th=14,
            mas=exposure,
            dk=0.2,
            z=0.1,
        )

        # In hybrid mode the spatially-uniform pre-bow-tie filtration (inherent
        # tube + collimator polycarbon window, modelled as Al) is folded into
        # the source spectrum. The angular-dependent Ti BHF and bow-tie remain
        # geometric in both modes to preserve the off-axis profile.
        if filtration_mode == "hybrid":
            s.filter("Al", 2.7)
            s.filter("Al", 0.3)

        # Optional: fold the Ti BHF into the spectrum instead of a geometric
        # TsBox (bhf_mode="spekpy"). Removes the TOPAS half-length (HLZ)
        # ambiguity: the thickness here is the physical mm of Ti.
        if bhf_mode == "spekpy":
            s.filter("Ti", bhf_thickness_mm)

        hvl_mm_al: float = float(s.get_hvl1())
        logger.info("Spectrum first HVL: %.4f mm Al", hvl_mm_al)

        summary_of_inputs: str = s.state.get_current_state_str(
            "full", s.get_std_results()
        )
        karr, spkarr = s.get_spectrum(edges=False, diff=False)
        no_particles: float = 4 * np.pi * 0.1**2 * s.get_flu()

        if exposure <= 0:
            raise ValueError("exposure (mAs) must be positive, got %s" % exposure)
        if int(histories) <= 0:
            raise ValueError("histories must be positive, got %s" % histories)

        spectrum_fluence_photons_per_mAs: float = no_particles / int(histories)
        calib_factor: float = no_particles / int(histories)

        # Write structured simulation metadata (new schema).
        metadata: dict = {
            "total_histories": int(histories),
            "exposure_mAs": exposure,
            "spectrum_fluence_photons_per_mAs": float(spectrum_fluence_photons_per_mAs),
            "spekpy": {
                "kvp": anode_voltage,
                "th": 14,
                "dk": 0.2,
                "z": 0.1,
                "mas": exposure,
                "version": sp.__version__,
                "filtration_mode": filtration_mode,
                "bhf_mode": bhf_mode,
                "bhf_thickness_mm": bhf_thickness_mm,
                "hvl_mmAl": hvl_mm_al,
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

        # Write backward-compatible head_calibration_factor.txt (deprecated path).
        calib_path = os.path.join(project_root, "tmp", "head_calibration_factor.txt")
        with open(calib_path, "w", encoding="utf-8") as f:
            f.write("%.10e" % calib_factor)
            f.write("\nMultiply dose by the factor above to get absolute dose \n")
            f.write("The number of histories in this run was: " + histories + "\n")
            f.write("Calibration factor = Number of particles/Histories\n")
            f.write("Filtration mode: %s\n" % filtration_mode)
            f.write("Spectrum first HVL: %.4f mm Al\n" % hvl_mm_al)
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
