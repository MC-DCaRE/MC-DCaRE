# OOP Refactoring Plan — MC-DCaRE

**Created:** 2026-04-24  
**Scope:** Full refactor — Strategy pattern, Quantity value object, pathlib, MVC/MVP GUI, CTDI calculator class

## Problem Statement

The MC-DCaRE codebase has accumulated significant technical debt:

1. **Repeated `if DICOM / elif CTDI` branching** across `orchestrator.py`, `parameter_editor.py`, `run_simulation.py`, and `topas_gui.py` — adding a new simulation type requires editing all four files.
2. **Stringly-typed config** — every value is a raw string like `"100 kV"`, forcing ad-hoc parsing at every call site.
3. **80% code duplication** in `Orchestrator.run_dicom_simulation`, `run_ctdi_simulation`, and `prepare_only`.
4. **Encapsulation violations** — `Orchestrator` calls `RunPreparer._generate_plug_files()` (private method).
5. **Dual `BoilerplateManager` instances** — both `Orchestrator` and `RunPreparer` create their own.
6. **235-line procedural GUI** with no separation of concerns.
7. **Positional list indexing** in imaging mode lookup tables.
8. **Mixed path construction** — string concatenation alongside `os.path.join`.
9. **No logging** — `print()` and bare `except Exception` throughout.

## Proposed Target Architecture

```
src/
  models/                      # Value objects and data structures
    quantity.py                # Quantity value object (value + unit)
    imaging_mode.py            # ImagingMode dataclass (replaces positional lists)
    simulation_config.py       # Typed config dataclasses (Quantity fields, Path fields)
    enums.py                   # SimulationType, FanMode, RotationDirection enums

  modes/                       # Strategy pattern for simulation types
    base.py                    # Abstract SimulationMode
    dicom_mode.py              # DICOM-specific logic
    ctdi_mode.py               # CTDI-specific logic

  services/                    # Stateful service objects
    boilerplate_manager.py     # Path-aware boilerplate file management (pathlib)
    parameter_editor.py        # TOPAS parameter file editing (delegates to mode)
    spectrum_generator.py      # X-ray spectrum generation (stateful service)
    run_preparer.py            # Run folder creation and file staging
    simulation_runner.py       # TOPAS process execution with error handling

  orchestrator.py              # Slim pipeline coordinator (delegates to mode)
  gui/                         # MVC/MVP GUI layer
    view.py                    # Layout definition + widget accessor methods
    controller.py              # Event handling + business logic dispatch
  fieldtobladeopening.py       # Pure function (unchanged, uses Quantity)

topas_gui.py                   # Entry point — creates View + Controller, runs loop
run_simulation.py              # CLI entry point (unchanged API)
calculate_ctdiw.py             # CTDI calculator class + CLI
```

---

## Phase 1: Foundation — Value Objects & Utilities

**Goal:** Introduce shared primitives that all subsequent phases depend on. No behavioral changes.

### 1.1 Create `Quantity` value object

**File:** `src/models/quantity.py`

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple

@dataclass(frozen=True)
class Quantity:
    value: float
    unit: str

    @classmethod
    def parse(cls, string_value: str) -> "Quantity":
        """Parse '100 kV' -> Quantity(100.0, 'kV')."""
        value = 0.0
        unit = ""
        for token in string_value.split():
            try:
                value = float(token)
            except ValueError:
                unit = token
        return cls(value, unit)

    def __str__(self) -> str:
        return f"{self.value} {self.unit}"
```

- Replaces `quantity_unit_stripper()` in `config.py` and inline parsing in `fieldtobladeopening.py`.
- Frozen dataclass — immutable, hashable, usable as dict key.
- Maintains backward compatibility via `__str__` which outputs `"100.0 kV"`.

### 1.2 Create `enums.py`

**File:** `src/models/enums.py`

```python
from enum import Enum

class SimulationType(str, Enum):
    DICOM = "DICOM"
    CTDI = "CTDI validation"

class FanMode(str, Enum):
    FULL = "Full Fan"
    HALF = "Half Fan"

class RotationDirection(str, Enum):
    CW = "CBCT Clockwise"
    CCW = "CBCT Anticlockwise"
    KV_KV = "kV-kV"
