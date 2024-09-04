
# Models simple cone beam geometry
######################################################

## Include File ###############################
includeFile= ConvertedTopasFile_head.txt
#includeFile = HUtoMaterialSchneider.txt

## Some Control Parameters ####################
i:Ts/Seed=9 #startingrandomseed
i:Ts/NumberOfThreads=1 #NumberofCPUthreadstowhichworkwillbedistributed
#negativenumbermeansuseallbutthesenumberofthreads
#zeromeansuseall
s:Ts/G4DataDirectory="/home/leekh/G4Data"

##DefineWorldGeometry############################
d:Ge/World/HLX=1.2 m #HalfLength
d:Ge/World/HLY=1.2 m
d:Ge/World/HLZ=1.2 m

####################################
# Including DICOM file for patient #
####################################
s:Ge/Patient/Parent                                = "World"
s:Ge/Patient/Material                              = "G4_WATER"
s:Ge/Patient/Type                                  = "TsDicomPatient"
#s:Ge/Patient/HUtoMaterialConversionMethod          = "Schneider"
s:Ge/Patient/ImagingtoMaterialConverter            = "Schneider"
d:Ge/Patient/RotX                                  = -90. deg
#d:Ge/Patient/RotX                                  = 0. deg
d:Ge/Patient/RotY                                  = 0. deg
d:Ge/Patient/RotZ                                  = 0. deg
s:Ge/Patient/DicomDirectory                        = "cherylair" #"CherylPhantomCTDI" 
sv:Ge/Patient/DicomModalityTags                    = 1 "CT"
# sv:Ge/Patient/ColorByRTStructNames                 = 2 "Lung_R" "Lung_L"
# sv:Ge/Patient/ColorByRTStructColors                = 2 "Blue" "Red" 
s:Ge/Patient/Color                                 = "green"
#s:Ge/Patient/DrawingStyle                          = "Cloud"
b:Ge/Patient/IgnoreInconsistentFrameOfReferenceUID = "True"

#isocenter
d:Ge/IsocenterX   = 1.0  mm #1.0  mm  #r
d:Ge/IsocenterY   = -151.5 mm #i - s 
d:Ge/IsocenterZ   = 17.0 mm #17.22506896012784 mm  #p- a

dc:Ge/Patient/DicomOriginX = 0.0 mm
dc:Ge/Patient/DicomOriginY = 0.0 mm
dc:Ge/Patient/DicomOriginZ = 0.0 mm

d:Ge/Patient/TransX  = Ge/Patient/DicomOriginX - Ge/IsocenterX mm 
d:Ge/Patient/TransY  = Ge/Patient/DicomOriginY - Ge/IsocenterY mm
d:Ge/Patient/TransZ  = Ge/Patient/DicomOriginZ - Ge/IsocenterZ mm

#####################
# Dose calculation  #
#####################
#s:Sc/DoseOnRTGrid100kz17/Quantity                    = "DoseToMedium"
#s:Sc/DoseOnRTGrid100kz17/Component                   = "Patient"
##b:Sc/DoseOnRTGrid/ToConsole             = "T"
#s:Sc/DoseOnRTGrid100kz17/IfOutputFileAlreadyExists   = "Overwrite"
#s:Sc/DoseOnRTGrid100kz17/OutputType                  = "DICOM" 
#s:Sc/DoseOnRtGrid/OutputFile                  = "Dose_PTV"
#b:Sc/DoseOnRTGrid100kz17/DICOMOutput32BitsPerPixel   = "True"

s:Sc/DoseOnRTGrid_tle100kz17/Quantity="TrackLengthEstimator"#Zbinningcausescreationofaparallelworldforscoring
s:Sc/DoseOnRTGrid_tle100kz17/InputFile="Muen.dat"
s:Sc/DoseOnRTGrid_tle100kz17/Component="Patient"
s:Sc/DoseOnRTGrid_tle100kz17/IfOutputFileAlreadyExists="Overwrite"
i:Sc/DoseOnRTGrid_tle/ZBins=1 #0.1 cm/bin1.0mm/bin
b:Sc/DoseOnRTGrid_tle100kz17/DICOMOutput32BitsPerPixel   = "True"
s:Sc/DoseOnRTGrid_tle100kz17/OutputType                  = "DICOM" 
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
d:Ge/CollimatorsVertical/TransZ=11.7 cm + Ge/BeamPosition/TransZ #0.0745minfrontofsource-K.Sangroh

