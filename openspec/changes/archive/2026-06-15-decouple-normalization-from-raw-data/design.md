## Context

The current normalization chain combines three components — `norm_factor`, `exposure_mAs`, and `dcf_used` — into a single `calibration_factor` at simulation time. This combined factor is written to `simulation_metadata.yaml` and `head_calibration_factor.txt`, then consumed by `CTDICalculator` to produce CTDI-w values. Separately, `CalibrationService.apply()` can apply another DCF multiplier on top.

This produces two practical problems:
1. **Dual DCF paths** — `dcf_used` lives in the config YAML AND a separate `calibration.yaml` managed by `CalibrationService`. A user who sets `dcf_used=0.85` in config and then runs `CalibrationService.apply()` gets double-counted DCF.
2. **Tied to runfolder** — the combined calibration_factor is specific to `(histories, mAs, dcf_used)` for that run. You can't re-normalize a runfolder with a different DCF or mAs without either re-running or understanding the internal math.
3. **Provenance opacity** — `norm_factor` is a derived quantity (`no_particles / (histories * exposure)`), making it hard to verify the individual components from metadata alone.

Since the raw TOPAS CSV Sum values are already stored in the runfolder, normalizing strictly in post-processing means any re-analysis is just re-computing with different parameters.

## Goals / Non-Goals

**Goals:**
- Single DCF authority: `calibration.yaml` keyed by `(kV, fan_mode)` is the only DCF source
- Raw-normalized separation: raw Sum in CSVs stays untouched; normalization is a post-processing concern
- Re-analyzable runfolders: any runfolder can be re-normalized with different DCF or mAs via CLI flags
- Backward compatibility window: old runfolders with `head_calibration_factor.txt` can still be processed (deprecation path)

**Non-Goals:**
- Changing TOPAS scorer templates or CSV output format
- Changing the SpekPy spectrum generation
- Adding new scorer types
- GUI changes (unless incidental to the service refactor)

## Decisions

### Decision 1: Raw Sum stays in CSVs, normalization removed from CTDICalculator

`CTDICalculator._extract_dose_from_file` returns raw Sum (already what it does). But `_process_file_type` currently multiplies by `calibration_factor` internally. This multiplication moves to `CalibrationService`.

**Rationale**: The existing `_process_file_type` produces a single calibrated CTDI-w. After the change, it produces a dict with `{raw_sum, total_histories, exposure_mAs, scorer_type, positions}`. Downstream callers can normalize or not as they choose.

**Caller impact**: `calculate_ctdiw.py main` and `BenchmarkCalculator.compare()` both consume CTDICalculator output and will need updates.

### Decision 2: simulation_metadata.yaml stores components, not product

Current:
```yaml
norm_factor: 2.34e-6
mAs: 100
total_histories: 1000000
dcf_used: 1.0
calibration_factor: 0.234  # norm_factor * mAs * dcf_used
```

New:
```yaml
total_histories: 1000000
exposure_mAs: 100
spectrum_fluence_photons_per_mAs: 2.34e8  # s.get_flu() * 4π * 0.1²
dcf_hint: 1.0  # optional, for reference only — NOT applied by calculator
```

The normalization is now:
```
dose_Gy = raw_Sum × (spectrum_fluence_photons_per_mAs × exposure_mAs / total_histories) × DCF(kV, fan_mode)
```

**Rationale**: Components are independently verifiable. The DCF used during calibration is a separate concern stored in `calibration.yaml`.

### Decision 3: calibration.yaml stays as-is, becomes the single DCF authority

The existing `MachineCalibration` / `CalibrationEntry` model already keys DCF on `(kV, fan_mode)`. No schema change needed.

`CalibrationService.apply()` is extended to accept raw CTDICalculator output and apply the full normalization (norm_factor + mAs + DCF). It also accepts an optional `--dcf-override` for ad-hoc calibration without writing to `calibration.yaml`.

### Decision 4: `dose_calibration_factor` in config YAML becomes advisory

The `GeneralConfig.dose_calibration_factor` field stays for backward compat but is renamed (or aliased) to `dcf_hint`. It is written to `simulation_metadata.yaml` as metadata only and never applied automatically. A deprecation warning is emitted if set to anything other than 1.0 in the config validation.

