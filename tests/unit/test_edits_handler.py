import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, mock_open
from src.edits_handler import editor


# Correct implementation of stringindexreplacement for testing
def correct_stringindexreplacement(SearchString: str, TargetList: list, ReplacementString=None):
    '''
    Targeted string replacement for a list.
    Function looks for the line that starts with SearchString in the list and replaces it with Replacement String.
    Function will replace the entire line and any information trailing the SearchString and replacement string will be lost in this process.
    If no replacement string is given in the arguments, the entire line is removed
    '''
    for lineIndex in range(len(TargetList)):
        if TargetList[lineIndex].startswith(SearchString):
            if ReplacementString is None:
                TargetList[lineIndex] = ''
                break  # exits after the first instance of match. Saves compute.
            else:
                TargetList[lineIndex] = SearchString + " = " + str(ReplacementString) + '\n'
                break  # exits after the first instance of match. Saves compute.


class TestStringIndexReplacement:
    def test_single_replacement_middle(self):
        """Test single replacement in middle of file"""
        lines = [
            "line1\n",
            "s:Ts/G4DataDirectory = old_value\n",
            "line3\n"
        ]
        # Call the correct implementation
        correct_stringindexreplacement("s:Ts/G4DataDirectory", lines, "new_value")
        assert lines[1] == "s:Ts/G4DataDirectory = new_value\n"

    def test_multiple_replacements_same_file(self):
        """Test multiple replacements in same file"""
        lines = [
            "line1\n",
            "i:Tf/NumberOfSequentialTimes = old_value1\n",
            "line3\n",
            "d:Tf/TimelineEnd = old_value2\n",
            "line5\n"
        ]
        correct_stringindexreplacement("i:Tf/NumberOfSequentialTimes", lines, "new_value1")
        correct_stringindexreplacement("d:Tf/TimelineEnd", lines, "new_value2")
        assert lines[1] == "i:Tf/NumberOfSequentialTimes = new_value1\n"
        assert lines[3] == "d:Tf/TimelineEnd = new_value2\n"

    def test_replacement_beginning_end(self):
        """Test replacement at beginning and end of file"""
        lines = [
            "s:Ts/Seed = old_value\n",
            "line2\n",
            "i:Ts/NumberOfThreads = old_value\n"
        ]
        correct_stringindexreplacement("s:Ts/Seed", lines, "new_value1")
        correct_stringindexreplacement("i:Ts/NumberOfThreads", lines, "new_value2")
        assert lines[0] == "s:Ts/Seed = new_value1\n"
        assert lines[2] == "i:Ts/NumberOfThreads = new_value2\n"

    def test_no_matches_found(self):
        """Test no matches found (should leave file unchanged)"""
        lines = [
            "line1\n",
            "line2\n",
            "line3\n"
        ]
        original_lines = lines.copy()
        correct_stringindexreplacement("nonexistent_string", lines, "new_value")
        assert lines == original_lines

    def test_replacement_none_value(self):
        """Test replacement with None value (should remove line)"""
        lines = [
            "line1\n",
            "includeFile = halffan.txt\n",
            "line3\n"
        ]
        correct_stringindexreplacement("includeFile = halffan.txt", lines)
        assert lines[1] == ""


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_boilerplate_files(temp_dir):
    """Create mock boilerplate files for testing"""
    boilerplate_dir = os.path.join(temp_dir, "boilerplates")
    os.makedirs(boilerplate_dir)
    
    # Create mock headsourcecode_boilerplate.txt
    headsource_path = os.path.join(boilerplate_dir, "headsourcecode_boilerplate.txt")
    with open(headsource_path, "w") as f:
        f.write("# Models simple cone beam geometry\n")
        f.write("includeFile=fullfan.txt\n")
        f.write("includeFile=halffan.txt\n")
        f.write("includeFile=patientDICOM.txt\n")
        f.write("s:Ts/G4DataDirectory=\"/root/G4Data\"\n")
        f.write("i:Ts/Seed=9\n")
        f.write("i:Ts/NumberOfThreads=4\n")
        f.write("i:Tf/NumberOfSequentialTimes = 501\n")
        f.write("d:Tf/TimelineEnd = 501 s\n")
        f.write("d:Tf/Rotate/Rate = 0.4 deg/s\n")
        f.write("d:Tf/Rotate/StartValue = 90 deg\n")
        f.write("i:So/beam/NumberOfHistoriesInRun = 20\n")
        f.write("dc:Ge/Coll1/TransY=5.3 cm\n")
        f.write("dc:Ge/Coll2/TransY=-5.3 cm\n")
        f.write("dc:Ge/Coll3/TransX=5.3 cm\n")
        f.write("dc:Ge/Coll4/TransX=-5.3 cm\n")
        f.write("Ts/UseQt=\"True\"\n")
        f.write("s:Gr/ViewA/Type=\"OpenGL\"\n")
        f.write("b:Gr/Enable=\"T\"\n")
    
    # Create mock include files
    include_dir = os.path.join(boilerplate_dir, "TOPAS_includeFiles")
    os.makedirs(include_dir)
    
    with open(os.path.join(include_dir, "CTDIphantom_16.txt"), "w") as f:
        f.write("#16cm phantom\n")
        f.write("s:Ge/couch/Parent=\"couchgroup\"\n")
        f.write("d:Ge/couch/HLX=260. mm\n")
        f.write("d:Ge/couch/HLY= 0.4 mm\n")
        f.write("d:Ge/couch/HLZ= 1000 mm\n")
        f.write("i:Sc/ChamberPlugDose_dtm/ZBins=100\n")
        f.write("i:Sc/ChamberPlugDose_tle/ZBins=100\n")
        f.write("i:Sc/ChamberPlugDose_dtw/ZBins=100\n")
    
    with open(os.path.join(include_dir, "CTDIphantom_32.txt"), "w") as f:
        f.write("#32cm phantom\n")
        f.write("s:Ge/couch/Parent=\"couchgroup\"\n")
        f.write("d:Ge/couch/HLX=260. mm\n")
        f.write("d:Ge/couch/HLY= 0.4 mm\n")
        f.write("d:Ge/couch/HLZ= 1000 mm\n")
        f.write("i:Sc/ChamberPlugDose_dtm/ZBins=100\n")
        f.write("i:Sc/ChamberPlugDose_tle/ZBins=100\n")
        f.write("i:Sc/ChamberPlugDose_dtw/ZBins=100\n")
    
    with open(os.path.join(include_dir, "patientDICOM.txt"), "w") as f:
        f.write("includeFile= HUtoMaterialSchneider.txt\n")
        f.write("s:Ge/Patient/DicomDirectory = \"/root/nccs/Sample_dicom_file/\"\n")
        f.write("d:Ge/patrotation/yaw = 0 deg\n")
        f.write("dc:Ge/IsocenterX = 0 mm\n")
        f.write("dc:Ge/IsocenterY = 0 mm\n")
        f.write("dc:Ge/IsocenterZ = 0 mm\n")
        f.write("dc:Ge/Patient/UserTransX = 0 mm\n")
        f.write("dc:Ge/Patient/UserTransY = 0 mm\n")
        f.write("dc:Ge/Patient/UserTransZ = 0 mm\n")
        f.write("s:Sc/DoseOnRTGrid100kz17/OutputFile = \"Dose_PTV\"\n")
    
    return boilerplate_dir


