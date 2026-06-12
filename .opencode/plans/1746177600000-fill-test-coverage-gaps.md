# Plan: Fill Test Coverage Gaps

## Problem

The test suite has 200 passing tests but leaves two significant source modules completely untested (`gui/controller.py`, `gui/view.py`), has duplicated fixtures across 3 files, no shared `conftest.py`, and missing edge case coverage in several areas. The `tests/integration/` directory is empty.

## Approach

Seven steps, ordered by priority and dependency. Steps 1-3 are infrastructure/refactor, steps 4-7 add new tests.

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `tests/unit/conftest.py` | Create | Shared fixtures: `MAIN_FILE_CONTENT`, `SUB_FILE_CONTENT`, `_make_dicom_config`, `_make_ctdi_config` |
| `tests/unit/test_gui_controller.py` | Create | Unit tests for `GUIController` event handlers |
| `tests/unit/test_gui_view.py` | Create | Unit tests for `MainView` update/helper methods |
| `tests/unit/test_base_mode.py` | Create | Direct tests for `SimulationMode.copy_common_files` |
| `tests/unit/test_config.py` | Modify | Add `_parse_bool` edge cases, `from_yaml` malformed input, `to_yaml` IOError |
| `tests/unit/test_parameter_editor.py` | Modify | Add empty list, partial prefix match tests |
| `tests/unit/test_fieldtobladeopening.py` | Modify | Add != 4 elements edge cases |
| `tests/unit/test_spectrum_generator.py` | Modify | Assert calibration factor value |
| `tests/unit/test_ctdi_mode.py` | Modify | Add direct `_generate_plug_files` tests (32cm, unknown size) |
| `tests/unit/test_orchestrator.py` | Modify | Add `_get_mode` unknown sim_type test, use shared fixtures |
| `tests/unit/test_dicom_mode.py` | Modify | Use shared fixtures from conftest |
| `tests/smoke/test_init.py` | Modify | Slim from 10 tests to 2-3 |
| `tests/integration/test_dry_run_pipeline.py` | Create | Integration test: config -> orchestrator dry-run end-to-end |

## Key Design Decisions

1. **Full mock for GUI tests** -- FreeSimpleGUI and pydicom are both fully mocked. No real GUI rendering or DICOM file access needed. This keeps tests fast and CI-friendly.

2. **`conftest.py` scope** -- Only `tests/unit/conftest.py` (not root `tests/conftest.py`) because smoke tests use different path conventions and don't need shared fixtures.

3. **Keep `sys.path.insert` in existing files** -- Adding it to conftest.py would be a larger refactor of all 18 test files. Out of scope; the shared conftest only provides fixtures, not path setup.

4. **GUI controller test strategy** -- Mock `MainView` as a `MagicMock` with the interface methods the controller calls (`read`, `reset_all`, `set_tab_visibility`, `update_patient_id`, etc.). Mock `Orchestrator.run`. Test each handler method in isolation, and test the `run()` event loop dispatch.

5. **GUI view test strategy** -- Mock `sg.Window` to avoid actual window creation. Test the update methods (`update_imaging_mode_fields`, `set_tab_visibility`, etc.) by verifying the correct `window[key].update()` calls.

6. **Python 3.8 target** -- All new code uses `from __future__ import annotations` and avoids walrus operator, `str.removeprefix`, `match` statements.

## Implementation Order

### Step 1: Create `tests/unit/conftest.py`

Extract duplicated fixtures from `test_orchestrator.py`, `test_dicom_mode.py`, `test_ctdi_mode.py`:

- `MAIN_FILE_CONTENT` -- the TOPAS main file template string (identical across all 3)
- `DICOM_SUB_FILE_CONTENT` -- DICOM sub-file template (from `test_dicom_mode.py`)
- `CTDI_SUB_FILE_CONTENT` -- CTDI sub-file template (from `test_ctdi_mode.py`)
- `_make_dicom_config(**overrides)` -- factory using `__dataclass_fields__` introspection
- `_make_ctdi_config(**overrides)` -- same pattern

