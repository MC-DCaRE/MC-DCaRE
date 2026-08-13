from __future__ import annotations

import os
import sys
from typing import Any, Dict
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.gui.controller import GUIController
from src.gui.adapter import gui_to_config
from src.models.keys import (
    CTDI_PHSP_FILE,
    CTDI_PHSP_MODE,
    CTDI_PHSP_MULTIPLE_USE,
    CTDI_RUN,
    CTDI_USER_BLADE,
    COUCH_ENABLED,
    DICOM_DIR,
    DICOM_RP,
    DICOM_RUN,
    IMAGING_MODE,
    PATIENT_ID,
    PHANTOM_RUN,
    RESET,
    SCAN_TYPE,
    SIM_TYPE,
)


class TestGUIControllerInit:
    def test_stores_view_and_orchestrator(self) -> None:
        mock_view = MagicMock()
        mock_orch = MagicMock()
        ctrl = GUIController(mock_view, mock_orch)
        assert ctrl.view is mock_view
        assert ctrl.orchestrator is mock_orch

    def test_event_handlers_has_expected_keys(self) -> None:
        ctrl = GUIController(MagicMock(), MagicMock())
        expected = {
            RESET,
            SIM_TYPE,
            DICOM_DIR,
            DICOM_RP,
            DICOM_RUN,
            CTDI_RUN,
            PHANTOM_RUN,
            IMAGING_MODE,
            SCAN_TYPE,
            COUCH_ENABLED,
            CTDI_USER_BLADE,
        }
        assert set(ctrl._event_handlers.keys()) == expected


class TestOnReset:
    def test_calls_view_reset_all_with_defaults(self) -> None:
        mock_view = MagicMock()
        ctrl = GUIController(mock_view, MagicMock())
        defaults: Dict[str, Any] = {"key": "val"}
        ctrl._default_values = defaults
        ctrl._on_reset(defaults)
        mock_view.reset_all.assert_called_once_with(defaults)

    def test_hides_both_tabs(self) -> None:
        mock_view = MagicMock()
        ctrl = GUIController(mock_view, MagicMock())
        ctrl._default_values = {}
        ctrl._on_reset({})
        mock_view.reset_all.assert_called_once_with({})


class TestOnSimTypeChange:
    def test_shows_dicom_tab_hides_ctdi(self) -> None:
        mock_view = MagicMock()
        ctrl = GUIController(mock_view, MagicMock())
        ctrl._on_sim_type_change({SIM_TYPE: "DICOM"})
        mock_view.set_tab_visibility.assert_called_once_with("DICOM")

    def test_shows_ctdi_tab_hides_dicom(self) -> None:
        mock_view = MagicMock()
        ctrl = GUIController(mock_view, MagicMock())
        ctrl._on_sim_type_change({SIM_TYPE: "CTDI"})
        mock_view.set_tab_visibility.assert_called_once_with("CTDI")


class TestOnDicomDir:
    @patch("src.gui.controller.dcmread")
    @patch("src.gui.controller.os.listdir")
    def test_updates_patient_id_when_ct_found(
        self, mock_listdir: MagicMock, mock_dcmread: MagicMock
    ) -> None:
        mock_listdir.return_value = ["img1.dcm"]
        mock_ds = MagicMock()
        mock_ds.Modality = "CT"
        mock_ds.PatientID = "PAT001"
        mock_dcmread.return_value = mock_ds

        mock_view = MagicMock()
        ctrl = GUIController(mock_view, MagicMock())
        ctrl._on_dicom_dir({DICOM_DIR: "/dicom"})

        mock_view.update_patient_id.assert_called_once_with("PAT001")
        mock_view.show_popup.assert_called_once_with(
            "Number of PAT001 CT images found", 1
        )

    @patch("src.gui.controller.dcmread")
    @patch("src.gui.controller.os.listdir")
    def test_shows_error_when_no_ct_images(
        self, mock_listdir: MagicMock, mock_dcmread: MagicMock
    ) -> None:
        mock_listdir.return_value = ["img.dcm"]
        mock_ds = MagicMock()
        mock_ds.Modality = "MR"
        mock_ds.PatientID = "PAT002"
        mock_dcmread.return_value = mock_ds

        mock_view = MagicMock()
        ctrl = GUIController(mock_view, MagicMock())
        ctrl._on_dicom_dir({DICOM_DIR: "/dicom"})

        mock_view.show_error.assert_called_once_with("No CT images found in directory")

    @patch("src.gui.controller.dcmread")
    @patch("src.gui.controller.os.listdir")
    def test_shows_error_on_mixed_patient_ids(
        self, mock_listdir: MagicMock, mock_dcmread: MagicMock
    ) -> None:
        mock_listdir.return_value = ["a.dcm", "b.dcm"]
        ds_a = MagicMock()
        ds_a.Modality = "CT"
        ds_a.PatientID = "PAT001"
        ds_b = MagicMock()
        ds_b.Modality = "CT"
        ds_b.PatientID = "PAT999"
        mock_dcmread.side_effect = [ds_a, ds_b]

        mock_view = MagicMock()
        ctrl = GUIController(mock_view, MagicMock())
        ctrl._on_dicom_dir({DICOM_DIR: "/dicom"})

        mock_view.show_error.assert_called_once()


