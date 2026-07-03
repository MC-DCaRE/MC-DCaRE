#!/usr/bin/env bash
set -euo pipefail

#
# Run all 6 MC-DCaRE calibrations sequentially (500M histories each)
#
# Usage:
#   bash configs/run_all_calibrations.sh
#
# Each simulation produces a runfolder. This script extracts the
# runfolder path from the output, then post-processes and benchmarks.
#
# Configs run:
#   1.  80 kV Full Fan (Image Gently)
#   2. 100 kV Full Fan (Head)
#   3. 125 kV Full Fan (Pelvis Spotlight)
#   4. 125 kV Half Fan (Pelvis)
#   5. 140 kV Half Fan (Pelvis Large)
#   6. 140 kV Full Fan (no reference)
#

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$SCRIPT_DIR"

CAL_YAML="calibration.example.yaml"
LOGFILE="run_all_calibrations.log"

# Calibration definitions: config reference_ctdiw_mGy kV fan_mode
CALIBRATIONS=(
  "configs/cal_80kv_ff_image-gently.yaml:0.9:80:Full Fan"
  "configs/cal_100kv_ff_head.yaml:3.2:100:Full Fan"
  "configs/cal_125kv_ff_pelvis-spotlight.yaml:12.3:125:Full Fan"
  "configs/cal_125kv_hf_pelvis.yaml:15.9:125:Half Fan"
  "configs/cal_140kv_hf_pelvis-large.yaml:37.1:140:Half Fan"
  "configs/cal_140kv_ff.yaml:NONE:140:Full Fan"
)

run_one() {
  local config="$1"
  local reference="$2"
  local kv="$3"
  local fan_mode="$4"
  local label

  label="$(basename "$config" .yaml)"
  echo ""
  echo "=============================================="
  echo "  ${label}"
  echo "=============================================="

  # Step 1: Run simulation
  echo "[$(date '+%H:%M:%S')] Running ${label} ..."
  local rundir
  rundir=$(uv run python run_simulation.py run "$config" | tee /dev/stderr | grep -oP 'Simulation (completed|detached) in \K.*')
  if [ -z "$rundir" ]; then
    echo "ERROR: could not extract runfolder from simulation output" >&2
    return 1
  fi
  echo "[$(date '+%H:%M:%S')] Runfolder: ${rundir}"

  # Step 2: Post-process
  echo "[$(date '+%H:%M:%S')] Post-processing ${label} ..."
  uv run python calculate_ctdiw.py main "$rundir" --output "${rundir}/CTDIw_results.csv"

  # Step 3: Benchmark
  if [ "$reference" = "NONE" ]; then
    echo "[$(date '+%H:%M:%S')] No reference CTDI-w available — skipping benchmark"
  else
    echo "[$(date '+%H:%M:%S')] Benchmarking ${label} (ref=${reference} mSv) ..."
    uv run python calculate_ctdiw.py benchmark "$rundir" \
      --reference "$reference" \
      --kV "$kv" \
      --fan-mode "$fan_mode" \
      --calibration-yaml "$CAL_YAML" || \
      echo "[$(date '+%H:%M:%S')] Benchmark comparison FAILED (expected for uncalibrated run) — DCF still written"
  fi
}

total=${#CALIBRATIONS[@]}
count=0
for entry in "${CALIBRATIONS[@]}"; do
  IFS=':' read -r config reference kv fan_mode <<<"$entry"
  count=$((count + 1))
  echo ""
  echo "==== [$count/$total] Starting $(basename "$config" .yaml) ===="
  if ! run_one "$config" "$reference" "$kv" "$fan_mode" 2>&1 | tee -a "$LOGFILE"; then
    echo "FAILED: $(basename "$config" .yaml)" | tee -a "$LOGFILE"
    echo "Check ${LOGFILE} for details." >&2
    exit 1
  fi
done

echo ""
echo "=============================================="
echo "  ALL CALIBRATIONS COMPLETE"
echo "=============================================="
echo "Log: ${LOGFILE}"
echo ""
echo "Verify calibration.example.yaml has updated DCFs, then commit."
