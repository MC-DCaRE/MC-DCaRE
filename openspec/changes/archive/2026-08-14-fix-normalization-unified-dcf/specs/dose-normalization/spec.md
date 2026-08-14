## Purpose

Defines how raw TOPAS scorer output is converted to absolute dose (Gy), ensuring that the Dose Calibration Factor (DCF) derived from CTDI phantom measurements transfers correctly to body phantom organ dose calculations, regardless of whether the simulation uses a direct beam source or a phase space replay source.

## ADDED Requirements

### Requirement: photons_per_mAs must use scoring-run N_scoring, not current total_histories

The `photons_per_mAs` normalization constant must be computed as `spectrum_fluence × N_scoring / exposure_mAs`, where `N_scoring` is the `total_histories` from the scoring run metadata (a fixed property of the beam model). It must NOT use the current simulation's `total_histories`, which varies by source type (direct beam: R × histories_per_run, phase space replay: N_phsp × M × R).

#### Scenario: CTDI calibration with 36 sequential times
- **WHEN** a CTDI calibration runs with sequential_times=36 and histories_per_run=5M (total 180M)
- **AND** the scoring run used N_scoring=5M
- **THEN** `photons_per_mAs` must equal `spectrum_fluence × 5M / exposure_mAs`
- **AND** must NOT equal `spectrum_fluence × 180M / exposure_mAs`

#### Scenario: Phase space replay with M=5, R=36
- **WHEN** a replay runs with M=5, R=36 (total scorer histories = N_phsp × 5 × 36)
- **THEN** `photons_per_mAs` must still equal `spectrum_fluence × 5M / exposure_mAs` (same constant)

### Requirement: raw_absolute_dose_Gy must use actual scorer-active histories

The absolute dose formula must use `N_scorer_active_histories` (the actual number of histories the TOPAS scorer accumulated over, as reported in the CSV `Histories_with_Scorer_Active` column) instead of `total_histories` from metadata. The formula must be:

```
absolute_Gy = (raw_sum / N_scorer_active_histories) × photons_per_mAs × mAs_used
```

#### Scenario: Direct beam CTDI with 36 angles
- **WHEN** the scorer reports 180M active histories
- **AND** raw_sum is the mean dose per Z-bin
- **THEN** absolute dose must equal `raw_sum × sf × N_scoring / 180M`

#### Scenario: Phase space replay with M=5, R=36
- **WHEN** the scorer reports N_phsp × 5 × 36 active histories
- **THEN** absolute dose must equal `raw_sum × sf × N_scoring / (N_phsp × M × R)`
- **AND** must be independent of M and R (they cancel because raw_sum scales linearly with M and R)

### Requirement: DCF must transfer between CTDI and phantom simulations

The DCF computed from CTDI calibration (`DCF = measured_CTDIw / absolute_ctdi`) must produce correct absolute organ dose when applied to phantom simulation results, without requiring a separate reference-derived calibration factor.

#### Scenario: DCF applied to phantom dose
- **GIVEN** DCF computed from CTDI calibration using the same beam line and rotation parameters
- **WHEN** DCF is applied to phantom organ dose computed with phase space replay
- **THEN** the calibrated organ doses must be physically reasonable (within 3× of literature values for the same protocol)
- **AND** the effective dose must be within the expected range for the protocol (not 100× off)

### Requirement: Replay metadata must not divide spectrum_fluence by M×R

The `_write_replay_metadata` function must NOT divide `spectrum_fluence_photons_per_mAs` by `phase_space_multiple_use × sequential_times`. The M×R scaling is now handled naturally by `N_scorer_active_histories` in the normalization formula.

#### Scenario: Replay metadata preserved unchanged
- **WHEN** replay metadata is written for M=5, R=36
- **THEN** `spectrum_fluence_photons_per_mAs` must equal the scoring run's value (unchanged)
- **AND** `total_histories` must equal the scoring run's value (unchanged)
- **AND** `phase_space_multiple_use` and `phase_space_sequential_times` must be recorded for reference
