# PCXMC Runner Module Specification

## Overview
Main orchestrator for CBCT dose calculations using PCXMC methodology.

## Class: PCXMCRunner

### Constructor
```python
PCXMCRunner(config: Dict[str, Any])
```

### Key Methods

#### run() -> Dict[str, Any]
Executes complete simulation pipeline:
1. Computes gantry angles
2. Scales resolution if enabled
3. Calculates sub-field coordinates
4. Amends sub-fields based on phantom geometry
5. Returns final results

#### save_results(results: Dict[str, Any], filename: str)
Saves results to JSON and NPZ formats with metadata.

#### plot_results(results: Dict[str, Any], output_dir: str = None)
Generates comparison plots and kerma distribution visualizations.

### Configuration Requirements
- **Phantom**: pWidth, pDepth, height, mass, age
- **Scan**: kV, FRD, startingAngle, finalAngle, numAnglesSimmed
- **Geometry**: iso, z, arms, headScan
- **Sub-fields**: subFieldCoords, subFieldWidths, kerma, filtration

### Output Structure
```python
{
    'angles': np.ndarray,           # Gantry angles
    'num_angles': int,              # Number of angles
    'num_sub_fields': int,          # Number of sub-fields
    'XCoordsFinal': np.ndarray,     # Final X coordinates
    'YCoordsFinal': np.ndarray,     # Final Y coordinates
    'KermaFinal': np.ndarray,       # Final kerma values
    'FiltFinal': np.ndarray,        # Final filtration values
    'WidthFinal': np.ndarray        # Final widths
}
```

## Function: run_pcxmc_simulation
Convenience wrapper for PCXMCRunner.run()

## Usage Example
```python
from src.pcxmc_runner import run_pcxmc_simulation
from src.config_loader import ConfigLoader

config = ConfigLoader().load_config("configs/demo_config.yaml")
results = run_pcxmc_simulation(config)