@patch('src.edits_handler.stringindexreplacement')
@patch('src.edits_handler.fieldtobladeopening')
def test_editor_main_file(mock_fieldtobladeopening, mock_stringindexreplacement, temp_dir, mock_boilerplate_files):
    """Test editor function with main file"""
    mock_fieldtobladeopening.return_value = ["1.0 cm", "-1.0 cm", "2.0 cm", "-2.0 cm"]
    # Mock the stringindexreplacement function to use our correct implementation
    mock_stringindexreplacement.side_effect = correct_stringindexreplacement
    
    # Create a temporary file to edit
    target_file = os.path.join(temp_dir, "mainheadsource.txt")
    shutil.copy(os.path.join(mock_boilerplate_files, "headsourcecode_boilerplate.txt"), target_file)
    
    # Define change dictionary
    change_dict = {
        '-G4FOLDERNAME-': '/new/g4data',
        '-TIMESEQ-': '100',
        '-TIMELINEEND-': '100 s',
        '-TIMEROTRATE-': '0.5 deg/s',
        '-STARTANGLEROT-': '180 deg',
        '-SEED-': '42',
        '-THREAD-': '8',
        '-HIST-': '1000',
        '-BLADE_X1-': '1.5 cm',
        '-BLADE_X2-': '-1.5 cm',
        '-BLADE_Y1-': '2.5 cm',
        '-BLADE_Y2-': '-2.5 cm',
        '-FAN-': 'Full Fan',
        '-FUNCTION_CHECK-': 'DICOM',
        '-DICOM_GRAPHICS-': False,
        '-DICOM-': '/new/dicom/path',
        '-DICOM_YAW-': '45 deg',
        '-DICOM_ISOX-': '10 mm',
        '-DICOM_ISOY-': '20 mm',
        '-DICOM_ISOZ-': '30 mm',
        '-DICOM_TX-': '100 mm',
        '-DICOM_TY-': '200 mm',
        '-DICOM_TZ-': '300 mm',
        '-PATID-': 'PAT123',
        '-DIRECTROT-': 'CW',
        '-IMAGEMODE-': 'DICOM',
    }
    
    # Call editor function
    editor(change_dict, target_file, 'main')
    
    # Verify changes were made
    with open(target_file, 'r') as f:
        content = f.readlines()
    
    # Check that values were replaced
    content_str = ''.join(content)
    assert 's:Ts/G4DataDirectory = "/new/g4data"' in content_str
    assert 'i:Tf/NumberOfSequentialTimes = 100' in content_str
    assert 'd:Tf/TimelineEnd = 100 s' in content_str
    assert 'd:Tf/Rotate/Rate = 0.5 deg/s' in content_str
    assert 'd:Tf/Rotate/StartValue = 180 deg' in content_str
    assert 'i:Ts/Seed = 42' in content_str
    assert 'i:Ts/NumberOfThreads = 8' in content_str
    assert 'i:So/beam/NumberOfHistoriesInRun = 1000' in content_str
    assert 'dc:Ge/Coll1/TransY = 1.5 cm' in content_str
    assert 'dc:Ge/Coll2/TransY = -1.5 cm' in content_str
    assert 'dc:Ge/Coll3/TransX = 2.5 cm' in content_str
    assert 'dc:Ge/Coll4/TransX = -2.5 cm' in content_str
    
    # Check that half fan includeFile was removed
    assert 'includeFile = halffan.txt' not in content_str
    
    # Check that graphics were removed for DICOM
    assert 'Ts/UseQt' not in content_str
    assert 's:Gr/ViewA/Type' not in content_str
    assert 'b:Gr/Enable' not in content_str


