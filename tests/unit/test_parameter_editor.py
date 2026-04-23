import os
import sys
import tempfile
from typing import Any, List
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.config import (
    CtdiConfig,
    DicomConfig,
    GeneralConfig,
    ImagingConfig,
    SimulationConfig,
)
from src.parameter_editor import ParameterEditor

MAIN_FILE_CONTENT: str = (
    's:Ts/G4DataDirectory = "/root/G4Data"\n'
    'i:Tf/NumberOfSequentialTimes = "1000"\n'
    'd:Tf/TimelineEnd = "501.0 s"\n'
    'd:Tf/Rotate/Rate = "0.4 deg/s"\n'
    'd:Tf/Rotate/StartValue = "0 deg"\n'
    'i:Ts/Seed = "9"\n'
    'i:Ts/NumberOfThreads = "1"\n'
    'i:So/beam/NumberOfHistoriesInRun = "100000"\n'
    'dc:Ge/Coll1/TransY = "6.175536078965273 cm"\n'
    'dc:Ge/Coll2/TransY = "-6.175536078965273 cm"\n'
    'dc:Ge/Coll3/TransX = "5.814471115800571 cm"\n'
    'dc:Ge/Coll4/TransX = "-5.814471115800571 cm"\n'
    "includeFile = halffan.txt\n"
    "includeFile = CTDIphantom_16.txt\n"
    "includeFile = CTDIphantom_32.txt\n"
    'sv:Ph/Default/LayeredMassGeometryWorlds = "some value"\n'
    'Ts/UseQt = "true"\n'
    's:Gr/ViewA/Type = "some type"\n'
    'b:Gr/Enable = "true"\n'
    "includeFile = patientDICOM.txt\n"
)

SUB_FILE_CONTENT: str = (
    'd:Ge/patrotation/yaw = "0. deg"\n'
    's:Ge/Patient/DicomDirectory = "/sampledicom/setA"\n'
    'dc:Ge/IsocenterX = "0 mm"\n'
    'dc:Ge/IsocenterY = "0 mm"\n'
    'dc:Ge/IsocenterZ = "0 mm"\n'
    'dc:Ge/Patient/UserTransX = "0. mm"\n'
    'dc:Ge/Patient/UserTransY = "0. mm"\n'
    'dc:Ge/Patient/UserTransZ = "0. mm"\n'
    's:Sc/DoseOnRTGrid100kz17/OutputFile = "output"\n'
    's:Ge/couch/Parent = "couchgroup"\n'
    'd:Ge/couch/HLX = "260. mm"\n'
    'd:Ge/couch/HLY = "0.4 mm"\n'
    'd:Ge/couch/HLZ = "1000 mm"\n'
    'i:Sc/ChamberPlugDose_dtm/ZBins = "100"\n'
    'i:Sc/ChamberPlugDose_tle/ZBins = "100"\n'
    'i:Sc/ChamberPlugDose_dtw/ZBins = "100"\n'
)


def _write_temp(content: str) -> str:
    f: Any = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
    f.write(content)
    f.close()
    return f.name


def _read(path: str) -> str:
    with open(path) as fh:
        return fh.read()


class TestStringIndexReplacement:
    def test_replaces_matching_line(self) -> None:
        lines: List[str] = ['s:Ts/G4DataDirectory = "/old"\n']
        ParameterEditor.string_index_replacement(
            "s:Ts/G4DataDirectory", lines, '"/new/path"'
        )
        assert lines[0] == 's:Ts/G4DataDirectory = "/new/path"\n'

    def test_removes_line_when_replacement_is_none(self) -> None:
        lines: List[str] = ["includeFile = halffan.txt\n"]
        ParameterEditor.string_index_replacement("includeFile = halffan.txt", lines)
        assert lines[0] == ""

    def test_no_change_when_search_not_found(self) -> None:
        lines: List[str] = ['i:Ts/Seed = "9"\n']
        ParameterEditor.string_index_replacement("nonexistent_prefix", lines, '"42"')
        assert lines[0] == 'i:Ts/Seed = "9"\n'

    def test_only_replaces_first_match(self) -> None:
        lines: List[str] = [
            'i:Ts/Seed = "1"\n',
            'i:Ts/Seed = "2"\n',
        ]
        ParameterEditor.string_index_replacement("i:Ts/Seed", lines, '"99"')
        assert lines[0] == 'i:Ts/Seed = "99"\n'
        assert lines[1] == 'i:Ts/Seed = "2"\n'


