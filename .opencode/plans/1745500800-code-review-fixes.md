# Code Review Fixes Plan

**Date:** 2026-04-24
**Status:** Pending
**Depends on:** `a9c1755` (Phases 3-8 OOP refactoring, already committed)

## Summary

Fix 7 issues identified in the post-refactoring code review. Ordered by priority and
grouped into two commits: high-priority bug/design fixes, then medium/low cleanups.

---

## Fix 1: Deduplicate `_copy_common_files` (HIGH)

**Problem:** `DicomMode._copy_common_files` (lines 80-101) and
`CtdiMode._copy_common_files` (lines 92-112) are character-for-character identical.

**Solution:** Move the method to `SimulationMode` base class as a concrete `@staticmethod`.
Both subclasses already call `self._copy_common_files(...)`, so no call-site changes needed.
Remove the duplicated definitions from both subclasses.

**Files changed:**
- `src/modes/base.py` — add `copy_common_files` static method (rename from `_copy_common_files`
  to public since it's now on the base class; alternatively keep `_` prefix as a protected
  convention)
- `src/modes/dicom_mode.py` — delete `_copy_common_files` (lines 80-101)
- `src/modes/ctdi_mode.py` — delete `_copy_common_files` (lines 92-112)
- `tests/unit/test_dicom_mode.py` — `TestPrepareRun` already mocks `shutil.copy` at the
  module level; no change needed since the method still calls `shutil.copy`
- `tests/unit/test_ctdi_mode.py` — same, no test change needed

**Detail for base.py:**
```python
import os
import shutil
from src.config import SimulationConfig

class SimulationMode(ABC):
    # ... existing abstract methods ...

    @staticmethod
    def copy_common_files(
        rundatadir: str, config: SimulationConfig, project_root: str
    ) -> None:
        include_dir = os.path.join(
            project_root, "src", "boilerplates", "TOPAS_includeFiles"
        )
        shutil.copy(os.path.join(include_dir, "Muen.dat"), rundatadir)
        shutil.copy(os.path.join(include_dir, "NbParticlesInTime.txt"), rundatadir)
        shutil.copy(
            os.path.join(project_root, "tmp", "ConvertedTopasFile.txt"),
            rundatadir,
        )
        shutil.copy(
            os.path.join(project_root, "tmp", "head_calibration_factor.txt"),
            rundatadir,
        )
        fan_mode = config.imaging.fan_mode
        if fan_mode == "Full Fan":
            shutil.copy(os.path.join(include_dir, "fullfan.txt"), rundatadir)
        elif fan_mode == "Half Fan":
            shutil.copy(os.path.join(include_dir, "halffan.txt"), rundatadir)
```

**Detail for dicom_mode.py / ctdi_mode.py call sites:**
Change `self._copy_common_files(...)` to `self.copy_common_files(...)` in both
`DicomMode.prepare_run` and `CtdiMode.prepare_run`.

---

## Fix 2: `SimulationRunner.run_topas` should check return code (HIGH)

**Problem:** `subprocess.run(command, cwd=working_dir, shell=True)` never checks the
return code. A failed TOPAS run silently continues.

**Solution:** Capture the result and raise `RuntimeError` on non-zero exit code.

**Files changed:**
- `src/simulation_runner.py` — change `run_topas` body
- `tests/unit/test_simulation_runner.py` — update existing test, add failure test

**Detail for simulation_runner.py:**
```python
@staticmethod
def run_topas(command: str, working_dir: str) -> None:
    logger.info("Running TOPAS: %s in %s", command, working_dir)
    result = subprocess.run(command, cwd=working_dir, shell=True)
    if result.returncode != 0:
        logger.error(
            "TOPAS exited with code %d: %s", result.returncode, command
        )
        raise RuntimeError(
            "TOPAS process failed with return code {}".format(result.returncode)
        )
```

**Detail for test_simulation_runner.py:**
- Existing `test_calls_subprocess_run_with_correct_args`: set `mock_run.return_value.returncode = 0`
  so it doesn't raise
- Add `test_raises_on_nonzero_return_code`: set `mock_run.return_value.returncode = 1`,
  assert `pytest.raises(RuntimeError)`
- Add `test_logs_error_on_failure`: check logger output on non-zero exit

---

## Fix 3: Read `headsourcecode.txt` once outside loop in `CtdiMode` (MEDIUM)

**Problem:** `_generate_plug_files` reads `headsourcecode.txt` on every loop iteration
(5 times). The content is identical for all positions.

**Solution:** Read it once before the loop and reuse the content.

**Files changed:**
- `src/modes/ctdi_mode.py` — move `open(headsourcecode.txt)` to before the `for` loop

**Detail:**
```python
# Before the loop, after reading phantom_content:
with open(
    os.path.join(project_root, "tmp", "headsourcecode.txt"), "r"
) as f:
    headsource_content = f.read()

commands: List[Tuple[str, str]] = []
for position in _PLUG_POSITIONS:
    combined = headsource_content + phantom_content
    # ... rest unchanged ...
```

No test changes needed — existing test mocks `_generate_plug_files` entirely, and the
function's output is unchanged.

---

## Fix 4: Replace `print()` with `logging` in `fieldtobladeopening.py` (MEDIUM)

**Problem:** `__main__` block uses `print()`, violating project convention.

**Solution:** Replace with `logging.info()`. Add `logging.basicConfig()` in the
`__main__` block.

**Files changed:**
- `src/fieldtobladeopening.py` — lines 46-48

