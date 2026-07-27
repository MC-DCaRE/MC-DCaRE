import sys
import os
from dataclasses import fields

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from src.config import (
    SimulationConfig,
    GeneralConfig,
    ImagingConfig,
    DicomConfig,
    CtdiConfig,
)


def test_imports_config_module() -> None:
    import src.config as config_module

    assert hasattr(config_module, "SimulationConfig")
    assert hasattr(config_module, "GeneralConfig")
    assert hasattr(config_module, "ImagingConfig")
    assert hasattr(config_module, "DicomConfig")
    assert hasattr(config_module, "CtdiConfig")


def test_simulation_config_can_be_instantiated() -> None:
    config = SimulationConfig()
    assert isinstance(config, SimulationConfig)
    assert isinstance(config.general, GeneralConfig)
    assert isinstance(config.imaging, ImagingConfig)
    assert isinstance(config.dicom, DicomConfig)
    assert isinstance(config.ctdi, CtdiConfig)


def test_defaults_returns_valid_config() -> None:
    config = SimulationConfig.defaults()
    assert isinstance(config, SimulationConfig)
    assert isinstance(config.general.g4_data_directory, str)
    assert isinstance(config.general.topas_directory, str)
    assert len(config.general.g4_data_directory) > 0
    assert len(config.general.topas_directory) > 0


def test_all_dataclass_fields_have_defaults() -> None:
    for dc_cls in [GeneralConfig, ImagingConfig, DicomConfig, CtdiConfig]:
        instance = dc_cls()
        for f in fields(dc_cls):
            val = getattr(instance, f.name)
            assert (
                val is not None
                or f.default is not None
                or f.default_factory is not None
            )