class TestOnDicomRp:
    @patch("src.gui.controller.dcmread")
    def test_extracts_isocenter_and_updates_view(self, mock_dcmread: MagicMock) -> None:
        mock_ds = MagicMock()
        mock_ds.PatientID = "PAT001"
        mock_cp = MagicMock()
        mock_cp.IsocenterPosition = [1.0, 2.0, 3.0]
        mock_beam = MagicMock()
        mock_beam.ControlPointSequence = [mock_cp]
        mock_ds.BeamSequence = [mock_beam]
        mock_dcmread.return_value = mock_ds

        mock_view = MagicMock()
        ctrl = GUIController(mock_view, MagicMock())
        ctrl._on_dicom_rp({DICOM_RP: "/plan.dcm", PATIENT_ID: "PAT001"})

        mock_view.update_isocenter.assert_called_once_with("1.0 mm", "2.0 mm", "3.0 mm")

    @patch("src.gui.controller.dcmread")
    def test_shows_error_on_patient_id_mismatch(self, mock_dcmread: MagicMock) -> None:
        mock_ds = MagicMock()
        mock_ds.PatientID = "WRONG_ID"
        mock_dcmread.return_value = mock_ds

        mock_view = MagicMock()
        ctrl = GUIController(mock_view, MagicMock())
        ctrl._on_dicom_rp({DICOM_RP: "/plan.dcm", PATIENT_ID: "PAT001"})

        mock_view.show_error.assert_called_once_with(
            "Patient ID for the CT image set and treatment plan does not match"
        )


class TestOnRun:
    @patch("src.gui.controller.gui_to_config")
    def test_builds_config_and_calls_orchestrator(
        self, mock_gui_to_config: MagicMock
    ) -> None:
        mock_config = MagicMock()
        mock_gui_to_config.return_value = mock_config
        mock_orch = MagicMock()
        mock_orch.run.return_value = "/rundir"

        mock_view = MagicMock()
        ctrl = GUIController(mock_view, mock_orch)
        ctrl._on_run({"some": "values"})

        mock_orch.run.assert_called_once_with(mock_config)
        mock_view.show_popup.assert_called_once_with("/rundir")

    @patch("src.gui.controller.gui_to_config")
    def test_shows_error_on_exception(self, mock_gui_to_config: MagicMock) -> None:
        mock_gui_to_config.side_effect = ValueError("bad config")

        mock_view = MagicMock()
        ctrl = GUIController(mock_view, MagicMock())
        ctrl._on_run({})

        mock_view.show_error.assert_called_once_with("Simulation failed: bad config")


class TestOnImagingModeChange:
    @patch("src.gui.controller.IMAGING_MODES")
    def test_updates_imaging_mode_fields(self, mock_modes: MagicMock) -> None:
        mock_mode = MagicMock()
        mock_modes.__getitem__ = MagicMock(return_value=mock_mode)

        mock_view = MagicMock()
        ctrl = GUIController(mock_view, MagicMock())
        ctrl._on_imaging_mode_change({SCAN_TYPE: "CW", IMAGING_MODE: "Head"})

        mock_view.update_imaging_mode_fields.assert_called_once_with(mock_mode)


