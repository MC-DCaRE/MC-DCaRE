
# Models simple cone beam geometry
######################################################

## Include File ###############################
includeFile = ConvertedTopasFile.txt

## Some Control Parameters ####################
i:Ts/Seed=9#startingrandomseed
i:Ts/NumberOfThreads=4#NumberofCPUthreadstowhichworkwillbedistributed
#negativenumbermeansuseallbutthesenumberofthreads
#zeromeansuseall
s:Ts/G4DataDirectory="/home/leekh/G4Data"

##DefineWorldGeometry############################
d:Ge/World/HLX=120 cm #HalfLength
d:Ge/World/HLY=120 cm
d:Ge/World/HLZ=120 cm

# Chamber plug made of G4_WATER  will overlay CTDI phantom when measurement takes place in that particular port-otherwise will be PMMA
sv:Ph/Default/LayeredMassGeometryWorlds = 5 "ChamberPlugCentre" "ChamberPlugTop" "ChamberPlugBottom" "ChamberPlugLeft" "ChamberPlugRight"

# PMMA
sv:Ma/PMMA/Components = 3 "Carbon" "Hydrogen" "Oxygen"
uv:Ma/PMMA/Fractions = 3  0.599848  0.080538  0.319614
d:Ma/PMMA/Density = 1.190 g/cm3
d:Ma/PMMA/MeanExcitationEnergy = 85.7 eV #nist say 74 eV? #85.7 eV on topas example
s:Ma/PMMA/DefaultColor = "Silver"


#Scorers#######################################################
s:Ge/CTDI/Type="TsCylinder"
s:Ge/CTDI/Parent="World"
s:Ge/CTDI/Material="PMMA"
d:Ge/CTDI/RMin=0.0 cm
d:Ge/CTDI/RMax=8.0 cm
d:Ge/CTDI/HL=7.25 cm
d:Ge/CTDI/SPhi=0. deg
d:Ge/CTDI/DPhi=360. deg
d:Ge/CTDI/TransX=0.0 cm
d:Ge/CTDI/TransY=0.0 cm
d:Ge/CTDI/TransZ=0.0 cm
d:Ge/CTDI/RotX=-90 deg

#ChamberPlugs
s:Ge/ChamberPlugCentre/Type="TsCylinder"
s:Ge/ChamberPlugCentre/Parent="World"
s:Ge/ChamberPlugCentre/Material="Air"
d:Ge/ChamberPlugCentre/RMin=0.0 cm
d:Ge/ChamberPlugCentre/RMax=1.0 cm
d:Ge/ChamberPlugCentre/HL=5.0 cm
d:Ge/ChamberPlugCentre/SPhi=0. deg
d:Ge/ChamberPlugCentre/DPhi=360. deg
d:Ge/ChamberPlugCentre/TransX=0.0 cm
d:Ge/ChamberPlugCentre/TransY=0.0 cm
d:Ge/ChamberPlugCentre/TransZ=0.0 cm
b:Ge/ChamberPlugCentre/isParallel="True"
d:Ge/ChamberPlugCentre/RotX=-90 deg
s:Ge/ChamberPlugCentre/color="skyblue"

s:Ge/ChamberPlugTop/Type="TsCylinder"
s:Ge/ChamberPlugTop/Parent="World"
s:Ge/ChamberPlugTop/Material="PMMA"
d:Ge/ChamberPlugTop/RMin=0.0 cm
d:Ge/ChamberPlugTop/RMax=0.655 cm
d:Ge/ChamberPlugTop/HL=5.0 cm
d:Ge/ChamberPlugTop/SPhi=0. deg
d:Ge/ChamberPlugTop/DPhi=360. deg
d:Ge/ChamberPlugTop/TransX=0.0 cm
d:Ge/ChamberPlugTop/TransY=0.0 cm
d:Ge/ChamberPlugTop/TransZ=-7.0 cm
b:Ge/ChamberPlugTop/isParallel="True"
d:Ge/ChamberPlugTop/RotX=-90 deg
s:Ge/ChamberPlugTop/color="Magenta"

