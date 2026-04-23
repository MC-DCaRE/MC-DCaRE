import os
from dataclasses import dataclass, field, asdict
from typing import Dict, Tuple
import yaml


@dataclass
class GeneralConfig:
    g4_data_directory: str = ""
    topas_directory: str = ""
    seed: str = "9"
    threads: str = "1"
    histories: str = "100000"


@dataclass
class ImagingConfig:
    simulation_type: str = "DICOM"
    start_angle: str = "0 deg"
    rotation_direction: str = "CBCT Clockwise"
    anode_voltage: str = "100 kV"
    exposure: str = "100 mAs"
    fan_mode: str = "Full Fan"
    imaging_mode: str = "Image Gently"
    rotation_rate: str = "0.4 deg/s"
    timeline_end: str = "501.0 s"
    sequential_times: str = "1000"
    time_verbosity: str = "0"
    field_x1: str = "14 cm"
    field_x2: str = "14 cm"
    field_y1: str = "10.7 cm"
    field_y2: str = "10.7 cm"
    blade_x1: str = "6.175536078965273 cm"
    blade_x2: str = "-6.175536078965273 cm"
    blade_y1: str = "5.814471115800571 cm"
    blade_y2: str = "-5.814471115800571 cm"


@dataclass
class DicomConfig:
    dicom_directory: str = "/sampledicom/setA"
    dicom_rp_file: str = "/sampledicom/RP.sample.dcm"
    patient_id: str = ""
    isocenter_x: str = "0 mm"
    isocenter_y: str = "0 mm"
    isocenter_z: str = "0 mm"
    patient_shift_x: str = "0. mm"
    patient_shift_y: str = "0. mm"
    patient_shift_z: str = "0. mm"
    patient_yaw: str = "0. deg"
    graphics_enabled: bool = False


@dataclass
class CtdiConfig:
    phantom_size: str = "16 cm"
    dose_to_medium_zbins: str = "100"
    tle_zbins: str = "100"
    dose_to_water_zbins: str = "100"
    couch_enabled: bool = True
    couch_width: str = "260. mm"
    couch_thickness: str = "0.4 mm"
    couch_length: str = "1000 mm"
    user_blade_enabled: bool = False
    user_field_x1: str = "14 cm"
    user_field_x2: str = "14 cm"
    user_field_y1: str = "10.7 cm"
    user_field_y2: str = "10.7 cm"
    graphics_enabled: bool = False


