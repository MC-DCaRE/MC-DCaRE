#!/usr/bin/env python
# coding: utf-8

# In[1]:


import spekpy as sp
import math
import shutil

# In[2]:

print("\n** Script to generate a filtered spectrum and export to a file **\n")

# Generate unfiltered spectrum


#pelvis
s=sp.Spek(kvp=100,th=14,mas =10,dk = 0.2, z=0.1) # (270mAs/900projs)

#Filter the spectrum
#s.filter('Al', 2).filter('Be',2.7).filter('Ti',0.89).filter('Glass Borosilicate (Corning Pyrex 7740)', 1)
#from trubeam only got exit window, titanium, bow tie as filters. there is 2mm polycarbonate cover not sure if should simulate
# s.filter('Be',2.7).filter('Ti',0.89)
s.filter('Al',2.7)
# Export (save) spectrum to file
spek_name = 'testing.spk'

# by default, diff is true but if not true, means fluence is given per bin (with width) instead of per energy (keV)
# which results in sum(spkarr) = 2* s.get_flu. reason unknown. if diff set to true (use fluence in bin instead of 
# per energy in keV)
# this does not change the spectrum dynamic- only scale it across the whole spectrum by 0.5
karr, spkarr = s.get_spectrum(edges= False, diff = False) 
s.export_spectrum(spek_name, comment='for topas export')


# In[3]:


#check that parameters are correct
s.summarize(mode='full')


# In[4]:

no_particles = 4*math.pi*0.1**2*s.get_flu()
print(f'{no_particles:.2e}')
print(no_particles)


# In[5]:


#multiply dose by this factor to get absolute dose - since reduce the numberhistories to 2009895
calib_factor = no_particles/2009895
with open('head_calibration_factor.txt', 'w') as f:
  f.write('%d' % calib_factor)

# In[6]:


from matplotlib import pyplot as plt

plt.plot(karr, spkarr)
plt.xlabel('Energy [keV]')
plt.ylabel('Fluence per mAs per unit energy [photons/cm2/mAs/keV]')
plt.title('An example x-ray spectrum')
plt.show()


# In[7]:


#normalising fluence by the total fluence to get weights for each energy bin 
normalised_spec = spkarr/s.get_flu()
print(normalised_spec)


# In[8]:


#check that all weights sum up close to one
print(sum(normalised_spec))


# In[9]:


#truncate the decimal to the sixth place 
norm_lst = normalised_spec.tolist()

normalised_spec_trimmed = []
for i in normalised_spec:
    if i >0.000001:
        #normalised_spec_trimmed.append(float(format(i, '.6f')))
        normalised_spec_trimmed.append(float(format(i, '.6f')))
    else:
        normalised_spec_trimmed.append(0)


# In[10]:


#Saved weights in topas format
import numpy as np

#suppress removes scientific notation
np.set_printoptions(suppress=True)
weightedFluence = np.asarray(normalised_spec_trimmed)
weightedFluence = np.insert(weightedFluence, 0, weightedFluence.size)
energySpectrum = np.insert(karr, 0, karr.size)
print(weightedFluence)
print(energySpectrum)
energySpectrum = np.delete(energySpectrum, 0)
weightedFluence = np.delete(weightedFluence, 0)
convertedFile = "dv:So/beam/BeamEnergySpectrumValues = " + str(energySpectrum.size) + "\n " \
                + str(energySpectrum)[1:-1] + " keV \n" \
                + "\n uv:So/beam/BeamEnergySpectrumWeights = " + str(weightedFluence.size) + "\n "\
                + str(weightedFluence)[1:-1]
#f = open("ConvertedTopasFile.txt", "w")
#f.write(convertedFile)
#f.close

with open('ConvertedTopasFile.txt', 'w') as f:
    f.write(convertedFile)
    # ...

#copy file into sub directories containing the different positions 
shutil.copy('ConvertedTopasFile.txt', 'centre/')
shutil.copy('ConvertedTopasFile.txt', 'top/')
shutil.copy('ConvertedTopasFile.txt', 'bottom/')
shutil.copy('ConvertedTopasFile.txt', 'left/')
shutil.copy('ConvertedTopasFile.txt', 'right/')
# In[11]:


convertedFile


# Listing all materials and methods/class in spekpy below

# In[12]:


# List all materials in user directory
sp.Spek.show_matls()


# In[13]:


dir(sp.Spek)

