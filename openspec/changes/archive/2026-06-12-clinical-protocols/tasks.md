## 1. ImagingMode Data Model Extension

- [x] 1.1 Add 8 new fields to `ImagingMode` dataclass in `src/models/imaging_mode.py`: `ctdi_phantom`, `dose_factor`, `start_angle`, `fan_detail`, `no_projections`, `proj_increment`, `acquisition_time`, `ctdiw_reference` (all `str`, appended after existing 13 fields)
- [x] 1.2 Update `as_tuple()` to return all 21 fields (should be automatic via `dataclasses.fields()` but verify)
- [x] 1.3 Update `IMAGING_MODE_SELECTION_LABELS` from 13 to 21 items, appending: `"Phantom"`, `"Dose Factor"`, `"Start Angle"`, `"Fan Detail"`, `"Projections"`, `"Proj Increment"`, `"Acq Time"`, `"CTDIw Ref"`
- [x] 1.4 Add values for the 8 new fields to all 21 existing tuples in `_IMAGING_MODES_DATA` (CBCT entries: real clinical values; kV-kV entries: `"N/A"` for CBCT-specific fields, `"0 deg"` for start_angle, `"N/A"` for fan_detail and dose_factor)

## 2. New Protocol Entries

- [x] 2.1 Add 26 new tuples to `_IMAGING_MODES_DATA` for the 13 new CBCT protocols (4D Spotlight, 4D Thorax, Abdomen, Abdo Spotlight, Breast 360, Extremity Spotlight, Head and Shoulders, Head SRS, Paediatric Body, Pediatric Head, Pelvis Spotlight, SBRT Spine, Thorax Spotlight) × 2 directions
- [x] 2.2 Verify `IMAGING_MODES` dict has exactly 47 entries after rebuild
- [x] 2.3 Verify `BACKWARD_COMPAT_LOOKUP` has 48 entries (1 selection + 47 modes), each value a list of 21 items

## 3. Config Resolution Function

- [x] 3.1 Add `_resolve_imaging_mode(imaging_data: dict, ctdi_data: dict) -> tuple[dict, dict]` to `src/config.py`
- [x] 3.2 Implement key construction: `f"{imaging_data['rotation_direction']}_{imaging_data['imaging_mode']}"` with `KeyError` → `ValueError` for missing keys
- [x] 3.3 Implement `IMAGING_MODES` lookup with `ValueError` for invalid keys (listing valid options)
- [x] 3.4 Add kV-kV direction rejection: raise `ValueError` if `rotation_direction` starts with `"kV-kV"`
- [x] 3.5 Implement the 15-field mapping loop with YAML-wins-over-defaults logic (absent/None/empty string → mode default)
- [x] 3.6 Ensure `dose_factor` and the 5 other unmapped fields (fan_detail, no_projections, proj_increment, acquisition_time, ctdiw_reference) are NOT written to any dict
- [x] 3.7 Call `_resolve_imaging_mode()` from `from_yaml()` after `yaml.safe_load()` but before dataclass construction

## 4. GUI Updates

- [x] 4.1 Replace hardcoded 7-item protocol dropdown in `src/gui/view.py` (line ~416) with dynamic extraction from `IMAGING_MODES` keys (filter to CBCT only, strip direction prefix, deduplicate → 20 items)
- [x] 4.2 Update `update_imaging_mode_fields()` in `src/gui/view.py` (line ~973) to read all 21 fields instead of 13
- [x] 4.3 Verify GUI table displays 21 columns correctly

## 5. YAML Config Simplification

- [x] 5.1 Simplify `ctdi_config.yaml` to mode-name-only format (keep `rotation_direction` and `imaging_mode`, remove duplicated beam parameters, keep non-beam fields like `zbins`, `couch` params)
- [x] 5.2 Update `kvk_config.yaml` to remove duplicated beam parameters (resolution not applied for kV-kV, but can still simplify if appropriate)
- [x] 5.3 Update `config.yaml` and `examples/config/` configs similarly

## 6. Tests

- [x] 6.1 Update `test_as_tuple_length` in `tests/unit/test_imaging_mode.py` from 13 to 21
- [x] 6.2 Add 26 new protocol keys to `test_all_expected_keys_present`
- [x] 6.3 Add test for kV-kV entries having `"N/A"` for CBCT-specific new fields and `"0 deg"` for start_angle
- [x] 6.4 Add tests for `_resolve_imaging_mode()`: valid CBCT resolution, invalid key raises ValueError, missing rotation_direction raises ValueError, kV-kV direction raises ValueError
- [x] 6.5 Add tests for YAML override behavior: explicit value wins, absent key falls back, null falls back, empty string falls back
- [x] 6.6 Add test for dose_factor not appearing in resolution output
- [x] 6.7 Add test for `ctdi_phantom` → `phantom_size` mapping with valid PhantomSize values
- [x] 6.8 Add integration test: minimal YAML produces fully populated `SimulationConfig`

## 7. Verification

- [x] 7.1 Run `uv run ruff format src/ tests/` and `uv run ruff check src/ tests/ --fix`
- [x] 7.2 Run `uv run mypy src/` (clean after `rm -rf .mypy_cache`)
- [x] 7.3 Run `uv run python -m pytest tests/ -v` — all tests pass
- [x] 7.4 Run `uv run python -m pytest tests/ --cov=src/` — coverage maintained or improved
