# Plan: Update AGENTS.md

## Problem

The existing `AGENTS.md` is outdated. The codebase has been restructured into sub-packages (`src/gui/`, `src/models/`, `src/modes/`, `src/services/`), the GUI was refactored to MVC, and several claims no longer match the code (e.g., `topas_gui.py` no longer uses wildcard imports from `guilayers`). Historical rename notes ("was `edits_handler.py`") add noise. CLI subcommands are undocumented.

## Approach

Rewrite `AGENTS.md` in place, preserving verified useful guidance and removing stale/obvious content.

## Key Changes from Current File

1. **Trim architecture section** — Replace exhaustive file-by-file listing with a concise structural overview noting the four `src/` sub-packages (`gui/`, `models/`, `modes/`, `services/`) and the Strategy pattern for simulation modes. No need to list every file — agents can discover those.

2. **Fix GUI description** — `topas_gui.py` now uses MVC (`src/gui/controller.py` + `src/gui/view.py`). It no longer does `from src.guilayers import *`. `guilayers.py` still exists as a layout definition module used by `view.py`.

3. **Remove historical rename notes** — "was `edits_handler.py`", "was `Energyspectrum.py`", "replaces `defaultvalues.py`" are noise for future agents.

4. **Add CLI commands section** — Document the Typer subcommands: `run_simulation.py run`, `generate_config`, `validate`, `convert`; and `calculate_ctdiw.py`.

5. **Note `imaging_modes_lookuptable.py` is a backward-compat shim** — It just re-exports from `src.models.imaging_mode`.

6. **Note mypy/python version discrepancy** — `pyproject.toml` says `requires-python >= 3.8` but `[tool.mypy] python_version = "3.9"`. Both `black` and `ruff` target py38.

7. **Keep verified high-signal content** — `uv run` prefix rule, pytest config split (`pytest.ini` vs `pyproject.toml`), `sys.path.insert` test pattern, 3.8 compatibility constraints, TOPAS boilerplate workflow, `spekpy` mock requirement, `from __future__ import annotations` everywhere.

8. **Remove obvious/low-signal content** — The `tmp/` and `runfolder/` descriptions are obvious from filenames. The full file tree under `src/` is better discovered than listed.

## Proposed AGENTS.md Structure

```
# Agent Instructions

## Python Commands
## Project Overview
## Architecture (concise)
## CLI Commands
## Testing
## Lint & Format
## Key Quirks
```

## Files to Modify

| File | Action | Purpose |
|------|--------|---------|
| `AGENTS.md` | Rewrite | Bring in line with current codebase |

## Implementation Order

1. Write the updated `AGENTS.md` content
