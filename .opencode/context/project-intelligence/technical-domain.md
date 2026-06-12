<!-- Context: project-intelligence/technical | Priority: critical | Version: 1.0 | Updated: 2026-05-21 -->

# Technical Domain

**Purpose**: Tech stack, architecture, and development patterns for MC-DCaRE.
**Last Updated**: 2026-05-21

## Quick Reference
- **Update Triggers**: Tech stack changes, new patterns, architecture decisions
- **Audience**: Developers, AI agents

## Primary Stack

| Layer | Technology | Version | Rationale |
|-------|-----------|---------|-----------|
| Language | Python | >=3.8 | Scientific computing ecosystem |
| Monte Carlo | TOPAS/Geant4 | external | Radiation transport simulation engine |
| Templates | Jinja2 | >=3.1.0 | TOPAS parameter file generation |
| Spectrum | SpekPy | >=2.5.4 | X-ray spectrum modeling |
| GUI | FreeSimpleGUI | >=5.2.0 | Desktop interface for simulation config |
| CLI | Typer | latest | Command-line interface framework |
| Data | pandas, numpy | >=1.24 | Dose data processing |
| DICOM | pydicom | >=2.4.4 | Medical imaging file handling |
| Build | hatchling | latest | Package build system |
| Format/Lint | ruff | latest | Replaces black + flake8 |
| Type Check | mypy | latest | Strict mode (disallow_untyped_defs) |
| Test | pytest | >=8.3.5 | With pytest-mock, pytest-cov |

## Entry Points

Three entry points into `src/`:

1. **`topas_gui.py`** -- FreeSimpleGUI desktop app. `MainView` (layout) + `GUIController` (events).
2. **`run_simulation.py`** -- Typer CLI: `run`, `generate-config`, `validate`, `convert`.
3. **`calculate_ctdiw.py`** -- Post-processing CLI for CTDI-w dose metrics from TOPAS CSV output.

## Architecture Pattern

**Orchestrator + Strategy**:

```
SimulationConfig (YAML)
  -> Orchestrator selects SimulationMode (CTDI or DICOM)
    -> mode.build_main_context() -> Dict[str, object]
    -> TemplateRenderer.render(.j2 template, context)
    -> mode.build_sub_context() -> Dict[str, object]
    -> TemplateRenderer.render(sub template, context)
    -> SpectrumGenerator (SpekPy)
    -> mode.prepare_run() -> copy files to runfolder
    -> mode.execute() -> SimulationRunner (TOPAS subprocess)
    -> CTDICalculator post-processes results
```

Key abstractions:
- `SimulationMode` ABC in `src/modes/base.py` -- strategy pattern
- `TemplateRenderer` in `src/template_renderer.py` -- Jinja2 rendering
- `Orchestrator` in `src/orchestrator.py` -- central coordinator
- `SimulationConfig` in `src/config.py` -- YAML-backed configuration

## Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Files | snake_case | `simulation_runner.py` |
| Classes | PascalCase | `CtdiMode`, `SimulationConfig` |
| Functions | snake_case | `build_main_context()` |
| Constants | UPPER_SNAKE | `_PLUG_POSITIONS` |
| Templates | kebab/snake + `.j2` | `headsourcecode_boilerplate.j2` |
| Imports | `src.` prefix | `from src.config import SimulationConfig` |
| GUI keys | `-UPPER-DASHES-` | `-SIMULATION-TYPE-` |
| Tests | `test_<module>.py` | `test_ctdi_mode.py` |

## Code Standards

- `from __future__ import annotations` at top of every module
- Type hints on all functions (`mypy --disallow-untyped-defs`)
- Docstrings on all public functions/classes (PEP 257)
- `logging.getLogger(__name__)` -- never `print()` (except entry points)
- `frozen=True` dataclasses for immutable value objects in `models/`
- ABCs define contracts (`modes/base.py`)
- Context dicts (`Dict[str, object]`) consumed by Jinja2 templates
- Line length: 88 (ruff/black)
- `uv run` for all Python execution (never bare `python`)

### Verification Pipeline (order matters)

```bash
uv run ruff format src/ tests/          # 1. Format
uv run ruff check src/ tests/ --fix     # 2. Lint
rm -rf .mypy_cache && uv run mypy src/  # 3. Type check (clean cache first)
uv run python -m pytest tests/ -v       # 4. Test
```

## Security Requirements

- YAML config files validated with Pydantic-style dataclasses
- Secrets via environment variables only (never hardcoded)
- TOPAS binary path from config, never assumed
- TOPAS execution always mocked in tests -- no external binary dependency
- `runfolder/` and `tmp/` are runtime output, gitignored
- No secrets or credentials in source code or templates

## 📂 Codebase References

| Pattern | Implementation | Config |
|---------|---------------|--------|
| Orchestrator | `src/orchestrator.py` | `pyproject.toml` |
| Strategy ABC | `src/modes/base.py` | `pytest.ini` |
| CTDI mode | `src/modes/ctdi_mode.py` | `opencode.jsonc` |
| DICOM mode | `src/modes/dicom_mode.py` | `.opencode/rules/` |
| Jinja2 templates | `src/boilerplates/*.j2` | `config.yaml` |
| Sub-templates | `src/boilerplates/TOPAS_includeFiles/*.j2` | |
| Config dataclass | `src/config.py` | |
| Template renderer | `src/template_renderer.py` | |
| CLI entry point | `run_simulation.py` | |
| GUI entry point | `topas_gui.py` | |
| CTDI post-processing | `calculate_ctdiw.py` | |

## Related Files
- `AGENTS.md` (root) -- Project-level agent instructions
- `src/AGENTS.md` -- Source package architecture
- `src/boilerplates/AGENTS.md` -- Template variable reference
- `src/modes/AGENTS.md` -- Mode strategy documentation
