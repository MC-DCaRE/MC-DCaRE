# Implementation Plan: TOPAS Parallel Worlds for CTDI Scoring

**Branch:** `develop-simulation-parallel-worlds`
**Date:** 2026-05-05
**Status:** Planning

---

## 1. Overview

### Current Approach
The MC-DCaRE project runs **5 separate TOPAS processes** in parallel using Python's `multiprocessing.Pool` for CTDI simulations — one per chamber plug position (Centre, Top, Bottom, Left, Right). Each process:

1. Renders a phantom template with one plug set to Air and the other four set to PMMA
2. Creates a separate TOPAS parameter file (e.g., `ChamberPlugCentre.txt`)
3. Runs as an independent TOPAS simulation via `multiprocessing.Pool.starmap`

### Proposed Approach
Replace the 5-process parallel execution with a **single TOPAS simulation** that scores all 5 plug positions simultaneously using TOPAS Parallel Worlds with Layered Mass Geometry. All 5 plugs will be set to Air material, each in its own parallel world, and 15 scorers (3 per position × 5 positions) will be defined in a single parameter file.

### Key Insight
The `headsourcecode_boilerplate.j2` template **already configures** `Ph/Default/LayeredMassGeometryWorlds` with all 5 plug names (line 12). The plugs already have `isParallel="True"` in the phantom templates. The infrastructure for parallel worlds is partially in place — the change is primarily about consolidating from 5 separate simulations into 1.

---

## 2. Detailed Changes

### 2.1 Template Changes

#### File: `src/boilerplates/TOPAS_includeFiles/CTDIphantom_16.j2`

**Current behaviour:** The template renders a single set of 3 scorers (`ChamberPlugDose_tle`, `ChamberPlugDose_dtm`, `ChamberPlugDose_dtw`) that all target `{{ plug_position }}` as the scored component. Plug materials are set via `plug_material_centre`, `plug_material_top`, etc., where only the active position gets Air and the rest get PMMA.

**Proposed changes:**

1. **Set ALL plug materials to Air** — remove the `plug_material_*` template variables and hardcode all plugs to `Air`:

   ```
   s:Ge/ChamberPlugCentre/Material="Air"
   s:Ge/ChamberPlugTop/Material="Air"
   s:Ge/ChamberPlugBottom/Material="Air"
   s:Ge/ChamberPlugLeft/Material="Air"
   s:Ge/ChamberPlugRight/Material="Air"
   ```

2. **Add `ParallelWorldName` to each plug** — each plug must be assigned to its own named parallel world so that the Layered Mass Geometry can track which world each scorer belongs to:

   ```
   s:Ge/ChamberPlugCentre/ParallelWorldName="ChamberPlugCentre"
   s:Ge/ChamberPlugTop/ParallelWorldName="ChamberPlugTop"
   s:Ge/ChamberPlugBottom/ParallelWorldName="ChamberPlugBottom"
   s:Ge/ChamberPlugLeft/ParallelWorldName="ChamberPlugLeft"
   s:Ge/ChamberPlugRight/ParallelWorldName="ChamberPlugRight"
   ```

3. **Replace the 3 single-position scorers with 15 position-specific scorers** — use Jinja2 `{% for %}` loop to generate 3 scorers per position:

   ```jinja2
   {% for position in plug_positions %}
   s:Sc/{{ position }}_tle/Quantity="TrackLengthEstimator"
   s:Sc/{{ position }}_tle/InputFile="Muen.dat"
   s:Sc/{{ position }}_tle/Component="{{ position }}"
   s:Sc/{{ position }}_tle/IfOutputFileAlreadyExists="Overwrite"
   i:Sc/{{ position }}_tle/ZBins={{ tle_zbins }}
   s:Sc/{{ position }}_tle/OutputFile="{{ position }}_tle"

   s:Sc/{{ position }}_dtm/Quantity="DoseToMaterial"
   s:Sc/{{ position }}_dtm/Component="{{ position }}"
   s:Sc/{{ position }}_dtm/IfOutputFileAlreadyExists="Overwrite"
   i:Sc/{{ position }}_dtm/ZBins={{ dose_to_medium_zbins }}
   s:Sc/{{ position }}_dtm/Material="Air"
   b:Sc/{{ position }}_dtm/PreCalculateStoppingPowerRatios="True"
   s:Sc/{{ position }}_dtm/OutputFile="{{ position }}_dtm"

   s:Sc/{{ position }}_dtw/Quantity="DoseToWater"
   s:Sc/{{ position }}_dtw/Component="{{ position }}"
   s:Sc/{{ position }}_dtw/IfOutputFileAlreadyExists="Overwrite"
   b:Sc/{{ position }}_dtw/PreCalculateStoppingPowerRatios="True"
   i:Sc/{{ position }}_dtw/ZBins={{ dose_to_water_zbins }}
   s:Sc/{{ position }}_dtw/OutputFile="{{ position }}_dtw"
   {% endfor %}
   ```