s:Ge/CollimatorsHorizontal/Type="Group"
s:Ge/CollimatorsHorizontal/Parent="CollimatorsVertical"
d:Ge/CollimatorsHorizontal/RotX=0. deg
d:Ge/CollimatorsHorizontal/RotY=0. deg
d:Ge/CollimatorsHorizontal/RotZ=0. deg
d:Ge/CollimatorsHorizontal/TransZ=1.4 cm + Ge/Coll1/LY #preventgeometryoverlapwithvertical

#Steelfiltergroup-filterexistinBrianHZCampospaperbutnotseeninTruebeamreferencepaper
#willcomparewithandwithouttoseethedifferenceitmakes

#bowtiefiltergroupcomponent
s:Ge/BowtieFilter/Type="Group"
s:Ge/BowtieFilter/Parent="CollimatorsHorizontal"
dc:Ge/BowtieFilter/RotX=0. deg
d:Ge/BowtieFilter/RotY=0. deg
d:Ge/BowtieFilter/RotZ=90. deg
d:Ge/BowtieFilter/TransX=0.0 cm
d:Ge/BowtieFilter/TransY=0.0 cm
d:Ge/BowtieFilter/TransZ=0.0385 m #preventgeometryoverlapwithvertical

#topcollimator
s:Ge/Coll1/Type="G4RTrap"
s:Ge/Coll1/Parent="CollimatorsVertical"
s:Ge/Coll1/Material="Lead"
dc:Ge/Coll1/TransX=0 cm
#dc:Ge/Coll1/TransY=5.205 cm#5.125+0.08 cm
dc:Ge/Coll1/TransY=5.81 cm #10.7cm#5.197+0.07 cm#5.19sinceminimumb4overlap
dc:Ge/Coll1/TransZ=0. cm
dc:Ge/Coll1/RotX=-90. deg
dc:Ge/Coll1/RotY=90. deg
dc:Ge/Coll1/RotZ=0 deg
dc:Ge/Coll1/LZ=120. mm
dc:Ge/Coll1/LY=3. mm
dc:Ge/Coll1/LX=100. mm
dc:Ge/Coll1/LTX=92. mm
s:Ge/Coll1/Color="red"

#bottomcollimator
s:Ge/Coll2/Type="G4RTrap"
s:Ge/Coll2/Parent="CollimatorsVertical"
s:Ge/Coll2/Material="Lead"
dc:Ge/Coll2/TransX=0 cm
dc:Ge/Coll2/TransY=-5.81 cm#5.267 cm
dc:Ge/Coll2/TransZ=0. cm
dc:Ge/Coll2/RotX=-90. deg
dc:Ge/Coll2/RotY=270. deg
dc:Ge/Coll2/RotZ=0 deg
dc:Ge/Coll2/LZ=120. mm
dc:Ge/Coll2/LY=3. mm
dc:Ge/Coll2/LX=100. mm
dc:Ge/Coll2/LTX=92. mm
s:Ge/Coll2/Color="red"

#rightcollimator
s:Ge/Coll3/Type="G4RTrap"
s:Ge/Coll3/Parent="CollimatorsHorizontal"
s:Ge/Coll3/Material="Lead"
dc:Ge/Coll3/TransX=6.01 cm#5.267 cm
dc:Ge/Coll3/TransY=0. cm
dc:Ge/Coll3/TransZ=0. cm
dc:Ge/Coll3/RotX=-90. deg
dc:Ge/Coll3/RotY=180. deg
dc:Ge/Coll3/RotZ=0 deg
dc:Ge/Coll3/LZ=120. mm
dc:Ge/Coll3/LY=3. mm
dc:Ge/Coll3/LX=100. mm
dc:Ge/Coll3/LTX=92. mm
s:Ge/Coll3/Color="red"