**Detail:**
```python
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info(fieldtobladeopening(["2 cm", "2 cm", "16 cm", "16 cm"]))
    logger.info(fieldtobladeopening(["10 cm", "10 cm", "10 cm", "10 cm"]))
```

Note: `test_fieldtobladeopening_script_execution` calls `runpy.run_path(module_path,
run_name="__main__")`. This test should still pass since `logging.basicConfig` is
idempotent when called multiple times.

---

## Fix 5: Guard against `None` from checkbox in controller (MEDIUM)

**Problem:** FreeSimpleGUI checkboxes can return `None` in edge cases.
`values[COUCH_ENABLED]` and `values[CTDI_USER_BLADE]` are passed directly to
`set_couch_visible(visible: bool)` and `set_blade_visible(visible: bool)`.

**Solution:** Wrap with `bool()` in the handlers.

**Files changed:**
- `src/gui/controller.py` — lines 138-142

**Detail:**
```python
def _on_couch_toggle(self, values: Dict[str, Any]) -> None:
    self.view.set_couch_visible(bool(values[COUCH_ENABLED]))

def _on_user_blade_toggle(self, values: Dict[str, Any]) -> None:
    self.view.set_blade_visible(bool(values[CTDI_USER_BLADE]))
```

No test changes needed — no existing tests for controller handlers.

---

## Fix 6: `Quantity.__str__` format cleanup (LOW)

**Problem:** `Quantity(100.0, "kV").__str__()` produces `"100.0 kV"` instead of
`"100 kV"`. The original strings in config use integer representation (`"100 kV"`).

**Solution:** Use `format(self.value, "g")` to strip unnecessary trailing zeros.

**Files changed:**
- `src/models/quantity.py` — line 27
- `tests/unit/test_quantity.py` — update `test_str_roundtrip` expected value

**Detail for quantity.py:**
```python
def __str__(self) -> str:
    return "{} {}".format(format(self.value, "g"), self.unit)
```

**Detail for test_quantity.py:**
```python
def test_str_roundtrip(self) -> None:
    q: Quantity = Quantity(100.0, "kV")
    assert str(q) == "100 kV"  # was "100.0 kV"
```

**Backward compat risk:** The `test_matches_old_quantity_unit_stripper` test compares
tuples `(value, unit)`, not strings, so it's unaffected. The `to_dict()` method in
`config.py` uses `str(value)` which calls `__str__` — this is the intended improvement.

Add additional test cases:
```python
def test_str_strips_trailing_zeros(self) -> None:
    assert str(Quantity(100.0, "kV")) == "100 kV"
    assert str(Quantity(0.4, "deg/s")) == "0.4 deg/s"
    assert str(Quantity(5.0, "mm")) == "5 mm"
```

---

## Fix 7: Redundant double-parse in `fieldtobladeopening` (LOW)

**Problem:** Lines 18-31 manually iterate tokens to check `found_number`, then line 32
calls `Quantity.parse(field_str)` which iterates tokens again.

**Solution:** Use `Quantity.parse()` directly and check `parsed.value == 0.0` as the
sentinel. If the input had no number, `Quantity.parse` returns `value=0.0`. The only
ambiguous case is `"0 cm"` which is valid and should not raise. Handle this by checking
if `"0"` or `"0."` or a float-parseable token exists in the input before the Quantity call.

Actually, the simpler approach: keep the manual check since it distinguishes `"0 cm"`
(valid, `found_number=True`) from `"cm"` (invalid, `found_number=False`). Just remove
the redundant `Quantity.parse` call and use the manual parsing result directly.

**Files changed:**
- `src/fieldtobladeopening.py` — lines 17-41

**Detail:**
```python
blade_position_list: List[str] = []
for count, field_str in enumerate(field_size_list):
    parsed = Quantity.parse(field_str)
    if parsed.value == 0.0 and not any(
        _is_numeric(t) for t in field_str.split()
    ):
        raise TypeError(
            "Field size must contain a numeric value, e.g. '14 cm'. Got: "
            + repr(field_str)
        )
    ...
```

**Risk:** This is a behavior change for edge cases. The current implementation is proven
correct by existing tests. **Recommendation: SKIP this fix** — the double-parse is a
minor performance concern (4 iterations over 2-token strings) and the existing code is
well-tested. Not worth the risk.

---

## Execution Order

1. Fix 1 (deduplicate `_copy_common_files`) — high impact, zero risk
2. Fix 2 (return code check) — high impact, adds safety
3. Fix 3 (read headsourcecode once) — medium, performance
4. Fix 4 (print -> logging) — medium, style
5. Fix 5 (None guard) — medium, safety
6. Fix 6 (Quantity format) — low, cosmetic improvement
7. Fix 7 — SKIP (see above)

**Commit strategy:** Two commits:
1. `fix(modes): deduplicate copy_common_files and check TOPAS return code` (Fixes 1, 2)
2. `fix(core): minor cleanups — file I/O, logging, None guard, Quantity format` (Fixes 3-6)

**Verification after each commit:** `uv run pytest tests/ -v && uv run ruff check src/ tests/`

---

## Test Impact Summary

| Fix | New tests needed | Existing tests affected |
|-----|-----------------|------------------------|
| 1   | 0               | 0 (mock level unchanged) |
| 2   | 2 (failure cases) | 3 (need `returncode=0` on mocks) |
| 3   | 0               | 0 (function output unchanged) |
| 4   | 0               | 1 (`test_fieldtobladeopening_script_execution` — should still pass) |
| 5   | 0               | 0 (no controller tests exist) |
| 6   | 1 (format test) | 1 (`test_str_roundtrip` assertion change) |
