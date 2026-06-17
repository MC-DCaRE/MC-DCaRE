## Context

The calibration pipeline consists of:
1. YAML config files in `configs/` defining simulation parameters (kV, fan_mode, imaging_mode, sequential_times, etc.)
2. `run_simulation.py` which reads a config and executes the TOPAS simulation
3. `calculate_ctdiw.py main` which post-processes runfolder CSV output into raw Gy
4. `calculate_ctdiw.py benchmark` which compares simulated raw Gy against reference CTDI-w and writes DCF to calibration.yaml

Current state: 4 config files exist, 2 calibrations lack configs. All existing configs use `sequential_times: 80` (80M histories). Calibration configs have `histories: 1000000` (1M per sequential run).

The 6 calibrations to run are:

| kV | Fan Mode | Protocol | Config | Reference CTDI-w (mGy) | Reference mAs |
|----|----------|----------|--------|----------------------|--------------|
| 80 | Full Fan | Image Gently | cal_80kv_ff_image-gently.yaml | 0.9 | 100.0 |
| 100 | Full Fan | Head | cal_100kv_ff_head.yaml | 3.2 | 150.0 |
| 125 | Full Fan | Short Thorax | cal_125kv_ff_pelvis-spotlight.yaml | 43.93 | 750.0 |
| 125 | Half Fan | Pelvis | (new) | 15.9 | 1080.0 |
| 140 | Full Fan | (no protocol) | (new) | N/A | N/A |
| 140 | Half Fan | Pelvis Large | cal_140kv_hf_pelvis-large.yaml | 37.1 | 1700.5 |

Note: 140 kV FF has no reference CTDI-w — benchmark will be skipped for this entry.

## Goals / Non-Goals

**Goals:**
- Run all 6 calibrations with 150M histories each
- Create config files for the 2 missing calibrations
- Post-process results and update calibration.example.yaml with new DCFs

**Non-Goals:**
- No code changes to the pipeline itself
- No new imaging mode definitions
- No cross-validation runs

## Decisions

1. **150 sequential runs of 1M each**: Configs set `sequential_times: 150` with `histories: 1,000,000` — matches existing pattern, just scaled up.
2. **125 kV FF uses Pelvis Spotlight config**: The existing `cal_125kv_ff_pelvis-spotlight.yaml` uses Pelvis Spotlight imaging mode. The calibration entry references Short Thorax with 750 mAs reference. This config already exists and was used for prior calibration — reuse it.
3. **125 kV HF Pelvis config**: Based on `cal_140kv_hf_pelvis-large.yaml` pattern but with Pelvis imaging mode, 1080 mAs exposure.
4. **140 kV FF config**: No reference protocol/mAs available — run a scan with a reasonable default (e.g., Head or Pelvis mode) for measurement only. DCF will remain null in calibration.yaml.
5. **Sequential execution order**: Run by increasing kV for independence. Each calibration is independent.
6. **Benchmark writes DCF directly**: Use `calculate_ctdiw.py benchmark --kV X --fan-mode "Half Fan" --reference Y --calibration-yaml calibration.example.yaml` to write computed DCF to the YAML file.

## Risks / Trade-offs

- [Long runtime] 6 calibrations x 150M histories at 20 threads each → ~XX hours total. Each calibration takes approximately the same time as 150 individual TOPAS runs.
- [Disk space] Each runfolder with 150M histories will be large. Ensure adequate storage.
- [140 kV FF no reference] This calibration cannot produce a DCF (no reference CTDI-w). Runs for completeness / future use only.
- [125 kV FF config mismatch] The Pelvis Spotlight config may use different blade settings than Short Thorax. Verify consistency or document the difference.
