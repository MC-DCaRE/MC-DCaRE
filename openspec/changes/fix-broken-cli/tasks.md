## 1. Fix run_simulation.py run command

- [ ] 1.1 Rewrite `run` command to use `orchestrator.run(config, dry_run=dry_run)` and `orchestrator.prepare_only(config)`
- [ ] 1.2 Fix file handler setup to use returned rundir instead of pre-creating runfolder
- [ ] 1.3 Update `tests/unit/test_run_simulation_cli.py` for fixed API calls

## 2. Fix spectrum_generator import

- [ ] 2.1 Move `import os` from line 58 to module-level imports
- [ ] 2.2 Run `ruff format`, `ruff check`, `mypy` on changed files
- [ ] 2.3 Run full test suite
