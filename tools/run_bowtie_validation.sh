#!/usr/bin/env bash
# Phase 1 (corrected): Z-binned bow-tie profiles, wide field, 3 Full-Fan configs.
set -u
cd "$(dirname "$0")/.."
mkdir -p artifacts/bowtie_validation

declare -A CFG=(
  [tscad_ff]=configs/validate_bowtie_tscad.yaml
  [legacy_ff]=configs/validate_bowtie_legacy.yaml
  [nobtie_ff]=configs/validate_bowtie_nobtie.yaml
)

: > artifacts/bowtie_validation/manifest.tsv
echo -e "label\trunfolder\tprofile_csv" >> artifacts/bowtie_validation/manifest.tsv

for label in tscad_ff legacy_ff nobtie_ff; do
  cfg=${CFG[$label]}
  echo "=== [$label] running $cfg ==="
  log=$(uv run python run_simulation.py run "$cfg" 2>&1)
  rd=$(echo "$log" | grep -oE "runfolder/[^ ]+" | tail -1)
  if [ -z "$rd" ] || [ ! -f "$rd/bowtie_profile.csv" ]; then
    echo "[$label] FAILED"; echo "$log" | tail -5
    echo -e "$label\tFAIL\t" >> artifacts/bowtie_validation/manifest.tsv
    continue
  fi
  prof="$rd/profile.csv"
  uv run python tools/convert_bowtie_profile.py --input "$rd/bowtie_profile.csv" --output "$prof" 2>&1 | grep -i wrote
  peak=$(uv run python -c "import csv;print('%.3e'%max(float(r[1]) for r in list(csv.reader(open('$prof')))[1:]))")
  echo "[$label] OK  rd=$rd  peak=$peak"
  echo -e "$label\t$rd\t$prof" >> artifacts/bowtie_validation/manifest.tsv
done
echo "=== Phase 1 (corrected) complete ==="
cat artifacts/bowtie_validation/manifest.tsv
