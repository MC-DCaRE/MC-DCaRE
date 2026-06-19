"""Event-loop controller that wires GUI events to the Orchestrator.

Exports :class:`GUIController`, which reads events from :class:`MainView`
and delegates each event to the appropriate handler or simulation action.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Callable, Dict

import FreeSimpleGUI as sg
from pydicom import dcmread
from src.gui.adapter import gui_to_config
from src.gui.view import MainView
from src.models.imaging_mode import IMAGING_MODES
from src.models.keys import (
    CTDI_RUN,
    CTDI_USER_BLADE,
    COUCH_ENABLED,
    DICOM_DIR,
    DICOM_RP,
    DICOM_RUN,
    G4_DATA_DIR,
    IMAGING_MODE,
    PATIENT_ID,
    PHANTOM_RUN,
    RESET,
    SCAN_TYPE,
    SIM_TYPE,
)
from src.orchestrator import Orchestrator

logger = logging.getLogger(__name__)


class GUIController:
    """Connects FreeSimpleGUI events from *view* to the *orchestrator*."""

    def __init__(self, view: MainView, orchestrator: Orchestrator) -> None:
        """Wire up *view* and *orchestrator* and register event handlers."""
        self.view = view
        self.orchestrator = orchestrator
        self._default_values: Dict[str, Any] = {}
        self._first_read: bool = True
        self._event_handlers: Dict[str, Callable[[Dict[str, Any]], None]] = {
            RESET: self._on_reset,
            SIM_TYPE: self._on_sim_type_change,
            DICOM_DIR: self._on_dicom_dir,
            DICOM_RP: self._on_dicom_rp,
            DICOM_RUN: self._on_run,
            CTDI_RUN: self._on_run,
            PHANTOM_RUN: self._on_run,
            IMAGING_MODE: self._on_imaging_mode_change,
            SCAN_TYPE: self._on_imaging_mode_change,
            COUCH_ENABLED: self._on_couch_toggle,
            CTDI_USER_BLADE: self._on_user_blade_toggle,
        }

    def run(self) -> None:
        """Run the main event loop until the window is closed."""
        while True:
            event, values = self.view.read()
            if self._first_read:
                self._default_values = dict(values)
                self._default_values["Browse"] = self._default_values[
                    "Browse0"
                ] = self._default_values["Browse1"] = self._default_values[
                    "Browse2"
                ] = "Browse"
                self._first_read = False
            if event == sg.WIN_CLOSED:
                break
            if event == G4_DATA_DIR + "_ENTER":
                logger.debug("GUI values dump: %s", repr(values))
            handler = self._event_handlers.get(event)
            if handler:
                handler(values)

    def _on_reset(self, values: Dict[str, Any]) -> None:
        """Restore all GUI elements to their initial defaults."""
        self.view.reset_all(self._default_values)

    def _on_sim_type_change(self, values: Dict[str, Any]) -> None:
        """Switch visible tab based on the selected simulation type."""
        self.view.set_tab_visibility(values[SIM_TYPE])

    def _on_dicom_dir(self, values: Dict[str, Any]) -> None:
        """Load and validate CT images from the selected DICOM directory."""
        count_of_CT_images = 0
        patient_ID = ""
        try:
            dicom_path = values[DICOM_DIR]
            list_of_files = os.listdir(dicom_path)
            for file in list_of_files:
                ds = dcmread(os.path.join(dicom_path, file))
                if ds.Modality == "CT":
                    if count_of_CT_images == 0:
                        count_of_CT_images += 1
                        patient_ID = ds.PatientID
                    else:
                        if ds.PatientID == patient_ID:
                            count_of_CT_images += 1
                        else:
                            raise RuntimeError("Multiple different patient IDs found")
            if count_of_CT_images == 0:
                self.view.show_error("No CT images found in directory")
                return
            self.view.update_patient_id(patient_ID)
            self.view.show_popup(
                "Number of " + patient_ID + " CT images found", count_of_CT_images
            )
        except Exception as e:
            logger.error("Error loading DICOM directory: %s", e, exc_info=True)
            self.view.show_error(
                "No CT images found or more than 1 patient file found: " + str(e)
            )

    def _on_dicom_rp(self, values: Dict[str, Any]) -> None:
        """Extract the isocenter from the selected DICOM RT Plan file."""
        ds = dcmread(values[DICOM_RP])
        if ds.PatientID == values[PATIENT_ID]:
            try:
                iso = ds.BeamSequence[0].ControlPointSequence[0].IsocenterPosition
                self.view.update_isocenter(
                    str(round(iso[0], 5)) + " mm",
                    str(round(iso[1], 5)) + " mm",
                    str(round(iso[2], 5)) + " mm",
                )
            except Exception as e:
                logger.error("Error extracting isocenter: %s", e, exc_info=True)
                self.view.show_error("No isocentre found: " + str(e))
        else:
            self.view.show_error(
                "Patient ID for the CT image set and treatment plan does not match"
            )

    def _on_run(self, values: Dict[str, Any]) -> None:
        """Build a config from GUI values and launch the simulation."""
        try:
            config = gui_to_config(values)
            rundir = self.orchestrator.run(config)
            self.view.show_popup(rundir)
        except Exception as e:
            logger.error("Simulation failed: %s", e, exc_info=True)
            self.view.show_error("Simulation failed: " + str(e))

    def _on_imaging_mode_change(self, values: Dict[str, Any]) -> None:
        """Look up the imaging mode and refresh protocol fields."""
        mode_key = values[SCAN_TYPE] + "_" + values[IMAGING_MODE]
        mode = IMAGING_MODES[mode_key]
        self.view.update_imaging_mode_fields(mode)

    def _on_couch_toggle(self, values: Dict[str, Any]) -> None:
        """Show or hide the couch dimension frame."""
        self.view.set_couch_visible(bool(values[COUCH_ENABLED]))

    def _on_user_blade_toggle(self, values: Dict[str, Any]) -> None:
        """Show or hide the user-specified jaw-position frame."""
        self.view.set_blade_visible(bool(values[CTDI_USER_BLADE]))
