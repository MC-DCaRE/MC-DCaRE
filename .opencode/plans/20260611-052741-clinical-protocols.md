# Clinical Protocols & Name-Based Config Resolution

## Summary

Extend `ImagingMode` with 8 new fields (ctdi_phantom, dose_factor, start_angle, fan_detail, no_projections, proj_increment, acquisition_time, ctdiw_reference) for 21 total. Add 14 new CBCT protocols × 2 directions = 28 entries. Add `_resolve_imaging_mode()` in `config.py` to auto-populate config sections from the mode name. YAML values always win over mode defaults.

## Files Modified

| File | Change |
|---|---|
| `src/models/imaging_mode.py` | +8 fields, +28 protocol entries, update `as_tuple()` to 21, update `IMAGING_MODE_SELECTION_LABELS` to 21, rebuild `BACKWARD_COMPAT_LOOKUP` |
| `src/config.py` | Add `_resolve_imaging_mode()`, call in `from_yaml()` |
| `tests/unit/test_imaging_mode.py` | Update `test_as_tuple_length` to 21, add 28 new protocol keys, add resolution tests |
| `ctdi_config.yaml` | Simplify to mode-only format |

## Protocol Data (14 new + 7 existing = 21 protocols)

All dimensions (rotation_rate, timeline_end, field/blade positions) derived per rules:
- Full Fan: 14×14 cm fields, x=6.176/-6.176, y=5.814/-5.814
- Half Fan: 24.7×3.3 cm fields, x=6.940/-5.411, y=5.814/-5.814
- Half trajectory → 501s, Full trajectory → 900s
- Phantom 160mm → "16 cm", 320mm → "32 cm"
- CW uses +0.4 deg/s, CCW uses -0.4 deg/s

New protocols: 4D Spotlight, 4D Thorax, Abdomen, Abdo Spotlight, Breast 360, Extremity Spotlight, Head and Shoulders, Head SRS, Paediatric Body, Pediatric Head, Pelvis Spotlight, SBRT Spine, Thorax Spotlight

## Resolution Logic

`_resolve_imaging_mode(imaging_data, general_data, ctdi_data)` maps:
- `mode.voltage` → `imaging.anode_voltage`
- `mode.ctdi_phantom` → `ctdi.phantom_size`
- `mode.start_angle` → `imaging.start_angle`
- `mode.rotation_rate` → `imaging.rotation_rate`
- `mode.timeline_end` → `imaging.timeline_end`
- `mode.fan_mode` → `imaging.fan_mode`
- `mode.field_x1/x2/y1/y2` → `imaging.field_x1/x2/y1/y2`
- `mode.blade_x1/x2/y1/y2` → `imaging.blade_x1/x2/y1/y2`
- `mode.exposure` → `imaging.exposure`
- `mode.dose_factor` → metadata only (NOT auto-mapped to `dose_calibration_factor`)

YAML explicit values always override mode defaults.
