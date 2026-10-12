#!/bin/sh
# One run of the test: start the AGC with Luminary 099, press some DSKY
# keys over the socket, record every memory write and every channel
# packet, then hand both recordings to Discovery.
#
#   ./run.sh                   lamp test (V35E), 8 seconds, 10x real time
#   ./run.sh "V16N36E" 20 1    show the clock, 20 seconds, real time
#
# Output goes in runs/<timestamp>/:
#   writes.bin        every erasable write, 10 bytes each (see README)
#   channels.bin      every channel packet the AGC sent, 4 bytes each
#   keys.bin          every packet we sent it (same form)
#   *.record.txt/json Discovery's records of the above
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
KEYS="${1:-V35E}"
SECONDS_="${2:-8}"
SPEED="${3:-10}"
RUN="$HERE/runs/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$RUN"
cd "$RUN"

echo "== AGC up (Luminary 099, ${SPEED}x real time), keys: $KEYS"
AGC_SPEED="$SPEED" AGC_TRACE_WRITES=writes.bin AGC_TRACE_CHANNELS=channels.bin \
  "$HERE/virtualagc/yaAGC/yaAGC" --nodebug --no-resume --quiet \
  "$HERE/virtualagc/Luminary099/MAIN.agc.bin" > yaagc.out 2>&1 &
AGC=$!
sleep 1

python3 "$HERE/channel.py" --log keys.bin --keys "$KEYS" --seconds "$SECONDS_"
kill $AGC 2>/dev/null; wait $AGC 2>/dev/null || true
rm -f core
echo "   writes.bin   $(wc -c < writes.bin) bytes"
echo "   channels.bin $(wc -c < channels.bin) bytes"

echo "== Discovery on the memory writes (frame search up to 128 bits, first 2 MB)"
python3 "$HERE/../../discovery.py" writes.bin --widest 128 --limit 2000000 --quiet --out .
echo "== Discovery on the channel packets"
python3 "$HERE/../../discovery.py" channels.bin --quiet --out .
echo "== done: $RUN"
grep -A3 "^FRAME" writes.bin.record.txt | head -4
grep -A6 "^LEVELS" writes.bin.record.txt
