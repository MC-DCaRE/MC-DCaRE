## Context

`run_simulation.py` was written for an earlier version of `Orchestrator` that had separate `create_runfolder()` and `run_with_runfolder()` methods. The current `Orchestrator.run()` handles both internally. The CLI was never updated after the API changed.

`spectrum_generator.py` has a late `import os` at line 58 with no justification.

## Goals / Non-Goals

**Goals:**
- Make `run_simulation.py run` functional
- Fix late import in spectrum_generator

**Non-Goals:**
- Adding new CLI features
- Refactoring the logging handler setup
- Changing Orchestrator API

## Decisions

1. **Use `Orchestrator.run()` directly**: The `run` command should call `orchestrator.run(config, dry_run=dry_run)`. The method returns the rundir. File handler for logging can be attached using the returned path.

2. **Preserve dry-run behavior**: `Orchestrator.prepare_only()` already exists and returns the rundir. Use it for `dry_run=True`.

3. **Move import**: Trivial fix, no design decision needed.

## Risks / Trade-offs

- Minimal risk. The Orchestrator API is well-tested (319 tests pass). The fix is a straightforward API alignment.
