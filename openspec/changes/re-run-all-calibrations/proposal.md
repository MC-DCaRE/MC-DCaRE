## Why

Current DCF values in calibration.example.yaml are based on initial calibration runs with 80M histories (80 sequential runs of 1M each). Re-running with 150M histories (150 x 1M) improves statistical precision. Two calibration entries (125 kV HF Pelvis, 140 kV FF) also lack config files entirely.

## What Changes

- Update `sequential_times: 150` in all existing calibration configs (80M -> 150M histories)
- Create new config files for 125 kV Half Fan (Pelvis) and 140 kV Full Fan calibration entries
- Run all 6 calibrations with 150M histories each
- Post-process each runfolder through `calculate_ctdiw.py` to compute raw Gy
- Benchmark each against reference CTDI-w values and write updated DCFs to calibration.example.yaml
- Update calibration.example.yaml with new dates and DCF values

## Capabilities

### New Capabilities

None — operational task, no new capabilities introduced.

### Modified Capabilities

None — no spec-level requirement changes.

## Impact

- `configs/cal_*.yaml`: 4 existing configs updated (sequential_times: 80 -> 150)
- `configs/cal_125kv_hf_pelvis.yaml`: new config file
- `configs/cal_140kv_ff.yaml`: new config file
- `calibration.example.yaml`: DCF values updated with new dates
