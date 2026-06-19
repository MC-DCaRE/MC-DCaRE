#!/bin/bash
# =====================================================================
# build_meshgeom.sh — Build OpenTOPAS-MeshGeom extension
# =====================================================================
# Rebuilds TOPAS 4.2.p3 with the MeshGeom extension (TsTetGeom component)
# alongside the existing nBio extension. Installs to user space so the
# system TOPAS is untouched.
#
# Prerequisites:
#   - OpenTOPAS 4.2.p3 installed at /opt/topas/TOPAS/
#   - Geant4 at /opt/topas/GEANT4/
#   - GDCM at /opt/topas/GDCM/
#   - cmake >= 3.16, gcc/g++ >= 9
#
# Usage:
#   chmod +x scripts/build_meshgeom.sh
#   ./scripts/build_meshgeom.sh
#
# After a successful build, update your simulation config YAML:
#   general:
#     topas_directory: "$HOME/topas_meshgeom_install/bin"
# =====================================================================

set -euo pipefail

# ---- Configuration (from existing cmake cache) ----------------------
OPEN_TOPAS_SRC="/opt/topas/TOPAS/OpenTOPAS"
GEANT4_DIR="/opt/topas/GEANT4/geant4-install/lib/cmake/Geant4"
GDCM_DIR="/opt/topas/GDCM/gdcm-install/lib/gdcm-2.6"
NBIO_EXT="/opt/topas/extensions/TOPAS-nBio"

# ---- User-writable paths --------------------------------------------
WORK_DIR="${HOME}/topas_meshgeom_build"
MESHGEOM_REPO="https://github.com/OpenTOPAS/OpenTOPAS-MeshGeom.git"
MESHGEOM_DIR="${WORK_DIR}/TOPAS-MeshGeom"
EXTENSIONS_DIR="${WORK_DIR}/extensions"
BUILD_DIR="${WORK_DIR}/build"
INSTALL_DIR="${HOME}/topas_meshgeom_install"

# ---- Helpers --------------------------------------------------------
log()  { echo -e "\033[1;34m[build]\033[0m $*"; }
ok()   { echo -e "\033[1;32m  OK\033[0m"; }
fail() { echo -e "\033[1;31m  FAILED: $*\033[0m"; exit 1; }

# ---- Step 1: Clone MeshGeom -----------------------------------------
log "Step 1/6: Clone OpenTOPAS-MeshGeom"
if [ -d "$MESHGEOM_DIR/.git" ]; then
    log "  Already cloned, pulling latest..."
    git -C "$MESHGEOM_DIR" pull --rebase || fail "git pull failed"
else
    git clone "$MESHGEOM_REPO" "$MESHGEOM_DIR" || fail "git clone failed"
fi
ok

# ---- Step 2: Set up extensions directory ----------------------------
log "Step 2/6: Set up extensions directory (nBio + MeshGeom)"
mkdir -p "$EXTENSIONS_DIR"
ln -sfn "$NBIO_EXT"      "$EXTENSIONS_DIR/TOPAS-nBio"
ln -sfn "$MESHGEOM_DIR"  "$EXTENSIONS_DIR/TOPAS-MeshGeom"
log "  Extensions:"
ls -1 "$EXTENSIONS_DIR/" | sed 's/^/    /'
ok

# ---- Step 3: cmake --------------------------------------------------
log "Step 3/6: Run cmake"
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"
cmake \
    -DTOPAS_TYPE="expanded" \
    -DGeant4_DIR="$GEANT4_DIR" \
    -DGDCM_DIR="$GDCM_DIR" \
    -DTOPAS_EXTENSIONS_DIR="$EXTENSIONS_DIR" \
    -DCMAKE_INSTALL_PREFIX="$INSTALL_DIR" \
    -B "$BUILD_DIR" \
    -S "$OPEN_TOPAS_SRC" \
    || fail "cmake configuration failed"
ok

# ---- Step 4: Build --------------------------------------------------
log "Step 4/6: Build (this takes 10-20 minutes)"
NPROC=$(nproc 2>/dev/null || echo 4)
log "  Using ${NPROC} parallel jobs"
make -C "$BUILD_DIR" -j"$NPROC" || fail "make failed"
ok

# ---- Step 5: Install ------------------------------------------------
log "Step 5/6: Install to ${INSTALL_DIR}"
make -C "$BUILD_DIR" install || fail "make install failed"
ok

# ---- Step 6: Verify TsTetGeom --------------------------------------
log "Step 6/6: Verify TsTetGeom registration"

TOPAS_BIN="${INSTALL_DIR}/bin/topas"
[ -x "$TOPAS_BIN" ] || fail "TOPAS binary not found at ${TOPAS_BIN}"

log "  TOPAS version:"
"$TOPAS_BIN" --version 2>&1 | sed 's/^/    /'

# Create a minimal test parameter file
TEST_FILE="${WORK_DIR}/test_tetgeom.txt"
mkdir -p "$WORK_DIR"
cat > "$TEST_FILE" << 'PARAM'
# Minimal TsTetGeom smoke test
s:Ge/World/HLX = 1.0 m
s:Ge/World/HLY = 1.0 m
s:Ge/World/HLZ = 1.0 m
s:Ge/World/Material = "Vacuum"

s:Ge/TestPhantom/Type = "TsTetGeom"
s:Ge/TestPhantom/Parent = "World"
s:Ge/TestPhantom/Material = "G4_WATER"

i:Ts/NumberOfThreads = 1
i:Ts/Seed = 42
b:Ts/PauseBeforeQuit = "False"
i:Ts/ShowHistoryCountAtInterval = 100
PARAM

log "  Running smoke test..."
OUTPUT=$("$TOPAS_BIN" "$TEST_FILE" 2>&1 || true)

if echo "$OUTPUT" | grep -qi "unknown\|unrecognized\|not found\|cannot find"; then
    echo "$OUTPUT" | head -30
    fail "TsTetGeom not recognized. Check that the MeshGeom extension compiled correctly."
fi

ok
echo ""
log "================================================================"
log "  Build successful!"
log "  TOPAS binary: ${TOPAS_BIN}"
log ""
log "  Update your simulation config:"
log "    general:"
log "      topas_directory: ${INSTALL_DIR}/bin"
log "================================================================"
