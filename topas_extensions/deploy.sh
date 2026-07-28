#!/usr/bin/env bash
# deploy.sh -- build & install the TrackDumper diagnostic scorer into the
# installed OpenTOPAS, then smoke-test it.
#
# Run this from a shell that has write access to /opt/topas (your normal
# user terminal, NOT the opencode sandbox). Idempotent.
#
#   cd <repo>/topas_extensions && ./deploy.sh
#
# Override the source/build roots if your layout differs:
#   TOPAS_SRC=/path/to/OpenTOPAS TOPAS_BUILD=/path/to/build ./deploy.sh
set -euo pipefail

TOPAS_SRC="${TOPAS_SRC:-/opt/topas/TOPAS/OpenTOPAS}"
TOPAS_BUILD="${TOPAS_BUILD:-/opt/topas/TOPAS/OpenTOPAS-build}"
TOPAS_BIN="${TOPAS_BIN:-/opt/topas/TOPAS/OpenTOPAS-install/bin/topas}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> 1/5  Locating the TOPAS scoring source directory"
# Custom scorers go alongside TsVScorer.cc (same place as TsScoreProtonLET).
TSVSCORER="$(find "$TOPAS_SRC" -name TsVScorer.cc -not -path '*/build/*' 2>/dev/null | head -1)"
if [ -z "$TSVSCORER" ]; then
    echo "ERROR: could not find TsVScorer.cc under $TOPAS_SRC." >&2
    echo "       Set TOPAS_SRC to your OpenTOPAS source root." >&2
    exit 1
fi
SCORING_DIR="$(dirname "$TSVSCORER")"
echo "    Found scoring source: $SCORING_DIR"

echo "==> 2/5  Copying TsTrackDumper.cc into the scoring source dir"
install -m 0644 "$HERE/TsTrackDumper.cc" "$SCORING_DIR/"

echo "==> 3/5  Reconfiguring cmake (re-scans for the new 'Scorer for' comment)"
cd "$TOPAS_BUILD"
cmake . >/dev/null

echo "==> 4/5  Rebuilding + installing (incremental; only the new scorer + relink)"
make -j"$(nproc)"
make install

echo "==> 5/5  Smoke test: TrackDumper on a water box"
cd "$HERE"
rm -f track_dump.csv track_dump.txt
# Use the absolute TOPAS binary path (sudo drops PATH, so `topas` isn't found).
"$TOPAS_BIN" test_TrackDumper.txt > smoke.log 2>&1 || { echo "SMOKE TEST FAILED:"; tail -20 smoke.log; exit 1; }
if [ -f track_dump.csv ] || [ -f track_dump.txt ]; then
    echo "OK: TrackDumper produced output:"
    ls -la track_dump.*
    echo "    (TOPAS now recognizes scorer Quantity \"TrackDumper\".)"
else
    echo "WARNING: scorer ran but produced no track_dump.* -- check smoke.log" >&2
    tail -20 smoke.log >&2
fi

echo
echo "==> Done. Next: attach TrackDumper to a chamber plug in both the Beam-source"
echo "    (direct) and PhaseSpace-source (replay) runs and diff the ntuple outputs."
echo "    See openspec/changes/fix-phase-space-replay-dose/design.md (Bug B)."