### Decision 5: CLI flags for post-hoc normalization

```bash
# Current
uv run python calculate_ctdiw.py main <runfolder>

# New — no DCF applied by default
uv run python calculate_ctdiw.py main <runfolder>
# Returns "raw" CTDI-w (norm_factor × mAs only)

# With calibration lookup
uv run python calculate_ctdiw.py main <runfolder> --calibrated

# With explicit DCF
uv run python calculate_ctdiw.py main <runfolder> --dcf 0.87

# With mAs rescaling
uv run python calculate_ctdiw.py main <runfolder> --calibrated --target-mAs 50
```

## Normalization Flow (After Change)

```
┌──────────────────────────────────────────────────────────────────────┐
│ Runfolder                                                            │
│                                                                      │
│  ChamberPlugCentre_tle.csv   ← raw Sum (un-normalized)              │
│  ChamberPlugTop_tle.csv                                             │
│  ...                                                                 │
│  simulation_metadata.yaml    ← total_histories, exposure_mAs,        │
│                                spectrum_fluence_photons_per_mAs      │
└─────────────────────────────┬────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│ CTDICalculator.calculate()                                          │
│                                                                      │
│  Returns: {raw_sum, scorer_type, is_primary, positions: {           │
│    centre: {raw_sum, z_bin_data},                                    │
│    peripheral: [{position, raw_sum}, ...]                            │
│  }, metadata: {total_histories, exposure_mAs, ...}}                  │
│                                                                      │
│  NO calibration_factor applied at this stage                         │
└─────────────────────────────┬────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│ CalibrationService.normalize(raw_result, kV, fan_mode,              │
│                              target_mAs=None, dcf_override=None)     │
│                                                                      │
│  1. Read norm_factor from metadata:                                  │
│     norm_factor = spec_fluence / total_histories                     │
│  2. Read mAs from metadata (or use target_mAs)                       │
│  3. Lookup DCF from calibration.yaml (or use override)               │
│  4. CTDI_w = raw_ctdi × norm_factor × mAs × DCF                     │
│                                                                      │
│  Returns: {CTDI_w, dcf_applied, mAs_used, ...}                      │
└──────────────────────────────────────────────────────────────────────┘
```

## Risks / Trade-offs

- **[Breaking change]** Existing callers of `CTDICalculator.calculate()` expect calibrated CTDI-w. Mitigation: major version bump, clear CHANGELOG, deprecation period with warning if old metadata format detected.
- **[Old runfolders]** Runfolders with `head_calibration_factor.txt` but no `simulation_metadata.yaml` will produce un-normalized results. Mitigation: `CTDICalculator` keeps the fallback path, emitting a deprecation warning. It computes implied `total_histories` from the text file header.
- **[Statistical noise visibility]** Un-normalized raw Sum values vary with histories. Two runfolders with different history counts will show different raw Sum for the same dose. Normalization is required before comparison. Mitigation: `calculate_ctdiw.py main` defaults to applying norm_factor × mAs (but NOT DCF), so the output is in physically meaningful Gy for comparison.
- **[Workflow change]** Users who rely on `CTDICalculator` returning calibrated values need to add a `CalibrationService` step. Mitigation: `calculate_ctdiw.py main --calibrated` provides the single-command calibrated workflow.

## Migration Plan

1. **Phase 1** — Refactor `CTDICalculator` to return un-normalized output + metadata. Add `CalibrationService.normalize()`. Update `calculate_ctdiw.py` with `--calibrated` and `--dcf` flags. Update tests.
2. **Phase 2** — Update `spectrum_generator.py` to write new metadata schema. Keep backward compat reader in `_read_simulation_metadata` for old format.
3. **Phase 3** — Deprecate `dose_calibration_factor` in config. Remove dual-DCF paths.
4. **Phase 4** — Archive. Remove old fallback paths.

Rollback: revert metadata schema to combined factor, restore CTDICalculator internal multiplication. In practice, Phase 1 is the only one that changes behavior — Phases 2-4 are cleanup.