#leftcollimator
s:Ge/Coll4/Type="G4RTrap"
s:Ge/Coll4/Parent="CollimatorsHorizontal"
s:Ge/Coll4/Material="Lead"
dc:Ge/Coll4/TransX=-6.01 cm#-5.267 cm
dc:Ge/Coll4/TransY=0. cm
dc:Ge/Coll4/TransZ=0. cm
dc:Ge/Coll4/RotX=-90. deg
dc:Ge/Coll4/RotY=0. deg
dc:Ge/Coll4/RotZ=0 deg
dc:Ge/Coll4/LZ=120. mm
dc:Ge/Coll4/LY=3. mm
dc:Ge/Coll4/LX=100. mm
dc:Ge/Coll4/LTX=92. mm
s:Ge/Coll4/Color="red"


#topcollimator
s:Ge/Coll1steel/Type="G4RTrap"
s:Ge/Coll1steel/Parent="CollimatorsVertical"
s:Ge/Coll1steel/Material="Steel"
dc:Ge/Coll1steel/TransX=0 cm
#dc:Ge/Coll1/TransY=5.205 cm#5.125+0.08 cm
dc:Ge/Coll1steel/TransY=Ge/Coll1/TransY - 0.2 cm #5.27 cm#5.197+0.07 cm#5.19sinceminimumb4overlap
dc:Ge/Coll1steel/TransZ=-0.25 cm #varian manual
dc:Ge/Coll1steel/RotX=-90. deg
dc:Ge/Coll1steel/RotY=90. deg
dc:Ge/Coll1steel/RotZ=0 deg
dc:Ge/Coll1steel/LZ=120. mm
dc:Ge/Coll1steel/LY=2. mm
dc:Ge/Coll1steel/LX=100. mm
dc:Ge/Coll1steel/LTX=100. mm
s:Ge/Coll1steel/Color="pink"

#bottomcollimator
s:Ge/Coll2steel/Type="G4RTrap"
s:Ge/Coll2steel/Parent="CollimatorsVertical"
s:Ge/Coll2steel/Material="Steel"
dc:Ge/Coll2steel/TransX=0 cm
dc:Ge/Coll2steel/TransY=Ge/Coll2/TransY + 0.2 cm#5.267 cm
dc:Ge/Coll2steel/TransZ=-0.25 cm #varian manual
dc:Ge/Coll2steel/RotX=-90. deg
dc:Ge/Coll2steel/RotY=270. deg
dc:Ge/Coll2steel/RotZ=0 deg
dc:Ge/Coll2steel/LZ=120. mm
dc:Ge/Coll2steel/LY=2. mm
dc:Ge/Coll2steel/LX=100. mm
dc:Ge/Coll2steel/LTX=100. mm
s:Ge/Coll2steel/Color="pink"

#rightcollimator
s:Ge/Coll3steel/Type="G4RTrap"
s:Ge/Coll3steel/Parent="CollimatorsHorizontal"
s:Ge/Coll3steel/Material="Steel"
dc:Ge/Coll3steel/TransX=Ge/Coll3/TransX - 0.2 cm#5.267 cm
dc:Ge/Coll3steel/TransY=0. cm
dc:Ge/Coll3steel/TransZ=-0.25 cm #varian manual
dc:Ge/Coll3steel/RotX=-90. deg
dc:Ge/Coll3steel/RotY=180. deg
dc:Ge/Coll3steel/RotZ=0 deg
dc:Ge/Coll3steel/LZ=120. mm
dc:Ge/Coll3steel/LY=2. mm
dc:Ge/Coll3steel/LX=100. mm
dc:Ge/Coll3steel/LTX=100. mm
s:Ge/Coll3steel/Color="pink"

