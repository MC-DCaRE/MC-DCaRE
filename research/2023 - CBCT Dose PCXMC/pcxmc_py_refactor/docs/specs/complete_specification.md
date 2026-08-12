# PCXMC Python Refactor - Complete Module Specifications

## Project Overview
This document provides comprehensive specifications for all modules in the PCXMC Python refactor project, which implements CBCT dose calculations based on the original MATLAB code.

## Module Specifications

### 1. config_loader.py
**Purpose**: Configuration loading and validation

**Class**: ConfigLoader
- **load_config(filepath)**: Load YAML or MATLAB config files
- **load_yaml_config(filepath)**: Load YAML configuration
- **load_matlab_config(filepath)**: Placeholder for MATLAB config (not implemented)
- **validate_config(config)**: Validate configuration structure

**Required Configuration Sections**:
- phantom_position: iso, z, arms
- scan: kV, FRD, headScan, startingAngle, finalAngle, numAnglesSimmed, numAnglesTrue, oblique
- subfields: coordinates, widths, total_width
- dose: kerma, filtration
- phantom: width, depth, height, mass, age

### 2. geometry.py
**Purpose**: Geometric calculations for phantom intersections

**Functions**:
- **find_intersections(a, b, angle, X, Y)**: Find line-ellipse intersections
- **within_ellipse(a, b, x, y)**: Check if point is within ellipse
- **rotate_point(x, y, angle_deg, center_x, center_y)**: Rotate points around center

### 3. interpolation.py
**Purpose**: Resolution scaling and interpolation

**Functions**:
- **res_scale(sub_coords, sub_widths, kerma, filtration, num_sub_fields)**: Scale resolution for sub-fields

### 4. utils.py
**Purpose**: Utility functions for trigonometric calculations

**Functions**:
- **sind(angle)**: Sine function for degrees
- **cosd(angle)**: Cosine function for degrees
- **wrap_to_360(angle)**: Wrap angles to 0-360 range

### 5. visualization.py
**Purpose**: Plotting and visualization functions

**Functions**:
- **plot_phantom_boundary(p_width, p_depth, head_scan, p_head_radii2, ax)**: Plot phantom outline
- **plot_subfields(X_coords, Y_coords, sub_field_widths, angles, nDI, ax, title)**: Plot sub-field positions
- **plot_comparison(...)**: Create side-by-side comparison plots
- **plot_kerma_distribution(...)**: Plot kerma values as heatmap
- **save_plots(...)**: Save multiple plot types to files

### 6. pcxmc_runner.py
**Purpose**: Main simulation orchestrator

**Class**: PCXMCRunner
- **run()**: Execute complete simulation
- **compute_gantry_angles()**: Calculate gantry angles
- **scale_resolution()**: Handle resolution scaling
- **calculate_subfield_coordinates()**: Compute sub-field positions
- **amend_subfields()**: Adjust sub-fields based on phantom geometry
- **save_results()**: Save results to file
- **plot_results()**: Generate visualizations

**Function**: run_pcxmc_simulation(config)
Convenience wrapper for running simulations

## Usage Workflow

### Basic Usage
```python
from src.config_loader import ConfigLoader
from src.pcxmc_runner import run_pcxmc_simulation

# Load configuration
config_loader = ConfigLoader()
config = config_loader.load_config("configs/demo_config.yaml")

# Run simulation
results = run_pcxmc_simulation(config)

# Save results
runner = PCXMCRunner(config)
runner.save_results(results, "outputs/simulation_results")
```

### Advanced Usage
```python
# Custom configuration
config = {
    'phantom_position': {
        'iso': [0, 0, 0],
        'z': 0,
        'arms': 1
    },
    'scan': {
        'kV': 120,
        'FRD': 100,
        'headScan': False,
        'startingAngle': 0,
        'finalAngle': 360,
        'numAnglesSimmed': 360,
        'numAnglesTrue': 360,
        'oblique': False
    },
    'subfields': {
        'coordinates': [[-10, 10], [0, 0]],
        'widths': [2, 2],
        'total_width': 20
    },
    'dose': {
        'kerma': [1.0, 1.0],
        'filtration': [0.1, 0.1]
    },
    'phantom': {
        'width': 20,
        'depth': 20,
        'height': 20,
        'mass': 70,
        'age': 30
    }
}

results = run_pcxmc_simulation(config)
```

## Error Handling
- Configuration validation with descriptive error messages
- Missing parameter detection
- Type checking for arrays and scalars
- File existence validation

## Output Formats
- **JSON**: Human-readable results with metadata
- **NPZ**: Efficient numpy array storage
- **PNG**: Visualization plots (comparison, kerma distribution)

## Dependencies
- numpy: Array operations and mathematical functions
- matplotlib: Plotting and visualization
- pyyaml: Configuration file parsing
- pathlib: File path handling

## File Structure
```
src/
├── config_loader.py    # Configuration management
├── geometry.py         # Geometric calculations
├── interpolation.py    # Resolution scaling
├── utils.py           # Utility functions
├── visualization.py   # Plotting functions
├── pcxmc_runner.py    # Main simulation engine
└── __init__.py        # Package initialization
