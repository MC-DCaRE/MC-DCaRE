from __future__ import annotations

import os
import sys
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.gui.view import MainView
from src.models.imaging_mode import ImagingMode
from src.models.keys import (
    BLADE_X1,
    BLADE_X2,
    BLADE_Y1,
    BLADE_Y2,
    COUCH,
    CTDI_BLADE,
    CTDI_PHANTOM,
    CTDI_TAB,
    DICOM_TAB,
    EXPOSURE,
    FAN_MODE,
    FIELD_X1,
    FIELD_X2,
    FIELD_Y1,
    FIELD_Y2,
    G4_DATA_DIR,
    ISO_X,
    ISO_Y,
    ISO_Z,
    PATIENT_ID,
    ROTATION_RATE,
    TIMELINE_END,
    TUBE_VOLTAGE,
)


@pytest.fixture
def mock_window() -> MagicMock:
    w = MagicMock()
    w.__getitem__ = MagicMock(return_value=MagicMock())
    return w


@pytest.fixture
def view(mock_window: MagicMock) -> MainView:
    with patch("src.gui.view.sg.Window", return_value=mock_window):
        v = MainView()
    return v


def _make_element_dict(keys: List[str]) -> Dict[str, MagicMock]:
    return {key: MagicMock() for key in keys}


class TestMainViewInit:
    def test_creates_window_with_title(self, mock_window: MagicMock) -> None:
        with patch("src.gui.view.sg.Window", return_value=mock_window) as mock_cls:
            MainView()
        _, kwargs = mock_cls.call_args
        assert kwargs["title"] == "MC-DCaRE"

    def test_binds_enter_key_to_g4_dir(self, mock_window: MagicMock) -> None:
        g4_elem = MagicMock()
        mock_window.__getitem__ = MagicMock(return_value=g4_elem)
        with patch("src.gui.view.sg.Window", return_value=mock_window):
            MainView()
        mock_window.__getitem__.assert_called_with(G4_DATA_DIR)
        g4_elem.bind.assert_called_with("<Return>", "_ENTER")


class TestUpdateImagingModeFields:
    def test_updates_all_field_elements(
        self, view: MainView, mock_window: MagicMock
    ) -> None:
        keys = [
            ROTATION_RATE,
            TUBE_VOLTAGE,
            EXPOSURE,
            FAN_MODE,
            TIMELINE_END,
            FIELD_X1,
            FIELD_X2,
            FIELD_Y1,
            FIELD_Y2,
            BLADE_X1,
            BLADE_X2,
            BLADE_Y1,
            BLADE_Y2,
            CTDI_PHANTOM,
        ]
        elements = _make_element_dict(keys)
        mock_window.__getitem__ = MagicMock(side_effect=lambda k: elements[k])

        mode = ImagingMode(
            rotation_rate="0.4 deg/s",
            voltage="100 kV",
            exposure="150 mAs",
            fan_mode="Full Fan",
            timeline_end="501 s",
            field_x1="14 cm",
            field_x2="14.0 cm",
            field_y1="10.7 cm",
            field_y2="10.7 cm",
            blade_x1="6.175536078965273 cm",
            blade_x2="-6.175536078965273 cm",
            blade_y1="5.814471115800571 cm",
            blade_y2="-5.814471115800571 cm",
            ctdi_phantom="16 cm",
            dose_factor="1.0",
            start_angle="0 deg",
            fan_detail="Full Fan",
            no_projections="680",
            proj_increment="0.5 deg",
            acquisition_time="340 s",
            ctdiw_reference="TBD",
        )

        view.update_imaging_mode_fields(mode)

        elements[ROTATION_RATE].update.assert_called_with(mode.rotation_rate)
        elements[TUBE_VOLTAGE].update.assert_called_with(mode.voltage)
        elements[EXPOSURE].update.assert_called_with(mode.exposure)
        elements[FAN_MODE].update.assert_called_with(mode.fan_mode)
        elements[TIMELINE_END].update.assert_called_with(mode.timeline_end)
        elements[FIELD_X1].update.assert_called_with(mode.field_x1)
        elements[FIELD_X2].update.assert_called_with(mode.field_x2)
        elements[FIELD_Y1].update.assert_called_with(mode.field_y1)
        elements[FIELD_Y2].update.assert_called_with(mode.field_y2)
        elements[BLADE_X1].update.assert_called_with(mode.blade_x1)
        elements[BLADE_X2].update.assert_called_with(mode.blade_x2)
        elements[BLADE_Y1].update.assert_called_with(mode.blade_y1)
        elements[BLADE_Y2].update.assert_called_with(mode.blade_y2)
        elements[CTDI_PHANTOM].update.assert_called_with(mode.ctdi_phantom)