#leftcollimator
s:Ge/Coll4steel/Type="G4RTrap"
s:Ge/Coll4steel/Parent="CollimatorsHorizontal"
s:Ge/Coll4steel/Material="Steel"
dc:Ge/Coll4steel/TransX=Ge/Coll4/TransX + 0.2 cm#-5.267 cm
dc:Ge/Coll4steel/TransY=0. cm
dc:Ge/Coll4steel/TransZ=-0.25 cm #varian manual
dc:Ge/Coll4steel/RotX=-90. deg
dc:Ge/Coll4steel/RotY=0. deg
dc:Ge/Coll4steel/RotZ=0 deg
dc:Ge/Coll4steel/LZ=120. mm
dc:Ge/Coll4steel/LY=2. mm
dc:Ge/Coll4steel/LX=100. mm
dc:Ge/Coll4steel/LTX=100. mm
s:Ge/Coll4steel/Color="pink"

#steelfilter

#Steelfiltergroup-filterexistinBrianHZCampospaperbutnotseeninTruebeamreferencepaper
#willcomparewithandwithouttoseethedifferenceitmakes
# s:Ge/SteelFilterGroup/Type="Group"
# s:Ge/SteelFilterGroup/Parent="CollimatorsHorizontal"
# d:Ge/SteelFilterGroup/RotX=0. deg
# d:Ge/SteelFilterGroup/RotY=0. deg
# d:Ge/SteelFilterGroup/RotZ=0. deg
# d:Ge/SteelFilterGroup/TransZ=1.59 cm #preventgeometryoverlapwithvertical

# #steelfilter
# s:Ge/SteelFilter/Type="TsBox"
# s:Ge/SteelFilter/Material="Titanium"
# s:Ge/SteelFilter/Parent="SteelFilterGroup"
# d:Ge/SteelFilter/HLX=0.1 m
# d:Ge/SteelFilter/HLY=0.1 m
# d:Ge/SteelFilter/HLZ=0.001 mm
# d:Ge/SteelFilter/TransX=0. m
# d:Ge/SteelFilter/TransY=0. m
# d:Ge/SteelFilter/TransZ=0. m#topreventoverlapwithtopandbottomcollimator
# dc:Ge/SteelFilter/RotX=0. deg
# dc:Ge/SteelFilter/RotY=0. deg
# dc:Ge/SteelFilter/RotZ=0. deg
# s:Ge/SteelFilter/Color="lightblue"
# s:Ge/SteelFilter/DrawingStyle="WireFrame"

#bowtiefilter-thinpiece
s:Ge/DemoFlat/Type="TsBox"
s:Ge/DemoFlat/Material="Aluminum"
s:Ge/DemoFlat/Parent="BowtieFilter"
d:Ge/DemoFlat/HLX=1. mm
d:Ge/DemoFlat/HLY=1.7 mm
d:Ge/DemoFlat/HLZ=75. mm
d:Ge/DemoFlat/TransX=0.0 mm
d:Ge/DemoFlat/TransY=0. m
d:Ge/DemoFlat/TransZ=0.0 mm
d:Ge/DemoFlat/RotX=0. deg
d:Ge/DemoFlat/RotY=-90. deg
d:Ge/DemoFlat/RotZ=0. deg
s:Ge/DemoFlat/Color="green"

#RTrap-RightAngularWedgeTrapezoid
s:Ge/DemoRTrap/Type="G4RTrap"
s:Ge/DemoRTrap/Parent="BowtieFilter"
s:Ge/DemoRTrap/Material="Aluminum"
d:Ge/DemoRTrap/TransX=0.0 mm
d:Ge/DemoRTrap/TransY=-25.0 mm - Ge/DemoFlat/HLY #paritallycoveringthefieldsizefromsecondarycollimator
#d:Ge/DemoRTrap/TransZ=0.35 m
d:Ge/DemoRTrap/TransZ=6.5 mm #empiricallymatchedtobe14mm
d:Ge/DemoRTrap/RotX=0 deg
d:Ge/DemoRTrap/RotY=90 deg
d:Ge/DemoRTrap/RotZ=0. deg
dc:Ge/DemoRTrap/LZ=150. mm
dc:Ge/DemoRTrap/LY=50. mm
dc:Ge/DemoRTrap/LX=28. mm
dc:Ge/DemoRTrap/LTX=2. mm
s:Ge/DemoRTrap/Color="pink"

