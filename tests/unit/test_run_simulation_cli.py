from __future__ import annotations

import json
import os
import sys
from unittest.mock import MagicMock, patch

import yaml
from typer.testing import CliRunner

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from run_simulation import app

MINIMAL_YAML: str = (
    "general:\n"
    "  g4_data_directory: /root/G4Data\n"
    "  topas_directory: /root/topas/bin/topas\n"
    "  seed: '9'\n"
    "  threads: '1'\n"
    "  histories: '100000'\n"
    "imaging:\n"
    "  simulation_type: DICOM\n"
    "  fan_mode: Full Fan\n"
    "  rotation_direction: CBCT Clockwise\n"
    "  anode_voltage: 100 kV\n"
    "  exposure: 100 mAs\n"
    "  imaging_mode: Image Gently\n"
    "  rotation_rate: 0.4 deg/s\n"
    "  timeline_end: 501.0 s\n"
    "  sequential_times: '1000'\n"
    "  time_verbosity: '0'\n"
    "  field_x1: 14 cm\n"
    "  field_x2: 14 cm\n"
    "  field_y1: 10.7 cm\n"
    "  field_y2: 10.7 cm\n"
    "  blade_x1: 6.175536078965273 cm\n"
    "  blade_x2: -6.175536078965273 cm\n"
    "  blade_y1: 5.814471115800571 cm\n"
    "  blade_y2: -5.814471115800571 cm\n"
    "  start_angle: 0 deg\n"
    "dicom:\n"
    "  dicom_directory: /sampledicom/setA\n"
    "  dicom_rp_file: /sampledicom/RP.sample.dcm\n"
    "  patient_id: ''\n"
    "  isocenter_x: 0 mm\n"
    "  isocenter_y: 0 mm\n"
    "  isocenter_z: 0 mm\n"
    "  patient_shift_x: 0. mm\n"
    "  patient_shift_y: 0. mm\n"
    "  patient_shift_z: 0. mm\n"
    "  patient_yaw: 0. deg\n"
    "  graphics_enabled: false\n"
    "ctdi:\n"
    "  phantom_size: 16 cm\n"
    "  dose_to_medium_zbins: '100'\n"
    "  tle_zbins: '100'\n"
    "  dose_to_water_zbins: '100'\n"
    "  couch_enabled: true\n"
    "  couch_width: 260. mm\n"
    "  couch_thickness: 0.4 mm\n"
    "  couch_length: 1000 mm\n"
    "  user_blade_enabled: false\n"
    "  user_field_x1: 14 cm\n"
    "  user_field_x2: 14 cm\n"
    "  user_field_y1: 10.7 cm\n"
    "  user_field_y2: 10.7 cm\n"
    "  graphics_enabled: false\n"
)

runner = CliRunner()


def _write_config(tmp_path: object, content: str = MINIMAL_YAML) -> str:
    path = os.path.join(str(tmp_path), "config.yaml")
    with open(path, "w") as f:
        f.write(content)
    return path


class TestGenerateConfig:
    def test_generate_config_creates_yaml(self, tmp_path: object) -> None:
        output = os.path.join(str(tmp_path), "generated.yaml")
        result = runner.invoke(app, ["generate-config", "--output", output])
        assert result.exit_code == 0
        assert os.path.exists(output)
        with open(output) as f:
            data = yaml.safe_load(f)
        assert "general" in data
        assert "imaging" in data
        assert "dicom" in data
        assert "ctdi" in data
        assert data["general"]["seed"] == "9"
        assert data["imaging"]["fan_mode"] == "Full Fan"

    def test_generate_config_default_output(self, tmp_path: object) -> None:
        output = os.path.join(str(tmp_path), "simulation_config.yaml")
        with patch("run_simulation.SimulationConfig.to_yaml") as mock_to_yaml:
            result = runner.invoke(app, ["generate-config", "--output", output])
            assert result.exit_code == 0
            mock_to_yaml.assert_called_once_with(output)


