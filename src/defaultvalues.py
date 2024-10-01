# This sets up the default values for the GUI. Makes it easier to reference and make edits. 
# default_ = 


default_G4_Directory = '/root/G4Data'
default_TOPAS_Directory = '/root/topas/bin/topas '
default_Seed = '9'
default_Threads  = '4'
default_Histories = '100000'

# DICOM specific stuff
default_DICOM_Directory = '/root/nccs/Topas_wrapper/test/sampledicom/cherylair'
default_DICOM_RP_file = '/root/nccs/Topas_wrapper/test/sampledicom/cherylair/RP.Cheryl Phantom CTDI.Physics.dcm'
default_DICOM_TRANS_X = '0. mm'
default_DICOM_TRANS_Y = '0. mm'
default_DICOM_TRANS_Z = '0. mm'
default_DICOM_ROT_X = '0. deg'
default_DICOM_ROT_Y = '0. deg'
default_DICOM_ROT_Z = '0. deg'
default_DICOM_IMAGE_START_ANGLE = '0 deg'
default_DICOM_IMAGE_STOP_ANGLE = '0 deg'
default_DICOM_IMAGE_VOLTAGE = '100 kV'
default_DICOM_BEAM_CURRENT = '100 mAs'
default_DICOM_ISOCENTER_X = '0. mm'
default_DICOM_ISOCENTER_Y = '0. mm'
default_DICOM_ISOCENTER_Z = '0. mm'

default_DTM_Zbins = '100'
default_TLE_Zbins = '100'

default_PHYSICS_LIST = 'Default'
default_PHYSICS_PROCESS ='False'
default_PHYSICS_TYPE = 'Geant4_Modular'
default_PHYSICS_MODULES = '6 "g4em-standard_opt4" "g4h-phy_QGSP_BIC_HP" "g4decay" "g4ion-binarycascade" "g4h-elastic_HP" "g4stopping"'
default_PHYSICS_EM_MIN ='100. eV'
default_PHYSICS_EM_MAX ='521. MeV'

default_COUCH_TYPE = 'TsBox'
default_COUCH_MATERIAL = 'Aluminum'
default_COUCH_TRANS_X = '0. mm'
default_COUCH_TRANS_Y = 'Ge/couch/HLZ + Ge/CTDI/RMax mm'
default_COUCH_TRANS_Z = '0. mm'
default_COUCH_HLZ = '1000 mm'
default_COUCH_HLY = '0.4 mm'
default_COUCH_HLX = '260. mm'

default_TIME_SEQ_TIME = '501'
default_TIME_VERBOSITY = '0'
default_TIME_TIME_END = '501.0 s'
default_TIME_ROT_FUNC = 'Linear deg'
default_TIME_ROT_RATE = '0.4 deg/s'
default_TIME_ROT_START = '90.0 deg'
default_TIME_ROT_HISTORY = '100000'
