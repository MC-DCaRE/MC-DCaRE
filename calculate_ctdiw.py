#!/usr/bin/env python3
"""
Calculate CTDI_w values from ChamberPlug CSV files.

This script processes ChamberPlug CSV files in a runfolder and calculates
CTDI_w using the formula: (2/3 * average peripheral doses) + (1/3 * center dose)

CTDI (Computed Tomography Dose Index) is based on Dose To Medium (DTM) measurements,
not Dose To Water (DTW). The script processes DTM and TLE (Total Lung Equivalent) files.
"""

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
import typer
from rich.console import Console

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
console = Console()

# Constants
PERIPHERAL_POSITIONS = ["Bottom", "Top", "Left", "Right"]
CENTER_POSITION = "Centre"
FILE_TYPES = ["dtm", "tle"]


def extract_dose_from_file(file_path: Path) -> Optional[float]:
    """
    Extract dose value from TOPAS CSV file.
    
    The file format contains header lines followed by a dose value.
    Example format:
    # TOPAS Version: 4.0
    # Parameter File: /path/to/file.txt
    # Results for scorer: ChamberPlugDose_dtm
    # Scored in component: ChamberPlugTop
    # DoseToMaterial ( Gy ) : Sum   
    5.109993539420543e-10
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        Dose value as float, or None if extraction fails
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Look for dose values - either single value or multiple Z bins
        dose_values = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                try:
                    # Try to parse as float (handles both single value and bin format)
                    parts = [part.strip() for part in line.split(',')]
                    
                    # Check for Z-bin format: "0, 0, bin_number, dose_value"
                    if (len(parts) >= 4 and
                        parts[0] == '0' and
                        parts[1] == '0' and
                        parts[2].isdigit()):
                        # This is Z bin format: x, y, z_bin, dose
                        dose = float(parts[3])
                        dose_values.append(dose)
                        logger.debug(f"Found Z-bin dose at bin {parts[2]}: {dose}")
                    else:
                        # Try to parse as single float value
                        dose = float(line)
                        dose_values.append(dose)
                        logger.debug(f"Found single dose: {dose}")
                except ValueError:
                    logger.warning(f"Could not parse dose value from line: {line}")
                    continue
        
        if dose_values:
            total_dose = sum(dose_values)
            logger.info(f"Extracted {len(dose_values)} dose values from {file_path}, total: {total_dose:.6e}")
            return total_dose
        else:
            logger.warning(f"No dose values found in file: {file_path}")
            return None
        
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return None
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
def extract_calibration_factor(runfolder: Path) -> Optional[float]:
    """
    Extract calibration factor from head_calibration_factor.txt file.
    
    Args:
        runfolder: Path to the runfolder
        
    Returns:
        Calibration factor as float, or None if extraction fails
    """
    try:
        calib_file = runfolder / "head_calibration_factor.txt"
        if not calib_file.exists():
            logger.warning(f"Calibration file not found: {calib_file}")
            return 1.0  # Default to no scaling
        
        with open(calib_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Look for the calibration factor (first line should contain the factor)
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith(' '):
                try:
                    factor = float(line)
                    logger.info(f"Calibration factor found: {factor}")
                    return factor
                except ValueError:
                    continue
        
        logger.warning("No calibration factor found in file")
        return 1.0
        
    except Exception as e:
        logger.error(f"Error reading calibration file: {e}")
        return 1.0


        return None


def find_chamber_files(runfolder: Path) -> Dict[str, Dict[str, Path]]:
    """
    Find all ChamberPlug CSV files in the runfolder.
    
    Args:
        runfolder: Path to the runfolder
        
    Returns:
        Dictionary with structure: {file_type: {position: file_path}}
    """
    chamber_files = {}
    
    for file_type in FILE_TYPES:
        chamber_files[file_type] = {}
        
        for position in PERIPHERAL_POSITIONS + [CENTER_POSITION]:
            pattern = f"ChamberPlug{position}_{file_type}.csv"
            file_path = runfolder / pattern
            
            if file_path.exists():
                chamber_files[file_type][position] = file_path
                logger.info(f"Found file: {file_path}")
            else:
                logger.warning(f"Missing file: {file_path}")
    
    return chamber_files


def calculate_ctdi_w(peripheral_doses: List[float], center_dose: float) -> float:
    """
    Calculate CTDI_w using the formula: (2/3 * average peripheral doses) + (1/3 * center dose)
    
    Args:
        peripheral_doses: List of peripheral dose values
        center_dose: Center dose value
        
    Returns:
        CTDI_w value
    """
    if not peripheral_doses:
        logger.warning("No peripheral doses provided")
        return 0.0
    
    if center_dose is None:
        logger.warning("No center dose provided")
        return 0.0
    
    peripheral_avg = sum(peripheral_doses) / len(peripheral_doses)
    ctdi_w = (2/3) * peripheral_avg + (1/3) * center_dose
    
    logger.info(f"Peripheral average: {peripheral_avg:.6e}, Center dose: {center_dose:.6e}")
    logger.info(f"CTDI_w: {ctdi_w:.6e}")
    
    return ctdi_w


def process_file_type(chamber_files: Dict[str, Path], file_type: str, calibration_factor: float = 1.0) -> Optional[Dict]:
    """
    Process files for a specific file type (dtw or tle).
    
    Args:
        chamber_files: Dictionary of file paths for the file type
        file_type: Type of files being processed ('dtw' or 'tle')
        calibration_factor: Calibration factor to scale doses
        
    Returns:
        Dictionary with results, or None if processing fails
    """
    logger.info(f"Processing {file_type} files")
    
    # Extract doses from peripheral positions
    peripheral_doses = []
    for position in PERIPHERAL_POSITIONS:
        if position in chamber_files:
            dose = extract_dose_from_file(chamber_files[position])
            if dose is not None:
                scaled_dose = dose * calibration_factor
                peripheral_doses.append(scaled_dose)
                logger.info(f"{position} dose: {scaled_dose:.6e} Gy (scaled by factor {calibration_factor})")
            else:
                logger.warning(f"Failed to extract dose from {position} file")
        else:
            logger.warning(f"Missing {position} position file")
    
    # Extract center dose
    center_dose = None
    if CENTER_POSITION in chamber_files:
        dose = extract_dose_from_file(chamber_files[CENTER_POSITION])
        if dose is not None:
            center_dose = dose * calibration_factor
            logger.info(f"Center dose: {center_dose:.6e} Gy (scaled by factor {calibration_factor})")
        else:
            logger.warning("Failed to extract dose from center file")
    else:
        logger.warning("Missing center position file")
    
    # Calculate CTDI_w
    if peripheral_doses and center_dose is not None:
        ctdi_w = calculate_ctdi_w(peripheral_doses, center_dose)
        peripheral_avg = sum(peripheral_doses) / len(peripheral_doses)
        
        return {
            "FileType": file_type,
            "PeripheralDoseAverage": peripheral_avg,
            "CenterDose": center_dose,
            "CTDI_w": ctdi_w,
            "CalibrationFactor": calibration_factor,
            "Timestamp": datetime.now().isoformat()
        }
    else:
        logger.error(f"Insufficient data to calculate CTDI_w for {file_type}")
        return None


def save_results(results: List[Dict], output_path: Path) -> None:
    """
    Save results to CSV file.
    
    Args:
        results: List of result dictionaries
        output_path: Path to save the CSV file
    """
    try:
        df = pd.DataFrame(results)
        df.to_csv(output_path, index=False)
        logger.info(f"Results saved to: {output_path}")
        console.print(f"✅ Results saved to: {output_path}", style="green")
    except Exception as e:
        logger.error(f"Error saving results: {e}")
        raise


def validate_runfolder(runfolder: Path) -> None:
    """
    Validate that the runfolder exists and is accessible.
    
    Args:
        runfolder: Path to the runfolder
        
    Raises:
        typer.BadParameter: If runfolder is invalid
    """
    if not runfolder.exists():
        raise typer.BadParameter(f"Runfolder does not exist: {runfolder}")
    
    if not runfolder.is_dir():
        raise typer.BadParameter(f"Path is not a directory: {runfolder}")
    
    # Check if at least one ChamberPlug file exists
    chamber_files_found = False
    for file_type in FILE_TYPES:
        for position in PERIPHERAL_POSITIONS + [CENTER_POSITION]:
            pattern = f"ChamberPlug{position}_{file_type}.csv"
            if (runfolder / pattern).exists():
                chamber_files_found = True
                break
        if chamber_files_found:
            break
    
    if not chamber_files_found:
        raise typer.BadParameter(
            f"No ChamberPlug CSV files found in runfolder: {runfolder}. "
            f"Expected files like: ChamberPlugTop_dtw.csv, ChamberPlugCenter_tle.csv"
        )


def main(
    runfolder: str = typer.Argument(..., help="Path to the runfolder containing ChamberPlug CSV files"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Output CSV filename (default: CTDIw_results.csv)")
) -> None:
    """
    Calculate CTDI_w values from ChamberPlug CSV files.
    
    This script processes ChamberPlug CSV files in the specified runfolder
    and calculates CTDI_w using the formula: (2/3 * average peripheral doses) + (1/3 * center dose)
    """
    # Convert to Path object
    runfolder_path = Path(runfolder).resolve()
    
    # Validate input
    validate_runfolder(runfolder_path)
    
    # Set output filename
    if output_file is None:
        output_path = runfolder_path / "CTDIw_results.csv"
    else:
        output_path = Path(output_file).resolve()
    
    console.print(f"🔍 Processing runfolder: {runfolder_path}", style="blue")
    
    # Extract calibration factor
    calibration_factor = extract_calibration_factor(runfolder_path)
    logger.info(f"Using calibration factor: {calibration_factor}")
    
    # Find all ChamberPlug files
    chamber_files = find_chamber_files(runfolder_path)
    
    # Process each file type
    results = []
    for file_type in FILE_TYPES:
        if chamber_files[file_type]:
            result = process_file_type(chamber_files[file_type], file_type, calibration_factor)
            if result:
                results.append(result)
        else:
            logger.warning(f"No files found for {file_type}")
    
    if not results:
        console.print("❌ No results generated. Check file availability and format.", style="red")
        raise typer.Exit(1)
    
    # Save results
    save_results(results, output_path)
    
    # Display summary
    console.print("\n📊 Results Summary:", style="bold")
    for result in results:
        console.print(f"  {result['FileType']}: CTDI_w = {result['CTDI_w']:.6e} Gy", style="cyan")


if __name__ == "__main__":
    typer.run(main)