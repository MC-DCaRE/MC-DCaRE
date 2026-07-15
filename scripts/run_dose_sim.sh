#!/bin/bash
# Run dose simulation with voxelized phantom
# Usage: ./run_dose_sim.sh <topas_file> <label>

set -e

TOPAS="/opt/topas/TOPAS/OpenTOPAS-install/bin/topas"
DIR="$(cd "$(dirname "$1")" && pwd)"
FILE="$(basename "$1")"
LABEL="${2:-dose}"

cd "$DIR"

echo "=== Running dose simulation: $LABEL ==="
echo "TOPAS file: $FILE"
echo ""

timeout 300 "$TOPAS" "$FILE" 2>&1 | tee "${LABEL}.log" | tail -30

echo ""
echo "=== Output files ==="
ls -lh *.csv 2>/dev/null || echo "No CSV files"

# Check dose results
for csv in phantom_dose.csv PhantomDose.csv; do
    if [ -f "$csv" ]; then
        echo ""
        echo "=== $csv ==="
        head -5 "$csv"
        echo "..."
        # Count non-zero dose entries
        total=$(wc -l < "$csv")
        nonzero=$(awk -F, 'NR>1 && $2+0 > 0 {count++} END {print count+0}' "$csv")
        echo "Total rows: $total"
        echo "Non-zero dose: $nonzero"
    fi
done