## Context

The normalization pipeline currently has two code paths that produce inconsistent absolute dose scales:

1. **Direct beam source** (CTDI calibration): `total_histories = R × histories_per_run` (e.g., 180M for 36 angles × 5M). The `compute_photons_per_mAs` function uses this value, causing `total_histories` to cancel in the absolute dose formula, giving `absolute = raw × sf`. This overcounts by R (typically 36×).

2. **Phase space replay** (phantom dose): `_write_replay_metadata` divides `sf` by M×R, and `total_histories` stays at `N_scoring`. The absolute dose becomes `raw × sf / (M×R)`. This is correct relative to the scoring run but on a different scale from the CTDI calibration.

The result: the DCF from CTDI is ~180× too small for phantom dose. No CTDI-derived calibration can transfer to organ dose.

## Goals / Non-Goals

**Goals:**
- Make the DCF transfer between CTDI calibration and phantom dose simulations
- Auto-detect and scale for: direct beam, phase space replay (M reuse), sequential times (R angles), and any combination
- Single normalization formula that works for all source types

**Non-Goals:**
- Changing the TOPAS simulation templates or geometry
- Changing the CTDI_w formula or the CTDICalculator mean-dose fix
- Re-running simulations (all existing CSV outputs remain valid — only post-processing changes)

## Decisions

### Decision 1: Use `N_scoring` (not `total_histories`) in `compute_photons_per_mAs`

**Rationale**: `photons_per_mAs` is a property of the beam model, not the current simulation. It represents how many real photons per mAs each simulated source photon represents. This depends on `sf` (from SpekPy) and `N_scoring` (how many source photons the scoring run used to calibrate sf). It does NOT depend on how many histories the current run uses.

**Alternative considered**: Store `N_scoring` explicitly in the metadata as a separate field. Rejected — it's already available as `total_histories` in the scoring run metadata, and the replay metadata copies it through.

### Decision 2: Use `N_scorer_active_histories` from the TOPAS CSV

**Rationale**: TOPAS reports `Histories_with_Scorer_Active` in every CSV output file. This is the actual number of histories that contributed to the scorer, accounting for:
- Direct beam: `R × histories_per_run` per angle, accumulated across all angles
- Phase space replay: `N_phsp × M × R` (each particle used M times across R angles)
- Phase space with M=0 (NumberOfHistoriesInRun override): whatever TOPAS ran

Using this value directly from the CSV eliminates all ambiguity about how many histories were simulated.

**Alternative considered**: Compute N_scorer_active from metadata (N_phsp × M × R). Rejected — this requires knowing N_phsp from the phase space header, which may not always be available in the runfolder. The CSV value is always available and authoritative.

### Decision 3: Do NOT divide sf by M×R in replay metadata

**Rationale**: The old approach divided sf by M×R to keep the per-primary dose intensive. But this created a different absolute scale from the CTDI calibration. With the new formula (`raw × sf × N_scoring / N_scorer_active`), the M×R scaling is handled by N_scorer_active naturally, because:
- `raw` scales linearly with M (each reuse deposits more dose)
- `N_scorer_active` also scales with M (more histories → more active)
- The ratio `raw / N_scorer_active` is independent of M

### Decision 4: Rename `total_histories` parameter to `n_scorer_active_histories`

**Rationale**: The old name was misleading — `total_histories` in the metadata represents the scoring run's history count, not the current run's scorer-active count. The new name makes it clear that this is the actual number of histories the scorer accumulated over.

**Breaking change**: All callers of `raw_absolute_dose_Gy()` must be updated. This is intentional — it forces review of each call site.

## Risks / Trade-offs

- **[Risk] Existing DCF values in calibration.yaml become invalid** → All DCFs must be recomputed from existing CTDI calibration CSVs with the new formula. The CSVs are still valid; only the post-processing changes.
- **[Risk] The `Histories_with_Scorer_Active` value might be wrong for some scorer types** → Verify by comparing with expected values (R × histories for direct beam, N_phsp × M × R for replay). Add validation in CTDICalculator.
- **[Risk] CTDI calibration CSVs from single-angle runs (sequential_times=1) have correct N_scorer_active but wrong angular coverage** → The DCF will be angle-specific, not rotationally averaged. Document that rotational calibration requires sequential_times ≥ 36.

## Migration Plan

1. Implement the code changes (4 files)
2. Run all unit tests — update expected values where the normalization formula changed
3. Re-compute all DCFs from existing CTDI calibration CSVs using the new formula
4. Re-compute the pelvis phantom effective dose with the new DCF
5. Verify: DCF transfers, effective dose is within expected range
6. Update calibration.yaml with recomputed DCFs
7. Commit

## Open Questions

- Should we also re-run the CTDI calibration with sequential_times=36 for all protocols? Current DCFs were computed with sequential_times=1 (single angle). The answer affects accuracy but not the normalization fix.
