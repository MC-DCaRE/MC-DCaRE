#full package contains generate_allproc.py, headsourcecode.bat, runfolder. in run folder, there are seedsweepspreadcsv (consolidates all csv results) and topas_multiproc (multi-processes)
#headsourcecode is the source code from which generate_allproc modifies from to generate new file.
#generate_allproc includes all lines in the headsourcecode. 
#for selectcomponents in generate_allproc, setting 0 to respective component removes that chunk of lines from headsourcecode in the new file, by using the remove_lines_with_keywords fn. 
#param_range takes in the list of strings - the factor to be varied i.e. CollimatorsVertical_TransZ
#under the para for loop, declare the variable which is the factor to be varied. i.e. CollimatorsVertical_TransZ= para

#things to note:
#all parameters are declared in strings 'parameter'
#parameters which are strings in topas require additional inverted commas '"stringparameter"'
#globals()[chamberplugmaterial] = air is a lazy way of declaring the respective chamberplug detector as air material. 
#globals()[chamberplugmaterial] = pmma is declared at end of chamberplug selector loop to return variable to default pmma material for next chamberplug in the loop.


import math
import os
from itertools import product
from numpy import arange
import numpy as np

directory = os.getcwd()


selectcomponents = {
'ChamberPlugCentre': 1,
'ChamberPlugTop': 1,
'ChamberPlugBottom': 1,
'ChamberPlugLeft': 1,
'ChamberPlugRight': 1,
'ChamberPlugDose_tle': 1,
'ChamberPlugDose_dtm': 1,
'ChamberPlugDose_dtw': 1,
'CollimatorsVertical': 1,
'CollimatorsHorizontal': 1,
'TitaniumFilter': 1,
'BowtieFilter': 1,
'Coll1': 1,
'Coll2': 1,
'Coll3': 1,
'Coll4': 1,
'DemoFlat': 1,
'DemoRTrap': 1,
'DemoLTrap': 1,
'topsidebox': 1,
'bottomsidebox': 1,
'couch': 1
}

components_to_be_del = [key for key, value in selectcomponents.items() if value == 0]


def remove_lines_with_keywords(input_file, output_file, keywords):
    with open(input_file, 'r') as inp, open(output_file, 'w') as out:
        for line in inp:
            #all keywords must not be inside the line to execute the if code block
            if not any(keyword in line for keyword in keywords):
                out.write(line)
    return output_file


includeFile = 'ConvertedTopasFile_head.txt'
Seed = '9'
NumberOfThreads = '4'
G4DataDirectory = 'before'
World_HLX = '120'
World_HLY = '120'
World_HLZ = '120'
LayeredMassGeometryWorlds = '5 "ChamberPlugCentre" "ChamberPlugTop" "ChamberPlugBottom" "ChamberPlugLeft" "ChamberPlugRight"'
PMMA_Components = '3 "Carbon" "Hydrogen" "Oxygen"'
PMMA_Fractions = "'3 0.599848 0.080538 0.319614"
PMMA_Density = '1.190'
PMMA_MeanExcitationEnergy = '85.7'
PMMA_DefaultColor = '"Silver"'

CTDI_Type='"TsCylinder"'
CTDI_Parent='"World"'
CTDI_Material='"PMMA"'
CTDI_RMin="0.0"
CTDI_RMax="8.0"
CTDI_HL="7.25"
CTDI_SPhi="0."
CTDI_DPhi="360."
CTDI_TransX="0.0"
CTDI_TransY="0.0"
CTDI_TransZ="0.0"
CTDI_RotX="-90"

ChamberPlugCentre_Type='"TsCylinder"'
ChamberPlugCentre_Parent='"World"'
ChamberPlugCentre_Material='"PMMA"'
ChamberPlugCentre_RMin="0.0"
ChamberPlugCentre_RMax="0.655"
ChamberPlugCentre_HL="5.0"
ChamberPlugCentre_SPhi="0."
ChamberPlugCentre_DPhi="360."
ChamberPlugCentre_TransX="0.0"
ChamberPlugCentre_TransY="0.0"
ChamberPlugCentre_TransZ="0.0"
ChamberPlugCentre_isParallel='"True"'
ChamberPlugCentre_RotX="-90"
ChamberPlugCentre_color='"skyblue"'

ChamberPlugTop_Type='"TsCylinder"'
ChamberPlugTop_Parent='"World"'
ChamberPlugTop_Material='"PMMA"'
ChamberPlugTop_RMin="0.0"
ChamberPlugTop_RMax="0.655"
ChamberPlugTop_HL="5.0"
ChamberPlugTop_SPhi="0."
ChamberPlugTop_DPhi="360."
ChamberPlugTop_TransX="0.0"
ChamberPlugTop_TransY="0.0"
ChamberPlugTop_TransZ="-7.0"
ChamberPlugTop_isParallel='"True"'
ChamberPlugTop_RotX="-90"
ChamberPlugTop_color='"Magenta"'

ChamberPlugBottom_Type='"TsCylinder"'
ChamberPlugBottom_Parent='"World"'
ChamberPlugBottom_Material='"PMMA"'
ChamberPlugBottom_RMin="0.0"
ChamberPlugBottom_RMax="0.655"
ChamberPlugBottom_HL="5.0"
ChamberPlugBottom_SPhi="0."
ChamberPlugBottom_DPhi="360."
ChamberPlugBottom_TransX="0.0"
ChamberPlugBottom_TransY="0.0"
ChamberPlugBottom_TransZ="7.0"
ChamberPlugBottom_isParallel='"True"'
ChamberPlugBottom_RotX="-90"
ChamberPlugBottom_color='"Lime"'

ChamberPlugLeft_Type='"TsCylinder"'
ChamberPlugLeft_Parent='"World"'
ChamberPlugLeft_Material='"PMMA"'
ChamberPlugLeft_RMin="0.0"
ChamberPlugLeft_RMax="0.655"
ChamberPlugLeft_HL="5.0"
ChamberPlugLeft_SPhi="0."
ChamberPlugLeft_DPhi="360."
ChamberPlugLeft_TransX="-7.0"
ChamberPlugLeft_TransY="0.0"
ChamberPlugLeft_TransZ="0.0"
ChamberPlugLeft_isParallel='"True"'
ChamberPlugLeft_RotX="-90"
ChamberPlugLeft_color='"Orange"'

ChamberPlugRight_Type='"TsCylinder"'
ChamberPlugRight_Parent='"World"'
ChamberPlugRight_Material='"PMMA"'
ChamberPlugRight_RMin="0.0"
ChamberPlugRight_RMax="0.655"
ChamberPlugRight_HL="5.0"
ChamberPlugRight_SPhi="0."
ChamberPlugRight_DPhi="360."
ChamberPlugRight_TransX="7.0"
ChamberPlugRight_TransY="0.0"
ChamberPlugRight_TransZ="0.0"
ChamberPlugRight_isParallel='"True"'
ChamberPlugRight_RotX="-90"
ChamberPlugRight_color='"Brown"'

ChamberPlugDose_tle_Quantity='"TrackLengthEstimator"'
ChamberPlugDose_tle_InputFile='"Muen.dat"'
ChamberPlugDose_tle_Component='"ChamberPlug'
ChamberPlugDose_tle_IfOutputFileAlreadyExists='"Overwrite"'
ChamberPlugDose_tle_ZBins="100"

ChamberPlugDose_dtm_Quantity='"DoseToMaterial"'
ChamberPlugDose_dtm_Component='"ChamberPlug'
ChamberPlugDose_dtm_IfOutputFileAlreadyExists='"Overwrite"'
ChamberPlugDose_dtm_Material='"Air"'
ChamberPlugDose_dtm_ZBins="100"

ChamberPlugDose_dtw_Quantity='"DoseToWater"'
ChamberPlugDose_dtw_Component='"ChamberPlug'
ChamberPlugDose_dtw_IfOutputFileAlreadyExists='"Overwrite"'
ChamberPlugDose_dtw_ZBins="100"

#ChamberPlugDose_dtmd_Quantity='"DoseToMedium"'
#ChamberPlugDose_dtmd_Component='"ChamberPlug'
#ChamberPlugDose_dtmd_IfOutputFileAlreadyExists='"Overwrite"'
#ChamberPlugDose_dtmd_ZBins="100"

###output files
ChamberPlugDose_tle_OutputFile='ChamberPlug_tle"'
ChamberPlugDose_dtm_OutputFile='ChamberPlug_dtm"'
ChamberPlugDose_dtw_OutputFile='ChamberPlug_dtw"'
#ChamberPlugDose_dtmd_OutputFile='ChamberPlug_dtmd"'

Ph_ListName='"Default"'
Ph_ListProcesses='"False"'
Ph_Default_Type='"Geant4_Modular"'
Ph_Default_Modules='6 "g4em-standard_opt4" "g4h-phy_QGSP_BIC_HP" "g4decay" "g4ion-binarycascade" "g4h-elastic_HP" "g4stopping"'

Ph_Default_EMRangeMin="100."
Ph_Default_EMRangeMax="521."

Rotation_Type='"Group"'
Rotation_Parent='"World"'
Rotation_RotX="0."
Rotation_RotY="Tf_Rotate_Value"
Rotation_RotZ="0."
Rotation_TransX="0.0"
Rotation_TransY="0.0"
Rotation_TransZ="0.0"

CollimatorsVertical_Type='"Group"'
CollimatorsVertical_Parent='"Rotation"'
CollimatorsVertical_RotX="0."
CollimatorsVertical_RotY="0."
CollimatorsVertical_RotZ="0."
CollimatorsVertical_TransZ ="9.3"

CollimatorsHorizontal_Type='"Group"'
CollimatorsHorizontal_Parent='"CollimatorsVertical"'
CollimatorsHorizontal_RotX="0."
CollimatorsHorizontal_RotY="0."
CollimatorsHorizontal_RotZ="0."
CollimatorsHorizontal_TransZ="1.4"

BowtieFilter_Type='"Group"'
BowtieFilter_Parent='"CollimatorsHorizontal"'
BowtieFilter_RotX="0."
BowtieFilter_RotY="0."
BowtieFilter_RotZ="90."
BowtieFilter_TransX="0.0"
BowtieFilter_TransY="0.0"
BowtieFilter_TransZ="3.85"

Coll1_Type='"G4RTrap"'
Coll1_Parent='"CollimatorsVertical"'
Coll1_Material='"Lead"'
Coll1_TransX="0"
Coll1_TransY="5.27" #"5.27"
Coll1_TransZ="0"
Coll1_RotX="-90."
Coll1_RotY="90."
Coll1_RotZ="0"
Coll1_LZ="12."
Coll1_LY="0.3"
Coll1_LX="10."
Coll1_LTX="9.2"
Coll1_Color='"pink"'

Coll2_Type='"G4RTrap"'
Coll2_Parent='"CollimatorsVertical"'
Coll2_Material='"Lead"'
Coll2_TransX="0"
Coll2_TransY="-5.27" #"-5.27"
Coll2_TransZ="0"
Coll2_RotX="-90."
Coll2_RotY="270."
Coll2_RotZ="0"
Coll2_LZ="12."
Coll2_LY="0.3"
Coll2_LX="10."
Coll2_LTX="9.2"
Coll2_Color='"pink"'

Coll3_Type='"G4RTrap"'
Coll3_Parent='"CollimatorsHorizontal"'
Coll3_Material='"Lead"'
Coll3_TransX="5.27" #"5.27"
Coll3_TransY="0."
Coll3_TransZ="0."
Coll3_RotX="-90."
Coll3_RotY="180."
Coll3_RotZ="0"
Coll3_LZ="12."
Coll3_LY="0.3"
Coll3_LX="10."
Coll3_LTX="9.2"
Coll3_Color='"yellow"'

Coll4_Type='"G4RTrap"'
Coll4_Parent='"CollimatorsHorizontal"'
Coll4_Material='"Lead"'
Coll4_TransX="-5.27" #"-5.27"
Coll4_TransY="0."
Coll4_TransZ="0."
Coll4_RotX="-90."
Coll4_RotY="0."
Coll4_RotZ="0"
Coll4_LZ="12."
Coll4_LY="0.3"
Coll4_LX="10."
Coll4_LTX="9.2"
Coll4_Color='"yellow"'

Coll1steel_Type='"G4RTrap"'
Coll1steel_Material='"Steel"'
Coll1steel_Parent='"CollimatorsVertical"'
Coll1steel_TransX="0"
Coll1steel_TransY="0.2"
Coll1steel_TransZ="-0.25"
Coll1steel_RotX="-90."
Coll1steel_RotY="90."
Coll1steel_RotZ="0"
Coll1steel_LZ="12."
Coll1steel_LY="0.2"
Coll1steel_LX="10."
Coll1steel_LTX="10."

Coll2steel_Type='"G4RTrap"'
Coll2steel_Material='"Steel"'
Coll2steel_Parent='"CollimatorsVertical"'
Coll2steel_TransX="0"
Coll2steel_TransY="0.2"
Coll2steel_TransZ="-0.25"
Coll2steel_RotX="-90."
Coll2steel_RotY="270."
Coll2steel_RotZ="0"
Coll2steel_LZ="12."
Coll2steel_LY="0.2"
Coll2steel_LX="10."
Coll2steel_LTX="10."

Coll3steel_Type='"G4RTrap"'
Coll3steel_Material='"Steel"'
Coll3steel_Parent='"CollimatorsHorizontal"'
Coll3steel_TransX="0.2"
Coll3steel_TransY="0"
Coll3steel_TransZ="-0.25"
Coll3steel_RotX="-90."
Coll3steel_RotY="180."
Coll3steel_RotZ="0"
Coll3steel_LZ="12."
Coll3steel_LY="0.2"
Coll3steel_LX="10."
Coll3steel_LTX="10."

Coll4steel_Type='"G4RTrap"'
Coll4steel_Material='"Steel"'
Coll4steel_Parent='"CollimatorsHorizontal"'
Coll4steel_TransX="0.2"
Coll4steel_TransY="0"
Coll4steel_TransZ="-0.25"
Coll4steel_RotX="-90."
Coll4steel_RotY="0."
Coll4steel_RotZ="0"
Coll4steel_LZ="12."
Coll4steel_LY="0.2"
Coll4steel_LX="10."
Coll4steel_LTX="10."

TitaniumFilterGroup_Type='"Group"'
TitaniumFilterGroup_Parent='"CollimatorsHorizontal"'
TitaniumFilterGroup_RotX="0." 
TitaniumFilterGroup_RotY="0." 
TitaniumFilterGroup_RotZ="0." 
TitaniumFilterGroup_TransZ="1.59"

TitaniumFilter_Type='"TsBox"'
TitaniumFilter_Material='"Titanium"'
TitaniumFilter_Parent='"TitaniumFilterGroup"'
TitaniumFilter_HLX="10." 
TitaniumFilter_HLY="10." 
TitaniumFilter_HLZ="0.0445" 
TitaniumFilter_TransX="0." 
TitaniumFilter_TransY="0." 
TitaniumFilter_TransZ="0." #topreventoverlapwithtopandbottomcollimator
TitaniumFilter_RotX="0." 
TitaniumFilter_RotY="0." 
TitaniumFilter_RotZ="0." 
TitaniumFilter_Color='"lightblue"'
TitaniumFilter_DrawingStyle='"WireFrame"'

DemoFlat_Type='"TsBox"'
DemoFlat_Material='"Aluminum"'
DemoFlat_Parent='"BowtieFilter"'
DemoFlat_HLX="0.1"
DemoFlat_HLY="0.4"
DemoFlat_HLZ="7.5"
DemoFlat_TransX="0.0"
DemoFlat_TransY="0."
DemoFlat_TransZ="0"
DemoFlat_RotX="0."
DemoFlat_RotY="-90."
DemoFlat_RotZ="0."
DemoFlat_Color='"green"'

DemoRTrap_Type='"G4RTrap"'
DemoRTrap_Parent='"BowtieFilter"'
DemoRTrap_Material='"Aluminum"'
DemoRTrap_TransX="0.0"
DemoRTrap_TransY="-2.5"
DemoRTrap_TransZ="0.65"
DemoRTrap_RotX="0"
DemoRTrap_RotY="90"
DemoRTrap_RotZ="0."
DemoRTrap_LZ="15."
DemoRTrap_LY="5."
DemoRTrap_LX="2.8"
DemoRTrap_LTX="0.2"
DemoRTrap_Color='"pink"'

DemoLTrap_Type='"G4RTrap"'
DemoLTrap_Parent='"BowtieFilter"'
DemoLTrap_Material='"Aluminum"'
DemoLTrap_TransX="0.0"
DemoLTrap_TransY="2.5"
DemoLTrap_TransZ="0.65"
DemoLTrap_RotX="180"
DemoLTrap_RotY="270"
DemoLTrap_RotZ="0."
DemoLTrap_LZ="15."
DemoLTrap_LY="5.0"
DemoLTrap_LX="2.8"
DemoLTrap_LTX="0.2"
DemoLTrap_Color='"pink"'

topsidebox_Type='"TsBox"'
topsidebox_Material='"Aluminum"'
topsidebox_Parent='"BowtieFilter"'
topsidebox_HLX="1.4"
topsidebox_HLY="2.5"
topsidebox_HLZ="7.5"
topsidebox_TransX="0.0"
topsidebox_TransY="5.0"
topsidebox_TransZ="1.3"
topsidebox_RotX="0."
topsidebox_RotY="-90."
topsidebox_RotZ="0."
topsidebox_Color='"green"'

bottomsidebox_Type='"TsBox"'
bottomsidebox_Material='"Aluminum"'
bottomsidebox_Parent='"BowtieFilter"'
bottomsidebox_HLX="1.4"
bottomsidebox_HLY="2.5"
bottomsidebox_HLZ="7.5"
bottomsidebox_TransX="0.0"
bottomsidebox_TransY="-5.0"
bottomsidebox_TransZ="1.3"
bottomsidebox_RotX="0."
bottomsidebox_RotY="-90."
bottomsidebox_RotZ="0."
bottomsidebox_Color='"green"'

couch_Type='"TsBox"'
couch_Material='"Aluminum"'
couch_Parent='"World"'
couch_HLX="26.0"
couch_HLY="100.0"
couch_HLZ="0.075"
couch_TransX="0.0"
couch_TransY="0.0"
couch_TransZ="Ge/couch/HLZ + Ge/CTDI/RMax"
couch_Color='"red"'

BeamPosition_Parent='"Rotation"'
BeamPosition_Type='"Group"'
BeamPosition_TransX="0."
BeamPosition_TransY="0."
BeamPosition_TransZ="-100."
BeamPosition_RotX="0."
BeamPosition_RotY="0."
BeamPosition_RotZ="0."

BeamEnergySpectrumType='"Continuous"'
beam_Type='"Beam"'
beam_Component='"BeamPosition"'
beam_BeamParticle='"gamma"'
beam_BeamPositionDistribution='"Gaussian"'
beam_BeamPositionCutoffShape='"Rectangle"'
beam_BeamPositionCutoffX="5."
beam_BeamPositionCutoffY="5."
beam_BeamPositionSpreadX="0.04246"
beam_BeamPositionSpreadY="0.04246"
beam_BeamAngularDistribution='"Gaussian"'
beam_BeamAngularCutoffX="90"
beam_BeamAngularCutoffY="90"
beam_BeamAngularSpreadX="28"
beam_BeamAngularSpreadY="28"
beam_NumberOfHistoriesInRun="100000"

NumberOfSequentialTimes="501"
Verbosity="0"
TimelineEnd="501.0s"
Rotate_Function='"Linear deg"'
Rotate_Rate="0.4"
Rotate_StartValue="90.0"
ShowHistoryCountAtInterval="100000"

Enable='"F"'
ViewA_WindowSizeX="1024"
ViewA_WindowSizeY="768"

ViewA_Theta="-20.0"
ViewA_Phi="30.0"
ViewA_IncludeAxes='"True"'
ViewA_AxesSize="0.5"
ViewA_Zoom="2e+01"
ShowCPUTime='"True"'

boundaries_list = []
boundaries_name_list = []

#creates all possible inputs with range type 
#when user inputs a range type for one of the elements like CollimatorsVertical_TransZ, we search through this script and see if there is a 
#line containing CollimatorsVertical_TransZ + str('_start') if there is, unhash that line and change the zero values to the corresponding start stop step
#given by user
#then unhash the next line as well to append the name for file naming 

#Seed_start,Seed_stop,Seed_step = 0,0,0
#boundaries_list.append([Seed_start,Seed_stop,Seed_step])
#boundaries_name_list.append(['Seed'])

#NumberOfThreads_start,NumberOfThreads_stop,NumberOfThreads_step = 0,0,0
#boundaries_list.append([NumberOfThreads_start,NumberOfThreads_stop,NumberOfThreads_step])
#boundaries_name_list.append(['NumberOfThreads'])

#beam_NumberOfHistoriesInRun_start,beam_NumberOfHistoriesInRun_stop,beam_NumberOfHistoriesInRun_step = 0,0,0
#boundaries_list.append([beam_NumberOfHistoriesInRun_start,beam_NumberOfHistoriesInRun_stop,beam_NumberOfHistoriesInRun_step])
#boundaries_name_list.append(['beam_NumberOfHistoriesInRun'])

#CTDI_RMin_start,CTDI_RMin_stop,CTDI_RMin_step = 0,0,0
#boundaries_list.append([CTDI_RMin_start,CTDI_RMin_stop,CTDI_RMin_step])
#boundaries_name_list.append(['CTDI_RMin'])
#CTDI_RMax_start,CTDI_RMax_stop,CTDI_RMax_step = 0,0,0
#boundaries_list.append([CTDI_RMax_start,CTDI_RMax_stop,CTDI_RMax_step])
#boundaries_name_list.append(['CTDI_RMax'])
#CTDI_HL_start,CTDI_HL_stop,CTDI_HL_step = 0,0,0
#boundaries_list.append([CTDI_HL_start,CTDI_HL_stop,CTDI_HL_step])
#boundaries_name_list.append(['CTDI_HL'])
#CTDI_SPhi_start,CTDI_SPhi_stop,CTDI_SPhi_step = 0,0,0
#boundaries_list.append([CTDI_SPhi_start,CTDI_SPhi_stop,CTDI_SPhi_step])
#boundaries_name_list.append(['CTDI_SPhi'])
#CTDI_DPhi_start,CTDI_DPhi_stop,CTDI_DPhi_step = 0,0,0
#boundaries_list.append([CTDI_DPhi_start,CTDI_DPhi_stop,CTDI_DPhi_step])
#boundaries_name_list.append(['CTDI_DPhi'])
#CTDI_TransX_start,CTDI_TransX_stop,CTDI_TransX_step = 0,0,0
#boundaries_list.append([CTDI_TransX_start,CTDI_TransX_stop,CTDI_TransX_step])
#boundaries_name_list.append(['CTDI_TransX'])
#CTDI_TransY_start,CTDI_TransY_stop,CTDI_TransY_step = 0,0,0
#boundaries_list.append([CTDI_TransY_start,CTDI_TransY_stop,CTDI_TransY_step])
#boundaries_name_list.append(['CTDI_TransY'])
#CTDI_TransZ_start,CTDI_TransZ_stop,CTDI_TransZ_step = 0,0,0
#boundaries_list.append([CTDI_TransZ_start,CTDI_TransZ_stop,CTDI_TransZ_step])
#boundaries_name_list.append(['CTDI_TransZ'])
#CTDI_RotX_start,CTDI_RotX_stop,CTDI_RotX_step = 0,0,0
#boundaries_list.append([CTDI_RotX_start,CTDI_RotX_stop,CTDI_RotX_step])
#boundaries_name_list.append(['CTDI_RotX'])

#ChamberPlugCentre_RMin_start,ChamberPlugCentre_RMin_stop,ChamberPlugCentre_RMin_step = 0,0,0
#boundaries_list.append([ChamberPlugCentre_RMin_start,ChamberPlugCentre_RMin_stop,ChamberPlugCentre_RMin_step])
#boundaries_name_list.append(['ChamberPlugCentre_RMin'])
#ChamberPlugCentre_RMax_start,ChamberPlugCentre_RMax_stop,ChamberPlugCentre_RMax_step = 0,0,0
#boundaries_list.append([ChamberPlugCentre_RMax_start,ChamberPlugCentre_RMax_stop,ChamberPlugCentre_RMax_step])
#boundaries_name_list.append(['ChamberPlugCentre_RMax'])
#ChamberPlugCentre_HL_start,ChamberPlugCentre_HL_stop,ChamberPlugCentre_HL_step = 0,0,0
#boundaries_list.append([ChamberPlugCentre_HL_start,ChamberPlugCentre_HL_stop,ChamberPlugCentre_HL_step])
#boundaries_name_list.append(['ChamberPlugCentre_HL'])
#ChamberPlugCentre_SPhi_start,ChamberPlugCentre_SPhi_stop,ChamberPlugCentre_SPhi_step = 0,0,0
#boundaries_list.append([ChamberPlugCentre_SPhi_start,ChamberPlugCentre_SPhi_stop,ChamberPlugCentre_SPhi_step])
#boundaries_name_list.append(['ChamberPlugCentre_SPhi'])
#ChamberPlugCentre_DPhi_start,ChamberPlugCentre_DPhi_stop,ChamberPlugCentre_DPhi_step = 0,0,0
#boundaries_list.append([ChamberPlugCentre_DPhi_start,ChamberPlugCentre_DPhi_stop,ChamberPlugCentre_DPhi_step])
#boundaries_name_list.append(['ChamberPlugCentre_DPhi'])
#ChamberPlugCentre_TransX_start,ChamberPlugCentre_TransX_stop,ChamberPlugCentre_TransX_step = 0,0,0
#boundaries_list.append([ChamberPlugCentre_TransX_start,ChamberPlugCentre_TransX_stop,ChamberPlugCentre_TransX_step])
#boundaries_name_list.append(['ChamberPlugCentre_TransX'])
#ChamberPlugCentre_TransY_start,ChamberPlugCentre_TransY_stop,ChamberPlugCentre_TransY_step = 0,0,0
#boundaries_list.append([ChamberPlugCentre_TransY_start,ChamberPlugCentre_TransY_stop,ChamberPlugCentre_TransY_step])
#boundaries_name_list.append(['ChamberPlugCentre_TransY'])
#ChamberPlugCentre_TransZ_start,ChamberPlugCentre_TransZ_stop,ChamberPlugCentre_TransZ_step = 0,0,0
#boundaries_list.append([ChamberPlugCentre_TransZ_start,ChamberPlugCentre_TransZ_stop,ChamberPlugCentre_TransZ_step])
#boundaries_name_list.append(['ChamberPlugCentre_TransZ'])
#ChamberPlugCentre_RotX_start,ChamberPlugCentre_RotX_stop,ChamberPlugCentre_RotX_step = 0,0,0
#boundaries_list.append([ChamberPlugCentre_RotX_start,ChamberPlugCentre_RotX_stop,ChamberPlugCentre_RotX_step])
#boundaries_name_list.append(['ChamberPlugCentre_RotX'])

#ChamberPlugTop_RMin_start,ChamberPlugTop_RMin_stop,ChamberPlugTop_RMin_step = 0,0,0
#boundaries_list.append([ChamberPlugTop_RMin_start,ChamberPlugTop_RMin_stop,ChamberPlugTop_RMin_step])
#boundaries_name_list.append(['ChamberPlugTop_RMin'])
#ChamberPlugTop_RMax_start,ChamberPlugTop_RMax_stop,ChamberPlugTop_RMax_step = 0,0,0
#boundaries_list.append([ChamberPlugTop_RMax_start,ChamberPlugTop_RMax_stop,ChamberPlugTop_RMax_step])
#boundaries_name_list.append(['ChamberPlugTop_RMax'])
#ChamberPlugTop_HL_start,ChamberPlugTop_HL_stop,ChamberPlugTop_HL_step = 0,0,0
#boundaries_list.append([ChamberPlugTop_HL_start,ChamberPlugTop_HL_stop,ChamberPlugTop_HL_step])
#boundaries_name_list.append(['ChamberPlugTop_HL'])
#ChamberPlugTop_SPhi_start,ChamberPlugTop_SPhi_stop,ChamberPlugTop_SPhi_step = 0,0,0
#boundaries_list.append([ChamberPlugTop_SPhi_start,ChamberPlugTop_SPhi_stop,ChamberPlugTop_SPhi_step])
#boundaries_name_list.append(['ChamberPlugTop_SPhi'])
#ChamberPlugTop_DPhi_start,ChamberPlugTop_DPhi_stop,ChamberPlugTop_DPhi_step = 0,0,0
#boundaries_list.append([ChamberPlugTop_DPhi_start,ChamberPlugTop_DPhi_stop,ChamberPlugTop_DPhi_step])
#boundaries_name_list.append(['ChamberPlugTop_DPhi'])
#ChamberPlugTop_TransX_start,ChamberPlugTop_TransX_stop,ChamberPlugTop_TransX_step = 0,0,0
#boundaries_list.append([ChamberPlugTop_TransX_start,ChamberPlugTop_TransX_stop,ChamberPlugTop_TransX_step])
#boundaries_name_list.append(['ChamberPlugTop_TransX'])
#ChamberPlugTop_TransY_start,ChamberPlugTop_TransY_stop,ChamberPlugTop_TransY_step = 0,0,0
#boundaries_list.append([ChamberPlugTop_TransY_start,ChamberPlugTop_TransY_stop,ChamberPlugTop_TransY_step])
#boundaries_name_list.append(['ChamberPlugTop_TransY'])
#ChamberPlugTop_TransZ_start,ChamberPlugTop_TransZ_stop,ChamberPlugTop_TransZ_step = 0,0,0
#boundaries_list.append([ChamberPlugTop_TransZ_start,ChamberPlugTop_TransZ_stop,ChamberPlugTop_TransZ_step])
#boundaries_name_list.append(['ChamberPlugTop_TransZ'])
#ChamberPlugTop_RotX_start,ChamberPlugTop_RotX_stop,ChamberPlugTop_RotX_step = 0,0,0
#boundaries_list.append([ChamberPlugTop_RotX_start,ChamberPlugTop_RotX_stop,ChamberPlugTop_RotX_step])
#boundaries_name_list.append(['ChamberPlugTop_RotX'])

#ChamberPlugBottom_RMin_start,ChamberPlugBottom_RMin_stop,ChamberPlugBottom_RMin_step = 0,0,0
#boundaries_list.append([ChamberPlugBottom_RMin_start,ChamberPlugBottom_RMin_stop,ChamberPlugBottom_RMin_step])
#boundaries_name_list.append(['ChamberPlugBottom_RMin'])
#ChamberPlugBottom_RMax_start,ChamberPlugBottom_RMax_stop,ChamberPlugBottom_RMax_step = 0,0,0
#boundaries_list.append([ChamberPlugBottom_RMax_start,ChamberPlugBottom_RMax_stop,ChamberPlugBottom_RMax_step])
#boundaries_name_list.append(['ChamberPlugBottom_RMax'])
#ChamberPlugBottom_HL_start,ChamberPlugBottom_HL_stop,ChamberPlugBottom_HL_step = 0,0,0
#boundaries_list.append([ChamberPlugBottom_HL_start,ChamberPlugBottom_HL_stop,ChamberPlugBottom_HL_step])
#boundaries_name_list.append(['ChamberPlugBottom_HL'])
#ChamberPlugBottom_SPhi_start,ChamberPlugBottom_SPhi_stop,ChamberPlugBottom_SPhi_step = 0,0,0
#boundaries_list.append([ChamberPlugBottom_SPhi_start,ChamberPlugBottom_SPhi_stop,ChamberPlugBottom_SPhi_step])
#boundaries_name_list.append(['ChamberPlugBottom_SPhi'])
#ChamberPlugBottom_DPhi_start,ChamberPlugBottom_DPhi_stop,ChamberPlugBottom_DPhi_step = 0,0,0
#boundaries_list.append([ChamberPlugBottom_DPhi_start,ChamberPlugBottom_DPhi_stop,ChamberPlugBottom_DPhi_step])
#boundaries_name_list.append(['ChamberPlugBottom_DPhi'])
#ChamberPlugBottom_TransX_start,ChamberPlugBottom_TransX_stop,ChamberPlugBottom_TransX_step = 0,0,0
#boundaries_list.append([ChamberPlugBottom_TransX_start,ChamberPlugBottom_TransX_stop,ChamberPlugBottom_TransX_step])
#boundaries_name_list.append(['ChamberPlugBottom_TransX'])
#ChamberPlugBottom_TransY_start,ChamberPlugBottom_TransY_stop,ChamberPlugBottom_TransY_step = 0,0,0
#boundaries_list.append([ChamberPlugBottom_TransY_start,ChamberPlugBottom_TransY_stop,ChamberPlugBottom_TransY_step])
#boundaries_name_list.append(['ChamberPlugBottom_TransY'])
#ChamberPlugBottom_TransZ_start,ChamberPlugBottom_TransZ_stop,ChamberPlugBottom_TransZ_step = 0,0,0
#boundaries_list.append([ChamberPlugBottom_TransZ_start,ChamberPlugBottom_TransZ_stop,ChamberPlugBottom_TransZ_step])
#boundaries_name_list.append(['ChamberPlugBottom_TransZ'])
#ChamberPlugBottom_RotX_start,ChamberPlugBottom_RotX_stop,ChamberPlugBottom_RotX_step = 0,0,0
#boundaries_list.append([ChamberPlugBottom_RotX_start,ChamberPlugBottom_RotX_stop,ChamberPlugBottom_RotX_step])
#boundaries_name_list.append(['ChamberPlugBottom_RotX'])

