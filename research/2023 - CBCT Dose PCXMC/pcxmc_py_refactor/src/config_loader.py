"""Configuration loader for PCXMC Python implementation.

Handles loading and validation of configuration files in both MATLAB and YAML formats.
"""

import yaml
import numpy as np
from typing import Dict, Any, Union
from pathlib import Path

class ConfigLoader:
    """Load and validate PCXMC configuration files."""
    
    @classmethod
    def load_config(cls, filepath: Union[str, Path]) -> Dict[str, Any]:
        """Load configuration from YAML or MATLAB file.
        
        Args:
            filepath: Path to configuration file
            
        Returns:
            Dictionary containing configuration parameters
            
        Raises:
            ValueError: If file format is unsupported or config is invalid
        """
        path = Path(filepath)
        if path.suffix == '.yaml':
            return cls.load_yaml_config(path)
        elif path.suffix == '.m':
            return cls.load_matlab_config(path)
        else:
            raise ValueError(f"Unsupported config file format: {path.suffix}")

    @staticmethod
    def load_yaml_config(filepath: Path) -> Dict[str, Any]:
        """Load configuration from YAML file.
        
        Args:
            filepath: Path to YAML configuration file
            
        Returns:
            Dictionary containing configuration parameters in flat format
        """
        with open(filepath, 'r') as f:
            config = yaml.safe_load(f)
        
        # Flatten the nested structure and map keys
        flat_config = {}
        
        # Map phantom_position section
        if 'phantom_position' in config:
            flat_config['iso'] = np.array(config['phantom_position']['iso'])
            flat_config['z'] = config['phantom_position']['z']
            flat_config['arms'] = config['phantom_position']['arms']
        
        # Map scan section
        if 'scan' in config:
            scan = config['scan']
            flat_config['kV'] = scan['kV']
            flat_config['FRD'] = scan['FRD']
            flat_config['headScan'] = scan['headScan']
            flat_config['startingAngle'] = scan['startingAngle']
            flat_config['finalAngle'] = scan['finalAngle']
            flat_config['numAnglesSimmed'] = scan['numAnglesSimmed']
            flat_config['numAnglesTrue'] = scan['numAnglesTrue']
            flat_config['oblique'] = scan['oblique']
        
        # Map subfields section
        if 'subfields' in config:
            subfields = config['subfields']
            flat_config['subFieldCoords'] = np.array(subfields['coordinates'])
            flat_config['subFieldWidths'] = np.array(subfields['widths'])
            flat_config['width'] = subfields['total_width']
        
        # Map dose section
        if 'dose' in config:
            dose = config['dose']
            flat_config['kerma'] = np.array(dose['kerma'])
            flat_config['filtration'] = np.array(dose['filtration'])
        
        # Map phantom section
        if 'phantom' in config:
            phantom = config['phantom']
            flat_config['pWidth'] = phantom['width']
            flat_config['pDepth'] = phantom['depth']
            flat_config['pHeadRadii2'] = phantom.get('head_radius2', phantom['depth'])
            flat_config['height'] = phantom['height']
            flat_config['mass'] = phantom['mass']
            flat_config['age'] = phantom['age']
        
        # Map processing section (optional)
        if 'processing' in config:
            processing = config['processing']
            flat_config['plotting'] = processing.get('plotting', False)
            flat_config['interpolation'] = processing.get('interpolation', False)
            flat_config['resolutionScaling'] = processing.get('resolution_scaling', False)
            flat_config['numSubFields'] = processing.get('num_subfields_target', 11)
        
        return flat_config

    @staticmethod
    def load_matlab_config(filepath: Path) -> Dict[str, Any]:
        """Load configuration from MATLAB file.
        
        Args:
            filepath: Path to MATLAB configuration file
            
        Returns:
            Dictionary containing configuration parameters
            
        Note:
            This is a placeholder for MATLAB config parsing.
            Actual implementation would need to parse MATLAB syntax.
        """
        raise NotImplementedError("MATLAB config parsing not yet implemented")

    @classmethod
    def validate_config(cls, config: Dict[str, Any]) -> None:
        """Validate configuration structure and values.
        
        Args:
            config: Configuration dictionary to validate
            
        Raises:
            ValueError: If configuration is invalid
        """
        # Check all required keys exist in flat config
        required_keys = [
            'iso', 'z', 'arms', 'kV', 'FRD', 'headScan',
            'startingAngle', 'finalAngle', 'numAnglesSimmed',
            'numAnglesTrue', 'subFieldCoords', 'subFieldWidths',
            'width', 'kerma', 'filtration', 'pWidth', 'pDepth',
            'height', 'mass', 'age'
        ]
        
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required configuration key: {key}")

        # Validate specific value constraints
        if config['kV'] <= 0:
            raise ValueError("Tube voltage (kV) must be positive")
        
        if config['FRD'] <= 0:
            raise ValueError("Focus-to-reference distance must be positive")
            
        if config['startingAngle'] > config['finalAngle']:
            raise ValueError("Starting angle cannot be greater than final angle")
