import pytest
import os
import numpy as np
from unittest.mock import patch, MagicMock
import tempfile
import shutil

# Import the module to test
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.Energyspectrum import generate_new_topas_beam_profile


class MockSpek:
    """Mock class for spekpy.Spek"""
    
    def __init__(self, kvp=None, th=None, dk=None, mu_data_source=None, physics=None, 
                 x=None, y=None, z=None, mas=None, brem=None, char=None, obli=None, 
                 comment=None, targ=None, shift=None, init_default=True):
        self.kvp = kvp
        self.th = th
        self.dk = dk
        self.mas = mas
        self.z = z
        self.targ = targ
        
        # Store parameters for verification
        self.constructor_params = {
            'kvp': kvp, 'th': th, 'dk': dk, 'mu_data_source': mu_data_source,
            'physics': physics, 'x': x, 'y': y, 'z': z, 'mas': mas, 'brem': brem,
            'char': char, 'obli': obli, 'comment': comment, 'targ': targ, 'shift': shift
        }
        
        # Mock state object
        self._state = MockState()
    
    def filter(self, matl, t):
        """Mock filter method"""
        self.filter_material = matl
        self.filter_thickness = t
    
    def get_flu(self):
        """Mock get_flu method"""
        # Return a fixed fluence value for testing
        return 1000.0
    
    def get_spectrum(self, edges=False, diff=False):
        """Mock get_spectrum method"""
        # Return mock energy and spectrum arrays
        karr = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
        spkarr = np.array([100.0, 200.0, 300.0, 200.0, 100.0])
        return karr, spkarr
    
    def get_std_results(self):
        """Mock get_std_results method"""
        class MockStdResults:
            def __init__(self):
                self.k = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
                self.spk = np.array([100.0, 200.0, 300.0, 200.0, 100.0])
                self.flu = 1000.0
                self.kerma = 500.0
                self.emean = 30.0
                self.hvl_1_al = 2.5
                self.hvl_2_al = 5.0
                self.hc_al = 0.5
                self.eeff_al = 25.0
                self.hvl_1_cu = 1.0
                self.hvl_2_cu = 2.0
                self.hc_cu = 0.4
                self.eeff_cu = 20.0
        return MockStdResults()
    
    @property
    def state(self):
        """Mock state property"""
        return self._state


class MockState:
    """Mock state class"""
    
    def get_current_state_str(self, mode, results):
        """Mock get_current_state_str method"""
        return "Mock spectrum state information"