4. **Remove template variables** that are no longer needed:
   - `plug_material_centre`, `plug_material_top`, `plug_material_bottom`, `plug_material_left`, `plug_material_right`
   - `plug_position` (single position)

5. **Add template variable** `plug_positions` — a list of all 5 position names passed from the context.

#### File: `src/boilerplates/TOPAS_includeFiles/CTDIphantom_32.j2`

Apply identical changes as `CTDIphantom_16.j2` above. The only differences between the two templates are the phantom radius (`RMax`) and peripheral plug offsets (`TransX`/`TransY`), which remain unchanged.

#### File: `src/boilerplates/headsourcecode_boilerplate.j2`

**No changes required.** Line 12 already contains:

```
sv:Ph/Default/LayeredMassGeometryWorlds = 5 "ChamberPlugCentre" "ChamberPlugTop" "ChamberPlugBottom" "ChamberPlugLeft" "ChamberPlugRight"
```

This is already correctly configured for the parallel worlds approach.

---

### 2.2 CTDI Mode Changes

#### File: `src/modes/ctdi_mode.py`

**Current behaviour:**
- `build_sub_context()` creates per-position context with one Air plug and four PMMA plugs
- `_generate_plug_files()` loops over 5 positions, renders the template 5 times, writes 5 parameter files, and returns 5 commands
- `execute()` calls `SimulationRunner.run_ctdi()` with the 5 commands

**Proposed changes:**

1. **Simplify `build_sub_context()`** — remove the `plug_position` parameter and the `plug_material_*` logic. Instead, pass a `plug_positions` list:

   ```python
   def build_sub_context(self, config: SimulationConfig) -> Dict[str, object]:
       return {
           "couch_enabled": config.ctdi.couch_enabled,
           "couch_width": config.ctdi.couch_width,
           "couch_thickness": config.ctdi.couch_thickness,
           "couch_length": config.ctdi.couch_length,
           "plug_positions": list(_PLUG_POSITIONS),
           "dose_to_medium_zbins": config.ctdi.dose_to_medium_zbins,
           "tle_zbins": config.ctdi.tle_zbins,
           "dose_to_water_zbins": config.ctdi.dose_to_water_zbins,
       }
   ```

2. **Replace `_generate_plug_files()` with `_generate_single_parameter_file()`** — render the phantom template once (with all 5 positions), combine with the head source code, and write a single file:

   ```python
   def _generate_single_parameter_file(
       self,
       config: SimulationConfig,
       rundatadir: str,
       project_root: str,
   ) -> str:
       """Generate a single TOPAS parameter file scoring all 5 plug positions."""
       renderer = TemplateRenderer(
           os.path.join(project_root, "src", "boilerplates"),
           os.path.join(project_root, "tmp"),
       )
       sub_template = self.get_sub_template_name(config)
       headsource_path = os.path.join(project_root, "tmp", "headsourcecode.txt")
       with open(headsource_path, "r") as f:
           headsource_content = f.read()
       sub_context = self.build_sub_context(config)
       phantom_rendered = renderer.render_string(
           "{% include '" + sub_template + "' %}",
           sub_context,
       )
       combined = headsource_content + phantom_rendered
       output_file = os.path.join(rundatadir, "CTDI_all_positions.txt")
       with open(output_file, "w") as f:
           f.write(combined)
       return output_file
   ```

3. **Update `execute()`** — call the single-file generator and use `SimulationRunner.run_dicom()`-style single execution:

   ```python
   def execute(
       self,
       config: SimulationConfig,
       rundir: str,
       project_root: str,
   ) -> None:
       param_file = self._generate_single_parameter_file(config, rundir, project_root)
       log_path = os.path.join(rundir, "topas_ctdi.log")
       command = [config.general.topas_directory, param_file]
       SimulationRunner.run_topas(command, rundir, log_path)
   ```

4. **Update `build_main_context()`** — no changes needed; it already provides the correct context for the main template.

---

### 2.3 Simulation Runner Changes

#### File: `src/simulation_runner.py`

