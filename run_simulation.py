#!/usr/bin/env python3
import json
import logging
import os
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Optional

import typer
from src.config import SimulationConfig
from src.orchestrator import Orchestrator

_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

app = typer.Typer()

logging.basicConfig(level=logging.INFO, format=_LOG_FORMAT)
logger = logging.getLogger(__name__)


def _add_file_handler(runfolder: str, log_filename: str) -> logging.FileHandler:
    handler = logging.FileHandler(os.path.join(runfolder, log_filename), mode="w")
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter(_LOG_FORMAT))
    logging.getLogger().addHandler(handler)
    return handler


def _remove_file_handler(handler: logging.FileHandler) -> None:
    logging.getLogger().removeHandler(handler)
    handler.close()


@app.command()
def run(config_file: str, dry_run: bool = False) -> None:
    config = SimulationConfig.from_yaml(config_file)
    orchestrator = Orchestrator(os.getcwd())
    if dry_run:
        rundir = orchestrator.prepare_only(config)
        file_handler = _add_file_handler(rundir, config.general.log_filename)
        logger.info("Dry run prepared in %s", rundir)
        _remove_file_handler(file_handler)
        print("Files prepared in " + rundir + ". TOPAS not executed.")
    else:
        rundir = orchestrator.create_runfolder()
        file_handler = _add_file_handler(rundir, config.general.log_filename)
        try:
            orchestrator.run_with_runfolder(rundir, config)
            logger.info("Simulation completed in %s", rundir)
        finally:
            _remove_file_handler(file_handler)
        print("Simulation completed in " + rundir)


@app.command()
def generate_config(output: str = "simulation_config.yaml") -> None:
    config = SimulationConfig.defaults()
    config.to_yaml(output)
    print("Template config written to " + output)


@app.command()
def validate(config_file: str) -> None:
    if not Path(config_file).exists():
        print("File not found: " + config_file, file=sys.stderr)
        raise typer.Exit(code=1)
    try:
        SimulationConfig.from_yaml(config_file)
        print("Configuration is valid: " + config_file)
    except Exception as e:
        print("Validation failed: " + str(e), file=sys.stderr)
        raise typer.Exit(code=1)


@app.command()
def convert(
    input_file: str,
    output_file: str,
    output_format: Optional[str] = typer.Option(
        None,
        "--format",
        help="Output format: yaml or json (auto-detected from extension if omitted)",
    ),
) -> None:
    config = SimulationConfig.from_yaml(input_file)
    ext = Path(output_file).suffix.lower()
    fmt = output_format or (ext.lstrip(".") if ext else None)
    if fmt not in ("yaml", "yml", "json"):
        print("Unsupported format: " + str(fmt), file=sys.stderr)
        raise typer.Exit(code=1)
    if fmt == "json":
        data = {
            "general": asdict(config.general),
            "imaging": asdict(config.imaging),
            "dicom": asdict(config.dicom),
            "ctdi": asdict(config.ctdi),
        }
        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)
    else:
        config.to_yaml(output_file)
    print("Converted " + input_file + " to " + output_file)


if __name__ == "__main__":
    app()