#ChamberPlugLeft_RMin_start,ChamberPlugLeft_RMin_stop,ChamberPlugLeft_RMin_step = 0,0,0
#boundaries_list.append([ChamberPlugLeft_RMin_start,ChamberPlugLeft_RMin_stop,ChamberPlugLeft_RMin_step])
#boundaries_name_list.append(['ChamberPlugLeft_RMin'])
#ChamberPlugLeft_RMax_start,ChamberPlugLeft_RMax_stop,ChamberPlugLeft_RMax_step = 0,0,0
#boundaries_list.append([ChamberPlugLeft_RMax_start,ChamberPlugLeft_RMax_stop,ChamberPlugLeft_RMax_step])
#boundaries_name_list.append(['ChamberPlugLeft_RMax'])
#ChamberPlugLeft_HL_start,ChamberPlugLeft_HL_stop,ChamberPlugLeft_HL_step = 0,0,0
#boundaries_list.append([ChamberPlugLeft_HL_start,ChamberPlugLeft_HL_stop,ChamberPlugLeft_HL_step])
#boundaries_name_list.append(['ChamberPlugLeft_HL'])
#ChamberPlugLeft_SPhi_start,ChamberPlugLeft_SPhi_stop,ChamberPlugLeft_SPhi_step = 0,0,0
#boundaries_list.append([ChamberPlugLeft_SPhi_start,ChamberPlugLeft_SPhi_stop,ChamberPlugLeft_SPhi_step])
#boundaries_name_list.append(['ChamberPlugLeft_SPhi'])
#ChamberPlugLeft_DPhi_start,ChamberPlugLeft_DPhi_stop,ChamberPlugLeft_DPhi_step = 0,0,0
#boundaries_list.append([ChamberPlugLeft_DPhi_start,ChamberPlugLeft_DPhi_stop,ChamberPlugLeft_DPhi_step])
#boundaries_name_list.append(['ChamberPlugLeft_DPhi'])
#ChamberPlugLeft_TransX_start,ChamberPlugLeft_TransX_stop,ChamberPlugLeft_TransX_step = 0,0,0
#boundaries_list.append([ChamberPlugLeft_TransX_start,ChamberPlugLeft_TransX_stop,ChamberPlugLeft_TransX_step])
#boundaries_name_list.append(['ChamberPlugLeft_TransX'])
#ChamberPlugLeft_TransY_start,ChamberPlugLeft_TransY_stop,ChamberPlugLeft_TransY_step = 0,0,0
#boundaries_list.append([ChamberPlugLeft_TransY_start,ChamberPlugLeft_TransY_stop,ChamberPlugLeft_TransY_step])
#boundaries_name_list.append(['ChamberPlugLeft_TransY'])
#ChamberPlugLeft_TransZ_start,ChamberPlugLeft_TransZ_stop,ChamberPlugLeft_TransZ_step = 0,0,0
#boundaries_list.append([ChamberPlugLeft_TransZ_start,ChamberPlugLeft_TransZ_stop,ChamberPlugLeft_TransZ_step])
#boundaries_name_list.append(['ChamberPlugLeft_TransZ'])
#ChamberPlugLeft_RotX_start,ChamberPlugLeft_RotX_stop,ChamberPlugLeft_RotX_step = 0,0,0
#boundaries_list.append([ChamberPlugLeft_RotX_start,ChamberPlugLeft_RotX_stop,ChamberPlugLeft_RotX_step])
#boundaries_name_list.append(['ChamberPlugLeft_RotX'])

#ChamberPlugRight_RMin_start,ChamberPlugRight_RMin_stop,ChamberPlugRight_RMin_step = 0,0,0
#boundaries_list.append([ChamberPlugRight_RMin_start,ChamberPlugRight_RMin_stop,ChamberPlugRight_RMin_step])
#boundaries_name_list.append(['ChamberPlugRight_RMin'])
#ChamberPlugRight_RMax_start,ChamberPlugRight_RMax_stop,ChamberPlugRight_RMax_step = 0,0,0
#boundaries_list.append([ChamberPlugRight_RMax_start,ChamberPlugRight_RMax_stop,ChamberPlugRight_RMax_step])
#boundaries_name_list.append(['ChamberPlugRight_RMax'])
#ChamberPlugRight_HL_start,ChamberPlugRight_HL_stop,ChamberPlugRight_HL_step = 0,0,0
#boundaries_list.append([ChamberPlugRight_HL_start,ChamberPlugRight_HL_stop,ChamberPlugRight_HL_step])
#boundaries_name_list.append(['ChamberPlugRight_HL'])
#ChamberPlugRight_SPhi_start,ChamberPlugRight_SPhi_stop,ChamberPlugRight_SPhi_step = 0,0,0
#boundaries_list.append([ChamberPlugRight_SPhi_start,ChamberPlugRight_SPhi_stop,ChamberPlugRight_SPhi_step])
#boundaries_name_list.append(['ChamberPlugRight_SPhi'])
#ChamberPlugRight_DPhi_start,ChamberPlugRight_DPhi_stop,ChamberPlugRight_DPhi_step = 0,0,0
#boundaries_list.append([ChamberPlugRight_DPhi_start,ChamberPlugRight_DPhi_stop,ChamberPlugRight_DPhi_step])
#boundaries_name_list.append(['ChamberPlugRight_DPhi'])
#ChamberPlugRight_TransX_start,ChamberPlugRight_TransX_stop,ChamberPlugRight_TransX_step = 0,0,0
#boundaries_list.append([ChamberPlugRight_TransX_start,ChamberPlugRight_TransX_stop,ChamberPlugRight_TransX_step])
#boundaries_name_list.append(['ChamberPlugRight_TransX'])
#ChamberPlugRight_TransY_start,ChamberPlugRight_TransY_stop,ChamberPlugRight_TransY_step = 0,0,0
#boundaries_list.append([ChamberPlugRight_TransY_start,ChamberPlugRight_TransY_stop,ChamberPlugRight_TransY_step])
#boundaries_name_list.append(['ChamberPlugRight_TransY'])
#ChamberPlugRight_TransZ_start,ChamberPlugRight_TransZ_stop,ChamberPlugRight_TransZ_step = 0,0,0
#boundaries_list.append([ChamberPlugRight_TransZ_start,ChamberPlugRight_TransZ_stop,ChamberPlugRight_TransZ_step])
#boundaries_name_list.append(['ChamberPlugRight_TransZ'])
#ChamberPlugRight_RotX_start,ChamberPlugRight_RotX_stop,ChamberPlugRight_RotX_step = 0,0,0
#boundaries_list.append([ChamberPlugRight_RotX_start,ChamberPlugRight_RotX_stop,ChamberPlugRight_RotX_step])
#boundaries_name_list.append(['ChamberPlugRight_RotX'])

#Zbin scoring
#ChamberPlugDose_tle_ZBins_start,ChamberPlugDose_tle_ZBins_stop,ChamberPlugDose_tle_ZBins_step = 0,0,0
#boundaries_list.append([ChamberPlugDose_tle_ZBins_start,ChamberPlugDose_tle_ZBins_stop,ChamberPlugDose_tle_ZBins_step])
#boundaries_name_list.append(['ChamberPlugDose_tle_Zbins'])
#ChamberPlugDose_dtm_ZBins_start,ChamberPlugDose_dtm_ZBins_stop,ChamberPlugDose_dtm_ZBins_step = 0,0,0
#boundaries_list.append([ChamberPlugDose_dtm_ZBins_start,ChamberPlugDose_dtm_ZBins_stop,ChamberPlugDose_dtm_ZBins_step])
#boundaries_name_list.append(['ChamberPlugDose_dtm_Zbins'])
#ChamberPlugDose_dtw_ZBins_start,ChamberPlugDose_dtw_ZBins_stop,ChamberPlugDose_dtw_ZBins_step = 0,0,0
#boundaries_list.append([ChamberPlugDose_dtw_ZBins_start,ChamberPlugDose_dtw_ZBins_stop,ChamberPlugDose_dtw_ZBins_step])
#boundaries_name_list.append(['ChamberPlugDose_dtw_Zbins'])
#ChamberPlugDose_dtmd_ZBins_start,ChamberPlugDose_dtmd_ZBins_stop,ChamberPlugDose_dtmd_ZBins_step = 0,0,0
#boundaries_list.append([ChamberPlugDose_dtmd_ZBins_start,ChamberPlugDose_dtmd_ZBins_stop,ChamberPlugDose_dtmd_ZBins_step])
#boundaries_name_list.append(['ChamberPlugDose_dtmd_Zbins'])

#physics
#Ph_Default_EMRangeMin_start,Ph_Default_EMRangeMin_stop,Ph_Default_EMRangeMin_step = 0,0,0
#boundaries_list.append([Ph_Default_EMRangeMin_start,Ph_Default_EMRangeMin_stop,Ph_Default_EMRangeMin_step])
#boundaries_name_list.append(['Ph_Default_EMRangeMin'])
#Ph_Default_EMRangeMax_start,Ph_Default_EMRangeMax_stop,Ph_Default_EMRangeMax_step = 0,0,0
#boundaries_list.append([Ph_Default_EMRangeMax_start,Ph_Default_EMRangeMax_stop,Ph_Default_EMRangeMax_step])
#boundaries_name_list.append(['Ph_Default_EMRangeMax'])

#rotation
#Rotation_RotX_start,Rotation_RotX_stop,Rotation_RotX_step = 0,0,0
#boundaries_list.append([Rotation_RotX_start,Rotation_RotX_stop,Rotation_RotX_step])
#boundaries_name_list.append(['Rotation_RotX'])
#Rotation_RotY_start,Rotation_RotY_stop,Rotation_RotY_step = 0,0,0
#boundaries_list.append([Rotation_RotY_start,Rotation_RotY_stop,Rotation_RotY_step])
#boundaries_name_list.append(['Rotation_RotY'])
#Rotation_RotZ_start,Rotation_RotZ_stop,Rotation_RotZ_step = 0,0,0
#boundaries_list.append([Rotation_RotZ_start,Rotation_RotZ_stop,Rotation_RotZ_step])
#boundaries_name_list.append(['Rotation_RotZ'])
#Rotation_TransX_start,Rotation_TransX_stop,Rotation_TransX_step = 0,0,0
#boundaries_list.append([Rotation_TransX_start,Rotation_TransX_stop,Rotation_TransX_step])
#boundaries_name_list.append(['Rotation_TransX'])
#Rotation_TransY_start,Rotation_TransY_stop,Rotation_TransY_step = 0,0,0
#boundaries_list.append([Rotation_TransY_start,Rotation_TransY_stop,Rotation_TransY_step])
#boundaries_name_list.append(['Rotation_TransY'])
#Rotation_TransZ_start,Rotation_TransZ_stop,Rotation_TransZ_step = 0,0,0
#boundaries_list.append([Rotation_TransZ_start,Rotation_TransZ_stop,Rotation_TransZ_step])
#boundaries_name_list.append(['Rotation_TransZ'])

##collimatorsvertical
#CollimatorsVertical_RotX_start,CollimatorsVertical_RotX_stop,CollimatorsVertical_RotX_step = 0,0,0
#boundaries_list.append([CollimatorsVertical_RotX_start,CollimatorsVertical_RotX_stop,CollimatorsVertical_RotX_step])
#boundaries_name_list.append(['CollimatorsVertical_RotX'])
#CollimatorsVertical_RotY_start,CollimatorsVertical_RotY_stop,CollimatorsVertical_RotY_step = 0,0,0
#boundaries_list.append([CollimatorsVertical_RotY_start,CollimatorsVertical_RotY_stop,CollimatorsVertical_RotY_step])
#boundaries_name_list.append(['CollimatorsVertical_RotY']) 
#CollimatorsVertical_RotZ_start,CollimatorsVertical_RotZ_stop,CollimatorsVertical_RotZ_step = 0,0,0
#boundaries_list.append([CollimatorsVertical_RotZ_start,CollimatorsVertical_RotZ_stop,CollimatorsVertical_RotZ_step])
#boundaries_name_list.append(['CollimatorsVertical_RotZ']) 
#CollimatorsVertical_TransZ_start,CollimatorsVertical_TransZ_stop,CollimatorsVertical_TransZ_step = 0,0,0
#boundaries_list.append([CollimatorsVertical_TransZ_start,CollimatorsVertical_TransZ_stop,CollimatorsVertical_TransZ_step])
#boundaries_name_list.append(['CollimatorsVertical_TransZ']) 

##collimatorshorizontal
#CollimatorsHorizontal_RotX_start,CollimatorsHorizontal_RotX_stop,CollimatorsHorizontal_RotX_step = 0,0,0
#boundaries_list.append([CollimatorsHorizontal_RotX_start,CollimatorsHorizontal_RotX_stop,CollimatorsHorizontal_RotX_step])
#boundaries_name_list.append(['CollimatorsHorizontal_RotX'])
#CollimatorsHorizontal_RotY_start,CollimatorsHorizontal_RotY_stop,CollimatorsHorizontal_RotY_step = 0,0,0
#boundaries_list.append([CollimatorsHorizontal_RotY_start,CollimatorsHorizontal_RotY_stop,CollimatorsHorizontal_RotY_step])
#boundaries_name_list.append(['CollimatorsHorizontal_RotY']) 
#CollimatorsHorizontal_RotZ_start,CollimatorsHorizontal_RotZ_stop,CollimatorsHorizontal_RotZ_step = 0,0,0
#boundaries_list.append([CollimatorsHorizontal_RotZ_start,CollimatorsHorizontal_RotZ_stop,CollimatorsHorizontal_RotZ_step])
#boundaries_name_list.append(['CollimatorsHorizontal_RotZ']) 
#CollimatorsHorizontal_TransZ_start,CollimatorsHorizontal_TransZ_stop,CollimatorsHorizontal_TransZ_step = 0,0,0
#boundaries_list.append([CollimatorsHorizontal_TransZ_start,CollimatorsHorizontal_TransZ_stop,CollimatorsHorizontal_TransZ_step])
#boundaries_name_list.append(['CollimatorsHorizontal_TransZ']) 

##steelfilter
#SteelFilterGroup_RotX_start,SteelFilterGroup_RotX_stop,SteelFilterGroup_RotX_step = 0,0,0
#boundaries_list.append([SteelFilterGroup_RotX_start,SteelFilterGroup_RotX_stop,SteelFilterGroup_RotX_step])
#boundaries_name_list.append(['SteelFilterGroup_RotX'])
#SteelFilterGroup_RotY_start,SteelFilterGroup_RotY_stop,SteelFilterGroup_RotY_step = 0,0,0
#boundaries_list.append([SteelFilterGroup_RotY_start,SteelFilterGroup_RotY_stop,SteelFilterGroup_RotY_step])
#boundaries_name_list.append(['SteelFilterGroup_RotY']) 
#SteelFilterGroup_RotZ_start,SteelFilterGroup_RotZ_stop,SteelFilterGroup_RotZ_step = 0,0,0
#boundaries_list.append([SteelFilterGroup_RotZ_start,SteelFilterGroup_RotZ_stop,SteelFilterGroup_RotZ_step])
#boundaries_name_list.append(['SteelFilterGroup_RotZ']) 
#SteelFilterGroup_TransZ_start,SteelFilterGroup_TransZ_stop,SteelFilterGroup_TransZ_step = 0,0,0
#boundaries_list.append([SteelFilterGroup_TransZ_start,SteelFilterGroup_TransZ_stop,SteelFilterGroup_TransZ_step])
#boundaries_name_list.append(['SteelFilterGroup_TransZ']) 

##bowtiefilter
#BowtieFilter_RotX_start,BowtieFilter_RotX_stop,BowtieFilter_RotX_step = 0,0,0
#boundaries_list.append([BowtieFilter_RotX_start,BowtieFilter_RotX_stop,BowtieFilter_RotX_step])
#boundaries_name_list.append(['BowtieFilter_RotX'])
#BowtieFilter_RotY_start,BowtieFilter_RotY_stop,BowtieFilter_RotY_step = 0,0,0
#boundaries_list.append([BowtieFilter_RotY_start,BowtieFilter_RotY_stop,BowtieFilter_RotY_step])
#boundaries_name_list.append(['BowtieFilter_RotY']) 
#BowtieFilter_RotZ_start,BowtieFilter_RotZ_stop,BowtieFilter_RotZ_step = 0,0,0
#boundaries_list.append([BowtieFilter_RotZ_start,BowtieFilter_RotZ_stop,BowtieFilter_RotZ_step])
#boundaries_name_list.append(['BowtieFilter_RotZ']) 
#BowtieFilter_TransX_start,BowtieFilter_TransX_stop,BowtieFilter_TransX_step = 0,0,0
#boundaries_list.append([BowtieFilter_TransX_start,BowtieFilter_TransX_stop,BowtieFilter_TransX_step])
#boundaries_name_list.append(['BowtieFilter_TransX']) 
#BowtieFilter_TransY_start,BowtieFilter_TransY_stop,BowtieFilter_TransY_step = 0,0,0
#boundaries_list.append([BowtieFilter_TransY_start,BowtieFilter_TransY_stop,BowtieFilter_TransY_step])
#boundaries_name_list.append(['BowtieFilter_TransY'])
#BowtieFilter_TransZ_start,BowtieFilter_TransZ_stop,BowtieFilter_TransZ_step = 0,0,0
#boundaries_list.append([BowtieFilter_TransZ_start,BowtieFilter_TransZ_stop,BowtieFilter_TransZ_step])
#boundaries_name_list.append(['BowtieFilter_TransZ'])

##Coll1
#Coll1_TransX_start,Coll1_TransX_stop,Coll1_TransX_step = 0,0,0
#boundaries_list.append([Coll1_TransX_start,Coll1_TransX_stop,Coll1_TransX_step])
#boundaries_name_list.append(['Coll1_TransX'])
#Coll1_TransY_start,Coll1_TransY_stop,Coll1_TransY_step = 0,0,0
#boundaries_list.append([Coll1_TransY_start,Coll1_TransY_stop,Coll1_TransY_step])
#boundaries_name_list.append(['Coll1_TransY'])
#Coll1_TransZ_start,Coll1_TransZ_stop,Coll1_TransZ_step = 0,0,0
#boundaries_list.append([Coll1_TransZ_start,Coll1_TransZ_stop,Coll1_TransZ_step])
#boundaries_name_list.append(['Coll1_TransZ'])
#Coll1_RotX_start,Coll1_RotX_stop,Coll1_RotX_step = 0,0,0
#boundaries_list.append([Coll1_RotX_start,Coll1_RotX_stop,Coll1_RotX_step])
#boundaries_name_list.append(['Coll1_RotX'])
#Coll1_RotY_start,Coll1_RotY_stop,Coll1_RotY_step = 0,0,0
#boundaries_list.append([Coll1_RotY_start,Coll1_RotY_stop,Coll1_RotY_step])
#boundaries_name_list.append(['Coll1_RotY'])
#Coll1_RotZ_start,Coll1_RotZ_stop,Coll1_RotZ_step = 0,0,0
#boundaries_list.append([Coll1_RotZ_start,Coll1_RotZ_stop,Coll1_RotZ_step])
#boundaries_name_list.append(['Coll1_RotZ'])
#Coll1_LZ_start,Coll1_LZ_stop,Coll1_LZ_step = 0,0,0
#boundaries_list.append([Coll1_LZ_start,Coll1_LZ_stop,Coll1_LZ_step])
#boundaries_name_list.append(['Coll1_LZ'])
#Coll1_LY_start,Coll1_LY_stop,Coll1_LY_step = 0,0,0
#boundaries_list.append([Coll1_LY_start,Coll1_LY_stop,Coll1_LY_step])
#boundaries_name_list.append(['Coll1_LY'])
#Coll1_LX_start,Coll1_LX_stop,Coll1_LX_step = 0,0,0
#boundaries_list.append([Coll1_LX_start,Coll1_LX_stop,Coll1_LX_step])
#boundaries_name_list.append(['Coll1_LX'])
#Coll1_LTX_start,Coll1_LTX_stop,Coll1_LTX_step = 0,0,0
#boundaries_list.append([Coll1_LTX_start,Coll1_LTX_stop,Coll1_LTX_step])
#boundaries_name_list.append(['Coll1_LTX'])

##Coll2
#Coll2_TransX_start,Coll2_TransX_stop,Coll2_TransX_step = 0,0,0
#boundaries_list.append([Coll2_TransX_start,Coll2_TransX_stop,Coll2_TransX_step])
#boundaries_name_list.append(['Coll2_TransX'])
#Coll2_TransY_start,Coll2_TransY_stop,Coll2_TransY_step = 0,0,0
#boundaries_list.append([Coll2_TransY_start,Coll2_TransY_stop,Coll2_TransY_step])
#boundaries_name_list.append(['Coll2_TransY'])
#Coll2_TransZ_start,Coll2_TransZ_stop,Coll2_TransZ_step = 0,0,0
#boundaries_list.append([Coll2_TransZ_start,Coll2_TransZ_stop,Coll2_TransZ_step])
#boundaries_name_list.append(['Coll2_TransZ'])
#Coll2_RotX_start,Coll2_RotX_stop,Coll2_RotX_step = 0,0,0
#boundaries_list.append([Coll2_RotX_start,Coll2_RotX_stop,Coll2_RotX_step])
#boundaries_name_list.append(['Coll2_RotX'])
#Coll2_RotY_start,Coll2_RotY_stop,Coll2_RotY_step = 0,0,0
#boundaries_list.append([Coll2_RotY_start,Coll2_RotY_stop,Coll2_RotY_step])
#boundaries_name_list.append(['Coll2_RotY'])
#Coll2_RotZ_start,Coll2_RotZ_stop,Coll2_RotZ_step = 0,0,0
#boundaries_list.append([Coll2_RotZ_start,Coll2_RotZ_stop,Coll2_RotZ_step])
#boundaries_name_list.append(['Coll2_RotZ'])
#Coll2_LZ_start,Coll2_LZ_stop,Coll2_LZ_step = 0,0,0
#boundaries_list.append([Coll2_LZ_start,Coll2_LZ_stop,Coll2_LZ_step])
#boundaries_name_list.append(['Coll2_LZ'])
#Coll2_LY_start,Coll2_LY_stop,Coll2_LY_step = 0,0,0
#boundaries_list.append([Coll2_LY_start,Coll2_LY_stop,Coll2_LY_step])
#boundaries_name_list.append(['Coll2_LY'])
#Coll2_LX_start,Coll2_LX_stop,Coll2_LX_step = 0,0,0
#boundaries_list.append([Coll2_LX_start,Coll2_LX_stop,Coll2_LX_step])
#boundaries_name_list.append(['Coll2_LX'])
#Coll2_LTX_start,Coll2_LTX_stop,Coll2_LTX_step = 0,0,0
#boundaries_list.append([Coll2_LTX_start,Coll2_LTX_stop,Coll2_LTX_step])
#boundaries_name_list.append(['Coll2_LTX'])

##Coll3
#Coll3_TransX_start,Coll3_TransX_stop,Coll3_TransX_step = 0,0,0
#boundaries_list.append([Coll3_TransX_start,Coll3_TransX_stop,Coll3_TransX_step])
#boundaries_name_list.append(['Coll3_TransX'])
#Coll3_TransY_start,Coll3_TransY_stop,Coll3_TransY_step = 0,0,0
#boundaries_list.append([Coll3_TransY_start,Coll3_TransY_stop,Coll3_TransY_step])
#boundaries_name_list.append(['Coll3_TransY'])
#Coll3_TransZ_start,Coll3_TransZ_stop,Coll3_TransZ_step = 0,0,0
#boundaries_list.append([Coll3_TransZ_start,Coll3_TransZ_stop,Coll3_TransZ_step])
#boundaries_name_list.append(['Coll3_TransZ'])
#Coll3_RotX_start,Coll3_RotX_stop,Coll3_RotX_step = 0,0,0
#boundaries_list.append([Coll3_RotX_start,Coll3_RotX_stop,Coll3_RotX_step])
#boundaries_name_list.append(['Coll3_RotX'])
#Coll3_RotY_start,Coll3_RotY_stop,Coll3_RotY_step = 0,0,0
#boundaries_list.append([Coll3_RotY_start,Coll3_RotY_stop,Coll3_RotY_step])
#boundaries_name_list.append(['Coll3_RotY'])
#Coll3_RotZ_start,Coll3_RotZ_stop,Coll3_RotZ_step = 0,0,0
#boundaries_list.append([Coll3_RotZ_start,Coll3_RotZ_stop,Coll3_RotZ_step])
#boundaries_name_list.append(['Coll3_RotZ'])
#Coll3_LZ_start,Coll3_LZ_stop,Coll3_LZ_step = 0,0,0
#boundaries_list.append([Coll3_LZ_start,Coll3_LZ_stop,Coll3_LZ_step])
#boundaries_name_list.append(['Coll3_LZ'])
#Coll3_LY_start,Coll3_LY_stop,Coll3_LY_step = 0,0,0
#boundaries_list.append([Coll3_LY_start,Coll3_LY_stop,Coll3_LY_step])
#boundaries_name_list.append(['Coll3_LY'])
#Coll3_LX_start,Coll3_LX_stop,Coll3_LX_step = 0,0,0
#boundaries_list.append([Coll3_LX_start,Coll3_LX_stop,Coll3_LX_step])
#boundaries_name_list.append(['Coll3_LX'])
#Coll3_LTX_start,Coll3_LTX_stop,Coll3_LTX_step = 0,0,0
#boundaries_list.append([Coll3_LTX_start,Coll3_LTX_stop,Coll3_LTX_step])
#boundaries_name_list.append(['Coll3_LTX'])

##Coll4
#Coll4_TransX_start,Coll4_TransX_stop,Coll4_TransX_step = 0,0,0
#boundaries_list.append([Coll4_TransX_start,Coll4_TransX_stop,Coll4_TransX_step])
#boundaries_name_list.append(['Coll4_TransX'])
#Coll4_TransY_start,Coll4_TransY_stop,Coll4_TransY_step = 0,0,0
#boundaries_list.append([Coll4_TransY_start,Coll4_TransY_stop,Coll4_TransY_step])
#boundaries_name_list.append(['Coll4_TransY'])
#Coll4_TransZ_start,Coll4_TransZ_stop,Coll4_TransZ_step = 0,0,0
#boundaries_list.append([Coll4_TransZ_start,Coll4_TransZ_stop,Coll4_TransZ_step])
#boundaries_name_list.append(['Coll4_TransZ'])
#Coll4_RotX_start,Coll4_RotX_stop,Coll4_RotX_step = 0,0,0
#boundaries_list.append([Coll4_RotX_start,Coll4_RotX_stop,Coll4_RotX_step])
#boundaries_name_list.append(['Coll4_RotX'])
#Coll4_RotY_start,Coll4_RotY_stop,Coll4_RotY_step = 0,0,0
#boundaries_list.append([Coll4_RotY_start,Coll4_RotY_stop,Coll4_RotY_step])
#boundaries_name_list.append(['Coll4_RotY'])
#Coll4_RotZ_start,Coll4_RotZ_stop,Coll4_RotZ_step = 0,0,0
#boundaries_list.append([Coll4_RotZ_start,Coll4_RotZ_stop,Coll4_RotZ_step])
#boundaries_name_list.append(['Coll4_RotZ'])
#Coll4_LZ_start,Coll4_LZ_stop,Coll4_LZ_step = 0,0,0
#boundaries_list.append([Coll4_LZ_start,Coll4_LZ_stop,Coll4_LZ_step])
#boundaries_name_list.append(['Coll4_LZ'])
#Coll4_LY_start,Coll4_LY_stop,Coll4_LY_step = 0,0,0
#boundaries_list.append([Coll4_LY_start,Coll4_LY_stop,Coll4_LY_step])
#boundaries_name_list.append(['Coll4_LY'])
#Coll4_LX_start,Coll4_LX_stop,Coll4_LX_step = 0,0,0
#boundaries_list.append([Coll4_LX_start,Coll4_LX_stop,Coll4_LX_step])
#boundaries_name_list.append(['Coll4_LX'])
#Coll4_LTX_start,Coll4_LTX_stop,Coll4_LTX_step = 0,0,0
#boundaries_list.append([Coll4_LTX_start,Coll4_LTX_stop,Coll4_LTX_step])
#boundaries_name_list.append(['Coll4_LTX'])

#Coll1steel_TransX_start,Coll1steel_TransX_stop,Coll1steel_TransX_step = 0,0,0
#boundaries_list.append([Coll1steel_TransX_start,Coll1steel_TransX_stop,Coll1steel_TransX_step])
#boundaries_name_list.append(['Coll1steel_TransX'])
#Coll1steel_TransY_start,Coll1steel_TransY_stop,Coll1steel_TransY_step = 0,0,0
#boundaries_list.append([Coll1steel_TransY_start,Coll1steel_TransY_stop,Coll1steel_TransY_step])
#boundaries_name_list.append(['Coll1steel_TransY'])
#Coll1steel_TransZ_start,Coll1steel_TransZ_stop,Coll1steel_TransZ_step = 0,0,0
#boundaries_list.append([Coll1steel_TransZ_start,Coll1steel_TransZ_stop,Coll1steel_TransZ_step])
#boundaries_name_list.append(['Coll1steel_TransZ'])
#Coll1steel_RotX_start,Coll1steel_RotX_stop,Coll1steel_RotX_step = 0,0,0
#boundaries_list.append([Coll1steel_RotX_start,Coll1steel_RotX_stop,Coll1steel_RotX_step])
#boundaries_name_list.append(['Coll1steel_RotX'])
#Coll1steel_RotY_start,Coll1steel_RotY_stop,Coll1steel_RotY_step = 0,0,0
#boundaries_list.append([Coll1steel_RotY_start,Coll1steel_RotY_stop,Coll1steel_RotY_step])
#boundaries_name_list.append(['Coll1steel_RotY'])
#Coll1steel_RotZ_start,Coll1steel_RotZ_stop,Coll1steel_RotZ_step = 0,0,0
#boundaries_list.append([Coll1steel_RotZ_start,Coll1steel_RotZ_stop,Coll1steel_RotZ_step])
#boundaries_name_list.append(['Coll1steel_RotZ'])
#Coll1steel_LZ_start,Coll1steel_LZ_stop,Coll1steel_LZ_step = 0,0,0
#boundaries_list.append([Coll1steel_LZ_start,Coll1steel_LZ_stop,Coll1steel_LZ_step])
#boundaries_name_list.append(['Coll1steel_LZ_start'])
#Coll1steel_LY_start,Coll1steel_LY_stop,Coll1steel_LY_step = 0,0,0
#boundaries_list.append([Coll1steel_LY_start,Coll1steel_LY_stop,Coll1steel_LY_step])
#boundaries_name_list.append(['Coll1steel_LY_start'])
#Coll1steel_LX_start,Coll1steel_LX_stop,Coll1steel_LX_step = 0,0,0
#oundaries_list.append([Coll1steel_LX_start,Coll1steel_LX_stop,Coll1steel_LX_step])
#boundaries_name_list.append(['Coll1steel_LX_start'])
#Coll1steel_LTX_start,Coll1steel_LTX_stop,Coll1steel_LTX_step = 0,0,0
#boundaries_list.append([Coll1steel_LTX_start,Coll1steel_LTX_stop,Coll1steel_LTX_step])
#boundaries_name_list.append(['Coll1steel_LTX_start'])

