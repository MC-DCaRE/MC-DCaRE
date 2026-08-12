# PCXMC Python Refactor - Technical Specifications

## Overview
This document provides detailed technical specifications for each module in the PCXMC Python refactor project. The specifications include file purposes, function inputs/outputs, and key algorithms.

## File Structure
```
src/
├── config_loader.py      # Configuration file loading and validation
├── geometry.py           # Geometric calculations and phantom modeling
├── interpolation.py      # Resolution scaling and interpolation
├── main.py               # Main entry point and CLI interface
├── pcxmc_runner.py       # Core PCXMC simulation engine
├── utils.py              # Utility functions and constants
├── visualization.py      # Plotting and visualization utilities
└── __init__.py           # Package initialization
```

---

## 1. config_loader.py

### Purpose
Handles loading and validation of configuration files in both YAML and MATLAB formats. Converts nested YAML structures to flat dictionaries expected by the PCXMC runner.

### Classes
#### ConfigLoader
**Purpose**: Main configuration loading class

**Methods**:
- `load_config(filepath: Union[str, Path]) -> Dict[str, Any]`
  - **Input**: File path to configuration file (.yaml or .m)
  - **Output**: Flat dictionary with all configuration parameters
  - **Raises**: ValueError for unsupported file formats

- `load_yaml_config(filepath: Path) -> Dict[str, Any]`
  - **Input**: Path to YAML configuration file
  - **Output**: Flat dictionary with mapped keys
  - **Key Mapping**:
    - `phantom_position.iso` → `iso`
    - `phantom_position.z` → `z`
    - `phantom_position.arms` → `arms`
    - `scan.kV` → `kV`
    - `scan.FRD` → `FRD`
    - `scan.headScan` → `headScan`
    - `subfields.coordinates` → `subFieldCoords`
    - `subfields.widths` → `subFieldWidths`
    - `subfields.total_width` → `width`
    - `dose.kerma` → `kerma`
    - `dose.filtration` → `filtration`
    - `phantom.width` → `pWidth`
    - `phantom.depth` → `pDepth`
    - `phantom.head_radius2` → `pHeadRadii2`
    - `phantom.height` → `height`
    - `phantom.mass` → `mass`
    - `phantom.age` → `age`

- `validate_config(config: Dict[str, Any]) -> None`
  - **Input**: Configuration dictionary
  - **Output**: None (raises ValueError if invalid)
  - **Validation Rules**:
    - All required keys must exist
    - kV must be positive
    - FRD must be positive
    - startingAngle must be ≤ finalAngle

---

## 2. geometry.py

### Purpose
Provides geometric calculations for phantom modeling, line-ellipse intersections, and coordinate transformations.

### Functions

#### find_intersections(a, b, angle, X, Y)
**Purpose**: Find intersection points between a line and an ellipse
- **Inputs**:
  - `a`: Semi-major axis of ellipse
  - `b`: Semi-minor axis of ellipse
  - `angle`: Angle of line in degrees
  - `X`: X-coordinate of line origin
  - `Y`: Y-coordinate of line origin
- **Output**: Tuple of (x_coords, y_coords) for intersection points
- **Algorithm**: Solves quadratic equation for line-ellipse intersection

#### within_ellipse(x, y, a, b)
**Purpose**: Check if point (x,y) lies within an ellipse
- **Inputs**:
  - `x, y`: Point coordinates
  - `a, b`: Semi-axes of ellipse
- **Output**: Boolean indicating if point is within ellipse
- **Algorithm**: Uses ellipse equation x²/a² + y²/b² ≤ 1

#### rotate_point(x, y, angle)
**Purpose**: Rotate a point around the origin
- **Inputs**:
  - `x, y`: Point coordinates
  - `angle`: Rotation angle in degrees
- **Output**: Tuple of (x_rotated, y_rotated)
- **Algorithm**: Uses rotation matrix transformation

---

## 3. interpolation.py

### Purpose
Handles resolution scaling and interpolation for dose calculations.

### Functions

#### res_scale(x, y, z, num_subfields_target)
**Purpose**: Rescale resolution for dose interpolation
- **Inputs**:
  - `x, y, z`: Input arrays to be rescaled
  - `num_subfields_target`: Target number of sub-fields
- **Output**: Tuple of rescaled (x, y, z) arrays
- **Algorithm**: Uses linear interpolation to achieve target resolution

---

## 4. main.py

### Purpose
Provides command-line interface for running PCXMC simulations.

### Functions

#### main()
**Purpose**: Entry point for CLI usage
- **Usage**: `python -m src.main [config_file]`
- **Arguments**:
  - `config_file`: Path to configuration file (optional, defaults to configs/demo_config.yaml)
- **Output**: Prints simulation results to console

---

## 5. pcxmc_runner.py

