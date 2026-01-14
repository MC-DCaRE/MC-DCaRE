# Config File Implementation - Quick Reference

## File Structure

```
src/mc_dcare/core/configuration/
├── __init__.py              # Package exports
├── base.py                  # Abstract base classes (IConfigSource, IConfigValidator)
├── models.py                # Pydantic domain models
├── loader.py                # Config file loading (YAML/JSON)
├── saver.py                 # Config file saving (YAML/JSON)
├── validator.py             # Validation logic
├── merger.py                # Config merging with defaults
├── defaults.py              # Default values (refactored from defaultvalues.py)
└── adapters.py              # Backward compatibility adapter
```

## Quick Start

### Load a Config File

```python
from src.mc_dcare.core.configuration.loader import ConfigLoader

# Load from YAML or JSON (auto-detect)
config = ConfigLoader.load_from_file("my_config.yaml")

# Access parameters
print(config.simulation.histories)  # 100000
print(config.imaging.voltage)       # 100.0
```

### Save a Config File

```python
from src.mc_dcare.core.configuration.saver import ConfigSaver
from src.mc_dcare.core.configuration.models import MCDCaREConfig

# Create config
config = MCDCaREConfig(
    simulation_type="DICOM",
    simulation={'histories': 50000}
)

# Save to YAML or JSON (auto-detect)
ConfigSaver.save_to_file(config, "output.yaml")
```

### Get Default Config

```python
from src.mc_dcare.core.configuration.defaults import get_default_config

config = get_default_config()
```

### Validate Config

```python
from src.mc_dcare.core.configuration.validator import ConfigValidator

config = ConfigLoader.load_from_file("my_config.yaml")
is_valid = ConfigValidator.validate(config)
```

### Merge with Defaults

```python
from src.mc_dcare.core.configuration.merger import ConfigMerger

user_config = {
    'simulation': {'histories': 50000},
    'imaging': {'voltage': 120.0}
}

merged = ConfigMerger.merge_with_defaults(user_config)
# User values override defaults
```

## Domain Models

### MCDCaREConfig (Root)

```python
from src.mc_dcare.core.configuration.models import MCDCaREConfig

config = MCDCaREConfig(
    simulation_type="DICOM",  # or "CTDI validation"
    simulation=SimulationConfig(...),
    imaging=ImagingConfig(...),
    dicom=DICOMConfig(...),  # Only for DICOM
    ctdi=CTDIConfig(...)      # Only for CTDI
)
```

### SimulationConfig

```python
from src.mc_dcare.core.configuration.models import SimulationConfig

sim_config = SimulationConfig(
    g4_data_directory="/path/to/G4Data",
    topas_directory="/path/to/topas/bin/topas",
    seed=9,
    threads=4,
    histories=100000
)
```

### ImagingConfig

```python
from src.mc_dcare.core.configuration.models import (
    ImagingConfig, ImagingMode, FanMode, RotationDirection
)

img_config = ImagingConfig(
    mode=ImagingMode.HEAD,  # Enum: IMAGE_GENTLY, HEAD, THORAX, etc.
    fan_mode=FanMode.FULL_FAN,  # Enum: FULL_FAN, HALF_FAN
    rotation_direction=RotationDirection.CBCT_CLOCKWISE,
    start_angle=0.0,  # degrees, -360 to 360
    voltage=100.0,  # kVp
    exposure=100.0  # mAs
)
```

### DICOMConfig

```python
from src.mc_dcare.core.configuration.models import DICOMConfig

dicom_config = DICOMConfig(
    directory="/path/to/dicom",
    rp_file="/path/to/RTPlan.dcm",
    patient_id=None,  # Auto-populated from DICOM
    translation_x="0. mm",
    translation_y="0. mm",
    translation_z="0. mm",
    rotation_yaw="0. deg",
    isocenter_x="0. mm",
    isocenter_y="0. mm",
    isocenter_z="0. mm"
)
```

### CTDIConfig

