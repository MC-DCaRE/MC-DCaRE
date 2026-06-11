"""CTDI-w dose metric calculator from TOPAS output CSVs."""

from __future__ import annotations

import logging
import math
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import yaml

logger = logging.getLogger(__name__)

PERIPHERAL_POSITIONS = ["Bottom", "Top", "Left", "Right"]
CENTER_POSITION = "Centre"
FILE_TYPES = ["dtm", "tle", "dtw"]
WATER_FILE_TYPES = ["water_dtm"]
ALL_FILE_TYPES = FILE_TYPES + WATER_FILE_TYPES
PRIMARY_SCORER = "tle"


class CTDICalculator:
    """Post-processes TOPAS chamber plug CSV outputs into CTDI-w metrics."""

    def __init__(self, runfolder: Path) -> None:
        self.runfolder = runfolder
        self.simulation_metadata: Optional[Dict] = None
        self.calibration_factor, self.simulation_metadata = (
            self._read_simulation_metadata()
        )

    def calculate(self) -> List[Dict]:
        """Compute CTDI-w results for each available scorer type.

        Returns one result dict per scorer type found in the runfolder.
        Each dict includes ``"scorer_type"``
        (``"tle"``|``"dtm"``|``"dtw"``|``"water_dtm"``)
        and ``"is_primary"`` (``True`` for TLE).
        """
        chamber_files = self._find_chamber_files()
        results: List[Dict] = []
        all_types = ALL_FILE_TYPES
        for file_type in all_types:
            if chamber_files[file_type]:
                # Water DTM files keep their file_type as scorer_type ("water_dtm")
                scorer_type = file_type
                result = self._process_file_type(chamber_files[file_type], scorer_type)
                if result:
                    results.append(result)
            else:
                logger.info("No files found for %s", file_type)
        return results

    def save_results(self, results: List[Dict], output_path: Path) -> None:
        """Save calculation results to a CSV file.

        Args:
            results: List of result dictionaries from calculate().
            output_path: Destination CSV path.

        Raises:
            Exception: Re-raises any I/O or pandas error.
        """
        try:
            df = pd.DataFrame(results)
            df.to_csv(output_path, index=False)
            logger.info("Results saved to: %s", output_path)
        except Exception as e:
            logger.error("Error saving results: %s", e)
            raise

    def _read_simulation_metadata(
        self,
    ) -> tuple[float, Optional[Dict]]:
        """Read simulation metadata from runfolder.

        Tries ``simulation_metadata.yaml`` first (structured provenance),
        falls back to ``head_calibration_factor.txt`` for backward compatibility.

        Returns:
            Tuple of (calibration_factor, metadata_dict_or_None).
        """
        metadata_path = self.runfolder / "simulation_metadata.yaml"
        if metadata_path.exists():
            try:
                with open(metadata_path, "r", encoding="utf-8") as f:
                    metadata = yaml.safe_load(f)
                if isinstance(metadata, dict):
                    combined = (
                        metadata["norm_factor"] * metadata["mAs"] * metadata["dcf_used"]
                    )
                    if not isinstance(combined, (int, float)) or not math.isfinite(
                        combined
                    ):
                        logger.warning(
                            "Non-finite calibration factor from metadata; falling back"
                        )
                    else:
                        logger.info(
                            "Loaded simulation metadata: norm_factor=%.6e, mAs=%s, dcf=%s",
                            metadata["norm_factor"],
                            metadata["mAs"],
                            metadata["dcf_used"],
                        )
                        return combined, metadata
                logger.warning(
                    "simulation_metadata.yaml is not a valid mapping; falling back"
                )
            except (KeyError, TypeError, yaml.YAMLError) as exc:
                logger.warning(
                    "Failed to parse simulation_metadata.yaml (%s); falling back", exc
                )

        # Fallback to legacy calibration factor file.
        factor = self._extract_calibration_factor()
        return factor, None

    def _extract_calibration_factor(self) -> float:
        """Read the head calibration factor from the run folder."""
        calib_file = self.runfolder / "head_calibration_factor.txt"
        if not calib_file.exists():
            raise FileNotFoundError("Calibration file not found: {}".format(calib_file))

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

        raise ValueError("No calibration factor found in {}".format(calib_file))

    def _find_chamber_files(self) -> Dict[str, Dict[str, Path]]:
        """Locate all ChamberPlug CSV files organised by file type and position."""
        chamber_files: Dict[str, Dict[str, Path]] = {}

        for file_type in ALL_FILE_TYPES:
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
        """Parse a TOPAS CSV output file and return the summed dose value."""
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
        """Compute peripheral average, center dose, and CTDI-w for one file type.

        The ``file_type`` parameter doubles as the scorer type label
        (``"tle"``, ``"dtm"``, ``"dtw"``, ``"water_dtm"``).  The result
        dict includes ``"scorer_type"`` and ``"is_primary"`` fields so
        downstream consumers can distinguish measurement-equivalent (TLE)
        results from secondary and water-chamber scorers.
        """
        scorer_type = file_type
        is_primary = scorer_type == PRIMARY_SCORER
        logger.info(
            "Processing %s files (scorer_type=%s, is_primary=%s)",
            file_type,
            scorer_type,
            is_primary,
        )

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
                "scorer_type": scorer_type,
                "is_primary": is_primary,
                "PeripheralDoseAverage": peripheral_avg,
                "CenterDose": center_dose,
                "CTDI_w": ctdi_w,
                "CalibrationFactor": self.calibration_factor,
                "Timestamp": datetime.now().isoformat(),
            }
        else:
            logger.error("Insufficient data to calculate CTDI_w for %s", file_type)
            return None

    def compare_scorers(self, results: List[Dict]) -> Dict:
        """Compare TLE results against analogue scorer results.

        Water-chamber scorers (``"water_dtm"``) are excluded from
        comparison because they share the same physics as DTM — only
        the fill material differs.

        Args:
            results: Output of :meth:`calculate` — list of result dicts,
                each containing ``"scorer_type"`` and ``"CTDI_w"`` keys.

        Returns:
            A dict with ``"tle_vs_dtm_ratio"``, ``"tle_vs_dtw_ratio"``
            (each a dict of per-position ratios plus ``"overall"``), and
            a ``"systematic_note"`` explaining the kerma-vs-dose
            discrepancy.

        Raises:
            ValueError: If *results* does not contain at least TLE and
                one analogue scorer, or if duplicate scorer types are
                detected.
        """
        by_type: Dict[str, Dict] = {}
        for r in results:
            st = r["scorer_type"]
            if st in by_type:
                raise ValueError(
                    "Duplicate scorer_type %r in results — "
                    "each scorer type must appear at most once" % st
                )
            by_type[st] = r

        if PRIMARY_SCORER not in by_type:
            raise ValueError("Results must contain TLE scorer data for comparison")

        analogue_types = [t for t in ("dtm", "dtw") if t in by_type]
        if not analogue_types:
            raise ValueError(
                "Results must contain at least one analogue scorer (DTM or DTW) for comparison"
            )

        comparison: Dict[str, object] = {}

        for analogue in analogue_types:
            tle_ctdi = by_type[PRIMARY_SCORER]["CTDI_w"]
            analogue_ctdi = by_type[analogue]["CTDI_w"]

            if not math.isfinite(tle_ctdi):
                raise ValueError("TLE CTDI_w is not finite (%s)" % tle_ctdi)
            if not math.isfinite(analogue_ctdi):
                raise ValueError(
                    "%s CTDI_w is not finite (%s)" % (analogue, analogue_ctdi)
                )

            ratio_key = "tle_vs_{}_ratio".format(analogue)

            if analogue_ctdi != 0.0:
                overall_ratio = tle_ctdi / analogue_ctdi
            else:
                overall_ratio = float("inf")

            ratio_data: Dict[str, object] = {"overall": overall_ratio}

            # Per-position ratios if position data is available
            tle_periph = by_type[PRIMARY_SCORER].get("PeripheralDoseAverage", 0.0)
            analogue_periph = by_type[analogue].get("PeripheralDoseAverage", 0.0)
            tle_center = by_type[PRIMARY_SCORER].get("CenterDose", 0.0)
            analogue_center = by_type[analogue].get("CenterDose", 0.0)

            if analogue_periph != 0.0:
                ratio_data["peripheral_avg"] = tle_periph / analogue_periph
            else:
                ratio_data["peripheral_avg"] = float("inf")
            if analogue_center != 0.0:
                ratio_data["center"] = tle_center / analogue_center
            else:
                ratio_data["center"] = float("inf")

            comparison[ratio_key] = ratio_data

        comparison["systematic_note"] = (
            "TLE estimates collision kerma (fluence-weighted), while DTM/DTW "
            "score analogue absorbed dose (event-based). A systematic ratio "
            "different from 1.0 reflects the fundamental kerma-vs-dose "
            "distinction, not a simulation error."
        )

        return comparison

    @staticmethod
    def calculate_ctdi_w(peripheral_doses: List[float], center_dose: float) -> float:
        """Compute the weighted CTDI-w from peripheral and center dose measurements.

        Args:
            peripheral_doses: Dose values at the four peripheral chamber positions.
            center_dose: Dose value at the central chamber position.

        Returns:
            CTDI-w value computed as (2/3) * peripheral_avg + (1/3) * center_dose.
        """
        if not peripheral_doses:
            logger.warning("No peripheral doses provided")
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
        """Verify that the run folder exists and contains expected chamber plug CSV files.

        Raises:
            ValueError: If the folder is missing or no chamber plug files are found.
        """
        if not self.runfolder.exists():
            raise ValueError("Runfolder does not exist: {}".format(self.runfolder))

        if not self.runfolder.is_dir():
            raise ValueError("Path is not a directory: {}".format(self.runfolder))

        chamber_files_found = False
        for file_type in ALL_FILE_TYPES:
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