### Purpose
Core PCXMC simulation engine that calculates dose distributions for CBCT scans.

### Functions

#### run_pcxmc_simulation(config)
**Purpose**: Main simulation function
- **Input**: Configuration dictionary with all required parameters
- **Output**: Dictionary containing:
  - `num_angles`: Number of angles simulated
  - `num_sub_fields`: Number of sub-fields
  - `dose_distribution`: Calculated dose values
  - `phantom_geometry`: Phantom dimensions and positioning

#### calculate_dose_distribution(config)
**Purpose**: Calculate dose distribution across phantom
- **Input**: Configuration dictionary
- **Output**: 2D array of dose values
- **Algorithm**:
  1. Initialize phantom geometry
  2. Calculate beam parameters for each angle
  3. Compute intersection points with phantom
  4. Apply dose calculation algorithms
  5. Interpolate results to target resolution

#### validate_inputs(config)
**Purpose**: Validate all input parameters
- **Input**: Configuration dictionary
- **Output**: None (raises ValueError if invalid)
- **Validation**: Checks ranges, dimensions, and consistency

---

## 6. utils.py

### Purpose
Provides utility functions and mathematical operations.

### Functions

#### sind(angle)
**Purpose**: Calculate sine of angle in degrees
- **Input**: Angle in degrees
- **Output**: Sine value

#### cosd(angle)
**Purpose**: Calculate cosine of angle in degrees
- **Input**: Angle in degrees
- **Output**: Cosine value

#### wrap_to_360(angle)
**Purpose**: Wrap angle to 0-360 degree range
- **Input**: Angle in degrees (can be any value)
- **Output**: Angle wrapped to 0-360 degrees

---

## 7. visualization.py

### Purpose
Provides plotting and visualization capabilities for dose distributions.

### Functions

#### plot_dose_distribution(dose_data, phantom_geometry)
**Purpose**: Create 2D visualization of dose distribution
- **Inputs**:
  - `dose_data`: 2D array of dose values
  - `phantom_geometry`: Phantom dimensions and positioning
- **Output**: Matplotlib figure object
- **Features**:
  - Color-coded dose map
  - Phantom outline overlay
  - Color bar with dose units

#### plot_3d_dose(dose_data, phantom_geometry)
**Purpose**: Create 3D visualization of dose distribution
- **Inputs**:
  - `dose_data`: 3D array of dose values
  - `phantom_geometry`: Phantom dimensions and positioning
- **Output**: Matplotlib 3D figure object

---

## Configuration File Format

### YAML Structure
```yaml
phantom_position:
  iso: [x, y, z]  # Isocenter coordinates
  z: float        # Phantom z-position
  arms: str       # Arm position ("up" or "down")

scan:
  kV: int         # Tube voltage
  FRD: float      # Focus-to-reference distance
  headScan: bool  # Whether this is a head scan
  startingAngle: float  # Starting angle in degrees
  finalAngle: float     # Final angle in degrees
  numAnglesSimmed: int  # Number of angles to simulate
  numAnglesTrue: int    # Actual number of angles
  oblique: bool         # Whether scan is oblique

subfields:
  coordinates: [[x1, y1], [x2, y2], ...]  # Sub-field coordinates
  widths: [w1, w2, ...]                    # Sub-field widths
  total_width: float                        # Total beam width

dose:
  kerma: [k1, k2, ...]                     # Kerma values
  filtration: [f1, f2, ...]                # Filtration values

phantom:
  width: float      # Phantom width
  depth: float      # Phantom depth
  height: float     # Phantom height
  mass: float       # Phantom mass
  age: int          # Phantom age
  head_radius2: float  # Head radius squared (optional)

processing:
  plotting: bool            # Enable plotting
  interpolation: bool       # Enable interpolation
  resolution_scaling: bool  # Enable resolution scaling
  num_subfields_target: int # Target number of sub-fields
```

---

## Usage Examples

### Basic Usage
```python
from src.config_loader import ConfigLoader
from src.pcxmc_runner import run_pcxmc_simulation

# Load configuration
config_loader = ConfigLoader()
config = config_loader.load_config("configs/demo_config.yaml")

# Run simulation
results = run_pcxmc_simulation(config)

# Access results
print(f"Number of angles: {results['num_angles']}")
print(f"Number of sub-fields: {results['num_sub_fields']}")
```

### Command Line Usage
```bash
# Run with default config
python simple_demo.py

# Run with custom config
python -m src.main configs/custom_config.yaml
```

---

## Error Handling

### Configuration Errors
- Missing required keys raise ValueError with descriptive messages
- Invalid parameter ranges are validated before simulation
- File format errors provide clear guidance on expected formats

### Runtime Errors
- Geometric calculations handle edge cases (no intersections, etc.)
- Array dimension mismatches are caught and reported
- Memory issues are handled gracefully for large simulations