def _dicom_config(**overrides: Any) -> SimulationConfig:
    general: GeneralConfig = GeneralConfig(
        g4_data_directory=overrides.get("g4_data_directory", "/root/G4Data"),
        topas_directory=overrides.get("topas_directory", "/root/topas"),
        seed=overrides.get("seed", "42"),
        threads=overrides.get("threads", "4"),
        histories=overrides.get("histories", "500000"),
    )
    imaging: ImagingConfig = ImagingConfig(
        simulation_type=overrides.get("simulation_type", "DICOM"),
        fan_mode=overrides.get("fan_mode", "Full Fan"),
        start_angle=overrides.get("start_angle", "0 deg"),
        rotation_rate=overrides.get("rotation_rate", "0.4 deg/s"),
        timeline_end=overrides.get("timeline_end", "501.0 s"),
        sequential_times=overrides.get("sequential_times", "1000"),
        blade_x1=overrides.get("blade_x1", "6.175536078965273 cm"),
        blade_x2=overrides.get("blade_x2", "-6.175536078965273 cm"),
        blade_y1=overrides.get("blade_y1", "5.814471115800571 cm"),
        blade_y2=overrides.get("blade_y2", "-5.814471115800571 cm"),
    )
    dicom: DicomConfig = DicomConfig(
        graphics_enabled=overrides.get("dicom_graphics_enabled", False),
        patient_yaw=overrides.get("patient_yaw", "0. deg"),
        dicom_directory=overrides.get("dicom_directory", "/sampledicom/setA"),
        isocenter_x=overrides.get("isocenter_x", "0 mm"),
        isocenter_y=overrides.get("isocenter_y", "0 mm"),
        isocenter_z=overrides.get("isocenter_z", "0 mm"),
        patient_shift_x=overrides.get("shift_x", "0. mm"),
        patient_shift_y=overrides.get("shift_y", "0. mm"),
        patient_shift_z=overrides.get("shift_z", "0. mm"),
        patient_id=overrides.get("patient_id", ""),
    )
    ctdi: CtdiConfig = CtdiConfig(
        phantom_size=overrides.get("phantom_size", "16 cm"),
        graphics_enabled=overrides.get("ctdi_graphics_enabled", False),
        couch_enabled=overrides.get("couch_enabled", True),
        couch_width=overrides.get("couch_width", "260. mm"),
        couch_thickness=overrides.get("couch_thickness", "0.4 mm"),
        couch_length=overrides.get("couch_length", "1000 mm"),
        dose_to_medium_zbins=overrides.get("dtm_zbins", "100"),
        tle_zbins=overrides.get("tle_zbins", "100"),
        dose_to_water_zbins=overrides.get("dtw_zbins", "100"),
        user_blade_enabled=overrides.get("user_blade_enabled", False),
        user_field_x1=overrides.get("user_field_x1", "14 cm"),
        user_field_x2=overrides.get("user_field_x2", "14 cm"),
        user_field_y1=overrides.get("user_field_y1", "10.7 cm"),
        user_field_y2=overrides.get("user_field_y2", "10.7 cm"),
    )
    return SimulationConfig(general=general, imaging=imaging, dicom=dicom, ctdi=ctdi)


class TestEditMainFile:
    def test_replaces_g4_directory(self) -> None:
        config: SimulationConfig = _dicom_config(g4_data_directory="/custom/g4data")
        editor: ParameterEditor = ParameterEditor(config)
        path: str = _write_temp(MAIN_FILE_CONTENT)
        try:
            editor.edit_main_file(path)
            content: str = _read(path)
            assert '/custom/g4data"' in content
            assert '"/root/G4Data"' not in content
        finally:
            os.unlink(path)

    def test_replaces_seed_threads_histories(self) -> None:
        config: SimulationConfig = _dicom_config(
            seed="99", threads="8", histories="2000000"
        )
        editor: ParameterEditor = ParameterEditor(config)
        path: str = _write_temp(MAIN_FILE_CONTENT)
        try:
            editor.edit_main_file(path)
            content: str = _read(path)
            assert "i:Ts/Seed = 99\n" in content
            assert "i:Ts/NumberOfThreads = 8\n" in content
            assert "i:So/beam/NumberOfHistoriesInRun = 2000000\n" in content
        finally:
            os.unlink(path)

    def test_removes_halffan_for_full_fan_mode(self) -> None:
        config: SimulationConfig = _dicom_config(fan_mode="Full Fan")
        editor: ParameterEditor = ParameterEditor(config)
        path: str = _write_temp(MAIN_FILE_CONTENT)
        try:
            editor.edit_main_file(path)
            content: str = _read(path)
            assert "includeFile = halffan.txt\n" not in content
        finally:
            os.unlink(path)

    def test_removes_fullfan_for_half_fan_mode(self) -> None:
        content_with_fullfan: str = MAIN_FILE_CONTENT.replace(
            "includeFile = halffan.txt", "includeFile = fullfan.txt"
        )
        config: SimulationConfig = _dicom_config(fan_mode="Half Fan")
        editor: ParameterEditor = ParameterEditor(config)
        path: str = _write_temp(content_with_fullfan)
        try:
            editor.edit_main_file(path)
            content: str = _read(path)
            assert "includeFile = fullfan.txt\n" not in content
        finally:
            os.unlink(path)

    def test_dicom_mode_removes_ctdi_phantoms_and_graphics(self) -> None:
        config: SimulationConfig = _dicom_config(
            simulation_type="DICOM", dicom_graphics_enabled=False
        )
        editor: ParameterEditor = ParameterEditor(config)
        path: str = _write_temp(MAIN_FILE_CONTENT)
        try:
            editor.edit_main_file(path)
            content: str = _read(path)
            assert "includeFile = CTDIphantom_16.txt\n" not in content
            assert "includeFile = CTDIphantom_32.txt\n" not in content
            assert "sv:Ph/Default/LayeredMassGeometryWorlds" not in content
            assert "Ts/UseQt" not in content
            assert "s:Gr/ViewA/Type" not in content
            assert "b:Gr/Enable" not in content
        finally:
            os.unlink(path)


