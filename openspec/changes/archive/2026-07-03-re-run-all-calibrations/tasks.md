## 1. Create Missing Calibration Config Files

- [x] 1.1 Create `configs/cal_125kv_hf_pelvis.yaml` — 125 kV Half Fan (Pelvis), sequential_times: 150
- [x] 1.2 Create `configs/cal_140kv_ff.yaml` — 140 kV Full Fan (no reference protocol), sequential_times: 150

## 2. Update Existing Config Files

- [x] 2.1 Update `configs/cal_80kv_ff_image-gently.yaml` — histories/sequential_times -> 500M (5000000 x 100)
- [x] 2.2 Update `configs/cal_100kv_ff_head.yaml` — histories/sequential_times -> 500M (5000000 x 100)
- [x] 2.3 Update `configs/cal_125kv_ff_pelvis-spotlight.yaml` — histories/sequential_times -> 500M (5000000 x 100)
- [x] 2.4 Update `configs/cal_140kv_hf_pelvis-large.yaml` — histories/sequential_times -> 500M (5000000 x 100)

> Config changes done. Simulation execution delegated to `configs/run_all_calibrations.sh`.
> Run it with: `bash configs/run_all_calibrations.sh`
>
> UPDATE: Plan revised to 500M histories per calibration (histories: 5000000,
> sequential_times: 100) for better statistics. Runfolders live in
> `calibration_runs/`. Post-processing/benchmarking run via `calculate_ctdiw.py`.

## 3. Run 80 kV Full Fan (Image Gently) Calibration

- [x] 3.1 Execute: `uv run python run_simulation.py run configs/cal_80kv_ff_image-gently.yaml` — RE-RUN completed runfolder/2026-07-03_10-02-04 (original 500M data was lost; see note below)
- [x] 3.2 Post-process: `uv run python calculate_ctdiw.py main <runfolder>` — CTDIw_results.csv written (tle raw_Gy=4.193768e+08)
- [x] 3.3 Benchmark: `uv run python calculate_ctdiw.py benchmark <runfolder> --reference 0.9 --kV 80 --fan-mode "Full Fan" --calibration-yaml calibration.example.yaml` — dcf_tle=1.073021e-03

> NOTE: The original completed 80 kV 500M runfolder was inadvertently deleted
> before post-processing; `calibration_runs/` is gitignored so it was
> unrecoverable. A fresh 80 kV 500M run was launched 2026-07-03.

## 4. Run 100 kV Full Fan (Head) Calibration

- [x] 4.1 Execute: `uv run python run_simulation.py run configs/cal_100kv_ff_head.yaml` — calibration_runs/2026-07-01_08-58-38
- [x] 4.2 Post-process: `uv run python calculate_ctdiw.py main <runfolder>` — CTDIw_results.csv written
- [x] 4.3 Benchmark: `uv run python calculate_ctdiw.py benchmark <runfolder> --reference 3.2 --kV 100 --fan-mode "Full Fan" --calibration-yaml calibration.example.yaml` — dcf_tle=1.196358e-03

## 5. Run 125 kV Full Fan (Pelvis Spotlight) Calibration

- [x] 5.1 Execute: `uv run python run_simulation.py run configs/cal_125kv_ff_pelvis-spotlight.yaml` — calibration_runs/2026-07-01_12-57-27
- [x] 5.2 Post-process: `uv run python calculate_ctdiw.py main <runfolder>` — CTDIw_results.csv written
- [x] 5.3 Benchmark: `uv run python calculate_ctdiw.py benchmark <runfolder> --reference 12.3 --kV 125 --fan-mode "Full Fan" --calibration-yaml calibration.example.yaml` — dcf_tle=1.233986e-03 (reference 12.3 mGy per committed calibration data; design.md's 43.93 was stale)

## 6. Run 125 kV Half Fan (Pelvis) Calibration

- [x] 6.1 Execute: `uv run python run_simulation.py run configs/cal_125kv_hf_pelvis.yaml` — calibration_runs/2026-07-01_16-43-50
- [x] 6.2 Post-process: `uv run python calculate_ctdiw.py main <runfolder>` — CTDIw_results.csv written
- [x] 6.3 Benchmark: `uv run python calculate_ctdiw.py benchmark <runfolder> --reference 15.9 --kV 125 --fan-mode "Half Fan" --calibration-yaml calibration.example.yaml` — dcf_tle=1.633637e-03

## 7. Run 140 kV Half Fan (Pelvis Large) Calibration

- [x] 7.1 Execute: `uv run python run_simulation.py run configs/cal_140kv_hf_pelvis-large.yaml` — calibration_runs/2026-07-02_00-21-56
- [x] 7.2 Post-process: `uv run python calculate_ctdiw.py main <runfolder>` — CTDIw_results.csv written
- [x] 7.3 Benchmark: `uv run python calculate_ctdiw.py benchmark <runfolder> --reference 37.1 --kV 140 --fan-mode "Half Fan" --calibration-yaml calibration.example.yaml` — dcf_tle=1.796979e-03

## 8. Run 140 kV Full Fan Calibration

- [x] 8.1 Execute: `uv run python run_simulation.py run configs/cal_140kv_ff.yaml` — calibration_runs/2026-07-01_20-35-24
- [x] 8.2 Post-process: `uv run python calculate_ctdiw.py main <runfolder>` — CTDIw_results.csv written (tle raw_Gy=3.398974e+09)
- [x] 8.3 Review raw Gy output (no reference CTDI-w available — benchmark skipped) — dcf remains null by design

## 9. Finalize

- [x] 9.1 Verify all 6 DCFs in calibration.example.yaml updated with new values and dates — 5 DCFs populated (80/100/125FF/125HF/140HF), 140FF null by design; all dated 2026-07-03; validated via MachineCalibration.from_yaml
- [x] 9.2 Commit and push all config changes and updated calibration.example.yaml — commit 027accb (500M DCFs) + 34ed380 (icrp145 archive) pushed to origin/main
