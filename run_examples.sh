#!/bin/sh
# Regenerates every record in the repo from the inputs.  Run from the repo root.
set -e
cd "$(dirname "$0")"

echo "== text"
python3 discovery.py examples/text/alice.txt --lens ascii --quiet
python3 discovery.py examples/text/alice.txt --lens ascii --quiet --separators 20,0a

echo "== german"
python3 discovery.py examples/german/ep-00-01-17.de --lens utf8 --quiet
python3 discovery.py examples/german/ep-00-01-17.en --lens ascii --quiet
(cd examples/german && python3 bridge.py ep-00-01-17.de.record.json ep-00-01-17.en.record.json > bridge.record.txt)

echo "== code"
cp discovery.py examples/code/input/discovery.py
# examples/code/input/hello is the committed binary; to rebuild it (a different
# compiler gives a different binary and a different record):
#   gcc -O1 -o examples/code/input/hello examples/code/input/hello.c
python3 discovery.py examples/code/input/discovery.py --lens ascii --quiet --out examples/code
python3 discovery.py examples/code/input/discovery.py --lens ascii --quiet --out examples/code --separators 20,0a
python3 discovery.py examples/code/input/hello --lens ascii --quiet --out examples/code
python3 discovery.py examples/code/input/hello --lens ascii --quiet --out examples/code --frame 8

echo "== agc"
python3 examples/agc/make_rope.py examples/agc/input/Luminary099.binsource examples/agc/input/luminary099.rope
python3 discovery.py examples/agc/input/luminary099.rope --lens octal --quiet --out examples/agc
python3 discovery.py examples/agc/input/luminary099.agc --lens ascii --quiet --out examples/agc --separators 2

echo "== memory"
rm -f examples/memory/alice.memory
cp examples/german/ep-00-01-17.de examples/memory/ep-00-01-17.de
(cd examples/memory && python3 ../../discovery.py alice-first-half.txt  --lens ascii --quiet --memory alice.memory)
(cd examples/memory && python3 ../../discovery.py alice-second-half.txt --lens ascii --quiet --memory alice.memory)
(cd examples/memory && python3 ../../discovery.py alice-second-half.txt --lens ascii --quiet --memory alice.memory)
(cd examples/memory && python3 ../../discovery.py ep-00-01-17.de        --lens utf8  --quiet --memory alice.memory)

echo "== hybrid"
(cd hybrid && python3 record_to_rules.py ../examples/text/alice.txt.record.json > record_to_rules.output.txt)
(cd hybrid && python3 loop.py ../examples/text/alice.txt.record.json > loop.collide.txt)
if python3 -c "import numpy" 2>/dev/null; then
    (cd hybrid && python3 net_as_lens.py ../examples/text/alice.txt > net_as_lens.output.txt)
fi
echo "== extend"
(cd extend && python3 cut_at_class.py ../examples/text/alice.txt > cut_at_class.output.txt)
(cd extend && python3 same_within.py ../examples/agc/input/luminary099.rope > same_within.output.txt)
(cd extend && python3 row_by_row.py ../hybrid/alice.txt.reservoir > row_by_row.output.txt)
(cd extend && python3 same_slot.py ../examples/text/alice.txt > same_slot.output.txt)
(cd extend && python3 functions.py ../examples/text/alice.txt 20 > functions.output.txt)
(cd extend && python3 sentence.py ../examples/text/alice.txt 5 > sentence.output.txt)

echo "done"