**Current behaviour:**
- `run_ctdi()` uses `multiprocessing.Pool` to run 5 TOPAS processes in parallel
- `run_dicom()` runs a single TOPAS process with log capture

**Proposed changes:**

1. **Remove `run_ctdi()` method** — it is no longer needed since CTDI now runs a single process.

2. **Remove `multiprocessing` import** — `import multiprocessing as mp` on line 8 is no longer needed.

3. **Keep `run_topas()` and `run_dicom()` unchanged** — `run_topas()` is the core execution method and will be called directly from `CtdiMode.execute()`.

4. **Update `validate_topas_binary()`** — no changes needed; it will still be called (either directly or via `run_dicom()` if we route through that method).

**Alternative approach (minimal change):** Instead of removing `run_ctdi()`, refactor it to call `run_topas()` with a single command, similar to `run_dicom()`. This preserves the method name for backward compatibility but removes multiprocessing:

```python
@staticmethod
def run_ctdi(topas_path: str, rundatadir: str, param_file: str) -> None:
    """Run a single CTDI simulation scoring all plug positions."""
    SimulationRunner.validate_topas_binary(topas_path)
    command = [topas_path, param_file]
    log_path = os.path.join(rundatadir, "topas_ctdi.log")
    logger.info("Starting CTDI simulation (parallel worlds)")
    SimulationRunner.run_topas(command, rundatadir, log_path)
```

**Recommendation:** Use the alternative approach to minimize the diff and preserve the `run_ctdi()` method signature concept, but simplify it to single-process execution.

---

### 2.4 Orchestrator Changes

#### File: `src/orchestrator.py`

**Current behaviour:**
- `run_with_runfolder()` calls `mode.build_sub_context(config)` without a `plug_position` argument (line 59), which defaults to `""`
- This renders the sub-template once into `tmp/` but the result is not directly used by CTDI mode (which re-renders in `_generate_plug_files()`)

**Proposed changes:**

1. **Update the `build_sub_context()` call** — remove the positional argument since `build_sub_context()` no longer takes `plug_position`:

   ```python
   sub_context = mode.build_sub_context(config)
   ```

   This is actually already the current call signature (no `plug_position` passed), so **no change needed** in the orchestrator if we make `plug_position` optional with a default in the base class.

2. **Consider whether the sub-template render in the orchestrator is still needed** — currently the orchestrator renders the sub-template to `tmp/CTDIphantom_16.txt`, but `CtdiMode._generate_plug_files()` re-renders it anyway. With the parallel worlds approach, the orchestrator's sub-template render becomes the canonical render. We could either:
   - Keep the current flow where the orchestrator renders to `tmp/` and CTDI mode re-renders (wasteful but minimal change)
   - Refactor so the orchestrator render is used directly (cleaner but larger change)

   **Recommendation:** Keep the current flow for now. The orchestrator render to `tmp/` can serve as a debug artifact, and the CTDI mode re-render ensures the correct context is used.

---

### 2.5 Base Mode Interface Changes

#### File: `src/modes/base.py`

**Current behaviour:**
- `build_sub_context()` has signature `(self, config: SimulationConfig, plug_position: str = "") -> Dict[str, object]`

**Proposed changes:**

1. **Update the `build_sub_context()` signature** — remove the `plug_position` parameter since it is no longer needed:

   ```python
   @abstractmethod
   def build_sub_context(self, config: SimulationConfig) -> Dict[str, object]:
       """Build the template context dict for the sub-include file."""
       ...
   ```

2. **Update `DicomMode.build_sub_context()`** accordingly (it currently accepts but ignores `plug_position`).

---

### 2.6 Post-Processing Impact

#### File: `src/services/ctdi_calculator.py`

**Current behaviour:**
- `_find_chamber_files()` looks for files named `ChamberPlug{Position}_{type}.csv` (e.g., `ChamberPlugCentre_dtm.csv`, `ChamberPlugTop_tle.csv`)
- The naming pattern is: `{plug_position}_{scorer_type}.csv`

**Proposed changes:**

1. **Verify output file naming** — the new template uses `OutputFile="{{ position }}_tle"` etc., which produces files like `ChamberPlugCentre_tle.csv`, `ChamberPlugTop_dtm.csv`. This matches the existing naming convention exactly.

2. **No changes needed** in `ctdi_calculator.py` — the output file naming is preserved.

**Verification checklist:**
- [ ] `ChamberPlugCentre_tle.csv` — produced by scorer `Sc/ChamberPlugCentre_tle`
- [ ] `ChamberPlugCentre_dtm.csv` — produced by scorer `Sc/ChamberPlugCentre_dtm`
- [ ] `ChamberPlugCentre_dtw.csv` — produced by scorer `Sc/ChamberPlugCentre_dtw`
- [ ] Same pattern for Top, Bottom, Left, Right
- [ ] Total: 15 CSV output files

