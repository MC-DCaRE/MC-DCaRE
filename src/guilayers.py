import FreeSimpleGUI as sg
from src.config import SimulationConfig

sg.theme("Reddit")

_defaults = SimulationConfig.defaults()

general_layer = sg.Frame(
    "General Settings",
    [
        [
            sg.Text("Geant4 Data Directory", size=(17, 1), text_color="black"),
            sg.In(
                default_text=_defaults.general.g4_data_directory,
                key="-G4_DATA_DIR-",
                size=(50, 1),
                enable_events=True,
            ),
            sg.FolderBrowse(button_text="Browse", key="Browse"),
        ],
        [
            sg.Text("TOPAS Directory", size=(17, 1), text_color="black"),
            sg.In(
                default_text=_defaults.general.topas_directory,
                key="-TOPAS_DIR-",
                size=(50, 1),
                enable_events=True,
            ),
            sg.FileBrowse(button_text="Browse", key="Browse0"),
        ],
        [sg.Button(button_text="Reset all parameters to default", key="-RESET-")],
    ],
)

main_menu_information_layer = sg.Frame(
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
        [sg.Text("   CTDI validation is for running simulations on CTDI phantom")],
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

function_layer = sg.Frame(
    "Choose your function",
    [
        [
            sg.Text("Simulation Type", size=(20, 1), text_color="black"),
            sg.Combo(
                ["DICOM", "CTDI validation"],
                default_value=None,
                key="-SIM_TYPE-",
                readonly=True,
                enable_events=True,
                size=20,
            ),
        ],
    ],
)

settings_information_layout = sg.Frame(
    "General settings",
    [
        [sg.Text("This page contains general settings used for all simulations.")],
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

Hidden_layer = sg.Frame(
    "Time Feature and other hidden values",
    [
        [
            sg.Text("Time Feature Verbosity", size=(14, 1), text_color="black"),
            sg.In(
                default_text=_defaults.imaging.time_verbosity,
                key="-TIME_VERBOSITY-",
                size=(10, 1),
                enable_events=True,
            ),
        ],
        [
            sg.Text("Timeline End", size=(14, 1), text_color="black"),
            sg.In(
                default_text=_defaults.imaging.timeline_end,
                key="-TIMELINE_END-",
                size=(10, 1),
                enable_events=True,
            ),
        ],
        [
            sg.Text("Gantry Rotation Rate", size=(14, 1), text_color="black"),
            sg.In(
                default_text=_defaults.imaging.rotation_rate,
                key="-ROTATION_RATE-",
                size=(15, 1),
                enable_events=True,
                readonly=True,
            ),
        ],
        [
            sg.In(
                default_text=_defaults.imaging.blade_x1,
                key="-BLADE_X1-",
                size=(10, 1),
                text_color="black",
                enable_events=True,
                readonly=True,
            )
        ],
        [
            sg.In(
                default_text=_defaults.imaging.blade_x2,
                key="-BLADE_X2-",
                size=(10, 1),
                text_color="black",
                enable_events=True,
                readonly=True,
            )
        ],
        [
            sg.In(
                default_text=_defaults.imaging.blade_y1,
                key="-BLADE_Y1-",
                size=(10, 1),
                text_color="black",
                enable_events=True,
                readonly=True,
            )
        ],
        [
            sg.In(
                default_text=_defaults.imaging.blade_y2,
                key="-BLADE_Y2-",
                size=(10, 1),
                text_color="black",
                enable_events=True,
                readonly=True,
            )
        ],
    ],
    visible=False,
)

History_layer = sg.Frame(
    "Simulation settings",
    [
        [
            sg.Text("Random Seed", size=(10, 1), text_color="black"),
            sg.In(
                default_text=_defaults.general.seed,
                key="-SEED-",
                size=(10, 1),
                enable_events=True,
            ),
        ],
        [
            sg.Text("CPU Threads", size=(10, 1), text_color="black"),
            sg.In(
                default_text=_defaults.general.threads,
                key="-THREADS-",
                size=(10, 1),
                enable_events=True,
            ),
        ],
        [
            sg.Text("Sequential Time Steps", size=(10, 1), text_color="black"),
            sg.In(
                default_text=_defaults.imaging.sequential_times,
                key="-SEQ_TIMES-",
                size=(10, 1),
                enable_events=True,
            ),
        ],
        [
            sg.Text("Number of Histories", size=(10, 1), text_color="black"),
            sg.In(
                default_text=_defaults.general.histories,
                key="-HISTORIES-",
                size=(10, 1),
                enable_events=True,
            ),
        ],
    ],
    vertical_alignment="top",
)

imaging_protocol_layer = sg.Frame(
    "Imaging protocol",
    [
        [
            sg.Text("Imaging Protocol", size=(10, 1), text_color="black"),
            sg.Combo(
                [
                    "Image Gently",
                    "Head",
                    "Short Thorax",
                    "Spotlight",
                    "Thorax",
                    "Pelvis",
                    "Pelvis Large",
                ],
                default_value="Image Gently",
                key="-IMAGING_MODE-",
                readonly=True,
                enable_events=True,
            ),
        ],
        [
            sg.Text("Bowtie Filter Mode", size=(10, 1), text_color="black"),
            sg.In(
                default_text=_defaults.imaging.fan_mode,
                key="-FAN_MODE-",
                size=(15, 1),
                text_color="black",
                enable_events=True,
                readonly=True,
            ),
        ],
        [
            sg.Text("Field Size X1", size=(10, 1), text_color="black"),
            sg.In(
                default_text=_defaults.imaging.field_x1,
                key="-FIELD_X1-",
                size=(15, 1),
                text_color="black",
                enable_events=True,
                readonly=True,
            ),
        ],
        [
            sg.Text("Field Size X2", size=(10, 1), text_color="black"),
            sg.In(
                default_text=_defaults.imaging.field_x2,
                key="-FIELD_X2-",
                size=(15, 1),
                text_color="black",
                enable_events=True,
                readonly=True,
            ),
        ],
        [
            sg.Text("Field Size Y1", size=(10, 1), text_color="black"),
            sg.In(
                default_text=_defaults.imaging.field_y1,
                key="-FIELD_Y1-",
                size=(15, 1),
                text_color="black",
                enable_events=True,
                readonly=True,
            ),
        ],
        [
            sg.Text("Field Size Y2", size=(10, 1), text_color="black"),
            sg.In(
                default_text=_defaults.imaging.field_y2,
                key="-FIELD_Y2-",
                size=(15, 1),
                text_color="black",
                enable_events=True,
                readonly=True,
            ),
        ],
    ],
)

imaging_scan_layer = sg.Frame(
    "Set up imaging parameters",
    [
        [
            sg.Text("Start Angle", size=(12, 1), text_color="black"),
            sg.In(
                default_text=_defaults.imaging.start_angle,
                key="-START_ANGLE-",
                size=(15, 1),
                enable_events=True,
            ),
        ],
        [
            sg.Text("Scan Type", size=(12, 1), text_color="black"),
            sg.Combo(
                ["CBCT Clockwise", "CBCT Anticlockwise", "kV-kV"],
                default_value="CBCT Clockwise",
                key="-SCAN_TYPE-",
                readonly=True,
                enable_events=True,
                size=(15, 1),
            ),
        ],
        [
            sg.Text("Tube Voltage (kVp)", size=(12, 1), text_color="black"),
            sg.In(
                default_text=_defaults.imaging.anode_voltage,
                key="-TUBE_VOLTAGE-",
                size=(15, 1),
                enable_events=True,
            ),
        ],
        [
            sg.Text("Tube Current (mAs)", size=(12, 1), text_color="black"),
            sg.In(
                default_text=_defaults.imaging.exposure,
                key="-EXPOSURE-",
                size=(15, 1),
                enable_events=True,
            ),
        ],
    ],
    vertical_alignment="top",
)

dicom_information_layer = sg.Frame(
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

dicom_file_layer = sg.Frame(
    "DICOM inputs",
    [
        [
            sg.Text("DICOM Image Directory", size=(17, 1), text_color="black"),
            sg.In(
                default_text=_defaults.dicom.dicom_directory,
                key="-DICOM_DIR-",
                size=(50, 1),
                enable_events=True,
            ),
            sg.FolderBrowse(button_text="Browse", key="Browse1"),
        ],
        [
            sg.Text("Loaded Patient ID", size=(17, 1), text_color="black"),
            sg.In(
                default_text="",
                key="-PATIENT_ID-",
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
                default_text=_defaults.dicom.dicom_rp_file,
                key="-DICOM_RP-",
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
                key="-DICOM_RUN-",
                size=(35, 1),
            )
        ],
    ],
)

dicom_patient_layer = sg.Frame(
    "Patient set up adjustments",
    [
        [
            sg.Text("X Shift from Isocenter", size=(14, 1), text_color="black"),
            sg.In(
                default_text=_defaults.dicom.patient_shift_x,
                key="-SHIFT_X-",
                size=(10, 1),
                enable_events=True,
            ),
        ],
        [
            sg.Text("Y Shift from Isocenter", size=(14, 1), text_color="black"),
            sg.In(
                default_text=_defaults.dicom.patient_shift_y,
                key="-SHIFT_Y-",
                size=(10, 1),
                enable_events=True,
            ),
        ],
        [
            sg.Text("Z Shift from Isocenter", size=(14, 1), text_color="black"),
            sg.In(
                default_text=_defaults.dicom.patient_shift_z,
                key="-SHIFT_Z-",
                size=(10, 1),
                enable_events=True,
            ),
        ],
        [
            sg.Text("Patient Yaw Rotation", size=(14, 1), text_color="black"),
            sg.In(
                default_text=_defaults.dicom.patient_yaw,
                key="-PATIENT_YAW-",
                size=(10, 1),
                enable_events=True,
            ),
        ],
    ],
)


dicom_planned_layer = sg.Frame(
    "Treatment plan parameters",
    [
        [
            sg.Text("Isocenter X", size=(10, 1), text_color="black"),
            sg.In(
                default_text=_defaults.dicom.isocenter_x,
                key="-ISO_X-",
                size=(10, 1),
                enable_events=True,
                readonly=True,
            ),
        ],
        [
            sg.Text("Isocenter Y", size=(10, 1), text_color="black"),
            sg.In(
                default_text=_defaults.dicom.isocenter_y,
                key="-ISO_Y-",
                size=(10, 1),
                enable_events=True,
                readonly=True,
            ),
        ],
        [
            sg.Text("Isocenter Z", size=(10, 1), text_color="black"),
            sg.In(
                default_text=_defaults.dicom.isocenter_z,
                key="-ISO_Z-",
                size=(10, 1),
                enable_events=True,
                readonly=True,
            ),
        ],
    ],
    vertical_alignment="top",
)

dicom_graphics_layer = sg.Frame(
    "DICOM simulation graphics",
    [
        [
            sg.Checkbox(
                "DICOM Graphics Toggle",
                enable_events=True,
                key="-DICOM_GRAPHICS-",
                default=False,
            )
        ],
        [sg.Text("It is highly recommended to never use this ")],
        [sg.Text("due to excessive lag from the large image set. ")],
    ],
    vertical_alignment="top",
)


CTDI_information_layer = sg.Frame(
    "Instructions on the usage of the CTDI phantom parameters",
    [
        [
            sg.Text(
                "Select the CTDI phantom used for the CTDI validation. The phantom will be automatically centered at isocenter."
            )
        ],
        [
            sg.Text(
                "Simulation will automatically generate and run 5 CTDI simulations for all 5 possible detector position."
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

CTDI_layer = sg.Frame(
    "CTDI options",
    [
        [
            sg.Text("CTDI Phantom Diameter", size=(25, 1), text_color="black"),
            sg.Combo(
                ["16 cm", "32 cm"],
                default_value="16 cm",
                key="-CTDI_PHANTOM-",
                readonly=True,
            ),
        ],
        [
            sg.Text("Dose to Medium Z-Bins", size=(25, 1), text_color="black"),
            sg.In(
                default_text=_defaults.ctdi.dose_to_medium_zbins,
                key="-DTM_ZBINS-",
                size=(10, 1),
                enable_events=True,
            ),
        ],
        [
            sg.Text("Track Length Estimator Z-Bins", size=(25, 1), text_color="black"),
            sg.In(
                default_text=_defaults.ctdi.tle_zbins,
                key="-TLE_ZBINS-",
                size=(10, 1),
                enable_events=True,
            ),
        ],
        [
            sg.Text("Dose to Water Z-Bins", size=(25, 1), text_color="black"),
            sg.In(
                default_text=_defaults.ctdi.dose_to_water_zbins,
                key="-DTW_ZBINS-",
                size=(10, 1),
                enable_events=True,
            ),
        ],
        [
            sg.Checkbox(
                "Include Couch", enable_events=True, key="-COUCH_ENABLED-", default=True
            )
        ],
        [
            sg.Checkbox(
                "Custom CTDI Jaw Positions",
                enable_events=True,
                key="-CTDI_USER_BLADE-",
                default=False,
            )
        ],
    ],
    vertical_alignment="top",
)

Couch_layer = sg.pin(
    sg.Frame(
        "Couch",
        [
            [
                sg.Text("Couch Length", size=(8, 1), text_color="black"),
                sg.In(
                    default_text=_defaults.ctdi.couch_length,
                    key="-COUCH_LENGTH-",
                    size=(10, 1),
                    enable_events=True,
                ),
            ],
            [
                sg.Text("Couch Width", size=(8, 1), text_color="black"),
                sg.In(
                    default_text=_defaults.ctdi.couch_width,
                    key="-COUCH_WIDTH-",
                    size=(10, 1),
                    enable_events=True,
                ),
            ],
            [
                sg.Text("Couch Thickness", size=(8, 1), text_color="black"),
                sg.In(
                    default_text=_defaults.ctdi.couch_thickness,
                    key="-COUCH_THICKNESS-",
                    size=(10, 1),
                    enable_events=True,
                ),
            ],
        ],
        key="-COUCH-",
        visible=True,
        vertical_alignment="top",
    ),
    shrink=False,
    vertical_alignment="top",
)

CTDI_blade_layer = sg.pin(
    sg.Frame(
        "CTDI user specified jaw",
        [
            [
                sg.Text("Field Size X1", size=(10, 1), text_color="black"),
                sg.In(
                    default_text=_defaults.ctdi.user_field_x1,
                    key="-CTDI_FIELD_X1-",
                    size=(15, 1),
                    text_color="black",
                    enable_events=True,
                ),
            ],
            [
                sg.Text("Field Size X2", size=(10, 1), text_color="black"),
                sg.In(
                    default_text=_defaults.ctdi.user_field_x2,
                    key="-CTDI_FIELD_X2-",
                    size=(15, 1),
                    text_color="black",
                    enable_events=True,
                ),
            ],
            [
                sg.Text("Field Size Y1", size=(10, 1), text_color="black"),
                sg.In(
                    default_text=_defaults.ctdi.user_field_y1,
                    key="-CTDI_FIELD_Y1-",
                    size=(15, 1),
                    text_color="black",
                    enable_events=True,
                ),
            ],
            [
                sg.Text("Field Size Y2", size=(10, 1), text_color="black"),
                sg.In(
                    default_text=_defaults.ctdi.user_field_y2,
                    key="-CTDI_FIELD_Y2-",
                    size=(15, 1),
                    text_color="black",
                    enable_events=True,
                ),
            ],
        ],
        key="-CTDI_BLADE-",
        visible=False,
        vertical_alignment="top",
    ),
    shrink=False,
    vertical_alignment="top",
)

CTDI_run_layer = sg.Frame(
    "Activate CTDI simulation",
    [
        [
            sg.Checkbox(
                "CTDI Graphics Toggle",
                enable_events=True,
                key="-CTDI_GRAPHICS-",
                default=False,
            )
        ],
        [
            sg.Button(
                "Run CTDI Simulation",
                enable_events=True,
                key="-CTDI_RUN-",
                disabled=False,
                disabled_button_color="grey",
            )
        ],
    ],
)