class TestSetTabVisibility:
    def test_dicom_type_shows_dicom_hides_ctdi(
        self, view: MainView, mock_window: MagicMock
    ) -> None:
        keys = [DICOM_TAB, CTDI_TAB]
        elements = _make_element_dict(keys)
        mock_window.__getitem__ = MagicMock(side_effect=lambda k: elements[k])

        view.set_tab_visibility("DICOM")

        elements[DICOM_TAB].update.assert_called_with(visible=True)
        elements[CTDI_TAB].update.assert_called_with(visible=False)

    def test_ctdi_type_shows_ctdi_hides_dicom(
        self, view: MainView, mock_window: MagicMock
    ) -> None:
        keys = [DICOM_TAB, CTDI_TAB]
        elements = _make_element_dict(keys)
        mock_window.__getitem__ = MagicMock(side_effect=lambda k: elements[k])

        view.set_tab_visibility("CTDI")

        elements[CTDI_TAB].update.assert_called_with(visible=True)
        elements[DICOM_TAB].update.assert_called_with(visible=False)


class TestResetAll:
    def test_updates_all_keys_and_hides_tabs(
        self, view: MainView, mock_window: MagicMock
    ) -> None:
        all_keys = ["key1", "key2", DICOM_TAB, CTDI_TAB]
        elements = _make_element_dict(all_keys)
        mock_window.__getitem__ = MagicMock(side_effect=lambda k: elements[k])

        defaults: Dict[str, Any] = {"key1": "val1", "key2": "val2"}
        view.reset_all(defaults)

        elements["key1"].update.assert_called_with("val1")
        elements["key2"].update.assert_called_with("val2")
        elements[DICOM_TAB].update.assert_called_with(visible=False)
        elements[CTDI_TAB].update.assert_called_with(visible=False)


class TestUpdatePatientId:
    def test_updates_patient_id_element(
        self, view: MainView, mock_window: MagicMock
    ) -> None:
        elements = {PATIENT_ID: MagicMock()}
        mock_window.__getitem__ = MagicMock(side_effect=lambda k: elements[k])

        view.update_patient_id("PAT001")

        elements[PATIENT_ID].update.assert_called_with("PAT001")


class TestUpdateIsocenter:
    def test_updates_iso_xyz(self, view: MainView, mock_window: MagicMock) -> None:
        keys = [ISO_X, ISO_Y, ISO_Z]
        elements = _make_element_dict(keys)
        mock_window.__getitem__ = MagicMock(side_effect=lambda k: elements[k])

        view.update_isocenter("1 mm", "2 mm", "3 mm")

        elements[ISO_X].update.assert_called_with("1 mm")
        elements[ISO_Y].update.assert_called_with("2 mm")
        elements[ISO_Z].update.assert_called_with("3 mm")


class TestSetCouchVisible:
    def test_visible_true(self, view: MainView, mock_window: MagicMock) -> None:
        elements = {COUCH: MagicMock()}
        mock_window.__getitem__ = MagicMock(side_effect=lambda k: elements[k])

        view.set_couch_visible(True)

        elements[COUCH].update.assert_called_with(visible=True)

    def test_visible_false(self, view: MainView, mock_window: MagicMock) -> None:
        elements = {COUCH: MagicMock()}
        mock_window.__getitem__ = MagicMock(side_effect=lambda k: elements[k])

        view.set_couch_visible(False)

        elements[COUCH].update.assert_called_with(visible=False)


class TestSetBladeVisible:
    def test_visible_true(self, view: MainView, mock_window: MagicMock) -> None:
        elements = {CTDI_BLADE: MagicMock()}
        mock_window.__getitem__ = MagicMock(side_effect=lambda k: elements[k])

        view.set_blade_visible(True)

        elements[CTDI_BLADE].update.assert_called_with(visible=True)

    def test_visible_false(self, view: MainView, mock_window: MagicMock) -> None:
        elements = {CTDI_BLADE: MagicMock()}
        mock_window.__getitem__ = MagicMock(side_effect=lambda k: elements[k])

        view.set_blade_visible(False)

        elements[CTDI_BLADE].update.assert_called_with(visible=False)


class TestShowError:
    def test_calls_sg_popup_error(self, view: MainView) -> None:
        with patch("src.gui.view.sg.popup_error") as mock_popup:
            view.show_error("msg")
        mock_popup.assert_called_with("msg")


class TestShowPopup:
    def test_calls_sg_popup_with_value(self, view: MainView) -> None:
        with patch("src.gui.view.sg.popup") as mock_popup:
            view.show_popup("msg", 42)
        mock_popup.assert_called_with("msg", 42, auto_close=True, non_blocking=True)

    def test_calls_sg_popup_without_value(self, view: MainView) -> None:
        with patch("src.gui.view.sg.popup") as mock_popup:
            view.show_popup("msg")
        mock_popup.assert_called_with("msg", None, auto_close=True, non_blocking=True)


class TestClose:
    def test_calls_window_close(self, view: MainView, mock_window: MagicMock) -> None:
        view.close()
        mock_window.close.assert_called_once()
