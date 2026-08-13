# models

## Purpose
Immutable domain value objects and constants for simulation configuration. Defines enums, physical quantities, imaging mode lookup tables, and FreeSimpleGUI element key constants.

## Architecture
Flat module with no subdirectories. Each file is a self-contained domain concept:
- `enums.py` defines simulation and fan type enumerations used by `modes/` and `config.py`
- `quantity.py` defines a `Quantity` frozen dataclass for physical values with units
- `imaging_mode.py` provides a frozen dataclass (21 fields) mapping beam parameters (rotation rate, voltage, fan mode, field size, blade openings, CTDI phantom, dose factor, acquisition geometry) for 47 Varian TrueBeam kV imaging protocols. Includes the `IMAGING_MODES` lookup dict.
- `keys.py` defines string constants used as FreeSimpleGUI element keys throughout `gui/`

## Key Files

| File | Role |
|---|---|
| `enums.py` | `SimulationType` (DICOM/CTDI) and `FanMode` (FullFan/HalfFan) enums |
| `quantity.py` | `Quantity` frozen dataclass for physical values with value and unit fields |
| `imaging_mode.py` | `ImagingMode` frozen dataclass (21 fields) with the `IMAGING_MODES` lookup table for 47 TrueBeam kV imaging presets and blade constants |
| `keys.py` | Uppercase string constants (`-KEY-` format) for FreeSimpleGUI element identification |

## Conventions
- All dataclasses use `frozen=True` for immutability
- No I/O or side effects (pure value objects)
- `logging.getLogger(__name__)` used only in `imaging_mode.py`
- GUI key constants follow `-UPPERCASE_WITH_DASHES-` pattern
- Enum values match display strings shown in the GUI dropdown