#RTrap-RightAngularWedgeTrapezoid-rotated180degree
s:Ge/DemoLTrap/Type="G4RTrap"
s:Ge/DemoLTrap/Parent="BowtieFilter"
s:Ge/DemoLTrap/Material="Aluminum"
d:Ge/DemoLTrap/TransX=0.0 mm
d:Ge/DemoLTrap/TransY=25.0 mm + Ge/DemoFlat/HLY #paritallycoveringthefieldsizefromsecondarycollimator
d:Ge/DemoLTrap/TransZ=6.5 mm#empiricallymatchedtobe14mm
d:Ge/DemoLTrap/RotX=180 deg
#d:Ge/DemoLTrap/RotY=90 deg
d:Ge/DemoLTrap/RotY=270 deg
d:Ge/DemoLTrap/RotZ=0. deg
d:Ge/DemoLTrap/LZ=150. mm
dc:Ge/DemoLTrap/LY=50. mm
dc:Ge/DemoLTrap/LX=28. mm
d:Ge/DemoLTrap/LTX=2. mm
s:Ge/DemoLTrap/Color="pink"

#bowtiefilter-topbox
s:Ge/topsidebox/Type="TsBox"
s:Ge/topsidebox/Material="Aluminum"
s:Ge/topsidebox/Parent="BowtieFilter"
d:Ge/topsidebox/HLX=14 mm
d:Ge/topsidebox/HLY=25 mm
d:Ge/topsidebox/HLZ=75. mm
d:Ge/topsidebox/TransX=0.0 mm
d:Ge/topsidebox/TransY=50. mm + Ge/DemoLTrap/TransY #85.mm
dc:Ge/topsidebox/TransZ=13 mm
d:Ge/topsidebox/RotX=0. deg
d:Ge/topsidebox/RotY=-90. deg
d:Ge/topsidebox/RotZ=0. deg
s:Ge/topsidebox/Color="green"

#bowtiefilter-bottombox
s:Ge/bottomsidebox/Type="TsBox"
s:Ge/bottomsidebox/Material="Aluminum"
s:Ge/bottomsidebox/Parent="BowtieFilter"
d:Ge/bottomsidebox/HLX=14 mm
d:Ge/bottomsidebox/HLY=25 mm
d:Ge/bottomsidebox/HLZ=75. mm
d:Ge/bottomsidebox/TransX=0.0 mm
d:Ge/bottomsidebox/TransY=-50. mm + Ge/DemoRTrap/TransY #-85.mm
#d:Ge/bottomsidebox/TransZ=26. mm
dc:Ge/bottomsidebox/TransZ=13 mm
dc:Ge/bottomsidebox/RotX=0. deg
d:Ge/bottomsidebox/RotY=-90. deg
d:Ge/bottomsidebox/RotZ=0. deg
s:Ge/bottomsidebox/Color="green"

#couch
# s:Ge/couch/Type="TsBox"
# s:Ge/couch/Material="Aluminum"
# s:Ge/couch/Parent="World"
# d:Ge/couch/HLX=260. mm
# d:Ge/couch/HLY=1000. mm
# d:Ge/couch/HLZ=0.40 mm
# d:Ge/couch/TransX=0.0 mm
# d:Ge/couch/TransY=0.0 mm
# d:Ge/couch/TransZ=Ge/couch/HLZ + Ge/CTDI/RMax mm
# s:Ge/couch/Color="red"

