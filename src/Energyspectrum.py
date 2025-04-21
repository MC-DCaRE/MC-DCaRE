import spekpy as sp
import numpy as np

def generate_new_topas_beam_profile(anode_voltage:float, exposure:float, Histories:str, path):
    s=sp.Spek(kvp=anode_voltage,th=14,mas =exposure,dk = 0.2, z=0.1) # unfiltered spectrum at 1mm 
    # s.filter('Al',2.7) #2.7mm filter at the kV xray tube exit window from manual

    summary_of_inputs = s.state.get_current_state_str('full', s.get_std_results())
    # Export (save) spectrum to file, doesnt seem to be used
    # s.export_spectrum('imaging_params.spk', comment='for topas export')
    # by default, diff is true but if not true, means fluence is given per bin (with width) instead of per energy (keV)
    # which results in sum(spkarr) = 2* s.get_flu. reason unknown. if diff set to true (use fluence in bin instead of 
    # per energy in keV)
    # this does not change the spectrum dynamic- only scale it across the whole spectrum by 0.5
    karr, spkarr = s.get_spectrum(edges= False, diff = False) # returns an array of photon energies and its corresponding fluence
    no_particles = 4*np.pi*0.1**2*s.get_flu()
    
    #multiply dose by this factor to get absolute dose - since reduce the numberhistories to 2009895
    calib_factor = no_particles/int(Histories) # no_particles/Histories
    with open(path + '/tmp/head_calibration_factor.txt', 'w') as f:
        f.write('%d' % calib_factor)
        f.write('\nMultiply dose by the factor above to get absolute dose \n')
        f.write('The number of histories in this run was: ' + Histories+'\n')
        f.write('Calibration factor = Number of particles/Histories\n')
        f.write('\n')
        f.write(summary_of_inputs)

    #normalising fluence by the total fluence to get weights for each energy bin 
    normalised_spec = spkarr/s.get_flu()
    #check that all weights sum up close to one
    # print(sum(normalised_spec))

    normalised_spec_trimmed = []
    for i in normalised_spec:
        if i >0.000001:
            #normalised_spec_trimmed.append(float(format(i, '.6f')))
            normalised_spec_trimmed.append(float(format(i, '.6f')))
        else:
            normalised_spec_trimmed.append(0)

    np.set_printoptions(suppress=True) #suppress removes scientific notation
    weightedFluence = np.asarray(normalised_spec_trimmed)
    weightedFluence = np.insert(weightedFluence, 0, weightedFluence.size)
    energySpectrum = np.insert(karr, 0, karr.size)
    energySpectrum = np.delete(energySpectrum, 0)
    weightedFluence = np.delete(weightedFluence, 0)
    convertedFile = "dv:So/beam/BeamEnergySpectrumValues = " + str(energySpectrum.size) + "\n " \
                    + str(energySpectrum)[1:-1] + " keV \n" \
                    + "\n uv:So/beam/BeamEnergySpectrumWeights = " + str(weightedFluence.size) + "\n "\
                    + str(weightedFluence)[1:-1]


    with open(path +'/tmp/ConvertedTopasFile.txt', 'w') as f:
        f.write(convertedFile)
        # ...


if __name__ == '__main__' : 
    # input values
    anode_voltage = 125 #'100 kV'
    exposure = 10 #'100 mAs'
    Histories = "100"
    generate_new_topas_beam_profile(anode_voltage, exposure, Histories, '/home/jkgan/MC-DCaRE')


