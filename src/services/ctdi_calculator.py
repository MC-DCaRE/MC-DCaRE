"""CTDI-w dose metric calculator from TOPAS output CSVs."""

from __future__ import annotations

import logging
import math
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


def extract_scorer_histories(csv_path: Path) -> Optional[int]:
    """Read ``Histories_with_Scorer_Active`` from a TOPAS CSV output file.

    TOPAS CSVs that include the column carry a header line such as::

        # TrackLengthEstimator ( Gy ) : Sum   Histories_with_Scorer_Active \
            Count_in_Bin   Standard_Deviation

    followed by comma-separated data rows whose trailing columns align with
    the post-``:`` header columns (the leading columns are bin indices:
    R/Phi/Z or X/Y/Z). This helper locates the column by name in the last
    ``#``-prefixed line before the first data row and returns the integer
    value from that first data row.

    Returns:
        The scorer-active history count, or ``None`` if the column is absent
        (e.g. older DoseToMedium scorers that only emit ``Sum``) or the file
        cannot be parsed.
    """
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            header_line: Optional[str] = None
            first_data_line: Optional[str] = None
            for raw in f:
                line = raw.rstrip("\n")
                if not line.strip():
                    continue
                if line.lstrip().startswith("#"):
                    header_line = line
                    continue
                first_data_line = line
                break
    except OSError as exc:
        logger.warning("Cannot read scorer histories from %s: %s", csv_path, exc)
        return None

    if header_line is None or first_data_line is None or ":" not in header_line:
        return None

    after_colon = header_line.split(":", 1)[1].strip()
    cols = after_colon.split()
    try:
        hist_idx = cols.index("Histories_with_Scorer_Active")
    except ValueError:
        return None

    parts = [p.strip() for p in first_data_line.split(",")]
    n_bins = len(parts) - len(cols)
    data_idx = n_bins + hist_idx
    if data_idx < 0 or data_idx >= len(parts):
        return None
    try:
        return int(float(parts[data_idx]))
    except ValueError:
        logger.warning(
            "Could not parse Histories_with_Scorer_Active from %s (col %d = %r)",
            csv_path,
            data_idx,
            parts[data_idx] if data_idx < len(parts) else "?",
        )
        return None