###########################################################
#Definebeamsource-conebeam
###########################################################
#Definelocatonofsourceingeometry##################
s:Ge/BeamPosition/Parent="Rotation"
s:Ge/BeamPosition/Type="Group"
d:Ge/BeamPosition/TransX=0. cm
d:Ge/BeamPosition/TransY=0. m
#d:Ge/BeamPosition/TransZ=Ge/World/HLZ m
d:Ge/BeamPosition/TransZ=-1. m
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
d:So/beam/BeamPositionSpreadX=0.4246 mm #distribution(ifGaussian)
d:So/beam/BeamPositionSpreadY=0.4246 mm #distribution(ifGaussian)
s:So/beam/BeamAngularDistribution="Gaussian" #FlatorGaussian
d:So/beam/BeamAngularCutoffX=90 deg #Xcutoffofangulardistrib(ifFlatorGaussian)arctan(25/100)
d:So/beam/BeamAngularCutoffY=90 deg #Ycutoffofangulardistrib(ifFlatorGaussian)arctan(25/100)
d:So/beam/BeamAngularSpreadX=5.8 deg #Xangulardistribution(ifGaussian)
d:So/beam/BeamAngularSpreadY=24.4 deg #Yangulardistribution(ifGaussian)
#i:So/beam/NumberOfHistoriesInRun=25257086363570 #ActualtotalnumberofparticlesfromSpekPy(fluence*area)

i:So/beam/NumberOfHistoriesInRun=10 #4000000#reducebyafactorof12566371fromtheactualparticlegivenbySpekPy.TobemultipliedbytheCTDIvaluetogetactualdosevalue
#i:So/beam/NumberOfHistoriesInRun=500000 #justforprototyping

#TimeFeature####################################

#eventuallyrunthis
#doesnotmakesensetorunthisforscoringPDDandbeamprofile

#fromtruebeamtechnicalreferenceguidevol.2imaging:pg.72fullfanscanarc200degree
#Declarethatthesimulationshouldcontain8runs.

#fullfanrotationrate
i:Tf/NumberOfSequentialTimes=50 #no.oftimesthissimulationwillreruneachtimewithparticles=numberofhistories
i:Tf/Verbosity=0 #Setverbosityhighertogetmoreinformation
d:Tf/TimelineEnd=501.0 s #Specifyanendtimefortherunsequence.
#ThefollowingfourparametersdefineaTimeFeaturewearecallingMyRotation.
s:Tf/Rotate/Function="Linear deg"
d:Tf/Rotate/Rate= -0.4 deg/s #2degree/0.6s->time/rotation=TimelineEnd/totalno.ofangles
d:Tf/Rotate/StartValue=290.0 deg
i:Ts/ShowHistoryCountAtInterval=100000
#halffanrotationrate
#i:Tf/NumberOfSequentialTimes=60 #no.oftimesthissimulationwillreruneachtimewithparticles=numberofhistories
#i:Tf/Verbosity=2#Setverbosityhighertogetmoreinformation
#d:Tf/TimelineEnd=60.0s#Specifyanendtimefortherunsequence.
#ThefollowingfourparametersdefineaTimeFeaturewearecallingMyRotation.
#s:Tf/Rotate/Function="Linear deg"
#d:Tf/Rotate/Rate=6 deg/s#2degree/0.6s->time/rotation=TimelineEnd/totalno.ofangles
#d:Tf/Rotate/StartValue=0.0 deg





# s:Ge/ChamberPlugTop/AssignToRegionNaMed = "targetregion"

# b:Vr/UseVarianceReduction = "true"
# s:Vr/ForcedInteraction/Type   = "ForcedInteraction"
# sv:Vr/ForcedInteraction/forregion/targetregion/processesNamed   = 2 "compt" "phot"
# dv:Vr/ForcedInteraction/ForRegion/targetregion/ForcedDistances  = 2 0.001 0.001 cm
# b:Vr/ForcedInteraction/ForRegion/targetregion/CorrectByWeight = "True"
# #halffan360
#fullfan200
#imagegentlyfullfan80kV
#headfullfan100kV
#spotlightfullfan125kV
#thorax/pelvishalffan125kV
#pelvislargehalffan140kV
#Asanadditionaldiagnostic,askforparameterstobeprintedoutateachrun:
#b:Ts/DumpNonDefaultParameters="True"

##Graphicsoutput###############################
# Ts/UseQt="True"#ShowGUI#hashthislinetosuppressgui
# s:Gr/ViewA/Type="OpenGL"#Showsimulation#hashthislinetosuppressgui
# b:Gr/Enable="T"
# b:Ph/ListProcesses = "True" # Set true to dump list of active physics processes to console
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