s:Ge/ChamberPlugBottom/Type="TsCylinder"
s:Ge/ChamberPlugBottom/Parent="World"
s:Ge/ChamberPlugBottom/Material="PMMA"
d:Ge/ChamberPlugBottom/RMin=0.0 cm
d:Ge/ChamberPlugBottom/RMax=0.655 cm
d:Ge/ChamberPlugBottom/HL=5.0 cm
d:Ge/ChamberPlugBottom/SPhi=0. deg
d:Ge/ChamberPlugBottom/DPhi=360. deg
d:Ge/ChamberPlugBottom/TransX=0.0 cm
d:Ge/ChamberPlugBottom/TransY=0.0 cm
d:Ge/ChamberPlugBottom/TransZ=7.0 cm
b:Ge/ChamberPlugBottom/isParallel="True"
d:Ge/ChamberPlugBottom/RotX=-90 deg
s:Ge/ChamberPlugBottom/color="Lime"

s:Ge/ChamberPlugLeft/Type="TsCylinder"
s:Ge/ChamberPlugLeft/Parent="World"
s:Ge/ChamberPlugLeft/Material="PMMA"
d:Ge/ChamberPlugLeft/RMin=0.0 cm
d:Ge/ChamberPlugLeft/RMax=0.655 cm
d:Ge/ChamberPlugLeft/HL=5.0 cm
d:Ge/ChamberPlugLeft/SPhi=0. deg
d:Ge/ChamberPlugLeft/DPhi=360. deg
d:Ge/ChamberPlugLeft/TransX=-7.0 cm
d:Ge/ChamberPlugLeft/TransY=0.0 cm
d:Ge/ChamberPlugLeft/TransZ=0.0 cm
b:Ge/ChamberPlugLeft/isParallel="True"
d:Ge/ChamberPlugLeft/RotX=-90 deg
s:Ge/ChamberPlugLeft/color="Orange"

s:Ge/ChamberPlugRight/Type="TsCylinder"
s:Ge/ChamberPlugRight/Parent="World"
s:Ge/ChamberPlugRight/Material="PMMA"
d:Ge/ChamberPlugRight/RMin=0.0 cm
d:Ge/ChamberPlugRight/RMax=0.655 cm
d:Ge/ChamberPlugRight/HL=5.0 cm
d:Ge/ChamberPlugRight/SPhi=0. deg
d:Ge/ChamberPlugRight/DPhi=360. deg
d:Ge/ChamberPlugRight/TransX=7.0 cm
d:Ge/ChamberPlugRight/TransY=0.0 cm
d:Ge/ChamberPlugRight/TransZ=0.0 cm
b:Ge/ChamberPlugRight/isParallel="True"
d:Ge/ChamberPlugRight/RotX=-90 deg
s:Ge/ChamberPlugRight/color="Brown"


##Scoring###########################################

#Scoringalongcylindricalaxis
s:Sc/ChamberPlugDose_tle/Quantity="TrackLengthEstimator"#Zbinningcausescreationofaparallelworldforscoring
s:Sc/ChamberPlugDose_tle/InputFile="Muen.dat"
s:Sc/ChamberPlugDose_tle/Component="ChamberPlugCentre"
s:Sc/ChamberPlugDose_tle/IfOutputFileAlreadyExists="Overwrite"
i:Sc/ChamberPlugDose_tle/ZBins=100#0.1 cm/bin1.0mm/bin

s:Sc/ChamberPlugDose_dtm/Quantity="DoseToMaterial"#Zbinningcausescreationofaparallelworldforscoring
s:Sc/ChamberPlugDose_dtm/Component="ChamberPlugCentre"
s:Sc/ChamberPlugDose_dtm/IfOutputFileAlreadyExists="Overwrite"
#i:Sc/ChamberPlugDose_dtm/ZBins=100#0.1 cm/bin1.0mm/bin
s:Sc/ChamberPlugDose_dtm/Material="Air"
b:Sc/ChamberPlugDose_dtm/PreCalculateStoppingPowerRatios ="True"

