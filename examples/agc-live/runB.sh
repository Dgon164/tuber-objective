#!/bin/sh
# Phase B: the loop with the vehicle on the socket. Same loop as Phase A; the vehicle is a second
# client on the same emulator port (the loop prints its port on the first line of its log).
#   ./runB.sh RUN_DIR STEPS SPEED DWELL
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
RUN="$1"; STEPS="${2:-120}"; SPEED="${3:-20}"; DWELL="${4:-0.5}"
mkdir -p "$RUN"
python3 "$HERE/loop.py" "$RUN" "$STEPS" "$SPEED" "$DWELL" --no-writes --vehicle > "$RUN.out" 2>&1
