# PCXMC Python Implementation

A Python implementation of the PCXMC (PC-based Monte Carlo) dose calculation software, originally developed in MATLAB for calculating organ doses and effective dose from CT scans.

## Overview

This package provides a complete Python implementation of the PCXMC dose calculation methodology, ported from the original MATLAB code. It calculates organ doses and effective dose for patients undergoing CT examinations based on scan parameters and phantom geometry.

## Features

- **Complete dose calculation**: Calculates organ doses and effective dose
- **Flexible phantom modeling**: Supports adult, pediatric, and head phantoms
- **Sub-field calculation**: Handles complex field geometries with sub-field decomposition
- **CTDI metrics**: Calculates CTDI100, CTDIw, CTDIvol, and DLP
- **Validation**: Comprehensive test suite ensuring accuracy
- **Modern Python**: Clean, object-oriented design with type hints

## Installation

### From Source

```bash
git clone https://github.com/nsw-health/romp-pcxmc-py.git
cd pcxmc-py
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/nsw-health/romp-pcxmc-py.git
cd pcxmc-py
pip install -e ".[dev]"
```

## Quick Start

### Basic Usage

```python
from pcxmc_py import PCXMCRunner

# Create runner instance
runner = PCXMCRunner()

# Set scan parameters
runner.set_scan_parameters(
    kVp=120,           # Tube voltage (kVp)
    mAs=200,           # Tube current-time product (mAs)
    SID=50,            # Source-to-isocenter distance (cm)
    scan_length=30,    # Scan length (cm)
    slice_thickness=0.5,  # Slice thickness (cm)
    pitch=1.0,         # Pitch factor
    start_angle=0,     # Starting gantry angle (degrees)
    end_angle=360,     # Ending gantry angle (degrees)
    n_sub_fields=60    # Number of sub-fields
)

# Set phantom parameters
runner.set_phantom_parameters(
    phantom_type='adult',
    width=20,          # Phantom width (cm)
    depth=25,          # Phantom depth (cm)
    height=170         # Phantom height (cm)
)

# Set organ data
runner.set_organ_data(
    organ_names=['Brain', 'Thyroid', 'Lungs', 'Liver', 'Kidneys'],
    x_coords=[0, 0, 0, 0, 0],
    y_coords=[15, 10, 0, -5, -8],
    weights=[0.01, 0.04, 0.12, 0.04, 0.04]
)

# Run calculation
results = runner.run_calculation()

# Get summary
summary = runner.get_summary()
print(f"Effective Dose: {summary['effective_dose_mSv']:.2f} mSv")
print(f"CTDIvol: {summary['ctdi_vol_mGy']:.2f} mGy")
print(f"DLP: {summary['dlp_mGy_cm']:.2f} mGy·cm")
```

### Example Calculation

```python
from pcxmc_py import run_example_calculation

runner, results, summary = run_example_calculation()
print("PCXMC Calculation Results:")
print(f"Effective Dose: {summary['effective_dose_mSv']:.2f} mSv")
print(f"CTDI100: {summary['ctdi_100_mGy']:.2f} mGy")
print(f"CTDIw: {summary['ctdi_w_mGy']:.2f} mGy")
print(f"CTDIvol: {summary['ctdi_vol_mGy']:.2f} mGy")
print(f"DLP: {summary['dlp_mGy_cm']:.2f} mGy·cm")
```

## API Reference

### PCXMCRunner

The main class for running dose calculations.

#### Methods

- `set_scan_parameters(**kwargs)`: Set scan acquisition parameters
- `set_phantom_parameters(**kwargs)`: Set phantom geometry parameters
- `set_organ_data(**kwargs)`: Set organ positions and tissue weighting factors
- `run_calculation()`: Execute the dose calculation
- `get_summary()`: Get a summary of calculation results

### Geometry Module

- `within_ellipse(a, b, x, y)`: Check if point is within ellipse
- `rotate_point(x, y, angle)`: Rotate point by given angle
- `find_intersections(a, b, angle, X, Y)`: Find intersections between line and ellipse

### Dose Module

- `calculate_organ_dose()`: Calculate organ doses and effective dose
- `calculate_ctdi()`: Calculate CTDI metrics
- `calculate_dose_length_product()`: Calculate DLP

## Testing

Run the test suite:

```bash
pytest tests/
```

Run with coverage:

```bash
pytest tests/ --cov=src --cov-report=html
```

## Development

### Project Structure

```
pcxmc-py/
├── src/
│   ├── __init__.py
│   ├── main.py          # Main PCXMC runner
│   ├── geometry.py      # Geometric calculations
│   ├── fields.py        # Field calculations
│   ├── dose.py          # Dose calculations
│   └── utils.py         # Utility functions
├── tests/
│   ├── test_main.py
│   ├── test_geometry.py
│   └── ...
├── docs/
│   └── REFACTOR_PLAN.md
├── requirements.txt
├── setup.py
└── README.md
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run tests (`pytest tests/`)
6. Commit your changes (`git commit -am 'Add new feature'`)
7. Push to the branch (`git push origin feature/new-feature`)
8. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Original MATLAB implementation by Aaron Fetin, NSW Health ROMP
- Based on the PCXMC methodology developed by STUK (Radiation and Nuclear Safety Authority, Finland)

## References

1. Tapiovaara, M., Siiskonen, T. (2008). PCXMC 2.0 User's Guide. STUK-A231.
2. ICRP Publication 103 (2007). The 2007 Recommendations of the International Commission on Radiological Protection.
3. ICRP Publication 60 (1991). 1990 Recommendations of the International Commission on Radiological Protection.
