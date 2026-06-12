## Context

`ImagingMode` is a frozen dataclass with 13 string fields, instantiated from raw tuples in `_IMAGING_MODES_DATA` (21 entries). `as_tuple()` returns all fields for the GUI's `BACKWARD_COMPAT_LOOKUP`. The config pipeline (`config.py`) reads YAML flat files into `ImagingConfig`/`CtdiConfig` dataclasses with no imaging mode resolution — every YAML file duplicates all 13 beam parameters. The GUI (`view.py`) has a hardcoded 7-item protocol dropdown and reads 13 fields for display.

The plan adds 8 fields and 26 entries. This design covers how the data model, resolution logic, config format, and GUI adapt.

## Goals / Non-Goals

**Goals:**
- Extend `ImagingMode` to hold all 21 protocol parameters needed for CTDI scoring and dose calibration
- Support all 20 TrueBeam CBCT protocols (7 existing + 13 new) across 2 rotation directions
- Auto-populate config from protocol name, eliminating parameter duplication in YAML files
- Preserve backward compatibility via `BACKWARD_COMPAT_LOOKUP` (with expanded tuple length)
- Keep existing tests passing with updated assertions

**Non-Goals:**
- kV-kV variants for new protocols
- GUI redesign or new UI elements for the 8 new fields
- Migration tooling for user-authored YAML configs
- Changing how Jinja2 templates consume config values

## Decisions

### D1: New fields appended to dataclass declaration order

Add 8 fields after the existing 13, in the order: `ctdi_phantom`, `dose_factor`, `start_angle`, `fan_detail`, `no_projections`, `proj_increment`, `acquisition_time`, `ctdiw_reference`.

**Rationale**: Appending preserves the positional indices of existing fields. Code that accesses fields by name (which is everything except `as_tuple()`) is unaffected. `as_tuple()` consumers break, but they're limited to `BACKWARD_COMPAT_LOOKUP` and the GUI's field display, both of which we're updating.

**Alternative rejected**: Interleaving new fields alongside their logical groupings (e.g., `fan_detail` next to `fan_mode`). This would shift all positional indices and make the migration harder to reason about.

### D2: Raw tuples grow from 13 to 21 elements

`_IMAGING_MODES_DATA` tuples expand from 13 to 21 elements, with new values in positions 14-21 matching the new field declaration order.

**Rationale**: Maintains the existing tuple-based data entry pattern. The tuples are internal to `imaging_mode.py` and only consumed by the `ImagingMode` constructor via unpacking.

### D3: `_resolve_imaging_mode()` is a module-level function in `config.py`

Signature: `_resolve_imaging_mode(imaging_data: dict, ctdi_data: dict) -> tuple[dict, dict]`

Called from `from_yaml()` after `yaml.safe_load()` but before dataclass construction. Takes the raw YAML dicts, composites the mode key (`imaging_data["rotation_direction"] + "_" + imaging_data["imaging_mode"]`), looks up `IMAGING_MODES[key]`, and fills missing values into the dicts. Returns modified `(imaging_data, ctdi_data)`. The function operates on YAML dict keys (`rotation_direction`, `imaging_mode`), not GUI element keys.

**Resolution algorithm**:
1. Extract `rotation_direction` and `imaging_mode` from `imaging_data`
2. Build key: `f"{rotation_direction}_{imaging_mode}"`
3. Look up `IMAGING_MODES[key]` — raise `ValueError` with valid keys if not found
4. For each mapped field, check if the YAML dict has the target key AND the value is not None/empty string
5. If YAML has the value → keep it (YAML wins)
6. If YAML lacks the value or it's None/empty → populate from mode field
7. Return modified dicts

**Mapping table** (mode field → YAML target key):

| Mode field | imaging_data key | ctdi_data key |
|---|---|---|
| `voltage` | `anode_voltage` | — |
| `ctdi_phantom` | — | `phantom_size` |
| `start_angle` | `start_angle` | — |
| `rotation_rate` | `rotation_rate` | — |
| `timeline_end` | `timeline_end` | — |
| `fan_mode` | `fan_mode` | — |
| `field_x1` | `field_x1` | — |
| `field_x2` | `field_x2` | — |
| `field_y1` | `field_y1` | — |
| `field_y2` | `field_y2` | — |
| `blade_x1` | `blade_x1` | — |
| `blade_x2` | `blade_x2` | — |
| `blade_y1` | `blade_y1` | — |
| `blade_y2` | `blade_y2` | — |
| `exposure` | `exposure` | — |

