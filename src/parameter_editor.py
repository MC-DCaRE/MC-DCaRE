import logging
from typing import List, Optional

from src.config import SimulationConfig
from src.fieldtobladeopening import fieldtobladeopening

logger = logging.getLogger(__name__)


class ParameterEditor:
    def __init__(self, config: SimulationConfig) -> None:
        self.config: SimulationConfig = config

    @staticmethod
    def string_index_replacement(
        search_string: str,
        target_list: List[str],
        replacement_string: Optional[str] = None,
    ) -> None:
        for line_index in range(len(target_list)):
            if target_list[line_index].startswith(search_string):
                if replacement_string is None:
                    target_list[line_index] = ""
                else:
                    target_list[line_index] = (
                        search_string + " = " + replacement_string + "\n"
                    )
                break

    def edit_main_file(self, target_file: str) -> None:
        cfg: SimulationConfig = self.config
        with open(target_file, "r") as f:
            filecontent: List[str] = f.readlines()

        s = self.string_index_replacement

        s(
            "s:Ts/G4DataDirectory",
            filecontent,
            '"' + cfg.general.g4_data_directory + '"',
        )
        s(
            "i:Tf/NumberOfSequentialTimes",
            filecontent,
            cfg.imaging.sequential_times,
        )
        s("d:Tf/TimelineEnd", filecontent, cfg.imaging.timeline_end)
        s("d:Tf/Rotate/Rate", filecontent, cfg.imaging.rotation_rate)
        s(
            "d:Tf/Rotate/StartValue",
            filecontent,
            cfg.imaging.start_angle,
        )
        s("i:Ts/Seed", filecontent, cfg.general.seed)
        s("i:Ts/NumberOfThreads", filecontent, cfg.general.threads)
        s(
            "i:So/beam/NumberOfHistoriesInRun",
            filecontent,
            cfg.general.histories,
        )

        s("dc:Ge/Coll1/TransY", filecontent, cfg.imaging.blade_x1)
        s("dc:Ge/Coll2/TransY", filecontent, cfg.imaging.blade_x2)
        s("dc:Ge/Coll3/TransX", filecontent, cfg.imaging.blade_y1)
        s("dc:Ge/Coll4/TransX", filecontent, cfg.imaging.blade_y2)

        if cfg.imaging.fan_mode == "Full Fan":
            s("includeFile = halffan.txt", filecontent)
        elif cfg.imaging.fan_mode == "Half Fan":
            s("includeFile = fullfan.txt", filecontent)

        if cfg.imaging.simulation_type == "DICOM":
            s("includeFile = CTDIphantom_16.txt", filecontent)
            s("includeFile = CTDIphantom_32.txt", filecontent)
            s(
                "sv:Ph/Default/LayeredMassGeometryWorlds",
                filecontent,
            )
            if not cfg.dicom.graphics_enabled:
                s("Ts/UseQt", filecontent)
                s("s:Gr/ViewA/Type", filecontent)
                s("b:Gr/Enable", filecontent)

        elif cfg.imaging.simulation_type == "CTDI validation":
            s("includeFile = patientDICOM.txt", filecontent)
            if not cfg.ctdi.graphics_enabled:
                s("Ts/UseQt", filecontent)
                s("s:Gr/ViewA/Type", filecontent)
                s("b:Gr/Enable", filecontent)

            if cfg.ctdi.user_blade_enabled:
                calculated_blade_positions: List[str] = fieldtobladeopening(
                    [
                        cfg.ctdi.user_field_x1,
                        cfg.ctdi.user_field_x2,
                        cfg.ctdi.user_field_y1,
                        cfg.ctdi.user_field_y2,
                    ]
                )
                s(
                    "dc:Ge/Coll1/TransY",
                    filecontent,
                    calculated_blade_positions[0],
                )
                s(
                    "dc:Ge/Coll2/TransY",
                    filecontent,
                    calculated_blade_positions[1],
                )
                s(
                    "dc:Ge/Coll3/TransX",
                    filecontent,
                    calculated_blade_positions[2],
                )
                s(
                    "dc:Ge/Coll4/TransX",
                    filecontent,
                    calculated_blade_positions[3],
                )

            if cfg.ctdi.phantom_size == "16 cm":
                s("includeFile = CTDIphantom_32.txt", filecontent)
            elif cfg.ctdi.phantom_size == "32 cm":
                s("includeFile = CTDIphantom_16.txt", filecontent)

        with open(target_file, "w") as f:
            f.writelines(filecontent)

        logger.info("Edited main file: %s", target_file)

    def edit_sub_file(self, target_file: str) -> None:
        cfg: SimulationConfig = self.config
        with open(target_file, "r") as f:
            filecontent: List[str] = f.readlines()

        s = self.string_index_replacement

        if cfg.imaging.simulation_type == "DICOM":
            s("d:Ge/patrotation/yaw", filecontent, cfg.dicom.patient_yaw)
            s(
                "s:Ge/Patient/DicomDirectory",
                filecontent,
                '"' + cfg.dicom.dicom_directory + '"',
            )
            s("dc:Ge/IsocenterX", filecontent, cfg.dicom.isocenter_x)
            s("dc:Ge/IsocenterY", filecontent, cfg.dicom.isocenter_y)
            s("dc:Ge/IsocenterZ", filecontent, cfg.dicom.isocenter_z)
            s(
                "dc:Ge/Patient/UserTransX",
                filecontent,
                cfg.dicom.patient_shift_x,
            )
            s(
                "dc:Ge/Patient/UserTransY",
                filecontent,
                cfg.dicom.patient_shift_y,
            )
            s(
                "dc:Ge/Patient/UserTransZ",
                filecontent,
                cfg.dicom.patient_shift_z,
            )
            s(
                "s:Sc/DoseOnRTGrid100kz17/OutputFile",
                filecontent,
                '"'
                + cfg.dicom.patient_id
                + "_"
                + cfg.imaging.rotation_direction
                + "_"
                + cfg.imaging.imaging_mode
                + "_"
                + cfg.imaging.start_angle
                + "_DOSE_PTV"
                + '"',
            )

        elif cfg.imaging.simulation_type == "CTDI validation":
            if not cfg.ctdi.couch_enabled:
                s('s:Ge/couch/Parent="couchgroup"', filecontent)
            s("d:Ge/couch/HLX", filecontent, cfg.ctdi.couch_width)
            s("d:Ge/couch/HLY", filecontent, cfg.ctdi.couch_thickness)
            s("d:Ge/couch/HLZ", filecontent, cfg.ctdi.couch_length)
            s(
                "i:Sc/ChamberPlugDose_dtm/ZBins",
                filecontent,
                cfg.ctdi.dose_to_medium_zbins,
            )
            s(
                "i:Sc/ChamberPlugDose_tle/ZBins",
                filecontent,
                cfg.ctdi.tle_zbins,
            )
            s(
                "i:Sc/ChamberPlugDose_dtw/ZBins",
                filecontent,
                cfg.ctdi.dose_to_water_zbins,
            )

        with open(target_file, "w") as f:
            f.writelines(filecontent)

        logger.info("Edited sub file: %s", target_file)