class TestValidate:
    def test_validate_valid_config(self, tmp_path: object) -> None:
        path = _write_config(tmp_path)
        result = runner.invoke(app, ["validate", path])
        assert result.exit_code == 0
        assert "valid" in result.output.lower()

    def test_validate_missing_file(self, tmp_path: object) -> None:
        path = os.path.join(str(tmp_path), "nonexistent.yaml")
        result = runner.invoke(app, ["validate", path])
        assert result.exit_code == 1

    def test_validate_invalid_yaml(self, tmp_path: object) -> None:
        path = _write_config(tmp_path, "imaging:\n  simulation_type: INVALID\n")
        result = runner.invoke(app, ["validate", path])
        assert result.exit_code == 1


class TestRun:
    @patch("run_simulation._add_file_handler")
    @patch("run_simulation.Orchestrator")
    def test_run_calls_orchestrator(
        self,
        mock_orch_cls: MagicMock,
        mock_add_fh: MagicMock,
        tmp_path: object,
    ) -> None:
        mock_instance = mock_orch_cls.return_value
        mock_instance.create_runfolder.return_value = "/rundir"
        mock_add_fh.return_value = MagicMock()
        path = _write_config(tmp_path)
        result = runner.invoke(app, ["run", path])
        assert result.exit_code == 0
        mock_instance.create_runfolder.assert_called_once()
        mock_instance.run_with_runfolder.assert_called_once()

    @patch("run_simulation._add_file_handler")
    @patch("run_simulation.Orchestrator")
    def test_run_dry_run_calls_prepare_only(
        self,
        mock_orch_cls: MagicMock,
        mock_add_fh: MagicMock,
        tmp_path: object,
    ) -> None:
        mock_instance = mock_orch_cls.return_value
        mock_instance.prepare_only.return_value = "/rundir"
        mock_add_fh.return_value = MagicMock()
        path = _write_config(tmp_path)
        result = runner.invoke(app, ["run", path, "--dry-run"])
        assert result.exit_code == 0
        mock_instance.prepare_only.assert_called_once()
        mock_instance.run_with_runfolder.assert_not_called()

    def test_run_missing_config(self, tmp_path: object) -> None:
        path = os.path.join(str(tmp_path), "nonexistent.yaml")
        result = runner.invoke(app, ["run", path])
        assert result.exit_code != 0


class TestConvert:
    def test_convert_outputs_json(self, tmp_path: object) -> None:
        input_path = _write_config(tmp_path)
        output_path = os.path.join(str(tmp_path), "output.json")
        result = runner.invoke(app, ["convert", input_path, output_path])
        assert result.exit_code == 0
        assert os.path.exists(output_path)
        with open(output_path) as f:
            data = json.load(f)
        assert "general" in data
        assert "imaging" in data
        assert "dicom" in data
        assert "ctdi" in data
        assert data["general"]["seed"] == "9"
        assert data["ctdi"]["couch_enabled"] is True

    def test_convert_outputs_yaml(self, tmp_path: object) -> None:
        input_path = _write_config(tmp_path)
        output_path = os.path.join(str(tmp_path), "output.yaml")
        result = runner.invoke(app, ["convert", input_path, output_path])
        assert result.exit_code == 0
        assert os.path.exists(output_path)
        with open(output_path) as f:
            data = yaml.safe_load(f)
        assert "general" in data
        assert data["imaging"]["fan_mode"] == "Full Fan"

    def test_convert_explicit_format_json(self, tmp_path: object) -> None:
        input_path = _write_config(tmp_path)
        output_path = os.path.join(str(tmp_path), "output.custom")
        result = runner.invoke(
            app, ["convert", input_path, output_path, "--format", "json"]
        )
        assert result.exit_code == 0
        with open(output_path) as f:
            data = json.load(f)
        assert "general" in data

    def test_convert_unsupported_format(self, tmp_path: object) -> None:
        input_path = _write_config(tmp_path)
        output_path = os.path.join(str(tmp_path), "output.xml")
        result = runner.invoke(app, ["convert", input_path, output_path])
        assert result.exit_code == 1