Fields NOT mapped: `dose_factor` (metadata only), `fan_detail`, `no_projections`, `proj_increment`, `acquisition_time`, `ctdiw_reference` (no corresponding config fields yet — available for future use).

**Value format constraints**:
- `ctdi_phantom` values in `ImagingMode` must exactly match `PhantomSize` enum values (`"16 cm"` or `"32 cm"`) to pass config validation after resolution.
- `start_angle` values must use Quantity-parseable format with units (e.g., `"0 deg"`, not `"0"`) because `ImagingConfig.start_angle` is `Quantity`-typed and `__post_init__` runs `Quantity.parse()`.
- All other mapped fields already carry units in their string values (e.g., `"100 kV"`, `"0.4 deg/s"`) which `Quantity.parse()` handles correctly.

**Rationale**: Module-level function keeps it testable independently of `SimulationConfig`. Called before dataclass construction so `validate()` still runs on the final values.

**Alternative rejected**: A method on `SimulationConfig`. This would require constructing the config first with potentially missing fields, then patching. Messier.

### D4: YAML format — mode name plus non-beam fields

New minimal YAML format:

```yaml
general:
  # ... unchanged
imaging:
  simulation_type: CTDI
  rotation_direction: CBCT Clockwise
  imaging_mode: Head
  # beam parameters auto-populated from mode — override by specifying them
ctdi:
  zbins: 5
  # phantom_size auto-populated from mode's ctdi_phantom — override by specifying it
  # ... other ctdi fields unchanged
```

**Rationale**: Users specify the protocol identity and only override what differs. The resolution function fills in the 15 mapped fields from the mode definition. Non-beam fields (simulation_type, sequential_times, zbins, couch params, water_chamber) remain explicit.

**Backward compatibility**: Existing full-format YAML files continue to work. If all beam parameters are present, the resolution function sees them and keeps them (YAML wins). No migration needed.

### D5: GUI dropdown derived from `IMAGING_MODES` keys

Replace the hardcoded 7-item dropdown list with a dynamically extracted list of unique protocol names from `IMAGING_MODES`. Filter to only CBCT keys (keys starting with `"CBCT Clockwise_"` or `"CBCT Anticlockwise_"`), strip the direction prefix, and deduplicate. kV-kV protocols do not appear in the dropdown.

**Rationale**: Adding 13 new protocol names to a hardcoded list is fragile. Dynamic extraction means future protocol additions are automatic.

### D6: `IMAGING_MODE_SELECTION_LABELS` grows to 21 labels

Add 8 new labels for the new fields: `"Phantom"`, `"Dose Factor"`, `"Start Angle"`, `"Fan Detail"`, `"Projections"`, `"Proj Increment"`, `"Acq Time"`, `"CTDIw Ref"`.

**Rationale**: Short labels for GUI column headers. Matches the field declaration order.

### D7: kV-kV entries get `"N/A"` for CBCT-specific new fields

kV-kV entries populate the 8 new fields with `"N/A"` for all except `start_angle` which gets `"0 deg"`. These are static 2-exposure setups with no rotation, no projections, no phantom, no acquisition timing.

**Rationale**: Avoids `None` in a string-typed dataclass. `"N/A"` is explicit about inapplicability.

## Risks / Trade-offs

- **`as_tuple()` length change (13→21) breaks positional consumers**: `BACKWARD_COMPAT_LOOKUP` is updated in the same change. External consumers (if any) will see longer tuples. → Mitigation: `BACKWARD_COMPAT_LOOKUP` is the only internal consumer, and the GUI update handles the expanded columns.

- **Resolution function masks config errors**: If a user typos a protocol name, they get a `ValueError` at config load time with the list of valid keys. → Mitigation: Explicit error message with valid options.

- **Duplicate protocol names across directions**: The key format `"CBCT Clockwise_Head"` includes direction, so there's no collision. But the GUI dropdown shows only the protocol name — users must still select direction separately. → Mitigation: Existing GUI pattern already separates direction and protocol selection.

- **Clinical data accuracy**: The 26 new entries and 21×8 updated values must match Varian TrueBeam specifications. Wrong values propagate to all simulations. → Mitigation: Values entered from verified specification sheets; tests validate field counts and key presence, not clinical accuracy.

## Open Questions

- Do the 13 new protocols have established Varian specification values for all 8 new fields? If some fields lack published values, `"TBD"` or empty strings may be needed temporarily.
- Should `fan_detail` values be documented somewhere for future mapping to a config field?
