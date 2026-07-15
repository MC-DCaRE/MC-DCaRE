<!-- Context: coding-workflow/procedures | Priority: high | Version: 1.0 | Updated: 2026-06-12 -->

# Coding Workflow Procedures

**Purpose**: Development workflow with automatic complexity routing. Simple changes get direct implementation; complex changes go through OpenSpec.
**Audience**: Coding workflow agent.

## Complexity Routing

### Simple (Direct Implementation)
Route here when the change:
- Touches 1-2 files
- Is a bug fix, typo, small refactor
- Adds/updates tests for existing code
- Is documentation-only
- Is a config tweak or dependency bump
- Has no architecture impact
- Has a single clear approach

### Complex (OpenSpec Workflow)
Route here when the change:
- Is a new feature or capability
- Modifies interfaces, ABCs, or contracts
- Touches 3+ files
- Affects architecture
- Changes public API or CLI surface
- Is performance-critical
- Has multiple valid design approaches

## Simple Path

### Stage 1: Branch
```bash
git checkout develop && git pull --rebase
git checkout -b develop-{context}-{feature}
```

### Stage 2: Implement
1. Read relevant source files — understand before editing
2. Make minimal, scoped changes
3. Follow project conventions:
   - `from __future__ import annotations` at top
   - Type hints on all functions
   - `logging.getLogger(__name__)` for logging
   - `frozen=True` for dataclasses in models/
   - `src.` prefix for imports

### Stage 3: Verify (order matters)
```bash
uv run ruff format src/ tests/          # 1. Format
uv run ruff check src/ tests/ --fix     # 2. Lint
rm -rf .mypy_cache && uv run mypy src/  # 3. Type check (clean cache)
uv run python -m pytest tests/ -v       # 4. Test
```
All four steps must pass. If any fails, fix and re-run from that step.

### Stage 4: Commit and Push
```bash
git add <specific files>
git commit -m "type(scope): description"
git push -u origin HEAD
git status  # Must show "up to date with origin"
```

### Stage 5: Suggest Review (if substantial)
If 2+ files changed, logic modified, or non-trivial fix:
> Ready for a code review? Run `/review` to check the changes.

## Complex Path (OpenSpec)

### Stage 1: Explain
Tell the user which complex criteria matched. 1-2 sentences.

### Stage 2: Propose
1. Load `openspec-workflow` skill (mandatory)
2. Load `openspec-propose` skill
3. Run `/opsx-propose` — creates proposal.md, design.md, tasks.md

If the user wants to explore first:
1. Load `openspec-workflow` skill
2. Load `openspec-explore` skill
3. Run `/opsx-explore`
4. Then proceed to propose

### Stage 3: Implement
1. Load `openspec-workflow` skill
2. Load `openspec-apply-change` skill
3. Run `/opsx-apply` — implements tasks sequentially
4. Run verification pipeline after all tasks complete

### Stage 4: Archive
1. Load `openspec-workflow` skill
2. Load `openspec-archive-change` skill
3. Run `/opsx-archive`

## Commit Format

```
type(scope): description

[Optional body]
[Optional footer: Closes #123]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Scopes: `config`, `ctdi`, `dicom`, `orchestrator`, `templates`, `gui`, `services`, `cli`, `models`, `test`

## Branch Naming

- Feature: `develop-{context}-{feature-name}`
- Sub-task: `develop-{context}-{feature}-{sub-task}`
- Hotfix: `main-hotfix-{issue-description}`

## Failure Handling

If verification fails:
1. Make one targeted fix if the cause is clear
2. Re-run verification from the failed step
3. If still failing after one attempt, stop and report
4. Do NOT weaken assertions, skip tests, or expand scope to get a pass

## Pre-flight Checks

Before starting any change:
- `git status` — working directory clean (or user acknowledged)
- `develop` branch exists and is up to date
- No uncommitted changes that could conflict

## Post-flight Checks

Before claiming done:
- Verification pipeline: all 4 steps passed
- Changes committed with proper format
- `git push` succeeded
- `git status` shows "up to date with origin"