class TestOnCouchToggle:
    def test_sets_couch_visible_true(self) -> None:
        mock_view = MagicMock()
        ctrl = GUIController(mock_view, MagicMock())
        ctrl._on_couch_toggle({COUCH_ENABLED: True})
        mock_view.set_couch_visible.assert_called_once_with(True)

    def test_sets_couch_visible_false(self) -> None:
        mock_view = MagicMock()
        ctrl = GUIController(mock_view, MagicMock())
        ctrl._on_couch_toggle({COUCH_ENABLED: False})
        mock_view.set_couch_visible.assert_called_once_with(False)


class TestOnUserBladeToggle:
    def test_sets_blade_visible_true(self) -> None:
        mock_view = MagicMock()
        ctrl = GUIController(mock_view, MagicMock())
        ctrl._on_user_blade_toggle({CTDI_USER_BLADE: True})
        mock_view.set_blade_visible.assert_called_once_with(True)

    def test_sets_blade_visible_false(self) -> None:
        mock_view = MagicMock()
        ctrl = GUIController(mock_view, MagicMock())
        ctrl._on_user_blade_toggle({CTDI_USER_BLADE: False})
        mock_view.set_blade_visible.assert_called_once_with(False)


class TestRunEventLoop:
    @patch("src.gui.controller.sg")
    def test_dispatches_handler_for_known_event(self, mock_sg: MagicMock) -> None:
        mock_sg.WIN_CLOSED = "WIN_CLOSED"
        mock_view = MagicMock()
        mock_view.read.side_effect = [(RESET, {}), ("WIN_CLOSED", {})]

        ctrl = GUIController(mock_view, MagicMock())
        ctrl._first_read = False
        handler_mock = MagicMock()
        ctrl._event_handlers[RESET] = handler_mock
        ctrl.run()

        handler_mock.assert_called_once_with({})

    @patch("src.gui.controller.sg")
    def test_breaks_on_win_closed(self, mock_sg: MagicMock) -> None:
        mock_sg.WIN_CLOSED = "WIN_CLOSED"
        mock_view = MagicMock()
        mock_view.read.return_value = ("WIN_CLOSED", {})

        ctrl = GUIController(mock_view, MagicMock())
        ctrl._first_read = False
        ctrl.run()

        mock_view.read.assert_called_once()

    @patch("src.gui.controller.sg")
    def test_ignores_unknown_event(self, mock_sg: MagicMock) -> None:
        mock_sg.WIN_CLOSED = "WIN_CLOSED"
        mock_view = MagicMock()
        mock_view.read.side_effect = [("unknown_event", {}), ("WIN_CLOSED", {})]

        ctrl = GUIController(mock_view, MagicMock())
        ctrl._first_read = False
        ctrl.run()

        mock_view.show_error.assert_not_called()


class TestPhaseSpaceAdapter:
    """Phase-space GUI controls round-trip through the adapter."""

    def _min_values(self, overrides: Dict[str, Any] = None) -> Dict[str, Any]:
        # Provide just enough keys to satisfy SimulationConfig required fields.
        from src.gui.adapter import _PLACEHOLDER_MAP

        values = {key: default for _section, _field, key, default in _PLACEHOLDER_MAP}
        if overrides:
            values.update(overrides)
        return values

    def test_defaults(self) -> None:
        config = gui_to_config(self._min_values())
        assert config.ctdi.phase_space_mode == "off"
        assert config.ctdi.phase_space_file == ""
        assert config.ctdi.phase_space_multiple_use == 1
        assert isinstance(config.ctdi.phase_space_multiple_use, int)

    def test_multiple_use_coerced_to_int(self) -> None:
        # FreeSimpleGUI InputText returns strings; downstream replay
        # normalization divides by this value, so it must be an int.
        config = gui_to_config(
            self._min_values(
                {
                    CTDI_PHSP_MODE: "replay",
                    CTDI_PHSP_FILE: "/path/to/beam.phsp",
                    CTDI_PHSP_MULTIPLE_USE: "5",
                }
            )
        )
        assert config.ctdi.phase_space_mode == "replay"
        assert config.ctdi.phase_space_file == "/path/to/beam.phsp"
        assert config.ctdi.phase_space_multiple_use == 5
        assert isinstance(config.ctdi.phase_space_multiple_use, int)

    def test_multiple_use_invalid_falls_back_to_one(self) -> None:
        config = gui_to_config(
            self._min_values({CTDI_PHSP_MULTIPLE_USE: "not-a-number"})
        )
        assert config.ctdi.phase_space_multiple_use == 1
