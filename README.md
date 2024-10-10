# MC-DCaRE
## Monte Carlo - Dose Calculation for Risk Evaluation

This project was developed by National Cancer Centre Singapore Department of Radiation Oncology Physics for use in determining imaging dose to the patient in the Varian TrueBeam kV Imaging system. 

The project builds on both TOPAS and Geant4 libraries to simulate the Varian TrueBeam kV imaging beam delivery system and executes Monte Carlo dose computation. 

A graphical user interface will be generated to allow end-users easy input of the directory of CT DICOM image set as well as main imaging parameters. 

As such, the kV imaging dose due to 3D CBCT or 2D kV-kV received by patients during treatment can be estimated by Monte Carlo computation. 

The accuracy of our simulations is benchmarked against CTDI dose specifications specified in the Varian TrueBeam Technical Reference Guide - (Volume 2: Imaging) as well as in-house measurements.

Full descriptions of the simulation and beam model is in pre-publication. 

Version: Beta Prerelease 


## How to install and run 

### Install TOPASMC and Geant 4

[TOPASMC download link](https://www.topasmc.org/download)

[Geant4 Tooklkit download link](https://geant4.web.cern.ch/)

Take note of the file directory for TOPASMC and Geant4. 

### Running MC-DCaRE
To run MC-DCaRE, run the python script `topas_gui.py`. In the main menu, specify the your Geant4 directory and the file location of your topas binary. 
Select your function and input your parameters to be processed. 