s:Sc/ChamberPlugDose_dtw/Quantity="DoseToWater"#Zbinningcausescreationofaparallelworldforscoring
s:Sc/ChamberPlugDose_dtw/Component="ChamberPlugCentre"
s:Sc/ChamberPlugDose_dtw/IfOutputFileAlreadyExists="Overwrite"
b:Sc/ChamberPlugDose_dtw/PreCalculateStoppingPowerRatios ="True"

s:Sc/ChamberPlugDose_tle/OutputFile="datafolder/Cntrhd_ChmbrPlgCntr_RMx_1p0bm_BmnglrSprdX_5p8bm_BmnglrSprdY_24p4ChamberPlug_tle"
s:Sc/ChamberPlugDose_dtm/OutputFile="datafolder/Cntrhd_ChmbrPlgCntr_RMx_1p0bm_BmnglrSprdX_5p8bm_BmnglrSprdY_24p4ChamberPlug_dtm"
s:Sc/ChamberPlugDose_dtw/OutputFile="datafolder/Cntrhd_ChmbrPlgCntr_RMx_1p0bm_BmnglrSprdX_5p8bm_BmnglrSprdY_24p4ChamberPlug_dtw"


#Physics############################################

#Usethisonlyforplacinggeometry-prototyping
#sv:Ph/Default/Modules=1"g4em-standard_opt0"

#defaultforwhenneedtoscore
s:Ph/ListName="Default"
b:Ph/ListProcesses="False"#Settruetodumplistofactivephysicsprocessestoconsole
s:Ph/Default/Type="Geant4_Modular"
sv:Ph/Default/Modules=6 "g4em-standard_opt4" "g4h-phy_QGSP_BIC_HP" "g4decay" "g4ion-binarycascade" "g4h-elastic_HP" "g4stopping"

#EMrangefromBrianHZapienCampos'MonteCarloModellingofthekVandMVImagingSystemsontheVarianTruebeamSTxLinac'
d:Ph/Default/EMRangeMin=100. eV
d:Ph/Default/EMRangeMax=521. MeV

#GroupComponent###########################################

#Activelyrotateimagingsystem
s:Ge/Rotation/Type="Group"
s:Ge/Rotation/Parent="World"
d:Ge/Rotation/RotX=0. deg
d:Ge/Rotation/RotY= Tf/Rotate/Value deg #Timefeatureddefinedbelow
d:Ge/Rotation/RotZ=0. deg
d:Ge/Rotation/TransX=0.0 cm
d:Ge/Rotation/TransY=0.0 cm
d:Ge/Rotation/TransZ=0.0 cm

#X-Ybladesgroup
s:Ge/CollimatorsVertical/Type="Group"
s:Ge/CollimatorsVertical/Parent="Rotation"
d:Ge/CollimatorsVertical/RotX=0. deg
d:Ge/CollimatorsVertical/RotY=0. deg
d:Ge/CollimatorsVertical/RotZ=0. deg
d:Ge/CollimatorsVertical/TransZ=9.3 cm + Ge/BeamPosition/TransZ #0.0745minfrontofsource-K.Sangroh

s:Ge/CollimatorsHorizontal/Type="Group"
s:Ge/CollimatorsHorizontal/Parent="CollimatorsVertical"
d:Ge/CollimatorsHorizontal/RotX=0. deg
d:Ge/CollimatorsHorizontal/RotY=0. deg
d:Ge/CollimatorsHorizontal/RotZ=0. deg
d:Ge/CollimatorsHorizontal/TransZ= 1.4 cm + Ge/Coll1/LY #preventgeometryoverlapwithvertical

