# Plan: Validate GitHub Issue #48 — spekpy Version Compatibility

## Problem

GitHub issue [#48](https://github.com/MC-DCaRE/MC-DCaRE/issues/48) claims `energyspectrum.py` "only works with spekpy version 2.0.13, not with 2.5.3 (latest as of 19 Jan)". The issue was filed 2026-01-19 against the upstream repo. We need to validate whether this claim is true and determine the right fix for the upstream repo.

## Investigation Summary (Read-Only Phase)

### What the issue says
- **Title**: "energyspectrum.py spekpy version"
- **Body**: "file only works with spekpy version 2.0.13, not with 2.5.3 (latest as of 19 Jan)"
- **File referenced**: `src/Energyspectrum.py` on `upstream/main`
- **No details provided**: no traceback, no error description, no reproduction steps

### Key Findings

1. **Upstream state** (`upstream/main`, commit `b785667`):
   - `requirements.txt` pins `spekpy==2.0.13`
   - `src/Energyspectrum.py` uses these spekpy APIs:
     - `sp.Spek(kvp=..., th=14, mas=..., dk=0.2, z=0.1)` — constructor
     - `s.state.get_current_state_str('full', s.get_std_results())` — state dump
     - `s.get_spectrum(edges=False, diff=False)` — spectrum retrieval
     - `s.get_flu()` — total fluence

2. **Local fork state** (`origin/main`, commit `d38970b`):
   - `pyproject.toml` requires `spekpy>=2.5.4`
   - `src/spectrum_generator.py` (refactored from `Energyspectrum.py`) uses **identical API calls**
   - All APIs verified working with installed `spekpy==2.5.4`

3. **spekpy release timeline**:
   | Version | Release Date | Notes |
   |---------|-------------|-------|
   | 2.0.13 | 2024-08-08 | Pinned in upstream requirements.txt |
   | 2.5.3  | 2025-10-14 | "Latest" when issue was filed (2026-01-19) |
   | 2.5.4  | 2026-03-31 | Current latest; pinned in local fork |

4. **API compatibility verified with 2.5.4**: All upstream code paths execute successfully with `spekpy==2.5.4`. No crashes, no API incompatibilities detected.

5. **Key API change**: `get_spectrum()` gained a `flu` parameter (default `True`) in 2.5.x that did not exist in 2.0.x. The upstream code calls `get_spectrum(edges=False, diff=False)` — this does NOT pass `flu`, so it gets the new default. This **may change output values** compared to 2.0.13 behavior but does not crash.

6. **Local fork already resolved this**: The refactored `spectrum_generator.py` works correctly with `spekpy>=2.5.4`.

### Assessment

**The issue is PARTIALLY VALID:**

- **TRUE**: The upstream code is pinned to `spekpy==2.0.13` and has not been tested/updated for newer versions. The `requirements.txt` needs updating.
- **LIKELY TRUE**: Version 2.5.3 may have had a bug or behavioral difference that caused incorrect results (2.5.4 was released 2 months after the issue was filed, possibly fixing it).
- **NOT DETERMINED**: Whether the code crashes or produces wrong results with 2.5.3 specifically — we cannot install 2.5.3 in plan mode to test.
- **RESOLVED in local fork**: The local fork already requires `spekpy>=2.5.4` and the refactored code works.

## Approach

### Step 1: Create a worktree from upstream/main
Create a git worktree based on `upstream/main` to test the original `src/Energyspectrum.py` in isolation.

### Step 2: Test with spekpy 2.5.3 (the problematic version)
In the worktree, install `spekpy==2.5.3` and run `Energyspectrum.py` directly:
```bash
cd <worktree>
uv pip install spekpy==2.5.3
uv run python src/Energyspectrum.py
```
Record any errors, tracebacks, or behavioral differences.

### Step 3: Test with spekpy 2.5.4 (the fix)
Install `spekpy==2.5.4` and repeat:
```bash
uv pip install spekpy==2.5.4
uv run python src/Energyspectrum.py
```
Confirm it works and compare output values with 2.5.3 (if 2.5.3 didn't crash).

### Step 4: Compare output values with 2.0.13 (original pinned version)
Optionally test with 2.0.13 to compare output:
```bash
uv pip install spekpy==2.0.13
uv run python src/Energyspectrum.py
```

### Step 5: Report findings and close/update the issue
Post a comment on issue #48 with:
- Confirmation of whether the issue is valid
- The specific API/behavioral change that causes the problem
- Recommendation: update `requirements.txt` to `spekpy>=2.5.4`

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `.opencode/plans/1777340540991-validate-spekpy-issue48.md` | Create | This plan |
| `~/.tmp/mc-dcare-issue48/` (worktree) | Create | Isolated test environment |
| GitHub issue #48 | Comment | Report validation results |

## Key Design Decisions

1. **Test against 2.5.3 specifically**: The issue references this version. We need to confirm the exact failure mode.
2. **Test against 2.5.4**: Confirm the local fork's dependency floor is correct.
3. **Use worktree from upstream/main**: The file on upstream is `src/Energyspectrum.py`; the local fork renamed it to `src/spectrum_generator.py`. Testing upstream code directly gives the most accurate validation.

## Implementation Order

1. `git worktree add` from `upstream/main`
2. Install `spekpy==2.5.3` → run `Energyspectrum.py` → record results
3. Install `spekpy==2.5.4` → run `Energyspectrum.py` → record results
4. (Optional) Install `spekpy==2.0.13` → run `Energyspectrum.py` → compare outputs
5. Post findings as a comment on GitHub issue #48
6. Clean up worktree