```

- `str, Enum` means `"DICOM" == SimulationType.DICOM` works — backward compatible with YAML strings.

### 1.3 Create `ImagingMode` dataclass

**File:** `src/models/imaging_mode.py`

Replace the positional list in `imaging_modes_lookuptable.py`:

```python
from dataclasses import dataclass
from typing import Dict

@dataclass(frozen=True)
class ImagingMode:
    rotation_rate: str
    voltage: str
    exposure: str
    fan_mode: str
    timeline_end: str
    field_x1: str
    field_x2: str
    field_y1: str
    field_y2: str
    blade_x1: str
    blade_x2: str
    blade_y1: str
    blade_y2: str

IMAGING_MODES: Dict[str, ImagingMode] = { ... }
```

- Convert existing dict of lists to dict of `ImagingMode` instances.
- Lookup returns a named object instead of a 13-element tuple.
- The `"selection"` key becomes unnecessary.

### 1.4 Migrate to `pathlib.Path` throughout

**Files:** `boilerplate_manager.py`, `run_preparer.py`, `spectrum_generator.py`, `orchestrator.py`

- Replace `str` path parameters with `Path`.
- Replace `os.path.join(a, b)` and `a + "/tmp/..."` with `Path(a) / "tmp" / "..."`.
- Replace `os.makedirs(dir, exist_ok=True)` with `Path(dir).mkdir(parents=True, exist_ok=True)`.
- `BoilerplateManager` constructor takes `project_root: Path`.

### 1.5 Add structured logging

**Files:** All `src/` modules

- Replace `print("ran")` in `simulation_runner.py` with `logger.info(...)`.
- Add `logger = logging.getLogger(__name__)` to every module.
- Keep existing `logging.basicConfig` in entry points (`topas_gui.py`, `run_simulation.py`).

### 1.6 Consolidate number/unit parsing

- `fieldtobladeopening.py`: Replace inline parsing loop with `Quantity.parse(field).value` and `.unit`.
- `config.py`: Remove standalone `quantity_unit_stripper()`, replace with `Quantity.parse()`.

**Testing:** All existing tests must pass after Phase 1. Add unit tests for `Quantity.parse`, `ImagingMode`, and `SimulationType` enum.

---

## Phase 2: Strategy Pattern — Simulation Modes

**Goal:** Eliminate the `if DICOM / elif CTDI` branching via the Strategy pattern.

### 2.1 Abstract `SimulationMode` base class

**File:** `src/modes/base.py`

```python
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Tuple
from src.models.simulation_config import SimulationConfig
from src.services.boilerplate_manager import BoilerplateManager

class SimulationMode(ABC):
    @abstractmethod
    def edit_main_file(self, config: SimulationConfig, file_path: Path) -> None:
        """Apply mode-specific edits to headsourcecode.txt."""
        ...

    @abstractmethod
    def edit_sub_file(self, config: SimulationConfig, file_path: Path) -> None:
        """Apply mode-specific edits to the sub-file (patientDICOM or CTDI phantom)."""
        ...

    @abstractmethod
    def get_sub_file_name(self, config: SimulationConfig) -> str:
        """Return the sub-file name for this mode (e.g. 'patientDICOM.txt')."""
        ...

    @abstractmethod
    def compute_histories(self, config: SimulationConfig) -> str:
        """Compute the number of histories for spectrum generation."""
        ...

    @abstractmethod
    def prepare_run(self, config: SimulationConfig, rundir: Path, ...) -> None:
        """Mode-specific run folder preparation."""
        ...

    @abstractmethod
    def run(self, topas_path: str, rundir: Path, ...) -> None:
        """Execute the TOPAS simulation(s)."""
        ...
```

### 2.2 `DicomMode` implementation

**File:** `src/modes/dicom_mode.py`

- `edit_main_file` — blanks CTDI phantom includes, handles graphics.
- `edit_sub_file` — sets patient params, DICOM directory, isocenter, shifts, output filename.
- `get_sub_file_name` — returns `"patientDICOM.txt"`.
- `compute_histories` — returns `str(int(sequential_times) * int(histories))`.
- `prepare_run` — copies headsourcecode, HU table, common files, patientDICOM.
- `run` — runs single TOPAS command.

### 2.3 `CtdiMode` implementation

**File:** `src/modes/ctdi_mode.py`

- `edit_main_file` — blanks DICOM include, handles graphics, optionally recalculates blade positions via `fieldtobladeopening`, blanks wrong-size phantom.
- `edit_sub_file` — sets couch params, z-bins.
- `get_sub_file_name` — returns `"CTDIphantom_{size}.txt"`.
- `compute_histories` — returns `config.general.histories`.
- `prepare_run` — calls `_generate_plug_files` (moved here from `RunPreparer`).
- `run` — runs multiple TOPAS commands in parallel.

### 2.4 Refactor `Orchestrator`

**File:** `src/orchestrator.py`

```python
from src.modes.base import SimulationMode
from src.modes.dicom_mode import DicomMode
from src.modes.ctdi_mode import CtdiMode