@dataclass
class SimulationConfig:
    general: GeneralConfig = field(default_factory=GeneralConfig)
    imaging: ImagingConfig = field(default_factory=ImagingConfig)
    dicom: DicomConfig = field(default_factory=DicomConfig)
    ctdi: CtdiConfig = field(default_factory=CtdiConfig)

    def to_dict(self) -> Dict[str, str]:
        return {
            "-G4_DATA_DIR-": self.general.g4_data_directory,
            "-TOPAS_DIR-": self.general.topas_directory,
            "-SEED-": self.general.seed,
            "-THREADS-": self.general.threads,
            "-HISTORIES-": self.general.histories,
            "-SIM_TYPE-": self.imaging.simulation_type,
            "-START_ANGLE-": self.imaging.start_angle,
            "-SCAN_TYPE-": self.imaging.rotation_direction,
            "-TUBE_VOLTAGE-": self.imaging.anode_voltage,
            "-EXPOSURE-": self.imaging.exposure,
            "-FAN_MODE-": self.imaging.fan_mode,
            "-IMAGING_MODE-": self.imaging.imaging_mode,
            "-ROTATION_RATE-": self.imaging.rotation_rate,
            "-TIMELINE_END-": self.imaging.timeline_end,
            "-SEQ_TIMES-": self.imaging.sequential_times,
            "-TIME_VERBOSITY-": self.imaging.time_verbosity,
            "-FIELD_X1-": self.imaging.field_x1,
            "-FIELD_X2-": self.imaging.field_x2,
            "-FIELD_Y1-": self.imaging.field_y1,
            "-FIELD_Y2-": self.imaging.field_y2,
            "-BLADE_X1-": self.imaging.blade_x1,
            "-BLADE_X2-": self.imaging.blade_x2,
            "-BLADE_Y1-": self.imaging.blade_y1,
            "-BLADE_Y2-": self.imaging.blade_y2,
            "-DICOM_DIR-": self.dicom.dicom_directory,
            "-DICOM_RP-": self.dicom.dicom_rp_file,
            "-PATIENT_ID-": self.dicom.patient_id,
            "-ISO_X-": self.dicom.isocenter_x,
            "-ISO_Y-": self.dicom.isocenter_y,
            "-ISO_Z-": self.dicom.isocenter_z,
            "-SHIFT_X-": self.dicom.patient_shift_x,
            "-SHIFT_Y-": self.dicom.patient_shift_y,
            "-SHIFT_Z-": self.dicom.patient_shift_z,
            "-PATIENT_YAW-": self.dicom.patient_yaw,
            "-DICOM_GRAPHICS-": str(self.dicom.graphics_enabled),
            "-CTDI_PHANTOM-": self.ctdi.phantom_size,
            "-DTM_ZBINS-": self.ctdi.dose_to_medium_zbins,
            "-TLE_ZBINS-": self.ctdi.tle_zbins,
            "-DTW_ZBINS-": self.ctdi.dose_to_water_zbins,
            "-COUCH_ENABLED-": str(self.ctdi.couch_enabled),
            "-COUCH_WIDTH-": self.ctdi.couch_width,
            "-COUCH_THICKNESS-": self.ctdi.couch_thickness,
            "-COUCH_LENGTH-": self.ctdi.couch_length,
            "-CTDI_USER_BLADE-": str(self.ctdi.user_blade_enabled),
            "-CTDI_FIELD_X1-": self.ctdi.user_field_x1,
            "-CTDI_FIELD_X2-": self.ctdi.user_field_x2,
            "-CTDI_FIELD_Y1-": self.ctdi.user_field_y1,
            "-CTDI_FIELD_Y2-": self.ctdi.user_field_y2,
            "-CTDI_GRAPHICS-": str(self.ctdi.graphics_enabled),
        }

    def to_yaml(self, path: str) -> None:
        data = {
            "general": asdict(self.general),
            "imaging": asdict(self.imaging),
            "dicom": asdict(self.dicom),
            "ctdi": asdict(self.ctdi),
        }
        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    @classmethod
    def from_yaml(cls, path: str) -> "SimulationConfig":
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        return cls(
            general=GeneralConfig(**data.get("general", {})),
            imaging=ImagingConfig(**data.get("imaging", {})),
            dicom=DicomConfig(**data.get("dicom", {})),
            ctdi=CtdiConfig(**data.get("ctdi", {})),
        )

    @classmethod
    def from_gui_values(cls, values: Dict[str, str]) -> "SimulationConfig":
        return cls(
            general=GeneralConfig(
                g4_data_directory=values.get("-G4_DATA_DIR-", ""),
                topas_directory=values.get("-TOPAS_DIR-", ""),
                seed=values.get("-SEED-", "9"),
                threads=values.get("-THREADS-", "1"),
                histories=values.get("-HISTORIES-", "100000"),
            ),
            imaging=ImagingConfig(
                simulation_type=values.get("-SIM_TYPE-", "DICOM"),
                start_angle=values.get("-START_ANGLE-", "0 deg"),
                rotation_direction=values.get("-SCAN_TYPE-", "CBCT Clockwise"),
                anode_voltage=values.get("-TUBE_VOLTAGE-", "100 kV"),
                exposure=values.get("-EXPOSURE-", "100 mAs"),
                fan_mode=values.get("-FAN_MODE-", "Full Fan"),
                imaging_mode=values.get("-IMAGING_MODE-", "Image Gently"),
                rotation_rate=values.get("-ROTATION_RATE-", "0.4 deg/s"),
                timeline_end=values.get("-TIMELINE_END-", "501.0 s"),
                sequential_times=values.get("-SEQ_TIMES-", "1000"),
                time_verbosity=values.get("-TIME_VERBOSITY-", "0"),
                field_x1=values.get("-FIELD_X1-", "14 cm"),
                field_x2=values.get("-FIELD_X2-", "14 cm"),
                field_y1=values.get("-FIELD_Y1-", "10.7 cm"),
                field_y2=values.get("-FIELD_Y2-", "10.7 cm"),
                blade_x1=values.get("-BLADE_X1-", "6.175536078965273 cm"),
                blade_x2=values.get("-BLADE_X2-", "-6.175536078965273 cm"),
                blade_y1=values.get("-BLADE_Y1-", "5.814471115800571 cm"),
                blade_y2=values.get("-BLADE_Y2-", "-5.814471115800571 cm"),
            ),
            dicom=DicomConfig(
                dicom_directory=values.get("-DICOM_DIR-", "/sampledicom/setA"),
                dicom_rp_file=values.get("-DICOM_RP-", "/sampledicom/RP.sample.dcm"),
                patient_id=values.get("-PATIENT_ID-", ""),
                isocenter_x=values.get("-ISO_X-", "0 mm"),
                isocenter_y=values.get("-ISO_Y-", "0 mm"),
                isocenter_z=values.get("-ISO_Z-", "0 mm"),
                patient_shift_x=values.get("-SHIFT_X-", "0. mm"),
                patient_shift_y=values.get("-SHIFT_Y-", "0. mm"),
                patient_shift_z=values.get("-SHIFT_Z-", "0. mm"),
                patient_yaw=values.get("-PATIENT_YAW-", "0. deg"),
                graphics_enabled=values.get("-DICOM_GRAPHICS-", False) is True
                or values.get("-DICOM_GRAPHICS-", "False") == "True",
            ),
            ctdi=CtdiConfig(
                phantom_size=values.get("-CTDI_PHANTOM-", "16 cm"),
                dose_to_medium_zbins=values.get("-DTM_ZBINS-", "100"),
                tle_zbins=values.get("-TLE_ZBINS-", "100"),
                dose_to_water_zbins=values.get("-DTW_ZBINS-", "100"),
                couch_enabled=values.get("-COUCH_ENABLED-", True) is True
                or values.get("-COUCH_ENABLED-", "True") == "True",
                couch_width=values.get("-COUCH_WIDTH-", "260. mm"),
                couch_thickness=values.get("-COUCH_THICKNESS-", "0.4 mm"),
                couch_length=values.get("-COUCH_LENGTH-", "1000 mm"),
                user_blade_enabled=values.get("-CTDI_USER_BLADE-", False) is True
                or values.get("-CTDI_USER_BLADE-", "False") == "True",
                user_field_x1=values.get("-CTDI_FIELD_X1-", "14 cm"),
                user_field_x2=values.get("-CTDI_FIELD_X2-", "14 cm"),
                user_field_y1=values.get("-CTDI_FIELD_Y1-", "10.7 cm"),
                user_field_y2=values.get("-CTDI_FIELD_Y2-", "10.7 cm"),
                graphics_enabled=values.get("-CTDI_GRAPHICS-", False) is True
                or values.get("-CTDI_GRAPHICS-", "False") == "True",
            ),
        )

    @classmethod
    def defaults(cls) -> "SimulationConfig":
        g4_dir = os.environ.get("G4DATA_DIR", "/root/G4Data")
        topas_dir = os.environ.get("TOPAS_DIR", "/root/topas/bin/topas ")
        return cls(
            general=GeneralConfig(
                g4_data_directory=g4_dir,
                topas_directory=topas_dir,
            ),
            imaging=ImagingConfig(),
            dicom=DicomConfig(),
            ctdi=CtdiConfig(),
        )


def quantity_unit_stripper(string_value: str) -> Tuple[float, str]:
    quantity = 0.0
    unit = ""
    for t in string_value.split():
        try:
            quantity = float(t)
        except ValueError:
            unit = t
    return quantity, unit
