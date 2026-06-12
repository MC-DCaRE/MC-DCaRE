## Why

`ImagingMode` defines 7 CBCT protocols across 2 rotation directions (Clockwise, Anticlockwise) plus 7 kV-kV entries (21 entries total, 13 fields each). The TrueBeam platform supports 20 clinical CBCT protocols. Config files duplicate all 13 beam parameters manually with no lookup table resolution, so adding a protocol or field means editing 8+ locations and 3+ YAML files. This change adds the 13 missing CBCT protocols and introduces name-based config resolution so YAML files only specify the protocol name.

## What Changes

- Add 8 new fields to `ImagingMode`: `ctdi_phantom`, `dose_factor`, `start_angle`, `fan_detail`, `no_projections`, `proj_increment`, `acquisition_time`, `ctdiw_reference` (13 → 21 fields total)
- Add 13 new CBCT protocols (4D Spotlight, 4D Thorax, Abdomen, Abdo Spotlight, Breast 360, Extremity Spotlight, Head and Shoulders, Head SRS, Paediatric Body, Pediatric Head, Pelvis Spotlight, SBRT Spine, Thorax Spotlight) × 2 directions = 26 new entries (21 → 47 total, kV-kV stays at 7)
- Add `_resolve_imaging_mode()` in `config.py` that composites `rotation_direction + "_" + imaging_mode` → `IMAGING_MODES` lookup → auto-populates `ImagingConfig` and `CtdiConfig` fields, with YAML values always winning over mode defaults. Explicitly absent or null YAML values fall back to mode defaults. Maps 15 fields: `voltage→anode_voltage`, `ctdi_phantom→phantom_size`, `start_angle`, `rotation_rate`, `timeline_end`, `fan_mode`, `field_x1`, `field_x2`, `field_y1`, `field_y2`, `blade_x1`, `blade_x2`, `blade_y1`, `blade_y2`, `exposure`. **`dose_factor` is metadata only — NOT auto-mapped to `dose_calibration_factor`.**
- Existing 21 entries receive the 8 new fields populated with real clinical values from Varian specifications. kV-kV entries use `"N/A"` for CBCT-specific fields (`ctdi_phantom`, `no_projections`, `proj_increment`, `acquisition_time`, `ctdiw_reference`), `"0 deg"` for `start_angle`, `"N/A"` for `fan_detail`, and `"N/A"` for `dose_factor`.
- **BREAKING**: `as_tuple()` returns 21 items (was 13). `IMAGING_MODE_SELECTION_LABELS` grows from 13 to 21. `BACKWARD_COMPAT_LOOKUP` per-value list length grows from 13 to 21. Any code indexing into `as_tuple()` by position breaks.
- Simplify `ctdi_config.yaml` to mode-name-only format: YAML specifies `rotation_direction` and `imaging_mode` only; resolution fills beam parameters. Non-beam fields (`phantom_size`, `zbins`, etc.) remain explicit in YAML.

## Capabilities

### New Capabilities
- `name-based-config-resolution`: Auto-populate `ImagingConfig` and `CtdiConfig` from protocol name via `_resolve_imaging_mode()`, mapping 15 fields from the resolved mode. YAML overrides win over mode defaults; absent/null YAML values fall back to mode defaults. `dose_factor` excluded from mapping.
- `clinical-protocol-extensions`: 13 new CBCT protocols with 8 new fields covering phantom selection, dose factors, acquisition geometry, and CTDIw reference values. All 47 entries populated with real clinical data.

### Modified Capabilities
<!-- No existing specs to modify — openspec/specs/ is empty -->

## Impact

- **`src/models/imaging_mode.py`**: +8 fields, +26 entries, updated `as_tuple()`, `IMAGING_MODE_SELECTION_LABELS`, `BACKWARD_COMPAT_LOOKUP`
- **`src/config.py`**: new `_resolve_imaging_mode()` method, called from `from_yaml()`
- **`src/imaging_modes_lookuptable.py`**: re-export shim unaffected (transparent)
- **`src/gui/view.py`**: hardcoded dropdown (7 protocol names at line 416) must expand to 20; `update_imaging_mode_fields()` (line 973) reads 13 fields by name, needs 21. GUI table gains 8 columns.
- **`src/gui/controller.py`**: `mode_key` construction at line 149 already handles `direction + "_" + mode` pattern — no logic change needed
- **`ctdi_config.yaml`**, **`kvk_config.yaml`**, **`config.yaml`**, and **`examples/config/`** configs: simplified format
- **`tests/unit/test_imaging_mode.py`**: `test_as_tuple_length` → 21, +26 new protocol keys, +resolution tests
- **`tests/unit/test_config.py`** (new or existing): resolution override tests
- Jinja2 templates: no impact — templates read from `config.imaging.*` fields, not directly from `ImagingMode`

## Non-goals

- Adding kV-kV variants for the new 13 protocols (kV-kV stays at 7 original entries)
- GUI redesign for new fields (read-only display in existing table, no new UI elements)
- Migration tooling for existing user YAML configs
- Auto-generating protocol data from external sources
- Deprecating `imaging_modes_lookuptable.py` re-export shim