#bowtiefiltergroupcomponent
s:Ge/BowtieFilter/Type="Group"
s:Ge/BowtieFilter/Parent="CollimatorsHorizontal"
d:Ge/BowtieFilter/RotX=0. deg
d:Ge/BowtieFilter/RotY=0. deg
d:Ge/BowtieFilter/RotZ=90. deg
d:Ge/BowtieFilter/TransX=0.0 cm
d:Ge/BowtieFilter/TransY=0.0 cm
d:Ge/BowtieFilter/TransZ=3.85 cm #preventgeometryoverlapwithvertical

#topcollimator
s:Ge/Coll1/Type="G4RTrap"
s:Ge/Coll1/Parent="CollimatorsVertical"
s:Ge/Coll1/Material="Lead"
d:Ge/Coll1/TransX=0 cm
d:Ge/Coll1/TransY=5.27 cm#5.197+0.07 cm#5.19sinceminimumb4overlap
d:Ge/Coll1/TransZ=0 cm
d:Ge/Coll1/RotX=-90. deg
d:Ge/Coll1/RotY=90. deg
d:Ge/Coll1/RotZ=0 deg
d:Ge/Coll1/LZ=12. cm
d:Ge/Coll1/LY=0.3 cm
d:Ge/Coll1/LX=10. cm
d:Ge/Coll1/LTX=9.2 cm
s:Ge/Coll1/Color="pink"

#bottomcollimator
s:Ge/Coll2/Type="G4RTrap"
s:Ge/Coll2/Parent="CollimatorsVertical"
s:Ge/Coll2/Material="Lead"
d:Ge/Coll2/TransX=0 cm
d:Ge/Coll2/TransY=-5.27 cm#5.267 cm
d:Ge/Coll2/TransZ=0 cm
d:Ge/Coll2/RotX=-90. deg
d:Ge/Coll2/RotY=270. deg
d:Ge/Coll2/RotZ=0 deg
d:Ge/Coll2/LZ=12. cm
d:Ge/Coll2/LY=0.3 cm
d:Ge/Coll2/LX=10. cm
d:Ge/Coll2/LTX=9.2 cm
s:Ge/Coll2/Color="pink"

#rightcollimator
s:Ge/Coll3/Type="G4RTrap"
s:Ge/Coll3/Parent="CollimatorsHorizontal"
s:Ge/Coll3/Material="Lead"
d:Ge/Coll3/TransX=5.27 cm#5.267 cm
d:Ge/Coll3/TransY=0. cm
d:Ge/Coll3/TransZ=0. cm
d:Ge/Coll3/RotX=-90. deg
d:Ge/Coll3/RotY=180. deg
d:Ge/Coll3/RotZ=0 deg
d:Ge/Coll3/LZ=12. cm
d:Ge/Coll3/LY=0.3 cm
d:Ge/Coll3/LX=10. cm
d:Ge/Coll3/LTX=9.2 cm
s:Ge/Coll3/Color="yellow"

#leftcollimator
s:Ge/Coll4/Type="G4RTrap"
s:Ge/Coll4/Parent="CollimatorsHorizontal"
s:Ge/Coll4/Material="Lead"
d:Ge/Coll4/TransX=-5.27 cm#-5.267 cm
d:Ge/Coll4/TransY=0. cm
d:Ge/Coll4/TransZ=0. cm
d:Ge/Coll4/RotX=-90. deg
d:Ge/Coll4/RotY=0. deg
d:Ge/Coll4/RotZ=0 deg
d:Ge/Coll4/LZ=12. cm
d:Ge/Coll4/LY=0.3 cm
d:Ge/Coll4/LX=10. cm
d:Ge/Coll4/LTX=9.2 cm
s:Ge/Coll4/Color="yellow"