class Orchestrator:
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.boilerplate_manager = BoilerplateManager(project_root)

    def _get_mode(self, config: SimulationConfig) -> SimulationMode:
        if config.imaging.simulation_type == SimulationType.DICOM:
            return DicomMode(self.project_root, self.boilerplate_manager)
        else:
            return CtdiMode(self.project_root, self.boilerplate_manager)

    def run(self, config: SimulationConfig, dry_run: bool = False) -> str:
        mode = self._get_mode(config)
        self.boilerplate_manager.reset_tmp()

        editor = ParameterEditor(config)
        editor.edit_main_file(mode, self.boilerplate_manager.get_headsource_path())
        sub_file = self.boilerplate_manager.get_tmp_path(mode.get_sub_file_name(config))
        editor.edit_sub_file(mode, sub_file)

        voltage = Quantity.parse(config.imaging.anode_voltage).value
        exposure = Quantity.parse(config.imaging.exposure).value
        histories = mode.compute_histories(config)
        SpectrumGenerator().generate(voltage, exposure, histories, self.project_root)

        rundir = mode.prepare_run(config, ...)
        if not dry_run:
            mode.run(config.general.topas_directory, rundir)
        return str(rundir)
```

- `run_dicom_simulation`, `run_ctdi_simulation`, and `prepare_only` collapse into a single `run()` method.
- No more private method access (`_generate_plug_files`).
- Single `BoilerplateManager` instance passed to modes.

### 2.5 Move `_generate_plug_files` into `CtdiMode`

- This private method belongs to CTDI-specific logic, not to the generic `RunPreparer`.
- `CtdiMode.prepare_run()` handles plug file generation internally.
- `RunPreparer` shrinks to common file-copying utilities only.

### 2.6 Refactor `run_simulation.py`

- Remove `if DICOM / elif CTDI` dispatch — just call `orchestrator.run(config)`.
- `dry_run` flag passed through directly.

**Testing:** Update `test_orchestrator.py` to mock `SimulationMode` instead of individual services. Add tests for `DicomMode` and `CtdiMode` in isolation.

---

## Phase 3: Config Refactoring

**Goal:** Type config fields properly, eliminate key-mapping duplication.

### 3.1 Type config fields with `Quantity`, `Path`, and enums

```python
@dataclass
class GeneralConfig:
    g4_data_directory: Path = Path("")
    topas_directory: Path = Path("")
    seed: int = 9
    threads: int = 1
    histories: int = 100000

@dataclass
class ImagingConfig:
    simulation_type: SimulationType = SimulationType.DICOM
    start_angle: Quantity = Quantity(0, "deg")
    anode_voltage: Quantity = Quantity(100, "kV")
    exposure: Quantity = Quantity(100, "mAs")
    fan_mode: FanMode = FanMode.FULL
    ...
```

**Backward compatibility concern:** YAML I/O and GUI `from_gui_values()` currently expect strings. Solutions:
- Add `__post_init__` or `__init__` overloads that accept strings and convert.
- YAML serialization converts `Quantity` to string via `str()`.
- `from_yaml` and `from_gui_values` remain string-in, convert to typed.

### 3.2 Auto-generate `to_dict()` mapping

Replace the 50-line manual mapping with a field-metadata approach:

```python
PLACEHOLDER_MAP = {
    ("general", "g4_data_directory"): "-G4_DATA_DIR-",
    ("general", "topas_directory"): "-TOPAS_DIR-",
    ...
}

def to_dict(self) -> Dict[str, str]:
    result = {}
    for (section, field_name), placeholder in PLACEHOLDER_MAP.items():
        value = getattr(getattr(self, section), field_name)
        result[placeholder] = str(value)
    return result
```

- Single source of truth for key mappings.
- Add a `from_dict()` inverse for `from_gui_values`.

### 3.3 Clean up `from_gui_values()` boolean parsing

Extract a helper:

```python
def _parse_bool(value: object) -> bool:
    return value is True or str(value) == "True"
