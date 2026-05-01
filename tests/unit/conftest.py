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
