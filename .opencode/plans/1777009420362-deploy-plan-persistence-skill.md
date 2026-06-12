# Plan: Deploy plan-persistence Skill Globally

## Problem

The global `~/.config/opencode/AGENTS.md` instructs agents to "Load the `plan-persistence` skill before planning," but the skill doesn't exist in `~/.config/opencode/skills/`. Only `prd-management` is deployed there. The `plan-persistence` skill already exists in `~/Github/AI-Model-Settings/opencode/.opencode/skills/plan-persistence/SKILL.md` but was never copied to the global config location.

The compaction plugin (`~/.config/opencode/plugins/plan-persistence.js`) is already deployed and working — it provides a 6-line reminder during compaction. The skill provides the full reference manual (file naming, required sections, writing procedure, when to write vs skip). They are complementary, not redundant.

## Approach

1. Create the directory `~/.config/opencode/skills/plan-persistence/`
2. Copy `SKILL.md` from the AI-Model-Settings source repo to the global skills directory

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `~/.config/opencode/skills/plan-persistence/SKILL.md` | Create | Full plan-writing instructions available via `skill` tool globally |

## Key Design Decisions

- **Source**: Copy from `~/Github/AI-Model-Settings/opencode/.opencode/skills/plan-persistence/SKILL.md` verbatim — it's already the canonical version
- **Location**: Global (`~/.config/opencode/skills/`) not project-level — the AGENTS.md that references it is global, so the skill must be too
- **No changes needed to AGENTS.md or plugin** — they already reference the skill correctly

## Implementation Order

1. `mkdir -p ~/.config/opencode/skills/plan-persistence/`
2. `cp ~/Github/AI-Model-Settings/opencode/.opencode/skills/plan-persistence/SKILL.md ~/.config/opencode/skills/plan-persistence/SKILL.md`
3. Verify the skill appears in the available skills list
