# Agent Instructions

## Python Commands

Always use `uv run` as the prefix for all Python commands in this project. Examples:

- `uv run pytest tests/ -v`
- `uv run python -m pytest tests/ -v`
- `uv run python script.py`
- `uv run ruff check src/`
- `uv run ruff format src/`

Never use bare `python`, `python3`, or `pip install` commands.
