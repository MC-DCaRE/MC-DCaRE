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

echo "==> 1/6  Locating the TOPAS extensions directory"
# TOPAS scans the extensions dir (configured at the original cmake) recursively.
# Find it from a known extension (TOPAS-nBio), default to /opt/topas/extensions.
NBIODIR="$(find /opt/topas/extensions -maxdepth 1 -type d -name 'TOPAS-nBio' 2>/dev/null | head -1)"
if [ -n "$NBIODIR" ]; then
    TOPAS_EXT="$(dirname "$NBIODIR")"
elif [ -d /opt/topas/extensions ]; then
    TOPAS_EXT="/opt/topas/extensions"
else
    echo "ERROR: could not find TOPAS extensions dir (expected /opt/topas/extensions)." >&2
    echo "       Set TOPAS_EXT to your extensions root." >&2
    exit 1
fi
MY_EXT_DIR="$TOPAS_EXT/MC-DCaRE"
echo "    Extensions root: $TOPAS_EXT"
echo "    This scorer dir: $MY_EXT_DIR"

echo "==> 2/6  Staging TsTrackDumper.cc in $MY_EXT_DIR"
mkdir -p "$MY_EXT_DIR"
install -m 0644 "$HERE/TsTrackDumper.cc" "$MY_EXT_DIR/"

echo "==> 3/6  Removing any stale copy from the core scoring dir"
# A previous (broken) deploy may have put it in OpenTOPAS/scoring/, where it
# compiles but is never registered. Remove it so there's no confusion.
rm -f "$TOPAS_SRC/scoring/TsTrackDumper.cc"

echo "==> 4/6  Reconfiguring cmake (re-scans extensions for 'Scorer for' comments)"
cd "$TOPAS_BUILD"
cmake . 2>&1 | grep -Ei 'TrackDumper|extensions in directory|Scorer for|error' || true

echo "==> 5/6  Rebuilding + installing (incremental)"
make -j"$(nproc)"
make install

echo "==> 6/6  Smoke test: TrackDumper on a water box"
cd "$HERE"
rm -f track_dump.csv track_dump.txt
# Use the absolute TOPAS binary path (sudo drops PATH).
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
