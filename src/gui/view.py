"""FreeSimpleGUI layout and view helpers for the MC-DCaRE desktop application.

Exports :class:`MainView`, the primary window class that constructs and
manages all GUI elements (tabs, frames, inputs) for simulation configuration.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

import FreeSimpleGUI as sg
from src.config import SimulationConfig
from src.models.imaging_mode import IMAGING_MODES, ImagingMode
from src.models.keys import (
    BLADE_X1,
    BLADE_X2,
    BLADE_Y1,
    BLADE_Y2,
    COUCH,
    COUCH_ENABLED,
    COUCH_LENGTH,
    COUCH_THICKNESS,
    COUCH_WIDTH,
    CTDI_BLADE,
    CTDI_FIELD_X1,
    CTDI_FIELD_X2,
    CTDI_FIELD_Y1,
    CTDI_FIELD_Y2,
    CTDI_GRAPHICS,
    CTDI_PHANTOM,
    CTDI_PHSP_FILE,
    CTDI_PHSP_MODE,
    CTDI_PHSP_MULTIPLE_USE,
    CTDI_RUN,
    CTDI_TAB,
    CTDI_USER_BLADE,
    DICOM_DIR,
    DICOM_GRAPHICS,
    DICOM_RP,
    DICOM_RUN,
    DICOM_TAB,
    DTM_ZBINS,
    DTW_ZBINS,
    EXPOSURE,
    FAN_MODE,
    FIELD_X1,
    FIELD_X2,
    FIELD_Y1,
    FIELD_Y2,
    G4_DATA_DIR,
    HISTORIES,
    IMAGING_MODE,
    ISO_X,
    ISO_Y,
    ISO_Z,
    PATIENT_ID,
    PATIENT_PITCH,
    PATIENT_ROLL,
    PATIENT_YAW,
    PHANTOM_COUCH_ENABLED,
    PHANTOM_COUCH_LENGTH,
    PHANTOM_COUCH_THICKNESS,
    PHANTOM_COUCH_WIDTH,
    PHANTOM_DATA_DIR,
    PHANTOM_GRAPHICS,
    PHANTOM_ROT_X,
    PHANTOM_ROT_Y,
    PHANTOM_ROT_Z,
    PHANTOM_RUN,
    PHANTOM_SEX,
    PHANTOM_TAB,
    PHANTOM_TRANS_X,
    PHANTOM_TRANS_Y,
    PHANTOM_TRANS_Z,
    RESET,
    ROTATION_RATE,
    SCAN_TYPE,
    SEED,
    SEQ_TIMES,
    SHIFT_X,
    SHIFT_Y,
    SHIFT_Z,
    SIM_TYPE,
    START_ANGLE,
    TAB_GROUP,
    THREADS,
    TIMELINE_END,
    TLE_ZBINS,
    TOPAS_DIR,
    TUBE_VOLTAGE,
)


class MainView:
    """Top-level application window with tabbed layout for MC-DCaRE simulations."""

    def __init__(self) -> None:
        """Build the window from default configuration values and finalize it."""
        self._defaults = SimulationConfig.defaults()
        self.window: sg.Window = sg.Window(
            title="MC-DCaRE",
            layout=self._build_layout(),
            finalize=True,
            auto_size_text=True,
            font=("", 15),
        )
        self.window[G4_DATA_DIR].bind("<Return>", "_ENTER")

    def _build_layout(self) -> List[List[Any]]:
        """Assemble all tabs and the title bar into the full window layout."""
        main_layout = [
            [self._build_main_menu_information()],
            [self._build_general_layer()],
            [self._build_function_layer()],
        ]
        chamber_layout = [
            [self._build_ctdi_information()],
            [
                self._build_ctdi_layer(),
                self._build_couch_layer(),
                self._build_ctdi_blade_layer(),
                self._build_ctdi_phase_space_layer(),
            ],
            [self._build_ctdi_run_layer()],
        ]
        dicom_layout = [
            [self._build_dicom_information()],
            [self._build_dicom_file_layer()],
            [sg.Text("")],
            [
                self._build_dicom_patient_layer(),
                self._build_dicom_planned_layer(),
                self._build_dicom_graphics_layer(),
            ],
        ]
        phantom_layout = [
            [self._build_phantom_information()],
            [self._build_phantom_data_layer()],
            [sg.Text("")],
            [
                self._build_phantom_placement_layer(),
                self._build_phantom_couch_layer(),
            ],
            [self._build_phantom_run_layer()],
        ]
        others_layout = [
            [self._build_settings_information()],
            [
                self._build_imaging_scan_layer(),
                self._build_imaging_protocol_layer(),
                self._build_history_layer(),
            ],
            [self._build_hidden_layer()],
        ]
        return [
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
                                key=DICOM_TAB,
                                visible=False,
                            ),
                            sg.Tab(
                                "CTDI phantom menu",
                                chamber_layout,
                                key=CTDI_TAB,
                                visible=False,
                            ),
                            sg.Tab(
                                "ICRP 145 phantom menu",
                                phantom_layout,
                                key=PHANTOM_TAB,
                                visible=False,
                            ),
                        ]
                    ],
                    key=TAB_GROUP,
                    expand_x=True,
                    expand_y=True,
                ),
            ],
        ]

    def _build_general_layer(self) -> sg.Frame:
        """Geant4 and TOPAS directory inputs with a reset button."""
        d = self._defaults
        return sg.Frame(
            "General Settings",
            [
                [
                    sg.Text("Geant4 Data Directory", size=(17, 1), text_color="black"),
                    sg.In(
                        default_text=d.general.g4_data_directory,
                        key=G4_DATA_DIR,
                        size=(50, 1),
                        enable_events=True,
                    ),
                    sg.FolderBrowse(button_text="Browse", key="Browse"),
                ],
                [
                    sg.Text("TOPAS Directory", size=(17, 1), text_color="black"),
                    sg.In(
                        default_text=d.general.topas_directory,
                        key=TOPAS_DIR,
                        size=(50, 1),
                        enable_events=True,
                    ),
                    sg.FileBrowse(button_text="Browse", key="Browse0"),
                ],
                [sg.Button(button_text="Reset all parameters to default", key=RESET)],
            ],
        )

    def _build_main_menu_information(self) -> sg.Frame:
        """Instructional text displayed on the main-menu tab."""
        return sg.Frame(
            "Instructions on the usage of the GUI",
            [
                [
                    sg.Text(
                        "Select your Topas and G4 data directories. Next, select the function you would like to enable. "
                    )
                ],
                [
                    sg.Text(
                        "   DICOM allows the user to specify a patient DICOM CT image folder to run simulations on"
                    )
                ],
                [
                    sg.Text(
                        "   CTDI validation is for running simulations on CTDI phantom"
                    )
                ],
                [
                    sg.Text(
                        "In the following pages, type in your desired value, a whitespace followed by the unit. Eg. 5 mm"
                    )
                ],
                [
                    sg.Text(
                        "XYZ corresponds to patient coordinate system; Left = +X, Posterior = +Y, Head = +Z"
                    )
                ],
                [
                    sg.Text(
                        "The scan angle is defined from the kV imaging source, if the kV source in on top of the patient, this is 0 degrees"
                    )
                ],
            ],
        )

    def _build_function_layer(self) -> sg.Frame:
        """Simulation-type selector (DICOM, CTDI, or ICRP145)."""
        return sg.Frame(
            "Choose your function",
            [
                [
                    sg.Text("Simulation Type", size=(20, 1), text_color="black"),
                    sg.Combo(
                        ["DICOM", "CTDI", "ICRP145"],
                        default_value=None,
                        key=SIM_TYPE,
                        readonly=True,
                        enable_events=True,
                        size=20,
                    ),
                ],
            ],
        )

    def _build_settings_information(self) -> sg.Frame:
        """Instructional text displayed on the settings tab."""
        return sg.Frame(
            "General settings",
            [
                [
                    sg.Text(
                        "This page contains general settings used for all simulations."
                    )
                ],
                [
                    sg.Text(
                        "You will be able to control the granularity of the simulations along with the scan parameters here."
                    )
                ],
                [
                    sg.Text(
                        "To use kV-kV option, the user will have to manually input the desired angle."
                    )
                ],
                [
                    sg.Text(
                        "For 2 or more kV-kV angles, please run the indivual angles separately."
                    )
                ],
                [
                    sg.Text(
                        "It is a known issue where using more threads than what your computer can support will result in the simulation failing."
                    )
                ],
            ],
        )

    def _build_hidden_layer(self) -> sg.Frame:
        """Time-feature and collimator-blade fields (hidden by default)."""
        d = self._defaults
        return sg.Frame(
            "Time Feature and other hidden values",
            [
                [
                    sg.Text("Timeline End", size=(14, 1), text_color="black"),
                    sg.In(
                        default_text=str(d.imaging.timeline_end),
                        key=TIMELINE_END,
                        size=(10, 1),
                        enable_events=True,
                    ),
                ],
                [
                    sg.Text("Gantry Rotation Rate", size=(14, 1), text_color="black"),
                    sg.In(
                        default_text=str(d.imaging.rotation_rate),
                        key=ROTATION_RATE,
                        size=(15, 1),
                        enable_events=True,
                        readonly=True,
                    ),
                ],
                [
                    sg.In(
                        default_text=str(d.imaging.blade_x1),
                        key=BLADE_X1,
                        size=(10, 1),
                        text_color="black",
                        enable_events=True,
                        readonly=True,
                    )
                ],
                [
                    sg.In(
                        default_text=str(d.imaging.blade_x2),
                        key=BLADE_X2,
                        size=(10, 1),
                        text_color="black",
                        enable_events=True,
                        readonly=True,
                    )
                ],
                [
                    sg.In(
                        default_text=str(d.imaging.blade_y1),
                        key=BLADE_Y1,
                        size=(10, 1),
                        text_color="black",
                        enable_events=True,
                        readonly=True,
                    )
                ],
                [
                    sg.In(
                        default_text=str(d.imaging.blade_y2),
                        key=BLADE_Y2,
                        size=(10, 1),
                        text_color="black",
                        enable_events=True,
                        readonly=True,
                    )
                ],
            ],
            visible=False,
        )

    def _build_history_layer(self) -> sg.Frame:
        """Seed, threads, sequential times, and history-count inputs."""
        d = self._defaults
        return sg.Frame(
            "Simulation settings",
            [
                [
                    sg.Text("Random Seed", size=(10, 1), text_color="black"),
                    sg.In(
                        default_text=d.general.seed,
                        key=SEED,
                        size=(10, 1),
                        enable_events=True,
                    ),
                ],
                [
                    sg.Text("CPU Threads", size=(10, 1), text_color="black"),
                    sg.In(
                        default_text=d.general.threads,
                        key=THREADS,
                        size=(10, 1),
                        enable_events=True,
                    ),
                ],
                [
                    sg.Text("Sequential Time Steps", size=(10, 1), text_color="black"),
                    sg.In(
                        default_text=d.imaging.sequential_times,
                        key=SEQ_TIMES,
                        size=(10, 1),
                        enable_events=True,
                    ),
                ],
                [
                    sg.Text("Number of Histories", size=(10, 1), text_color="black"),
                    sg.In(
                        default_text=d.general.histories,
                        key=HISTORIES,
                        size=(10, 1),
                        enable_events=True,
                    ),
                ],
            ],
            vertical_alignment="top",
        )

    @staticmethod
    def _cbct_protocol_names() -> list[str]:
        """Extract unique CBCT protocol names from IMAGING_MODES keys."""
        seen: set[str] = set()
        names: list[str] = []
        for key in IMAGING_MODES:
            if not key.startswith("CBCT "):
                continue
            _, _, name = key.partition("_")
            if name not in seen:
                seen.add(name)
                names.append(name)
        return names

    def _build_imaging_protocol_layer(self) -> sg.Frame:
        """Imaging-protocol dropdown and read-only field-size / bowtie fields."""
        d = self._defaults
        return sg.Frame(
            "Imaging protocol",
            [
                [
                    sg.Text("Imaging Protocol", size=(10, 1), text_color="black"),
                    sg.Combo(
                        self._cbct_protocol_names(),
                        default_value="Image Gently",
                        key=IMAGING_MODE,
                        readonly=True,
                        enable_events=True,
                    ),
                ],
                [
                    sg.Text("Bowtie Filter Mode", size=(10, 1), text_color="black"),
                    sg.In(
                        default_text=d.imaging.fan_mode,
                        key=FAN_MODE,
                        size=(15, 1),
                        text_color="black",
                        enable_events=True,
                        readonly=True,
                    ),
                ],
                [
                    sg.Text("Field Size X1", size=(10, 1), text_color="black"),
                    sg.In(
                        default_text=str(d.imaging.field_x1),
                        key=FIELD_X1,
                        size=(15, 1),
                        text_color="black",
                        enable_events=True,
                        readonly=True,
                    ),
                ],
                [
                    sg.Text("Field Size X2", size=(10, 1), text_color="black"),
                    sg.In(
                        default_text=str(d.imaging.field_x2),
                        key=FIELD_X2,
                        size=(15, 1),
                        text_color="black",
                        enable_events=True,
                        readonly=True,
                    ),
                ],
                [
                    sg.Text("Field Size Y1", size=(10, 1), text_color="black"),
                    sg.In(
                        default_text=str(d.imaging.field_y1),
                        key=FIELD_Y1,
                        size=(15, 1),
                        text_color="black",
                        enable_events=True,
                        readonly=True,
                    ),
                ],
                [
                    sg.Text("Field Size Y2", size=(10, 1), text_color="black"),
                    sg.In(
                        default_text=str(d.imaging.field_y2),
                        key=FIELD_Y2,
                        size=(15, 1),
                        text_color="black",
                        enable_events=True,
                        readonly=True,
                    ),
                ],
            ],
        )

    def _build_imaging_scan_layer(self) -> sg.Frame:
        """Start-angle, scan-type, tube-voltage, and exposure inputs."""
        d = self._defaults
        return sg.Frame(
            "Set up imaging parameters",
            [
                [
                    sg.Text("Start Angle", size=(12, 1), text_color="black"),
                    sg.In(
                        default_text=str(d.imaging.start_angle),
                        key=START_ANGLE,
                        size=(15, 1),
                        enable_events=True,
                    ),
                ],
                [
                    sg.Text("Scan Type", size=(12, 1), text_color="black"),
                    sg.Combo(
                        ["CBCT Clockwise", "CBCT Anticlockwise", "kV-kV"],
                        default_value="CBCT Clockwise",
                        key=SCAN_TYPE,
                        readonly=True,
                        enable_events=True,
                        size=(15, 1),
                    ),
                ],
                [
                    sg.Text("Tube Voltage (kVp)", size=(12, 1), text_color="black"),
                    sg.In(
                        default_text=str(d.imaging.anode_voltage),
                        key=TUBE_VOLTAGE,
                        size=(15, 1),
                        enable_events=True,
                    ),
                ],
                [
                    sg.Text("Tube Current (mAs)", size=(12, 1), text_color="black"),
                    sg.In(
                        default_text=str(d.imaging.exposure),
                        key=EXPOSURE,
                        size=(15, 1),
                        enable_events=True,
                    ),
                ],
            ],
            vertical_alignment="top",
        )

    def _build_dicom_information(self) -> sg.Frame:
        """Instructional text displayed on the DICOM tab."""
        return sg.Frame(
            "Instructions on the usage of the DICOM adjustments",
            [
                [
                    sg.Text(
                        "The programme automatically shifts the patient such that the isocentre of the treatment plan is matched to the isocentre of the beam."
                    )
                ],
                [
                    sg.Text(
                        "For patient set up adjustments, make any adjustments relative to the ioscentre of the treatment plan."
                    )
                ],
                [
                    sg.Text(
                        "If the first imaging scan was Left, Posterior and Superior of the planned isocentre, this would be a positve XYZ input."
                    )
                ],
                [
                    sg.Text(
                        "Use the previous tab to make edits to other parameters like collimator openings and exposure. "
                    )
                ],
                [sg.Text("The programme currently only supports CT modality.")],
            ],
        )

    def _build_dicom_file_layer(self) -> sg.Frame:
        """DICOM directory, patient-ID, RT-plan file, and run button."""
        d = self._defaults
        return sg.Frame(
            "DICOM inputs",
            [
                [
                    sg.Text("DICOM Image Directory", size=(17, 1), text_color="black"),
                    sg.In(
                        default_text=d.dicom.dicom_directory,
                        key=DICOM_DIR,
                        size=(50, 1),
                        enable_events=True,
                    ),
                    sg.FolderBrowse(button_text="Browse", key="Browse1"),
                ],
                [
                    sg.Text("Loaded Patient ID", size=(17, 1), text_color="black"),
                    sg.In(
                        default_text="",
                        key=PATIENT_ID,
                        size=(17, 1),
                        text_color="black",
                        background_color="light grey",
                        enable_events=True,
                        readonly=True,
                    ),
                ],
                [
                    sg.Text("DICOM RT Plan File", size=(17, 1), text_color="black"),
                    sg.In(
                        default_text=d.dicom.dicom_rp_file,
                        key=DICOM_RP,
                        size=(50, 1),
                        enable_events=True,
                    ),
                    sg.FileBrowse(
                        button_text="Browse",
                        key="Browse2",
                        file_types=(("DICOM File", "*.dcm"),),
                    ),
                ],
                [
                    sg.Button(
                        "Run DICOM Simulation",
                        enable_events=True,
                        key=DICOM_RUN,
                        size=(35, 1),
                    )
                ],
            ],
        )

    def _build_dicom_patient_layer(self) -> sg.Frame:
        """Patient-shift and rotation inputs relative to isocenter."""
        d = self._defaults
        return sg.Frame(
            "Patient set up adjustments",
            [
                [
                    sg.Text("X Shift from Isocenter", size=(14, 1), text_color="black"),
                    sg.In(
                        default_text=str(d.dicom.patient_shift_x),
                        key=SHIFT_X,
                        size=(10, 1),
                        enable_events=True,
                    ),
                ],
                [
                    sg.Text("Y Shift from Isocenter", size=(14, 1), text_color="black"),
                    sg.In(
                        default_text=str(d.dicom.patient_shift_y),
                        key=SHIFT_Y,
                        size=(10, 1),
                        enable_events=True,
                    ),
                ],
                [
                    sg.Text("Z Shift from Isocenter", size=(14, 1), text_color="black"),
                    sg.In(
                        default_text=str(d.dicom.patient_shift_z),
                        key=SHIFT_Z,
                        size=(10, 1),
                        enable_events=True,
                    ),
                ],
                [
                    sg.Text("Patient Yaw Rotation", size=(14, 1), text_color="black"),
                    sg.In(
                        default_text=str(d.dicom.patient_yaw),
                        key=PATIENT_YAW,
                        size=(10, 1),
                        enable_events=True,
                    ),
                ],
                [
                    sg.Text("Patient Pitch Rotation", size=(14, 1), text_color="black"),
                    sg.In(
                        default_text=str(d.dicom.patient_pitch),
                        key=PATIENT_PITCH,
                        size=(10, 1),
                        enable_events=True,
                    ),
                ],
                [
                    sg.Text("Patient Roll Rotation", size=(14, 1), text_color="black"),
                    sg.In(
                        default_text=str(d.dicom.patient_roll),
                        key=PATIENT_ROLL,
                        size=(10, 1),
                        enable_events=True,
                    ),
                ],
            ],
        )

    def _build_dicom_planned_layer(self) -> sg.Frame:
        """Read-only isocenter coordinates extracted from the RT plan."""
        d = self._defaults
        return sg.Frame(
            "Treatment plan parameters",
            [
                [
                    sg.Text("Isocenter X", size=(10, 1), text_color="black"),
                    sg.In(
                        default_text=str(d.dicom.isocenter_x),
                        key=ISO_X,
                        size=(10, 1),
                        enable_events=True,
                        readonly=True,
                    ),
                ],
                [
                    sg.Text("Isocenter Y", size=(10, 1), text_color="black"),
                    sg.In(
                        default_text=str(d.dicom.isocenter_y),
                        key=ISO_Y,
                        size=(10, 1),
                        enable_events=True,
                        readonly=True,
                    ),
                ],
                [
                    sg.Text("Isocenter Z", size=(10, 1), text_color="black"),
                    sg.In(
                        default_text=str(d.dicom.isocenter_z),
                        key=ISO_Z,
                        size=(10, 1),
                        enable_events=True,
                        readonly=True,
                    ),
                ],
            ],
            vertical_alignment="top",
        )

    def _build_dicom_graphics_layer(self) -> sg.Frame:
        """DICOM graphics toggle checkbox with usage warning."""
        return sg.Frame(
            "DICOM simulation graphics",
            [
                [
                    sg.Checkbox(
                        "DICOM Graphics Toggle",
                        enable_events=True,
                        key=DICOM_GRAPHICS,
                        default=False,
                    )
                ],
                [sg.Text("It is highly recommended to never use this ")],
                [sg.Text("due to excessive lag from the large image set. ")],
            ],
            vertical_alignment="top",
        )

    def _build_ctdi_information(self) -> sg.Frame:
        """Instructional text displayed on the CTDI tab."""
        return sg.Frame(
            "Instructions on the usage of the CTDI phantom parameters",
            [
                [
                    sg.Text(
                        "Select the CTDI phantom used for the CTDI validation. The phantom will be automatically centered at isocenter."
                    )
                ],
                [
                    sg.Text(
                        "Simulation will automatically generate and run a single CTDI simulation for all 5 detector positions using parallel worlds."
                    )
                ],
                [
                    sg.Text(
                        "Use the previous tab to make edits to other parameters like collimator openings and exposure. "
                    )
                ],
                [
                    sg.Text(
                        "Use the couch toggle to select or remove the couch from the simulation, depending on your set up"
                    )
                ],
                [
                    sg.Text(
                        "The phantom is automatically placed on top of the couch if the couch is selected."
                    )
                ],
                [
                    sg.Text(
                        "You can also choose to change the thickeness of the couch in terms of its aluminium thickness."
                    )
                ],
            ],
        )

    def _build_ctdi_layer(self) -> sg.Frame:
        """CTDI phantom diameter, scoring bins, couch toggle, and jaw toggle."""
        d = self._defaults
        return sg.Frame(
            "CTDI options",
            [
                [
                    sg.Text("CTDI Phantom Diameter", size=(25, 1), text_color="black"),
                    sg.Combo(
                        ["16 cm", "32 cm"],
                        default_value="16 cm",
                        key=CTDI_PHANTOM,
                        readonly=True,
                    ),
                ],
                [
                    sg.Text("Dose to Medium Z-Bins", size=(25, 1), text_color="black"),
                    sg.In(
                        default_text=d.ctdi.dose_to_medium_zbins,
                        key=DTM_ZBINS,
                        size=(10, 1),
                        enable_events=True,
                    ),
                ],
                [
                    sg.Text(
                        "Track Length Estimator Z-Bins",
                        size=(25, 1),
                        text_color="black",
                    ),
                    sg.In(
                        default_text=d.ctdi.tle_zbins,
                        key=TLE_ZBINS,
                        size=(10, 1),
                        enable_events=True,
                    ),
                ],
                [
                    sg.Text("Dose to Water Z-Bins", size=(25, 1), text_color="black"),
                    sg.In(
                        default_text=d.ctdi.dose_to_water_zbins,
                        key=DTW_ZBINS,
                        size=(10, 1),
                        enable_events=True,
                    ),
                ],
                [
                    sg.Checkbox(
                        "Include Couch",
                        enable_events=True,
                        key=COUCH_ENABLED,
                        default=True,
                    )
                ],
                [
                    sg.Checkbox(
                        "Custom CTDI Jaw Positions",
                        enable_events=True,
                        key=CTDI_USER_BLADE,
                        default=False,
                    )
                ],
            ],
            vertical_alignment="top",
        )

    def _build_couch_layer(self) -> sg.pin:
        """Pinnable frame with couch dimension inputs."""
        d = self._defaults
        return sg.pin(
            sg.Frame(
                "Couch",
                [
                    [
                        sg.Text("Couch Length", size=(8, 1), text_color="black"),
                        sg.In(
                            default_text=str(d.ctdi.couch_length),
                            key=COUCH_LENGTH,
                            size=(10, 1),
                            enable_events=True,
                        ),
                    ],
                    [
                        sg.Text("Couch Width", size=(8, 1), text_color="black"),
                        sg.In(
                            default_text=str(d.ctdi.couch_width),
                            key=COUCH_WIDTH,
                            size=(10, 1),
                            enable_events=True,
                        ),
                    ],
                    [
                        sg.Text("Couch Thickness", size=(8, 1), text_color="black"),
                        sg.In(
                            default_text=str(d.ctdi.couch_thickness),
                            key=COUCH_THICKNESS,
                            size=(10, 1),
                            enable_events=True,
                        ),
                    ],
                ],
                key=COUCH,
                visible=True,
                vertical_alignment="top",
            ),
            shrink=False,
            vertical_alignment="top",
        )

    def _build_ctdi_blade_layer(self) -> sg.pin:
        """Pinnable frame for user-specified CTDI jaw positions."""
        d = self._defaults
        return sg.pin(
            sg.Frame(
                "CTDI user specified jaw",
                [
                    [
                        sg.Text("Field Size X1", size=(10, 1), text_color="black"),
                        sg.In(
                            default_text=str(d.ctdi.user_field_x1),
                            key=CTDI_FIELD_X1,
                            size=(15, 1),
                            text_color="black",
                            enable_events=True,
                        ),
                    ],
                    [
                        sg.Text("Field Size X2", size=(10, 1), text_color="black"),
                        sg.In(
                            default_text=str(d.ctdi.user_field_x2),
                            key=CTDI_FIELD_X2,
                            size=(15, 1),
                            text_color="black",
                            enable_events=True,
                        ),
                    ],
                    [
                        sg.Text("Field Size Y1", size=(10, 1), text_color="black"),
                        sg.In(
                            default_text=str(d.ctdi.user_field_y1),
                            key=CTDI_FIELD_Y1,
                            size=(15, 1),
                            text_color="black",
                            enable_events=True,
                        ),
                    ],
                    [
                        sg.Text("Field Size Y2", size=(10, 1), text_color="black"),
                        sg.In(
                            default_text=str(d.ctdi.user_field_y2),
                            key=CTDI_FIELD_Y2,
                            size=(15, 1),
                            text_color="black",
                            enable_events=True,
                        ),
                    ],
                ],
                key=CTDI_BLADE,
                visible=False,
                vertical_alignment="top",
            ),
            shrink=False,
            vertical_alignment="top",
        )

    def _build_ctdi_phase_space_layer(self) -> sg.Frame:
        """Phase-space score/replay controls (CTDI advanced)."""
        d = self._defaults.ctdi
        return sg.Frame(
            "Phase space (optional)",
            [
                [
                    sg.Text("Mode", size=(22, 1), text_color="black"),
                    sg.Combo(
                        values=["off", "score", "replay"],
                        default_value=d.phase_space_mode,
                        key=CTDI_PHSP_MODE,
                        size=(12, 1),
                        readonly=True,
                        text_color="black",
                    ),
                    sg.Text(
                        "score = write .phsp; replay = reuse a scored .phsp",
                        text_color="gray",
                    ),
                ],
                [
                    sg.Text(
                        "Phase space file (.phsp)", size=(22, 1), text_color="black"
                    ),
                    sg.InputText(
                        default_text=d.phase_space_file,
                        key=CTDI_PHSP_FILE,
                        size=(40, 1),
                        text_color="black",
                    ),
                ],
                [
                    sg.Text("Multiple use (M)", size=(22, 1), text_color="black"),
                    sg.InputText(
                        default_text=str(d.phase_space_multiple_use),
                        key=CTDI_PHSP_MULTIPLE_USE,
                        size=(12, 1),
                        text_color="black",
                    ),
                    sg.Text(
                        "replay only: reuse each particle M times",
                        text_color="gray",
                    ),
                ],
            ],
        )

    def _build_ctdi_run_layer(self) -> sg.Frame:
        """CTDI graphics toggle and simulation run button."""
        return sg.Frame(
            "Activate CTDI simulation",
            [
                [
                    sg.Checkbox(
                        "CTDI Graphics Toggle",
                        enable_events=True,
                        key=CTDI_GRAPHICS,
                        default=False,
                    )
                ],
                [
                    sg.Button(
                        "Run CTDI Simulation",
                        enable_events=True,
                        key=CTDI_RUN,
                        disabled=False,
                        disabled_button_color="grey",
                    )
                ],
            ],
        )

    def _build_phantom_information(self) -> sg.Frame:
        """Instructional text for the ICRP 145 phantom tab."""
        return sg.Frame(
            "ICRP 145 phantom information",
            [
                [
                    sg.Text(
                        "Configure an ICRP 145 adult reference phantom (MRCP-AM/AF) "
                        "for standardized CT dose simulation."
                    )
                ],
                [sg.Text("Requires OpenTOPAS with the TsTetGeom extension.")],
            ],
        )

    def _build_phantom_data_layer(self) -> sg.Frame:
        """Phantom data directory and sex selection."""
        d = self._defaults.phantom
        return sg.Frame(
            "Phantom data",
            [
                [
                    sg.Text("Phantom data directory", size=(22, 1), text_color="black"),
                    sg.InputText(
                        default_text=d.phantom_data_directory,
                        key=PHANTOM_DATA_DIR,
                        size=(40, 1),
                        text_color="black",
                    ),
                ],
                [
                    sg.Text("Phantom sex", size=(22, 1), text_color="black"),
                    sg.Combo(
                        ["AM", "AF"],
                        default_value=d.phantom_sex,
                        key=PHANTOM_SEX,
                        readonly=True,
                        size=10,
                    ),
                ],
            ],
        )

    def _build_phantom_placement_layer(self) -> sg.Frame:
        """Supine placement offsets (translation and rotation)."""
        d = self._defaults.phantom
        return sg.Frame(
            "Placement offsets",
            [
                [
                    sg.Text("Trans X (cm)", size=(15, 1), text_color="black"),
                    sg.InputText(
                        default_text=str(d.trans_x),
                        key=PHANTOM_TRANS_X,
                        size=(15, 1),
                        text_color="black",
                    ),
                ],
                [
                    sg.Text("Trans Y (cm)", size=(15, 1), text_color="black"),
                    sg.InputText(
                        default_text=str(d.trans_y),
                        key=PHANTOM_TRANS_Y,
                        size=(15, 1),
                        text_color="black",
                    ),
                ],
                [
                    sg.Text("Trans Z (cm)", size=(15, 1), text_color="black"),
                    sg.InputText(
                        default_text=str(d.trans_z),
                        key=PHANTOM_TRANS_Z,
                        size=(15, 1),
                        text_color="black",
                    ),
                ],
                [
                    sg.Text("Rot X (deg)", size=(15, 1), text_color="black"),
                    sg.InputText(
                        default_text=str(d.rot_x),
                        key=PHANTOM_ROT_X,
                        size=(15, 1),
                        text_color="black",
                    ),
                ],
                [
                    sg.Text("Rot Y (deg)", size=(15, 1), text_color="black"),
                    sg.InputText(
                        default_text=str(d.rot_y),
                        key=PHANTOM_ROT_Y,
                        size=(15, 1),
                        text_color="black",
                    ),
                ],
                [
                    sg.Text("Rot Z (deg)", size=(15, 1), text_color="black"),
                    sg.InputText(
                        default_text=str(d.rot_z),
                        key=PHANTOM_ROT_Z,
                        size=(15, 1),
                        text_color="black",
                    ),
                ],
            ],
        )

    def _build_phantom_couch_layer(self) -> sg.Frame:
        """Couch parameters for the phantom simulation."""
        d = self._defaults.phantom
        return sg.Frame(
            "Couch settings",
            [
                [
                    sg.Checkbox(
                        "Enable couch",
                        enable_events=True,
                        key=PHANTOM_COUCH_ENABLED,
                        default=d.couch_enabled,
                    )
                ],
                [
                    sg.Text("Couch width (mm)", size=(20, 1), text_color="black"),
                    sg.InputText(
                        default_text=str(d.couch_width),
                        key=PHANTOM_COUCH_WIDTH,
                        size=(15, 1),
                        text_color="black",
                    ),
                ],
                [
                    sg.Text("Couch thickness (mm)", size=(20, 1), text_color="black"),
                    sg.InputText(
                        default_text=str(d.couch_thickness),
                        key=PHANTOM_COUCH_THICKNESS,
                        size=(15, 1),
                        text_color="black",
                    ),
                ],
                [
                    sg.Text("Couch length (mm)", size=(20, 1), text_color="black"),
                    sg.InputText(
                        default_text=str(d.couch_length),
                        key=PHANTOM_COUCH_LENGTH,
                        size=(15, 1),
                        text_color="black",
                    ),
                ],
            ],
        )

    def _build_phantom_run_layer(self) -> sg.Frame:
        """Phantom graphics toggle and simulation run button."""
        return sg.Frame(
            "Activate ICRP 145 phantom simulation",
            [
                [
                    sg.Checkbox(
                        "Phantom Graphics Toggle",
                        enable_events=True,
                        key=PHANTOM_GRAPHICS,
                        default=False,
                    )
                ],
                [
                    sg.Button(
                        "Run ICRP 145 Phantom Simulation",
                        enable_events=True,
                        key=PHANTOM_RUN,
                        disabled=False,
                        disabled_button_color="grey",
                    )
                ],
            ],
        )

    def read(self) -> Tuple[str, Dict[str, Any]]:
        """Block until the next GUI event, returning ``(event, values)``."""
        return self.window.read()  # type: ignore[no-any-return]

    def update_imaging_mode_fields(self, mode: ImagingMode) -> None:
        """Populate all imaging-protocol fields from the given *mode*."""
        self.window[ROTATION_RATE].update(mode.rotation_rate)
        self.window[TUBE_VOLTAGE].update(mode.voltage)
        self.window[EXPOSURE].update(mode.exposure)
        self.window[FAN_MODE].update(mode.fan_mode)
        self.window[TIMELINE_END].update(mode.timeline_end)
        self.window[FIELD_X1].update(mode.field_x1)
        self.window[FIELD_X2].update(mode.field_x2)
        self.window[FIELD_Y1].update(mode.field_y1)
        self.window[FIELD_Y2].update(mode.field_y2)
        self.window[BLADE_X1].update(mode.blade_x1)
        self.window[BLADE_X2].update(mode.blade_x2)
        self.window[BLADE_Y1].update(mode.blade_y1)
        self.window[BLADE_Y2].update(mode.blade_y2)
        # ctdi_phantom maps to phantom_size on the CTDI tab
        self.window[CTDI_PHANTOM].update(mode.ctdi_phantom)

    def set_tab_visibility(self, sim_type: str) -> None:
        """Show the tab for *sim_type* and hide the others."""
        self.window[DICOM_TAB].update(visible=sim_type == "DICOM")
        self.window[CTDI_TAB].update(visible=sim_type == "CTDI")
        self.window[PHANTOM_TAB].update(visible=sim_type == "ICRP145")

    def reset_all(self, defaults: Dict[str, Any]) -> None:
        """Restore every element to *defaults* and hide simulation-specific tabs."""
        for key in defaults:
            self.window[key].update(defaults[key])
        self.window[DICOM_TAB].update(visible=False)
        self.window[CTDI_TAB].update(visible=False)
        self.window[PHANTOM_TAB].update(visible=False)

    def update_patient_id(self, patient_id: str) -> None:
        """Display the loaded *patient_id* in the read-only patient-ID field."""
        self.window[PATIENT_ID].update(patient_id)

    def update_isocenter(self, x: str, y: str, z: str) -> None:
        """Set the three read-only isocenter coordinate fields."""
        self.window[ISO_X].update(x)
        self.window[ISO_Y].update(y)
        self.window[ISO_Z].update(z)

    def set_couch_visible(self, visible: bool) -> None:
        """Toggle visibility of the couch-dimension frame."""
        self.window[COUCH].update(visible=visible)

    def set_blade_visible(self, visible: bool) -> None:
        """Toggle visibility of the user-specified jaw-position frame."""
        self.window[CTDI_BLADE].update(visible=visible)

    def show_error(self, message: str) -> None:
        """Display a modal error popup with *message*."""
        sg.popup_error(message)

    def show_popup(self, message: str, value: object = None) -> None:
        """Display a short-lived auto-closing popup with *message* and optional *value*."""
        sg.popup(message, value, auto_close=True, non_blocking=True)

    def close(self) -> None:
        """Destroy the underlying FreeSimpleGUI window."""
        self.window.close()
