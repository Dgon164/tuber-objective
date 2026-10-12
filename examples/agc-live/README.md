# The flight program, running

This is an example of something you can do with Discovery, not part of
Discovery. Nothing in `discovery.py` changes for it.

`examples/agc/` read the Apollo 11 Lunar Module flight program (Luminary
099) as a file and found the machine's word size, its instruction
vocabulary, and the common instruction sequences. This folder runs the
same program on an emulator of the real machine and records what it
does — every word of memory it changes, and every signal it sends to or
gets from the hardware. Those recordings are signals like any other,
and Discovery reads them the same way it read the file. It's the
`hybrid/net_as_lens.py` pattern (another system's output, written as
bytes, read as a signal) with a 1960s flight computer in place of the
net.

Where it could go is in `notes/open.md` under "The AGC in the loop":
reverse engineer the flight from the code, by comparing the machine
before and after each piece runs, reading the tests each piece makes
before it branches, and chaining those requirements backward from
"landed" to the first key press. No manual, no training. This folder is
the plumbing for that, and a first run. The rest hasn't been done.

## What's in here

| file | what it is |
|---|---|
| `build.sh` | builds the emulator, the assembler, and the rope from source. One command, about a minute. |
| `run.sh` | one recording: start the AGC, press keys over the socket, record everything, hand it to Discovery |
| `channel.py` | the smallest piece of hardware: connects to the emulator's socket, presses DSKY keys |
| `show.py` | prints a recording in octal so a person can read it (a lens; Discovery never sees it) |
| `discovery-trace.patch` | the change to the emulator, as a diff |
| `virtualagc/` | the emulator (`yaAGC`), the assembler (`yaYUL`), and the Luminary 099 source, from the Virtual AGC project, patched |
| `example-run/` | Discovery's records from one recording of the lamp test |
| `nudge-run/` | two flights, one kicked: the comparator finds the autopilot's chain from the pulse in to the jets out, with nothing named. `bridge_flights.py`, `flips.py` are its readers. |
| `loop.py`, `walk.py`, `do.py` | the loop: press, record, compare, choose; the walk backward from a goal to key presses; press them and check. `phase-a/` is its run on the DSKY alone. |
| `vehicle.py` | a small lunar module on the socket (hardware; from the 10-10 work), with a pad start and the astronaut's direct controls |
| `launch.py` | the loop with the vehicle: model, predict, walk. `phase-c/` is the run where it launched. `phase-b/` is the earlier run that could not, and says why. `goalB.py`, `runB.sh` go with it. |

Each `phase-*/` and `nudge-run/` folder has a `BREAKDOWN.md` that lists
every given first, then what came out, then where it stopped.

## Build and run

```
cd examples/agc-live
./build.sh
./run.sh
```

`build.sh` compiles `yaAGC` and `yaYUL` with gcc (nothing else needed)
and assembles `Luminary099/MAIN.agc` into `MAIN.agc.bin`, the rope the
emulator loads. This is the same program as `examples/agc/input/
luminary099.rope`; the file there is packed 15 bits to a word, the
emulator's is 16 bits with the parity bit, so they don't match byte for
byte.

`run.sh` with no arguments starts the AGC at 10x real time, waits a
second, presses `V35E` (the lamp test: every light and digit on), stays
up for eight seconds, then stops. It writes to `runs/<timestamp>/`:

- `writes.bin` — every write to erasable memory
- `channels.bin` — every packet on the hardware socket, both directions
- `keys.bin` — the packets `channel.py` sent

and then runs Discovery on the first two. Other runs:

```
./run.sh "V16N36E" 20 1      show the mission clock, 20 seconds, real time
./run.sh "V37E00E" 10 20     go to P00 (idle program), 10 seconds, 20x
```

Key letters: `V` `N` `E` verb, noun, enter; digits; `+` `-`; `C` clear;
`K` key release; `R` reset; `P` proceed.

## What you should see

From the write trace, the frame step finds the record width on its own:

```
FRAME
  width  score
   80    0.830   col  16 at 0.000   col  19 at 0.830
  chosen width 80
```

80 bits is the record. The columns that are always 0 are the record's
own layout: bit 16 (the instruction word is 15 bits in a 16-bit slot),
bits 32–36 (erasable addresses are under 4096), bits 48 and 64 (the
parity position of the old and new values). Discovery read the layout
from the signal.

The most common words are the idle loop. With no DSKY attached and no
hardware, the AGC has nothing to do, and its executive runs the same few
writes over and over. Those come out at the top of the WORDS table with
equal counts. That's correct.

The classes are where it gets interesting. In `example-run/
writes.bin.record.txt`, class `{0.0}` has ten members that are the same
two-write sequence with only the written value changing — `…1400`,
`…1402`, through `…1406`. That's one routine called ten times with a
different argument each time, grouped from the trace alone.