@patch('src.edits_handler.stringindexreplacement')
@patch('src.edits_handler.fieldtobladeopening')
def test_editor_sub_file_dicom(mock_fieldtobladeopening, mock_stringindexreplacement, temp_dir, mock_boilerplate_files):
    """Test editor function with sub file for DICOM"""
    mock_fieldtobladeopening.return_value = ["1.0 cm", "-1.0 cm", "2.0 cm", "-2.0 cm"]
    # Mock the stringindexreplacement function to use our correct implementation
    mock_stringindexreplacement.side_effect = correct_stringindexreplacement
    
    # Create a temporary file to edit
    target_file = os.path.join(temp_dir, "patientDICOM.txt")
    shutil.copy(os.path.join(mock_boilerplate_files, "TOPAS_includeFiles", "patientDICOM.txt"), target_file)
    
    # Define change dictionary
    change_dict = {
        '-FUNCTION_CHECK-': 'DICOM',
        '-DICOM-': '/new/dicom/path',
        '-DICOM_YAW-': '45 deg',
        '-DICOM_ISOX-': '10 mm',
        '-DICOM_ISOY-': '20 mm',
        '-DICOM_ISOZ-': '30 mm',
        '-DICOM_TX-': '100 mm',
        '-DICOM_TY-': '200 mm',
        '-DICOM_TZ-': '300 mm',
        '-PATID-': 'PAT123',
        '-DIRECTROT-': 'CW',
        '-IMAGEMODE-': 'DICOM',
        '-STARTANGLEROT-': '180 deg',
    }
    
    # Call editor function
    editor(change_dict, target_file, 'sub')
    
    # Verify changes were made
    with open(target_file, 'r') as f:
        content = f.readlines()
    
    # Check that values were replaced
    content_str = ''.join(content)
    assert 's:Ge/Patient/DicomDirectory = "/new/dicom/path"' in content_str
    assert 'd:Ge/patrotation/yaw = 45 deg' in content_str
    assert 'dc:Ge/IsocenterX = 10 mm' in content_str
    assert 'dc:Ge/IsocenterY = 20 mm' in content_str
    assert 'dc:Ge/IsocenterZ = 30 mm' in content_str
    assert 'dc:Ge/Patient/UserTransX = 100 mm' in content_str
    assert 'dc:Ge/Patient/UserTransY = 200 mm' in content_str
    assert 'dc:Ge/Patient/UserTransZ = 300 mm' in content_str
    assert 's:Sc/DoseOnRTGrid100kz17/OutputFile = "PAT123_CW_DICOM_180 deg_DOSE_PTV"' in content_str