class CTDICalculator:
    """Post-processes TOPAS chamber plug CSV outputs into CTDI-w metrics."""

    def __init__(self, runfolder: Path) -> None:
        self.runfolder = runfolder
        self.total_histories: int = 0
        self.exposure_mAs: float = 0.0
        self.simulation_metadata: Optional[Dict] = None
        self.n_scorer_active_histories: Optional[int] = None
        self._read_metadata()

    def calculate(self) -> List[Dict]:
        """Compute raw CTDI-w results for each available scorer type.

        Returns one result dict per scorer type found in the runfolder.
        Each dict includes ``"scorer_type"``
        (``"tle"``|``"dtm"``|``"dtw"``|``"water_dtm"``),
        ``"is_primary"`` (``True`` for TLE),
        ``"raw_sum"`` (un-normalized CTDI-w from raw Sum values),
        per-position raw sums, and ``"metadata"`` with
        ``total_histories``, ``exposure_mAs``, and
        ``n_scorer_active_histories`` (the scorer-active history count read
        from the CSV ``Histories_with_Scorer_Active`` column; ``None`` when
        the scorer does not emit it). No calibration factor, norm_factor,
        or DCF is applied.
        """
        chamber_files = self._find_chamber_files()
        self._read_scorer_active_histories(chamber_files)
        results: List[Dict] = []
        for file_type in ALL_FILE_TYPES:
            if chamber_files[file_type]:
                scorer_type = file_type
                result = self._process_file_type(chamber_files[file_type], scorer_type)
                if result:
                    result["metadata"] = {
                        "total_histories": self.total_histories,
                        "exposure_mAs": self.exposure_mAs,
                        "n_scorer_active_histories": self.n_scorer_active_histories,
                    }
                    if self.simulation_metadata:
                        if (
                            "spectrum_fluence_photons_per_mAs"
                            in self.simulation_metadata
                        ):
                            result["metadata"]["spectrum_fluence_photons_per_mAs"] = (
                                self.simulation_metadata[
                                    "spectrum_fluence_photons_per_mAs"
                                ]
                            )
                        if "norm_factor" in self.simulation_metadata:
                            result["metadata"]["norm_factor"] = (
                                self.simulation_metadata["norm_factor"]
                            )
                    results.append(result)
            else:
                logger.info("No files found for %s", file_type)
        return results

    def _read_scorer_active_histories(
        self, chamber_files: Dict[str, Dict[str, Path]]
    ) -> None:
        """Extract ``Histories_with_Scorer_Active`` from the first available CSV.

        The value is a property of the run (the same for every position and
        scorer type), so a single CSV suffices. Sets
        ``self.n_scorer_active_histories`` (``None`` when the column is absent
        or no files are found).
        """
        for file_type in ALL_FILE_TYPES:
            for position in PERIPHERAL_POSITIONS + [CENTER_POSITION]:
                path = chamber_files.get(file_type, {}).get(position)
                if path is None:
                    continue
                count = extract_scorer_histories(path)
                if count is not None:
                    self.n_scorer_active_histories = count
                    logger.info(
                        "Scorer-active histories from %s (%s %s): %d",
                        path.name,
                        position,
                        file_type,
                        count,
                    )
                    return
                # Column absent on this file; try the next. Fall back to the
                # legacy total_histories if no CSV in the runfolder emits it.
        if self.n_scorer_active_histories is None:
            logger.warning(
                "No CSV in %s reports Histories_with_Scorer_Active; "
                "falling back to metadata total_histories=%d for normalization",
                self.runfolder,
                self.total_histories,
            )

    def save_results(self, results: List[Dict], output_path: Path) -> None:
        """Save calculation results to a CSV file.

        Args:
            results: List of result dictionaries from calculate().
            output_path: Destination CSV path.

        Raises:
            Exception: Re-raises any I/O or pandas error.
        """
        flat: List[Dict] = []
        for r in results:
            row = {
                "scorer_type": r.get("scorer_type"),
                "is_primary": r.get("is_primary"),
                "raw_sum": r.get("raw_sum"),
                "total_histories": r.get("metadata", {}).get("total_histories"),
                "exposure_mAs": r.get("metadata", {}).get("exposure_mAs"),
            }
            for pos_name, pos_sum in (r.get("peripheral_raw_sums") or {}).items():
                row["peripheral_" + pos_name.lower()] = pos_sum
            row["center_raw_sum"] = r.get("center_raw_sum")
            flat.append(row)
        try:
            df = pd.DataFrame(flat)
            df.to_csv(output_path, index=False)
            logger.info("Results saved to: %s", output_path)
        except Exception as e:
            logger.error("Error saving results: %s", e)
            raise

    def _read_metadata(self) -> None:
        """Read simulation metadata from runfolder.

        Tries ``simulation_metadata.yaml`` first (structured provenance),
        falls back to ``head_calibration_factor.txt`` for backward compatibility.
        Sets ``self.total_histories``, ``self.exposure_mAs``, and
        ``self.simulation_metadata``.
        """
        metadata_path = self.runfolder / "simulation_metadata.yaml"
        if metadata_path.exists():
            try:
                with open(metadata_path, "r", encoding="utf-8") as f:
                    metadata = yaml.safe_load(f)
                if isinstance(metadata, dict):
                    if "norm_factor" in metadata:
                        self._read_old_metadata(metadata)
                    else:
                        self._read_new_metadata(metadata)
                    return
                logger.warning(
                    "simulation_metadata.yaml is not a valid mapping; falling back"
                )
            except (KeyError, TypeError, yaml.YAMLError) as exc:
                logger.warning(
                    "Failed to parse simulation_metadata.yaml (%s); falling back", exc
                )

        # Fallback to legacy calibration factor file.
        self._extract_legacy_metadata()

    def _read_new_metadata(self, metadata: Dict) -> None:
        """Parse new-format simulation_metadata.yaml."""
        self.total_histories = int(metadata["total_histories"])
        self.exposure_mAs = float(metadata["exposure_mAs"])
        self.simulation_metadata = metadata
        logger.info(
            "Loaded new-format metadata: histories=%s, mAs=%s",
            self.total_histories,
            self.exposure_mAs,
        )

    def _read_old_metadata(self, metadata: Dict) -> None:
        """Parse old-format simulation_metadata.yaml (norm_factor/mAs/dcf_used)."""
        self.total_histories = int(metadata.get("total_histories", 0))
        if self.total_histories <= 0:
            logger.warning(
                "Old-format metadata missing valid total_histories; defaulting to 0"
            )
        self.exposure_mAs = float(metadata["mAs"])
        self.simulation_metadata = metadata
        logger.info(
            "Loaded old-format metadata: histories=%s, mAs=%s",
            self.total_histories,
            self.exposure_mAs,
        )

    def _extract_legacy_metadata(self) -> None:
        """Read total_histories from legacy head_calibration_factor.txt."""
        calib_file = self.runfolder / "head_calibration_factor.txt"
        if not calib_file.exists():
            raise FileNotFoundError(
                "No metadata found in runfolder: {}".format(self.runfolder)
            )

        logger.warning(
            "Using legacy head_calibration_factor.txt — "
            "consider regenerating simulation_metadata.yaml"
        )

        with open(calib_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        total_histories = 0
        for line in lines:
            line_stripped = line.strip()
            if line_stripped.startswith("The number of histories in this run was:"):
                try:
                    total_histories = int(line_stripped.split(":")[1].strip())
                    break
                except (ValueError, IndexError):
                    continue

        if total_histories <= 0:
            logger.warning(
                "Could not parse total_histories from %s; defaulting to 0",
                calib_file,
            )

        self.total_histories = total_histories
        self.exposure_mAs = 0.0
        self.simulation_metadata = None
        logger.info(
            "Legacy metadata: histories=%s (exposure_mAs unavailable from legacy format)",
            total_histories,
        )

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
                            # Binned format: R, Phi, Z, Sum, Histories, ...
                            dose = float(parts[3])
                            dose_values.append(dose)
                            logger.debug(
                                "Found Z-bin dose at bin %s: %s", parts[2], dose
                            )
                        elif len(parts) >= 4:
                            # Unbinned format (e.g. water_dtm): Sum, Histories,
                            # Count, StdDev -- the Sum is parts[0] and is the
                            # mean dose over the scored volume.
                            dose = float(parts[0])
                            dose_values.append(dose)
                            logger.debug("Found unbinned dose: %s", dose)
                        else:
                            dose = float(line)
                            dose_values.append(dose)
                            logger.debug("Found single dose: %s", dose)
                    except ValueError:
                        logger.warning("Could not parse dose value from line: %s", line)
                        continue

            if dose_values:
                mean_dose = sum(dose_values) / len(dose_values)
                logger.info(
                    "Extracted %d dose values from %s, mean: %.6e",
                    len(dose_values),
                    file_path,
                    mean_dose,
                )
                return mean_dose
            else:
                logger.warning("No dose values found in file: %s", file_path)
                return None

        except FileNotFoundError:
            logger.error("File not found: %s", file_path)
            return None
        except (OSError, UnicodeDecodeError) as e:
            logger.error("Error reading file %s: %s", file_path, e)
            return None

    def _process_file_type(
        self, chamber_files: Dict[str, Path], file_type: str
    ) -> Optional[Dict]:
        """Compute raw (unscaled) CTDI-w and per-position raw Sum values.

        The ``file_type`` parameter doubles as the scorer type label
        (``"tle"``, ``"dtm"``, ``"dtw"``, ``"water_dtm"``).  The result
        dict includes ``"scorer_type"`` and ``"is_primary"`` fields so
        downstream consumers can distinguish measurement-equivalent (TLE)
        results from secondary and water-chamber scorers.

        No calibration factor, norm_factor, or DCF is applied.
        """
        scorer_type = file_type
        is_primary = scorer_type == PRIMARY_SCORER
        logger.info(
            "Processing %s files (scorer_type=%s, is_primary=%s)",
            file_type,
            scorer_type,
            is_primary,
        )

        peripheral_raw: List[float] = []
        peripheral_sums: Dict[str, float] = {}
        for position in PERIPHERAL_POSITIONS:
            if position in chamber_files:
                dose = self._extract_dose_from_file(chamber_files[position])
                if dose is not None:
                    peripheral_raw.append(dose)
                    peripheral_sums[position] = dose
                    logger.info("%s raw sum: %.6e (unscaled)", position, dose)
                else:
                    logger.warning("Failed to extract dose from %s file", position)
            else:
                logger.warning("Missing %s position file", position)

        center_raw: Optional[float] = None
        if CENTER_POSITION in chamber_files:
            dose = self._extract_dose_from_file(chamber_files[CENTER_POSITION])
            if dose is not None:
                center_raw = dose
                logger.info("Center raw sum: %.6e (unscaled)", center_raw)
            else:
                logger.warning("Failed to extract dose from center file")
        else:
            logger.warning("Missing center position file")

        if peripheral_raw and center_raw is not None:
            raw_ctdi_w = self.calculate_ctdi_w(peripheral_raw, center_raw)

            return {
                "scorer_type": scorer_type,
                "is_primary": is_primary,
                "raw_sum": raw_ctdi_w,
                "peripheral_raw_sums": peripheral_sums,
                "center_raw_sum": center_raw,
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
                each containing ``"scorer_type"`` and ``"raw_sum"`` keys.

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
            tle_raw = by_type[PRIMARY_SCORER]["raw_sum"]
            analogue_raw = by_type[analogue]["raw_sum"]

            if not math.isfinite(tle_raw):
                raise ValueError("TLE raw_sum is not finite (%s)" % tle_raw)
            if not math.isfinite(analogue_raw):
                raise ValueError(
                    "%s raw_sum is not finite (%s)" % (analogue, analogue_raw)
                )

            ratio_key = "tle_vs_{}_ratio".format(analogue)

            if analogue_raw != 0.0:
                overall_ratio = tle_raw / analogue_raw
            else:
                overall_ratio = float("inf")

            ratio_data: Dict[str, object] = {"overall": overall_ratio}

            tle_periph = by_type[PRIMARY_SCORER].get("peripheral_raw_sums", {})
            analogue_periph = by_type[analogue].get("peripheral_raw_sums", {})
            tle_center = by_type[PRIMARY_SCORER].get("center_raw_sum", 0.0)
            analogue_center = by_type[analogue].get("center_raw_sum", 0.0)

            tle_periph_avg = (
                sum(tle_periph.values()) / len(tle_periph) if tle_periph else 0.0
            )
            analogue_periph_avg = (
                sum(analogue_periph.values()) / len(analogue_periph)
                if analogue_periph
                else 0.0
            )

            if analogue_periph_avg != 0.0:
                ratio_data["peripheral_avg"] = tle_periph_avg / analogue_periph_avg
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

        chamber_files_found = any(
            (
                self.runfolder / "ChamberPlug{}_{}.csv".format(position, file_type)
            ).exists()
            for file_type in ALL_FILE_TYPES
            for position in PERIPHERAL_POSITIONS + [CENTER_POSITION]
        )

        if not chamber_files_found:
            raise ValueError(
                "No ChamberPlug CSV files found in runfolder: {}. "
                "Expected files like: ChamberPlugTop_dtw.csv, ChamberPlugCenter_tle.csv".format(
                    self.runfolder
                )
            )