```

Replace the three duplicated `is True or ... == "True"` patterns.

### 3.4 Consolidate GUI key strings

Define all placeholder keys as constants in a single module (e.g., `src/models/keys.py`). Both `config.py` and `guilayers.py` import from there.

**Testing:** Update `test_config.py` extensively — YAML round-trip, `from_gui_values`, `to_dict`, Quantity fields.

---

## Phase 4: Parameter Editor Refactoring

**Goal:** Make `ParameterEditor` mode-aware, eliminate the remaining branching.

### 4.1 Split into common edits + mode-specific edits

The `ParameterEditor` applies two kinds of edits:
1. **Common** (always applied): G4 data dir, seed, threads, histories, blades, fan mode.
2. **Mode-specific**: Delegated to `SimulationMode.edit_main_file()` / `edit_sub_file()`.

```python
class ParameterEditor:
    def __init__(self, config: SimulationConfig) -> None:
        self.config = config

    def edit_main_file(self, mode: SimulationMode, file_path: Path) -> None:
        lines = file_path.read_text().splitlines(keepends=True)
        self._apply_common_edits(lines)
        mode.edit_main_file(self.config, lines)
        file_path.write_text("".join(lines))

    def _apply_common_edits(self, lines: List[str]) -> None:
        """Edits shared by all simulation types."""
        s = self._replace_line
        cfg = self.config
        s("s:Ts/G4DataDirectory", lines, str(cfg.general.g4_data_directory))
        s("i:Ts/Seed", lines, str(cfg.general.seed))
        ...
```

### 4.2 Make `string_index_replacement` a private instance method

- Rename to `_replace_line`.
- Add a return value (`bool`) indicating whether a replacement was found.
- Log a warning if a replacement target is not found (currently silent).

### 4.3 Move mode-specific edit logic into `DicomMode` and `CtdiMode`

- `DicomMode.edit_main_file(lines)` — blanks CTDI includes, handles graphics.
- `CtdiMode.edit_main_file(lines)` — blanks DICOM include, handles user blades, phantom size.
- `DicomMode.edit_sub_file(lines)` — patient params, output filename.
- `CtdiMode.edit_sub_file(lines)` — couch params, z-bins.

**Testing:** Test each mode's edit logic independently with fixture files.

---

## Phase 5: Service Layer Cleanup

### 5.1 Consolidate `BoilerplateManager` — single instance

- `RunPreparer` receives `BoilerplateManager` via constructor injection instead of creating its own.
- `Orchestrator` creates one `BoilerplateManager` and passes it to everything.

```python
class RunPreparer:
    def __init__(self, project_root: Path, bm: BoilerplateManager) -> None:
        self.project_root = project_root
        self.boilerplate_manager = bm
```

### 5.2 Make `SpectrumGenerator` a stateful service

```python
class SpectrumGenerator:
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root

    def generate(self, voltage: float, exposure: float, histories: str) -> None:
        ...