Then update the 3 consumer files to import from conftest instead of defining locally. Remove the duplicated definitions. Run tests to confirm no breakage.

### Step 2: Slim `tests/smoke/test_init.py`

Reduce from 10 tests to 3:
- `test_init_module_imports` -- keep as-is
- `test_src_package_structure` -- keep as-is
- `test_init_module_no_side_effects` -- keep as-is

Remove: `test_init_module_exists`, `test_init_module_is_empty`, `test_init_module_no_executable_code`, `test_init_module_no_syntax_errors`, `test_init_module_encoding` (redundant with import test).

### Step 3: Create `tests/unit/test_gui_controller.py`

Test `GUIController` with fully mocked `MainView` and `Orchestrator`:

```
fixtures:
  - mock_view: MagicMock (with reset_all, set_tab_visibility, update_patient_id, 
    update_isocenter, update_imaging_mode_fields, show_error, show_popup,
    set_couch_visible, set_blade_visible, read)
  - mock_orchestrator: MagicMock

TestGUIControllerInit:
  - test_stores_view_and_orchestrator
  - test_event_handlers_map_has_expected_keys (RESET, SIM_TYPE, DICOM_DIR, etc.)

TestOnReset:
  - test_calls_reset_all_with_stored_defaults
  - test_hides_both_tabs

TestOnSimTypeChange:
  - test_shows_dicom_tab_hides_ctdi_for_dicom
  - test_shows_ctdi_tab_hides_dicom_for_ctdi

TestOnDicomDir:
  - test_reads_directory_and_updates_patient_id (mock os.listdir, dcmread)
  - test_shows_error_when_no_ct_images
  - test_shows_error_on_mixed_patient_ids
  - test_shows_popup_with_count

TestOnDicomRp:
  - test_extracts_isocenter_and_updates_view (mock dcmread with BeamSequence)
  - test_shows_error_on_missing_isocenter
  - test_shows_error_on_patient_id_mismatch

TestOnRun:
  - test_builds_config_and_calls_orchestrator
  - test_shows_error_on_exception

TestOnImagingModeChange:
  - test_updates_imaging_mode_fields_from_lookup

TestOnCouchToggle:
  - test_sets_couch_visible_true
  - test_sets_couch_visible_false

TestOnUserBladeToggle:
  - test_sets_blade_visible_true
  - test_sets_blade_visible_false

TestRun:
  - test_dispatches_reset_handler
  - test_dispatches_sim_type_handler
  - test_ignores_unknown_events
  - test_breaks_on_win_closed
```

Key mocks needed:
- `from unittest.mock import MagicMock, patch, PropertyMock`
- `patch("src.gui.controller.dcmread")` for pydicom
- `mock_view.read.return_value = (event, values_dict)`

### Step 4: Create `tests/unit/test_gui_view.py`

Test `MainView` with mocked `sg.Window`:

```
fixtures:
  - mock_window: MagicMock
  - patch("src.gui.view.sg.Window", return_value=mock_window)
  - view: MainView instance

TestMainViewInit:
  - test_creates_window_with_correct_title
  - test_binds_enter_key_to_g4_data_dir

TestUpdateImagingModeFields:
  - test_updates_all_13_fields_from_imaging_mode

TestSetTabVisibility:
  - test_dicom_shows_ctdi_hides
  - test_ctdi_shows_dicom_hides

TestResetAll:
  - test_updates_all_keys_with_defaults
  - test_hides_both_tabs

TestUpdatePatientId:
  - test_updates_patient_id_element

TestUpdateIsocenter:
  - test_updates_iso_x_y_z_elements

TestSetCouchVisible:
  - test_calls_update_with_visible_true
  - test_calls_update_with_visible_false

TestSetBladeVisible:
  - test_calls_update_with_visible_true
  - test_calls_update_with_visible_false

TestShowError:
  - test_calls_sg_popup_error

TestShowPopup:
  - test_calls_sg_popup_with_message_and_value
  - test_calls_sg_popup_with_message_only

TestClose:
  - test_calls_window_close
```

