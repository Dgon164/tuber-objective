#!/bin/bash
# Run every goal in goals/ from the record of an earlier run, then the same goals from nothing, so the two can be
# compared: does what the loop learned under one objective carry over to another?
#   bash transfer.sh MEMORY_RUN_DIR OUT_DIR STEPS
set -e
MEM=$1; OUT=$2; STEPS=${3:-600}
HERE=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$OUT"
for g in "$HERE"/goals/*.txt; do
  name=$(basename "$g" .txt)
  echo "== $name from memory"
  python "$HERE/grade.py" "$OUT/$name-from-memory" "$STEPS" --max-attempt 120 --mission "$g" --memory "$MEM" > "$OUT/$name-from-memory.out" 2>&1
  grep "missions complete\|closest approach" "$OUT/$name-from-memory/grade.log" | tail -3
done
for g in "$HERE"/goals/*.txt; do
  name=$(basename "$g" .txt)
  echo "== $name from nothing"
  python "$HERE/grade.py" "$OUT/$name-from-nothing" "$STEPS" --max-attempt 120 --mission "$g" > "$OUT/$name-from-nothing.out" 2>&1
  grep "missions complete\|closest approach" "$OUT/$name-from-nothing/grade.log" | tail -3
done