#topcollimator
s:Ge/Coll1steel/Type="G4RTrap"
s:Ge/Coll1steel/Parent="CollimatorsVertical"
s:Ge/Coll1steel/Material="Steel"
d:Ge/Coll1steel/TransX=0 cm
#d:Ge/Coll1/TransY=5.205 cm#5.125+0.08 cm
d:Ge/Coll1steel/TransY=Ge/Coll1/TransY - 0.2 cm #5.27 cm#5.197+0.07 cm#5.19sinceminimumb4overlap
d:Ge/Coll1steel/TransZ=-0.25 cm #varian manual
d:Ge/Coll1steel/RotX=-90. deg
d:Ge/Coll1steel/RotY=90. deg
d:Ge/Coll1steel/RotZ=0 deg
d:Ge/Coll1steel/LZ=12. cm
d:Ge/Coll1steel/LY=0.2 cm
d:Ge/Coll1steel/LX=10. cm
d:Ge/Coll1steel/LTX=10. cm
s:Ge/Coll1steel/Color="pink"

#bottomcollimator
s:Ge/Coll2steel/Type="G4RTrap"
s:Ge/Coll2steel/Parent="CollimatorsVertical"
s:Ge/Coll2steel/Material="Steel"
d:Ge/Coll2steel/TransX=0 cm
d:Ge/Coll2steel/TransY=Ge/Coll2/TransY + 0.2 cm#5.267 cm
d:Ge/Coll2steel/TransZ=-0.25 cm #varian manual
d:Ge/Coll2steel/RotX=-90. deg
d:Ge/Coll2steel/RotY=270. deg
d:Ge/Coll2steel/RotZ=0 deg
d:Ge/Coll2steel/LZ=12. cm
d:Ge/Coll2steel/LY=0.2 cm
d:Ge/Coll2steel/LX=10. cm
d:Ge/Coll2steel/LTX=10. cm
s:Ge/Coll2steel/Color="pink"

#rightcollimator
s:Ge/Coll3steel/Type="G4RTrap"
s:Ge/Coll3steel/Parent="CollimatorsHorizontal"
s:Ge/Coll3steel/Material="Steel"
d:Ge/Coll3steel/TransX=Ge/Coll3/TransX - 0.2 cm#5.267 cm
d:Ge/Coll3steel/TransY=0. cm
d:Ge/Coll3steel/TransZ=-0.25 cm #varian manual
d:Ge/Coll3steel/RotX=-90. deg
d:Ge/Coll3steel/RotY=180. deg
d:Ge/Coll3steel/RotZ=0 deg
d:Ge/Coll3steel/LZ=12. cm
d:Ge/Coll3steel/LY=0.2 cm
d:Ge/Coll3steel/LX=10. cm
d:Ge/Coll3steel/LTX=10. cm
s:Ge/Coll3steel/Color="pink"

#leftcollimator
s:Ge/Coll4steel/Type="G4RTrap"
s:Ge/Coll4steel/Parent="CollimatorsHorizontal"
s:Ge/Coll4steel/Material="Steel"
d:Ge/Coll4steel/TransX=Ge/Coll4/TransX + 0.2 cm#-5.267 cm
d:Ge/Coll4steel/TransY=0. cm
d:Ge/Coll4steel/TransZ=-0.25 cm #varian manual
d:Ge/Coll4steel/RotX=-90. deg
d:Ge/Coll4steel/RotY=0. deg
d:Ge/Coll4steel/RotZ=0 deg
d:Ge/Coll4steel/LZ=12. cm
d:Ge/Coll4steel/LY=0.2 cm
d:Ge/Coll4steel/LX=10. cm
d:Ge/Coll4steel/LTX=10. cm
s:Ge/Coll4steel/Color="pink"

#Titaniumfilter
#Steelfiltergroup-filterexistinBrianHZCampospaperbutnotseeninTruebeamreferencepaper
#willcomparewithandwithouttoseethedifferenceitmakes
s:Ge/TitaniumFilterGroup/Type="Group"
s:Ge/TitaniumFilterGroup/Parent="CollimatorsHorizontal"
d:Ge/TitaniumFilterGroup/RotX=0. deg
d:Ge/TitaniumFilterGroup/RotY=0. deg
d:Ge/TitaniumFilterGroup/RotZ=0. deg
d:Ge/TitaniumFilterGroup/TransZ=1.59 cm #preventgeometryoverlapwithvertical

