import numpy as np
import spekpy as sp


class SpectrumGenerator:
    @staticmethod
    def generate(
        anode_voltage: float,
        exposure: float,
        histories: str,
        project_root: str,
    ) -> None:
        s = sp.Spek(kvp=anode_voltage, th=14, mas=exposure, dk=0.2, z=0.1)

        summary_of_inputs = s.state.get_current_state_str("full", s.get_std_results())
        karr, spkarr = s.get_spectrum(edges=False, diff=False)
        no_particles = 4 * np.pi * 0.1**2 * s.get_flu()

        calib_factor = no_particles / int(histories)
        with open(project_root + "/tmp/head_calibration_factor.txt", "w") as f:
            f.write("%.10e" % calib_factor)
            f.write("\nMultiply dose by the factor above to get absolute dose \n")
            f.write("The number of histories in this run was: " + histories + "\n")
            f.write("Calibration factor = Number of particles/Histories\n")
            f.write("\n")
            f.write(summary_of_inputs)

        normalised_spec = spkarr / s.get_flu()

        normalised_spec_trimmed = []
        for i in normalised_spec:
            if i > 0.000001:
                normalised_spec_trimmed.append(float(format(i, ".6f")))
            else:
                normalised_spec_trimmed.append(0)

        np.set_printoptions(suppress=True)
        weighted_fluence = np.asarray(normalised_spec_trimmed)
        energy_spectrum = karr
        converted_file = (
            "dv:So/beam/BeamEnergySpectrumValues = "
            + str(energy_spectrum.size)
            + "\n "
            + str(energy_spectrum)[1:-1]
            + " keV \n"
            + "\n uv:So/beam/BeamEnergySpectrumWeights = "
            + str(weighted_fluence.size)
            + "\n "
            + str(weighted_fluence)[1:-1]
        )

        with open(project_root + "/tmp/ConvertedTopasFile.txt", "w") as f:
            f.write(converted_file)