#Coll2steel_TransX_start,Coll2steel_TransX_stop,Coll2steel_TransX_step = 0,0,0
#boundaries_list.append([Coll2steel_TransX_start,Coll2steel_TransX_stop,Coll2steel_TransX_step])
#boundaries_name_list.append(['Coll2steel_TransX'])
#Coll2steel_TransY_start,Coll2steel_TransY_stop,Coll2steel_TransY_step = 0,0,0
#boundaries_list.append([Coll2steel_TransY_start,Coll2steel_TransY_stop,Coll2steel_TransY_step])
#boundaries_name_list.append(['Coll2steel_TransY'])
#Coll2steel_TransZ_start,Coll2steel_TransZ_stop,Coll2steel_TransZ_step = 0,0,0
#boundaries_list.append([Coll2steel_TransZ_start,Coll2steel_TransZ_stop,Coll2steel_TransZ_step])
#boundaries_name_list.append(['Coll2steel_TransZ'])
#Coll2steel_RotX_start,Coll2steel_RotX_stop,Coll2steel_RotX_step = 0,0,0
#boundaries_list.append([Coll2steel_RotX_start,Coll2steel_RotX_stop,Coll2steel_RotX_step])
#boundaries_name_list.append(['Coll2steel_RotX'])
#Coll2steel_RotY_start,Coll2steel_RotY_stop,Coll2steel_RotY_step = 0,0,0
#boundaries_list.append([Coll2steel_RotY_start,Coll2steel_RotY_stop,Coll2steel_RotY_step])
#boundaries_name_list.append(['Coll2steel_RotY'])
#Coll2steel_RotZ_start,Coll2steel_RotZ_stop,Coll2steel_RotZ_step = 0,0,0
#boundaries_list.append([Coll2steel_RotZ_start,Coll2steel_RotZ_stop,Coll2steel_RotZ_step])
#boundaries_name_list.append(['Coll2steel_RotZ'])
#Coll2steel_LZ_start,Coll2steel_LZ_stop,Coll2steel_LZ_step = 0,0,0
#boundaries_list.append([Coll2steel_LZ_start,Coll2steel_LZ_stop,Coll2steel_LZ_step])
#boundaries_name_list.append(['Coll2steel_LZ_start'])
#Coll2steel_LY_start,Coll2steel_LY_stop,Coll2steel_LY_step = 0,0,0
#boundaries_list.append([Coll2steel_LY_start,Coll2steel_LY_stop,Coll2steel_LY_step])
#boundaries_name_list.append(['Coll2steel_LY_start'])
#Coll2steel_LX_start,Coll2steel_LX_stop,Coll2steel_LX_step = 0,0,0
#boundaries_list.append([Coll2steel_LX_start,Coll2steel_LX_stop,Coll2steel_LX_step])
#boundaries_name_list.append(['Coll2steel_LX_start'])
#Coll2steel_LTX_start,Coll2steel_LTX_stop,Coll2steel_LTX_step = 0,0,0
#boundaries_list.append([Coll2steel_LTX_start,Coll2steel_LTX_stop,Coll2steel_LTX_step])
#boundaries_name_list.append(['Coll2steel_LTX_start'])

#Coll3steel_TransX_start,Coll3steel_TransX_stop,Coll3steel_TransX_step = 0,0,0
#boundaries_list.append([Coll3steel_TransX_start,Coll3steel_TransX_stop,Coll3steel_TransX_step])
#boundaries_name_list.append(['Coll3steel_TransX'])
#Coll3steel_TransY_start,Coll3steel_TransY_stop,Coll3steel_TransY_step = 0,0,0
#boundaries_list.append([Coll3steel_TransY_start,Coll3steel_TransY_stop,Coll3steel_TransY_step])
#boundaries_name_list.append(['Coll3steel_TransY'])
#Coll3steel_TransZ_start,Coll3steel_TransZ_stop,Coll3steel_TransZ_step = 0,0,0
#boundaries_list.append([Coll3steel_TransZ_start,Coll3steel_TransZ_stop,Coll3steel_TransZ_step])
#oundaries_name_list.append(['Coll3steel_TransZ'])
#Coll3steel_RotX_start,Coll3steel_RotX_stop,Coll3steel_RotX_step = 0,0,0
#boundaries_list.append([Coll3steel_RotX_start,Coll3steel_RotX_stop,Coll3steel_RotX_step])
#boundaries_name_list.append(['Coll3steel_RotX'])
#Coll3steel_RotY_start,Coll3steel_RotY_stop,Coll3steel_RotY_step = 0,0,0
#boundaries_list.append([Coll3steel_RotY_start,Coll3steel_RotY_stop,Coll3steel_RotY_step])
#boundaries_name_list.append(['Coll3steel_RotY'])
#Coll3steel_RotZ_start,Coll3steel_RotZ_stop,Coll3steel_RotZ_step = 0,0,0
#boundaries_list.append([Coll3steel_RotZ_start,Coll3steel_RotZ_stop,Coll3steel_RotZ_step])
#boundaries_name_list.append(['Coll3steel_RotZ'])
#Coll3steel_LZ_start,Coll3steel_LZ_stop,Coll3steel_LZ_step = 0,0,0
#boundaries_list.append([Coll3steel_LZ_start,Coll3steel_LZ_stop,Coll3steel_LZ_step])
#boundaries_name_list.append(['Coll3steel_LZ_start'])
#Coll3steel_LY_start,Coll3steel_LY_stop,Coll3steel_LY_step = 0,0,0
#oundaries_list.append([Coll3steel_LY_start,Coll3steel_LY_stop,Coll3steel_LY_step])
#boundaries_name_list.append(['Coll3steel_LY_start'])
#Coll3steel_LX_start,Coll3steel_LX_stop,Coll3steel_LX_step = 0,0,0
#boundaries_list.append([Coll3steel_LX_start,Coll3steel_LX_stop,Coll3steel_LX_step])
#boundaries_name_list.append(['Coll3steel_LX_start'])
#Coll3steel_LTX_start,Coll3steel_LTX_stop,Coll3steel_LTX_step = 0,0,0
#boundaries_list.append([Coll3steel_LTX_start,Coll3steel_LTX_stop,Coll3steel_LTX_step])
#boundaries_name_list.append(['Coll3steel_LTX_start'])

#Coll4steel_TransX_start,Coll4steel_TransX_stop,Coll4steel_TransX_step = 0,0,0
#boundaries_list.append([Coll4steel_TransX_start,Coll4steel_TransX_stop,Coll4steel_TransX_step])
#boundaries_name_list.append(['Coll4steel_TransX'])
#Coll4steel_TransY_start,Coll4steel_TransY_stop,Coll4steel_TransY_step = 0,0,0
#boundaries_list.append([Coll4steel_TransY_start,Coll4steel_TransY_stop,Coll4steel_TransY_step])
#boundaries_name_list.append(['Coll4steel_TransY'])
#Coll4steel_TransZ_start,Coll4steel_TransZ_stop,Coll4steel_TransZ_step = 0,0,0
#boundaries_list.append([Coll4steel_TransZ_start,Coll4steel_TransZ_stop,Coll4steel_TransZ_step])
#boundaries_name_list.append(['Coll4steel_TransZ'])
#Coll4steel_RotX_start,Coll4steel_RotX_stop,Coll4steel_RotX_step = 0,0,0
#boundaries_list.append([Coll4steel_RotX_start,Coll4steel_RotX_stop,Coll4steel_RotX_step])
#boundaries_name_list.append(['Coll4steel_RotX'])
#Coll4steel_RotY_start,Coll4steel_RotY_stop,Coll4steel_RotY_step = 0,0,0
#boundaries_list.append([Coll4steel_RotY_start,Coll4steel_RotY_stop,Coll4steel_RotY_step])
#boundaries_name_list.append(['Coll4steel_RotY'])
#Coll4steel_RotZ_start,Coll4steel_RotZ_stop,Coll4steel_RotZ_step = 0,0,0
#boundaries_list.append([Coll4steel_RotZ_start,Coll4steel_RotZ_stop,Coll4steel_RotZ_step])
#boundaries_name_list.append(['Coll4steel_RotZ'])
#Coll4steel_LZ_start,Coll4steel_LZ_stop,Coll4steel_LZ_step = 0,0,0
#boundaries_list.append([Coll4steel_LZ_start,Coll4steel_LZ_stop,Coll4steel_LZ_step])
#boundaries_name_list.append(['Coll4steel_LZ_start'])
#Coll4steel_LY_start,Coll4steel_LY_stop,Coll4steel_LY_step = 0,0,0
#boundaries_list.append([Coll4steel_LY_start,Coll4steel_LY_stop,Coll4steel_LY_step])
#boundaries_name_list.append(['Coll4steel_LY_start'])
#Coll4steel_LX_start,Coll4steel_LX_stop,Coll4steel_LX_step = 0,0,0
#boundaries_list.append([Coll4steel_LX_start,Coll4steel_LX_stop,Coll4steel_LX_step])
#boundaries_name_list.append(['Coll4steel_LX_start'])
#Coll4steel_LTX_start,Coll4steel_LTX_stop,Coll4steel_LTX_step = 0,0,0
#boundaries_list.append([Coll4steel_LTX_start,Coll4steel_LTX_stop,Coll4steel_LTX_step])
#boundaries_name_list.append(['Coll4steel_LTX_start'])

##TitaniumFilter
#TitaniumFilter_TransX_start,TitaniumFilter_TransX_stop,TitaniumFilter_TransX_step = 0,0,0
#boundaries_list.append([TitaniumFilter_TransX_start,TitaniumFilter_TransX_stop,TitaniumFilter_TransX_step])
#boundaries_name_list.append(['TitaniumFilter_TransX'])
#TitaniumFilter_TransY_start,TitaniumFilter_TransY_stop,TitaniumFilter_TransY_step = 0,0,0
#boundaries_list.append([TitaniumFilter_TransY_start,TitaniumFilter_TransY_stop,TitaniumFilter_TransY_step])
#boundaries_name_list.append(['TitaniumFilter_TransY'])
#TitaniumFilter_TransZ_start,TitaniumFilter_TransZ_stop,TitaniumFilter_TransZ_step = 0,0,0
#boundaries_list.append([TitaniumFilter_TransZ_start,TitaniumFilter_TransZ_stop,TitaniumFilter_TransZ_step])
#boundaries_name_list.append(['TitaniumFilter_TransZ'])
#TitaniumFilter_RotX_start,TitaniumFilter_RotX_stop,TitaniumFilter_RotX_step = 0,0,0
#boundaries_list.append([TitaniumFilter_RotX_start,TitaniumFilter_RotX_stop,TitaniumFilter_RotX_step])
#boundaries_name_list.append(['TitaniumFilter_RotX'])
#TitaniumFilter_RotY_start,TitaniumFilter_RotY_stop,TitaniumFilter_RotY_step = 0,0,0
#boundaries_list.append([TitaniumFilter_RotY_start,TitaniumFilter_RotY_stop,TitaniumFilter_RotY_step])
#boundaries_name_list.append(['TitaniumFilter_RotY'])
#TitaniumFilter_RotZ_start,TitaniumFilter_RotZ_stop,TitaniumFilter_RotZ_step = 0,0,0
#boundaries_list.append([TitaniumFilter_RotZ_start,TitaniumFilter_RotZ_stop,TitaniumFilter_RotZ_step])
#boundaries_name_list.append(['TitaniumFilter_RotZ'])
#TitaniumFilter_HLZ_start,TitaniumFilter_HLZ_stop,TitaniumFilter_HLZ_step = 0,0,0
#boundaries_list.append([TitaniumFilter_HLZ_start,TitaniumFilter_HLZ_stop,TitaniumFilter_HLZ_step])
#boundaries_name_list.append(['TitaniumFilter_HLZ'])
#TitaniumFilter_HLY_start,TitaniumFilter_HLY_stop,TitaniumFilter_HLY_step = 0,0,0
#boundaries_list.append([TitaniumFilter_HLY_start,TitaniumFilter_HLY_stop,TitaniumFilter_HLY_step])
#boundaries_name_list.append(['TitaniumFilter_HLY'])
#TitaniumFilter_HLX_start,TitaniumFilter_HLX_stop,TitaniumFilter_HLX_step = 0,0,0
#boundaries_list.append([TitaniumFilter_HLX_start,TitaniumFilter_HLX_stop,TitaniumFilter_HLX_step])
#boundaries_name_list.append(['TitaniumFilter_HLX'])

##DemoFlat
#DemoFlat_TransX_start,DemoFlat_TransX_stop,DemoFlat_TransX_step = 0,0,0
#boundaries_list.append([DemoFlat_TransX_start,DemoFlat_TransX_stop,DemoFlat_TransX_step])
#boundaries_name_list.append(['DemoFlat_TransX'])
#DemoFlat_TransY_start,DemoFlat_TransY_stop,DemoFlat_TransY_step = 0,0,0
#boundaries_list.append([DemoFlat_TransY_start,DemoFlat_TransY_stop,DemoFlat_TransY_step])
#boundaries_name_list.append(['DemoFlat_TransY'])
#DemoFlat_TransZ_start,DemoFlat_TransZ_stop,DemoFlat_TransZ_step = 0,0,0
#boundaries_list.append([DemoFlat_TransZ_start,DemoFlat_TransZ_stop,DemoFlat_TransZ_step])
#boundaries_name_list.append(['DemoFlat_TransZ'])
#DemoFlat_RotX_start,DemoFlat_RotX_stop,DemoFlat_RotX_step = 0,0,0
#boundaries_list.append([DemoFlat_RotX_start,DemoFlat_RotX_stop,DemoFlat_RotX_step])
#boundaries_name_list.append(['DemoFlat_RotX'])
#DemoFlat_RotY_start,DemoFlat_RotY_stop,DemoFlat_RotY_step = 0,0,0
#boundaries_list.append([DemoFlat_RotY_start,DemoFlat_RotY_stop,DemoFlat_RotY_step])
#boundaries_name_list.append(['DemoFlat_RotY'])
#DemoFlat_RotZ_start,DemoFlat_RotZ_stop,DemoFlat_RotZ_step = 0,0,0
#boundaries_list.append([DemoFlat_RotZ_start,DemoFlat_RotZ_stop,DemoFlat_RotZ_step])
#boundaries_name_list.append(['DemoFlat_RotZ'])
#DemoFlat_HLZ_start,DemoFlat_HLZ_stop,DemoFlat_HLZ_step = 0,0,0
#boundaries_list.append([DemoFlat_HLZ_start,DemoFlat_HLZ_stop,DemoFlat_HLZ_step])
#boundaries_name_list.append(['DemoFlat_HLZ'])
#DemoFlat_HLY_start,DemoFlat_HLY_stop,DemoFlat_HLY_step = 0,0,0
#boundaries_list.append([DemoFlat_HLY_start,DemoFlat_HLY_stop,DemoFlat_HLY_step])
#boundaries_name_list.append(['DemoFlat_HLY'])
#DemoFlat_HLX_start,DemoFlat_HLX_stop,DemoFlat_HLX_step = 0,0,0
#boundaries_list.append([DemoFlat_HLX_start,DemoFlat_HLX_stop,DemoFlat_HLX_step])
#boundaries_name_list.append(['DemoFlat_HLX'])

##DemoRTrap
#DemoRTrap_TransX_start,DemoRTrap_TransX_stop,DemoRTrap_TransX_step = 0,0,0
#boundaries_list.append([DemoRTrap_TransX_start,DemoRTrap_TransX_stop,DemoRTrap_TransX_step])
#boundaries_name_list.append(['DemoRTrap_TransX'])
#DemoRTrap_TransY_start,DemoRTrap_TransY_stop,DemoRTrap_TransY_step = 0,0,0
#boundaries_list.append([DemoRTrap_TransY_start,DemoRTrap_TransY_stop,DemoRTrap_TransY_step])
#boundaries_name_list.append(['DemoRTrap_TransY'])
#DemoRTrap_TransZ_start,DemoRTrap_TransZ_stop,DemoRTrap_TransZ_step = 0,0,0
#boundaries_list.append([DemoRTrap_TransZ_start,DemoRTrap_TransZ_stop,DemoRTrap_TransZ_step])
#boundaries_name_list.append(['DemoRTrap_TransZ'])
#DemoRTrap_RotX_start,DemoRTrap_RotX_stop,DemoRTrap_RotX_step = 0,0,0
#boundaries_list.append([DemoRTrap_RotX_start,DemoRTrap_RotX_stop,DemoRTrap_RotX_step])
#boundaries_name_list.append(['DemoRTrap_RotX'])
#DemoRTrap_RotY_start,DemoRTrap_RotY_stop,DemoRTrap_RotY_step = 0,0,0
#boundaries_list.append([DemoRTrap_RotY_start,DemoRTrap_RotY_stop,DemoRTrap_RotY_step])
#boundaries_name_list.append(['DemoRTrap_RotY'])
#DemoRTrap_RotZ_start,DemoRTrap_RotZ_stop,DemoRTrap_RotZ_step = 0,0,0
#boundaries_list.append([DemoRTrap_RotZ_start,DemoRTrap_RotZ_stop,DemoRTrap_RotZ_step])
#boundaries_name_list.append(['DemoRTrap_RotZ'])
#DemoRTrap_LZ_start,DemoRTrap_LZ_stop,DemoRTrap_LZ_step = 0,0,0
#boundaries_list.append([DemoRTrap_LZ_start,DemoRTrap_LZ_stop,DemoRTrap_LZ_step])
#boundaries_name_list.append(['DemoRTrap_LZ'])
#DemoRTrap_LY_start,DemoRTrap_LY_stop,DemoRTrap_LY_step = 0,0,0
#boundaries_list.append([DemoRTrap_LY_start,DemoRTrap_LY_stop,DemoRTrap_LY_step])
#boundaries_name_list.append(['DemoRTrap_LY'])
#DemoRTrap_LX_start,DemoRTrap_LX_stop,DemoRTrap_LX_step = 0,0,0
#boundaries_list.append([DemoRTrap_LX_start,DemoRTrap_LX_stop,DemoRTrap_LX_step])
#boundaries_name_list.append(['DemoRTrap_LX'])
#DemoRTrap_LTX_start,DemoRTrap_LTX_stop,DemoRTrap_LTX_step = 0,0,0
#boundaries_list.append([DemoRTrap_LTX_start,DemoRTrap_LTX_stop,DemoRTrap_LTX_step])
#boundaries_name_list.append(['DemoRTrap_LTX'])

##DemoLTrap
#DemoLTrap_TransX_start,DemoLTrap_TransX_stop,DemoLTrap_TransX_step = 0,0,0
#boundaries_list.append([DemoLTrap_TransX_start,DemoLTrap_TransX_stop,DemoLTrap_TransX_step])
#boundaries_name_list.append(['DemoLTrap_TransX'])
#DemoLTrap_TransY_start,DemoLTrap_TransY_stop,DemoLTrap_TransY_step = 0,0,0
#boundaries_list.append([DemoLTrap_TransY_start,DemoLTrap_TransY_stop,DemoLTrap_TransY_step])
#boundaries_name_list.append(['DemoLTrap_TransY'])
#DemoLTrap_TransZ_start,DemoLTrap_TransZ_stop,DemoLTrap_TransZ_step = 0,0,0
#boundaries_list.append([DemoLTrap_TransZ_start,DemoLTrap_TransZ_stop,DemoLTrap_TransZ_step])
#boundaries_name_list.append(['DemoLTrap_TransZ'])
#DemoLTrap_RotX_start,DemoLTrap_RotX_stop,DemoLTrap_RotX_step = 0,0,0
#boundaries_list.append([DemoLTrap_RotX_start,DemoLTrap_RotX_stop,DemoLTrap_RotX_step])
#boundaries_name_list.append(['DemoLTrap_RotX'])
#DemoLTrap_RotY_start,DemoLTrap_RotY_stop,DemoLTrap_RotY_step = 0,0,0
#boundaries_list.append([DemoLTrap_RotY_start,DemoLTrap_RotY_stop,DemoLTrap_RotY_step])
#boundaries_name_list.append(['DemoLTrap_RotY'])
#DemoLTrap_RotZ_start,DemoLTrap_RotZ_stop,DemoLTrap_RotZ_step = 0,0,0
#boundaries_list.append([DemoLTrap_RotZ_start,DemoLTrap_RotZ_stop,DemoLTrap_RotZ_step])
#boundaries_name_list.append(['DemoLTrap_RotZ'])
#DemoLTrap_LZ_start,DemoLTrap_LZ_stop,DemoLTrap_LZ_step = 0,0,0
#boundaries_list.append([DemoLTrap_LZ_start,DemoLTrap_LZ_stop,DemoLTrap_LZ_step])
#boundaries_name_list.append(['DemoLTrap_LZ'])
#DemoLTrap_LY_start,DemoLTrap_LY_stop,DemoLTrap_LY_step = 0,0,0
#boundaries_list.append([DemoLTrap_LY_start,DemoLTrap_LY_stop,DemoLTrap_LY_step])
#boundaries_name_list.append(['DemoLTrap_LY'])
#DemoLTrap_LX_start,DemoLTrap_LX_stop,DemoLTrap_LX_step = 0,0,0
#boundaries_list.append([DemoLTrap_LX_start,DemoLTrap_LX_stop,DemoLTrap_LX_step])
#boundaries_name_list.append(['DemoLTrap_LX'])
#DemoLTrap_LTX_start,DemoLTrap_LTX_stop,DemoLTrap_LTX_step = 0,0,0
#boundaries_list.append([DemoLTrap_LTX_start,DemoLTrap_LTX_stop,DemoLTrap_LTX_step])
#boundaries_name_list.append(['DemoLTrap_LTX'])

#topsidebox_TransX_start,topsidebox_TransX_stop,topsidebox_TransX_step = 0,0,0
#boundaries_list.append([topsidebox_TransX_start,topsidebox_TransX_stop,topsidebox_TransX_step])
#boundaries_name_list.append(['topsidebox_TransX'])
#topsidebox_TransY_start,topsidebox_TransY_stop,topsidebox_TransY_step = 0,0,0
#boundaries_list.append([topsidebox_TransY_start,topsidebox_TransY_stop,topsidebox_TransY_step])
#boundaries_name_list.append(['topsidebox_TransY'])
#topsidebox_TransZ_start,topsidebox_TransZ_stop,topsidebox_TransZ_step = 0,0,0
#boundaries_list.append([topsidebox_TransZ_start,topsidebox_TransZ_stop,topsidebox_TransZ_step])
#boundaries_name_list.append(['topsidebox_TransZ'])
#topsidebox_RotX_start,topsidebox_RotX_stop,topsidebox_RotX_step = 0,0,0
#boundaries_list.append([topsidebox_RotX_start,topsidebox_RotX_stop,topsidebox_RotX_step])
#boundaries_name_list.append(['topsidebox_RotX'])
#topsidebox_RotY_start,topsidebox_RotY_stop,topsidebox_RotY_step = 0,0,0
#boundaries_list.append([topsidebox_RotY_start,topsidebox_RotY_stop,topsidebox_RotY_step])
#boundaries_name_list.append(['topsidebox_RotY'])
#topsidebox_RotZ_start,topsidebox_RotZ_stop,topsidebox_RotZ_step = 0,0,0
#boundaries_list.append([topsidebox_RotZ_start,topsidebox_RotZ_stop,topsidebox_RotZ_step])
#boundaries_name_list.append(['topsidebox_RotZ'])
#topsidebox_HLZ_start,topsidebox_HLZ_stop,topsidebox_HLZ_step = 0,0,0
#boundaries_list.append([topsidebox_HLZ_start,topsidebox_HLZ_stop,topsidebox_HLZ_step])
#boundaries_name_list.append(['topsidebox_HLZ'])
#topsidebox_HLY_start,topsidebox_HLY_stop,topsidebox_HLY_step = 0,0,0
#boundaries_list.append([topsidebox_HLY_start,topsidebox_HLY_stop,topsidebox_HLY_step])
#boundaries_name_list.append(['topsidebox_HLY'])
#topsidebox_HLX_start,topsidebox_HLX_stop,topsidebox_HLX_step = 0,0,0
#boundaries_list.append([topsidebox_HLX_start,topsidebox_HLX_stop,topsidebox_HLX_step])
#boundaries_name_list.append(['topsidebox_HLX'])

##bottomsidebox
#bottomsidebox_TransX_start,bottomsidebox_TransX_stop,bottomsidebox_TransX_step = 0,0,0
#boundaries_list.append([bottomsidebox_TransX_start,bottomsidebox_TransX_stop,bottomsidebox_TransX_step])
#boundaries_name_list.append(['bottomsidebox_TransX'])
#bottomsidebox_TransY_start,bottomsidebox_TransY_stop,bottomsidebox_TransY_step = 0,0,0
#boundaries_list.append([bottomsidebox_TransY_start,bottomsidebox_TransY_stop,bottomsidebox_TransY_step])
#boundaries_name_list.append(['bottomsidebox_TransY'])
#bottomsidebox_TransZ_start,bottomsidebox_TransZ_stop,bottomsidebox_TransZ_step = 0,0,0
#boundaries_list.append([bottomsidebox_TransZ_start,bottomsidebox_TransZ_stop,bottomsidebox_TransZ_step])
#boundaries_name_list.append(['bottomsidebox_TransZ'])
#bottomsidebox_RotX_start,bottomsidebox_RotX_stop,bottomsidebox_RotX_step = 0,0,0
#boundaries_list.append([bottomsidebox_RotX_start,bottomsidebox_RotX_stop,bottomsidebox_RotX_step])
#boundaries_name_list.append(['bottomsidebox_RotX'])
#bottomsidebox_RotY_start,bottomsidebox_RotY_stop,bottomsidebox_RotY_step = 0,0,0
#boundaries_list.append([bottomsidebox_RotY_start,bottomsidebox_RotY_stop,bottomsidebox_RotY_step])
#boundaries_name_list.append(['bottomsidebox_RotY'])
#bottomsidebox_RotZ_start,bottomsidebox_RotZ_stop,bottomsidebox_RotZ_step = 0,0,0
#boundaries_list.append([bottomsidebox_RotZ_start,bottomsidebox_RotZ_stop,bottomsidebox_RotZ_step])
#boundaries_name_list.append(['bottomsidebox_RotZ'])
#bottomsidebox_HLZ_start,bottomsidebox_HLZ_stop,bottomsidebox_HLZ_step = 0,0,0
#boundaries_list.append([bottomsidebox_HLZ_start,bottomsidebox_HLZ_stop,bottomsidebox_HLZ_step])
#boundaries_name_list.append(['bottomsidebox_HLZ'])
#bottomsidebox_HLY_start,bottomsidebox_HLY_stop,bottomsidebox_HLY_step = 0,0,0
#boundaries_list.append([bottomsidebox_HLY_start,bottomsidebox_HLY_stop,bottomsidebox_HLY_step])
#boundaries_name_list.append(['bottomsidebox_HLY'])
#bottomsidebox_HLX_start,bottomsidebox_HLX_stop,bottomsidebox_HLX_step = 0,0,0
#boundaries_list.append([bottomsidebox_HLX_start,bottomsidebox_HLX_stop,bottomsidebox_HLX_step])
#boundaries_name_list.append(['bottomsidebox_HLX'])

##couch
#couch_TransX_start,couch_TransX_stop,couch_TransX_step = 0,0,0
#boundaries_list.append([couch_TransX_start,couch_TransX_stop,couch_TransX_step])
#boundaries_name_list.append(['couch_TransX'])
#couch_TransY_start,couch_TransY_stop,couch_TransY_step = 0,0,0
#boundaries_list.append([couch_TransY_start,couch_TransY_stop,couch_TransY_step])
#boundaries_name_list.append(['couch_TransY'])
#couch_TransZ_start,couch_TransZ_stop,couch_TransZ_step = 0,0,0
#boundaries_list.append([couch_TransZ_start,couch_TransZ_stop,couch_TransZ_step])
#boundaries_name_list.append(['couch_TransZ'])
#couch_HLZ_start,couch_HLZ_stop,couch_HLZ_step = 0,0,0
#boundaries_list.append([couch_HLZ_start,couch_HLZ_stop,couch_HLZ_step])
#boundaries_name_list.append(['couch_HLZ'])
#couch_HLY_start,couch_HLY_stop,couch_HLY_step = 0,0,0
#boundaries_list.append([couch_HLY_start,couch_HLY_stop,couch_HLY_step])
#boundaries_name_list.append(['couch_HLY'])
#couch_HLX_start,couch_HLX_stop,couch_HLX_step = 0,0,0
#boundaries_list.append([couch_HLX_start,couch_HLX_stop,couch_HLX_step])
#boundaries_name_list.append(['couch_HLX'])

#BeamPosition_TransX_start,BeamPosition_TransX_stop,BeamPosition_TransX_step = 0,0,0
#boundaries_list.append([BeamPosition_TransX_start,BeamPosition_TransX_stop,BeamPosition_TransX_step])
#boundaries_name_list.append(['BeamPosition_TransX'])
#BeamPosition_TransY_start,BeamPosition_TransY_stop,BeamPosition_TransY_step = 0,0,0
#boundaries_list.append([BeamPosition_TransY_start,BeamPosition_TransY_stop,BeamPosition_TransY_step])
#boundaries_name_list.append(['BeamPosition_TransY'])
#BeamPosition_TransZ_start,BeamPosition_TransZ_stop,BeamPosition_TransZ_step = 0,0,0
#boundaries_list.append([BeamPosition_TransZ_start,BeamPosition_TransZ_stop,BeamPosition_TransZ_step])
#boundaries_name_list.append(['BeamPosition_TransZ'])
#BeamPosition_RotZ_start,BeamPosition_RotZ_stop,BeamPosition_RotZ_step = 0,0,0
#boundaries_list.append([BeamPosition_RotZ_start,BeamPosition_RotZ_stop,BeamPosition_RotZ_step])
#boundaries_name_list.append(['BeamPosition_RotZ'])
#BeamPosition_RotY_start,BeamPosition_RotY_stop,BeamPosition_RotY_step = 0,0,0
#boundaries_list.append([BeamPosition_RotY_start,BeamPosition_RotY_stop,BeamPosition_RotY_step])
#boundaries_name_list.append(['BeamPosition_RotY'])
#BeamPosition_RotX_start,BeamPosition_RotX_stop,BeamPosition_RotX_step = 0,0,0
#boundaries_list.append([BeamPosition_RotX_start,BeamPosition_RotX_stop,BeamPosition_RotX_step])
#boundaries_name_list.append(['BeamPosition_RotX'])

##beam
#beam_BeamPositionCutoffX_start,beam_BeamPositionCutoffX_stop,beam_BeamPositionCutoffX_step = 0,0,0
#boundaries_list.append([beam_BeamPositionCutoffX_start,beam_BeamPositionCutoffX_stop,beam_BeamPositionCutoffX_step])
#boundaries_name_list.append(['beam_BeamPositionCutoffX'])
#beam_BeamPositionCutoffY_start,beam_BeamPositionCutoffY_stop,beam_BeamPositionCutoffY_step = 0,0,0
#boundaries_list.append([beam_BeamPositionCutoffY_start,beam_BeamPositionCutoffY_stop,beam_BeamPositionCutoffY_step])
#boundaries_name_list.append(['beam_BeamPositionCutoffY'])
#beam_BeamPositionSpreadX_start,beam_BeamPositionSpreadX_stop,beam_BeamPositionSpreadX_step = 0,0,0
#boundaries_list.append([beam_BeamPositionSpreadX_start,beam_BeamPositionSpreadX_stop,beam_BeamPositionSpreadX_step])
#boundaries_name_list.append(['beam_BeamPositionSpreadX'])
#beam_BeamPositionSpreadY_start,beam_BeamPositionSpreadY_stop,beam_BeamPositionSpreadY_step = 0,0,0
#boundaries_list.append([beam_BeamPositionSpreadY_start,beam_BeamPositionSpreadY_stop,beam_BeamPositionSpreadY_step])
#boundaries_name_list.append(['beam_BeamPositionSpreadY'])
#beam_BeamAngularCutoffX_start,beam_BeamAngularCutoffX_stop,beam_BeamAngularCutoffX_step = 0,0,0
#boundaries_list.append([beam_BeamAngularCutoffX_start,beam_BeamAngularCutoffX_stop,beam_BeamAngularCutoffX_step])
#boundaries_name_list.append(['beam_BeamAngularCutoffX'])
#beam_BeamAngularCutoffY_start,beam_BeamAngularCutoffY_stop,beam_BeamAngularCutoffY_step = 0,0,0
#boundaries_list.append([beam_BeamAngularCutoffY_start,beam_BeamAngularCutoffY_stop,beam_BeamAngularCutoffY_step])
#boundaries_name_list.append(['beam_BeamAngularCutoffY'])
#beam_BeamAngularSpreadX_start,beam_BeamAngularSpreadX_stop,beam_BeamAngularSpreadX_step = 0,0,0
#boundaries_list.append([beam_BeamAngularSpreadX_start,beam_BeamAngularSpreadX_stop,beam_BeamAngularSpreadX_step])
#boundaries_name_list.append(['beam_BeamAngularSpreadX'])
#beam_BeamAngularSpreadY_start,beam_BeamAngularSpreadY_stop,beam_BeamAngularSpreadY_step = 0,0,0
#boundaries_list.append([beam_BeamAngularSpreadY_start,beam_BeamAngularSpreadY_stop,beam_BeamAngularSpreadY_step])
#boundaries_name_list.append(['beam_BeamAngularSpreadY'])

