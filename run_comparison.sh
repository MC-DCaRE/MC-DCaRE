#!/bin/bash
# Run legacy / new / old bow-tie at 5M histories each. Top-level uv (no nested
# uv). All temp files in-workspace. Restores tracked files at the end.
set -u
cd /home/bchcphysics/Github/MC-DCaRE
BK=.cmp_backup
mkdir -p "$BK"

BOWTIE=src/boilerplates/TOPAS_includeFiles/bowtie_ff.txt
HEAD=src/boilerplates/headsourcecode_boilerplate.j2

# Backups + prepared variants
cp "$BOWTIE" "$BK/bowtie_new.txt"
cp "$HEAD" "$BK/head_orig.j2"
sed '/^includeFile=ConvertedTopasFile.txt/a b:Ge/QuitIfOverlapDetected = "False"' "$HEAD" > "$BK/head_quit.j2"
cat > "$BK/bowtie_old.txt" <<'EOF'
s:Ge/BowtieFilter/Type = "TsCAD"
s:Ge/BowtieFilter/Parent = "CollimatorsHorizontal"
s:Ge/BowtieFilter/Material = "G4_Al"
s:Ge/BowtieFilter/InputFile = "fullfan"
s:Ge/BowtieFilter/FileFormat = "stl"
d:Ge/BowtieFilter/Units = 1.0 mm
d:Ge/BowtieFilter/TransX = 0.0 mm
d:Ge/BowtieFilter/TransY = 0.0 mm
d:Ge/BowtieFilter/TransZ = 38.5 mm
d:Ge/BowtieFilter/RotX = 0. deg
d:Ge/BowtieFilter/RotY = 0. deg
dc:Ge/BowtieFilter/RotZ = -90. deg
s:Ge/BowtieFilter/DrawingStyle = "Wireframe"
EOF

# Install head with QuitIfOverlapDetected=False for all three runs
cp "$BK/head_quit.j2" "$HEAD"

echo "=== RUN 1/3: LEGACY (CSG) ==="
uv run python run_simulation.py run configs/cmp_legacy_5m.yaml 2>&1 | grep -iE "completed in" | tail -1
echo "=== RUN 2/3: NEW (TsCAD Rotation 18cm) ==="
uv run python run_simulation.py run configs/cmp_tscad_5m.yaml 2>&1 | grep -iE "completed in" | tail -1
echo "=== RUN 3/3: OLD (TsCAD collimator bay) ==="
cp "$BK/bowtie_old.txt" "$BOWTIE"
uv run python run_simulation.py run configs/cmp_tscad_5m.yaml 2>&1 | grep -iE "completed in" | tail -1

# Restore
cp "$BK/bowtie_new.txt" "$BOWTIE"
cp "$BK/head_orig.j2" "$HEAD"
echo "=== RESTORED bowtie_ff.txt + head template ==="
echo "=== Three newest runfolders (oldest->newest = legacy, new, old): ==="
ls -dt runfolder/2026-* | head -3 | tac
echo "CMP_DONE"
