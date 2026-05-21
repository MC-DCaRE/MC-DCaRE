## MODIFIED Requirements

### Requirement: CLI run command executes simulations

The `run_simulation.py run` command MUST use the public `Orchestrator.run()` and `Orchestrator.prepare_only()` methods.

#### Scenario: Run simulation from CLI
- **WHEN** `uv run python run_simulation.py run config.yaml`
- **THEN** the simulation executes via `Orchestrator.run(config)` and completes successfully

#### Scenario: Dry run from CLI
- **WHEN** `uv run python run_simulation.py run config.yaml --dry-run`
- **THEN** files are prepared via `Orchestrator.prepare_only(config)` without executing TOPAS