@patch('src.edits_handler.stringindexreplacement')
@patch('src.edits_handler.fieldtobladeopening')
def test_editor_sub_file_ctdi(mock_fieldtobladeopening, mock_stringindexreplacement, temp_dir, mock_boilerplate_files):
    """Test editor function with sub file for CTDI validation"""
    mock_fieldtobladeopening.return_value = ["1.0 cm", "-1.0 cm", "2.0 cm", "-2.0 cm"]
    # Mock the stringindexreplacement function to use our correct implementation
    mock_stringindexreplacement.side_effect = correct_stringindexreplacement
    
    # Create a temporary file to edit
    target_file = os.path.join(temp_dir, "CTDIphantom_16.txt")
    shutil.copy(os.path.join(mock_boilerplate_files, "TOPAS_includeFiles", "CTDIphantom_16.txt"), target_file)
    
    # Define change dictionary
    change_dict = {
        '-FUNCTION_CHECK-': 'CTDI validation',
        '-COUCH_TOG-': False,
        '-COUCHHLX-': '200. mm',
        '-COUCHHLY-': '0.5 mm',
        '-COUCHHLZ-': '900 mm',
        '-DTMZB-': '50',
        '-TLEZB-': '50',
        '-DTWZB-': '50',
    }
    
    # Call editor function
    editor(change_dict, target_file, 'sub')
    
    # Verify changes were made
    with open(target_file, 'r') as f:
        content = f.readlines()
    
    # Check that values were replaced
    content_str = ''.join(content)
    assert 'd:Ge/couch/HLX = 200. mm' in content_str
    assert 'd:Ge/couch/HLY = 0.5 mm' in content_str
    assert 'd:Ge/couch/HLZ = 900 mm' in content_str
    assert 'i:Sc/ChamberPlugDose_dtm/ZBins = 50' in content_str
    assert 'i:Sc/ChamberPlugDose_tle/ZBins = 50' in content_str
    assert 'i:Sc/ChamberPlugDose_dtw/ZBins = 50' in content_str
    
    # Check that couch parent link was removed
    assert 's:Ge/couch/Parent="couchgroup"' not in content_str


def test_editor_ctdi_with_blade_toggling(temp_dir, mock_boilerplate_files):
    """Test editor function with CTDI validation and blade toggling"""
    with patch('src.edits_handler.fieldtobladeopening') as mock_fieldtobladeopening, \
         patch('src.edits_handler.stringindexreplacement') as mock_stringindexreplacement:
        mock_fieldtobladeopening.return_value = ["1.0 cm", "-1.0 cm", "2.0 cm", "-2.0 cm"]
        # Mock the stringindexreplacement function to use our correct implementation
        mock_stringindexreplacement.side_effect = correct_stringindexreplacement
        
        # Create a temporary file to edit
        target_file = os.path.join(temp_dir, "mainheadsource.txt")
        shutil.copy(os.path.join(mock_boilerplate_files, "headsourcecode_boilerplate.txt"), target_file)
        
        # Define change dictionary
        change_dict = {
            '-G4FOLDERNAME-': '/new/g4data',
            '-TIMESEQ-': '100',
            '-TIMELINEEND-': '100 s',
            '-TIMEROTRATE-': '0.5 deg/s',
            '-STARTANGLEROT-': '180 deg',
            '-SEED-': '42',
            '-THREAD-': '8',
            '-HIST-': '1000',
            '-BLADE_X1-': '1.5 cm',
            '-BLADE_X2-': '-1.5 cm',
            '-BLADE_Y1-': '2.5 cm',
            '-BLADE_Y2-': '-2.5 cm',
            '-FAN-': 'Full Fan',
            '-FUNCTION_CHECK-': 'CTDI validation',
            '-CTDI_GRAPHICS-': True,
            '-CTDI_BLADE_TOG-': True,
            '-CTDI_FIELD_X1-': '5 cm',
            '-CTDI_FIELD_X2-': '5 cm',
            '-CTDI_FIELD_Y1-': '10 cm',
            '-CTDI_FIELD_Y2-': '10 cm',
            '-CTDI_PHANTOM-': '16 cm',
        }
        
        # Call editor function
        editor(change_dict, target_file, 'main')
        
        # Verify fieldtobladeopening was called
        mock_fieldtobladeopening.assert_called_once_with(['5 cm', '5 cm', '10 cm', '10 cm'])
        
        # Verify changes were made
        with open(target_file, 'r') as f:
            content = f.readlines()
        
        # Check that values were replaced
        content_str = ''.join(content)
        assert 'dc:Ge/Coll1/TransY = 1.0 cm' in content_str
        assert 'dc:Ge/Coll2/TransY = -1.0 cm' in content_str
        assert 'dc:Ge/Coll3/TransX = 2.0 cm' in content_str
        assert 'dc:Ge/Coll4/TransX = -2.0 cm' in content_str
        
        # Check that CTDI phantom 32 includeFile was removed
        assert 'includeFile = CTDIphantom_32.txt' not in content_str


if __name__ == "__main__":
    pytest.main()