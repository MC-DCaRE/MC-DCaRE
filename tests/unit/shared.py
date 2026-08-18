from __future__ import annotations

DEFAULT_MAIN_CONTEXT: dict = {
    "g4_data_directory": "/root/G4Data",
    "seed": "9",
    "threads": "1",
    "histories": "100000",
    "sequential_times": "1000",
    "timeline_end": "501 s",
    "rotation_rate": "0.4 deg/s",
    "start_angle": "0 deg",
    "coll1_trans_y": "1.2519 cm",
    "coll2_trans_y": "-1.2519 cm",
    "coll3_trans_x": "1.638 cm",
    "coll4_trans_x": "-1.638 cm",
    "fan_mode": "Full Fan",
    "graphics_enabled": False,
    "simulation_type": "CTDI",
    "phantom_size": "16",
    "patient_yaw": "0 deg",
    "patient_pitch": "0 deg",
    "patient_roll_value": 0.0,
    "rotation_direction": "CBCT Clockwise",
    "start_angle_value": 0.0,
    "second_angle_value": 0.0,
}

DEFAULT_CTDI_SUB_CONTEXT: dict = {
    "couch_enabled": True,
    "couch_width": "260 mm",
    "couch_thickness": "0.4 mm",
    "couch_length": "1000 mm",
    "plug_positions": [
        "ChamberPlugCentre",
        "ChamberPlugTop",
        "ChamberPlugBottom",
        "ChamberPlugLeft",
        "ChamberPlugRight",
    ],
    "dose_to_medium_zbins": "100",
    "tle_zbins": "100",
    "dose_to_water_zbins": "100",
    "water_chamber_enabled": False,
}

DEFAULT_DICOM_SUB_CONTEXT: dict = {
    "patient_yaw": "0 deg",
    "patient_pitch": "0 deg",
    "dicom_directory": "/sampledicom/setA",
    "isocenter_x": "0 mm",
    "isocenter_y": "0 mm",
    "isocenter_z": "0 mm",
    "patient_shift_x": "0 mm",
    "patient_shift_y": "0 mm",
    "patient_shift_z": "0 mm",
    "output_filename": "__CBCT Image Gently_0 deg_DOSE_PTV",
}
