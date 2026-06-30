#!/bin/bash
# Render all RayTracer visualizations for a given fan mode directory
# Usage: ./render_all.sh <dir> [topas_binary]

set -e

DIR="${1:-.}"
TOPAS="${2:-/opt/topas/TOPAS/OpenTOPAS-install/bin/topas}"

cd "$DIR"

echo "Rendering from: $(pwd)"
echo "TOPAS: $TOPAS"
echo ""

count=0
for topas_file in beamhead_angle_*.topas vis_angle_*.topas; do
    [ -f "$topas_file" ] || continue

    echo "=== Rendering: $topas_file ==="

    # Run TOPAS (captures all 4 viewer outputs)
    timeout 120 "$TOPAS" "$topas_file" 2>&1 | grep -E "(RayTracer|Error)" || true

    # Rename viewer outputs: viewer-0=front, 1=side, 2=top, 3=iso
    base="${topas_file%.topas}"
    views=("front" "side" "top" "iso")
    for i in 0 1 2 3; do
        src="g4RayTracer.viewer-${i}_0000.jpeg"
        dst="${base}_${views[$i]}.jpeg"
        if [ -f "$src" ]; then
            mv "$src" "$dst"
            echo "  -> $dst"
            count=$((count + 1))
        fi
    done
    echo ""
done

echo "Done! Rendered $count images in $(pwd)"
ls -lh *.jpeg