import logging
import os

import FreeSimpleGUI as sg
from pydicom import dcmread
from src.config import SimulationConfig
from src.orchestrator import Orchestrator
from src.guilayers import *
from src.imaging_modes_lookuptable import imaging_modes_lookup


main_layout = [[main_menu_information_layer], [general_layer], [function_layer]]

chamber_layout = [
    [CTDI_information_layer],
    [CTDI_layer, Couch_layer, CTDI_blade_layer],
    [CTDI_run_layer],
]

dicom_layout = [
    [dicom_information_layer],
    [dicom_file_layer],
    [sg.Text("")],
    [dicom_patient_layer, dicom_planned_layer, dicom_graphics_layer],
]

others_layout = [
    [settings_information_layout],
    [imaging_scan_layer, imaging_protocol_layer, History_layer],
    [Hidden_layer],
]

layout = [
    [
        sg.Text(
            "Monte Carlo - Dose Calculation for Risk Evaluation",
            justification="center",
            text_color="dark blue",
            font=("", 40, "bold"),
        )
    ],
    [
        sg.TabGroup(
            [
                [
                    sg.Tab("Main menu", main_layout),
                    sg.Tab("Simulation settings", others_layout),
                    sg.Tab(
                        "DICOM adjustments menu",
                        dicom_layout,
                        key="-DICOM_TAB-",
                        visible=False,
                    ),
                    sg.Tab(
                        "CTDI phantom menu",
                        chamber_layout,
                        key="-CTDI_TAB-",
                        visible=False,
                    ),
                ]
            ],
            key="-TAB GROUP-",
            expand_x=True,
            expand_y=True,
        ),
    ],
]

sg.set_options(scaling=1)
window = sg.Window(
    title="MC-DCaRE", layout=layout, finalize=True, auto_size_text=True, font=("", 15)
)

path = os.getcwd()
initiate = True
orchestrator = Orchestrator(path)
window["-G4_DATA_DIR-"].bind("<Return>", "_ENTER")