```python
from src.mc_dcare.core.configuration.models import CTDIConfig

ctdi_config = CTDIConfig(
    phantom_size="16 cm",  # or "32 cm"
    couch_enabled=True,
    couch_hlx="260. mm",
    couch_hly="0.4 mm",
    couch_hlz="1000. mm",
    dtm_zbins=100,
    tle_zbins=100,
    dtw_zbins=100,
    user_blade_enabled=False
)
```

## Config File Format (YAML)

### DICOM Example

```yaml
simulation_type: "DICOM"

simulation:
  g4_data_directory: "/path/to/G4Data"
  topas_directory: "/path/to/topas/bin/topas"
  seed: 9
  threads: 4
  histories: 100000

imaging:
  mode: "Head"
  fan_mode: "Full Fan"
  rotation_direction: "CBCT Clockwise"
  start_angle: 0.0
  voltage: 100.0
  exposure: 100.0

dicom:
  directory: "/path/to/dicom"
  rp_file: "/path/to/RTPlan.dcm"
  translation_x: "0. mm"
  translation_y: "0. mm"
  translation_z: "0. mm"
  rotation_yaw: "0. deg"
  isocenter_x: "0. mm"
  isocenter_y: "0. mm"
  isocenter_z: "0. mm"
```

### CTDI Example

```yaml
simulation_type: "CTDI validation"

simulation:
  g4_data_directory: "/path/to/G4Data"
  topas_directory: "/path/to/topas/bin/topas"
  seed: 9
  threads: 4
  histories: 100000

imaging:
  mode: "Head"
  fan_mode: "Full Fan"
  rotation_direction: "CBCT Clockwise"
  start_angle: 0.0
  voltage: 100.0
  exposure: 100.0

ctdi:
  phantom_size: "16 cm"
  couch_enabled: true
  couch_hlx: "260. mm"
  couch_hly: "0.4 mm"
  couch_hlz: "1000. mm"
  dtm_zbins: 100
  tle_zbins: 100
  dtw_zbins: 100
  user_blade_enabled: false
```

## Backward Compatibility

### Convert Old Dict to Config

```python
from src.mc_dcare.core.configuration.adapters import ConfigAdapter

old_values = {
    '-FUNCTION_CHECK-': 'DICOM',
    '-SEED-': '42',
    '-HIST-': '50000',
}

# This will raise a DeprecationWarning
config = ConfigAdapter.dict_to_config(old_values)
```

### Convert Config to Old Dict

```python
from src.mc_dcare.core.configuration.adapters import ConfigAdapter

config = MCDCaREConfig(simulation={'seed': 42})

# This will raise a DeprecationWarning
values = ConfigAdapter.config_to_dict(values)
```

## CLI Usage

### Validate Config

```bash
python -m src.mc_dcare.cli.config_cli validate my_config.yaml
```

### Convert Formats

```bash
# YAML to JSON
python -m src.mc_dcare.cli.config_cli convert config.yaml config.json

# JSON to YAML
python -m src.mc_dcare.cli.config_cli convert config.json config.yaml
```

### Generate Default Config

```bash
# DICOM default
python -m src.mc_dcare.cli.config_cli generate default.yaml --type dicom

# CTDI default
python -m src.mc_dcare.cli.config_cli generate default.yaml --type ctdi
```

## Common Patterns

### Pattern 1: Load, Modify, Save

```python
from src.mc_dcare.core.configuration.loader import ConfigLoader
from src.mc_dcare.core.configuration.saver import ConfigSaver

# Load
config = ConfigLoader.load_from_file("template.yaml")

# Modify
config.simulation.histories = 200000
config.imaging.voltage = 120.0

# Save
ConfigSaver.save_to_file(config, "custom_config.yaml")
```

### Pattern 2: Validate Before Use

```python
from src.mc_dcare.core.configuration.loader import ConfigLoader
from src.mc_dcare.core.configuration.validator import ConfigValidator

try:
    config = ConfigLoader.load_from_file("config.yaml")
    ConfigValidator.validate(config)
    print("Config is valid!")
except ValueError as e:
    print(f"Validation error: {e}")
```