s:Ge/TitaniumFilter/Type="TsBox"
s:Ge/TitaniumFilter/Material="Titanium"
s:Ge/TitaniumFilter/Parent="TitaniumFilterGroup"
d:Ge/TitaniumFilter/HLX=10. cm
d:Ge/TitaniumFilter/HLY=10. cm
d:Ge/TitaniumFilter/HLZ=0.0445 cm

d:Ge/TitaniumFilter/TransX=0. cm
d:Ge/TitaniumFilter/TransY=0. cm
d:Ge/TitaniumFilter/TransZ=0. cm#topreventoverlapwithtopandbottomcollimator
d:Ge/TitaniumFilter/RotX=0. deg
d:Ge/TitaniumFilter/RotY=0. deg
d:Ge/TitaniumFilter/RotZ=0. deg
s:Ge/TitaniumFilter/Color="lightblue"
s:Ge/TitaniumFilter/DrawingStyle="WireFrame"

#bowtiefilter-thinpiece
s:Ge/DemoFlat/Type="TsBox"
s:Ge/DemoFlat/Material="Aluminum"
s:Ge/DemoFlat/Parent="BowtieFilter"
d:Ge/DemoFlat/HLX=0.1 cm
d:Ge/DemoFlat/HLY=0.4 cm
d:Ge/DemoFlat/HLZ=7.5 cm
d:Ge/DemoFlat/TransX=0.0 cm
d:Ge/DemoFlat/TransY=0. cm
d:Ge/DemoFlat/TransZ=0 cm
d:Ge/DemoFlat/RotX=0. deg
d:Ge/DemoFlat/RotY=-90. deg
d:Ge/DemoFlat/RotZ=0. deg
s:Ge/DemoFlat/Color="green"

#RTrap-RightAngularWedgeTrapezoid
s:Ge/DemoRTrap/Type="G4RTrap"
s:Ge/DemoRTrap/Parent="BowtieFilter"
s:Ge/DemoRTrap/Material="Aluminum"
d:Ge/DemoRTrap/TransX=0.0 cm
d:Ge/DemoRTrap/TransY=-2.5 cm - Ge/DemoFlat/HLY #paritallycoveringthefieldsizefromsecondarycollimator
#d:Ge/DemoRTrap/TransZ=35. cm
d:Ge/DemoRTrap/TransZ=0.65 cm #empiricallymatchedtobe14mm
d:Ge/DemoRTrap/RotX=0 deg
d:Ge/DemoRTrap/RotY=90 deg
d:Ge/DemoRTrap/RotZ=0. deg
d:Ge/DemoRTrap/LZ=15. cm
d:Ge/DemoRTrap/LY=5. cm
d:Ge/DemoRTrap/LX=2.8 cm
d:Ge/DemoRTrap/LTX=0.2 cm
s:Ge/DemoRTrap/Color="pink"

#RTrap-RightAngularWedgeTrapezoid-rotated180degree
s:Ge/DemoLTrap/Type="G4RTrap"
s:Ge/DemoLTrap/Parent="BowtieFilter"
s:Ge/DemoLTrap/Material="Aluminum"
d:Ge/DemoLTrap/TransX=0.0 cm
d:Ge/DemoLTrap/TransY=2.5 cm + Ge/DemoFlat/HLY #paritallycoveringthefieldsizefromsecondarycollimator
d:Ge/DemoLTrap/TransZ=0.65 cm#empiricallymatchedtobe14mm
d:Ge/DemoLTrap/RotX=180 deg
#d:Ge/DemoLTrap/RotY=90 deg
d:Ge/DemoLTrap/RotY=270 deg
d:Ge/DemoLTrap/RotZ=0. deg
d:Ge/DemoLTrap/LZ=15. cm
d:Ge/DemoLTrap/LY=5.0 cm
d:Ge/DemoLTrap/LX=2.8 cm
d:Ge/DemoLTrap/LTX=0.2 cm
s:Ge/DemoLTrap/Color="pink"

