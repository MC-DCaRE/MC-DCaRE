# models

## Purpose
Immutable domain value objects and constants for simulation configuration. Defines enums, physical quantities, imaging mode lookup tables, and FreeSimpleGUI element key constants.

## Architecture
Flat module with no subdirectories. Each file is a self-contained domain concept:
- `enums.py` defines simulation and fan type enumerations used by `modes/` and `config.py`
- `quantity.py` defines a `Quantity` frozen dataclass for physical values with units
- `imaging_mode.py` provides a large frozen dataclass (~398 lines) mapping beam parameters (rotation rate, voltage, bowtie, SAD, blade openings) for each Varian TrueBeam imaging mode
- `keys.py` defines string constants used as FreeSimpleGUI element keys throughout `gui/`

## Key Files

| File | Role |
|---|---|
| `enums.py` | `SimulationType` (DICOM/CTDI) and `FanMode` (FullFan/HalfFan) enums |
| `quantity.py` | `Quantity` frozen dataclass for physical values with value and unit fields |
| `imaging_mode.py` | `ImagingMode` frozen dataclass with rotation rate, voltage, bowtie type, SAD, blade openings, and lookup tables for all TrueBeam kV imaging presets |
| `keys.py` | Uppercase string constants (`-KEY-` format) for FreeSimpleGUI element identification |

## Conventions
- All dataclasses use `frozen=True` for immutability
- No I/O or side effects (pure value objects)
- `logging.getLogger(__name__)` used only in `imaging_mode.py`
- GUI key constants follow `-UPPERCASE_WITH_DASHES-` pattern
- Enum values match display strings shown in the GUI dropdown
