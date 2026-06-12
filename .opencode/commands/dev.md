---
description: "Start a coding workflow — auto-routes simple changes to direct implementation, complex changes to OpenSpec"
---

Start a development workflow. Automatically assesses change complexity and routes accordingly.

**Input**: The argument after `/dev` is a description of the change to make.

**Examples**:
- `/dev Fix the typo in the CTDI calculator error message`  (simple)
- `/dev Add support for multi-slice CTDI scoring`  (complex)
- `/dev Refactor the mode base class to support custom phantoms`  (complex)
- `/dev Update the test fixtures for the new config format`  (simple)

**Complexity Routing**

**Simple** (direct implementation) when:
- Touches 1-2 files
- Bug fix, typo, small refactor
- Test additions/updates
- Documentation only
- Config tweak
- Single clear approach

**Complex** (OpenSpec workflow) when:
- New feature or capability
- Interface/ABC/contract changes
- 3+ files affected
- Architecture changes
- API or CLI surface changes
- Multiple valid approaches

**Steps**

1. **Understand the change** — Clarify what the user wants if ambiguous.

2. **Assess complexity** — Apply routing criteria. State the assessment.

3. **If simple**:
   - Create feature branch from develop
   - Implement the change
   - Run verification: `ruff format` → `ruff check --fix` → `mypy` → `pytest`
   - Commit and push
   - Suggest `/review` if substantial

4. **If complex**:
   - Explain why it warrants planning
   - Load `openspec-workflow` skill
   - Load `openspec-propose` skill
   - Run `/opsx-propose` to create proposal, design, tasks
   - After user approval, run `/opsx-apply` to implement
   - Run verification pipeline
   - Run `/opsx-archive` to close

**Constraints**:
- Always create feature branch before implementation
- Never claim done without running verification pipeline
- Never work directly on develop or main
- Use `uv run` for all Python commands
