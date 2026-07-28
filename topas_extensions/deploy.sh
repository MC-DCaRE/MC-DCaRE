#!/usr/bin/env bash
# deploy.sh -- build & install the TrackDumper diagnostic scorer into the
# installed OpenTOPAS, then smoke-test it.
#
# Run this from a shell that has write access to /opt/topas (e.g. your normal
# user terminal, NOT the opencode sandbox, which is sandboxed away from
# /opt/topas). It is idempotent.
#
#   cd <repo>/topas_extensions && ./deploy.sh
#
# After it succeeds, TOPAS will recognize the scorer type "TrackDumper".
set -euo pipefail

TOPAS_SRC="${TOPAS_SRC:-/opt/topas/TOPAS/OpenTOPAS}"
TOPAS_BUILD="${TOPAS_BUILD:-/opt/topas/TOPAS/OpenTOPAS-build}"
EXT_SCORING_DIR="$TOPAS_SRC/extensions/scoring"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> 1/5  Copying TsTrackDumper.cc into $EXT_SCORING_DIR"
if [ ! -d "$EXT_SCORING_DIR" ]; then
    echo "ERROR: expected extensions/scoring dir at $EXT_SCORING_DIR not found." >&2
    echo "       Set TOPAS_SRC to your OpenTOPAS source root." >&2
    exit 1
fi
install -m 0644 "$HERE/TsTrackDumper.cc" "$EXT_SCORING_DIR/"

echo "==> 2/5  Ensuring the extensions CMakeLists picks up the new source"
# TOPAS's extensions build auto-registers scorers from the
# `// Scorer for <Name>` header comment via a glob of *.cc. If your TOPAS
# uses an explicit source list instead, append the file manually:
CML="$TOPAS_SRC/extensions/CMakeLists.txt"
if ! grep -q "TsTrackDumper" "$CML" 2>/dev/null; then
    if grep -qi "GLOB\|file(GLOB" "$CML"; then
        echo "    (CMakeLists globs *.cc -- nothing to do)"
    else
        echo "    WARNING: $CML does not glob and does not list TsTrackDumper." >&2
        echo "    Append 'TsTrackDumper.cc' to its source list, then re-run." >&2
        exit 1
    fi
fi

echo "==> 3/5  Reconfiguring + rebuilding the extensions target (incremental)"
cd "$TOPAS_BUILD"
# Re-run cmake so any new source file is picked up, then build just extensions.
cmake . >/dev/null
make -j"$(nproc)" extensions

echo "==> 4/5  Installing"
make install

echo "==> 5/5  Smoke test: load TrackDumper on a water box"
cd "$HERE"
topas test_TrackDumper.txt > smoke.log 2>&1 || { echo "SMOKE TEST FAILED -- see smoke.log"; exit 1; }
if [ -f track_dump.csv ] || [ -f track_dump.txt ]; then
    echo "OK: TrackDumper produced output:"
    ls -la track_dump.*
    echo "Scorer is installed and working. Inspect the ntuple columns:"
    head -2 track_dump.* 2>/dev/null
else
    echo "WARNING: scorer ran but no track_dump.* output found -- check smoke.log" >&2
fi

echo
echo "==> Done. To diagnose the replay bug, run Beam-source vs PhaseSpace-source"
echo "    with TrackDumper attached to a chamber plug and diff the ntuple output."
echo "    See openspec/changes/fix-phase-space-replay-dose/design.md for the plan."