From the channel log, the frame step picks 16; the packet is 32 bits in
two halves of fixed form, and 16 and 32 tie, so it takes the smaller.
`--frame 32` reads whole packets. Either way the WORDS table is the list
of channels the AGC talked to and how often: 010 is the DSKY display,
015 is the keys coming in (four packets: V, 3, 5, E), 034 and 035 are
the downlink — the AGC's own telemetry stream, which it sends whether or
not anything is listening.

## The two recordings

**`writes.bin`**: one record per erasable write, 10 bytes, big-endian:

| bytes | what |
|---|---|
| 0–1 | address of the instruction that did the write, 0–36863, same index as the word in the rope |
| 2–3 | that instruction's word (15 bits) |
| 4–5 | the erasable address written, 0–4095 |
| 6–7 | the value there before |
| 8–9 | the value there after |

The instruction address is the rope index, so it lines up with
`examples/agc/`: word *n* of the rope is bytes 2*n* and 2*n*+1 of
`MAIN.agc.bin`. The one place this is ambiguous is code running from
erasable memory (addresses under 2048), which is rare.

**`channels.bin`**: one packet per channel event, 4 bytes, the
emulator's own socket form. `channel.py` has the layout and decodes it.
Both directions go in the same file — what the AGC sent to the hardware
and what the hardware (here, `channel.py`) sent to it.

## The patch

Three additions to the emulator, all marked `discovery trace` in the
source, shown in full in `discovery-trace.patch`:

1. `agc_engine.c`, in `Assign()` — the one function every erasable
   write goes through. If `AGC_TRACE_WRITES` names a file, write the
   10-byte record there.
2. `agc_engine.c`, in `agc_engine()` — right after the instruction is
   fetched, remember its address and word so the write record can carry
   them.
3. `SocketAPI.c` — if `AGC_TRACE_CHANNELS` names a file, copy every
   packet sent and every packet received into it.

And one more for speed: `agc_simulator.c` reads `AGC_SPEED`, and runs
the machine that many times faster than real time. The emulator paces
itself to the real AGC's speed by default, which is right for a DSKY
with a person at it and slow for recording.

## What was planned, and what of it has been done

1. **Opcodes by effect.** Single-step and compare: which instructions
   change erasable memory, which change only the accumulator, which
   change the program counter by something other than one. Group the
   opcode bits by what they changed. That's the instruction set, from
   behavior. The write trace already has the first class (the writers)
   — it's the instruction words that appear in it.
2. **Read set and write set per subroutine.** The call structure is in
   `examples/agc/`'s record (`TC BANKCALL` and its targets). Cut the
   write trace at those boundaries. What each stretch writes is its
   write set; what it reads before it branches is its requirements.
   Match one routine's reads against every other's writes, and the
   order they need to run in falls out.
3. **Channels against the vehicle.** Needs something on the other side
   of the socket that moves — NASSP in Orbiter (Windows), or a minimal
   model of your own. The channel log and the vehicle's state are two
   signals; the bridge finds which channel bits come with which motion.
4. **The walk backward.** From the landed state, through the channels
   that produce it, the routines that write those channels, the routines
   those require, to the keys. The multi-hop reasoner from `notes/
   open.md`.

Stage 3 is done in `nudge-run/` (the chain from pulses to jets to motion, read off two flights). The walk is built (`walk.py`, `launch.py`) and ran on the DSKY (`phase-a/`) and on the pad (`phase-c/`). Stages 1 and 2 — opcodes by effect and read/write sets per routine, from the write trace — are not done.

## Where things come from

- Virtual AGC: https://www.ibiblio.org/apollo/ and
  https://github.com/virtualagc/virtualagc — the emulator, the
  assembler, every flight program's source, and the documentation on
  how the machine works. The `virtualagc/` folder here is a copy of
  three of its folders plus one file, GPL, see `virtualagc/COPYING`.
- Luminary 099: the Apollo 11 LM flight program, public domain, source
  as transcribed by the Virtual AGC project.
- NASSP (the LM and CSM in the Orbiter space flight simulator, with the
  real AGC code inside): https://github.com/orbiternassp/NASSP
- Orbiter: http://orbit.medphys.ucl.ac.uk/
- The Apollo 11 flight journal, with every DSKY entry of the descent and
  when it was made: https://history.nasa.gov/afj/ap11fj/ — not used
  here, and the point is not to use it. It's listed so you know it
  exists if you ever need to check a result against what the crew did.

## Things to know

- The emulator wants a `core` file to resume from; `--no-resume` in
  `run.sh` makes it start clean each time, and the script deletes the
  dump it writes.
- `yaDSKY` (a picture of the DSKY you can click) is in the Virtual AGC
  repo but not here; it needs wxWidgets. `channel.py` does the same job
  with no picture.
- The symbol table `MAIN.agc.symtab` that the build makes is for the
  emulator's debugger, which can show you which routine an address is
  in. That's a reading aid, same standing as the lens: the trace is
  addresses, and Discovery works on the addresses.
- A full descent at real time is about twelve minutes; at 20x it's
  under a minute and writes about 600 MB of trace. Discovery's mint is a
  sort per round and pure Python, so cut the trace (per subroutine, per
  window) before reading it whole. `--limit` reads the first part.
