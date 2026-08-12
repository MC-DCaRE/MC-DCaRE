"""Main entry point for PCXMC Python implementation."""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
from .utils import wrap_to_360
from .pcxmc_runner import PCXMCRunner


def create_default_config() -> Dict[str, Any]:
    """Create default configuration matching MATLAB implementation."""
    return {
        # Phantom parameters
        'iso': np.array([-2.2, 1.2]),  # Isocentre coordinate (x,y)
        'z': 0.0,  # Sup-Inf offset (cm)
        'arms': 0,  # Binary value for arms inclusion
        'kV': 125,  # Tube voltage
        'FRD': 100.0,  # Distance from source to reference point (cm)
        'headScan': False,  # Head scan flag
        'startingAngle': 0.0,  # Starting gantry angle
        'finalAngle': 360.0,  # Final gantry angle
        'numAnglesSimmed': 360,  # Number of projections to simulate
        'numAnglesTrue': 360,  # Number of projections in actual scan
        'oblique': 0.0,  # Oblique angle flag
        
        # Sub-field configuration
        'subFieldCoords': np.array([
            [0, 0, 0, 0, 0, 0, 0],  # x coordinates
            [-15, -10, -5, 0, 5, 10, 15]  # y coordinates
        ]),
        'subFieldWidths': np.array([5, 5, 5, 5, 5, 5, 5]),
        'width': 20.6,  # Field width at isocentre (cm)
        'kerma': np.array([0.1, 0.2, 0.5, 1.0, 0.5, 0.2, 0.1]),  # Air kerma per projection (mGy)
        'filtration': np.array([0.1, 0.2, 0.5, 1.0, 0.5, 0.2, 0.1]),  # Total filtration (mm Al)
        
        # Phantom geometry
        'pWidth': 15.0,  # Phantom width (cm)
        'pDepth': 15.0,  # Phantom depth (cm)
        'pHeadRadii2': 13.0,  # Posterior head radius for head scans (cm)
        'height': 172.0,  # Phantom height (cm)
        'mass': 95.0,  # Phantom mass (kg)
        'age': 30.0,  # Phantom age (years)
        
        # Options
        'plotting': True,
        'interpolation': False,
        'resolutionScaling': False,
        'numSubFields': 11
    }


def main():
    """Main function demonstrating the PCXMC Python implementation."""
    print("PCXMC Python Implementation")
    print("=" * 40)
    
    # Create default configuration
    config = create_default_config()
    
    # Create runner
    runner = PCXMCRunner(config)
    
    # Run simulation
    print("Running simulation...")
    results = runner.run()
    
    # Display results
    print("\nSimulation Results:")
    print("-" * 20)
    print(f"Number of angles: {results['num_angles']}")
    print(f"Number of sub-fields: {results['num_sub_fields']}")
    print(f"Total data points: {len(results['XCoordsFinal'])}")
    
    # Export results
    print("\nResults ready for PCXMC input format")


if __name__ == "__main__":
    main()