### Step 5: Create `tests/unit/test_base_mode.py`

Test `SimulationMode.copy_common_files` directly:

```
TestCopyCommonFiles:
  - test_copies_muen_dat (use tmp_path, create boilerplates structure)
  - test_copies_nbparticlesintime
  - test_copies_converted_topas_file
  - test_copies_calibration_factor
  - test_copies_fullfan_for_full_fan_mode
  - test_copies_halffan_for_half_fan_mode
  - test_copies_no_fan_file_for_unknown_mode (neither Full nor Half)
```

Use `tmp_path` fixture with manually created boilerplate file structure.

### Step 6: Add edge case tests to existing files

**`test_config.py`** -- add:
- `TestParseBool`: test `True`, `"True"`, `False`, `"False"`, `1`, `0`, `""`, `"true"` (lowercase)
- `TestFromYamlMalformed`: test `from_yaml` with non-dict YAML raises error or uses defaults
- `TestToDictAllKeys`: expand to check all 51 placeholder keys are present

**`test_parameter_editor.py`** -- add:
- `test_empty_list_returns_false`
- `test_partial_prefix_does_not_match_wrong_line` (e.g., searching "i:Ts/Seed" should NOT match "i:Ts/SeedExtra")

**`test_fieldtobladeopening.py`** -- add:
- `test_empty_list_raises_error`
- `test_three_elements_raises_index_error` (count==3 has no else branch for y blade, actually count >= 4 uses else; need to verify)
- `test_five_elements_extra_ignored` (count >= 4 all get ybladeopening * -1)

**`test_spectrum_generator.py`** -- add:
- `test_calibration_factor_is_correct` -- compute expected: `4 * pi * 0.01 * get_flu() / int(histories)` and assert

**`test_ctdi_mode.py`** -- add:
- `TestGeneratePlugFiles32cm` -- phantom_size="32 cm" uses CTDIphantom_32.txt
- `TestGeneratePlugFilesUnknownSize` -- phantom_size="40 cm" falls back to ctdi16
- `TestGeneratePlugFilesContent` -- verify placeholder replacement and material swap in generated files

**`test_orchestrator.py`** -- add:
- `test_get_mode_unknown_returns_ctdi_mode` (anything that isn't "DICOM" falls through to CtdiMode)

### Step 7: Create `tests/integration/test_dry_run_pipeline.py`

End-to-end integration test that doesn't require TOPAS or real files:

```
TestDryRunPipeline:
  - test_dicom_config_to_dry_run_creates_runfolder
    - Create a real tmp_path with boilerplates structure
    - Build SimulationConfig with DICOM type
    - Call Orchestrator(config).run(config, dry_run=True)
    - Assert runfolder was created
    - Assert headsourcecode.txt was modified (common edits applied)
    - Assert patientDICOM.txt was modified
    - Assert ConvertedTopasFile.txt was created
    - Assert execute was NOT called

  - test_ctdi_config_to_dry_run_creates_runfolder
    - Same pattern for CTDI mode
    - Assert CTDIphantom_16.txt was modified
```

This requires real file I/O but no external executables. It validates the full orchestrator pipeline end-to-end.

## Estimated New Tests

| File | New Tests | Notes |
|------|-----------|-------|
| `conftest.py` | 0 (fixtures only) | |
| `test_gui_controller.py` | ~18 | Biggest new file |
| `test_gui_view.py` | ~15 | |
| `test_base_mode.py` | ~7 | |
| `test_config.py` (additions) | ~5 | |
| `test_parameter_editor.py` (additions) | ~2 | |
| `test_fieldtobladeopening.py` (additions) | ~3 | |
| `test_spectrum_generator.py` (additions) | ~1 | |
| `test_ctdi_mode.py` (additions) | ~3 | |
| `test_orchestrator.py` (additions) | ~1 | |
| `test_dry_run_pipeline.py` | ~2 | Integration tier |
| **Total new** | **~57** | |
| `test_init.py` (removed) | -7 | |
| **Net change** | **+50 tests** | |

Final test count estimate: ~250 tests.
