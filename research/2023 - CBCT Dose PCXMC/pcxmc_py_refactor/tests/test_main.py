"""Tests for main PCXMC runner."""

import pytest
import numpy as np
from src.main import PCXMCRunner, run_example_calculation


class TestPCXMCRunner:
    """Test cases for PCXMCRunner class."""
    
    def test_initialization(self):
        """Test runner initialization."""
        runner = PCXMCRunner()
        assert runner.scan_parameters == {}
        assert runner.phantom_parameters == {}
        assert runner.organ_data == {}
        assert runner.results == {}
    
    def test_set_scan_parameters(self):
        """Test setting scan parameters."""
        runner = PCXMCRunner()
        runner.set_scan_parameters(
            kVp=120, mAs=200, SID=50, scan_length=30,
            slice_thickness=0.5, pitch=1.0, start_angle=0,
            end_angle=360, n_sub_fields=60
        )
        
        expected = {
            'kVp': 120, 'mAs': 200, 'SID': 50, 'scan_length': 30,
            'slice_thickness': 0.5, 'pitch': 1.0, 'start_angle': 0,
            'end_angle': 360, 'n_sub_fields': 60
        }
        assert runner.scan_parameters == expected
    
    def test_set_phantom_parameters(self):
        """Test setting phantom parameters."""
        runner = PCXMCRunner()
        runner.set_phantom_parameters(
            phantom_type='adult', width=20, depth=25, height=170
        )
        
        expected = {
            'phantom_type': 'adult', 'width': 20, 'depth': 25,
            'height': 170, 'head_radii2': None
        }
        assert runner.phantom_parameters == expected
    
    def test_set_organ_data(self):
        """Test setting organ data."""
        runner = PCXMCRunner()
        organ_names = ['Brain', 'Thyroid']
        x_coords = [0, 0]
        y_coords = [15, 10]
        weights = [0.01, 0.04]
        
        runner.set_organ_data(organ_names, x_coords, y_coords, weights)
        
        assert runner.organ_data['names'] == organ_names
        np.testing.assert_array_equal(runner.organ_data['x_coords'], [0, 0])
        np.testing.assert_array_equal(runner.organ_data['y_coords'], [15, 10])
        np.testing.assert_array_equal(runner.organ_data['weights'], [0.01, 0.04])
    
    def test_generate_sub_fields(self):
        """Test sub-field generation."""
        runner = PCXMCRunner()
        runner.set_scan_parameters(
            kVp=120, mAs=200, SID=50, scan_length=30,
            slice_thickness=0.5, pitch=1.0, start_angle=0,
            end_angle=360, n_sub_fields=4
        )
        
        X_coords, Y_coords, widths, angles = runner.generate_sub_fields()
        
        assert len(X_coords) == 4
        assert len(Y_coords) == 4
        assert len(widths) == 4
        assert len(angles) == 4
        
        # Check Y coordinates are evenly spaced
        expected_y = np.array([-15, -5, 5, 15])
        np.testing.assert_array_almost_equal(Y_coords, expected_y)
        
        # Check angles are evenly spaced
        expected_angles = np.array([0, 120, 240, 360])
        np.testing.assert_array_almost_equal(angles, expected_angles)
    
    def test_run_calculation_missing_parameters(self):
        """Test that calculation fails with missing parameters."""
        runner = PCXMCRunner()
        
        with pytest.raises(ValueError, match="Scan parameters not set"):
            runner.run_calculation()
        
        runner.set_scan_parameters(
            kVp=120, mAs=200, SID=50, scan_length=30,
            slice_thickness=0.5, pitch=1.0, start_angle=0,
            end_angle=360, n_sub_fields=4
        )
        
        with pytest.raises(ValueError, match="Phantom parameters not set"):
            runner.run_calculation()
        
        runner.set_phantom_parameters(
            phantom_type='adult', width=20, depth=25
        )
        
        with pytest.raises(ValueError, match="Organ data not set"):
            runner.run_calculation()
    
    def test_run_calculation_complete(self):
        """Test complete calculation run."""
        runner = PCXMCRunner()
        
        # Set minimal parameters for calculation
        runner.set_scan_parameters(
            kVp=120, mAs=200, SID=50, scan_length=10,
            slice_thickness=1.0, pitch=1.0, start_angle=0,
            end_angle=360, n_sub_fields=4
        )
        
        runner.set_phantom_parameters(
            phantom_type='adult', width=20, depth=25
        )
        
        runner.set_organ_data(
            organ_names=['Test'],
            x_coords=[0],
            y_coords=[0],
            weights=[0.01]
        )
        
        results = runner.run_calculation()
        
        assert 'field_data' in results
        assert 'dose_results' in results
        assert 'ctdi_results' in results
        assert 'dlp' in results
        
        # Check that results are stored
        assert runner.results == results
    
    def test_get_summary_no_results(self):
        """Test getting summary without results."""
        runner = PCXMCRunner()
        
        with pytest.raises(ValueError, match="No results available"):
            runner.get_summary()
    
    def test_get_summary_with_results(self):
        """Test getting summary with results."""
        runner = PCXMCRunner()
        
        # Mock results
        runner.results = {
            'dose_results': {'effective_dose': 2.5},
            'ctdi_results': {
                'ctdi_100': 10.0,
                'ctdi_w': 8.0,
                'ctdi_vol': 8.0
            },
            'dlp': 240.0,
            'field_data': {'X_final': [1, 2, 3]}
        }
        
        summary = runner.get_summary()
        
        expected = {
            'effective_dose_mSv': 2.5,
            'ctdi_100_mGy': 10.0,
            'ctdi_w_mGy': 8.0,
            'ctdi_vol_mGy': 8.0,
            'dlp_mGy_cm': 240.0,
            'n_sub_fields_used': 3
        }
        
        assert summary == expected


class TestRunExampleCalculation:
    """Test cases for example calculation."""
    
    def test_run_example(self):
        """Test running example calculation."""
        runner, results, summary = run_example_calculation()
        
        assert isinstance(runner, PCXMCRunner)
        assert isinstance(results, dict)
        assert isinstance(summary, dict)
        
        # Check summary has expected keys
        expected_keys = {
            'effective_dose_mSv', 'ctdi_100_mGy', 'ctdi_w_mGy',
            'ctdi_vol_mGy', 'dlp_mGy_cm', 'n_sub_fields_used'
        }
        assert set(summary.keys()) == expected_keys
        
        # Check values are reasonable
        assert summary['effective_dose_mSv'] >= 0
        assert summary['ctdi_100_mGy'] >= 0
        assert summary['ctdi_w_mGy'] >= 0
        assert summary['ctdi_vol_mGy'] >= 0
        assert summary['dlp_mGy_cm'] >= 0
        assert summary['n_sub_fields_used'] > 0


if __name__ == "__main__":
    pytest.main([__file__])
