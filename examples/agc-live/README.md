# The flight program, running

This is an example of something you can build with Discovery. It doesn't
change anything in `discovery.py`.

In `examples/agc/`, we took the Apollo 11 Lunar Module flight program
(Luminary 099) as a file and figured out the machine's word size, its
instruction set, and the common instruction patterns. This folder does
the next thing: it runs that same program on an emulator of the real
computer and records everything it does -- every memory location it
writes, every signal it sends to or gets from the hardware. Those
recordings are just signals, like any other, and Discovery reads them the
same way it read the file. It is the `hybrid/net_as_lens.py` pattern
(take another system's output as bytes, read it as a signal), except
here the "other system" is a 1960s flight computer.

The bigger goal is in `notes/open.md` under "The AGC in the loop":
reverse-engineer the flight from the code alone, by comparing the
machine's state before and after each piece runs, reading the tests each
piece checks before it decides which way to go, and chaining those
requirements backward from "landed" to the first key press. No manual,
no training data. This folder is the plumbing for that, plus the runs
we have done so far: one recording read by Discovery (`example-run/`);
two flights with one nudged (`nudge-run/`: the autopilot's chain from
the incoming pulse to the outgoing jets, found by comparing the two
flights, with nothing named); and the full loop -- press, record,
compare, choose, walk backward from a goal -- on the DSKY display alone
(`phase-a/`), with the vehicle attached (`phase-b/`), and on the launch
pad with the astronaut's controls (`phase-c/`, which actually launched).
What is not done yet is at the end of this page: sorting opcodes
(instruction codes) by their effects and finding the read/write sets
(which memory locations each routine touches) from the write trace.

## What's in here

| file | what it is |
|---|---|
| `build.sh` | Builds the emulator, the assembler, and the rope (the read-only program memory) from source. One command, about a minute. |
| `run.sh` | One recording session: starts the AGC, presses keys over a socket connection, records everything, then hands it to Discovery. |
| `channel.py` | The simplest piece of hardware: connects to the emulator's socket and presses DSKY keys. |
| `show.py` | Prints a recording in octal so a human can read it. This is just a display tool -- Discovery never sees it. |
| `discovery-trace.patch` | The change we made to the emulator, shown as a diff. |
| `virtualagc/` | The emulator (`yaAGC`), the assembler (`yaYUL`), and the Luminary 099 source, all from the Virtual AGC project, with our patch applied. |
| `example-run/` | Discovery's output from one recording of the lamp test. |
| `nudge-run/` | Two flights, one nudged: the comparator (Discovery's tool for finding what differs between two things) finds the autopilot's chain from the pulse in to the jets out, with nothing named. `bridge_flights.py` and `flips.py` are its readers. |
| `loop.py`, `walk.py`, `do.py` | The loop: press, record, compare, choose. The backward walk from a goal to key presses. Press them and check. `phase-a/` is its run on the DSKY alone. |
| `vehicle.py` | A small lunar module model on the socket (hardware, from the 10-10 work), with a pad start and the astronaut's direct controls. |
| `launch.py` | The loop with the vehicle: build a model, predict, walk backward. `phase-c/` is the run where it launched. `phase-b/` is the earlier run that could not, and explains why. `goalB.py` and `runB.sh` go with it. |

Each `phase-*/` and `nudge-run/` folder has a `BREAKDOWN.md` that lists
every input first, then what came out, then where it hit its limits.

## Build and run

```
cd examples/agc-live
./build.sh
./run.sh
```

`build.sh` compiles `yaAGC` and `yaYUL` with gcc (nothing else needed)
and assembles `Luminary099/MAIN.agc` into `MAIN.agc.bin`, which is the
rope the emulator loads. This is the same program as `examples/agc/input/
luminary099.rope`; the file there packs 15 bits per word while the
emulator's version uses 16 bits (with a parity bit), so the two files
don't match byte for byte.

`run.sh` with no arguments starts the AGC at 10x real time, waits a
second, presses `V35E` (the lamp test -- it turns on every light and
digit), stays up for eight seconds, then stops. It writes to
`runs/<timestamp>/`:

- `writes.bin` -- every write to erasable memory (the part of memory the program can change)
- `channels.bin` -- every packet on the hardware socket, both directions
- `keys.bin` -- the packets `channel.py` sent

and then runs Discovery on the first two. Other examples:

```
./run.sh "V16N36E" 20 1      show the mission clock, 20 seconds, real time
./run.sh "V37E00E" 10 20     go to P00 (idle program), 10 seconds, 20x
```

Key letters: `V` `N` `E` are verb, noun, enter; then digits; `+` `-`;
`C` clear; `K` key release; `R` reset; `P` proceed.

## What you should see

From the write trace, the frame step (where Discovery figures out how
wide each record is) finds the record width on its own:

```
FRAME
  width  score
   80    0.830   col  16 at 0.000   col  19 at 0.830
  chosen width 80
```

80 bits is the record. The columns that are always 0 reveal the record's
own layout: bit 16 (the instruction word is 15 bits packed into a 16-bit
slot), bits 32-36 (erasable addresses are under 4096, so the high bits
are always zero), bits 48 and 64 (the parity position of the old and new
values). Discovery read the layout straight from the signal.

The most common words are the idle loop. With no DSKY attached and no
hardware, the AGC has nothing to do, so its executive runs the same few
writes over and over. They show up at the top of the WORDS table with
equal counts. That is correct.

The classes are where it gets interesting. In `example-run/
writes.bin.record.txt`, class `{0.0}` has ten members that are the same
two-write sequence with only the written value changing -- `...1400`,
`...1402`, through `...1406`. That is one routine called ten times with
a different argument each time, grouped from the trace alone.

From the channel log, the frame step picks 16; the packet is really 32
bits in two halves of a fixed form, and 16 and 32 tie, so it takes the
smaller one. `--frame 32` reads whole packets. Either way, the WORDS
table is the list of channels the AGC talked to and how often: 010 is
the DSKY display, 015 is the keys coming in (four packets: V, 3, 5, E),
034 and 035 are the downlink -- the AGC's own telemetry stream, which it
sends whether or not anything is listening.

## The two recordings

**`writes.bin`**: one record per erasable write, 10 bytes, big-endian:

| bytes | what |
|---|---|
| 0-1 | Address of the instruction that did the write, 0-36863. This is the same index as the word in the rope. |
| 2-3 | That instruction's word (15 bits). |
| 4-5 | The erasable address written to, 0-4095. |
| 6-7 | The value that was there before. |
| 8-9 | The value that is there after. |

The instruction address is the rope index, so it lines up with
`examples/agc/`: word *n* of the rope is bytes 2*n* and 2*n*+1 of
`MAIN.agc.bin`. The one spot where this is ambiguous is code running
from erasable memory (addresses under 2048), which is rare.

**`channels.bin`**: one packet per channel event, 4 bytes, in the
emulator's own socket format. `channel.py` has the layout and decodes
it. Both directions go into the same file -- what the AGC sent to the
hardware and what the hardware (here, `channel.py`) sent back.

## The patch

Three additions to the emulator, all marked `discovery trace` in the
source and shown in full in `discovery-trace.patch`:

1. `agc_engine.c`, in `Assign()` -- the one function every erasable
   write goes through. If the environment variable `AGC_TRACE_WRITES`
   names a file, write the 10-byte record there.
2. `agc_engine.c`, in `agc_engine()` -- right after the instruction is
   fetched, remember its address and word so the write record can carry
   them.
3. `SocketAPI.c` -- if `AGC_TRACE_CHANNELS` names a file, copy every
   packet sent and every packet received into it.

Plus one more for speed: `agc_simulator.c` reads `AGC_SPEED` and runs
the machine that many times faster than real time. The emulator normally
paces itself to the real AGC's speed, which is right when you have a
person at the DSKY but slow for just recording.

## What was planned, and what has been done

1. **Opcodes by effect.** Single-step the machine and compare: which
   instructions change erasable memory, which change only the
   accumulator (the register it does math in), which change the program
   counter (where the machine is in the code) by something other than
   one. Group the opcode bits by what they changed. That gives you the
   instruction set, learned from behavior. The write trace already has
   the first class (the writers) -- those are the instruction words that
   appear in it.
2. **Read set and write set per subroutine.** The call structure is in
   `examples/agc/`'s record (`TC BANKCALL` and its targets). Cut the
   write trace at those boundaries. What each stretch writes is its
   write set; what it reads before it decides where to go is its
   requirements. Match one routine's reads against every other's writes,
   and the order they need to run in falls out on its own.
3. **Channels against the vehicle.** This needs something on the other
   side of the socket that actually moves -- NASSP in Orbiter (Windows),
   or a minimal physics model of your own. The channel log and the
   vehicle's state are two signals; the bridge (Discovery's tool for
   comparing two different signals) finds which channel bits go with
   which motion.
4. **The backward walk.** From the landed state, through the channels
   that produce it, the routines that write those channels, the routines
   those require, all the way back to the keys. The multi-hop reasoner
   from `notes/open.md`.

Stage 3 is done in `nudge-run/` (the chain from pulses to jets to motion, found by comparing two flights). The backward walk is built (`walk.py`, `launch.py`) and ran on the DSKY (`phase-a/`) and on the pad (`phase-c/`). Stages 1 and 2 -- opcodes by effect and read/write sets per routine, from the write trace -- are not done yet.

## Where things come from

- Virtual AGC: https://www.ibiblio.org/apollo/ and
  https://github.com/virtualagc/virtualagc -- the emulator, the
  assembler, every flight program's source, and the documentation on
  how the machine works. The `virtualagc/` folder here is a copy of
  three of its folders plus one file, GPL, see `virtualagc/COPYING`.
- Luminary 099: the Apollo 11 LM flight program, public domain, source
  as transcribed by the Virtual AGC project.
- NASSP (the LM and CSM in the Orbiter space flight simulator, with the
  real AGC code inside): https://github.com/orbiternassp/NASSP
- Orbiter: http://orbit.medphys.ucl.ac.uk/
- The Apollo 11 flight journal, with every DSKY entry of the descent and
  when it was made: https://history.nasa.gov/afj/ap11fj/ -- not used
  here, and the whole point is to *not* use it. It is listed so you know
  it exists if you ever need to check a result against what the crew
  actually did.

## Things to know

- The emulator wants a `core` file to resume from; `--no-resume` in
  `run.sh` makes it start clean each time, and the script deletes the
  dump it writes.
- `yaDSKY` (a picture of the DSKY you can click on) is in the Virtual
  AGC repo but not included here; it needs wxWidgets. `channel.py` does
  the same job without the picture.
- The symbol table `MAIN.agc.symtab` that the build produces is for the
  emulator's debugger, which can show you which routine an address
  belongs to. That is just a reading aid, same standing as the display
  lens: the trace is addresses, and Discovery works on the addresses.
- A full descent at real time takes about twelve minutes; at 20x it is
  under a minute and writes about 600 MB of trace. Discovery's mint
  (the step that finds repeated patterns) does a sort per round and is
  pure Python, so cut the trace into pieces (per subroutine, per time
  window) before reading it whole. `--limit` reads just the first part.