```

- Holds `project_root` as state instead of passing it every call.
- Use `pathlib.Path` for file output.
- Constants (anode angle, dk, SID) become class-level or constructor parameters.

### 5.3 Make `SimulationRunner` a proper service

```python
class SimulationRunner:
    def __init__(self, max_workers: int = 5) -> None:
        self.max_workers = max_workers

    def run(self, commands: List[Tuple[str, Path]]) -> None:
        with mp.Pool(processes=min(self.max_workers, os.cpu_count() or 1)) as pool:
            pool.starmap(self._run_topas, commands)

    @staticmethod
    def _run_topas(command: str, working_dir: Path) -> None:
        result = subprocess.run(command, cwd=str(working_dir), shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error("TOPAS failed: %s", result.stderr)
            raise RuntimeError(f"TOPAS exited with code {result.returncode}")
        logger.info("TOPAS completed successfully")
```

- Fix: `run_dicom` no longer creates a Pool for a single task — just calls `_run_topas` directly.
- Add error handling and return code checking.
- Remove `print("ran")`.

**Testing:** Update mocks for new constructor signatures. Add tests for error handling in `SimulationRunner`.

---

## Phase 6: GUI MVC/MVP Refactoring

**Goal:** Separate the 235-line procedural event loop into View and Controller classes.

### 6.1 View class

**File:** `src/gui/view.py`

Encapsulates FreeSimpleGUI layout and provides typed widget access:

```python
class MainView:
    def __init__(self) -> None:
        self.window = sg.Window(
            title="MC-DCaRE",
            layout=self._build_layout(),
            finalize=True,
            auto_size_text=True,
            font=("", 15),
        )

    def _build_layout(self) -> List[List[Any]]:
        ...  # All current layout definitions move here

    def read(self) -> Tuple[str, Dict[str, Any]]:
        return self.window.read()

    def update_imaging_mode_fields(self, mode: ImagingMode) -> None:
        """Single method replaces 26 lines of repeated update calls."""
        self.window["-ROTATION_RATE-"].update(mode.rotation_rate)
        self.window["-TUBE_VOLTAGE-"].update(mode.voltage)
        ...

    def set_tab_visibility(self, sim_type: SimulationType) -> None:
        ...

    def show_error(self, message: str) -> None:
        sg.popup_error(message)

    def close(self) -> None:
        self.window.close()
```

- All layout definitions from `guilayers.py` and `topas_gui.py` consolidate here.
- Widget update logic that's currently 26 repetitive lines becomes a single loop.
- `guilayers.py` becomes `src/gui/layouts.py` or is absorbed into `view.py`.

### 6.2 Controller class

**File:** `src/gui/controller.py`

Encapsulates event handling logic:

```python
class GUIController:
    def __init__(self, view: MainView, orchestrator: Orchestrator) -> None:
        self.view = view
        self.orchestrator = orchestrator
        self._default_values: Dict[str, Any] = {}
        self._event_handlers = {
            "-RESET-": self._on_reset,
            "-SIM_TYPE-": self._on_sim_type_change,
            "-DICOM_DIR-": self._on_dicom_dir,
            "-DICOM_RP-": self._on_dicom_rp,
            "-DICOM_RUN-": self._on_dicom_run,
            "-CTDI_RUN-": self._on_ctdi_run,
            "-IMAGING_MODE-": self._on_imaging_mode_change,
            "-SCAN_TYPE-": self._on_imaging_mode_change,
            "-COUCH_ENABLED-": self._on_couch_toggle,
            "-CTDI_USER_BLADE-": self._on_user_blade_toggle,
        }

    def run(self) -> None:
        while True:
            event, values = self.view.read()
            if event == sg.WIN_CLOSED:
                break
            if not self._default_values:
                self._default_values = dict(values)
            handler = self._event_handlers.get(event)
            if handler:
                handler(values)

    def _on_reset(self, values: Dict) -> None: ...
    def _on_sim_type_change(self, values: Dict) -> None: ...
    def _on_dicom_dir(self, values: Dict) -> None: ...
    def _on_dicom_rp(self, values: Dict) -> None: ...
    def _on_dicom_run(self, values: Dict) -> None: ...
    def _on_ctdi_run(self, values: Dict) -> None: ...
    def _on_imaging_mode_change(self, values: Dict) -> None: ...
    def _on_couch_toggle(self, values: Dict) -> None: ...
    def _on_user_blade_toggle(self, values: Dict) -> None: ...
```

- Event dispatch via dict lookup instead of `if/elif` chain.
- Each handler is testable in isolation (mock `view` and `orchestrator`).
- `topas_gui.py` shrinks to ~10 lines:

```python
from src.gui.view import MainView
from src.gui.controller import GUIController
from src.orchestrator import Orchestrator

def main() -> None:
    view = MainView()
    orchestrator = Orchestrator(Path.cwd())
    controller = GUIController(view, orchestrator)
    controller.run()
    view.close()

if __name__ == "__main__":
    main()
```

### 6.3 Fix DICOM directory reading performance

- Read each DICOM file once, cache `Modality` and `PatientID`.
- Or use `pydicom.dcmread(path, stop_before_pixels=True)` for faster reads.

**Testing:** Test controller handlers with mocked view and orchestrator. Test view's `update_imaging_mode_fields` by verifying widget update calls.

---

## Phase 7: CTDI Calculator Class

**Goal:** Wrap `calculate_ctdiw.py` functions into a cohesive class.

### 7.1 `CTDICalculator` class

**File:** `src/services/ctdi_calculator.py` (new, in `src/`)

```python
class CTDICalculator:
    def __init__(self, runfolder: Path) -> None:
        self.runfolder = runfolder
        self.calibration_factor = self._extract_calibration_factor()

    def calculate(self) -> List[Dict]:
        chamber_files = self._find_chamber_files()
        results = []
        for file_type in FILE_TYPES:
            result = self._process_file_type(chamber_files[file_type], file_type)
            if result:
                results.append(result)
        return results

    def save_results(self, results: List[Dict], output_path: Path) -> None: ...
    def _extract_calibration_factor(self) -> float: ...
    def _find_chamber_files(self) -> Dict[str, Dict[str, Path]]: ...
    def _extract_dose_from_file(self, file_path: Path) -> Optional[float]: ...
    def _process_file_type(self, ...) -> Optional[Dict]: ...
    @staticmethod
    def calculate_ctdi_w(peripheral: List[float], center: float) -> float: ...
```

### 7.2 Keep CLI as thin wrapper

`calculate_ctdiw.py` becomes:

```python
app = typer.Typer()

@app.command()
def main(runfolder: str, output_file: Optional[str] = None) -> None:
    calculator = CTDICalculator(Path(runfolder))
    results = calculator.calculate()
    calculator.save_results(results, output_path)
```

**Testing:** Test `CTDICalculator` with fixture files.

---

## Phase 8: Test Updates & Validation

### 8.1 Update existing tests

- `test_config.py` — update for `Quantity` fields, `Path` types, new `from_gui_values` signature.
- `test_orchestrator.py` — mock `SimulationMode` instead of individual services.
- `test_parameter_editor.py` — test common edits + mode-specific edits separately.
- `test_run_preparer.py` — update for constructor injection of `BoilerplateManager`.
- `test_simulation_runner.py` — test error handling, remove pool-for-single-task assumption.
- `test_spectrum_generator.py` — update for instance method instead of static.
- `test_boilerplate_manager.py` — update for `Path` return types.
- `test_calculate_ctdiw.py` — test `CTDICalculator` class.
- `test_fieldtobladeopening.py` — update for `Quantity.parse`.

### 8.2 New test files

- `tests/unit/test_quantity.py` — `Quantity.parse`, `__str__`, edge cases.
- `tests/unit/test_enums.py` — enum values and string comparison.
- `tests/unit/test_imaging_mode.py` — `ImagingMode` dataclass, lookup dict.
- `tests/unit/test_dicom_mode.py` — DicomMode edit/prepare/run logic.
- `tests/unit/test_ctdi_mode.py` — CtdiMode edit/prepare/run logic.
- `tests/unit/test_gui_controller.py` — event handler tests with mocked dependencies.

### 8.3 Final validation

```bash
uv run ruff format src/
uv run ruff check src/
uv run mypy src/
uv run pytest tests/ -v
```

---

## Execution Order & Dependencies

```
Phase 1 (Foundation)  ──→  Phase 2 (Strategy)  ──→  Phase 4 (Parameter Editor)
                              │                          │
                              └──→ Phase 5 (Services) ←──┘
                                       │
Phase 3 (Config) ←── Phase 1           │
                                       ↓
                              Phase 6 (GUI MVC)
                                       │
Phase 7 (CTDI Calculator) ←── Phase 1  │
                                       ↓
                              Phase 8 (Test Updates)
```

- **Phase 1 must come first** — everything depends on `Quantity`, `Path`, and enums.
- **Phase 2 is next** — the Strategy pattern is the core architectural change.
- **Phase 3 can happen in parallel with Phase 2** but config fields referencing `Quantity` work better after both.
- **Phase 4 and 5** depend on Phase 2's mode abstractions.
- **Phase 6** depends on Phase 2 (orchestrator changes) and Phase 3 (config changes).
- **Phase 7** is standalone — can happen anytime after Phase 1.
- **Phase 8** is continuous — update tests as each phase lands.

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Python 3.8 compatibility | No walrus, no `match`, no `str.removeprefix`. `from __future__ import annotations` for forward refs. |
| FreeSimpleGUI coupling | View class isolates all FreeSimpleGUI imports. Controller is testable without a display. |
| YAML backward compatibility | `Quantity.__str__()` outputs `"100.0 kV"` — compatible with existing YAML files. Add converter for old format. |
| Wildcard import in `topas_gui.py` | Phase 6 removes `from src.guilayers import *` entirely. |
| Large PR size | Execute phase-by-phase with green tests between each. |
