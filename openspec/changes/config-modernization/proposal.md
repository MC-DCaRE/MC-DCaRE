## Why

All dimensional values in `SimulationConfig` are stored as `str` (`"6.175536078965273 cm"`, `"100 kV"`). Validation happens late (at render time) and only covers enum fields and integer-valued strings. Physical parameters like `isocenter_x`, `couch_width`, and `blade_x1` accept any garbage string, failing at render time with unclear errors.

The `_PLACEHOLDER_MAP` in `config.py` couples config dataclasses directly to FreeSimpleGUI element keys. Config cannot exist without knowing about GUI keys, making the config module harder to reuse from CLI contexts.

`SimulationConfig` is mutable (`frozen=False`) while its sub-configs are immutable (`frozen=True`).

## What Changes

- Replace string-typed dimensional fields with `Quantity` objects (value + unit)
- Reverse coupling: config uses `Quantity` types, a separate adapter maps config→GUI keys
- Make `SimulationConfig` frozen (immutable) like its sub-configs
- Add early validation in `validate()` for all dimensional fields
- Update all consumers (modes, spectrum generator, orchestrator) to use typed access

## Capabilities

### Modified Capabilities
- `config-system`: Typed dimensional values, immutability, decoupled GUI mapping

## Impact

- `src/config.py` — major refactor: `Quantity` types, remove `_PLACEHOLDER_MAP` coupling
- `src/models/quantity.py` — may need enhancements
- `src/modes/ctdi_mode.py` — read `Quantity` from config instead of strings
- `src/modes/dicom_mode.py` — same
- `src/spectrum_generator.py` — receive typed values instead of parsing strings
- `src/fieldtobladeopening.py` — receive typed values
- `src/orchestrator.py` — updated type flow
- `src/gui/controller.py` — use adapter for GUI mapping
- All test files matching config consumers