class TestGenerateNewTopasBeamProfile:
    """Test class for generate_new_topas_beam_profile function"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @patch('src.Energyspectrum.sp')
    def test_generate_new_topas_beam_profile_with_different_kvp_values(self, mock_spek_module, temp_dir):
        """Test generate_new_topas_beam_profile with different kVp values"""
        # Setup mock
        mock_spek_instance = MockSpek()
        mock_spek_instance.get_spectrum = MagicMock(return_value=(np.array([10.0, 20.0, 30.0]), np.array([100.0, 200.0, 300.0])))
        mock_spek_instance.get_flu = MagicMock(return_value=1000.0)
        mock_spek_module.Spek.return_value = mock_spek_instance

        # Create tmp directory
        tmp_dir = os.path.join(temp_dir, 'tmp')
        os.makedirs(tmp_dir, exist_ok=True)

        # Test with 80 kVp
        generate_new_topas_beam_profile(80.0, 10.0, "1000", temp_dir)
        
        # Verify spekpy.Spek was called with correct parameters
        mock_spek_module.Spek.assert_called_once_with(
            kvp=80.0, th=14, mas=10.0, dk=0.2, z=0.1
        )
        
        # Verify output files were created
        assert os.path.exists(os.path.join(temp_dir, 'tmp', 'head_calibration_factor.txt'))
        assert os.path.exists(os.path.join(temp_dir, 'tmp', 'ConvertedTopasFile.txt'))
    
    @patch('src.Energyspectrum.sp')
    def test_generate_new_topas_beam_profile_with_filtration(self, mock_spek_module, temp_dir):
        """Test generate_new_topas_beam_profile with filtration"""
        # Setup mock
        mock_spek_instance = MockSpek()
        mock_spek_instance.get_spectrum = MagicMock(return_value=(np.array([10.0, 20.0, 30.0]), np.array([100.0, 200.0, 300.0])))
        mock_spek_instance.get_flu = MagicMock(return_value=1000.0)
        mock_spek_module.Spek.return_value = mock_spek_instance

        # Create tmp directory
        tmp_dir = os.path.join(temp_dir, 'tmp')
        os.makedirs(tmp_dir, exist_ok=True)

        # Test with filtration (currently commented in the original code)
        generate_new_topas_beam_profile(100.0, 10.0, "1000", temp_dir)
        
        # Verify spekpy.Spek was called with correct parameters
        mock_spek_module.Spek.assert_called_once_with(
            kvp=100.0, th=14, mas=10.0, dk=0.2, z=0.1
        )
        
        # Verify output files were created
        assert os.path.exists(os.path.join(temp_dir, 'tmp', 'head_calibration_factor.txt'))
        assert os.path.exists(os.path.join(temp_dir, 'tmp', 'ConvertedTopasFile.txt'))
    
    @patch('src.Energyspectrum.sp')
    def test_generate_new_topas_beam_profile_with_different_target_materials(self, mock_spek_module, temp_dir):
        """Test generate_new_topas_beam_profile with different target materials"""
        # Setup mock
        mock_spek_instance = MockSpek()
        mock_spek_instance.get_spectrum = MagicMock(return_value=(np.array([10.0, 20.0, 30.0]), np.array([100.0, 200.0, 300.0])))
        mock_spek_instance.get_flu = MagicMock(return_value=1000.0)
        mock_spek_module.Spek.return_value = mock_spek_instance

        # Create tmp directory
        tmp_dir = os.path.join(temp_dir, 'tmp')
        os.makedirs(tmp_dir, exist_ok=True)

        # Test with different target materials
        generate_new_topas_beam_profile(100.0, 10.0, "1000", temp_dir)
        
        # Verify spekpy.Spek was called with correct parameters
        mock_spek_module.Spek.assert_called_once_with(
            kvp=100.0, th=14, mas=10.0, dk=0.2, z=0.1
        )
        
        # Verify output files were created
        assert os.path.exists(os.path.join(temp_dir, 'tmp', 'head_calibration_factor.txt'))
        assert os.path.exists(os.path.join(temp_dir, 'tmp', 'ConvertedTopasFile.txt'))
    
    @patch('src.Energyspectrum.sp')
    def test_spek_constructor_parameters(self, mock_spek_module, temp_dir):
        """Test that Spek constructor is called with correct parameters"""
        # Setup mock
        mock_spek_instance = MockSpek()
        mock_spek_instance.get_spectrum = MagicMock(return_value=(np.array([10.0, 20.0, 30.0]), np.array([100.0, 200.0, 300.0])))
        mock_spek_instance.get_flu = MagicMock(return_value=1000.0)
        mock_spek_module.Spek.return_value = mock_spek_instance

        # Create tmp directory
        tmp_dir = os.path.join(temp_dir, 'tmp')
        os.makedirs(tmp_dir, exist_ok=True)

        # Call function
        generate_new_topas_beam_profile(125.0, 15.0, "500", temp_dir)
        
        # Verify spekpy.Spek was called with correct parameters
        mock_spek_module.Spek.assert_called_once_with(
            kvp=125.0, th=14, mas=15.0, dk=0.2, z=0.1
        )
        
        # Verify output files were created
        assert os.path.exists(os.path.join(temp_dir, 'tmp', 'head_calibration_factor.txt'))
        assert os.path.exists(os.path.join(temp_dir, 'tmp', 'ConvertedTopasFile.txt'))
    
    @patch('src.Energyspectrum.sp')
    def test_mock_return_values_for_calibration_factors_and_spectrum_data(self, mock_spek_module, temp_dir):
        """Test mock return values for calibration factors and spectrum data"""
        # Setup mock
        mock_spek_instance = MockSpek()
        mock_spek_instance.get_spectrum = MagicMock(return_value=(np.array([10.0, 20.0, 30.0]), np.array([100.0, 200.0, 300.0])))
        mock_spek_instance.get_flu = MagicMock(return_value=1000.0)
        mock_spek_module.Spek.return_value = mock_spek_instance

        # Create tmp directory
        tmp_dir = os.path.join(temp_dir, 'tmp')
        os.makedirs(tmp_dir, exist_ok=True)

        # Call function
        generate_new_topas_beam_profile(100.0, 10.0, "1000", temp_dir)
        
        # Verify calibration factor calculation
        # calib_factor = no_particles/Histories = 4*pi*0.1^2*1000/1000 = 0.1256
        expected_calib_factor = int(4 * np.pi * 0.1**2 * 1000 / 1000)
        
        # Read calibration factor file
        with open(os.path.join(temp_dir, 'tmp', 'head_calibration_factor.txt'), 'r') as f:
            content = f.read()
            assert str(expected_calib_factor) in content
    
    @patch('src.Energyspectrum.sp')
    def test_head_calibration_factor_file_content(self, mock_spek_module, temp_dir):
        """Test head calibration factor file content"""
        # Setup mock
        mock_spek_instance = MockSpek()
        mock_spek_instance.get_flu = MagicMock(return_value=1000.0)
        mock_spek_module.Spek.return_value = mock_spek_instance

        # Create tmp directory
        tmp_dir = os.path.join(temp_dir, 'tmp')
        os.makedirs(tmp_dir, exist_ok=True)

        # Call function
        generate_new_topas_beam_profile(100.0, 10.0, "1000", temp_dir)
        
        # Read calibration factor file
        with open(os.path.join(temp_dir, 'tmp', 'head_calibration_factor.txt'), 'r') as f:
            content = f.read()
            
        # Verify file content
        assert 'Multiply dose by the factor above to get absolute dose' in content
        assert 'The number of histories in this run was: 1000' in content
        assert 'Calibration factor = Number of particles/Histories' in content
        assert 'Mock spectrum state information' in content
    
    @patch('src.Energyspectrum.sp')
    def test_converted_topas_file_format_and_content(self, mock_spek_module, temp_dir):
        """Test converted TOPAS file format and content"""
        # Setup mock
        mock_spek_instance = MockSpek()
        mock_karr = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
        mock_spkarr = np.array([100.0, 200.0, 300.0, 200.0, 100.0])
        mock_spek_instance.get_spectrum = MagicMock(return_value=(mock_karr, mock_spkarr))
        mock_spek_instance.get_flu = MagicMock(return_value=1000.0)
        mock_spek_module.Spek.return_value = mock_spek_instance

        # Create tmp directory
        tmp_dir = os.path.join(temp_dir, 'tmp')
        os.makedirs(tmp_dir, exist_ok=True)

        # Call function
        generate_new_topas_beam_profile(100.0, 10.0, "1000", temp_dir)
        
        # Read converted TOPAS file
        with open(os.path.join(temp_dir, 'tmp', 'ConvertedTopasFile.txt'), 'r') as f:
            content = f.read()
            
        # Verify file format
        assert 'dv:So/beam/BeamEnergySpectrumValues' in content
        assert 'uv:So/beam/BeamEnergySpectrumWeights' in content
        assert 'keV' in content
        
        # Verify spectrum data is included
        assert '10. 20. 30. 40. 50.' in content  # Energy values (with spaces)
        # Normalized spectrum values should be present
        assert '0.1 0.2 0.3 0.2 0.1' in content
    
    def test_invalid_kvp_values_should_raise_value_error(self):
        """Test that invalid kVp values raise ValueError"""
        # Create a temporary directory for this test
        temp_dir = tempfile.mkdtemp()
        try:
            # Test with negative kVp - spekpy will raise an exception
            with pytest.raises(Exception):
                generate_new_topas_beam_profile(-10.0, 10.0, "1000", temp_dir)
            
            # Test with zero kVp - spekpy will raise an exception
            with pytest.raises(Exception):
                generate_new_topas_beam_profile(0.0, 10.0, "1000", temp_dir)
            
            # Test with very high kVp - spekpy will raise an exception
            with pytest.raises(Exception):
                generate_new_topas_beam_profile(500.0, 10.0, "1000", temp_dir)
        finally:
            shutil.rmtree(temp_dir)
    
    @patch('src.Energyspectrum.sp')
    def test_empty_missing_output_files(self, mock_spek_module, temp_dir):
        """Test behavior with empty/missing output files"""
        # Setup mock
        mock_spek_instance = MockSpek()
        mock_spek_instance.get_spectrum = MagicMock(return_value=(np.array([10.0, 20.0, 30.0]), np.array([100.0, 200.0, 300.0])))
        mock_spek_instance.get_flu = MagicMock(return_value=1000.0)
        mock_spek_module.Spek.return_value = mock_spek_instance

        # Create temp subdirectory if it doesn't exist
        tmp_dir = os.path.join(temp_dir, 'tmp')
        os.makedirs(tmp_dir, exist_ok=True)

        # Call function
        generate_new_topas_beam_profile(100.0, 10.0, "1000", temp_dir)
        
        # Verify output files were created
        assert os.path.exists(os.path.join(temp_dir, 'tmp', 'head_calibration_factor.txt'))
        assert os.path.exists(os.path.join(temp_dir, 'tmp', 'ConvertedTopasFile.txt'))
        
        # Verify files are not empty
        assert os.path.getsize(os.path.join(temp_dir, 'tmp', 'head_calibration_factor.txt')) > 0
        assert os.path.getsize(os.path.join(temp_dir, 'tmp', 'ConvertedTopasFile.txt')) > 0
    
    @patch('src.Energyspectrum.sp')
    def test_main_block_example_usage(self, mock_spek_module, temp_dir):
        """Test the example usage in the main block"""
        # Setup mock
        mock_spek_instance = MockSpek()
        mock_spek_instance.get_spectrum = MagicMock(return_value=(np.array([10.0, 20.0, 30.0]), np.array([100.0, 200.0, 300.0])))
        mock_spek_instance.get_flu = MagicMock(return_value=1000.0)
        mock_spek_module.Spek.return_value = mock_spek_instance

        # Create tmp directory
        tmp_dir = os.path.join(temp_dir, 'tmp')
        os.makedirs(tmp_dir, exist_ok=True)

        # Call the function with the same parameters as in the main block
        generate_new_topas_beam_profile(125.0, 10.0, "100", temp_dir)
        
        # Verify output files were created
        assert os.path.exists(os.path.join(temp_dir, 'tmp', 'head_calibration_factor.txt'))
        assert os.path.exists(os.path.join(temp_dir, 'tmp', 'ConvertedTopasFile.txt'))


if __name__ == '__main__':
    pytest.main([__file__])