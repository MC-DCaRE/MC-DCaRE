"""Tests for PCXMC runner module."""

import pytest
import numpy as np
from src.pcxmc_runner import PCXMCRunner


class TestPCXMCRunner:
    """Test cases for PCXMCRunner class."""
    
    def test_initialization(self):
        """Test runner initialization with config."""
        config = {
            'iso': np.array([0.0, 0.0]),
            'z': 0.0,
            'arms': 0,
            'kV': 120,
            'FRD': 100.0,
            'headScan': False,
            'startingAngle': 0.0,
            'finalAngle': 360.0,
            'numAnglesSimmed': 10,
            'numAnglesTrue': 10,
            'oblique': 0.0,
            'subFieldCoords': np.array([[0, 0], [0, 0]]),
            'subFieldWidths': np.array([5.0, 5.0]),
            'width': 20.0,
            'kerma': np.array([1.0, 1.0]),
            'filtration': np.array([1.0, 1.0]),
            'pWidth': 15.0,
            'pDepth': 15.0,
            'pHeadRadii2': 10.0,
            'height': 170.0,
            'mass': 70.0,
            'age': 30.0,
            'plotting': False,
            'interpolation': False,
            'resolutionScaling': False,
            'numSubFields': 2
        }
        
        runner = PCXMCRunner(config)
        assert runner.config == config
    
    def test_run_calculation_basic(self):
        """Test basic calculation run."""
        config = {
            'iso': np.array([0.0, 0.0]),
            'z': 0.0,
            'arms': 0,
            'kV': 120,
            'FRD': 100.0,
            'headScan': False,
            'startingAngle': 0.0,
            'finalAngle': 360.0,
            'numAnglesSimmed': 4,
            'numAnglesTrue': 4,
            'oblique': 0.0,
            'subFieldCoords': np.array([[0, 0], [0, 0]]),
            'subFieldWidths': np.array([5.0, 5.0]),
            'width': 20.0,
            'kerma': np.array([1.0, 1.0]),
            'filtration': np.array([1.0, 1.0]),
            'pWidth': 15.0,
            'pDepth': 15.0,
            'pHeadRadii2': 10.0,
            'height': 170.0,
            'mass': 70.0,
            'age': 30.0,
            'plotting': False,
            'interpolation': False,
            'resolutionScaling': False,
            'numSubFields': 2
        }
        
        runner = PCXMCRunner(config)
        results = runner.run()
        
        assert 'XCoordsFinal' in results
        assert 'YCoordsFinal' in results
        assert 'widthsFinal' in results
        assert 'anglesFinal' in results
        assert len(results['XCoordsFinal']) > 0
    
    def test_head_scan_calculation(self):
        """Test head scan calculation."""
        config = {
            'iso': np.array([-2.2, 1.2]),
            'z': 0.0,
            'arms': 0,
            'kV': 125,
            'FRD': 100.0,
            'headScan': True,
            'startingAngle': 0.0,
            'finalAngle': 360.0,
            'numAnglesSimmed': 8,
            'numAnglesTrue': 8,
            'oblique': 0.0,
            'subFieldCoords': np.array([[0, 0, 0], [-10, 0, 10]]),
            'subFieldWidths': np.array([4.0, 4.0, 4.0]),
            'width': 15.0,
            'kerma': np.array([0.2, 0.5, 1.0]),
            'filtration': np.array([0.2, 0.5, 1.0]),
            'pWidth': 8.0,
            'pDepth': 8.0,
            'pHeadRadii2': 10.0,
            'height': 175.0,
            'mass': 70.0,
            'age': 35.0,
            'plotting': False,
            'interpolation': False,
            'resolutionScaling': False,
            'numSubFields': 3
        }
        
        runner = PCXMCRunner(config)
        results = runner.run()
        
        assert len(results['XCoordsFinal']) == 24  # 8 angles * 3 sub-fields
    
    def test_resolution_scaling(self):
        """Test resolution scaling functionality."""
        config = {
            'iso': np.array([0.0, 0.0]),
            'z': 0.0,
            'arms': 0,
            'kV': 120,
            'FRD': 100.0,
            'headScan': False,
            'startingAngle': 0.0,
            'finalAngle': 360.0,
            'numAnglesSimmed': 5,
            'numAnglesTrue': 5,
            'oblique': 0.0,
            'subFieldCoords': np.array([[0, 0], [0, 0]]),
            'subFieldWidths': np.array([10.0, 10.0]),
            'width': 20.0,
            'kerma': np.array([1.0, 1.0]),
            'filtration': np.array([1.0, 1.0]),
            'pWidth': 15.0,
            'pDepth': 15.0,
            'pHeadRadii2': 10.0,
            'height': 170.0,
            'mass': 70.0,
            'age': 30.0,
            'plotting': False,
            'interpolation': True,
            'resolutionScaling': True,
            'numSubFields': 6
        }
        
        runner = PCXMCRunner(config)
        results = runner.run()
        
        # Should have 6 sub-fields instead of original 2
        assert len(results['XCoordsFinal']) == 30  # 5 angles * 6 sub-fields
    
    def test_invalid_config(self):
        """Test handling of invalid configuration."""
        with pytest.raises(KeyError):
            PCXMCRunner({})  # Empty config
    
    def test_geometry_calculation(self):
        """Test geometry calculations."""
        config = {
            'iso': np.array([1.0, 2.0]),
            'z': 0.0,
            'arms': 0,
            'kV': 120,
            'FRD': 100.0,
            'headScan': False,
            'startingAngle': 0.0,
            'finalAngle': 90.0,
            'numAnglesSimmed': 3,
            'numAnglesTrue': 3,
            'oblique': 0.0,
            'subFieldCoords': np.array([[0, 0], [0, 0]]),
            'subFieldWidths': np.array([5.0, 5.0]),
            'width': 20.0,
            'kerma': np.array([1.0, 1.0]),
            'filtration': np.array([1.0, 1.0]),
            'pWidth': 15.0,
            'pDepth': 15.0,
            'pHeadRadii2': 10.0,
            'height': 170.0,
            'mass': 70.0,
            'age': 30.0,
            'plotting': False,
            'interpolation': False,
            'resolutionScaling': False,
            'numSubFields': 2
        }
        
        runner = PCXMCRunner(config)
        results = runner.run()
        
        # Check that angles are properly calculated
        expected_angles = [0.0, 45.0, 90.0]
        np.testing.assert_array_almost_equal(
            results['anglesFinal'][:3], expected_angles, decimal=1
        )


if __name__ == "__main__":
    pytest.main([__file__])
