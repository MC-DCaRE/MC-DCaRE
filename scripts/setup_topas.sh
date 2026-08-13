# OpenTOPAS environment for all users
# Install: sudo cp /opt/topas/setup_topas.sh /etc/profile.d/topas.sh
# Or: source this file in individual user .bashrc profiles

export GEANT4_INSTALL="/opt/topas/GEANT4/geant4-install"
export TOPAS_G4_DATA_DIR="/opt/topas/GEANT4/G4DATA"
export LD_LIBRARY_PATH="/opt/topas/TOPAS/OpenTOPAS-install/lib:/opt/topas/GEANT4/geant4-install/lib:/opt/topas/GDCM/gdcm-install/lib:$LD_LIBRARY_PATH"
export PATH="/opt/topas/TOPAS/OpenTOPAS-install/bin:$PATH"