### Pattern 3: Merge User Config with Defaults

```python
from src.mc_dcare.core.configuration.merger import ConfigMerger

# User provides only what they want to change
user_config = {
    'simulation': {'histories': 50000},
    'imaging': {'voltage': 120.0}
}

# Get full config with defaults
config = ConfigMerger.merge_with_defaults(user_config)

# All other parameters have default values
print(config.simulation.seed)  # 9 (default)
print(config.simulation.histories)  # 50000 (user)
```

## Validation Rules

### Simulation Config
- `seed`: Must be >= 0
- `threads`: Must be >= 1
- `histories`: Must be >= 1

### Imaging Config
- `start_angle`: Must be between -360 and 360 degrees
- `voltage`: Must be >= 0
- `exposure`: Must be >= 0

### CTDI Config
- `phantom_size`: Must be "16 cm" or "32 cm"
- `dtm_zbins`, `tle_zbins`, `dtw_zbins`: Must be >= 1

### Consistency Validation
- DICOM simulation cannot have CTDI config
- CTDI simulation cannot have DICOM config

## Error Handling

### FileNotFoundError

```python
from src.mc_dcare.core.configuration.loader import ConfigLoader

try:
    config = ConfigLoader.load_from_file("nonexistent.yaml")
except FileNotFoundError as e:
    print(f"Config file not found: {e}")
```

### ValidationError

```python
from src.mc_dcare.core.configuration.models import SimulationConfig

try:
    config = SimulationConfig(threads=-1)  # Invalid!
except ValueError as e:
    print(f"Validation error: {e}")
```

### UnsupportedFormatError

```python
from src.mc_dcare.core.configuration.loader import ConfigLoader

try:
    config = ConfigLoader.load_from_file("config.txt")  # Unsupported!
except ValueError as e:
    print(f"Unsupported format: {e}")
```

## Migration from Old Code

### Before

```python
from src.defaultvalues import default_Seed, default_Histories

seed = default_Seed  # 9
histories = default_Histories  # 100000
```

### After

```python
from src.mc_dcare.core.configuration.defaults import get_default_config

config = get_default_config()
seed = config.simulation.seed  # 9
histories = config.simulation.histories  # 100000
```

## Testing

### Unit Test Example

```python
import pytest
from src.mc_dcare.core.configuration.models import SimulationConfig

def test_simulation_config_validation():
    # Valid config
    config = SimulationConfig(seed=42, threads=4, histories=100000)
    assert config.seed == 42
    
    # Invalid config
    with pytest.raises(ValueError):
        SimulationConfig(threads=-1)
```

### Integration Test Example

```python
from pathlib import Path
from src.mc_dcare.core.configuration.loader import ConfigLoader
from src.mc_dcare.core.configuration.saver import ConfigSaver
from src.mc_dcare.core.configuration.models import MCDCaREConfig

def test_roundtrip():
    original = MCDCaREConfig(simulation={'histories': 50000})
    
    # Save
    test_file = Path("test_config.yaml")
    ConfigSaver.save_to_file(original, test_file)
    
    # Load
    loaded = ConfigLoader.load_from_file(test_file)
    
    # Verify
    assert loaded.simulation.histories == 50000
    
    # Cleanup
    test_file.unlink()
```

## Performance Notes

- Config loading: < 100ms for typical files
- Validation: < 50ms for typical configs
- No runtime overhead during simulation

## Dependencies

- `pydantic`: Data validation and settings management
- `pyyaml`: YAML support
- (No additional dependencies for JSON)

## Next Steps

1. Read full implementation plan: [`config_file_implementation_plan.md`](config_file_implementation_plan.md)
2. Review architecture: [`config_architecture_overview.md`](config_architecture_overview.md)
3. Check examples in `examples/config/`
4. Run CLI: `python -m src.mc_dcare.cli.config_cli --help`
