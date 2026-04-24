from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)

PERIPHERAL_POSITIONS = ["Bottom", "Top", "Left", "Right"]
CENTER_POSITION = "Centre"
FILE_TYPES = ["dtm", "tle"]


class CTDICalculator:
    def __init__(self, runfolder: Path) -> None:
        self.runfolder = runfolder
        self.calibration_factor = self._extract_calibration_factor()

    def calculate(self) -> List[Dict]:
        chamber_files = self._find_chamber_files()
        results: List[Dict] = []
        for file_type in FILE_TYPES:
            if chamber_files[file_type]:
                result = self._process_file_type(chamber_files[file_type], file_type)
                if result:
                    results.append(result)
            else:
                logger.warning("No files found for %s", file_type)
        return results

    def save_results(self, results: List[Dict], output_path: Path) -> None:
        try:
            df = pd.DataFrame(results)
            df.to_csv(output_path, index=False)
            logger.info("Results saved to: %s", output_path)
        except Exception as e:
            logger.error("Error saving results: %s", e)
            raise

    def _extract_calibration_factor(self) -> float:
        try:
            calib_file = self.runfolder / "head_calibration_factor.txt"
            if not calib_file.exists():
                logger.warning("Calibration file not found: %s", calib_file)
                return 1.0

            with open(calib_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            for line in lines:
                line = line.strip()
                if line and not line.startswith("#") and not line.startswith(" "):
                    try:
                        factor = float(line)
                        logger.info("Calibration factor found: %s", factor)
                        return factor
                    except ValueError:
                        continue

            logger.warning("No calibration factor found in file")
            return 1.0

        except Exception as e:
            logger.error("Error reading calibration file: %s", e)
            return 1.0

    def _find_chamber_files(self) -> Dict[str, Dict[str, Path]]:
        chamber_files: Dict[str, Dict[str, Path]] = {}

        for file_type in FILE_TYPES:
            chamber_files[file_type] = {}

            for position in PERIPHERAL_POSITIONS + [CENTER_POSITION]:
                pattern = "ChamberPlug{}_{}.csv".format(position, file_type)
                file_path = self.runfolder / pattern

                if file_path.exists():
                    chamber_files[file_type][position] = file_path
                    logger.info("Found file: %s", file_path)
                else:
                    logger.warning("Missing file: %s", file_path)

        return chamber_files

    def _extract_dose_from_file(self, file_path: Path) -> Optional[float]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            dose_values: List[float] = []

            for line in lines:
                line = line.strip()
                if line and not line.startswith("#"):
                    try:
                        parts = [part.strip() for part in line.split(",")]

                        if (
                            len(parts) >= 4
                            and parts[0] == "0"
                            and parts[1] == "0"
                            and parts[2].isdigit()
                        ):
                            dose = float(parts[3])
                            dose_values.append(dose)
                            logger.debug(
                                "Found Z-bin dose at bin %s: %s", parts[2], dose
                            )
                        else:
                            dose = float(line)
                            dose_values.append(dose)
                            logger.debug("Found single dose: %s", dose)
                    except ValueError:
                        logger.warning("Could not parse dose value from line: %s", line)
                        continue

            if dose_values:
                total_dose = sum(dose_values)
                logger.info(
                    "Extracted %d dose values from %s, total: %.6e",
                    len(dose_values),
                    file_path,
                    total_dose,
                )
                return total_dose
            else:
                logger.warning("No dose values found in file: %s", file_path)
                return None

        except FileNotFoundError:
            logger.error("File not found: %s", file_path)
            return None
        except Exception as e:
            logger.error("Error reading file %s: %s", file_path, e)
            return None

    def _process_file_type(
        self, chamber_files: Dict[str, Path], file_type: str
    ) -> Optional[Dict]:
        logger.info("Processing %s files", file_type)

        peripheral_doses: List[float] = []
        for position in PERIPHERAL_POSITIONS:
            if position in chamber_files:
                dose = self._extract_dose_from_file(chamber_files[position])
                if dose is not None:
                    scaled_dose = dose * self.calibration_factor
                    peripheral_doses.append(scaled_dose)
                    logger.info(
                        "%s dose: %.6e Gy (scaled by factor %s)",
                        position,
                        scaled_dose,
                        self.calibration_factor,
                    )
                else:
                    logger.warning("Failed to extract dose from %s file", position)
            else:
                logger.warning("Missing %s position file", position)

        center_dose: Optional[float] = None
        if CENTER_POSITION in chamber_files:
            dose = self._extract_dose_from_file(chamber_files[CENTER_POSITION])
            if dose is not None:
                center_dose = dose * self.calibration_factor
                logger.info(
                    "Center dose: %.6e Gy (scaled by factor %s)",
                    center_dose,
                    self.calibration_factor,
                )
            else:
                logger.warning("Failed to extract dose from center file")
        else:
            logger.warning("Missing center position file")

        if peripheral_doses and center_dose is not None:
            ctdi_w = self.calculate_ctdi_w(peripheral_doses, center_dose)
            peripheral_avg = sum(peripheral_doses) / len(peripheral_doses)

            return {
                "FileType": file_type,
                "PeripheralDoseAverage": peripheral_avg,
                "CenterDose": center_dose,
                "CTDI_w": ctdi_w,
                "CalibrationFactor": self.calibration_factor,
                "Timestamp": datetime.now().isoformat(),
            }
        else:
            logger.error("Insufficient data to calculate CTDI_w for %s", file_type)
            return None

    @staticmethod
    def calculate_ctdi_w(peripheral_doses: List[float], center_dose: float) -> float:
        if not peripheral_doses:
            logger.warning("No peripheral doses provided")
            return 0.0

        if center_dose is None:
            logger.warning("No center dose provided")
            return 0.0

        peripheral_avg = sum(peripheral_doses) / len(peripheral_doses)
        ctdi_w = (2 / 3) * peripheral_avg + (1 / 3) * center_dose

        logger.info(
            "Peripheral average: %.6e, Center dose: %.6e",
            peripheral_avg,
            center_dose,
        )
        logger.info("CTDI_w: %.6e", ctdi_w)

        return ctdi_w

    def validate(self) -> None:
        if not self.runfolder.exists():
            raise ValueError("Runfolder does not exist: {}".format(self.runfolder))

        if not self.runfolder.is_dir():
            raise ValueError("Path is not a directory: {}".format(self.runfolder))

        chamber_files_found = False
        for file_type in FILE_TYPES:
            for position in PERIPHERAL_POSITIONS + [CENTER_POSITION]:
                pattern = "ChamberPlug{}_{}.csv".format(position, file_type)
                if (self.runfolder / pattern).exists():
                    chamber_files_found = True
                    break
            if chamber_files_found:
                break

        if not chamber_files_found:
            raise ValueError(
                "No ChamberPlug CSV files found in runfolder: {}. "
                "Expected files like: ChamberPlugTop_dtw.csv, ChamberPlugCenter_tle.csv".format(
                    self.runfolder
                )
            )
