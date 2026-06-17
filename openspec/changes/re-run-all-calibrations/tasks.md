## 1. Create Missing Calibration Config Files

- [x] 1.1 Create `configs/cal_125kv_hf_pelvis.yaml` — 125 kV Half Fan (Pelvis), sequential_times: 150
- [x] 1.2 Create `configs/cal_140kv_ff.yaml` — 140 kV Full Fan (no reference protocol), sequential_times: 150

## 2. Update Existing Config Files

- [x] 2.1 Update `configs/cal_80kv_ff_image-gently.yaml` — sequential_times: 80 -> 150
- [x] 2.2 Update `configs/cal_100kv_ff_head.yaml` — sequential_times: 80 -> 150
- [x] 2.3 Update `configs/cal_125kv_ff_pelvis-spotlight.yaml` — sequential_times: 80 -> 150
- [x] 2.4 Update `configs/cal_140kv_hf_pelvis-large.yaml` — sequential_times: 80 -> 150

> Config changes done. Simulation execution delegated to `configs/run_all_calibrations.sh`.
> Run it with: `bash configs/run_all_calibrations.sh`

## 3. Run 80 kV Full Fan (Image Gently) Calibration

- [ ] 3.1 Execute: `uv run python run_simulation.py run configs/cal_80kv_ff_image-gently.yaml`
- [ ] 3.2 Post-process: `uv run python calculate_ctdiw.py main <runfolder>`
- [ ] 3.3 Benchmark: `uv run python calculate_ctdiw.py benchmark <runfolder> --reference 0.9 --kV 80 --fan-mode "Full Fan" --calibration-yaml calibration.example.yaml`

## 4. Run 100 kV Full Fan (Head) Calibration

- [ ] 4.1 Execute: `uv run python run_simulation.py run configs/cal_100kv_ff_head.yaml`
- [ ] 4.2 Post-process: `uv run python calculate_ctdiw.py main <runfolder>`
- [ ] 4.3 Benchmark: `uv run python calculate_ctdiw.py benchmark <runfolder> --reference 3.2 --kV 100 --fan-mode "Full Fan" --calibration-yaml calibration.example.yaml`

## 5. Run 125 kV Full Fan (Pelvis Spotlight) Calibration

- [ ] 5.1 Execute: `uv run python run_simulation.py run configs/cal_125kv_ff_pelvis-spotlight.yaml`
- [ ] 5.2 Post-process: `uv run python calculate_ctdiw.py main <runfolder>`
- [ ] 5.3 Benchmark: `uv run python calculate_ctdiw.py benchmark <runfolder> --reference 43.93 --kV 125 --fan-mode "Full Fan" --calibration-yaml calibration.example.yaml`

## 6. Run 125 kV Half Fan (Pelvis) Calibration

- [ ] 6.1 Execute: `uv run python run_simulation.py run configs/cal_125kv_hf_pelvis.yaml`
- [ ] 6.2 Post-process: `uv run python calculate_ctdiw.py main <runfolder>`
- [ ] 6.3 Benchmark: `uv run python calculate_ctdiw.py benchmark <runfolder> --reference 15.9 --kV 125 --fan-mode "Half Fan" --calibration-yaml calibration.example.yaml`

## 7. Run 140 kV Half Fan (Pelvis Large) Calibration

- [ ] 7.1 Execute: `uv run python run_simulation.py run configs/cal_140kv_hf_pelvis-large.yaml`
- [ ] 7.2 Post-process: `uv run python calculate_ctdiw.py main <runfolder>`
- [ ] 7.3 Benchmark: `uv run python calculate_ctdiw.py benchmark <runfolder> --reference 37.1 --kV 140 --fan-mode "Half Fan" --calibration-yaml calibration.example.yaml`

## 8. Run 140 kV Full Fan Calibration

- [ ] 8.1 Execute: `uv run python run_simulation.py run configs/cal_140kv_ff.yaml`
- [ ] 8.2 Post-process: `uv run python calculate_ctdiw.py main <runfolder>`
- [ ] 8.3 Review raw Gy output (no reference CTDI-w available — benchmark skipped)

## 9. Finalize

- [ ] 9.1 Verify all 6 DCFs in calibration.example.yaml updated with new values and dates
- [ ] 9.2 Commit and push all config changes and updated calibration.example.yaml
