## proposal Round 1 — 2026-06-11

### 🔴 Fixed
- Protocol count corrected: 13 new protocols (not 14), × 2 directions = 26 new entries, 47 total (not 49)
- All derived counts updated throughout: +26 entries in Impact, +26 protocol keys in tests
- Added `dose_factor` exclusion constraint: "metadata only, NOT auto-mapped to dose_calibration_factor"
- Added strategy for existing 21 entries receiving 8 new fields: real clinical values for CBCT, "N/A" for kV-kV CBCT-specific fields
- Expanded GUI impact: hardcoded dropdown (7→20), update_imaging_mode_fields (13→21 fields), +8 columns
- Added YAML target format description: rotation_direction + imaging_mode only, non-beam fields remain explicit
- Fixed BACKWARD_COMPAT_LOOKUP phrasing: "per-value list length grows from 13 to 21"
- Added Non-goals section: kV-kV variants, GUI redesign, migration tooling, auto-generation, shim deprecation

### 🟡 Addressed
- Listed specific YAML files affected (ctdi_config.yaml, kvk_config.yaml, config.yaml, examples/config/)
- Noted controller.py mode_key construction already works correctly

### 🔴 Outstanding
(none)

## proposal Round 2 — 2026-06-11

### 🔴 Fixed
- "3 rotation directions" corrected to "2 rotation directions (Clockwise, Anticlockwise) plus 7 kV-kV entries (a different modality)"
- "21 clinical CBCT protocols" corrected to "20 clinical CBCT protocols" (7 existing + 13 new = 20)
- "Maps 10 fields" corrected to "Maps 15 fields" with each field listed individually (not shorthand)
- Added null/absent YAML value fallback behavior: falls back to mode defaults
- kV-kV handling for remaining new fields: `fan_detail` → `"N/A"`, `dose_factor` → `"N/A"`

### 🟡 Addressed
- Capability description updated to match corrected 15-field mapping count

### 🔴 Outstanding
(none)

## design Round 1 — 2026-06-11

### 🔴 Fixed
- Removed `general_data` from `_resolve_imaging_mode()` signature (no mapping targets in general section)
- Added value format constraints: `ctdi_phantom` must match `PhantomSize` enum values (`"16 cm"`/`"32 cm"`), `start_angle` must be Quantity-parseable (`"0 deg"`)
- D5 dropdown extraction now filters to CBCT keys only (excludes kV-kV prefix)
- Clarified resolution function operates on YAML dict keys, not GUI element keys

### 🟡 Addressed
- Noted all other mapped fields already carry units compatible with `Quantity.parse()`

### 🔴 Outstanding
(none)

## specs Round 1 — 2026-06-11

### 🔴 Fixed
- `dose_factor` scenario rephrased: removed `general_data` reference (contradicts frozen 2-param signature), now tests that resolution output contains no dose_factor-derived keys
- Added empty string YAML fallback scenario
- Added missing `rotation_direction` error scenario (raises ValueError)
- Added kV-kV direction rejection scenario (raises ValueError, prevents invalid phantom_size)
- Explicitly listed 6 unmapped fields after mapping table (dose_factor, fan_detail, no_projections, proj_increment, acquisition_time, ctdiw_reference)
- Added integration requirement with from_yaml() and minimal-YAML scenario

### 🟡 Addressed
- All scenarios now consistent with frozen 2-parameter function signature

### 🔴 Outstanding
(none)