#NumberOfSequentialTimes_start,NumberOfSequentialTimes_stop,NumberOfSequentialTimes_step = 0,0,0
#boundaries_list.append([NumberOfSequentialTimes_start,NumberOfSequentialTimes_stop,NumberOfSequentialTimes_step])
#boundaries_name_list.append(['NumberOfSequentialTimes'])
#TimelineEnd_start,TimelineEnd_stop,TimelineEnd_step = 0,0,0
#boundaries_list.append([TimelineEnd_start,TimelineEnd_stop,TimelineEnd_step])
#boundaries_name_list.append(['TimelineEnd'])
#Rotate_rate_start,Rotate_rate_stop,Rotate_rate_step = 0,0,0
#boundaries_list.append([Rotate_rate_start,Rotate_rate_stop,Rotate_rate_step])
#boundaries_name_list.append(['Rotate_rate'])
#Rotate_StartValue_start,Rotate_StartValue_stop,Rotate_StartValue_step = 0,0,0
#boundaries_list.append([Rotate_StartValue_start,Rotate_StartValue_stop,Rotate_StartValue_step])
#boundaries_name_list.append(['Rotate_StartValue'])
#ShowHistoryCountAtInterval_start,ShowHistoryCountAtInterval_stop,ShowHistoryCountAtInterval_step = 0,0,0
#boundaries_list.append([ShowHistoryCountAtInterval_start,ShowHistoryCountAtInterval_stop,ShowHistoryCountAtInterval_step])
#boundaries_name_list.append(['ShowHistoryCountAtInterval'])

#at the end we need a nested list to be used in the second for loop below to create names of files
boundaries_name_list = [boundaries_name_list]

