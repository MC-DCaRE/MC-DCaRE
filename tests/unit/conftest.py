from __future__ import annotations

import sys
import os
from typing import Any

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.config import (
    CtdiConfig,
    DicomConfig,
    GeneralConfig,
    ImagingConfig,
    SimulationConfig,
)

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
    "includeFile = fullfan.txt\n"
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


def _make_config(**overrides: Any) -> SimulationConfig:
    general_kw: dict = {}
    imaging_kw: dict = {}
    dicom_kw: dict = {}
    ctdi_kw: dict = {}
    for k, v in overrides.items():
        if k in GeneralConfig.__dataclass_fields__:
            general_kw[k] = v
        elif k in ImagingConfig.__dataclass_fields__:
            imaging_kw[k] = v
        elif k in DicomConfig.__dataclass_fields__:
            dicom_kw[k] = v
        elif k in CtdiConfig.__dataclass_fields__:
            ctdi_kw[k] = v
    return SimulationConfig(
        general=GeneralConfig(**general_kw),
        imaging=ImagingConfig(**imaging_kw),
        dicom=DicomConfig(**dicom_kw),
        ctdi=CtdiConfig(**ctdi_kw),
    )


@pytest.fixture
def make_config() -> Any:
    return _make_config
