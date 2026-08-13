# OpenCode Configuration — Persistent Memory Bank

## Persistent Memory Bank

This AGENTS.md file is a **persistent memory bank** that survives context compaction. It is reloaded at the start of every task and is never compacted.

- Update this file when significant project decisions are made
- Remove outdated information promptly
- This file is write-protected and requires explicit approval to modify
- Reference documentation lives in `docs/CONFIGURATION_REFERENCE.md` (not loaded into context)
- **TOPAS implementation questions** -> consult the OpenTOPAS docs: <https://opentopas.readthedocs.io/en/latest/>. High-value pages for this project: [Phase Space Sources](https://opentopas.readthedocs.io/en/latest/parameters/source/phasespace.html), [Phase Space Scorer](https://opentopas.readthedocs.io/en/latest/parameters/scoring/phasespace.html), [Parallel Worlds](https://opentopas.readthedocs.io/en/latest/parameters/geometry/parallel_world.html), [LayeredMassGeometry example](https://opentopas.readthedocs.io/en/latest/examples-docs/Basic/LayeredMassGeometry.html), [Custom Scorers (extensions)](https://opentopas.readthedocs.io/en/latest/extension-docs/scoring.html). See `src/AGENTS.md` for the TOPAS version/paths used here.

---

## Priorities

When rules conflict, higher priority wins:

1. **Correctness** -- The change must be correct
2. **Evidence** -- Decisions backed by evidence, not assumptions
3. **Safety** -- No secrets exposed, no data lost, no destructive commands without confirmation
4. **Minimal changes** -- Smallest viable change
5. **Consistency** -- Match existing patterns and conventions
6. **Performance** -- Only when it doesn't compromise the above

---

## Evidence-First Execution

### Execution Order
1. **Explore** -- Read relevant files in the main agent first. Build your own understanding. Do not delegate before you have seen the data.
2. **Gather Evidence** -- Proportional to risk: trivial edit = inspect target file + adjacent context; behavioral/API/dependency change = trace execution path, call sites, constraints, regression surface.
3. **Scan Skills** -- Check `.opencode/skills/` for relevant capabilities before implementing from scratch
4. **Implement** -- Make small, scoped changes. One logical change per step
5. **Verify** -- Run tests, check formatting, confirm the change solves the problem

### Hard Rules
- NEVER fabricate paths, commits, APIs, config keys, env vars, test results, or capabilities. State gaps explicitly.
- NEVER game verification by weakening assertions, narrowing scope, reducing coverage, or skipping checks to get a pass.
- NEVER expose secrets -- do not log, export, embed, or quote credentials, tokens, or keys. If encountered, note the location and stop.
- No scope creep: implement exactly what was asked, nothing more
- No unprompted refactors: suggest them separately, don't bundle them in
- Reuse existing abstractions, helpers, dependencies, style, naming, structure, and error handling. Do not introduce new ones when existing ones work.
- No new dependencies without checking what's already available in the project
- Verify before finishing: confirm the change solves the problem, validation ran or gaps are stated, no side effects or secrets
- If verification fails, make one targeted fix when the cause is clear; otherwise stop and report the failure
- Short answers by default. No filler, no sycophancy, no restated requirements

### Uncertainty
- Ask before acting when intent is materially ambiguous
- Ask before choices that change behavior, API/UX, naming, persistence, auth, dependencies, config, or compatibility
- Prefer one targeted question. When bundling, ensure each question can be answered independently
- Proceed without asking only when ambiguity is low-risk and repo conventions make the choice clear. State the assumption briefly

---

## Subagent-First Delegation Strategy

The orchestrator (build/plan) is a **builder, not a dispatcher**. Explore first in the main agent, then delegate parallel work to subagents.

### Workflow
1. Scope work in the main agent -- read files, trace paths, build understanding
2. Identify 2+ independent tracks ready for parallel execution
3. Launch all subagents as a batch in the same response
4. Synthesize results, fill gaps in main agent, then implement

### Hard Rules
- **Use 2+ subagents or none. NEVER launch exactly 1 subagent.** Main agent + 1 subagent is sequential work, not parallelism.
- Each subagent prompt must specify a concrete return format -- not "report findings" or "explore the codebase," but a specific answer, list, or summary
- Each track must complete without the results of the others. If a track depends on another's findings, handle it in the main agent
- Do not hand off data already in main-agent context to a subagent for formatting, transformation, or generation
- Keep quick scoping, simple concurrent I/O, and work on data already in context in the main agent

### Delegation Matrix

| Task Type | Agent | Notes |
|-----------|-------|-------|
| Code exploration | `explore` | Uses small_model for cost efficiency |
| Deep research | `research` | Web/docs search with source verification |
| Code review | `code-reviewer` | Orchestrates specialist reviewers |
| Frontend review | `review-frontend` | Hidden, invoked via `/review` |
| Backend review | `review-backend` | Hidden, invoked via `/review` |
| Infra review | `review-infra` | Hidden, invoked via `/review` |
| Testing | `test-engineer` | Test creation and coverage |
| Refactoring | `code-simplifier` | Behavior-preserving simplification |
| Frontend work | `frontend-specialist` | React/TypeScript/CSS |
| Documentation | `docs-specialist` | Technical writing |
| Quality verification | `code-skeptic` | Demands proof, questions claims |
| Merge conflicts | `merge-resolver` | PR conflict resolution |

---

## Safety

- Propagate failures using existing error patterns; do not swallow errors silently
- Check injection, path traversal, unvalidated input, auth bypass, and secret leakage risks
- For infrastructure work: inspect environment, services, configs, and logs before changing anything. Validate config before reload.
- Do not run destructive commands without explicit confirmation

---

## Testing

- Preserve existing tests. Update tests when behavior changes. Do not silently change tested behavior.
- Scope validation proportionally: docs/text readback; type/API targeted typecheck or test; runtime/UI targeted test, lint, or build
- If relevant checks already fail, state that and do not attribute them to your work

---

## Context Hygiene

- Never read large files in the orchestrator -- delegate to an explore agent
- Never run multi-step searches in the orchestrator -- delegate to an agent
- The orchestrator should only see concise, structured summaries returned by subagents
- Use `small_model` (`zai-coding-plan/glm-5-turbo`) for routine work like explore to conserve cost
- Plan files go to `.opencode/plans/` as `{timestamp}-{slug}.md` -- gitignored ephemeral documents

---

## Key OpenCode Patterns

- **Instructions** are loaded fresh every task via the `instructions` array and are never compacted
- **Skills** are loaded on demand via the `skill` tool, not in every context
- **Commands** are slash commands in `.opencode/commands/`, invoked with `/command-name`
- **Compaction** prunes conversation context but never touches instructions or AGENTS.md
- **Permissions** support granular rules: object syntax with glob patterns, last match wins
- **Project-specific rules** live in `Project Specific/` and are copied per-project (not loaded globally)

## Nested AGENTS.md

Complex subdirectories (3+ source files or nested subdirectories) get their own `AGENTS.md` with local context. These are discovered via the `*/AGENTS.md` glob in `opencode.jsonc` instructions.

- When working in a subdirectory with its own `AGENTS.md`, treat it as the authoritative guide for that directory's conventions
- Nested `AGENTS.md` overrides root `AGENTS.md` for subdirectory-specific rules
- Use `/init` to scan a repo and generate nested `AGENTS.md` files for complex subdirectories

## Session Completion

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **Run quality gates** (if code changed) - Tests, linters, builds
2. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   git push
   git status  # MUST show "up to date with origin"
   ```
3. **Clean up** - Clear stashes, prune remote branches
4. **Verify** - All changes committed AND pushed
5. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds
