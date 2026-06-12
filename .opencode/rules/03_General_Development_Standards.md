# General Development Standards

## Tooling Commands
```bash
uv run ruff format package_name/      # Format before every commit
uv run ruff check package_name/ --fix # Lint
uv run mypy package_name/            # Type check
uv run python -m pytest tests/ -v    # Test
uv run python -m pytest tests/ --cov=package_name/  # Coverage
```

## Code Quality
- Type hints required on all functions (PEP 484)
- Docstrings on all public functions/classes (PEP 257)
- Format and lint with `ruff`, type check with `mypy`
- Testing with `pytest` (never `unittest`)
- Tests in `tests/` mirroring package structure, testing both happy path and error conditions

## Configuration Management
- Use YAML config files validated with Pydantic models
- Secrets via environment variables only (`${VAR_NAME}` in config)
- Config structure: `database`, `app`, `output` sections

## Conventions
- Use dependency injection for loose coupling
- Interfaces for contracts between layers
- Document key architectural decisions as ADRs
- Use `logging` module, never `print()`
- Use `typer.Exit(1)` for CLI failures
- Log format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

## Pre-Commit Checklist
- Tests pass, ruff formatted and clean, mypy clean
- Commit format: `type(scope): description` (feat/fix/docs/style/refactor/test/chore)

## File Size Guidelines
| Type | Target Lines | Max |
|------|-------------|-----|
| Entry points | < 100 | 100 |
| Abstractions | 200-500 | 500 |
| Implementations | 200-500 | 2,000 |
| Utilities/Tests | 200-500 | 500 |

Don't artificially split files. Prioritize readability over line counts.

## Task Decomposition & Prioritization

### Decomposition Rules
- Each subtask = one clear purpose with measurable outcomes
- Break down until each task is independently verifiable
- Tasks should produce a concrete artifact (code, test, document, config)

### Priority Framework
- **Critical**: Blocks other work or breaks production
- **High**: Required for current milestone, no workaround available
- **Medium**: Important but not blocking, workaround exists
- **Low**: Nice to have, can defer without impact

Always decompose tasks before implementing. Start with the highest-priority task that unblocks the most other work.