if __name__ == '__main__':

    air = '"Air"'
    pmma = '"PMMA"'
    protocolnames = ["Top","Centre", "Bottom", "Left", "Right"]

    def my_arange(start, end, step):
        return np.linspace(start, end, num=round((end-start)/step), endpoint=False)

    for names in protocolnames:
        #this block of code was hashed because we are already giving the user the option to change material above
        #all pmma by default
        chamberplugmaterial = 'ChamberPlug'+names+'_Material'
        #assign all chamberplugmaterial to air?
        globals()[chamberplugmaterial] = air

    #current task: to create a range input variable into generate_all_proc such that when user enters a range (instead of a single value)
    #it creates additional loop (containing all permutations) for the simulation to run in each loop



    #if gui input is a range, create a new variable containing that range like param_range below
    #instead of it being an actual list, create a lower limit, upper limit and step size instead
    #create another list containing the corresponding names of each element
    #centre

        if len(boundaries_list) != 0: 
            for component_name, values in zip(boundaries_name_list*len([*product(*(my_arange(*b) for b in boundaries_list))]),product(*(my_arange(*b) for b in boundaries_list))):

                #unhash the code below when name is mentioned 
                #problem now is that if we search line by line, there will be 2 lines containing CollimatorsVertical_TransZ
                #unless i put the ' = values[0]' too hmmmm
                #now problem is that even if we unhash, the indexing values will not be according to their position in the values tuple
                #because if some values were not touched in the middle like 'ChamberPlugCentre_HL', then the order would be wrong
                #how do we solve this?
                #CollimatorsVertical_TransZ=values[0]
                i = 0
                #Seed,i=str(int(values[i])),i+1
                #NumberOfThreads,i=str(int(values[i])),i+1
                #beam_NumberOfHistoriesInRun,i=str(int(values[i])),i+1

                #CTDI_RMin,i=str(values[i]),i+1
                #CTDI_RMax,i=str(values[i]),i+1
                #CTDI_HL,i=str(values[i]),i+1
                #CTDI_SPhi,i=str(values[i]),i+1
                #CTDI_DPhi,i=str(values[i]),i+1
                #CTDI_TransX,i=str(values[i]),i+1
                #CTDI_TransY,i=str(values[i]),i+1
                #CTDI_TransZ,i=str(values[i]),i+1
                #CTDI_RotX,i=str(values[i]),i+1

                #ChamberPlugCentre_RMin,i=str(values[i]),i+1
                #ChamberPlugCentre_RMax,i=str(values[i]),i+1
                #ChamberPlugCentre_HL,i=str(values[i]),i+1
                #ChamberPlugCentre_SPhi,i=str(values[i]),i+1
                #ChamberPlugCentre_DPhi,i=str(values[i]),i+1
                #ChamberPlugCentre_TransX,i=str(values[i]),i+1
                #ChamberPlugCentre_TransY,i=str(values[i]),i+1
                #ChamberPlugCentre_TransZ,i=str(values[i]),i+1
                #ChamberPlugCentre_RotX,i=str(values[i]),i+1

                #ChamberPlugTop_RMin,i=str(values[i]),i+1
                #ChamberPlugTop_RMax,i=str(values[i]),i+1
                #ChamberPlugTop_HL,i=str(values[i]),i+1
                #ChamberPlugTop_SPhi,i=str(values[i]),i+1
                #ChamberPlugTop_DPhi,i=str(values[i]),i+1
                #ChamberPlugTop_TransX,i=str(values[i]),i+1
                #ChamberPlugTop_TransY,i=str(values[i]),i+1
                #ChamberPlugTop_TransZ,i=str(values[i]),i+1
                #ChamberPlugTop_RotX,i=str(values[i]),i+1

                #ChamberPlugBottom_RMin,i=str(values[i]),i+1
                #ChamberPlugBottom_RMax,i=str(values[i]),i+1
                #ChamberPlugBottom_HL,i=str(values[i]),i+1
                #ChamberPlugBottom_SPhi,i=str(values[i]),i+1
                #ChamberPlugBottom_DPhi,i=str(values[i]),i+1
                #ChamberPlugBottom_TransX,i=str(values[i]),i+1
                #ChamberPlugBottom_TransY,i=str(values[i]),i+1
                #ChamberPlugBottom_TransZ,i=str(values[i]),i+1
                #ChamberPlugBottom_RotX,i=str(values[i]),i+1

                #ChamberPlugLeft_RMin,i=str(values[i]),i+1
                #ChamberPlugLeft_RMax,i=str(values[i]),i+1
                #ChamberPlugLeft_HL,i=str(values[i]),i+1
                #ChamberPlugLeft_SPhi,i=str(values[i]),i+1
                #ChamberPlugLeft_DPhi,i=str(values[i]),i+1
                #ChamberPlugLeft_TransX,i=str(values[i]),i+1
                #ChamberPlugLeft_TransY,i=str(values[i]),i+1
                #ChamberPlugLeft_TransZ,i=str(values[i]),i+1
                #ChamberPlugLeft_RotX,i=str(values[i]),i+1

                #ChamberPlugRight_RMin,i=str(values[i]),i+1
                #ChamberPlugRight_RMax,i=str(values[i]),i+1
                #ChamberPlugRight_HL,i=str(values[i]),i+1
                #ChamberPlugRight_SPhi,i=str(values[i]),i+1
                #ChamberPlugRight_DPhi,i=str(values[i]),i+1
                #ChamberPlugRight_TransX,i=str(values[i]),i+1
                #ChamberPlugRight_TransY,i=str(values[i]),i+1
                #ChamberPlugRight_TransZ,i=str(values[i]),i+1
                #ChamberPlugRight_RotX,i=str(values[i]),i+1

                #ChamberPlugDose_tle_Zbins,i=str(int(values[i])),i+1
                #ChamberPlugDose_dtm_Zbins,i=str(int(values[i])),i+1
                #ChamberPlugDose_dtw_Zbins,i=str(int(values[i])),i+1
                #ChamberPlugDose_dtmd_Zbins,i=str(int(values[i])),i+1
                #Ph_Default_EMRangeMin,i=str(values[i]),i+1
                #Ph_Default_EMRangeMax,i=str(values[i]),i+1

                #Rotation_RotX,i=str(values[i]),i+1
                #Rotation_RotY,i=str(values[i]),i+1
                #Rotation_RotZ,i=str(values[i]),i+1
                #Rotation_TransX,i=str(values[i]),i+1
                #Rotation_TransY,i=str(values[i]),i+1
                #Rotation_TransZ,i=str(values[i]),i+1

                #CollimatorsVertical_RotX,i=str(values[i]),i+1
                #CollimatorsVertical_RotY,i=str(values[i]),i+1
                #CollimatorsVertical_RotZ,i=str(values[i]),i+1
                #CollimatorsVertical_TransZ,i=str(values[i]),i+1
                #CollimatorsHorizontal_RotX,i=str(values[i]),i+1
                #CollimatorsHorizontal_RotY,i=str(values[i]),i+1
                #CollimatorsHorizontal_RotZ,i=str(values[i]),i+1
                #CollimatorsHorizontal_TransZ,i=str(values[i]),i+1

                #SteelFilterGroup_RotX,i=str(values[i]),i+1
                #SteelFilterGroup_RotY,i=str(values[i]),i+1
                #SteelFilterGroup_RotZ,i=str(values[i]),i+1
                #SteelFilterGroup_TransZ,i=str(values[i]),i+1

                #BowtieFilter_RotX,i=str(values[i]),i+1
                #BowtieFilter_RotY,i=str(values[i]),i+1
                #BowtieFilter_RotZ,i=str(values[i]),i+1
                #BowtieFilter_TransX,i=str(values[i]),i+1
                #BowtieFilter_TransY,i=str(values[i]),i+1
                #BowtieFilter_TransZ,i=str(values[i]),i+1

                #Coll1_TransX,i=str(values[i]),i+1
                #Coll1_TransY,i=str(values[i]),i+1
                #Coll1_TransZ,i=str(values[i]),i+1
                #Coll1_RotX,i=str(values[i]),i+1
                #Coll1_RotY,i=str(values[i]),i+1
                #Coll1_RotZ,i=str(values[i]),i+1
                #Coll1_LZ,i=str(values[i]),i+1
                #Coll1_LY,i=str(values[i]),i+1
                #Coll1_LX,i=str(values[i]),i+1
                #Coll1_LTX,i=str(values[i]),i+1

                #Coll2_TransX,i=str(values[i]),i+1
                #Coll2_TransY,i=str(values[i]),i+1
                #Coll2_TransZ,i=str(values[i]),i+1
                #Coll2_RotX,i=str(values[i]),i+1
                #Coll2_RotY,i=str(values[i]),i+1
                #Coll2_RotZ,i=str(values[i]),i+1
                #Coll2_LZ,i=str(values[i]),i+1
                #Coll2_LY,i=str(values[i]),i+1
                #Coll2_LX,i=str(values[i]),i+1
                #Coll2_LTX,i=str(values[i]),i+1

                #Coll3_TransX,i=str(values[i]),i+1
                #Coll3_TransY,i=str(values[i]),i+1
                #Coll3_TransZ,i=str(values[i]),i+1
                #Coll3_RotX,i=str(values[i]),i+1
                #Coll3_RotY,i=str(values[i]),i+1
                #Coll3_RotZ,i=str(values[i]),i+1
                #Coll3_LZv,i=str(values[i]),i+1
                #Coll3_LY,i=str(values[i]),i+1
                #Coll3_LX,i=str(values[i]),i+1
                #Coll3_LTX,i=str(values[i]),i+1

                #Coll4_TransX,i=str(values[i]),i+1
                #Coll4_TransY,i=str(values[i]),i+1
                #Coll4_TransZv,i=str(values[i]),i+1
                #Coll4_RotX,i=str(values[i]),i+1
                #Coll4_RotY,i=str(values[i]),i+1
                #Coll4_RotZ,i=str(values[i]),i+1
                #Coll4_LZ,i=str(values[i]),i+1
                #Coll4_LY,i=str(values[i]),i+1
                #Coll4_LX,i=str(values[i]),i+1
                #Coll4_LTX,i=str(values[i]),i+1

                #Coll1steel_TransX,i=str(values[i]),i+1
                #Coll1steel_TransY,i=str(values[i]),i+1
                #Coll1steel_TransZ,i=str(values[i]),i+1
                #Coll1steel_RotX,i=str(values[i]),i+1
                #Coll1steel_RotY,i=str(values[i]),i+1
                #Coll1steel_RotZ,i=str(values[i]),i+1
                #Coll1steel_LZ,i=str(values[i]),i+1
                #Coll1steel_LY,i=str(values[i]),i+1
                #Coll1steel_LX,i=str(values[i]),i+1
                #Coll1steel_LTX,i=str(values[i]),i+1

                #Coll2steel_TransX,i=str(values[i]),i+1
                #Coll2steel_TransY,i=str(values[i]),i+1
                #Coll2steel_TransZ,i=str(values[i]),i+1
                #Coll2steel_RotX,i=str(values[i]),i+1
                #Coll2steel_RotY,i=str(values[i]),i+1
                #Coll2steel_RotZ,i=str(values[i]),i+1
                #Coll2steel_LZ,i=str(values[i]),i+1
                #Coll2steel_LY,i=str(values[i]),i+1
                #Coll2steel_LX,i=str(values[i]),i+1
                #Coll2steel_LTX,i=str(values[i]),i+1

                #Coll3steel_TransX,i=str(values[i]),i+1
                #Coll3steel_TransY,i=str(values[i]),i+1
                #Coll3steel_TransZ,i=str(values[i]),i+1
                #Coll3steel_RotX,i=str(values[i]),i+1
                #Coll3steel_RotY,i=str(values[i]),i+1
                #Coll3steel_RotZ,i=str(values[i]),i+1
                #Coll3steel_LZ,i=str(values[i]),i+1
                #Coll3steel_LY,i=str(values[i]),i+1
                #Coll3steel_LX,i=str(values[i]),i+1
                #Coll3steel_LTX,i=str(values[i]),i+1

                #Coll4steel_TransX,i=str(values[i]),i+1
                #Coll4steel_TransY,i=str(values[i]),i+1
                #Coll4steel_TransZ,i=str(values[i]),i+1
                #Coll4steel_RotX,i=str(values[i]),i+1
                #Coll4steel_RotY,i=str(values[i]),i+1
                #Coll4steel_RotZ,i=str(values[i]),i+1
                #Coll4steel_LZ,i=str(values[i]),i+1
                #Coll4steel_LY,i=str(values[i]),i+1
                #Coll4steel_LX,i=str(values[i]),i+1
                #Coll4steel_LTX,i=str(values[i]),i+1

                #TitaniumFilter_TransX,i=str(values[in]),i+1
                #TitaniumFilter_TransY,i=str(values[i]),i+1
                #TitaniumFilter_TransZ,i=str(values[i]),i+1
                #TitaniumFilter_RotX,i=str(values[i]),i+1
                #TitaniumFilter_RotY,i=str(values[i]),i+1
                #TitaniumFilter_RotZ,i=str(values[i]),i+1
                #TitaniumFilter_HLZ,i=str(values[i]),i+1
                #TitaniumFilter_HLY,i=str(values[i]),i+1
                #TitaniumFilter_HLX,i=str(values[i]),i+1

                #DemoFlat_TransX,i=str(values[i]),i+1
                #DemoFlat_TransY,i=str(values[i]),i+1
                #DemoFlat_TransZ,i=str(values[i]),i+1
                #DemoFlat_RotX,i=str(values[i]),i+1
                #DemoFlat_RotY,i=str(values[i]),i+1
                #DemoFlat_RotZ,i=str(values[i]),i+1
                #DemoFlat_HLZ,i=str(values[i]),i+1
                #DemoFlat_HLY,i=str(values[i]),i+1
                #DemoFlat_HLX,i=str(values[i]),i+1

                #DemoRTrap_TransX,i=str(values[i]),i+1
                #DemoRTrap_TransY,i=str(values[i]),i+1
                #DemoRTrap_TransZ,i=str(values[i]),i+1
                #DemoRTrap_RotX,i=str(values[i]),i+1
                #DemoRTrap_RotY,i=str(values[i]),i+1
                #DemoRTrap_RotZ,i=str(values[i]),i+1
                #DemoRTrap_LZ,i=str(values[i]),i+1
                #DemoRTrap_LY,i=str(values[i]),i+1
                #DemoRTrap_LX,i=str(values[i]),i+1
                #DemoRTrap_LTX,i=str(values[i]),i+1

                #DemoLTrap_TransX,i=str(values[i]),i+1
                #DemoLTrap_TransY,i=str(values[i]),i+1
                #DemoLTrap_TransZ,i=str(values[i]),i+1
                #DemoLTrap_RotX,i=str(values[i]),i+1
                #DemoLTrap_RotY,i=str(values[i]),i+1
                #DemoLTrap_RotZ,i=str(values[i]),i+1
                #DemoLTrap_LZ,i=str(values[i]),i+1
                #DemoLTrap_LY,i=str(values[i]),i+1
                #DemoLTrap_LX,i=str(values[i]),i+1
                #DemoLTrap_LTX,i=str(values[i]),i+1

                #topsidebox_TransX,i=str(values[i]),i+1
                #topsidebox_TransY,i=str(values[i]),i+1
                #topsidebox_TransZ,i=str(values[i]),i+1
                #topsidebox_RotX,i=str(values[i]),i+1
                #topsidebox_RotY,i=str(values[i]),i+1
                #topsidebox_RotZ,i=str(values[i]),i+1
                #topsidebox_HLZ,i=str(values[i]),i+1
                #topsidebox_HLY,i=str(values[i]),i+1
                #topsidebox_HLX,i=str(values[i]),i+1

                #bottomsidebox_TransX,i=str(values[i]),i+1
                #bottomsidebox_TransY,i=str(values[i]),i+1
                #bottomsidebox_TransZ,i=str(values[i]),i+1
                #bottomsidebox_RotX,i=str(values[i]),i+1
                #bottomsidebox_RotY,i=str(values[i]),i+1
                #bottomsidebox_RotZ,i=str(values[i]),i+1
                #bottomsidebox_HLZ,i=str(values[i]),i+1
                #bottomsidebox_HLY,i=str(values[i]),i+1
                #bottomsidebox_HLX,i=str(values[i]),i+1

                #couch_TransX,i=str(values[i]),i+1 
                #couch_TransY,i=str(values[i]),i+1
                #couch_TransZ,i=str(values[i]),i+1
                #couch_HLZ,i=str(values[i]),i+1
                #couch_HLY,i=str(values[i]),i+1
                #couch_HLX,i=str(values[i]),i+1

                #BeamPosition_TransX,i=str(values[i]),i+1
                #BeamPosition_TransY,i=str(values[i]),i+1
                #BeamPosition_TransZ,i=str(values[i]),i+1
                #BeamPosition_RotZ,i=str(values[i]),i+1
                #BeamPosition_RotY,i=str(values[i]),i+1
                #BeamPosition_RotX,i=str(values[i]),i+1

                #beam_BeamPositionCutoffX,i=str(values[i]),i+1
                #beam_BeamPositionCutoffY,i=str(values[i]),i+1
                #beam_BeamPositionSpreadX,i=str(values[i]),i+1
                #beam_BeamPositionSpreadY,i=str(values[i]),i+1
                #beam_BeamAngularCutoffX,i=str(values[i]),i+1
                #beam_BeamAngularCutoffY,i=str(values[i]),i+1
                #beam_BeamAngularSpreadX,i=str(values[i]),i+1
                #beam_BeamAngularSpreadY,i=str(values[i]),i+1

                #NumberOfSequentialTimes,i=str(values[i]),i+1
                #TimelineEnd,i=str(values[i]),i+1
                #Rotate_rate,i=str(values[i]),i+1
                #Rotate_StartValue,i=str(values[i]),i+1
                #ShowHistoryCountAtInterval,i=str(values[i]),i+1

                #any reason why it is named as centrecsv here?
                centrecsvname = names + "head_"
                for individual_component_name,individual_values in zip(component_name, values):
                    try:
                        if type(float(individual_values)) == float:
                            individual_values = np.round(float(individual_values),4)
                    except:
                        pass
                    centrecsvname += str(individual_component_name)+'_'+str(individual_values)
                centrecsvname = centrecsvname.replace(".","p")
                centrecsvname = centrecsvname.replace("'",'')
                centrecsvname = centrecsvname.replace("[","")
                centrecsvname = centrecsvname.replace("]","")
                #remove vowels for shorter filename 
                centrecsvname = ''.join(char for char in centrecsvname if char.lower() not in 'aeiou')
                #centrecsvname = centrecsvname.replace("-","m")
                #this creates the file in runfolder?
                new_file_name = "runfolder/"+centrecsvname+".bat"
                write_file = open(new_file_name, "w")   
                new_file_name=remove_lines_with_keywords("headsourcecode.bat", new_file_name, components_to_be_del)
                #create a variable here when the input is a range
                #open file in read mode
                print('seed :'+Seed+'threads :'+NumberOfThreads)
                file = open(new_file_name, "r")
                replaced_content = ""
                

                for line in file:

                    line = line.strip()

                    new_line=line.replace("includeFile = ConvertedTopasFile_head.txt","includeFile = "+includeFile)
                    new_line=new_line.replace("i:Ts/Seed=9","i:Ts/Seed="+Seed)
                    new_line=new_line.replace("i:Ts/NumberOfThreads=2","i:Ts/NumberOfThreads="+str(NumberOfThreads))
                    new_line=new_line.replace('s:Ts/G4DataDirectory="/home/leekh/G4Data"','s:Ts/G4DataDirectory='+G4DataDirectory)

                    new_line=new_line.replace("d:Ge/World/HLX=120","d:Ge/World/HLX="+World_HLX)
                    new_line=new_line.replace("d:Ge/World/HLY=120","d:Ge/World/HLY="+World_HLY)
                    new_line=new_line.replace("d:Ge/World/HLZ=120","d:Ge/World/HLZ="+World_HLZ)

                    #Chamber plug made of G4_WATER will overlay CTDI phantom when measurement takes place in that particular port-otherwise will be PMMA
                    new_line = new_line.replace('sv:Ph/Default/LayeredMassGeometryWorlds = 5 "ChamberPlugCentre" "ChamberPlugTop" "ChamberPlugBottom" "ChamberPlugLeft" "ChamberPlugRight"','sv:Ph/Default/LayeredMassGeometryWorlds = ' + LayeredMassGeometryWorlds)

                    #PMMA
                    new_line = new_line.replace('sv:Ma/PMMA/Components = 3 "Carbon" "Hydrogen" "Oxygen"','sv:Ma/PMMA/Components = '+PMMA_Components)
                    new_line = new_line.replace('uv:Ma/PMMA/Fractions = 3 0.599848 0.080538 0.319614','uv:Ma/PMMA/Fractions = '+PMMA_Fractions)
                    new_line = new_line.replace('d:Ma/PMMA/Density = 1.190','d:Ma/PMMA/Density = '+ PMMA_Density)
                    new_line = new_line.replace('d:Ma/PMMA/MeanExcitationEnergy = 85.7','d:Ma/PMMA/MeanExcitationEnergy = '+PMMA_MeanExcitationEnergy)
                    new_line = new_line.replace('s:Ma/PMMA/DefaultColor = "Silver"','s:Ma/PMMA/DefaultColor = '+PMMA_DefaultColor)

                    #Scorers#######################################################
                    new_line=new_line.replace('s:Ge/CTDI/Type="TsCylinder"','s:Ge/CTDI/Type='+CTDI_Type)
                    new_line=new_line.replace('s:Ge/CTDI/Parent="World"','s:Ge/CTDI/Parent='+CTDI_Parent)
                    new_line=new_line.replace('s:Ge/CTDI/Material="PMMA"','s:Ge/CTDI/Material='+CTDI_Material)
                    new_line=new_line.replace('d:Ge/CTDI/RMin=0.0','d:Ge/CTDI/RMin='+CTDI_RMin)
                    new_line=new_line.replace('d:Ge/CTDI/RMax=8.0','d:Ge/CTDI/RMax='+CTDI_RMax)
                    new_line=new_line.replace('d:Ge/CTDI/HL=7.25','d:Ge/CTDI/HL='+CTDI_HL)
                    new_line=new_line.replace('d:Ge/CTDI/SPhi=0.','d:Ge/CTDI/SPhi='+CTDI_SPhi)
                    new_line=new_line.replace('d:Ge/CTDI/DPhi=360.','d:Ge/CTDI/DPhi='+CTDI_DPhi)
                    new_line=new_line.replace('d:Ge/CTDI/TransX=0.0','d:Ge/CTDI/TransX='+CTDI_TransX)
                    new_line=new_line.replace('d:Ge/CTDI/TransY=0.0','d:Ge/CTDI/TransY='+CTDI_TransY)
                    new_line=new_line.replace('d:Ge/CTDI/TransZ=0.0','d:Ge/CTDI/TransZ='+CTDI_TransZ)
                    new_line=new_line.replace('d:Ge/CTDI/RotX=-90','d:Ge/CTDI/RotX='+CTDI_RotX)

                    #ChamberPlugs            
                    
                    new_line=new_line.replace('s:Ge/ChamberPlugCentre/Type="TsCylinder"','s:Ge/ChamberPlugCentre/Type='+ChamberPlugCentre_Type)
                    new_line=new_line.replace('s:Ge/ChamberPlugCentre/Parent="World"','s:Ge/ChamberPlugCentre/Parent='+ChamberPlugCentre_Parent)
                    new_line=new_line.replace('s:Ge/ChamberPlugCentre/Material="PMMA"','s:Ge/ChamberPlugCentre/Material='+ChamberPlugCentre_Material)
                    new_line=new_line.replace('d:Ge/ChamberPlugCentre/RMin=0.0','d:Ge/ChamberPlugCentre/RMin='+ChamberPlugCentre_RMin)
                    new_line=new_line.replace('d:Ge/ChamberPlugCentre/RMax=0.655','d:Ge/ChamberPlugCentre/RMax='+ChamberPlugCentre_RMax)
                    new_line=new_line.replace('d:Ge/ChamberPlugCentre/HL=5.0','d:Ge/ChamberPlugCentre/HL='+ChamberPlugCentre_HL)
                    new_line=new_line.replace('d:Ge/ChamberPlugCentre/SPhi=0.','d:Ge/ChamberPlugCentre/SPhi='+ChamberPlugCentre_SPhi)
                    new_line=new_line.replace('d:Ge/ChamberPlugCentre/DPhi=360.','d:Ge/ChamberPlugCentre/DPhi='+ChamberPlugCentre_DPhi)
                    new_line=new_line.replace('d:Ge/ChamberPlugCentre/TransX=0.0','d:Ge/ChamberPlugCentre/TransX='+ChamberPlugCentre_TransX)
                    new_line=new_line.replace('d:Ge/ChamberPlugCentre/TransY=0.0','d:Ge/ChamberPlugCentre/TransY='+ChamberPlugCentre_TransY)
                    new_line=new_line.replace('d:Ge/ChamberPlugCentre/TransZ=0.0','d:Ge/ChamberPlugCentre/TransZ='+ChamberPlugCentre_TransZ)
                    new_line=new_line.replace('b:Ge/ChamberPlugCentre/isParallel="True"','b:Ge/ChamberPlugCentre/isParallel='+ChamberPlugCentre_isParallel)
                    new_line=new_line.replace('d:Ge/ChamberPlugCentre/RotX=-90','d:Ge/ChamberPlugCentre/RotX='+ChamberPlugCentre_RotX)
                    new_line=new_line.replace('s:Ge/ChamberPlugCentre/color="skyblue"','s:Ge/ChamberPlugCentre/color='+ChamberPlugCentre_color)

                    new_line=new_line.replace('s:Ge/ChamberPlugTop/Type="TsCylinder"','s:Ge/ChamberPlugTop/Type='+ChamberPlugTop_Type)
                    new_line=new_line.replace('s:Ge/ChamberPlugTop/Parent="World"','s:Ge/ChamberPlugTop/Parent='+ChamberPlugTop_Parent)
                    new_line=new_line.replace('s:Ge/ChamberPlugTop/Material="PMMA"','s:Ge/ChamberPlugTop/Material='+ChamberPlugTop_Material)
                    new_line=new_line.replace('d:Ge/ChamberPlugTop/RMin=0.0','d:Ge/ChamberPlugTop/RMin='+ChamberPlugTop_RMin)
                    new_line=new_line.replace('d:Ge/ChamberPlugTop/RMax=0.655','d:Ge/ChamberPlugTop/RMax='+ChamberPlugTop_RMax)
                    new_line=new_line.replace('d:Ge/ChamberPlugTop/HL=5.0','d:Ge/ChamberPlugTop/HL='+ChamberPlugTop_HL)
                    new_line=new_line.replace('d:Ge/ChamberPlugTop/SPhi=0.','d:Ge/ChamberPlugTop/SPhi='+ChamberPlugTop_SPhi)
                    new_line=new_line.replace('d:Ge/ChamberPlugTop/DPhi=360.','d:Ge/ChamberPlugTop/DPhi='+ChamberPlugTop_DPhi)
                    new_line=new_line.replace('d:Ge/ChamberPlugTop/TransX=0.0','d:Ge/ChamberPlugTop/TransX='+ChamberPlugTop_TransX)
                    new_line=new_line.replace('d:Ge/ChamberPlugTop/TransY=0.0','d:Ge/ChamberPlugTop/TransY='+ChamberPlugTop_TransY)
                    new_line=new_line.replace('d:Ge/ChamberPlugTop/TransZ=-7.0','d:Ge/ChamberPlugTop/TransZ='+ChamberPlugTop_TransZ)
                    new_line=new_line.replace('b:Ge/ChamberPlugTop/isParallel="True"','b:Ge/ChamberPlugTop/isParallel='+ChamberPlugTop_isParallel)
                    new_line=new_line.replace('d:Ge/ChamberPlugTop/RotX=-90','d:Ge/ChamberPlugTop/RotX='+ChamberPlugTop_RotX)
                    new_line=new_line.replace('s:Ge/ChamberPlugTop/color="Magenta"','s:Ge/ChamberPlugTop/color='+ChamberPlugTop_color)

                    new_line=new_line.replace('s:Ge/ChamberPlugBottom/Type="TsCylinder"','s:Ge/ChamberPlugBottom/Type='+ChamberPlugBottom_Type)
                    new_line=new_line.replace('s:Ge/ChamberPlugBottom/Parent="World"','s:Ge/ChamberPlugBottom/Parent='+ChamberPlugBottom_Parent)
                    new_line=new_line.replace('s:Ge/ChamberPlugBottom/Material="PMMA"','s:Ge/ChamberPlugBottom/Material='+ChamberPlugBottom_Material)
                    new_line=new_line.replace('d:Ge/ChamberPlugBottom/RMin=0.0','d:Ge/ChamberPlugBottom/RMin='+ChamberPlugBottom_RMin)
                    new_line=new_line.replace('d:Ge/ChamberPlugBottom/RMax=0.655','d:Ge/ChamberPlugBottom/RMax='+ChamberPlugBottom_RMax)
                    new_line=new_line.replace('d:Ge/ChamberPlugBottom/HL=5.0','d:Ge/ChamberPlugBottom/HL='+ChamberPlugBottom_HL)
                    new_line=new_line.replace('d:Ge/ChamberPlugBottom/SPhi=0.','d:Ge/ChamberPlugBottom/SPhi='+ChamberPlugBottom_SPhi)
                    new_line=new_line.replace('d:Ge/ChamberPlugBottom/DPhi=360.','d:Ge/ChamberPlugBottom/DPhi='+ChamberPlugBottom_DPhi)
                    new_line=new_line.replace('d:Ge/ChamberPlugBottom/TransX=0.0','d:Ge/ChamberPlugBottom/TransX='+ChamberPlugBottom_TransX)
                    new_line=new_line.replace('d:Ge/ChamberPlugBottom/TransY=0.0','d:Ge/ChamberPlugBottom/TransY='+ChamberPlugBottom_TransY)
                    new_line=new_line.replace('d:Ge/ChamberPlugBottom/TransZ=7.0','d:Ge/ChamberPlugBottom/TransZ='+ChamberPlugBottom_TransZ)
                    new_line=new_line.replace('b:Ge/ChamberPlugBottom/isParallel="True"','b:Ge/ChamberPlugBottom/isParallel='+ChamberPlugBottom_isParallel)
                    new_line=new_line.replace('d:Ge/ChamberPlugBottom/RotX=-90','d:Ge/ChamberPlugBottom/RotX='+ChamberPlugBottom_RotX)
                    new_line=new_line.replace('s:Ge/ChamberPlugBottom/color="Lime"','s:Ge/ChamberPlugBottom/color='+ChamberPlugBottom_color)

                    new_line=new_line.replace('s:Ge/ChamberPlugLeft/Type="TsCylinder"','s:Ge/ChamberPlugLeft/Type='+ChamberPlugLeft_Type)
                    new_line=new_line.replace('s:Ge/ChamberPlugLeft/Parent="World"','s:Ge/ChamberPlugLeft/Parent='+ChamberPlugLeft_Parent)
                    new_line=new_line.replace('s:Ge/ChamberPlugLeft/Material="PMMA"','s:Ge/ChamberPlugLeft/Material='+ChamberPlugLeft_Material)
                    new_line=new_line.replace('d:Ge/ChamberPlugLeft/RMin=0.0','d:Ge/ChamberPlugLeft/RMin='+ChamberPlugLeft_RMin)
                    new_line=new_line.replace('d:Ge/ChamberPlugLeft/RMax=0.655','d:Ge/ChamberPlugLeft/RMax='+ChamberPlugLeft_RMax)
                    new_line=new_line.replace('d:Ge/ChamberPlugLeft/HL=5.0','d:Ge/ChamberPlugLeft/HL='+ChamberPlugLeft_HL)
                    new_line=new_line.replace('d:Ge/ChamberPlugLeft/SPhi=0.','d:Ge/ChamberPlugLeft/SPhi='+ChamberPlugLeft_SPhi)
                    new_line=new_line.replace('d:Ge/ChamberPlugLeft/DPhi=360.','d:Ge/ChamberPlugLeft/DPhi='+ChamberPlugLeft_DPhi)
                    new_line=new_line.replace('d:Ge/ChamberPlugLeft/TransX=-7.0','d:Ge/ChamberPlugLeft/TransX='+ChamberPlugLeft_TransX)
                    new_line=new_line.replace('d:Ge/ChamberPlugLeft/TransY=0.0','d:Ge/ChamberPlugLeft/TransY='+ChamberPlugLeft_TransY)
                    new_line=new_line.replace('d:Ge/ChamberPlugLeft/TransZ=0.0','d:Ge/ChamberPlugLeft/TransZ='+ChamberPlugLeft_TransZ)
                    new_line=new_line.replace('b:Ge/ChamberPlugLeft/isParallel="True"','b:Ge/ChamberPlugLeft/isParallel='+ChamberPlugLeft_isParallel)
                    new_line=new_line.replace('d:Ge/ChamberPlugLeft/RotX=-90','d:Ge/ChamberPlugLeft/RotX='+ChamberPlugLeft_RotX)
                    new_line=new_line.replace('s:Ge/ChamberPlugLeft/color="Orange"','s:Ge/ChamberPlugLeft/color='+ChamberPlugLeft_color)

                    new_line=new_line.replace('s:Ge/ChamberPlugRight/Type="TsCylinder"','s:Ge/ChamberPlugRight/Type='+ChamberPlugRight_Type)
                    new_line=new_line.replace('s:Ge/ChamberPlugRight/Parent="World"','s:Ge/ChamberPlugRight/Parent='+ChamberPlugRight_Parent)
                    new_line=new_line.replace('s:Ge/ChamberPlugRight/Material="PMMA"','s:Ge/ChamberPlugRight/Material='+ChamberPlugRight_Material)
                    new_line=new_line.replace('d:Ge/ChamberPlugRight/RMin=0.0','d:Ge/ChamberPlugRight/RMin='+ChamberPlugRight_RMin)
                    new_line=new_line.replace('d:Ge/ChamberPlugRight/RMax=0.655','d:Ge/ChamberPlugRight/RMax='+ChamberPlugRight_RMax)
                    new_line=new_line.replace('d:Ge/ChamberPlugRight/HL=5.0','d:Ge/ChamberPlugRight/HL='+ChamberPlugRight_HL)
                    new_line=new_line.replace('d:Ge/ChamberPlugRight/SPhi=0.','d:Ge/ChamberPlugRight/SPhi='+ChamberPlugRight_SPhi)
                    new_line=new_line.replace('d:Ge/ChamberPlugRight/DPhi=360.','d:Ge/ChamberPlugRight/DPhi='+ChamberPlugRight_DPhi)
                    new_line=new_line.replace('d:Ge/ChamberPlugRight/TransX=7.0','d:Ge/ChamberPlugRight/TransX='+ChamberPlugRight_TransX)
                    new_line=new_line.replace('d:Ge/ChamberPlugRight/TransY=0.0','d:Ge/ChamberPlugRight/TransY='+ChamberPlugRight_TransY)
                    new_line=new_line.replace('d:Ge/ChamberPlugRight/TransZ=0.0','d:Ge/ChamberPlugRight/TransZ='+ChamberPlugRight_TransZ)
                    new_line=new_line.replace('b:Ge/ChamberPlugRight/isParallel="True"','b:Ge/ChamberPlugRight/isParallel='+ChamberPlugRight_isParallel)
                    new_line=new_line.replace('d:Ge/ChamberPlugRight/RotX=-90','d:Ge/ChamberPlugRight/RotX='+ChamberPlugRight_RotX)
                    new_line=new_line.replace('s:Ge/ChamberPlugRight/color="Brown"','s:Ge/ChamberPlugRight/color='+ChamberPlugRight_color)


                    ##Scoring###########################################

                    #Scoringalongcylindricalaxis
                    new_line=new_line.replace('s:Sc/ChamberPlugDose_tle/Quantity="TrackLengthEstimator"','s:Sc/ChamberPlugDose_tle/Quantity='+ChamberPlugDose_tle_Quantity)
                    new_line=new_line.replace('s:Sc/ChamberPlugDose_tle/InputFile="Muen.dat"','s:Sc/ChamberPlugDose_tle/InputFile='+ChamberPlugDose_tle_InputFile)
                    new_line=new_line.replace('s:Sc/ChamberPlugDose_tle/Component="ChamberPlugCentre','s:Sc/ChamberPlugDose_tle/Component='+ChamberPlugDose_tle_Component+str(names))
                    new_line=new_line.replace('s:Sc/ChamberPlugDose_tle/IfOutputFileAlreadyExists="Overwrite"','s:Sc/ChamberPlugDose_tle/IfOutputFileAlreadyExists='+ChamberPlugDose_tle_IfOutputFileAlreadyExists)
                    new_line=new_line.replace('i:Sc/ChamberPlugDose_tle/ZBins=100','i:Sc/ChamberPlugDose_tle/ZBins='+ChamberPlugDose_tle_ZBins)

                    new_line=new_line.replace('s:Sc/ChamberPlugDose_dtm/Quantity="DoseToMaterial"','s:Sc/ChamberPlugDose_dtm/Quantity='+ChamberPlugDose_dtm_Quantity)
                    new_line=new_line.replace('s:Sc/ChamberPlugDose_dtm/Component="ChamberPlugCentre','s:Sc/ChamberPlugDose_dtm/Component='+ChamberPlugDose_dtm_Component+str(names))
                    new_line=new_line.replace('s:Sc/ChamberPlugDose_dtm/IfOutputFileAlreadyExists="Overwrite"','s:Sc/ChamberPlugDose_dtm/IfOutputFileAlreadyExists='+ChamberPlugDose_dtm_IfOutputFileAlreadyExists)
                    new_line=new_line.replace('s:Sc/ChamberPlugDose_dtm/Material="Air"','s:Sc/ChamberPlugDose_dtm/Material='+ChamberPlugDose_dtm_Material)
                    new_line=new_line.replace('i:Sc/ChamberPlugDose_dtm/ZBins=100','i:Sc/ChamberPlugDose_dtm/ZBins='+ChamberPlugDose_dtm_ZBins)

                    new_line=new_line.replace('s:Sc/ChamberPlugDose_dtw/Quantity="DoseToWater"','s:Sc/ChamberPlugDose_dtw/Quantity='+ChamberPlugDose_dtw_Quantity)
                    new_line=new_line.replace('s:Sc/ChamberPlugDose_dtw/Component="ChamberPlugCentre','s:Sc/ChamberPlugDose_dtw/Component='+ChamberPlugDose_dtw_Component+str(names))
                    new_line=new_line.replace('s:Sc/ChamberPlugDose_dtw/IfOutputFileAlreadyExists="Overwrite"','s:Sc/ChamberPlugDose_dtw/IfOutputFileAlreadyExists='+ChamberPlugDose_dtw_IfOutputFileAlreadyExists)
                    new_line=new_line.replace('i:Sc/ChamberPlugDose_dtw/ZBins=100','i:Sc/ChamberPlugDose_dtw/ZBins='+ChamberPlugDose_dtw_ZBins)

                    #new_line=new_line.replace('s:Sc/ChamberPlugDose_dtmd/Quantity="DoseToWater"','s:Sc/ChamberPlugDose_dtmd/Quantity='+ChamberPlugDose_dtmd_Quantity)
                    #new_line=new_line.replace('s:Sc/ChamberPlugDose_dtmd/Component="ChamberPlugCentre','s:Sc/ChamberPlugDose_dtmd/Component='+ChamberPlugDose_dtmd_Component+str(names))
                    #new_line=new_line.replace('s:Sc/ChamberPlugDose_dtmd/IfOutputFileAlreadyExists="Overwrite"','s:Sc/ChamberPlugDose_dtmd/IfOutputFileAlreadyExists='+ChamberPlugDose_dtmd_IfOutputFileAlreadyExists)
                    #new_line=new_line.replace('i:Sc/ChamberPlugDose_dtmd/ZBins=100','i:Sc/ChamberPlugDose_dtmd/ZBins='+ChamberPlugDose_dtmd_ZBins)

                    new_line=new_line.replace('s:Sc/ChamberPlugDose_tle/OutputFile="ChamberPlugCentre_tle"','s:Sc/ChamberPlugDose_tle/OutputFile="'+"datafolder/"+str(centrecsvname)+ChamberPlugDose_tle_OutputFile)
                    new_line=new_line.replace('s:Sc/ChamberPlugDose_dtm/OutputFile="ChamberPlugCentre_dtm"','s:Sc/ChamberPlugDose_dtm/OutputFile="'+"datafolder/"+str(centrecsvname)+ChamberPlugDose_dtm_OutputFile)
                    new_line=new_line.replace('s:Sc/ChamberPlugDose_dtw/OutputFile="ChamberPlugCentre_dtw"','s:Sc/ChamberPlugDose_dtw/OutputFile="'+"datafolder/"+str(centrecsvname)+ChamberPlugDose_dtw_OutputFile)
                    

                    #Physics############################################

                    #Usethisonlyforplacinggeometry-prototyping
                    #sv:Ph/Default/Modules=1"g4em-standard_opt0"

                    #defaultforwhenneedtoscore
                    new_line=new_line.replace('s:Ph/ListName="Default"','s:Ph/ListName='+Ph_ListName)
                    new_line=new_line.replace('b:Ph/ListProcesses="False"','b:Ph/ListProcesses='+Ph_ListProcesses)#Settruetodumplistofactivephysicsprocessestoconsole
                    new_line=new_line.replace('s:Ph/Default/Type="Geant4_Modular"','s:Ph/Default/Type='+Ph_Default_Type)
                    new_line=new_line.replace('sv:Ph/Default/Modules= 6 "g4em-standard_opt4" "g4h-phy_QGSP_BIC_HP" "g4decay" "g4ion-binarycascade" "g4h-elastic_HP" "g4stopping"','sv:Ph/Default/Modules='+Ph_Default_Modules)

                    #EMrangefromBrianHZapienCampos'MonteCarloModellingofthekVandMVImagingSystemsontheVarianTruebeamSTxLinac'
                    new_line=new_line.replace('d:Ph/Default/EMRangeMin=100.','d:Ph/Default/EMRangeMin='+Ph_Default_EMRangeMin)
                    new_line=new_line.replace('d:Ph/Default/EMRangeMax=521.','d:Ph/Default/EMRangeMax='+Ph_Default_EMRangeMax)

                    #GroupComponent###########################################

                    #Activelyrotateimagingsystem
                    new_line=new_line.replace('s:Ge/Rotation/Type="Group"','s:Ge/Rotation/Type='+Rotation_Type)
                    new_line=new_line.replace('s:Ge/Rotation/Parent="World"','s:Ge/Rotation/Parent='+Rotation_Parent)
                    new_line=new_line.replace('d:Ge/Rotation/RotX=0.','d:Ge/Rotation/RotX='+Rotation_RotX)
                    new_line=new_line.replace('d:Ge/Rotation/RotY=Tf/Rotate/Value','d:Ge/Rotation/RotY='+Rotation_RotY)
                    new_line=new_line.replace('d:Ge/Rotation/RotZ=0.','d:Ge/Rotation/RotZ='+Rotation_RotZ)
                    new_line=new_line.replace('d:Ge/Rotation/TransX=0.0','d:Ge/Rotation/TransX='+Rotation_TransX)
                    new_line=new_line.replace('d:Ge/Rotation/TransY=0.0','d:Ge/Rotation/TransY='+Rotation_TransY)
                    new_line=new_line.replace('d:Ge/Rotation/TransZ=0.0','d:Ge/Rotation/TransZ='+Rotation_TransZ)

                    #X-Ybladesgroup
                    new_line=new_line.replace('s:Ge/CollimatorsVertical/Type="Group"','s:Ge/CollimatorsVertical/Type='+CollimatorsVertical_Type)
                    new_line=new_line.replace('s:Ge/CollimatorsVertical/Parent="Rotation"','s:Ge/CollimatorsVertical/Parent='+CollimatorsVertical_Parent)
                    new_line=new_line.replace('d:Ge/CollimatorsVertical/RotX=0.','d:Ge/CollimatorsVertical/RotX='+CollimatorsVertical_RotX)
                    new_line=new_line.replace('d:Ge/CollimatorsVertical/RotY=0.','d:Ge/CollimatorsVertical/RotY='+CollimatorsVertical_RotY)
                    new_line=new_line.replace('d:Ge/CollimatorsVertical/RotZ=0.','d:Ge/CollimatorsVertical/RotZ='+CollimatorsVertical_RotZ)
                    new_line=new_line.replace('d:Ge/CollimatorsVertical/TransZ=9.3','d:Ge/CollimatorsVertical/TransZ='+CollimatorsVertical_TransZ)

                    new_line=new_line.replace('s:Ge/CollimatorsHorizontal/Type="Group"','s:Ge/CollimatorsHorizontal/Type='+CollimatorsHorizontal_Type)
                    new_line=new_line.replace('s:Ge/CollimatorsHorizontal/Parent="CollimatorsVertical"','s:Ge/CollimatorsHorizontal/Parent='+CollimatorsHorizontal_Parent)
                    new_line=new_line.replace('d:Ge/CollimatorsHorizontal/RotX=0.','d:Ge/CollimatorsHorizontal/RotX='+CollimatorsHorizontal_RotX)
                    new_line=new_line.replace('d:Ge/CollimatorsHorizontal/RotY=0.','d:Ge/CollimatorsHorizontal/RotY='+CollimatorsHorizontal_RotY)
                    new_line=new_line.replace('d:Ge/CollimatorsHorizontal/RotZ=0.','d:Ge/CollimatorsHorizontal/RotZ='+CollimatorsHorizontal_RotZ)
                    new_line=new_line.replace('d:Ge/CollimatorsHorizontal/TransZ=1.4','d:Ge/CollimatorsHorizontal/TransZ= '+CollimatorsHorizontal_TransZ)

                    #Steelfiltergroup-filterexistinBrianHZCampospaperbutnotseeninTruebeamreferencepaper
                    #willcomparewithandwithouttoseethedifferenceitmakes
                    new_line=new_line.replace('s:Ge/TitaniumFilterGroup/Type="Group"','s:Ge/TitaniumFilterGroup/Type='+TitaniumFilterGroup_Type)
                    new_line=new_line.replace('s:Ge/TitaniumFilterGroup/Parent="CollimatorsHorizontal"','s:Ge/TitaniumFilterGroup/Parent='+TitaniumFilterGroup_Parent)
                    new_line=new_line.replace('d:Ge/TitaniumFilterGroup/RotX=0.','d:Ge/TitaniumFilterGroup/RotX='+TitaniumFilterGroup_RotX)
                    new_line=new_line.replace('d:Ge/TitaniumFilterGroup/RotY=0.','d:Ge/TitaniumFilterGroup/RotY='+TitaniumFilterGroup_RotY)
                    new_line=new_line.replace('d:Ge/TitaniumFilterGroup/RotZ=0.','d:Ge/TitaniumFilterGroup/RotZ='+TitaniumFilterGroup_RotZ)
                    new_line=new_line.replace('d:Ge/TitaniumFilterGroup/TransZ=1.59','d:Ge/TitaniumFilterGroup/TransZ='+TitaniumFilterGroup_TransZ)

                    #bowtiefiltergroupcomponent
                    new_line=new_line.replace('s:Ge/BowtieFilter/Type="Group"','s:Ge/BowtieFilter/Type='+BowtieFilter_Type)
                    new_line=new_line.replace('s:Ge/BowtieFilter/Parent="CollimatorsHorizontal"','s:Ge/BowtieFilter/Parent='+BowtieFilter_Parent)
                    new_line=new_line.replace('d:Ge/BowtieFilter/RotX=0.','d:Ge/BowtieFilter/RotX='+BowtieFilter_RotX)
                    new_line=new_line.replace('d:Ge/BowtieFilter/RotY=0.','d:Ge/BowtieFilter/RotY='+BowtieFilter_RotY)
                    new_line=new_line.replace('d:Ge/BowtieFilter/RotZ=90.','d:Ge/BowtieFilter/RotZ='+BowtieFilter_RotZ)
                    new_line=new_line.replace('d:Ge/BowtieFilter/TransX=0.0','d:Ge/BowtieFilter/TransX='+BowtieFilter_TransX)
                    new_line=new_line.replace('d:Ge/BowtieFilter/TransY=0.0','d:Ge/BowtieFilter/TransY='+BowtieFilter_TransY)
                    new_line=new_line.replace('d:Ge/BowtieFilter/TransZ=3.85','d:Ge/BowtieFilter/TransZ='+BowtieFilter_TransZ)

                    #topcollimator
                    new_line=new_line.replace('s:Ge/Coll1/Type="G4RTrap"','s:Ge/Coll1/Type='+Coll1_Type)
                    new_line=new_line.replace('s:Ge/Coll1/Parent="CollimatorsVertical"','s:Ge/Coll1/Parent='+Coll1_Parent)
                    new_line=new_line.replace('s:Ge/Coll1/Material="Lead"','s:Ge/Coll1/Material='+Coll1_Material)
                    new_line=new_line.replace('d:Ge/Coll1/TransX=0','d:Ge/Coll1/TransX='+Coll1_TransX)
                    new_line=new_line.replace('d:Ge/Coll1/TransY=5.27','d:Ge/Coll1/TransY='+Coll1_TransY)
                    new_line=new_line.replace('d:Ge/Coll1/TransZ=0','d:Ge/Coll1/TransZ='+Coll1_TransZ)
                    new_line=new_line.replace('d:Ge/Coll1/RotX=-90.','d:Ge/Coll1/RotX='+Coll1_RotX)
                    new_line=new_line.replace('d:Ge/Coll1/RotY=90.','d:Ge/Coll1/RotY='+Coll1_RotY)
                    new_line=new_line.replace('d:Ge/Coll1/RotZ=0','d:Ge/Coll1/RotZ='+Coll1_RotZ)
                    new_line=new_line.replace('d:Ge/Coll1/LZ=12.','d:Ge/Coll1/LZ='+Coll1_LZ)
                    new_line=new_line.replace('d:Ge/Coll1/LY=0.3','d:Ge/Coll1/LY='+Coll1_LY)
                    new_line=new_line.replace('d:Ge/Coll1/LX=10.','d:Ge/Coll1/LX='+Coll1_LX)
                    new_line=new_line.replace('d:Ge/Coll1/LTX=9.2','d:Ge/Coll1/LTX='+Coll1_LTX)
                    new_line=new_line.replace('s:Ge/Coll1/Color="pink"','s:Ge/Coll1/Color='+Coll1_Color)

                    #bottomcollimator
                    new_line=new_line.replace('s:Ge/Coll2/Type="G4RTrap"','s:Ge/Coll2/Type='+Coll2_Type)
                    new_line=new_line.replace('s:Ge/Coll2/Parent="CollimatorsVertical"','s:Ge/Coll2/Parent='+Coll2_Parent)
                    new_line=new_line.replace('s:Ge/Coll2/Material="Lead"','s:Ge/Coll2/Material='+Coll2_Material)
                    new_line=new_line.replace('d:Ge/Coll2/TransX=0','d:Ge/Coll2/TransX='+Coll2_TransX)
                    new_line=new_line.replace('d:Ge/Coll2/TransY=-5.27','d:Ge/Coll2/TransY='+Coll2_TransY)
                    new_line=new_line.replace('d:Ge/Coll2/TransZ=0','d:Ge/Coll2/TransZ='+Coll2_TransZ)
                    new_line=new_line.replace('d:Ge/Coll2/RotX=-90.','d:Ge/Coll2/RotX='+Coll2_RotX)
                    new_line=new_line.replace('d:Ge/Coll2/RotY=270.','d:Ge/Coll2/RotY='+Coll2_RotY)
                    new_line=new_line.replace('d:Ge/Coll2/RotZ=0','d:Ge/Coll2/RotZ='+Coll2_RotZ)
                    new_line=new_line.replace('d:Ge/Coll2/LZ=12.','d:Ge/Coll2/LZ='+Coll2_LZ)
                    new_line=new_line.replace('d:Ge/Coll2/LY=0.3','d:Ge/Coll2/LY='+Coll2_LY)
                    new_line=new_line.replace('d:Ge/Coll2/LX=10.','d:Ge/Coll2/LX='+Coll2_LX)
                    new_line=new_line.replace('d:Ge/Coll2/LTX=9.2','d:Ge/Coll2/LTX='+Coll2_LTX)
                    new_line=new_line.replace('s:Ge/Coll2/Color="pink"','s:Ge/Coll2/Color='+Coll2_Color)

                    #rightcollimator
                    new_line=new_line.replace('s:Ge/Coll3/Type="G4RTrap"','s:Ge/Coll3/Type='+Coll3_Type)
                    new_line=new_line.replace('s:Ge/Coll3/Parent="CollimatorsHorizontal"','s:Ge/Coll3/Parent='+Coll3_Parent)
                    new_line=new_line.replace('s:Ge/Coll3/Material="Lead"','s:Ge/Coll3/Material='+Coll3_Material)
                    new_line=new_line.replace('d:Ge/Coll3/TransX=5.27','d:Ge/Coll3/TransX='+Coll3_TransX)
                    new_line=new_line.replace('d:Ge/Coll3/TransY=0.','d:Ge/Coll3/TransY='+Coll3_TransY)
                    new_line=new_line.replace('d:Ge/Coll3/TransZ=0.','d:Ge/Coll3/TransZ='+Coll3_TransZ)
                    new_line=new_line.replace('d:Ge/Coll3/RotX=-90.','d:Ge/Coll3/RotX='+Coll3_RotX)
                    new_line=new_line.replace('d:Ge/Coll3/RotY=180.','d:Ge/Coll3/RotY='+Coll3_RotY)
                    new_line=new_line.replace('d:Ge/Coll3/RotZ=0','d:Ge/Coll3/RotZ='+Coll3_RotZ)
                    new_line=new_line.replace('d:Ge/Coll3/LZ=12.','d:Ge/Coll3/LZ='+Coll3_LZ)
                    new_line=new_line.replace('d:Ge/Coll3/LY=0.3','d:Ge/Coll3/LY='+Coll3_LY)
                    new_line=new_line.replace('d:Ge/Coll3/LX=10.','d:Ge/Coll3/LX='+Coll3_LX)
                    new_line=new_line.replace('d:Ge/Coll3/LTX=9.2','d:Ge/Coll3/LTX='+Coll3_LTX)
                    new_line=new_line.replace('s:Ge/Coll3/Color="yellow"','s:Ge/Coll3/Color='+Coll3_Color)

                    #leftcollimator
                    new_line=new_line.replace('s:Ge/Coll4/Type="G4RTrap"','s:Ge/Coll4/Type='+Coll4_Type)
                    new_line=new_line.replace('s:Ge/Coll4/Parent="CollimatorsHorizontal"','s:Ge/Coll4/Parent='+Coll4_Parent)
                    new_line=new_line.replace('s:Ge/Coll4/Material="Lead"','s:Ge/Coll4/Material='+Coll4_Material)
                    new_line=new_line.replace('d:Ge/Coll4/TransX=-5.27','d:Ge/Coll4/TransX='+Coll4_TransX)
                    new_line=new_line.replace('d:Ge/Coll4/TransY=0.','d:Ge/Coll4/TransY='+Coll4_TransY)
                    new_line=new_line.replace('d:Ge/Coll4/TransZ=0.','d:Ge/Coll4/TransZ='+Coll4_TransZ)
                    new_line=new_line.replace('d:Ge/Coll4/RotX=-90.','d:Ge/Coll4/RotX='+Coll4_RotX)
                    new_line=new_line.replace('d:Ge/Coll4/RotY=0.','d:Ge/Coll4/RotY='+Coll4_RotY)
                    new_line=new_line.replace('d:Ge/Coll4/RotZ=0','d:Ge/Coll4/RotZ='+Coll4_RotZ)
                    new_line=new_line.replace('d:Ge/Coll4/LZ=12.','d:Ge/Coll4/LZ='+Coll4_LZ)
                    new_line=new_line.replace('d:Ge/Coll4/LY=0.3','d:Ge/Coll4/LY='+Coll4_LY)
                    new_line=new_line.replace('d:Ge/Coll4/LX=10.0.','d:Ge/Coll4/LX='+Coll4_LX)
                    new_line=new_line.replace('d:Ge/Coll4/LTX=9.2','d:Ge/Coll4/LTX='+Coll4_LTX)
                    new_line=new_line.replace('s:Ge/Coll4/Color="yellow"','s:Ge/Coll4/Color='+Coll4_Color)

                    new_line=new_line.replace('s:Ge/Coll1steel/Type="G4RTrap"','s:Ge/Coll1steel/Type='+Coll1steel_Type)
                    new_line=new_line.replace('s:Ge/Coll1steel/Parent="CollimatorsVertical"','s:Ge/Coll1steel/Parent='+Coll1steel_Parent)
                    new_line=new_line.replace('s:Ge/Coll1steel/Material="Steel"','s:Ge/Coll1steel/Material='+Coll1steel_Material)
                    new_line=new_line.replace('d:Ge/Coll1steel/TransX=0','d:Ge/Coll1steel/TransX='+Coll1steel_TransX)
                    new_line=new_line.replace('d:Ge/Coll1steel/TransY=Ge/Coll1/TransY - 0.2','d:Ge/Coll1steel/TransY=Ge/Coll1/TransY - '+Coll1steel_TransY)
                    new_line=new_line.replace('d:Ge/Coll1steel/TransZ=-0.25','d:Ge/Coll1steel/TransZ='+Coll1steel_TransZ)
                    new_line=new_line.replace('c:Ge/Coll1steel/RotX=-90.','c:Ge/Coll1steel/RotX='+Coll1steel_RotX)
                    new_line=new_line.replace('d:Ge/Coll1steel/RotY=90.','d:Ge/Coll1steel/RotY='+Coll1steel_RotY)
                    new_line=new_line.replace('d:Ge/Coll1steel/RotZ=0','d:Ge/Coll1steel/RotZ='+Coll1steel_RotZ)
                    new_line=new_line.replace('d:Ge/Coll1steel/LZ=12.','d:Ge/Coll1steel/LZ='+Coll1steel_LZ)
                    new_line=new_line.replace('d:Ge/Coll1steel/LY=0.2','d:Ge/Coll1steel/LY='+Coll1steel_LY)
                    new_line=new_line.replace('d:Ge/Coll1steel/LX=10.','d:Ge/Coll1steel/LX='+Coll1steel_LX)
                    new_line=new_line.replace('d:Ge/Coll1steel/LTX=10.','d:Ge/Coll1steel/LTX='+Coll1steel_LTX)

                    new_line=new_line.replace('s:Ge/Coll2steel/Type="G4RTrap"','s:Ge/Coll2steel/Type='+Coll2steel_Type)
                    new_line=new_line.replace('s:Ge/Coll2steel/Parent="CollimatorsVertical"','s:Ge/Coll2steel/Parent='+Coll2steel_Parent)
                    new_line=new_line.replace('s:Ge/Coll2steel/Material="Steel"','s:Ge/Coll2steel/Material='+Coll2steel_Material)
                    new_line=new_line.replace('d:Ge/Coll2steel/TransX=0','d:Ge/Coll2steel/TransX='+Coll2steel_TransX)
                    new_line=new_line.replace('d:Ge/Coll2steel/TransY=Ge/Coll2/TransY - 0.2','d:Ge/Coll2steel/TransY=Ge/Coll2/TransY - '+Coll2steel_TransY)
                    new_line=new_line.replace('d:Ge/Coll2steel/TransZ=-0.25','d:Ge/Coll2steel/TransZ='+Coll2steel_TransZ)
                    new_line=new_line.replace('c:Ge/Coll2steel/RotX=-90.','c:Ge/Coll2steel/RotX='+Coll2steel_RotX)
                    new_line=new_line.replace('d:Ge/Coll2steel/RotY=90.','d:Ge/Coll2steel/RotY='+Coll2steel_RotY)
                    new_line=new_line.replace('d:Ge/Coll2steel/RotZ=0','d:Ge/Coll2steel/RotZ='+Coll2steel_RotZ)
                    new_line=new_line.replace('d:Ge/Coll2steel/LZ=12.','d:Ge/Coll2steel/LZ='+Coll2steel_LZ)
                    new_line=new_line.replace('d:Ge/Coll2steel/LY=0.2','d:Ge/Coll2steel/LY='+Coll2steel_LY)
                    new_line=new_line.replace('d:Ge/Coll2steel/LX=10.','d:Ge/Coll2steel/LX='+Coll2steel_LX)
                    new_line=new_line.replace('d:Ge/Coll2steel/LTX=10.','d:Ge/Coll2steel/LTX='+Coll2steel_LTX)

                    new_line=new_line.replace('s:Ge/Coll3steel/Type="G4RTrap"','s:Ge/Coll3steel/Type='+Coll3steel_Type)
                    new_line=new_line.replace('s:Ge/Coll3steel/Parent="CollimatorsVertical"','s:Ge/Coll3steel/Parent='+Coll3steel_Parent)
                    new_line=new_line.replace('s:Ge/Coll3steel/Material="Steel"','s:Ge/Coll3steel/Material='+Coll3steel_Material)
                    new_line=new_line.replace('d:Ge/Coll3steel/TransX=0','d:Ge/Coll3steel/TransX='+Coll3steel_TransX)
                    new_line=new_line.replace('d:Ge/Coll3steel/TransY=Ge/Coll3/TransY - 0.2','d:Ge/Coll3steel/TransY=Ge/Coll3/TransY - '+Coll3steel_TransY)
                    new_line=new_line.replace('d:Ge/Coll3steel/TransZ=-0.25','d:Ge/Coll3steel/TransZ='+Coll3steel_TransZ)
                    new_line=new_line.replace('c:Ge/Coll3steel/RotX=-90.','c:Ge/Coll3steel/RotX='+Coll3steel_RotX)
                    new_line=new_line.replace('d:Ge/Coll3steel/RotY=90.','d:Ge/Coll3steel/RotY='+Coll3steel_RotY)
                    new_line=new_line.replace('d:Ge/Coll3steel/RotZ=0','d:Ge/Coll3steel/RotZ='+Coll3steel_RotZ)
                    new_line=new_line.replace('d:Ge/Coll3steel/LZ=12.','d:Ge/Coll3steel/LZ='+Coll3steel_LZ)
                    new_line=new_line.replace('d:Ge/Coll3steel/LY=0.2','d:Ge/Coll3steel/LY='+Coll3steel_LY)
                    new_line=new_line.replace('d:Ge/Coll3steel/LX=10.','d:Ge/Coll3steel/LX='+Coll3steel_LX)
                    new_line=new_line.replace('d:Ge/Coll3steel/LTX=10.','d:Ge/Coll3steel/LTX='+Coll3steel_LTX)

                    new_line=new_line.replace('s:Ge/Coll4steel/Type="G4RTrap"','s:Ge/Coll4steel/Type='+Coll4steel_Type)
                    new_line=new_line.replace('s:Ge/Coll4steel/Parent="CollimatorsVertical"','s:Ge/Coll4steel/Parent='+Coll4steel_Parent)
                    new_line=new_line.replace('s:Ge/Coll4steel/Material="Steel"','s:Ge/Coll4steel/Material='+Coll4steel_Material)
                    new_line=new_line.replace('d:Ge/Coll4steel/TransX=0','d:Ge/Coll4steel/TransX='+Coll4steel_TransX)
                    new_line=new_line.replace('d:Ge/Coll4steel/TransY=Ge/Coll4/TransY - 0.2','d:Ge/Coll4steel/TransY=Ge/Coll4/TransY - '+Coll4steel_TransY)
                    new_line=new_line.replace('d:Ge/Coll4steel/TransZ=-0.25','d:Ge/Coll4steel/TransZ='+Coll4steel_TransZ)
                    new_line=new_line.replace('c:Ge/Coll4steel/RotX=-90.','c:Ge/Coll4steel/RotX='+Coll4steel_RotX)
                    new_line=new_line.replace('d:Ge/Coll4steel/RotY=90.','d:Ge/Coll4steel/RotY='+Coll4steel_RotY)
                    new_line=new_line.replace('d:Ge/Coll4steel/RotZ=0','d:Ge/Coll4steel/RotZ='+Coll4steel_RotZ)
                    new_line=new_line.replace('d:Ge/Coll4steel/LZ=12.','d:Ge/Coll4steel/LZ='+Coll4steel_LZ)
                    new_line=new_line.replace('d:Ge/Coll4steel/LY=0.2','d:Ge/Coll4steel/LY='+Coll4steel_LY)
                    new_line=new_line.replace('d:Ge/Coll4steel/LX=10.','d:Ge/Coll4steel/LX='+Coll4steel_LX)
                    new_line=new_line.replace('d:Ge/Coll4steel/LTX=10.','d:Ge/Coll4steel/LTX='+Coll4steel_LTX)
                    #TitaniumFilter
                    new_line=new_line.replace('s:Ge/TitaniumFilter/Type="TsBox"','s:Ge/TitaniumFilter/Type='+TitaniumFilter_Type)
                    new_line=new_line.replace('s:Ge/TitaniumFilter/Material="Titanium"','s:Ge/TitaniumFilter/Material='+TitaniumFilter_Material)
                    new_line=new_line.replace('s:Ge/TitaniumFilter/Parent="TitaniumFilterGroup"','s:Ge/TitaniumFilter/Parent='+TitaniumFilter_Parent)
                    new_line=new_line.replace('d:Ge/TitaniumFilter/HLX=10.','d:Ge/TitaniumFilter/HLX='+TitaniumFilter_HLX)
                    new_line=new_line.replace('d:Ge/TitaniumFilter/HLY=10.','d:Ge/TitaniumFilter/HLY='+TitaniumFilter_HLY)
                    new_line=new_line.replace('d:Ge/TitaniumFilter/HLZ=0.0445','d:Ge/TitaniumFilter/HLZ='+TitaniumFilter_HLZ)
                    new_line=new_line.replace('d:Ge/TitaniumFilter/TransX=0.','d:Ge/TitaniumFilter/TransX='+TitaniumFilter_TransX)
                    new_line=new_line.replace('d:Ge/TitaniumFilter/TransY=0.','d:Ge/TitaniumFilter/TransY='+TitaniumFilter_TransY)
                    new_line=new_line.replace('d:Ge/TitaniumFilter/TransZ=0.','d:Ge/TitaniumFilter/TransZ='+TitaniumFilter_TransZ)
                    new_line=new_line.replace('d:Ge/TitaniumFilter/RotX=0.','d:Ge/TitaniumFilter/RotX='+TitaniumFilter_RotX)
                    new_line=new_line.replace('d:Ge/TitaniumFilter/RotY=0.','d:Ge/TitaniumFilter/RotY='+TitaniumFilter_RotY)
                    new_line=new_line.replace('d:Ge/TitaniumFilter/RotZ=0.','d:Ge/TitaniumFilter/RotZ='+TitaniumFilter_RotZ)
                    new_line=new_line.replace('s:Ge/TitaniumFilter/Color="lightblue"','s:Ge/TitaniumFilter/Color='+TitaniumFilter_Color)
                    new_line=new_line.replace('s:Ge/TitaniumFilter/DrawingStyle="WireFrame"','s:Ge/TitaniumFilter/DrawingStyle='+TitaniumFilter_DrawingStyle)
                    #bowtiefilter-thinpiece
                    new_line=new_line.replace('s:Ge/DemoFlat/Type="TsBox"','s:Ge/DemoFlat/Type='+DemoFlat_Type)
                    new_line=new_line.replace('s:Ge/DemoFlat/Material="Aluminum"','s:Ge/DemoFlat/Material='+DemoFlat_Material)
                    new_line=new_line.replace('s:Ge/DemoFlat/Parent="BowtieFilter"','s:Ge/DemoFlat/Parent='+DemoFlat_Parent)
                    new_line=new_line.replace('d:Ge/DemoFlat/HLX=0.1','d:Ge/DemoFlat/HLX='+DemoFlat_HLX)
                    new_line=new_line.replace('d:Ge/DemoFlat/HLY=0.4','d:Ge/DemoFlat/HLY='+DemoFlat_HLY)
                    new_line=new_line.replace('d:Ge/DemoFlat/HLZ=7.5.','d:Ge/DemoFlat/HLZ='+DemoFlat_HLZ)
                    new_line=new_line.replace('d:Ge/DemoFlat/TransX=0.0','d:Ge/DemoFlat/TransX='+DemoFlat_TransX)
                    new_line=new_line.replace('d:Ge/DemoFlat/TransY=0.','d:Ge/DemoFlat/TransY='+DemoFlat_TransY)
                    new_line=new_line.replace('d:Ge/DemoFlat/TransZ=0','d:Ge/DemoFlat/TransZ='+DemoFlat_TransZ)
                    new_line=new_line.replace('d:Ge/DemoFlat/RotX=0.','d:Ge/DemoFlat/RotX='+DemoFlat_RotX)
                    new_line=new_line.replace('d:Ge/DemoFlat/RotY=-90.','d:Ge/DemoFlat/RotY='+DemoFlat_RotY)
                    new_line=new_line.replace('d:Ge/DemoFlat/RotZ=0.','d:Ge/DemoFlat/RotZ='+DemoFlat_RotZ)
                    new_line=new_line.replace('s:Ge/DemoFlat/Color="green"','s:Ge/DemoFlat/Color='+DemoFlat_Color)

                    #RTrap-RightAngularWedgeTrapezoid
                    new_line=new_line.replace('s:Ge/DemoRTrap/Type="G4RTrap"','s:Ge/DemoRTrap/Type='+DemoRTrap_Type)
                    new_line=new_line.replace('s:Ge/DemoRTrap/Parent="BowtieFilter"','s:Ge/DemoRTrap/Parent='+DemoRTrap_Parent)
                    new_line=new_line.replace('s:Ge/DemoRTrap/Material="Aluminum"','s:Ge/DemoRTrap/Material='+DemoRTrap_Material)
                    new_line=new_line.replace('d:Ge/DemoRTrap/TransX=0.0','d:Ge/DemoRTrap/TransX='+DemoRTrap_TransX)
                    new_line=new_line.replace('d:Ge/DemoRTrap/TransY=-2.5','d:Ge/DemoRTrap/TransY='+DemoRTrap_TransY)
                    new_line=new_line.replace('d:Ge/DemoRTrap/TransZ=0.65.','d:Ge/DemoRTrap/TransZ='+DemoRTrap_TransZ)
                    new_line=new_line.replace('d:Ge/DemoRTrap/RotX=0','d:Ge/DemoRTrap/RotX='+DemoRTrap_RotX)
                    new_line=new_line.replace('d:Ge/DemoRTrap/RotY=90','d:Ge/DemoRTrap/RotY='+DemoRTrap_RotY)
                    new_line=new_line.replace('d:Ge/DemoRTrap/RotZ=0.','d:Ge/DemoRTrap/RotZ='+DemoRTrap_RotZ)
                    new_line=new_line.replace('d:Ge/DemoRTrap/LZ=15.','d:Ge/DemoRTrap/LZ='+DemoRTrap_LZ)
                    new_line=new_line.replace('d:Ge/DemoRTrap/LY=5.','d:Ge/DemoRTrap/LY='+DemoRTrap_LY)
                    new_line=new_line.replace('d:Ge/DemoRTrap/LX=2.8','d:Ge/DemoRTrap/LX='+DemoRTrap_LX)
                    new_line=new_line.replace('d:Ge/DemoRTrap/LTX=0.2','d:Ge/DemoRTrap/LTX='+DemoRTrap_LTX)
                    new_line=new_line.replace('s:Ge/DemoRTrap/Color="pink"','s:Ge/DemoRTrap/Color='+DemoRTrap_Color)

                    #RTrap-RightAngularWedgeTrapezoid-rotated180ree
                    new_line=new_line.replace('s:Ge/DemoLTrap/Type="G4RTrap"','s:Ge/DemoLTrap/Type='+DemoLTrap_Type)
                    new_line=new_line.replace('s:Ge/DemoLTrap/Parent="BowtieFilter"','s:Ge/DemoLTrap/Parent='+DemoLTrap_Parent)
                    new_line=new_line.replace('s:Ge/DemoLTrap/Material="Aluminum"','s:Ge/DemoLTrap/Material='+DemoLTrap_Material)
                    new_line=new_line.replace('d:Ge/DemoLTrap/TransX=0.0','d:Ge/DemoLTrap/TransX='+DemoLTrap_TransX)
                    new_line=new_line.replace('d:Ge/DemoLTrap/TransY=2.5','d:Ge/DemoLTrap/TransY='+DemoLTrap_TransY)
                    new_line=new_line.replace('d:Ge/DemoLTrap/TransZ=0.65','d:Ge/DemoLTrap/TransZ='+DemoLTrap_TransZ)
                    new_line=new_line.replace('d:Ge/DemoLTrap/RotX=180','d:Ge/DemoLTrap/RotX='+DemoLTrap_RotX)
                    new_line=new_line.replace('d:Ge/DemoLTrap/RotY=270','d:Ge/DemoLTrap/RotY='+DemoLTrap_RotY)
                    new_line=new_line.replace('d:Ge/DemoLTrap/RotZ=0.','d:Ge/DemoLTrap/RotZ='+DemoLTrap_RotZ)
                    new_line=new_line.replace('d:Ge/DemoLTrap/LZ=15.','d:Ge/DemoLTrap/LZ='+DemoLTrap_LZ)
                    new_line=new_line.replace('d:Ge/DemoLTrap/LY=5.','d:Ge/DemoLTrap/LY='+DemoLTrap_LY)
                    new_line=new_line.replace('d:Ge/DemoLTrap/LX=2.8','d:Ge/DemoLTrap/LX='+DemoLTrap_LX)
                    new_line=new_line.replace('d:Ge/DemoLTrap/LTX=0.2','d:Ge/DemoLTrap/LTX='+DemoLTrap_LTX)
                    new_line=new_line.replace('s:Ge/DemoLTrap/Color="pink"','s:Ge/DemoLTrap/Color='+DemoLTrap_Color)

                    #bowtiefilter-topbox
                    new_line=new_line.replace('s:Ge/topsidebox/Type="TsBox"','s:Ge/topsidebox/Type='+topsidebox_Type)
                    new_line=new_line.replace('s:Ge/topsidebox/Material="Aluminum"','s:Ge/topsidebox/Material='+topsidebox_Material)
                    new_line=new_line.replace('s:Ge/topsidebox/Parent="BowtieFilter"','s:Ge/topsidebox/Parent='+topsidebox_Parent)
                    new_line=new_line.replace('d:Ge/topsidebox/HLX=1.4','d:Ge/topsidebox/HLX='+topsidebox_HLX)
                    new_line=new_line.replace('d:Ge/topsidebox/HLY=2.5','d:Ge/topsidebox/HLY='+topsidebox_HLY)
                    new_line=new_line.replace('d:Ge/topsidebox/HLZ=7.5','d:Ge/topsidebox/HLZ='+topsidebox_HLZ)
                    new_line=new_line.replace('d:Ge/topsidebox/TransX=0.0','d:Ge/topsidebox/TransX='+topsidebox_TransX)
                    new_line=new_line.replace('d:Ge/topsidebox/TransY=5.0','d:Ge/topsidebox/TransY='+topsidebox_TransY)
                    new_line=new_line.replace('d:Ge/topsidebox/TransZ=1.3.','d:Ge/topsidebox/TransZ='+topsidebox_TransZ)
                    new_line=new_line.replace('d:Ge/topsidebox/RotX=0.','d:Ge/topsidebox/RotX='+topsidebox_RotX)
                    new_line=new_line.replace('d:Ge/topsidebox/RotY=-90.','d:Ge/topsidebox/RotY='+topsidebox_RotY)
                    new_line=new_line.replace('d:Ge/topsidebox/RotZ=0.','d:Ge/topsidebox/RotZ='+topsidebox_RotZ)
                    new_line=new_line.replace('s:Ge/topsidebox/Color="green"','s:Ge/topsidebox/Color='+topsidebox_Color)

                    #bowtiefilter-bottombox
                    new_line=new_line.replace('s:Ge/bottomsidebox/Type="TsBox"','s:Ge/bottomsidebox/Type='+bottomsidebox_Type)
                    new_line=new_line.replace('s:Ge/bottomsidebox/Material="Aluminum"','s:Ge/bottomsidebox/Material='+bottomsidebox_Material)
                    new_line=new_line.replace('s:Ge/bottomsidebox/Parent="BowtieFilter"','s:Ge/bottomsidebox/Parent='+bottomsidebox_Parent)
                    new_line=new_line.replace('d:Ge/bottomsidebox/HLX=1.4','d:Ge/bottomsidebox/HLX='+bottomsidebox_HLX)
                    new_line=new_line.replace('d:Ge/bottomsidebox/HLY=2.5','d:Ge/bottomsidebox/HLY='+bottomsidebox_HLY)
                    new_line=new_line.replace('d:Ge/bottomsidebox/HLZ=7.5','d:Ge/bottomsidebox/HLZ='+bottomsidebox_HLZ)
                    new_line=new_line.replace('d:Ge/bottomsidebox/TransX=0.0','d:Ge/bottomsidebox/TransX='+bottomsidebox_TransX)
                    new_line=new_line.replace('d:Ge/bottomsidebox/TransY=-5.0','d:Ge/bottomsidebox/TransY='+bottomsidebox_TransY)
                    new_line=new_line.replace('d:Ge/bottomsidebox/TransZ=1.3','d:Ge/bottomsidebox/TransZ='+bottomsidebox_TransZ)
                    new_line=new_line.replace('d:Ge/bottomsidebox/RotX=0.','d:Ge/bottomsidebox/RotX='+bottomsidebox_RotX)
                    new_line=new_line.replace('d:Ge/bottomsidebox/RotY=-90.','d:Ge/bottomsidebox/RotY='+bottomsidebox_RotY)
                    new_line=new_line.replace('d:Ge/bottomsidebox/RotZ=0.','d:Ge/bottomsidebox/RotZ='+bottomsidebox_RotZ)
                    new_line=new_line.replace('s:Ge/bottomsidebox/Color="green"','s:Ge/bottomsidebox/Color='+bottomsidebox_Color)

                    #couch
                    new_line=new_line.replace('s:Ge/couch/Type="TsBox"','s:Ge/couch/Type='+couch_Type)
                    new_line=new_line.replace('s:Ge/couch/Material="Aluminum"','s:Ge/couch/Material='+couch_Material)
                    new_line=new_line.replace('s:Ge/couch/Parent="World"','s:Ge/couch/Parent='+couch_Parent)
                    new_line=new_line.replace('d:Ge/couch/HLX=26.0','d:Ge/couch/HLX='+couch_HLX)
                    new_line=new_line.replace('d:Ge/couch/HLY=100.0','d:Ge/couch/HLY='+couch_HLY)
                    new_line=new_line.replace('d:Ge/couch/HLZ=0.075','d:Ge/couch/HLZ='+couch_HLZ)
                    new_line=new_line.replace('d:Ge/couch/TransX=0.0','d:Ge/couch/TransX='+couch_TransX)
                    new_line=new_line.replace('d:Ge/couch/TransY=0.0','d:Ge/couch/TransY='+couch_TransY)
                    new_line=new_line.replace('d:Ge/couch/TransZ=Ge/couch/HLZ + Ge/CTDI/RMax','d:Ge/couch/TransZ='+couch_TransZ)
                    new_line=new_line.replace('s:Ge/couch/Color="red"','s:Ge/couch/Color='+couch_Color)

                    ###########################################################
                    #Define beam source - cone beam
                    ###########################################################
                    #Define locaton of source in geometry ##################
                    new_line=new_line.replace('s:Ge/BeamPosition/Parent="Rotation"','s:Ge/BeamPosition/Parent='+BeamPosition_Parent)
                    new_line=new_line.replace('s:Ge/BeamPosition/Type="Group"','s:Ge/BeamPosition/Type='+BeamPosition_Type)
                    new_line=new_line.replace('d:Ge/BeamPosition/TransX=0.','d:Ge/BeamPosition/TransX='+BeamPosition_TransX)
                    new_line=new_line.replace('d:Ge/BeamPosition/TransY=0.','d:Ge/BeamPosition/TransY='+BeamPosition_TransY)
                    new_line=new_line.replace('d:Ge/BeamPosition/TransZ=-100.','d:Ge/BeamPosition/TransZ='+BeamPosition_TransZ)
                    new_line=new_line.replace('d:Ge/BeamPosition/RotX=0.','d:Ge/BeamPosition/RotX='+BeamPosition_RotX)
                    new_line=new_line.replace('d:Ge/BeamPosition/RotY=0.','d:Ge/BeamPosition/RotY='+BeamPosition_RotY)
                    new_line=new_line.replace('d:Ge/BeamPosition/RotZ=0.','d:Ge/BeamPosition/RotZ='+BeamPosition_RotZ)
                    #spectrum-needinputfromspekpy
                    new_line=new_line.replace('s:So/beam/BeamEnergySpectrumType="Continuous"','s:So/beam/BeamEnergySpectrumType='+BeamEnergySpectrumType)
                    #new_line=new_line.replace('d:So/beam/BeamEnergy=169.23MeV','d:So/beam/BeamEnergy='+)
                    new_line=new_line.replace('s:So/beam/Type="Beam"','s:So/beam/Type='+beam_Type)#Beam,Isotropic,EmittanceorPhaseSpace
                    new_line=new_line.replace('s:So/beam/Component="BeamPosition"','s:So/beam/Component='+beam_Component)
                    new_line=new_line.replace('s:So/beam/BeamParticle="gamma"','s:So/beam/BeamParticle='+beam_BeamParticle)#'proton','gamma','e-''
                    new_line=new_line.replace('s:So/beam/BeamPositionDistribution="Gaussian"','s:So/beam/BeamPositionDistribution='+beam_BeamPositionDistribution)#FlatorGaussian
                    new_line=new_line.replace('s:So/beam/BeamPositionCutoffShape="Rectangle"','s:So/beam/BeamPositionCutoffShape='+beam_BeamPositionCutoffShape)#Point,Ellipse,RectangleorIsotropic
                    new_line=new_line.replace('d:So/beam/BeamPositionCutoffX=5.','d:So/beam/BeamPositionCutoffX='+beam_BeamPositionCutoffX)#Xextentofposition(ifFlatorGaussian)#fromvarianpg.203
                    new_line=new_line.replace('d:So/beam/BeamPositionCutoffY=5.','d:So/beam/BeamPositionCutoffY='+beam_BeamPositionCutoffY)#Yextentofposition(ifFlatorGaussian
                    new_line=new_line.replace('d:So/beam/BeamPositionSpreadX=0.4246','d:So/beam/BeamPositionSpreadX='+beam_BeamPositionSpreadX)#distribution(ifGaussian)
                    new_line=new_line.replace('d:So/beam/BeamPositionSpreadY=0.4246','d:So/beam/BeamPositionSpreadY='+beam_BeamPositionSpreadY)#distribution(ifGaussian)
                    new_line=new_line.replace('s:So/beam/BeamAngularDistribution="Gaussian"','s:So/beam/BeamAngularDistribution='+beam_BeamAngularDistribution)#FlatorGaussian
                    new_line=new_line.replace('d:So/beam/BeamAngularCutoffX=90','d:So/beam/BeamAngularCutoffX='+beam_BeamAngularCutoffX)#Xcutoffofangulardistrib(ifFlatorGaussian)arctan(25/100)
                    new_line=new_line.replace('d:So/beam/BeamAngularCutoffY=90','d:So/beam/BeamAngularCutoffY='+beam_BeamAngularCutoffY)#Ycutoffofangulardistrib(ifFlatorGaussian)arctan(25/100)
                    new_line=new_line.replace('d:So/beam/BeamAngularSpreadX=28','d:So/beam/BeamAngularSpreadX='+beam_BeamAngularSpreadX)#Xangulardistribution(ifGaussian)
                    new_line=new_line.replace('d:So/beam/BeamAngularSpreadY=28','d:So/beam/BeamAngularSpreadY='+beam_BeamAngularSpreadY)#Yangulardistribution(ifGaussian)
                    new_line=new_line.replace('i:So/beam/NumberOfHistoriesInRun=100000','i:So/beam/NumberOfHistoriesInRun='+beam_NumberOfHistoriesInRun)#4000000#reducebyafactorof12566371fromtheactualparticlegivenbySpekPy.TobemultipliedbytheCTDIvaluetogetactualdosevalue

                    #TimeFeature####################################

                    #eventuallyrunthis
                    #doesnotmakesensetorunthisforscoringPDDandbeamprofile

                    #fromtruebeamtechnicalreferenceguidevol.2imaging:pg.72fullfanscanarc200degree
                    #Declarethatthesimulationshouldcontain8runs.

                    #fullfanrotationrate
                    new_line=new_line.replace('i:Tf/NumberOfSequentialTimes=501','i:Tf/NumberOfSequentialTimes='+NumberOfSequentialTimes)#no.oftimesthissimulationwillreruneachtimewithparticles=numberofhistories
                    new_line=new_line.replace('i:Tf/Verbosity=1','i:Tf/Verbosity='+Verbosity)#Setverbosityhighertogetmoreinformation
                    new_line=new_line.replace('d:Tf/TimelineEnd=501.0s','d:Tf/TimelineEnd='+TimelineEnd)#Specifyanendtimefortherunsequence.
                    #ThefollowingfourparametersdefineaTimeFeaturewearecallingMyRotation.
                    new_line=new_line.replace('s:Tf/Rotate/Function="Linear deg"','s:Tf/Rotate/Function='+Rotate_Function)
                    new_line=new_line.replace('d:Tf/Rotate/Rate=0.4','d:Tf/Rotate/Rate='+Rotate_Rate)#2degree/0.6s->time/rotation=TimelineEnd/totalno.ofangles
                    new_line=new_line.replace('d:Tf/Rotate/StartValue=90.0','d:Tf/Rotate/StartValue='+Rotate_StartValue)

                    #halffanrotationrate
                    #new_line=new_line.replace('i:Tf/NumberOfSequentialTimes=60#no.oftimesthissimulationwillreruneachtimewithparticles=numberofhistories
                    #new_line=new_line.replace('i:Tf/Verbosity=2#Setverbosityhighertogetmoreinformation
                    #new_line=new_line.replace('d:Tf/TimelineEnd=60.0s#Specifyanendtimefortherunsequence.
                    #ThefollowingfourparametersdefineaTimeFeaturewearecallingMyRotation.
                    #new_line=new_line.replace('s:Tf/Rotate/Function="Lineardeg"
                    #new_line=new_line.replace('d:Tf/Rotate/Rate=6 deg/s#2degree/0.6s->time/rotation=TimelineEnd/totalno.ofangles
                    #new_line=new_line.replace('d:Tf/Rotate/StartValue=0.0 deg



                    new_line=new_line.replace('i:Ts/ShowHistoryCountAtInterval=100000','i:Ts/ShowHistoryCountAtInterval='+ShowHistoryCountAtInterval)

                    #halffan360
                    #fullfan200
                    #imagegentlyfullfan80kV
                    #headfullfan100kV
                    #spotlightfullfan125kV
                    #thorax/pelvishalffan125kV
                    #pelvislargehalffan140kV
                    #Asanadditionaldiagnostic,askforparameterstobeprintedoutateachrun:
                    #b:Ts/DumpNonDefaultParameters="True"

                    ##Graphicsoutput###############################
                    #new_line=new_line.replace('Ts/UseQt="True"#ShowGUI#hashthislinetosuppressgui
                    #new_line=new_line.replace('s:Gr/ViewA/Type="OpenGL"#Showsimulation#hashthislinetosuppressgui
                    #new_line=new_line.replace('b:Gr/Enable="T"
                    new_line=new_line.replace('b:Gr/Enable="F"','b:Gr/Enable='+Enable)
                    new_line=new_line.replace('i:Gr/ViewA/WindowSizeX=1024','i:Gr/ViewA/WindowSizeX='+ViewA_WindowSizeX)
                    new_line=new_line.replace('i:Gr/ViewA/WindowSizeY=768','i:Gr/ViewA/WindowSizeY='+ViewA_WindowSizeY)
                    #u:Gr/ViewA/Zoom=1.25
                    new_line=new_line.replace('d:Gr/ViewA/Theta=-20.0','d:Gr/ViewA/Theta='+ViewA_Theta)
                    new_line=new_line.replace('d:Gr/ViewA/Phi=30.0','d:Gr/ViewA/Phi='+ViewA_Phi)
                    new_line=new_line.replace('b:Gr/ViewA/IncludeAxes="True"','b:Gr/ViewA/IncludeAxes='+ViewA_IncludeAxes)
                    new_line=new_line.replace('d:Gr/ViewA/AxesSize=0.5','d:Gr/ViewA/AxesSize='+ViewA_AxesSize)
                    new_line=new_line.replace('u:Gr/ViewA/Zoom=2e+01','u:Gr/ViewA/Zoom='+ViewA_Zoom)
                    new_line=new_line.replace('b:Ts/ShowCPUTime="True"','b:Ts/ShowCPUTime='+ShowCPUTime)

                    replaced_content = replaced_content + new_line + "\n"

                file.close()
                #new_file_name = centrecsvname+".bat"
                write_file = open(new_file_name, "w")
                write_file.write(replaced_content)
                write_file.close()

        #if there are no changes to the default setting or single value change, this replacement block code will be executed instead    
        #note that the import statement in topas_gui.py will trigger this if block because the import statement will run the entire generate_allproc file
        #and since the initial boundaries_list variable is an empty list (length = 0) this will tigger this if block and generate additional 5 files we don't need
        #to stop it from triggering when importing, simply use __name__ == "__main__" and this block of code will only run if it is the top level file aka 'python3 generate_allproc.py'
        if len(boundaries_list) == 0 and __name__ == "__main__":
            centrecsvname = names+"head"+"_default"
            centrecsvname = centrecsvname.replace(".","p")
            #centrecsvname = centrecsvname.replace("-","m")
            new_file_name = "runfolder/"+centrecsvname+".bat"
            #write_file = open(new_file_name, "w")   
            new_file_name=remove_lines_with_keywords("headsourcecode.bat", new_file_name, components_to_be_del)

            file = open(new_file_name, "r")
            replaced_content = ""

            for line in file:

                line = line.strip()

                new_line=line.replace("includeFile = ConvertedTopasFile_head.txt","includeFile = "+includeFile)
                new_line=new_line.replace("i:Ts/Seed=9","i:Ts/Seed="+Seed)
                new_line=new_line.replace("i:Ts/NumberOfThreads=2","i:Ts/NumberOfThreads="+str(NumberOfThreads))
                new_line=new_line.replace('s:Ts/G4DataDirectory="/home/leekh/G4Data"','s:Ts/G4DataDirectory='+G4DataDirectory)

                new_line=new_line.replace("d:Ge/World/HLX=120","d:Ge/World/HLX="+World_HLX)
                new_line=new_line.replace("d:Ge/World/HLY=120","d:Ge/World/HLY="+World_HLY)
                new_line=new_line.replace("d:Ge/World/HLZ=120","d:Ge/World/HLZ="+World_HLZ)

                #Chamber plug made of G4_WATER will overlay CTDI phantom when measurement takes place in that particular port-otherwise will be PMMA
                new_line = new_line.replace('sv:Ph/Default/LayeredMassGeometryWorlds = 5 "ChamberPlugCentre" "ChamberPlugTop" "ChamberPlugBottom" "ChamberPlugLeft" "ChamberPlugRight"','sv:Ph/Default/LayeredMassGeometryWorlds = ' + LayeredMassGeometryWorlds)

                #PMMA
                new_line = new_line.replace('sv:Ma/PMMA/Components = 3 "Carbon" "Hydrogen" "Oxygen"','sv:Ma/PMMA/Components = '+PMMA_Components)
                new_line = new_line.replace('uv:Ma/PMMA/Fractions = 3 0.599848 0.080538 0.319614','uv:Ma/PMMA/Fractions = '+PMMA_Fractions)
                new_line = new_line.replace('d:Ma/PMMA/Density = 1.190','d:Ma/PMMA/Density = '+ PMMA_Density)
                new_line = new_line.replace('d:Ma/PMMA/MeanExcitationEnergy = 85.7','d:Ma/PMMA/MeanExcitationEnergy = '+PMMA_MeanExcitationEnergy)
                new_line = new_line.replace('s:Ma/PMMA/DefaultColor = "Silver"','s:Ma/PMMA/DefaultColor = '+PMMA_DefaultColor)

                #Scorers#######################################################
                new_line=new_line.replace('s:Ge/CTDI/Type="TsCylinder"','s:Ge/CTDI/Type='+CTDI_Type)
                new_line=new_line.replace('s:Ge/CTDI/Parent="World"','s:Ge/CTDI/Parent='+CTDI_Parent)
                new_line=new_line.replace('s:Ge/CTDI/Material="PMMA"','s:Ge/CTDI/Material='+CTDI_Material)
                new_line=new_line.replace('d:Ge/CTDI/RMin=0.0','d:Ge/CTDI/RMin='+CTDI_RMin)
                new_line=new_line.replace('d:Ge/CTDI/RMax=8.0','d:Ge/CTDI/RMax='+CTDI_RMax)
                new_line=new_line.replace('d:Ge/CTDI/HL=7.25','d:Ge/CTDI/HL='+CTDI_HL)
                new_line=new_line.replace('d:Ge/CTDI/SPhi=0.','d:Ge/CTDI/SPhi='+CTDI_SPhi)
                new_line=new_line.replace('d:Ge/CTDI/DPhi=360.','d:Ge/CTDI/DPhi='+CTDI_DPhi)
                new_line=new_line.replace('d:Ge/CTDI/TransX=0.0','d:Ge/CTDI/TransX='+CTDI_TransX)
                new_line=new_line.replace('d:Ge/CTDI/TransY=0.0','d:Ge/CTDI/TransY='+CTDI_TransY)
                new_line=new_line.replace('d:Ge/CTDI/TransZ=0.0','d:Ge/CTDI/TransZ='+CTDI_TransZ)
                new_line=new_line.replace('d:Ge/CTDI/RotX=-90','d:Ge/CTDI/RotX='+CTDI_RotX)

                #ChamberPlugs            
                
                new_line=new_line.replace('s:Ge/ChamberPlugCentre/Type="TsCylinder"','s:Ge/ChamberPlugCentre/Type='+ChamberPlugCentre_Type)
                new_line=new_line.replace('s:Ge/ChamberPlugCentre/Parent="World"','s:Ge/ChamberPlugCentre/Parent='+ChamberPlugCentre_Parent)
                new_line=new_line.replace('s:Ge/ChamberPlugCentre/Material="PMMA"','s:Ge/ChamberPlugCentre/Material='+ChamberPlugCentre_Material)
                new_line=new_line.replace('d:Ge/ChamberPlugCentre/RMin=0.0','d:Ge/ChamberPlugCentre/RMin='+ChamberPlugCentre_RMin)
                new_line=new_line.replace('d:Ge/ChamberPlugCentre/RMax=0.655','d:Ge/ChamberPlugCentre/RMax='+ChamberPlugCentre_RMax)
                new_line=new_line.replace('d:Ge/ChamberPlugCentre/HL=5.0','d:Ge/ChamberPlugCentre/HL='+ChamberPlugCentre_HL)
                new_line=new_line.replace('d:Ge/ChamberPlugCentre/SPhi=0.','d:Ge/ChamberPlugCentre/SPhi='+ChamberPlugCentre_SPhi)
                new_line=new_line.replace('d:Ge/ChamberPlugCentre/DPhi=360.','d:Ge/ChamberPlugCentre/DPhi='+ChamberPlugCentre_DPhi)
                new_line=new_line.replace('d:Ge/ChamberPlugCentre/TransX=0.0','d:Ge/ChamberPlugCentre/TransX='+ChamberPlugCentre_TransX)
                new_line=new_line.replace('d:Ge/ChamberPlugCentre/TransY=0.0','d:Ge/ChamberPlugCentre/TransY='+ChamberPlugCentre_TransY)
                new_line=new_line.replace('d:Ge/ChamberPlugCentre/TransZ=0.0','d:Ge/ChamberPlugCentre/TransZ='+ChamberPlugCentre_TransZ)
                new_line=new_line.replace('b:Ge/ChamberPlugCentre/isParallel="True"','b:Ge/ChamberPlugCentre/isParallel='+ChamberPlugCentre_isParallel)
                new_line=new_line.replace('d:Ge/ChamberPlugCentre/RotX=-90','d:Ge/ChamberPlugCentre/RotX='+ChamberPlugCentre_RotX)
                new_line=new_line.replace('s:Ge/ChamberPlugCentre/color="skyblue"','s:Ge/ChamberPlugCentre/color='+ChamberPlugCentre_color)

                new_line=new_line.replace('s:Ge/ChamberPlugTop/Type="TsCylinder"','s:Ge/ChamberPlugTop/Type='+ChamberPlugTop_Type)
                new_line=new_line.replace('s:Ge/ChamberPlugTop/Parent="World"','s:Ge/ChamberPlugTop/Parent='+ChamberPlugTop_Parent)
                new_line=new_line.replace('s:Ge/ChamberPlugTop/Material="PMMA"','s:Ge/ChamberPlugTop/Material='+ChamberPlugTop_Material)
                new_line=new_line.replace('d:Ge/ChamberPlugTop/RMin=0.0','d:Ge/ChamberPlugTop/RMin='+ChamberPlugTop_RMin)
                new_line=new_line.replace('d:Ge/ChamberPlugTop/RMax=0.655','d:Ge/ChamberPlugTop/RMax='+ChamberPlugTop_RMax)
                new_line=new_line.replace('d:Ge/ChamberPlugTop/HL=5.0','d:Ge/ChamberPlugTop/HL='+ChamberPlugTop_HL)
                new_line=new_line.replace('d:Ge/ChamberPlugTop/SPhi=0.','d:Ge/ChamberPlugTop/SPhi='+ChamberPlugTop_SPhi)
                new_line=new_line.replace('d:Ge/ChamberPlugTop/DPhi=360.','d:Ge/ChamberPlugTop/DPhi='+ChamberPlugTop_DPhi)
                new_line=new_line.replace('d:Ge/ChamberPlugTop/TransX=0.0','d:Ge/ChamberPlugTop/TransX='+ChamberPlugTop_TransX)
                new_line=new_line.replace('d:Ge/ChamberPlugTop/TransY=0.0','d:Ge/ChamberPlugTop/TransY='+ChamberPlugTop_TransY)
                new_line=new_line.replace('d:Ge/ChamberPlugTop/TransZ=-7.0','d:Ge/ChamberPlugTop/TransZ='+ChamberPlugTop_TransZ)
                new_line=new_line.replace('b:Ge/ChamberPlugTop/isParallel="True"','b:Ge/ChamberPlugTop/isParallel='+ChamberPlugTop_isParallel)
                new_line=new_line.replace('d:Ge/ChamberPlugTop/RotX=-90','d:Ge/ChamberPlugTop/RotX='+ChamberPlugTop_RotX)
                new_line=new_line.replace('s:Ge/ChamberPlugTop/color="Magenta"','s:Ge/ChamberPlugTop/color='+ChamberPlugTop_color)

                new_line=new_line.replace('s:Ge/ChamberPlugBottom/Type="TsCylinder"','s:Ge/ChamberPlugBottom/Type='+ChamberPlugBottom_Type)
                new_line=new_line.replace('s:Ge/ChamberPlugBottom/Parent="World"','s:Ge/ChamberPlugBottom/Parent='+ChamberPlugBottom_Parent)
                new_line=new_line.replace('s:Ge/ChamberPlugBottom/Material="PMMA"','s:Ge/ChamberPlugBottom/Material='+ChamberPlugBottom_Material)
                new_line=new_line.replace('d:Ge/ChamberPlugBottom/RMin=0.0','d:Ge/ChamberPlugBottom/RMin='+ChamberPlugBottom_RMin)
                new_line=new_line.replace('d:Ge/ChamberPlugBottom/RMax=0.655','d:Ge/ChamberPlugBottom/RMax='+ChamberPlugBottom_RMax)
                new_line=new_line.replace('d:Ge/ChamberPlugBottom/HL=5.0','d:Ge/ChamberPlugBottom/HL='+ChamberPlugBottom_HL)
                new_line=new_line.replace('d:Ge/ChamberPlugBottom/SPhi=0.','d:Ge/ChamberPlugBottom/SPhi='+ChamberPlugBottom_SPhi)
                new_line=new_line.replace('d:Ge/ChamberPlugBottom/DPhi=360.','d:Ge/ChamberPlugBottom/DPhi='+ChamberPlugBottom_DPhi)
                new_line=new_line.replace('d:Ge/ChamberPlugBottom/TransX=0.0','d:Ge/ChamberPlugBottom/TransX='+ChamberPlugBottom_TransX)
                new_line=new_line.replace('d:Ge/ChamberPlugBottom/TransY=0.0','d:Ge/ChamberPlugBottom/TransY='+ChamberPlugBottom_TransY)
                new_line=new_line.replace('d:Ge/ChamberPlugBottom/TransZ=7.0','d:Ge/ChamberPlugBottom/TransZ='+ChamberPlugBottom_TransZ)
                new_line=new_line.replace('b:Ge/ChamberPlugBottom/isParallel="True"','b:Ge/ChamberPlugBottom/isParallel='+ChamberPlugBottom_isParallel)
                new_line=new_line.replace('d:Ge/ChamberPlugBottom/RotX=-90','d:Ge/ChamberPlugBottom/RotX='+ChamberPlugBottom_RotX)
                new_line=new_line.replace('s:Ge/ChamberPlugBottom/color="Lime"','s:Ge/ChamberPlugBottom/color='+ChamberPlugBottom_color)

                new_line=new_line.replace('s:Ge/ChamberPlugLeft/Type="TsCylinder"','s:Ge/ChamberPlugLeft/Type='+ChamberPlugLeft_Type)
                new_line=new_line.replace('s:Ge/ChamberPlugLeft/Parent="World"','s:Ge/ChamberPlugLeft/Parent='+ChamberPlugLeft_Parent)
                new_line=new_line.replace('s:Ge/ChamberPlugLeft/Material="PMMA"','s:Ge/ChamberPlugLeft/Material='+ChamberPlugLeft_Material)
                new_line=new_line.replace('d:Ge/ChamberPlugLeft/RMin=0.0','d:Ge/ChamberPlugLeft/RMin='+ChamberPlugLeft_RMin)
                new_line=new_line.replace('d:Ge/ChamberPlugLeft/RMax=0.655','d:Ge/ChamberPlugLeft/RMax='+ChamberPlugLeft_RMax)
                new_line=new_line.replace('d:Ge/ChamberPlugLeft/HL=5.0','d:Ge/ChamberPlugLeft/HL='+ChamberPlugLeft_HL)
                new_line=new_line.replace('d:Ge/ChamberPlugLeft/SPhi=0.','d:Ge/ChamberPlugLeft/SPhi='+ChamberPlugLeft_SPhi)
                new_line=new_line.replace('d:Ge/ChamberPlugLeft/DPhi=360.','d:Ge/ChamberPlugLeft/DPhi='+ChamberPlugLeft_DPhi)
                new_line=new_line.replace('d:Ge/ChamberPlugLeft/TransX=-7.0','d:Ge/ChamberPlugLeft/TransX='+ChamberPlugLeft_TransX)
                new_line=new_line.replace('d:Ge/ChamberPlugLeft/TransY=0.0','d:Ge/ChamberPlugLeft/TransY='+ChamberPlugLeft_TransY)
                new_line=new_line.replace('d:Ge/ChamberPlugLeft/TransZ=0.0','d:Ge/ChamberPlugLeft/TransZ='+ChamberPlugLeft_TransZ)
                new_line=new_line.replace('b:Ge/ChamberPlugLeft/isParallel="True"','b:Ge/ChamberPlugLeft/isParallel='+ChamberPlugLeft_isParallel)
                new_line=new_line.replace('d:Ge/ChamberPlugLeft/RotX=-90','d:Ge/ChamberPlugLeft/RotX='+ChamberPlugLeft_RotX)
                new_line=new_line.replace('s:Ge/ChamberPlugLeft/color="Orange"','s:Ge/ChamberPlugLeft/color='+ChamberPlugLeft_color)

                new_line=new_line.replace('s:Ge/ChamberPlugRight/Type="TsCylinder"','s:Ge/ChamberPlugRight/Type='+ChamberPlugRight_Type)
                new_line=new_line.replace('s:Ge/ChamberPlugRight/Parent="World"','s:Ge/ChamberPlugRight/Parent='+ChamberPlugRight_Parent)
                new_line=new_line.replace('s:Ge/ChamberPlugRight/Material="PMMA"','s:Ge/ChamberPlugRight/Material='+ChamberPlugRight_Material)
                new_line=new_line.replace('d:Ge/ChamberPlugRight/RMin=0.0','d:Ge/ChamberPlugRight/RMin='+ChamberPlugRight_RMin)
                new_line=new_line.replace('d:Ge/ChamberPlugRight/RMax=0.655','d:Ge/ChamberPlugRight/RMax='+ChamberPlugRight_RMax)
                new_line=new_line.replace('d:Ge/ChamberPlugRight/HL=5.0','d:Ge/ChamberPlugRight/HL='+ChamberPlugRight_HL)
                new_line=new_line.replace('d:Ge/ChamberPlugRight/SPhi=0.','d:Ge/ChamberPlugRight/SPhi='+ChamberPlugRight_SPhi)
                new_line=new_line.replace('d:Ge/ChamberPlugRight/DPhi=360.','d:Ge/ChamberPlugRight/DPhi='+ChamberPlugRight_DPhi)
                new_line=new_line.replace('d:Ge/ChamberPlugRight/TransX=7.0','d:Ge/ChamberPlugRight/TransX='+ChamberPlugRight_TransX)
                new_line=new_line.replace('d:Ge/ChamberPlugRight/TransY=0.0','d:Ge/ChamberPlugRight/TransY='+ChamberPlugRight_TransY)
                new_line=new_line.replace('d:Ge/ChamberPlugRight/TransZ=0.0','d:Ge/ChamberPlugRight/TransZ='+ChamberPlugRight_TransZ)
                new_line=new_line.replace('b:Ge/ChamberPlugRight/isParallel="True"','b:Ge/ChamberPlugRight/isParallel='+ChamberPlugRight_isParallel)
                new_line=new_line.replace('d:Ge/ChamberPlugRight/RotX=-90','d:Ge/ChamberPlugRight/RotX='+ChamberPlugRight_RotX)
                new_line=new_line.replace('s:Ge/ChamberPlugRight/color="Brown"','s:Ge/ChamberPlugRight/color='+ChamberPlugRight_color)


                ##Scoring###########################################

                #Scoringalongcylindricalaxis
                new_line=new_line.replace('s:Sc/ChamberPlugDose_tle/Quantity="TrackLengthEstimator"','s:Sc/ChamberPlugDose_tle/Quantity='+ChamberPlugDose_tle_Quantity)
                new_line=new_line.replace('s:Sc/ChamberPlugDose_tle/InputFile="Muen.dat"','s:Sc/ChamberPlugDose_tle/InputFile='+ChamberPlugDose_tle_InputFile)
                new_line=new_line.replace('s:Sc/ChamberPlugDose_tle/Component="ChamberPlugCentre','s:Sc/ChamberPlugDose_tle/Component='+ChamberPlugDose_tle_Component+str(names))
                new_line=new_line.replace('s:Sc/ChamberPlugDose_tle/IfOutputFileAlreadyExists="Overwrite"','s:Sc/ChamberPlugDose_tle/IfOutputFileAlreadyExists='+ChamberPlugDose_tle_IfOutputFileAlreadyExists)
                new_line=new_line.replace('i:Sc/ChamberPlugDose_tle/ZBins=100','i:Sc/ChamberPlugDose_tle/ZBins='+ChamberPlugDose_tle_ZBins)

                new_line=new_line.replace('s:Sc/ChamberPlugDose_dtm/Quantity="DoseToMaterial"','s:Sc/ChamberPlugDose_dtm/Quantity='+ChamberPlugDose_dtm_Quantity)
                new_line=new_line.replace('s:Sc/ChamberPlugDose_dtm/Component="ChamberPlugCentre','s:Sc/ChamberPlugDose_dtm/Component='+ChamberPlugDose_dtm_Component+str(names))
                new_line=new_line.replace('s:Sc/ChamberPlugDose_dtm/IfOutputFileAlreadyExists="Overwrite"','s:Sc/ChamberPlugDose_dtm/IfOutputFileAlreadyExists='+ChamberPlugDose_dtm_IfOutputFileAlreadyExists)
                new_line=new_line.replace('s:Sc/ChamberPlugDose_dtm/Material="Air"','s:Sc/ChamberPlugDose_dtm/Material='+ChamberPlugDose_dtm_Material)
                new_line=new_line.replace('i:Sc/ChamberPlugDose_dtm/ZBins=100','i:Sc/ChamberPlugDose_dtm/ZBins='+ChamberPlugDose_dtm_ZBins)

                new_line=new_line.replace('s:Sc/ChamberPlugDose_dtw/Quantity="DoseToWater"','s:Sc/ChamberPlugDose_dtw/Quantity='+ChamberPlugDose_dtw_Quantity)
                new_line=new_line.replace('s:Sc/ChamberPlugDose_dtw/Component="ChamberPlugCentre','s:Sc/ChamberPlugDose_dtw/Component='+ChamberPlugDose_dtw_Component+str(names))
                new_line=new_line.replace('s:Sc/ChamberPlugDose_dtw/IfOutputFileAlreadyExists="Overwrite"','s:Sc/ChamberPlugDose_dtw/IfOutputFileAlreadyExists='+ChamberPlugDose_dtw_IfOutputFileAlreadyExists)
                new_line=new_line.replace('i:Sc/ChamberPlugDose_dtw/ZBins=100','i:Sc/ChamberPlugDose_dtw/ZBins='+ChamberPlugDose_dtw_ZBins)

                #new_line=new_line.replace('s:Sc/ChamberPlugDose_dtmd/Quantity="DoseToWater"','s:Sc/ChamberPlugDose_dtmd/Quantity='+ChamberPlugDose_dtmd_Quantity)
                #new_line=new_line.replace('s:Sc/ChamberPlugDose_dtmd/Component="ChamberPlugCentre','s:Sc/ChamberPlugDose_dtmd/Component='+ChamberPlugDose_dtmd_Component+str(names))
                #new_line=new_line.replace('s:Sc/ChamberPlugDose_dtmd/IfOutputFileAlreadyExists="Overwrite"','s:Sc/ChamberPlugDose_dtmd/IfOutputFileAlreadyExists='+ChamberPlugDose_dtmd_IfOutputFileAlreadyExists)
                #new_line=new_line.replace('i:Sc/ChamberPlugDose_dtmd/ZBins=100','i:Sc/ChamberPlugDose_dtmd/ZBins='+ChamberPlugDose_dtmd_ZBins)

                new_line=new_line.replace('s:Sc/ChamberPlugDose_tle/OutputFile="ChamberPlugCentre_tle"','s:Sc/ChamberPlugDose_tle/OutputFile="'+"datafolder/"+str(centrecsvname)+ChamberPlugDose_tle_OutputFile)
                new_line=new_line.replace('s:Sc/ChamberPlugDose_dtm/OutputFile="ChamberPlugCentre_dtm"','s:Sc/ChamberPlugDose_dtm/OutputFile="'+"datafolder/"+str(centrecsvname)+ChamberPlugDose_dtm_OutputFile)
                new_line=new_line.replace('s:Sc/ChamberPlugDose_dtw/OutputFile="ChamberPlugCentre_dtw"','s:Sc/ChamberPlugDose_dtw/OutputFile="'+"datafolder/"+str(centrecsvname)+ChamberPlugDose_dtw_OutputFile)
                

                #Physics############################################

                #Usethisonlyforplacinggeometry-prototyping
                #sv:Ph/Default/Modules=1"g4em-standard_opt0"

                #defaultforwhenneedtoscore
                new_line=new_line.replace('s:Ph/ListName="Default"','s:Ph/ListName='+Ph_ListName)
                new_line=new_line.replace('b:Ph/ListProcesses="False"','b:Ph/ListProcesses='+Ph_ListProcesses)#Settruetodumplistofactivephysicsprocessestoconsole
                new_line=new_line.replace('s:Ph/Default/Type="Geant4_Modular"','s:Ph/Default/Type='+Ph_Default_Type)
                new_line=new_line.replace('sv:Ph/Default/Modules= 6 "g4em-standard_opt4" "g4h-phy_QGSP_BIC_HP" "g4decay" "g4ion-binarycascade" "g4h-elastic_HP" "g4stopping"','sv:Ph/Default/Modules='+Ph_Default_Modules)

                #EMrangefromBrianHZapienCampos'MonteCarloModellingofthekVandMVImagingSystemsontheVarianTruebeamSTxLinac'
                new_line=new_line.replace('d:Ph/Default/EMRangeMin=100.','d:Ph/Default/EMRangeMin='+Ph_Default_EMRangeMin)
                new_line=new_line.replace('d:Ph/Default/EMRangeMax=521.','d:Ph/Default/EMRangeMax='+Ph_Default_EMRangeMax)

                #GroupComponent###########################################

                #Activelyrotateimagingsystem
                new_line=new_line.replace('s:Ge/Rotation/Type="Group"','s:Ge/Rotation/Type='+Rotation_Type)
                new_line=new_line.replace('s:Ge/Rotation/Parent="World"','s:Ge/Rotation/Parent='+Rotation_Parent)
                new_line=new_line.replace('d:Ge/Rotation/RotX=0.','d:Ge/Rotation/RotX='+Rotation_RotX)
                new_line=new_line.replace('d:Ge/Rotation/RotY=Tf/Rotate/Value','d:Ge/Rotation/RotY='+Rotation_RotY)
                new_line=new_line.replace('d:Ge/Rotation/RotZ=0.','d:Ge/Rotation/RotZ='+Rotation_RotZ)
                new_line=new_line.replace('d:Ge/Rotation/TransX=0.0','d:Ge/Rotation/TransX='+Rotation_TransX)
                new_line=new_line.replace('d:Ge/Rotation/TransY=0.0','d:Ge/Rotation/TransY='+Rotation_TransY)
                new_line=new_line.replace('d:Ge/Rotation/TransZ=0.0','d:Ge/Rotation/TransZ='+Rotation_TransZ)

                #X-Ybladesgroup
                new_line=new_line.replace('s:Ge/CollimatorsVertical/Type="Group"','s:Ge/CollimatorsVertical/Type='+CollimatorsVertical_Type)
                new_line=new_line.replace('s:Ge/CollimatorsVertical/Parent="Rotation"','s:Ge/CollimatorsVertical/Parent='+CollimatorsVertical_Parent)
                new_line=new_line.replace('d:Ge/CollimatorsVertical/RotX=0.','d:Ge/CollimatorsVertical/RotX='+CollimatorsVertical_RotX)
                new_line=new_line.replace('d:Ge/CollimatorsVertical/RotY=0.','d:Ge/CollimatorsVertical/RotY='+CollimatorsVertical_RotY)
                new_line=new_line.replace('d:Ge/CollimatorsVertical/RotZ=0.','d:Ge/CollimatorsVertical/RotZ='+CollimatorsVertical_RotZ)
                new_line=new_line.replace('d:Ge/CollimatorsVertical/TransZ=9.3','d:Ge/CollimatorsVertical/TransZ='+CollimatorsVertical_TransZ)

                new_line=new_line.replace('s:Ge/CollimatorsHorizontal/Type="Group"','s:Ge/CollimatorsHorizontal/Type='+CollimatorsHorizontal_Type)
                new_line=new_line.replace('s:Ge/CollimatorsHorizontal/Parent="CollimatorsVertical"','s:Ge/CollimatorsHorizontal/Parent='+CollimatorsHorizontal_Parent)
                new_line=new_line.replace('d:Ge/CollimatorsHorizontal/RotX=0.','d:Ge/CollimatorsHorizontal/RotX='+CollimatorsHorizontal_RotX)
                new_line=new_line.replace('d:Ge/CollimatorsHorizontal/RotY=0.','d:Ge/CollimatorsHorizontal/RotY='+CollimatorsHorizontal_RotY)
                new_line=new_line.replace('d:Ge/CollimatorsHorizontal/RotZ=0.','d:Ge/CollimatorsHorizontal/RotZ='+CollimatorsHorizontal_RotZ)
                new_line=new_line.replace('d:Ge/CollimatorsHorizontal/TransZ=1.4','d:Ge/CollimatorsHorizontal/TransZ= '+CollimatorsHorizontal_TransZ)

                #Steelfiltergroup-filterexistinBrianHZCampospaperbutnotseeninTruebeamreferencepaper
                #willcomparewithandwithouttoseethedifferenceitmakes
                new_line=new_line.replace('s:Ge/TitaniumFilterGroup/Type="Group"','s:Ge/TitaniumFilterGroup/Type='+TitaniumFilterGroup_Type)
                new_line=new_line.replace('s:Ge/TitaniumFilterGroup/Parent="CollimatorsHorizontal"','s:Ge/TitaniumFilterGroup/Parent='+TitaniumFilterGroup_Parent)
                new_line=new_line.replace('d:Ge/TitaniumFilterGroup/RotX=0.','d:Ge/TitaniumFilterGroup/RotX='+TitaniumFilterGroup_RotX)
                new_line=new_line.replace('d:Ge/TitaniumFilterGroup/RotY=0.','d:Ge/TitaniumFilterGroup/RotY='+TitaniumFilterGroup_RotY)
                new_line=new_line.replace('d:Ge/TitaniumFilterGroup/RotZ=0.','d:Ge/TitaniumFilterGroup/RotZ='+TitaniumFilterGroup_RotZ)
                new_line=new_line.replace('d:Ge/TitaniumFilterGroup/TransZ=1.59','d:Ge/TitaniumFilterGroup/TransZ='+TitaniumFilterGroup_TransZ)

                #bowtiefiltergroupcomponent
                new_line=new_line.replace('s:Ge/BowtieFilter/Type="Group"','s:Ge/BowtieFilter/Type='+BowtieFilter_Type)
                new_line=new_line.replace('s:Ge/BowtieFilter/Parent="CollimatorsHorizontal"','s:Ge/BowtieFilter/Parent='+BowtieFilter_Parent)
                new_line=new_line.replace('d:Ge/BowtieFilter/RotX=0.','d:Ge/BowtieFilter/RotX='+BowtieFilter_RotX)
                new_line=new_line.replace('d:Ge/BowtieFilter/RotY=0.','d:Ge/BowtieFilter/RotY='+BowtieFilter_RotY)
                new_line=new_line.replace('d:Ge/BowtieFilter/RotZ=90.','d:Ge/BowtieFilter/RotZ='+BowtieFilter_RotZ)
                new_line=new_line.replace('d:Ge/BowtieFilter/TransX=0.0','d:Ge/BowtieFilter/TransX='+BowtieFilter_TransX)
                new_line=new_line.replace('d:Ge/BowtieFilter/TransY=0.0','d:Ge/BowtieFilter/TransY='+BowtieFilter_TransY)
                new_line=new_line.replace('d:Ge/BowtieFilter/TransZ=3.85','d:Ge/BowtieFilter/TransZ='+BowtieFilter_TransZ)

                #topcollimator
                new_line=new_line.replace('s:Ge/Coll1/Type="G4RTrap"','s:Ge/Coll1/Type='+Coll1_Type)
                new_line=new_line.replace('s:Ge/Coll1/Parent="CollimatorsVertical"','s:Ge/Coll1/Parent='+Coll1_Parent)
                new_line=new_line.replace('s:Ge/Coll1/Material="Lead"','s:Ge/Coll1/Material='+Coll1_Material)
                new_line=new_line.replace('d:Ge/Coll1/TransX=0','d:Ge/Coll1/TransX='+Coll1_TransX)
                new_line=new_line.replace('d:Ge/Coll1/TransY=5.27','d:Ge/Coll1/TransY='+Coll1_TransY)
                new_line=new_line.replace('d:Ge/Coll1/TransZ=0','d:Ge/Coll1/TransZ='+Coll1_TransZ)
                new_line=new_line.replace('d:Ge/Coll1/RotX=-90.','d:Ge/Coll1/RotX='+Coll1_RotX)
                new_line=new_line.replace('d:Ge/Coll1/RotY=90.','d:Ge/Coll1/RotY='+Coll1_RotY)
                new_line=new_line.replace('d:Ge/Coll1/RotZ=0','d:Ge/Coll1/RotZ='+Coll1_RotZ)
                new_line=new_line.replace('d:Ge/Coll1/LZ=12.','d:Ge/Coll1/LZ='+Coll1_LZ)
                new_line=new_line.replace('d:Ge/Coll1/LY=0.3','d:Ge/Coll1/LY='+Coll1_LY)
                new_line=new_line.replace('d:Ge/Coll1/LX=10.','d:Ge/Coll1/LX='+Coll1_LX)
                new_line=new_line.replace('d:Ge/Coll1/LTX=9.2','d:Ge/Coll1/LTX='+Coll1_LTX)
                new_line=new_line.replace('s:Ge/Coll1/Color="pink"','s:Ge/Coll1/Color='+Coll1_Color)

                #bottomcollimator
                new_line=new_line.replace('s:Ge/Coll2/Type="G4RTrap"','s:Ge/Coll2/Type='+Coll2_Type)
                new_line=new_line.replace('s:Ge/Coll2/Parent="CollimatorsVertical"','s:Ge/Coll2/Parent='+Coll2_Parent)
                new_line=new_line.replace('s:Ge/Coll2/Material="Lead"','s:Ge/Coll2/Material='+Coll2_Material)
                new_line=new_line.replace('d:Ge/Coll2/TransX=0','d:Ge/Coll2/TransX='+Coll2_TransX)
                new_line=new_line.replace('d:Ge/Coll2/TransY=-5.27','d:Ge/Coll2/TransY='+Coll2_TransY)
                new_line=new_line.replace('d:Ge/Coll2/TransZ=0','d:Ge/Coll2/TransZ='+Coll2_TransZ)
                new_line=new_line.replace('d:Ge/Coll2/RotX=-90.','d:Ge/Coll2/RotX='+Coll2_RotX)
                new_line=new_line.replace('d:Ge/Coll2/RotY=270.','d:Ge/Coll2/RotY='+Coll2_RotY)
                new_line=new_line.replace('d:Ge/Coll2/RotZ=0','d:Ge/Coll2/RotZ='+Coll2_RotZ)
                new_line=new_line.replace('d:Ge/Coll2/LZ=12.','d:Ge/Coll2/LZ='+Coll2_LZ)
                new_line=new_line.replace('d:Ge/Coll2/LY=0.3','d:Ge/Coll2/LY='+Coll2_LY)
                new_line=new_line.replace('d:Ge/Coll2/LX=10.','d:Ge/Coll2/LX='+Coll2_LX)
                new_line=new_line.replace('d:Ge/Coll2/LTX=9.2','d:Ge/Coll2/LTX='+Coll2_LTX)
                new_line=new_line.replace('s:Ge/Coll2/Color="pink"','s:Ge/Coll2/Color='+Coll2_Color)

                #rightcollimator
                new_line=new_line.replace('s:Ge/Coll3/Type="G4RTrap"','s:Ge/Coll3/Type='+Coll3_Type)
                new_line=new_line.replace('s:Ge/Coll3/Parent="CollimatorsHorizontal"','s:Ge/Coll3/Parent='+Coll3_Parent)
                new_line=new_line.replace('s:Ge/Coll3/Material="Lead"','s:Ge/Coll3/Material='+Coll3_Material)
                new_line=new_line.replace('d:Ge/Coll3/TransX=5.27','d:Ge/Coll3/TransX='+Coll3_TransX)
                new_line=new_line.replace('d:Ge/Coll3/TransY=0.','d:Ge/Coll3/TransY='+Coll3_TransY)
                new_line=new_line.replace('d:Ge/Coll3/TransZ=0.','d:Ge/Coll3/TransZ='+Coll3_TransZ)
                new_line=new_line.replace('d:Ge/Coll3/RotX=-90.','d:Ge/Coll3/RotX='+Coll3_RotX)
                new_line=new_line.replace('d:Ge/Coll3/RotY=180.','d:Ge/Coll3/RotY='+Coll3_RotY)
                new_line=new_line.replace('d:Ge/Coll3/RotZ=0','d:Ge/Coll3/RotZ='+Coll3_RotZ)
                new_line=new_line.replace('d:Ge/Coll3/LZ=12.','d:Ge/Coll3/LZ='+Coll3_LZ)
                new_line=new_line.replace('d:Ge/Coll3/LY=0.3','d:Ge/Coll3/LY='+Coll3_LY)
                new_line=new_line.replace('d:Ge/Coll3/LX=10.','d:Ge/Coll3/LX='+Coll3_LX)
                new_line=new_line.replace('d:Ge/Coll3/LTX=9.2','d:Ge/Coll3/LTX='+Coll3_LTX)
                new_line=new_line.replace('s:Ge/Coll3/Color="yellow"','s:Ge/Coll3/Color='+Coll3_Color)

                #leftcollimator
                new_line=new_line.replace('s:Ge/Coll4/Type="G4RTrap"','s:Ge/Coll4/Type='+Coll4_Type)
                new_line=new_line.replace('s:Ge/Coll4/Parent="CollimatorsHorizontal"','s:Ge/Coll4/Parent='+Coll4_Parent)
                new_line=new_line.replace('s:Ge/Coll4/Material="Lead"','s:Ge/Coll4/Material='+Coll4_Material)
                new_line=new_line.replace('d:Ge/Coll4/TransX=-5.27','d:Ge/Coll4/TransX='+Coll4_TransX)
                new_line=new_line.replace('d:Ge/Coll4/TransY=0.','d:Ge/Coll4/TransY='+Coll4_TransY)
                new_line=new_line.replace('d:Ge/Coll4/TransZ=0.','d:Ge/Coll4/TransZ='+Coll4_TransZ)
                new_line=new_line.replace('d:Ge/Coll4/RotX=-90.','d:Ge/Coll4/RotX='+Coll4_RotX)
                new_line=new_line.replace('d:Ge/Coll4/RotY=0.','d:Ge/Coll4/RotY='+Coll4_RotY)
                new_line=new_line.replace('d:Ge/Coll4/RotZ=0','d:Ge/Coll4/RotZ='+Coll4_RotZ)
                new_line=new_line.replace('d:Ge/Coll4/LZ=12.','d:Ge/Coll4/LZ='+Coll4_LZ)
                new_line=new_line.replace('d:Ge/Coll4/LY=0.3','d:Ge/Coll4/LY='+Coll4_LY)
                new_line=new_line.replace('d:Ge/Coll4/LX=10.0.','d:Ge/Coll4/LX='+Coll4_LX)
                new_line=new_line.replace('d:Ge/Coll4/LTX=9.2','d:Ge/Coll4/LTX='+Coll4_LTX)
                new_line=new_line.replace('s:Ge/Coll4/Color="yellow"','s:Ge/Coll4/Color='+Coll4_Color)

                new_line=new_line.replace('s:Ge/Coll1steel/Type="G4RTrap"','s:Ge/Coll1steel/Type='+Coll1steel_Type)
                new_line=new_line.replace('s:Ge/Coll1steel/Parent="CollimatorsVertical"','s:Ge/Coll1steel/Parent='+Coll1steel_Parent)
                new_line=new_line.replace('s:Ge/Coll1steel/Material="Steel"','s:Ge/Coll1steel/Material='+Coll1steel_Material)
                new_line=new_line.replace('d:Ge/Coll1steel/TransX=0','d:Ge/Coll1steel/TransX='+Coll1steel_TransX)
                new_line=new_line.replace('d:Ge/Coll1steel/TransY=Ge/Coll1/TransY - 0.2','d:Ge/Coll1steel/TransY=Ge/Coll1/TransY - '+Coll1steel_TransY)
                new_line=new_line.replace('d:Ge/Coll1steel/TransZ=-0.25','d:Ge/Coll1steel/TransZ='+Coll1steel_TransZ)
                new_line=new_line.replace('c:Ge/Coll1steel/RotX=-90.','c:Ge/Coll1steel/RotX='+Coll1steel_RotX)
                new_line=new_line.replace('d:Ge/Coll1steel/RotY=90.','d:Ge/Coll1steel/RotY='+Coll1steel_RotY)
                new_line=new_line.replace('d:Ge/Coll1steel/RotZ=0','d:Ge/Coll1steel/RotZ='+Coll1steel_RotZ)
                new_line=new_line.replace('d:Ge/Coll1steel/LZ=12.','d:Ge/Coll1steel/LZ='+Coll1steel_LZ)
                new_line=new_line.replace('d:Ge/Coll1steel/LY=0.2','d:Ge/Coll1steel/LY='+Coll1steel_LY)
                new_line=new_line.replace('d:Ge/Coll1steel/LX=10.','d:Ge/Coll1steel/LX='+Coll1steel_LX)
                new_line=new_line.replace('d:Ge/Coll1steel/LTX=10.','d:Ge/Coll1steel/LTX='+Coll1steel_LTX)

                new_line=new_line.replace('s:Ge/Coll2steel/Type="G4RTrap"','s:Ge/Coll2steel/Type='+Coll2steel_Type)
                new_line=new_line.replace('s:Ge/Coll2steel/Parent="CollimatorsVertical"','s:Ge/Coll2steel/Parent='+Coll2steel_Parent)
                new_line=new_line.replace('s:Ge/Coll2steel/Material="Steel"','s:Ge/Coll2steel/Material='+Coll2steel_Material)
                new_line=new_line.replace('d:Ge/Coll2steel/TransX=0','d:Ge/Coll2steel/TransX='+Coll2steel_TransX)
                new_line=new_line.replace('d:Ge/Coll2steel/TransY=Ge/Coll2/TransY - 0.2','d:Ge/Coll2steel/TransY=Ge/Coll2/TransY - '+Coll2steel_TransY)
                new_line=new_line.replace('d:Ge/Coll2steel/TransZ=-0.25','d:Ge/Coll2steel/TransZ='+Coll2steel_TransZ)
                new_line=new_line.replace('c:Ge/Coll2steel/RotX=-90.','c:Ge/Coll2steel/RotX='+Coll2steel_RotX)
                new_line=new_line.replace('d:Ge/Coll2steel/RotY=90.','d:Ge/Coll2steel/RotY='+Coll2steel_RotY)
                new_line=new_line.replace('d:Ge/Coll2steel/RotZ=0','d:Ge/Coll2steel/RotZ='+Coll2steel_RotZ)
                new_line=new_line.replace('d:Ge/Coll2steel/LZ=12.','d:Ge/Coll2steel/LZ='+Coll2steel_LZ)
                new_line=new_line.replace('d:Ge/Coll2steel/LY=0.2','d:Ge/Coll2steel/LY='+Coll2steel_LY)
                new_line=new_line.replace('d:Ge/Coll2steel/LX=10.','d:Ge/Coll2steel/LX='+Coll2steel_LX)
                new_line=new_line.replace('d:Ge/Coll2steel/LTX=10.','d:Ge/Coll2steel/LTX='+Coll2steel_LTX)

                new_line=new_line.replace('s:Ge/Coll3steel/Type="G4RTrap"','s:Ge/Coll3steel/Type='+Coll3steel_Type)
                new_line=new_line.replace('s:Ge/Coll3steel/Parent="CollimatorsVertical"','s:Ge/Coll3steel/Parent='+Coll3steel_Parent)
                new_line=new_line.replace('s:Ge/Coll3steel/Material="Steel"','s:Ge/Coll3steel/Material='+Coll3steel_Material)
                new_line=new_line.replace('d:Ge/Coll3steel/TransX=0','d:Ge/Coll3steel/TransX='+Coll3steel_TransX)
                new_line=new_line.replace('d:Ge/Coll3steel/TransY=Ge/Coll3/TransY - 0.2','d:Ge/Coll3steel/TransY=Ge/Coll3/TransY - '+Coll3steel_TransY)
                new_line=new_line.replace('d:Ge/Coll3steel/TransZ=-0.25','d:Ge/Coll3steel/TransZ='+Coll3steel_TransZ)
                new_line=new_line.replace('c:Ge/Coll3steel/RotX=-90.','c:Ge/Coll3steel/RotX='+Coll3steel_RotX)
                new_line=new_line.replace('d:Ge/Coll3steel/RotY=90.','d:Ge/Coll3steel/RotY='+Coll3steel_RotY)
                new_line=new_line.replace('d:Ge/Coll3steel/RotZ=0','d:Ge/Coll3steel/RotZ='+Coll3steel_RotZ)
                new_line=new_line.replace('d:Ge/Coll3steel/LZ=12.','d:Ge/Coll3steel/LZ='+Coll3steel_LZ)
                new_line=new_line.replace('d:Ge/Coll3steel/LY=0.2','d:Ge/Coll3steel/LY='+Coll3steel_LY)
                new_line=new_line.replace('d:Ge/Coll3steel/LX=10.','d:Ge/Coll3steel/LX='+Coll3steel_LX)
                new_line=new_line.replace('d:Ge/Coll3steel/LTX=10.','d:Ge/Coll3steel/LTX='+Coll3steel_LTX)

                new_line=new_line.replace('s:Ge/Coll4steel/Type="G4RTrap"','s:Ge/Coll4steel/Type='+Coll4steel_Type)
                new_line=new_line.replace('s:Ge/Coll4steel/Parent="CollimatorsVertical"','s:Ge/Coll4steel/Parent='+Coll4steel_Parent)
                new_line=new_line.replace('s:Ge/Coll4steel/Material="Steel"','s:Ge/Coll4steel/Material='+Coll4steel_Material)
                new_line=new_line.replace('d:Ge/Coll4steel/TransX=0','d:Ge/Coll4steel/TransX='+Coll4steel_TransX)
                new_line=new_line.replace('d:Ge/Coll4steel/TransY=Ge/Coll4/TransY - 0.2','d:Ge/Coll4steel/TransY=Ge/Coll4/TransY - '+Coll4steel_TransY)
                new_line=new_line.replace('d:Ge/Coll4steel/TransZ=-0.25','d:Ge/Coll4steel/TransZ='+Coll4steel_TransZ)
                new_line=new_line.replace('c:Ge/Coll4steel/RotX=-90.','c:Ge/Coll4steel/RotX='+Coll4steel_RotX)
                new_line=new_line.replace('d:Ge/Coll4steel/RotY=90.','d:Ge/Coll4steel/RotY='+Coll4steel_RotY)
                new_line=new_line.replace('d:Ge/Coll4steel/RotZ=0','d:Ge/Coll4steel/RotZ='+Coll4steel_RotZ)
                new_line=new_line.replace('d:Ge/Coll4steel/LZ=12.','d:Ge/Coll4steel/LZ='+Coll4steel_LZ)
                new_line=new_line.replace('d:Ge/Coll4steel/LY=0.2','d:Ge/Coll4steel/LY='+Coll4steel_LY)
                new_line=new_line.replace('d:Ge/Coll4steel/LX=10.','d:Ge/Coll4steel/LX='+Coll4steel_LX)
                new_line=new_line.replace('d:Ge/Coll4steel/LTX=10.','d:Ge/Coll4steel/LTX='+Coll4steel_LTX)
                #TitaniumFilter
                new_line=new_line.replace('s:Ge/TitaniumFilter/Type="TsBox"','s:Ge/TitaniumFilter/Type='+TitaniumFilter_Type)
                new_line=new_line.replace('s:Ge/TitaniumFilter/Material="Titanium"','s:Ge/TitaniumFilter/Material='+TitaniumFilter_Material)
                new_line=new_line.replace('s:Ge/TitaniumFilter/Parent="TitaniumFilterGroup"','s:Ge/TitaniumFilter/Parent='+TitaniumFilter_Parent)
                new_line=new_line.replace('d:Ge/TitaniumFilter/HLX=10.','d:Ge/TitaniumFilter/HLX='+TitaniumFilter_HLX)
                new_line=new_line.replace('d:Ge/TitaniumFilter/HLY=10.','d:Ge/TitaniumFilter/HLY='+TitaniumFilter_HLY)
                new_line=new_line.replace('d:Ge/TitaniumFilter/HLZ=0.0445','d:Ge/TitaniumFilter/HLZ='+TitaniumFilter_HLZ)
                new_line=new_line.replace('d:Ge/TitaniumFilter/TransX=0.','d:Ge/TitaniumFilter/TransX='+TitaniumFilter_TransX)
                new_line=new_line.replace('d:Ge/TitaniumFilter/TransY=0.','d:Ge/TitaniumFilter/TransY='+TitaniumFilter_TransY)
                new_line=new_line.replace('d:Ge/TitaniumFilter/TransZ=0.','d:Ge/TitaniumFilter/TransZ='+TitaniumFilter_TransZ)
                new_line=new_line.replace('d:Ge/TitaniumFilter/RotX=0.','d:Ge/TitaniumFilter/RotX='+TitaniumFilter_RotX)
                new_line=new_line.replace('d:Ge/TitaniumFilter/RotY=0.','d:Ge/TitaniumFilter/RotY='+TitaniumFilter_RotY)
                new_line=new_line.replace('d:Ge/TitaniumFilter/RotZ=0.','d:Ge/TitaniumFilter/RotZ='+TitaniumFilter_RotZ)
                new_line=new_line.replace('s:Ge/TitaniumFilter/Color="lightblue"','s:Ge/TitaniumFilter/Color='+TitaniumFilter_Color)
                new_line=new_line.replace('s:Ge/TitaniumFilter/DrawingStyle="WireFrame"','s:Ge/TitaniumFilter/DrawingStyle='+TitaniumFilter_DrawingStyle)
                #bowtiefilter-thinpiece
                new_line=new_line.replace('s:Ge/DemoFlat/Type="TsBox"','s:Ge/DemoFlat/Type='+DemoFlat_Type)
                new_line=new_line.replace('s:Ge/DemoFlat/Material="Aluminum"','s:Ge/DemoFlat/Material='+DemoFlat_Material)
                new_line=new_line.replace('s:Ge/DemoFlat/Parent="BowtieFilter"','s:Ge/DemoFlat/Parent='+DemoFlat_Parent)
                new_line=new_line.replace('d:Ge/DemoFlat/HLX=0.1','d:Ge/DemoFlat/HLX='+DemoFlat_HLX)
                new_line=new_line.replace('d:Ge/DemoFlat/HLY=0.4','d:Ge/DemoFlat/HLY='+DemoFlat_HLY)
                new_line=new_line.replace('d:Ge/DemoFlat/HLZ=7.5.','d:Ge/DemoFlat/HLZ='+DemoFlat_HLZ)
                new_line=new_line.replace('d:Ge/DemoFlat/TransX=0.0','d:Ge/DemoFlat/TransX='+DemoFlat_TransX)
                new_line=new_line.replace('d:Ge/DemoFlat/TransY=0.','d:Ge/DemoFlat/TransY='+DemoFlat_TransY)
                new_line=new_line.replace('d:Ge/DemoFlat/TransZ=0','d:Ge/DemoFlat/TransZ='+DemoFlat_TransZ)
                new_line=new_line.replace('d:Ge/DemoFlat/RotX=0.','d:Ge/DemoFlat/RotX='+DemoFlat_RotX)
                new_line=new_line.replace('d:Ge/DemoFlat/RotY=-90.','d:Ge/DemoFlat/RotY='+DemoFlat_RotY)
                new_line=new_line.replace('d:Ge/DemoFlat/RotZ=0.','d:Ge/DemoFlat/RotZ='+DemoFlat_RotZ)
                new_line=new_line.replace('s:Ge/DemoFlat/Color="green"','s:Ge/DemoFlat/Color='+DemoFlat_Color)

                #RTrap-RightAngularWedgeTrapezoid
                new_line=new_line.replace('s:Ge/DemoRTrap/Type="G4RTrap"','s:Ge/DemoRTrap/Type='+DemoRTrap_Type)
                new_line=new_line.replace('s:Ge/DemoRTrap/Parent="BowtieFilter"','s:Ge/DemoRTrap/Parent='+DemoRTrap_Parent)
                new_line=new_line.replace('s:Ge/DemoRTrap/Material="Aluminum"','s:Ge/DemoRTrap/Material='+DemoRTrap_Material)
                new_line=new_line.replace('d:Ge/DemoRTrap/TransX=0.0','d:Ge/DemoRTrap/TransX='+DemoRTrap_TransX)
                new_line=new_line.replace('d:Ge/DemoRTrap/TransY=-2.5','d:Ge/DemoRTrap/TransY='+DemoRTrap_TransY)
                new_line=new_line.replace('d:Ge/DemoRTrap/TransZ=0.65.','d:Ge/DemoRTrap/TransZ='+DemoRTrap_TransZ)
                new_line=new_line.replace('d:Ge/DemoRTrap/RotX=0','d:Ge/DemoRTrap/RotX='+DemoRTrap_RotX)
                new_line=new_line.replace('d:Ge/DemoRTrap/RotY=90','d:Ge/DemoRTrap/RotY='+DemoRTrap_RotY)
                new_line=new_line.replace('d:Ge/DemoRTrap/RotZ=0.','d:Ge/DemoRTrap/RotZ='+DemoRTrap_RotZ)
                new_line=new_line.replace('d:Ge/DemoRTrap/LZ=15.','d:Ge/DemoRTrap/LZ='+DemoRTrap_LZ)
                new_line=new_line.replace('d:Ge/DemoRTrap/LY=5.','d:Ge/DemoRTrap/LY='+DemoRTrap_LY)
                new_line=new_line.replace('d:Ge/DemoRTrap/LX=2.8','d:Ge/DemoRTrap/LX='+DemoRTrap_LX)
                new_line=new_line.replace('d:Ge/DemoRTrap/LTX=0.2','d:Ge/DemoRTrap/LTX='+DemoRTrap_LTX)
                new_line=new_line.replace('s:Ge/DemoRTrap/Color="pink"','s:Ge/DemoRTrap/Color='+DemoRTrap_Color)

                #RTrap-RightAngularWedgeTrapezoid-rotated180ree
                new_line=new_line.replace('s:Ge/DemoLTrap/Type="G4RTrap"','s:Ge/DemoLTrap/Type='+DemoLTrap_Type)
                new_line=new_line.replace('s:Ge/DemoLTrap/Parent="BowtieFilter"','s:Ge/DemoLTrap/Parent='+DemoLTrap_Parent)
                new_line=new_line.replace('s:Ge/DemoLTrap/Material="Aluminum"','s:Ge/DemoLTrap/Material='+DemoLTrap_Material)
                new_line=new_line.replace('d:Ge/DemoLTrap/TransX=0.0','d:Ge/DemoLTrap/TransX='+DemoLTrap_TransX)
                new_line=new_line.replace('d:Ge/DemoLTrap/TransY=2.5','d:Ge/DemoLTrap/TransY='+DemoLTrap_TransY)
                new_line=new_line.replace('d:Ge/DemoLTrap/TransZ=0.65 cm','d:Ge/DemoLTrap/TransZ='+DemoLTrap_TransZ)
                new_line=new_line.replace('d:Ge/DemoLTrap/RotX=180','d:Ge/DemoLTrap/RotX='+DemoLTrap_RotX)
                new_line=new_line.replace('d:Ge/DemoLTrap/RotY=270','d:Ge/DemoLTrap/RotY='+DemoLTrap_RotY)
                new_line=new_line.replace('d:Ge/DemoLTrap/RotZ=0.','d:Ge/DemoLTrap/RotZ='+DemoLTrap_RotZ)
                new_line=new_line.replace('d:Ge/DemoLTrap/LZ=15.','d:Ge/DemoLTrap/LZ='+DemoLTrap_LZ)
                new_line=new_line.replace('d:Ge/DemoLTrap/LY=5.','d:Ge/DemoLTrap/LY='+DemoLTrap_LY)
                new_line=new_line.replace('d:Ge/DemoLTrap/LX=2.8','d:Ge/DemoLTrap/LX='+DemoLTrap_LX)
                new_line=new_line.replace('d:Ge/DemoLTrap/LTX=0.2','d:Ge/DemoLTrap/LTX='+DemoLTrap_LTX)
                new_line=new_line.replace('s:Ge/DemoLTrap/Color="pink"','s:Ge/DemoLTrap/Color='+DemoLTrap_Color)

                #bowtiefilter-topbox
                new_line=new_line.replace('s:Ge/topsidebox/Type="TsBox"','s:Ge/topsidebox/Type='+topsidebox_Type)
                new_line=new_line.replace('s:Ge/topsidebox/Material="Aluminum"','s:Ge/topsidebox/Material='+topsidebox_Material)
                new_line=new_line.replace('s:Ge/topsidebox/Parent="BowtieFilter"','s:Ge/topsidebox/Parent='+topsidebox_Parent)
                new_line=new_line.replace('d:Ge/topsidebox/HLX=1.4','d:Ge/topsidebox/HLX='+topsidebox_HLX)
                new_line=new_line.replace('d:Ge/topsidebox/HLY=2.5','d:Ge/topsidebox/HLY='+topsidebox_HLY)
                new_line=new_line.replace('d:Ge/topsidebox/HLZ=7.5','d:Ge/topsidebox/HLZ='+topsidebox_HLZ)
                new_line=new_line.replace('d:Ge/topsidebox/TransX=0.0','d:Ge/topsidebox/TransX='+topsidebox_TransX)
                new_line=new_line.replace('d:Ge/topsidebox/TransY=5.0','d:Ge/topsidebox/TransY='+topsidebox_TransY)
                new_line=new_line.replace('d:Ge/topsidebox/TransZ=1.3.','d:Ge/topsidebox/TransZ='+topsidebox_TransZ)
                new_line=new_line.replace('d:Ge/topsidebox/RotX=0.','d:Ge/topsidebox/RotX='+topsidebox_RotX)
                new_line=new_line.replace('d:Ge/topsidebox/RotY=-90.','d:Ge/topsidebox/RotY='+topsidebox_RotY)
                new_line=new_line.replace('d:Ge/topsidebox/RotZ=0.','d:Ge/topsidebox/RotZ='+topsidebox_RotZ)
                new_line=new_line.replace('s:Ge/topsidebox/Color="green"','s:Ge/topsidebox/Color='+topsidebox_Color)

                #bowtiefilter-bottombox
                new_line=new_line.replace('s:Ge/bottomsidebox/Type="TsBox"','s:Ge/bottomsidebox/Type='+bottomsidebox_Type)
                new_line=new_line.replace('s:Ge/bottomsidebox/Material="Aluminum"','s:Ge/bottomsidebox/Material='+bottomsidebox_Material)
                new_line=new_line.replace('s:Ge/bottomsidebox/Parent="BowtieFilter"','s:Ge/bottomsidebox/Parent='+bottomsidebox_Parent)
                new_line=new_line.replace('d:Ge/bottomsidebox/HLX=1.4','d:Ge/bottomsidebox/HLX='+bottomsidebox_HLX)
                new_line=new_line.replace('d:Ge/bottomsidebox/HLY=2.5','d:Ge/bottomsidebox/HLY='+bottomsidebox_HLY)
                new_line=new_line.replace('d:Ge/bottomsidebox/HLZ=7.5','d:Ge/bottomsidebox/HLZ='+bottomsidebox_HLZ)
                new_line=new_line.replace('d:Ge/bottomsidebox/TransX=0.0','d:Ge/bottomsidebox/TransX='+bottomsidebox_TransX)
                new_line=new_line.replace('d:Ge/bottomsidebox/TransY=-5.0','d:Ge/bottomsidebox/TransY='+bottomsidebox_TransY)
                new_line=new_line.replace('d:Ge/bottomsidebox/TransZ=1.3','d:Ge/bottomsidebox/TransZ='+bottomsidebox_TransZ)
                new_line=new_line.replace('d:Ge/bottomsidebox/RotX=0.','d:Ge/bottomsidebox/RotX='+bottomsidebox_RotX)
                new_line=new_line.replace('d:Ge/bottomsidebox/RotY=-90.','d:Ge/bottomsidebox/RotY='+bottomsidebox_RotY)
                new_line=new_line.replace('d:Ge/bottomsidebox/RotZ=0.','d:Ge/bottomsidebox/RotZ='+bottomsidebox_RotZ)
                new_line=new_line.replace('s:Ge/bottomsidebox/Color="green"','s:Ge/bottomsidebox/Color='+bottomsidebox_Color)

                #couch
                new_line=new_line.replace('s:Ge/couch/Type="TsBox"','s:Ge/couch/Type='+couch_Type)
                new_line=new_line.replace('s:Ge/couch/Material="Aluminum"','s:Ge/couch/Material='+couch_Material)
                new_line=new_line.replace('s:Ge/couch/Parent="World"','s:Ge/couch/Parent='+couch_Parent)
                new_line=new_line.replace('d:Ge/couch/HLX=26.0','d:Ge/couch/HLX='+couch_HLX)
                new_line=new_line.replace('d:Ge/couch/HLY=100.0','d:Ge/couch/HLY='+couch_HLY)
                new_line=new_line.replace('d:Ge/couch/HLZ=0.075','d:Ge/couch/HLZ='+couch_HLZ)
                new_line=new_line.replace('d:Ge/couch/TransX=0.0','d:Ge/couch/TransX='+couch_TransX)
                new_line=new_line.replace('d:Ge/couch/TransY=0.0','d:Ge/couch/TransY='+couch_TransY)
                new_line=new_line.replace('d:Ge/couch/TransZ=Ge/couch/HLZ + Ge/CTDI/RMax','d:Ge/couch/TransZ='+couch_TransZ)
                new_line=new_line.replace('s:Ge/couch/Color="red"','s:Ge/couch/Color='+couch_Color)

                ###########################################################
                #Define beam source - cone beam
                ###########################################################
                #Define locaton of source in geometry ##################
                new_line=new_line.replace('s:Ge/BeamPosition/Parent="Rotation"','s:Ge/BeamPosition/Parent='+BeamPosition_Parent)
                new_line=new_line.replace('s:Ge/BeamPosition/Type="Group"','s:Ge/BeamPosition/Type='+BeamPosition_Type)
                new_line=new_line.replace('d:Ge/BeamPosition/TransX=0.','d:Ge/BeamPosition/TransX='+BeamPosition_TransX)
                new_line=new_line.replace('d:Ge/BeamPosition/TransY=0.','d:Ge/BeamPosition/TransY='+BeamPosition_TransY)
                new_line=new_line.replace('d:Ge/BeamPosition/TransZ=-100.','d:Ge/BeamPosition/TransZ='+BeamPosition_TransZ)
                new_line=new_line.replace('d:Ge/BeamPosition/RotX=0.','d:Ge/BeamPosition/RotX='+BeamPosition_RotX)
                new_line=new_line.replace('d:Ge/BeamPosition/RotY=0.','d:Ge/BeamPosition/RotY='+BeamPosition_RotY)
                new_line=new_line.replace('d:Ge/BeamPosition/RotZ=0.','d:Ge/BeamPosition/RotZ='+BeamPosition_RotZ)
                #spectrum-needinputfromspekpy
                new_line=new_line.replace('s:So/beam/BeamEnergySpectrumType="Continuous"','s:So/beam/BeamEnergySpectrumType='+BeamEnergySpectrumType)
                #new_line=new_line.replace('d:So/beam/BeamEnergy=169.23MeV','d:So/beam/BeamEnergy='+)
                new_line=new_line.replace('s:So/beam/Type="Beam"','s:So/beam/Type='+beam_Type)#Beam,Isotropic,EmittanceorPhaseSpace
                new_line=new_line.replace('s:So/beam/Component="BeamPosition"','s:So/beam/Component='+beam_Component)
                new_line=new_line.replace('s:So/beam/BeamParticle="gamma"','s:So/beam/BeamParticle='+beam_BeamParticle)#'proton','gamma','e-''
                new_line=new_line.replace('s:So/beam/BeamPositionDistribution="Gaussian"','s:So/beam/BeamPositionDistribution='+beam_BeamPositionDistribution)#FlatorGaussian
                new_line=new_line.replace('s:So/beam/BeamPositionCutoffShape="Rectangle"','s:So/beam/BeamPositionCutoffShape='+beam_BeamPositionCutoffShape)#Point,Ellipse,RectangleorIsotropic
                new_line=new_line.replace('d:So/beam/BeamPositionCutoffX=5.','d:So/beam/BeamPositionCutoffX='+beam_BeamPositionCutoffX)#Xextentofposition(ifFlatorGaussian)#fromvarianpg.203
                new_line=new_line.replace('d:So/beam/BeamPositionCutoffY=5.','d:So/beam/BeamPositionCutoffY='+beam_BeamPositionCutoffY)#Yextentofposition(ifFlatorGaussian
                new_line=new_line.replace('d:So/beam/BeamPositionSpreadX=0.4246','d:So/beam/BeamPositionSpreadX='+beam_BeamPositionSpreadX)#distribution(ifGaussian)
                new_line=new_line.replace('d:So/beam/BeamPositionSpreadY=0.4246','d:So/beam/BeamPositionSpreadY='+beam_BeamPositionSpreadY)#distribution(ifGaussian)
                new_line=new_line.replace('s:So/beam/BeamAngularDistribution="Gaussian"','s:So/beam/BeamAngularDistribution='+beam_BeamAngularDistribution)#FlatorGaussian
                new_line=new_line.replace('d:So/beam/BeamAngularCutoffX=90','d:So/beam/BeamAngularCutoffX='+beam_BeamAngularCutoffX)#Xcutoffofangulardistrib(ifFlatorGaussian)arctan(25/100)
                new_line=new_line.replace('d:So/beam/BeamAngularCutoffY=90','d:So/beam/BeamAngularCutoffY='+beam_BeamAngularCutoffY)#Ycutoffofangulardistrib(ifFlatorGaussian)arctan(25/100)
                new_line=new_line.replace('d:So/beam/BeamAngularSpreadX=28','d:So/beam/BeamAngularSpreadX='+beam_BeamAngularSpreadX)#Xangulardistribution(ifGaussian)
                new_line=new_line.replace('d:So/beam/BeamAngularSpreadY=28','d:So/beam/BeamAngularSpreadY='+beam_BeamAngularSpreadY)#Yangulardistribution(ifGaussian)
                new_line=new_line.replace('i:So/beam/NumberOfHistoriesInRun=100000','i:So/beam/NumberOfHistoriesInRun='+beam_NumberOfHistoriesInRun)#4000000#reducebyafactorof12566371fromtheactualparticlegivenbySpekPy.TobemultipliedbytheCTDIvaluetogetactualdosevalue

                #TimeFeature####################################

                #eventuallyrunthis
                #doesnotmakesensetorunthisforscoringPDDandbeamprofile

                #fromtruebeamtechnicalreferenceguidevol.2imaging:pg.72fullfanscanarc200degree
                #Declarethatthesimulationshouldcontain8runs.

                #fullfanrotationrate
                new_line=new_line.replace('i:Tf/NumberOfSequentialTimes=501','i:Tf/NumberOfSequentialTimes='+NumberOfSequentialTimes)#no.oftimesthissimulationwillreruneachtimewithparticles=numberofhistories
                new_line=new_line.replace('i:Tf/Verbosity=1','i:Tf/Verbosity='+Verbosity)#Setverbosityhighertogetmoreinformation
                new_line=new_line.replace('d:Tf/TimelineEnd=501.0s','d:Tf/TimelineEnd='+TimelineEnd)#Specifyanendtimefortherunsequence.
                #ThefollowingfourparametersdefineaTimeFeaturewearecallingMyRotation.
                new_line=new_line.replace('s:Tf/Rotate/Function="Linear deg"','s:Tf/Rotate/Function='+Rotate_Function)
                new_line=new_line.replace('d:Tf/Rotate/Rate=0.4','d:Tf/Rotate/Rate='+Rotate_Rate)#2degree/0.6s->time/rotation=TimelineEnd/totalno.ofangles
                new_line=new_line.replace('d:Tf/Rotate/StartValue=90.0','d:Tf/Rotate/StartValue='+Rotate_StartValue)

                #halffanrotationrate
                #new_line=new_line.replace('i:Tf/NumberOfSequentialTimes=60#no.oftimesthissimulationwillreruneachtimewithparticles=numberofhistories
                #new_line=new_line.replace('i:Tf/Verbosity=2#Setverbosityhighertogetmoreinformation
                #new_line=new_line.replace('d:Tf/TimelineEnd=60.0s#Specifyanendtimefortherunsequence.
                #ThefollowingfourparametersdefineaTimeFeaturewearecallingMyRotation.
                #new_line=new_line.replace('s:Tf/Rotate/Function="Lineardeg"
                #new_line=new_line.replace('d:Tf/Rotate/Rate=6 deg/s#2degree/0.6s->time/rotation=TimelineEnd/totalno.ofangles
                #new_line=new_line.replace('d:Tf/Rotate/StartValue=0.0 deg



                new_line=new_line.replace('i:Ts/ShowHistoryCountAtInterval=100000','i:Ts/ShowHistoryCountAtInterval='+ShowHistoryCountAtInterval)

                #halffan360
                #fullfan200
                #imagegentlyfullfan80kV
                #headfullfan100kV
                #spotlightfullfan125kV
                #thorax/pelvishalffan125kV
                #pelvislargehalffan140kV
                #Asanadditionaldiagnostic,askforparameterstobeprintedoutateachrun:
                #b:Ts/DumpNonDefaultParameters="True"

                ##Graphicsoutput###############################
                #new_line=new_line.replace('Ts/UseQt="True"#ShowGUI#hashthislinetosuppressgui
                #new_line=new_line.replace('s:Gr/ViewA/Type="OpenGL"#Showsimulation#hashthislinetosuppressgui
                #new_line=new_line.replace('b:Gr/Enable="T"
                new_line=new_line.replace('b:Gr/Enable="F"','b:Gr/Enable='+Enable)
                new_line=new_line.replace('i:Gr/ViewA/WindowSizeX=1024','i:Gr/ViewA/WindowSizeX='+ViewA_WindowSizeX)
                new_line=new_line.replace('i:Gr/ViewA/WindowSizeY=768','i:Gr/ViewA/WindowSizeY='+ViewA_WindowSizeY)
                #u:Gr/ViewA/Zoom=1.25
                new_line=new_line.replace('d:Gr/ViewA/Theta=-20.0','d:Gr/ViewA/Theta='+ViewA_Theta)
                new_line=new_line.replace('d:Gr/ViewA/Phi=30.0','d:Gr/ViewA/Phi='+ViewA_Phi)
                new_line=new_line.replace('b:Gr/ViewA/IncludeAxes="True"','b:Gr/ViewA/IncludeAxes='+ViewA_IncludeAxes)
                new_line=new_line.replace('d:Gr/ViewA/AxesSize=0.5','d:Gr/ViewA/AxesSize='+ViewA_AxesSize)
                new_line=new_line.replace('u:Gr/ViewA/Zoom=2e+01','u:Gr/ViewA/Zoom='+ViewA_Zoom)
                new_line=new_line.replace('b:Ts/ShowCPUTime="True"','b:Ts/ShowCPUTime='+ShowCPUTime)


                replaced_content = replaced_content + new_line + "\n"

            file.close()
            #new_file_name = centrecsvname+".bat"
            write_file = open(new_file_name, "w")
            write_file.write(replaced_content)
            write_file.close()

        globals()[chamberplugmaterial] = pmma
 #new_subfile_name = "head"+names+"_ctdisourcexshift_beam_sub.bat"
 #write_subfile = open(new_subfile_name, "w")
 #write_subfile.write(replaced_content)
 #write_subfile.close()