---

## 3. Test Updates

### 3.1 Unit Tests: `tests/unit/test_ctdi_mode.py`

**Changes required:**

1. **`TestBuildSubContext`** — update all tests to remove `plug_position` argument:
   - `test_couch_enabled_in_context` — remove `plug_position="ChamberPlugCentre"`
   - `test_couch_dimensions_in_context` — remove `plug_position="ChamberPlugCentre"`
   - `test_zbins_in_context` — remove `plug_position="ChamberPlugCentre"`
   - `test_active_plug_has_air_material` — **remove entirely** (no longer relevant; all plugs are always Air)
   - `test_plug_position_in_context` — **replace** with test that `plug_positions` list contains all 5 positions

2. **`TestExecute`** — update to reflect single-file execution:
   - Mock `_generate_single_parameter_file` instead of `_generate_plug_files`
   - Mock `SimulationRunner.run_topas` instead of `SimulationRunner.run_ctdi`

3. **`TestGeneratePlugFiles` → `TestGenerateSingleParameterFile`**:
   - Rename class
   - Test that exactly 1 file is generated (not 5)
   - Test that the file contains all 5 position names
   - Test that the file contains 15 scorer definitions

### 3.2 Unit Tests: `tests/unit/test_simulation_runner.py`

**Changes required:**

1. **`TestRunCtdi`** — update to reflect single-process execution:
   - Remove `mp.Pool` mocking
   - Test that `run_topas` is called once with the correct command and log path
   - Or remove `TestRunCtdi` entirely if `run_ctdi()` is removed

2. **Remove multiprocessing-related assertions** — no more `mock_pool.starmap` calls.

### 3.3 Unit Tests: `tests/unit/test_base_mode.py`

**Changes required:**

1. Update `build_sub_context` tests to remove `plug_position` parameter.

### 3.4 New Tests: Parallel Worlds Template Rendering

**Add new test file:** `tests/unit/test_parallel_worlds_template.py`

Tests to add:
- Render `CTDIphantom_16.j2` with `plug_positions` list and verify all 5 plugs have `Material="Air"`
- Verify all 5 plugs have `ParallelWorldName` set
- Verify exactly 15 scorer definitions are present (3 per position × 5 positions)
- Verify output file names match expected pattern (`ChamberPlugCentre_tle`, etc.)
- Verify no `PMMA` material assignments for any plug
- Same tests for `CTDIphantom_32.j2`

---

## 4. Risk Assessment

### 4.1 Statistical Equivalence

| Concern | Assessment |
|---------|-----------|
| **Same total histories?** | Currently: 5 × N histories (N per process). Proposed: N histories shared across all 5 scorers. **Each scorer gets fewer effective histories** (same N total, but split across 5 scoring volumes). This may increase statistical uncertainty per position. |
| **Mitigation** | Increase `histories` by 5× to maintain equivalent statistics per position. Alternatively, validate that the statistical uncertainty is acceptable with the current history count. |
| **Random seed** | Currently: each of the 5 processes uses the same seed (from config), producing independent but reproducible results. Proposed: single seed, single simulation. Results will differ numerically but should be statistically equivalent given enough histories. |

**Recommendation:** Run a validation study comparing the 5-process vs. 1-process results with identical total histories to verify statistical equivalence before merging.

### 4.2 Output File Format Compatibility

| Concern | Assessment |
|---------|-----------|
| **File naming** | ✅ Preserved — scorer names like `ChamberPlugCentre_tle` produce `ChamberPlugCentre_tle.csv` |
| **File content format** | ✅ Should be identical — TOPAS CSV format is determined by scorer type, not by parallel worlds |
| **Number of output files** | ⚠️ Changes from 15 files across 5 directories to 15 files in 1 directory. Since all files were already in the same `rundatadir`, this is actually unchanged. |

### 4.3 Performance Impact

| Concern | Assessment |
|---------|-----------|
| **Wall-clock time** | Currently: ~T (time for one simulation, since 5 run in parallel). Proposed: ~T to ~1.5T (single simulation with more scoring overhead). May be slightly slower due to 15 scorers vs 3, but avoids multiprocessing overhead. |
| **Memory** | Single TOPAS process uses less total memory than 5 concurrent processes. |
| **CPU utilization** | Currently: uses up to 5 CPU cores. Proposed: single process uses `threads` cores (configurable). For multi-threaded TOPAS, this may be comparable. |

