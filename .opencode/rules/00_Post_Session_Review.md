# Post-Session Review Suggestion

## Overview

After completing substantial implementation work, the agent MUST proactively suggest a code review. This mirrors the behavior of Kilo Code's built-in `suggest` tool, which automatically offers a `/local-review-uncommitted` after implementation tasks.

## When to Suggest Review

Suggest `/review` after completing **substantial implementation work**, defined as:

- Modified or created 2+ files
- Changed logic in existing functions or classes
- Added new features, endpoints, or components
- Fixed a non-trivial bug
- Refactored code across multiple files

**Do NOT suggest review** for:
- Trivial changes (single-line fixes, typo corrections)
- Read-only operations (exploration, Q&A, explanations)
- Tasks the user explicitly said were minor
- Documentation-only changes (unless architecture-level)

## How to Suggest

After presenting your final response for a substantial implementation task, append a brief suggestion:

```
---

Ready for a code review? Run `/review` to check the changes.
```

Keep it to 1-2 lines. Do not elaborate or explain why review is beneficial. Do not repeat the suggestion if the user dismisses it.

## Important Notes

- This is a soft suggestion, not a requirement — the user may accept or ignore it
- Only suggest once per implementation task — do not nag
- If the user explicitly declines, do not suggest again in that session
- The `/review` command delegates to the `code-reviewer` agent for a thorough review
- This rule applies to the `build` agent (primary coding agent) and any agent that performs file modifications
- The suggestion should appear AFTER the work summary, not during or before
