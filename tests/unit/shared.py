from __future__ import annotations

MAIN_FILE_CONTENT: str = (
    's:Ts/G4DataDirectory = "/root/G4Data"\n'
    'i:Tf/NumberOfSequentialTimes = "1000"\n'
    'd:Tf/TimelineEnd = "501.0 s"\n'
    'd:Tf/Rotate/Rate = "0.4 deg/s"\n'
    'd:Tf/Rotate/StartValue = "0 deg"\n'
    'i:Ts/Seed = "9"\n'
    'i:Ts/NumberOfThreads = "1"\n'
    'i:So/beam/NumberOfHistoriesInRun = "100000"\n'
    'dc:Ge/Coll1/TransY = "6.175536078965273 cm"\n'
    'dc:Ge/Coll2/TransY = "-6.175536078965273 cm"\n'
    'dc:Ge/Coll3/TransX = "5.814471115800571 cm"\n'
    'dc:Ge/Coll4/TransX = "-5.814471115800571 cm"\n'
    "includeFile = halffan.txt\n"
    "includeFile = CTDIphantom_16.txt\n"
    "includeFile = CTDIphantom_32.txt\n"
    'sv:Ph/Default/LayeredMassGeometryWorlds = "some value"\n'
    'Ts/UseQt = "true"\n'
    's:Gr/ViewA/Type = "some type"\n'
    'b:Gr/Enable = "true"\n'
    "includeFile = patientDICOM.txt\n"
)

DICOM_SUB_FILE_CONTENT: str = (
    'd:Ge/patrotation/yaw = "0. deg"\n'
    's:Ge/Patient/DicomDirectory = "/sampledicom/setA"\n'
    'dc:Ge/IsocenterX = "0 mm"\n'
    'dc:Ge/IsocenterY = "0 mm"\n'
    'dc:Ge/IsocenterZ = "0 mm"\n'
    'dc:Ge/Patient/UserTransX = "0. mm"\n'
    'dc:Ge/Patient/UserTransY = "0. mm"\n'
    'dc:Ge/Patient/UserTransZ = "0. mm"\n'
    's:Sc/DoseOnRTGrid100kz17/OutputFile = "output"\n'
)

CTDI_SUB_FILE_CONTENT: str = (
    's:Ge/couch/Parent="couchgroup"\n'
    "d:Ge/couch/HLX=260. mm\n"
    "d:Ge/couch/HLY= 0.4 mm\n"
    "d:Ge/couch/HLZ= 1000 mm\n"
    "i:Sc/ChamberPlugDose_dtm/ZBins=100\n"
    "i:Sc/ChamberPlugDose_tle/ZBins=100\n"
    "i:Sc/ChamberPlugDose_dtw/ZBins=100\n"
)
