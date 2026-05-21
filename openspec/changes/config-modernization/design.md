## Context

`SimulationConfig` has 49 string-typed fields for physical quantities. Validation in `validate()` only checks enum membership and integer-valued strings. The `_PLACEHOLDER_MAP` tuple list couples every config field to a FreeSimpleGUI element key (`keys.py`), meaning config cannot exist without the GUI module.

Current flow:
```
YAML → strings → config (no validation) → mode parses strings → template
GUI → GUI_KEY values → config (via _PLACEHOLDER_MAP) → same path
```

## Goals / Non-Goals

**Goals:**
- Dimensional config fields stored as `Quantity` (value: float, unit: str)
- Config validated at construction time (fail fast)
- Config decoupled from GUI keys — adapter handles mapping
- `SimulationConfig` frozen (immutable)

**Non-Goals:**
- Changing the YAML file format (backward compatible)
- Changing template rendering (context dicts still use strings for Jinja2)
- Removing `keys.py` (still needed for GUI)
- Changing the CTDI phantom or DICOM mode architectures

## Decisions

1. **`Quantity` for dimensional fields**: Fields like `blade_x1`, `anode_voltage`, `isocenter_x` become `Quantity` objects. Integer-valued string fields (`seed`, `threads`, `histories`) remain `str` for now (validated as int in `validate()`).

2. **GUI adapter pattern**: New `GUIAdapter` class owns the mapping between config fields and GUI keys. Config doesn't import `keys.py`. The adapter translates `Quantity` → string for GUI display and GUI string → `Quantity` for config construction.

3. **YAML backward compatibility**: `from_yaml()` parses strings into `Quantity` objects. `to_yaml()` serializes `Quantity` back to strings. Existing YAML files work unchanged.

4. **Frozen top-level config**: `SimulationConfig` gets `frozen=True`. Factory methods (`from_yaml`, `from_gui_values`, `defaults`) construct immutable instances.

5. **Template context stays string-based**: Modes still produce `Dict[str, object]` for Jinja2. The mode's `build_*_context()` method calls `str(quantity)` or `quantity.to_topas_string()` to produce the string the template expects.

## Risks / Trade-offs

- **Risk**: Large refactor touching config, modes, GUI, and all consumers. Mitigation: incremental approach — type fields first, then decouple GUI adapter.
- **Risk**: `Quantity` parsing edge cases (unitless values, compound units). Mitigation: existing `Quantity.parse()` handles most cases; add tests for edge cases.
- **Trade-off**: More code in the adapter layer, but config becomes reusable without GUI dependency.