#bowtiefilter-topbox
s:Ge/topsidebox/Type="TsBox"
s:Ge/topsidebox/Material="Aluminum"
s:Ge/topsidebox/Parent="BowtieFilter"
d:Ge/topsidebox/HLX=1.4 cm
d:Ge/topsidebox/HLY=2.5 cm
d:Ge/topsidebox/HLZ=7.5 cm
d:Ge/topsidebox/TransX=0.0 cm
d:Ge/topsidebox/TransY=5.0 cm + Ge/DemoLTrap/TransY #85.mm
d:Ge/topsidebox/TransZ=1.3 cm
d:Ge/topsidebox/RotX=0. deg
d:Ge/topsidebox/RotY=-90. deg
d:Ge/topsidebox/RotZ=0. deg
s:Ge/topsidebox/Color="green"

#bowtiefilter-bottombox
s:Ge/bottomsidebox/Type="TsBox"
s:Ge/bottomsidebox/Material="Aluminum"
s:Ge/bottomsidebox/Parent="BowtieFilter"
d:Ge/bottomsidebox/HLX=1.4 cm
d:Ge/bottomsidebox/HLY=2.5 cm
d:Ge/bottomsidebox/HLZ=7.5 cm
d:Ge/bottomsidebox/TransX=0.0 cm
d:Ge/bottomsidebox/TransY=-5.0 cm + Ge/DemoRTrap/TransY #-85.mm
#d:Ge/bottomsidebox/TransZ=2.6 cm
d:Ge/bottomsidebox/TransZ=1.3 cm
d:Ge/bottomsidebox/RotX=0. deg
d:Ge/bottomsidebox/RotY=-90. deg
d:Ge/bottomsidebox/RotZ=0. deg
s:Ge/bottomsidebox/Color="green"

#couch
s:Ge/couch/Type="TsBox"
s:Ge/couch/Material="Aluminum"
s:Ge/couch/Parent="World"
d:Ge/couch/HLX=26.0 cm
d:Ge/couch/HLY=100.0 cm
d:Ge/couch/HLZ=0.075 cm
d:Ge/couch/TransX=0.0 cm
d:Ge/couch/TransY=0.0 cm
d:Ge/couch/TransZ=Ge/couch/HLZ + Ge/CTDI/RMax cm
s:Ge/couch/Color="red"

