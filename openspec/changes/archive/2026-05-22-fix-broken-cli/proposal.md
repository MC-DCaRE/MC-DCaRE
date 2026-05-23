## Why

`run_simulation.py` references methods that don't exist on `Orchestrator`:
- Line 46: `orchestrator.create_runfolder()` — the method is `_create_runfolder()` (private)
- Line 49: `orchestrator.run_with_runfolder(rundir, config)` — doesn't exist

The public API is `Orchestrator.run(config)` which handles runfolder creation and execution internally. The CLI `run` command crashes at runtime.

`src/spectrum_generator.py` has `import os` inside the `generate()` method body (line 58) despite no reason for late import.

## What Changes

- Fix `run_simulation.py run` command to use the public `Orchestrator.run()` API
- Move `import os` to module level in `spectrum_generator.py`

## Capabilities

### Modified Capabilities
- `cli-run-command`: Fix broken `run` subcommand to use correct Orchestrator API

## Impact

- `run_simulation.py` — fix `run` command
- `src/spectrum_generator.py` — move import to top
