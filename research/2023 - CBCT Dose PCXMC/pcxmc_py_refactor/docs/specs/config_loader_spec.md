# ConfigLoader Module Specification

## Overview
The ConfigLoader module handles loading and validation of configuration files for the PCXMC simulation system. It supports both YAML and MATLAB formats, with YAML being the primary format.

## Class: ConfigLoader

### Purpose
Provides a unified interface for loading configuration files and converting them to the flat dictionary format expected by the PCXMC runner.

### Dependencies
- `yaml` (PyYAML package)
- `numpy` for array conversion
- `pathlib` for path handling

### Public Methods

#### load_config(cls, filepath: Union[str, Path]) -> Dict[str, Any]
**Description**: Main entry point for loading any supported configuration format.

**Parameters**:
- `filepath`: Path to configuration file (supports .yaml and .m extensions)

**Returns**:
- Flat dictionary containing all configuration parameters

**Raises**:
- `ValueError`: If file format is not supported
- `FileNotFoundError`: If file doesn't exist
- `yaml.YAMLError`: If YAML parsing fails

**Supported Formats**:
- YAML (.yaml, .yml)
- MATLAB (.m) - Basic support for simple structures

#### load_yaml_config(cls, filepath: Path) -> Dict[str, Any]
**Description**: Loads and processes YAML configuration files.

**Key Mapping**:
Converts nested YAML structure to flat dictionary with these mappings:

| YAML Key | Flat Dictionary Key |
|----------|---------------------|
| phantom_position.iso | iso |
| phantom_position.z | z |
| phantom_position.arms | arms |
| scan.kV | kV |
| scan.FRD | FRD |
| scan.headScan | headScan |
| scan.startingAngle | startingAngle |
| scan.finalAngle | finalAngle |
| scan.numAnglesSimmed | numAnglesSimmed |
| scan.numAnglesTrue | numAnglesTrue |
| scan.oblique | oblique |
| subfields.coordinates | subFieldCoords |
| subfields.widths | subFieldWidths |
| subfields.total_width | width |
| dose.kerma | kerma |
| dose.filtration | filtration |
| phantom.width | pWidth |
| phantom.depth | pDepth |
| phantom.head_radius2 | pHeadRadii2 |
| phantom.height | height |
| phantom.mass | mass |
| phantom.age | age |

**Array Handling**:
- All arrays are converted to numpy arrays
- Nested lists are flattened appropriately
- Missing optional keys are set to None

#### validate_config(cls, config: Dict[str, Any]) -> None
**Description**: Validates configuration parameters before simulation.

**Validation Rules**:
1. **Required Keys**: All keys in REQUIRED_KEYS must be present
2. **Positive Values**: kV and FRD must be positive
3. **Angle Range**: startingAngle must be ≤ finalAngle
4. **Array Dimensions**: subFieldCoords and subFieldWidths must have matching dimensions
5. **Numeric Types**: All numeric parameters must be convertible to float

**Required Keys**:
- iso
- z
- arms
- kV
- FRD
- headScan
- startingAngle
- finalAngle
- numAnglesSimmed
- numAnglesTrue
- oblique
- subFieldCoords
- subFieldWidths
- width
- kerma
- filtration
- pWidth
- pDepth
- height
- mass
- age

### Private Methods

#### _load_matlab_config(cls, filepath: Path) -> Dict[str, Any]
**Description**: Basic MATLAB file loader (placeholder for future implementation).

**Note**: Currently raises NotImplementedError. Future implementation will parse MATLAB structure arrays.

### Usage Examples

```python
from src.config_loader import ConfigLoader
from pathlib import Path

# Basic usage
config_loader = ConfigLoader()
config = config_loader.load_config("configs/demo_config.yaml")

# With Path object
config_path = Path("configs/custom_config.yaml")
config = config_loader.load_config(config_path)

# Validate configuration
try:
    ConfigLoader.validate_config(config)
    print("Configuration is valid")
except ValueError as e:
    print(f"Invalid configuration: {e}")
```

### Error Handling

#### File Errors
- **FileNotFoundError**: Raised when specified file doesn't exist
- **PermissionError**: Raised when file cannot be read due to permissions
- **IsADirectoryError**: Raised when path points to a directory

#### Format Errors
- **ValueError**: Raised for unsupported file extensions
- **yaml.YAMLError**: Raised for malformed YAML syntax
- **TypeError**: Raised when configuration values have incorrect types

#### Validation Errors
- **ValueError**: Raised with descriptive messages for:
  - Missing required keys
  - Invalid parameter ranges
  - Mismatched array dimensions
  - Non-numeric values where numbers expected

### Configuration File Format

#### YAML Structure
```yaml
phantom_position:
  iso: [0, 0, 0]    # Isocenter coordinates [x, y, z]
  z: 0.0            # Phantom z-position
  arms: "up"        # Arm position: "up" or "down"

scan:
  kV: 120           # Tube voltage in kV
  FRD: 100.0        # Focus-to-reference distance in cm
  headScan: false   # True for head scan, false for body scan
  startingAngle: 0.0    # Starting gantry angle in degrees
  finalAngle: 360.0     # Final gantry angle in degrees
  numAnglesSimmed: 360  # Number of angles to simulate
  numAnglesTrue: 360    # Actual number of angles
  oblique: false        # True for oblique scan

subfields:
  coordinates: [[-10, 10], [-5, 5]]  # Sub-field coordinates
  widths: [2.0, 3.0]                 # Sub-field widths
  total_width: 20.0                  # Total beam width

dose:
  kerma: [1.0, 1.5, 2.0]            # Kerma values
  filtration: [1.0, 1.0, 1.0]       # Filtration values

phantom:
  width: 40.0       # Phantom width in cm
  depth: 20.0       # Phantom depth in cm
  height: 170.0     # Phantom height in cm
  mass: 70.0        # Phantom mass in kg
  age: 30           # Phantom age in years
  head_radius2: 64.0  # Head radius squared (optional)
```

### Best Practices
1. Always validate configuration before running simulations
2. Use absolute paths for configuration files in production
3. Store sensitive parameters (like patient data) in separate files
4. Use YAML anchors for repeated values
5. Document any custom parameters in comments