###########################################################
#Definebeamsource-conebeam
###########################################################
#Definelocatonofsourceingeometry##################
s:Ge/BeamPosition/Parent="Rotation"
s:Ge/BeamPosition/Type="Group"
d:Ge/BeamPosition/TransX=0. cm
d:Ge/BeamPosition/TransY=0. cm
#d:Ge/BeamPosition/TransZ=Ge/World/HLZ cm
d:Ge/BeamPosition/TransZ=-100. cm
d:Ge/BeamPosition/RotX=0. deg #originally180
d:Ge/BeamPosition/RotY=0. deg
d:Ge/BeamPosition/RotZ=0. deg
#spectrum-needinputfromspekpy
s:So/beam/BeamEnergySpectrumType="Continuous"
#s:So/beam/BeamEnergySpectrumType="None"#"Continuous"
#d:So/beam/BeamEnergy=169.23 MeV
s:So/beam/Type="Beam"#Beam,Isotropic,EmittanceorPhaseSpace
s:So/beam/Component="BeamPosition"
s:So/beam/BeamParticle="gamma"#'proton','gamma','e-''
s:So/beam/BeamPositionDistribution="Gaussian"#FlatorGaussian
s:So/beam/BeamPositionCutoffShape="Rectangle"#Point,Ellipse,RectangleorIsotropic
d:So/beam/BeamPositionCutoffX=5. cm #Xextentofposition(ifFlatorGaussian)#fromvarianpg.203
d:So/beam/BeamPositionCutoffY=5. cm #Yextentofposition(ifFlatorGaussian
d:So/beam/BeamPositionSpreadX=0.04246 cm #distribution(ifGaussian)
d:So/beam/BeamPositionSpreadY=0.04246 cm #distribution(ifGaussian)
s:So/beam/BeamAngularDistribution="Gaussian" #FlatorGaussian
d:So/beam/BeamAngularCutoffX=90 deg #Xcutoffofangulardistrib(ifFlatorGaussian)arctan(25/100)
d:So/beam/BeamAngularCutoffY=90 deg #Ycutoffofangulardistrib(ifFlatorGaussian)arctan(25/100)
d:So/beam/BeamAngularSpreadX=5.8 deg #Xangulardistribution(ifGaussian)
d:So/beam/BeamAngularSpreadY=24.4 deg #Yangulardistribution(ifGaussian)
#i:So/beam/NumberOfHistoriesInRun=25257086363570 #ActualtotalnumberofparticlesfromSpekPy(fluence*area)
i:So/beam/NumberOfHistoriesInRun=100000 #4000000#reducebyafactorof12566371fromtheactualparticlegivenbySpekPy.TobemultipliedbytheCTDIvaluetogetactualdosevalue
#i:So/beam/NumberOfHistoriesInRun=500000 #justforprototyping

#TimeFeature####################################

#eventuallyrunthis
#doesnotmakesensetorunthisforscoringPDDandbeamprofile

#fromtruebeamtechnicalreferenceguidevol.2imaging:pg.72fullfanscanarc200degree
#Declarethatthesimulationshouldcontain8runs.

#fullfanrotationrate
i:Tf/NumberOfSequentialTimes=501 #no.oftimesthissimulationwillreruneachtimewithparticles=numberofhistories
i:Tf/Verbosity=0 #Setverbosityhighertogetmoreinformation
d:Tf/TimelineEnd=501.0 s #Specifyanendtimefortherunsequence.
#ThefollowingfourparametersdefineaTimeFeaturewearecallingMyRotation.
s:Tf/Rotate/Function="Linear deg"
d:Tf/Rotate/Rate=0.4 deg/s #2degree/0.6s->time/rotation=TimelineEnd/totalno.ofangles
d:Tf/Rotate/StartValue=90.0 deg

#halffanrotationrate
#i:Tf/NumberOfSequentialTimes=60 #no.oftimesthissimulationwillreruneachtimewithparticles=numberofhistories
#i:Tf/Verbosity=2#Setverbosityhighertogetmoreinformation
#d:Tf/TimelineEnd=60.0s#Specifyanendtimefortherunsequence.
#ThefollowingfourparametersdefineaTimeFeaturewearecallingMyRotation.
#s:Tf/Rotate/Function="Linear deg"
#d:Tf/Rotate/Rate=6 deg/s#2degree/0.6s->time/rotation=TimelineEnd/totalno.ofangles
#d:Tf/Rotate/StartValue=0.0 deg


i:Ts/ShowHistoryCountAtInterval=100000

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
#Ts/UseQt="True"#ShowGUI#hashthislinetosuppressgui
#s:Gr/ViewA/Type="OpenGL"#Showsimulation#hashthislinetosuppressgui
#b:Gr/Enable="T"
b:Gr/Enable="F"
i:Gr/ViewA/WindowSizeX=1024
i:Gr/ViewA/WindowSizeY=768
#u:Gr/ViewA/Zoom=1.25
d:Gr/ViewA/Theta=-20.0 deg
d:Gr/ViewA/Phi=30.0 deg
b:Gr/ViewA/IncludeAxes="True"
d:Gr/ViewA/AxesSize=0.5 m
u:Gr/ViewA/Zoom=2e+01
b:Ts/ShowCPUTime="True"