### 4.4 Backward Compatibility

| Concern | Assessment |
|---------|-----------|
| **Existing run folders** | ⚠️ Old run folders with 5 separate log files (`topas_ChamberPlugCentre.log`, etc.) will differ from new format (single `topas_ctdi.log`). Post-processing code is unaffected. |
| **Configuration** | ✅ No changes to `SimulationConfig` or YAML format. |
| **GUI** | ✅ No changes to GUI layout or behavior. |
| **CLI** | ✅ No changes to CLI commands or options. |

### 4.5 TOPAS Version Compatibility

| Concern | Assessment |
|---------|-----------|
| **Parallel Worlds support** | The codebase already uses `isParallel="True"` and `LayeredMassGeometryWorlds`, indicating the TOPAS version in use supports parallel worlds. |
| **Multiple scorers per component** | Standard TOPAS feature; no version concerns. |
| **ParallelWorldName parameter** | Needs verification — confirm that the TOPAS version supports explicit `ParallelWorldName` assignment. If not, the parallel world name may be derived from the component name automatically. |

---

## 5. Implementation Order

### Phase 1: Template Refactor (Low Risk)
1. Create new template context variable `plug_positions`
2. Update `CTDIphantom_16.j2` to use Jinja2 loop for scorers
3. Update `CTDIphantom_32.j2` similarly
4. Set all plug materials to Air
5. Add `ParallelWorldName` to each plug (if required by TOPAS version)
6. Write template rendering tests

### Phase 2: Mode Refactor (Medium Risk)
1. Update `CtdiMode.build_sub_context()` to remove `plug_position` parameter
2. Replace `_generate_plug_files()` with `_generate_single_parameter_file()`
3. Update `CtdiMode.execute()` for single-process execution
4. Update `SimulationMode.build_sub_context()` in base class
5. Update `DicomMode.build_sub_context()` accordingly
6. Write unit tests for new mode behavior

### Phase 3: Runner Simplification (Low Risk)
1. Simplify or remove `SimulationRunner.run_ctdi()`
2. Remove `multiprocessing` import
3. Update runner tests

### Phase 4: Validation (Critical)
1. Run both old (5-process) and new (1-process) simulations with identical parameters
2. Compare output CSV files for statistical equivalence
3. Verify CTDI-w calculations produce consistent results
4. Document any statistical differences

### Phase 5: Cleanup
1. Remove dead code (old `_generate_plug_files`, multiprocessing logic)
2. Update documentation
3. Final lint/type-check/test pass

---

## 6. Files Changed Summary

| File | Change Type | Description |
|------|------------|-------------|
| `src/boilerplates/TOPAS_includeFiles/CTDIphantom_16.j2` | Modify | All plugs Air, 15 scorers via Jinja2 loop, add ParallelWorldName |
| `src/boilerplates/TOPAS_includeFiles/CTDIphantom_32.j2` | Modify | Same changes as 16cm template |
| `src/modes/ctdi_mode.py` | Modify | Remove 5-file loop, single file generation, simplify context |
| `src/modes/base.py` | Modify | Remove `plug_position` from `build_sub_context()` signature |
| `src/modes/dicom_mode.py` | Modify | Update `build_sub_context()` signature |
| `src/simulation_runner.py` | Modify | Simplify/remove `run_ctdi()`, remove multiprocessing |
| `tests/unit/test_ctdi_mode.py` | Modify | Update for single-file generation |
| `tests/unit/test_simulation_runner.py` | Modify | Remove multiprocessing tests |
| `tests/unit/test_base_mode.py` | Modify | Update `build_sub_context` tests |
| `tests/unit/test_parallel_worlds_template.py` | New | Template rendering tests for parallel worlds |

---

## 7. Open Questions

1. **Is `ParallelWorldName` required?** The current templates use `isParallel="True"` but do not set `ParallelWorldName`. TOPAS may auto-assign parallel world names from the component name. Need to verify whether explicit `ParallelWorldName` is needed or if the current approach (component name = parallel world name) is sufficient.

2. **History count adjustment?** Should the history count be automatically multiplied by 5 to maintain per-position statistical equivalence, or should this be left to the user to configure?

3. **TOPAS thread count?** With a single simulation using all available threads, should the default thread count be increased to match the previous effective parallelism (5 × threads)?

4. **Validation dataset?** Is there an existing reference dataset that can be used to validate the statistical equivalence of the parallel worlds approach?
