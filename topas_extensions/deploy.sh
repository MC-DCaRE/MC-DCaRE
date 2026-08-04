#!/usr/bin/env bash
# deploy.sh -- build & install the TrackDumper diagnostic scorer as a TOPAS
# extension, then smoke-test it.
#
# Run from a shell with write access to /opt/topas (your terminal, not the
# opencode sandbox). Idempotent.
#
#   cd <repo>/topas_extensions && sudo ./deploy.sh
#
# Overrides:
#   TOPAS_SRC=/path/to/OpenTOPAS TOPAS_BUILD=/path/to/build \
#   TOPAS_EXT=/path/to/extensions  TOPAS_BIN=/path/to/topas  ./deploy.sh
#
# IMPORTANT: the scorer must live in the EXTENSIONS dir (cmake scans it for
# `// Scorer for X` comments and auto-registers). It must NOT go in the core
# OpenTOPAS/scoring/ dir -- that dir's scorers are hardcoded in the core
# factory and the comment scan does not cover it.
set -euo pipefail

TOPAS_SRC="${TOPAS_SRC:-/opt/topas/TOPAS/OpenTOPAS}"
TOPAS_BUILD="${TOPAS_BUILD:-/opt/topas/TOPAS/OpenTOPAS-build}"
TOPAS_BIN="${TOPAS_BIN:-/opt/topas/TOPAS/OpenTOPAS-install/bin/topas}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> 1/5  Locating the scanned TOPAS extensions scorers directory"
# The build's cmake scans a configured extensions dir. From the scan output it
# finds /opt/topas/extensions/TOPAS-nBio (so the configured dir is nBio, not
# the parent -- a sibling MC-DCaRE/ dir is NOT scanned). The reliable spot is
# nBio's own scorers dir, which the scan confirms it globs recursively.
NBIODIR="$(find /opt/topas/extensions -maxdepth 1 -type d -name 'TOPAS-nBio' 2>/dev/null | head -1)"
if [ -z "$NBIODIR" ] || [ ! -d "$NBIODIR/scorers" ]; then
    echo "ERROR: could not find /opt/topas/extensions/TOPAS-nBio/scorers." >&2
    echo "       Set TOPAS_EXT to your scanned extensions dir and adjust." >&2
    exit 1
fi
MY_EXT_DIR="$NBIODIR/scorers"
echo "    Staging scorer in: $MY_EXT_DIR"

echo "==> 2/5  Staging TsTrackDumper.cc/.hh (and cleaning up prior attempts)"
install -m 0644 "$HERE/TsTrackDumper.cc" "$MY_EXT_DIR/"
install -m 0644 "$HERE/TsTrackDumper.hh" "$MY_EXT_DIR/"
# Clean up an earlier deploy's stale copies.
rm -f "$TOPAS_SRC/scoring/TsTrackDumper.cc"
rm -rf /opt/topas/extensions/MC-DCaRE

echo "==> 3/5  Reconfiguring cmake (force re-scan of extensions for 'Scorer for' comments)"
cd "$TOPAS_BUILD"
# CMake's file(GLOB ...) does not detect newly added source files on an
# incremental `cmake .`. Touch the top-level CMakeLists to force a full
# re-glob of the extensions tree.
touch "$TOPAS_SRC/CMakeLists.txt" 2>/dev/null || true
cmake . > cmake_reconfig.log 2>&1 || { cat cmake_reconfig.log; exit 1; }
echo "    --- cmake extension scan (look for 'TrackDumper' below) ---"
grep -Ei 'TrackDumper|extensions in directory|is a Scorer for' cmake_reconfig.log || echo "    (no scorer scan output found)"
echo "    ----------------------------------------------------------"
if ! grep -q 'TrackDumper.cc is a Scorer for TrackDumper' cmake_reconfig.log; then
    echo "WARNING: cmake did not register TsTrackDumper as a Scorer." >&2
    echo "         The extension dir may need a fresh configure. Try:" >&2
    echo "           cd $TOPAS_BUILD && rm -f CMakeCache.txt && cmake -DTOPAS_EXT_DIR=$TOPAS_EXT ." >&2
fi

echo "==> 4/5  Rebuilding + installing (incremental)"
make -j"$(nproc)"
make install

echo "==> 5/5  Smoke test: TrackDumper on a water box"
cd "$HERE"
rm -f track_dump.csv track_dump.txt
# sudo drops the user's LD_LIBRARY_PATH, so the TOPAS/Geant4 shared libs
# (libG4Tree.so etc.) won't be found. Locate the Geant4 lib dir and set it.
G4LIB="$(dirname "$(find /opt/topas/GEANT4 -name libG4Tree.so 2>/dev/null | head -1)")"
TOPASLIB="$(dirname "$(find /opt/topas/TOPAS/OpenTOPAS-install -name 'libTOPAS*.so' 2>/dev/null | head -1)")"
export LD_LIBRARY_PATH="${G4LIB:+$G4LIB:}${TOPASLIB:+$TOPASLIB:}${LD_LIBRARY_PATH:-}"
echo "    LD_LIBRARY_PATH includes: ${G4LIB:-<g4 not found>} ${TOPASLIB:-}"
"$TOPAS_BIN" test_TrackDumper.txt > smoke.log 2>&1 || { echo "SMOKE TEST FAILED:"; tail -25 smoke.log; exit 1; }
if [ -f track_dump.csv ] || [ -f track_dump.txt ]; then
    echo "OK: TrackDumper produced output:"
    ls -la track_dump.*
    echo "    (TOPAS now recognizes scorer Quantity \"TrackDumper\".)"
else
    echo "WARNING: scorer ran but produced no track_dump.* -- check smoke.log" >&2
    tail -25 smoke.log >&2
fi

echo
echo "==> Done. Next: attach TrackDumper to a chamber plug in both the Beam-source"
echo "    (direct) and PhaseSpace-source (replay) runs and diff the ntuple outputs."
echo "    See openspec/changes/fix-phase-space-replay-dose/design.md (Bug B)."