while True:
    event, values = window.read()

    if initiate:
        values_default = values
        values_default["Browse"] = values_default["Browse0"] = values_default[
            "Browse1"
        ] = values_default["Browse2"] = "Browse"
        initiate = False

    if event == "-RESET-":
        for i in values:
            window[i].update(values_default[i])
        window["-CTDI_TAB-"].update(visible=False)
        window["-DICOM_TAB-"].update(visible=False)

    if event == "-G4_DATA_DIR-_ENTER":
        logging.debug("GUI values dump: %s", repr(values))

    if event == "-SIM_TYPE-":
        if values["-SIM_TYPE-"] == "DICOM":
            window["-DICOM_TAB-"].update(visible=True)
            window["-CTDI_TAB-"].update(visible=False)
        elif values["-SIM_TYPE-"] == "CTDI validation":
            window["-CTDI_TAB-"].update(visible=True)
            window["-DICOM_TAB-"].update(visible=False)

    if event == "-DICOM_DIR-":
        count_of_CT_images = 0
        try:
            DICOM_PATH = values["-DICOM_DIR-"]
            list_of_files = os.listdir(DICOM_PATH)
            for files in list_of_files:
                if dcmread(os.path.join(DICOM_PATH, files)).Modality == "CT":
                    if count_of_CT_images == 0:
                        count_of_CT_images += 1
                        patient_ID = dcmread(os.path.join(DICOM_PATH, files)).PatientID
                    elif count_of_CT_images != 0:
                        if (
                            dcmread(os.path.join(DICOM_PATH, files)).PatientID
                            == patient_ID
                        ):
                            count_of_CT_images += 1
                        else:
                            raise RuntimeError(
                                "Multiple different patient IDs found in CT image set"
                            )
            values["-PATIENT_ID-"] = patient_ID
            window["-PATIENT_ID-"].update(values["-PATIENT_ID-"])
            sg.popup(
                "Number of " + patient_ID + " CT images found",
                count_of_CT_images,
                auto_close=True,
                non_blocking=True,
            )
        except Exception as e:
            sg.popup_error(
                "No CT images found in the folder or more than 1 patient file found: "
                + str(e)
            )

    if event == "-DICOM_RP-":
        if dcmread(values["-DICOM_RP-"]).PatientID == values["-PATIENT_ID-"]:
            try:
                isocentre_coors = (
                    dcmread(values["-DICOM_RP-"])
                    .BeamSequence[0]
                    .ControlPointSequence[0]
                    .IsocenterPosition
                )
                values["-ISO_X-"] = str(round(isocentre_coors[0], 5)) + " mm"
                values["-ISO_Y-"] = str(round(isocentre_coors[1], 5)) + " mm"
                values["-ISO_Z-"] = str(round(isocentre_coors[2], 5)) + " mm"
                window["-ISO_X-"].update(values["-ISO_X-"])
                window["-ISO_Y-"].update(values["-ISO_Y-"])
                window["-ISO_Z-"].update(values["-ISO_Z-"])
            except Exception as e:
                sg.popup_error("No isocentre found: " + str(e))
        else:
            sg.popup_error(
                "Patient ID for the CT image set and treatment plan does not match"
            )

    if event == "-DICOM_RUN-":
        try:
            config = SimulationConfig.from_gui_values(values)
            rundir = orchestrator.run_dicom_simulation(config)
            sg.popup(rundir)
        except Exception as e:
            sg.popup_error(
                "Ensure that you have specified a valid DICOM folder and file: "
                + str(e)
            )

    if event == "-CTDI_RUN-":
        try:
            config = SimulationConfig.from_gui_values(values)
            rundir = orchestrator.run_ctdi_simulation(config)
            sg.popup(rundir)
        except Exception as e:
            sg.popup_error("CTDI simulation failed: " + str(e))

    if event == "-IMAGING_MODE-" or event == "-SCAN_TYPE-":
        imagemode = values["-SCAN_TYPE-"] + "_" + values["-IMAGING_MODE-"]
        (
            rotrate,
            voltage,
            exposure,
            fan,
            timeend,
            fieldx1,
            fieldx2,
            fieldy1,
            fieldy2,
            bladex1,
            bladex2,
            bladey1,
            bladey2,
        ) = imaging_modes_lookup[imagemode]
        values["-ROTATION_RATE-"] = rotrate
        values["-TUBE_VOLTAGE-"] = voltage
        values["-EXPOSURE-"] = exposure
        values["-FAN_MODE-"] = fan
        values["-TIMELINE_END-"] = timeend
        values["-FIELD_X1-"] = fieldx1
        values["-FIELD_X2-"] = fieldx2
        values["-FIELD_Y1-"] = fieldy1
        values["-FIELD_Y2-"] = fieldy2
        values["-BLADE_X1-"] = bladex1
        values["-BLADE_X2-"] = bladex2
        values["-BLADE_Y1-"] = bladey1
        values["-BLADE_Y2-"] = bladey2

        window["-ROTATION_RATE-"].update(values["-ROTATION_RATE-"])
        window["-TUBE_VOLTAGE-"].update(values["-TUBE_VOLTAGE-"])
        window["-EXPOSURE-"].update(values["-EXPOSURE-"])
        window["-FAN_MODE-"].update(values["-FAN_MODE-"])
        window["-TIMELINE_END-"].update(values["-TIMELINE_END-"])
        window["-FIELD_X1-"].update(values["-FIELD_X1-"])
        window["-FIELD_X2-"].update(values["-FIELD_X2-"])
        window["-FIELD_Y1-"].update(values["-FIELD_Y1-"])
        window["-FIELD_Y2-"].update(values["-FIELD_Y2-"])
        window["-BLADE_X1-"].update(values["-BLADE_X1-"])
        window["-BLADE_X2-"].update(values["-BLADE_X2-"])
        window["-BLADE_Y1-"].update(values["-BLADE_Y1-"])
        window["-BLADE_Y2-"].update(values["-BLADE_Y2-"])

    if event == "-COUCH_ENABLED-":
        window["-COUCH-"].update(visible=values["-COUCH_ENABLED-"])

    if event == "-CTDI_USER_BLADE-":
        window["-CTDI_BLADE-"].update(visible=values["-CTDI_USER_BLADE-"])

    if event == sg.WIN_CLOSED:
        break

window.close()
