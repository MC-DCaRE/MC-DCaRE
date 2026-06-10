# Spec: Simulation Metadata

## Capability

Capture full simulation provenance in a structured YAML file for reconstruction and post-hoc calibration.

## ADDED Requirements

### CAL-META-001: simulation_metadata.yaml schema
Written to `tmp/` by SpectrumGenerator, copied to runfolder by `copy_common_files()`.

Fields:
- `norm_factor` (float) — per-mAs normalization: `4πr² × fluence(1 mAs, kV) / N_total`
- `mAs` (float) — simulation mAs
- `total_histories` (int) — `sequential_times × histories`
- `dcf_used` (float) — always 1.0 (post-hoc calibration)
- `spekpy` (dict):
  - `kvp` (float)
  - `th` (float) — anode angle in degrees
  - `dk` (float) — keV energy bin width
  - `z` (float) — focus-to-reference distance in cm
  - `mas` (float)
  - `version` (str) — SpekPy version string
- `fan_mode` (str) — "Full Fan" or "Half Fan"
- `seed` (int)
- `threads` (int)
- `timestamp` (str) — ISO 8601

**norm_factor computation algorithm**: SpekPy fluence is linear in mAs (confirmed at machine precision). Current code computes `combined_factor = 4πr² × fluence(kV, mAs) / N_total × DCF`. To decompose: `norm_factor = combined_factor / mAs` (with DCF=1.0). Equivalently, run SpekPy at the given mAs, get fluence, compute `4πr² × fluence / (N_total × mAs)`. Both yield the same result.

### CAL-META-002: Backward-compatible head_calibration_factor.txt
- Continue writing `head_calibration_factor.txt` with existing format
- Contains combined factor: `norm_factor × mAs × dcf_used`
- Ensures existing runfolders work with current CTDICalculator

### CAL-META-003: CTDICalculator reader
- Try reading `simulation_metadata.yaml` first
- Fall back to `head_calibration_factor.txt` if metadata file not found
- No behavior change for existing runfolders

### CAL-META-004: SpectrumGenerator parameter changes
- `fan_mode`, `seed`, and `threads` must be passed to `SpectrumGenerator.generate()` to include in metadata
- Currently `SpectrumGenerator` only receives `(anode_voltage, exposure, histories, project_root, dose_calibration_factor)` — add `fan_mode: str`, `seed: int`, `threads: int`
- Alternatively, accept a config object or subset to avoid signature bloat
