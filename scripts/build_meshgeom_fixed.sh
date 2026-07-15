#!/bin/bash
# Build MeshGeom extension with Geant4 11.x MT-safe parameterization fix
# Patches TsTetGeomParameterization.hh and .cc, then rebuilds TOPAS with MeshGeom
set -e

MESHGEOM_DIR="${MESHGEOM_DIR:-$HOME/topas_meshgeom_build/TOPAS-MeshGeom}"
FIX_DIR="$(cd "$(dirname "$0")" && pwd)/meshgeom_fix"
TOPAS_SRC="${TOPAS_SRC:-$HOME/OpenTOPAS-4.0.0}"
GEANT4_DIR="${GEANT4_DIR:-$HOME/geant4-v11.1.2-install}"
INSTALL_DIR="${INSTALL_DIR:-$HOME/topas_meshgeom_fixed}"
GDCM_DIR="/opt/topas/GDCM/gdcm-install/lib/gdcm-2.6"

echo "=== Building MeshGeom with Geant4 11.x MT-safe fix ==="
echo "MeshGeom source: $MESHGEOM_DIR"
echo "Fix files:       $FIX_DIR"
echo "TOPAS source:    $TOPAS_SRC"
echo "Geant4:          $GEANT4_DIR"
echo "Install dir:     $INSTALL_DIR"
echo ""

# Verify MeshGeom source exists
if [ ! -d "$MESHGEOM_DIR/src" ]; then
    echo "ERROR: MeshGeom source not found at $MESHGEOM_DIR/src"
    echo "Clone it first: git clone https://github.com/OpenTOPAS/OpenTOPAS-MeshGeom.git $MESHGEOM_DIR"
    exit 1
fi

# Verify fix files exist
for f in TsTetGeomParameterization.hh TsTetGeomParameterization.cc; do
    if [ ! -f "$FIX_DIR/$f" ]; then
        echo "ERROR: Fix file not found: $FIX_DIR/$f"
        exit 1
    fi
done

# Backup original files and apply fix
echo "=== Patching MeshGeom source ==="
for f in TsTetGeomParameterization.hh TsTetGeomParameterization.cc; do
    SRC="$MESHGEOM_DIR/src/$f"
    BAK="$MESHGEOM_DIR/src/$f.bak"
    if [ ! -f "$BAK" ]; then
        cp "$SRC" "$BAK"
        echo "  Backed up: $f -> $f.bak"
    fi
    cp "$FIX_DIR/$f" "$SRC"
    echo "  Patched:  $f"
done

echo ""

# Try TOPAS 4.2.p3 first (the existing installation with Geant4 11.3.2)
TOPAS_42_SRC="/opt/topas/TOPAS/OpenTOPAS"
TOPAS_42_BUILD="$HOME/topas_meshgeom_fixed_build"

if [ -d "$TOPAS_42_SRC" ]; then
    echo "=== Building with TOPAS 4.2.p3 (Geant4 11.3.2) ==="
    TOPAS_SRC="$TOPAS_42_SRC"
    BUILD_DIR="$TOPAS_42_BUILD"

    # Clean build directory
    rm -rf "$BUILD_DIR"
    mkdir -p "$BUILD_DIR"
    cd "$BUILD_DIR"

    # Configure
    echo "Configuring..."
    cmake \
        -DCMAKE_INSTALL_PREFIX="$INSTALL_DIR" \
        -DCMAKE_BUILD_TYPE=Release \
        -DGeant4_DIR="/opt/topas/GEANT4/geant4-install/lib/cmake/Geant4" \
        -DGDCM_DIR="$GDCM_DIR" \
        -DTOPAS_EXTENSIONS_DIR="$MESHGEOM_DIR" \
        -DTOPAS_USE_GDML=ON \
        -DTOPAS_USE_QT=ON \
        -DTOPAS_USE_QT6=ON \
        "$TOPAS_SRC"

    # Build
    echo "Building..."
    cmake --build . -- -j$(nproc)

    # Install
    echo "Installing..."
    cmake --install .

    echo ""
    echo "=== Build complete ==="
    echo "TOPAS installed to: $INSTALL_DIR"
    echo "Binary: $INSTALL_DIR/bin/topas"
    echo ""
    echo "To test:"
    echo "  $INSTALL_DIR/bin/topas ~/test_topas_400_omeds/run_Omed.topas"
else
    echo "ERROR: TOPAS source not found at $TOPAS_42_SRC"
    exit 1
fi