class TestEditSubFile:
    def test_dicom_mode_replaces_patient_params(self) -> None:
        config: SimulationConfig = _dicom_config(
            simulation_type="DICOM",
            patient_yaw="90. deg",
            dicom_directory="/dicom/new",
        )
        editor: ParameterEditor = ParameterEditor(config)
        path: str = _write_temp(SUB_FILE_CONTENT)
        try:
            editor.edit_sub_file(path)
            content: str = _read(path)
            assert "d:Ge/patrotation/yaw = 90. deg\n" in content
            assert '"/dicom/new"' in content
        finally:
            os.unlink(path)

    def test_dicom_mode_replaces_isocenter(self) -> None:
        config: SimulationConfig = _dicom_config(
            simulation_type="DICOM",
            isocenter_x="10.5 mm",
            isocenter_y="20.0 mm",
            isocenter_z="30.0 mm",
        )
        editor: ParameterEditor = ParameterEditor(config)
        path: str = _write_temp(SUB_FILE_CONTENT)
        try:
            editor.edit_sub_file(path)
            content: str = _read(path)
            assert "dc:Ge/IsocenterX = 10.5 mm\n" in content
            assert "dc:Ge/IsocenterY = 20.0 mm\n" in content
            assert "dc:Ge/IsocenterZ = 30.0 mm\n" in content
        finally:
            os.unlink(path)

    def test_ctdi_mode_replaces_couch_params(self) -> None:
        config: SimulationConfig = _dicom_config(
            simulation_type="CTDI validation",
            couch_width="300. mm",
            couch_thickness="0.5 mm",
            couch_length="1200 mm",
        )
        editor: ParameterEditor = ParameterEditor(config)
        path: str = _write_temp(SUB_FILE_CONTENT)
        try:
            editor.edit_sub_file(path)
            content: str = _read(path)
            assert "d:Ge/couch/HLX = 300. mm\n" in content
            assert "d:Ge/couch/HLY = 0.5 mm\n" in content
            assert "d:Ge/couch/HLZ = 1200 mm\n" in content
        finally:
            os.unlink(path)

    def test_ctdi_mode_replaces_zbins(self) -> None:
        config: SimulationConfig = _dicom_config(
            simulation_type="CTDI validation",
            dtm_zbins="200",
            tle_zbins="300",
            dtw_zbins="400",
        )
        editor: ParameterEditor = ParameterEditor(config)
        path: str = _write_temp(SUB_FILE_CONTENT)
        try:
            editor.edit_sub_file(path)
            content: str = _read(path)
            assert "i:Sc/ChamberPlugDose_dtm/ZBins = 200\n" in content
            assert "i:Sc/ChamberPlugDose_tle/ZBins = 300\n" in content
            assert "i:Sc/ChamberPlugDose_dtw/ZBins = 400\n" in content
        finally:
            os.unlink(path)

    def test_ctdi_mode_user_blade_enabled_replaces_blade_positions(
        self,
    ) -> None:
        mock_blades: List[str] = [
            "1.0 cm",
            "-1.0 cm",
            "2.0 cm",
            "-2.0 cm",
        ]
        with patch("src.parameter_editor.fieldtobladeopening") as mock_ftb:
            mock_ftb.return_value = mock_blades
            config: SimulationConfig = _dicom_config(
                simulation_type="CTDI validation",
                user_blade_enabled=True,
                user_field_x1="10 cm",
                user_field_x2="10 cm",
                user_field_y1="5 cm",
                user_field_y2="5 cm",
            )
            editor: ParameterEditor = ParameterEditor(config)
            path: str = _write_temp(MAIN_FILE_CONTENT)
            try:
                editor.edit_main_file(path)
                content: str = _read(path)
                mock_ftb.assert_called_once_with(["10 cm", "10 cm", "5 cm", "5 cm"])
                assert "dc:Ge/Coll1/TransY = 1.0 cm\n" in content
                assert "dc:Ge/Coll2/TransY = -1.0 cm\n" in content
                assert "dc:Ge/Coll3/TransX = 2.0 cm\n" in content
                assert "dc:Ge/Coll4/TransX = -2.0 cm\n" in content
            finally:
                os.unlink(path)
