# MC-DCaRE
## Monte Carlo - Dose Calculation for Risk Evaluation

This project was developed by National Cancer Centre Singapore DRO Physics for use in determining imaging dose to the patient during treatment set up iin a Varian TrueBeam. 

The project requires both TOPAS MC and Geant 4. This python script is a wrapper that creates a graphical user interface that allows end point users to easily input a CT DICOM image set and the imaging parameters to determine the estimated imaging dose recieved by patients during treatment set up on top of their treatment dose. 

The script stimulates a Varian TrueBeam kV imaging source head and runs a Monte Carlo simulation using it. 

The accuracy of our simulations is benchmarked against in house results conducted on our Varian TrueBeam machines and against the CTDI information given in the Varian TrueBeam Technical Reference manual.

Version: Beta Prerelease 

User type: Fully unlocked engineering   
