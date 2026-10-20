# The flight program in operation

This folder is an example of something you can build with Discovery.
Nothing in it changes `discovery.py`.

Some background first. The Apollo Guidance Computer, or AGC, was the
small computer that flew the Apollo spacecraft. The program it ran on
the Apollo 11 Lunar Module is called Luminary 099. The astronauts talked
to the computer through the DSKY, a panel with a numeric keypad and a
few rows of lit digits. The folder `examples/agc/` reads Luminary 099 as
a file, and from that file alone Discovery found the width of the
machine's word, its instruction set, and the instruction sequences it
uses most.

This folder takes the next step: it runs the same program on an
emulator. An emulator is a program that imitates the real computer
instruction by instruction, so the original 1969 flight program runs
unchanged on an ordinary PC. While the program runs, the emulator writes
down two things: every memory location the program changes, and every
signal that passes between the program and the hardware around it, in
both directions. Those recordings are files of bits like any other, and
Discovery reads them the same way it read the program itself.

That is the same approach as `hybrid/net_as_lens.py`: take the output of
some other system as bytes and read those bytes as a signal. Here the
other system is a flight computer from the 1960s.

The larger aim is written up in `notes/open.md` under "The AGC in the
loop": work out the structure of the flight from the code alone, with no
manual and no training data. It has three parts:

- compare the state of the machine before and after each piece of code
  runs
- read which values each piece of code checks before it decides where
  to go next
- starting from the "landed" state, trace what each piece needs,
  backward, until you reach the first key press

This folder holds the tools for that aim, and the runs that are done so
far:

- one recording that Discovery read (`example-run/`)
- two flights, one with a push and one without (`nudge-run/`).
  Discovery's basic comparison, which says whether two things are the
  same, different, or one is part of the other, is called the
  comparator. Pointed at the two flights, it found the chain of the
  autopilot from the pulse that comes in to the jets that fire. It was
  given no names for anything.
- the full loop: press a key, record what happens, compare it with what
  was seen before, choose the next press, and walk backward from a goal
  to the presses that reach it. The loop ran in three places:
  - on the DSKY display alone (`phase-a/`)
  - with a model of the vehicle attached (`phase-b/`)
  - on the launch pad with the astronaut's own controls (`phase-c/`).
    In that run the vehicle took off.

The last section of this page lists what isn't done yet. One task is to
sort the instruction codes (the opcodes) by what each one changes. The
other is to find, from the recording of memory writes, which memory
locations each routine reads and which it writes.

## Contents of this folder

| file | description |
|---|---|
| `build.sh` | Builds the emulator, the assembler, and the rope from source. The rope is the computer's read-only program memory, named for the way the real one was made, with wires threaded through magnetic cores. One command, about a minute. |
| `run.sh` | Does one recording session. It starts the computer, presses keys over a network socket, records every memory write and every hardware packet, then hands the recordings to Discovery. |
| `channel.py` | The simplest possible piece of hardware. It connects to the emulator's socket and presses DSKY keys. |
| `show.py` | Prints a recording in base 8 so a person can read it. It's a display tool only; Discovery doesn't use it. |
| `discovery-trace.patch` | The change made to the emulator, as a diff. |
| `virtualagc/` | The emulator (`yaAGC`), the assembler (`yaYUL`), and the source code of Luminary 099, all from the Virtual AGC project, with the patch applied. |
| `example-run/` | What Discovery wrote from one recording of the lamp test. |
| `nudge-run/` | Two flights, one with a push. The comparator finds the autopilot's chain from the pulse that comes in to the jets that fire, with no names given. The scripts that read the two flights are `bridge_flights.py` and `flips.py`. |
| `loop.py`, `walk.py`, `do.py` | The loop: press, record, compare, choose. The backward walk from a goal to the key presses that reach it. The check: press those keys on a fresh machine and compare what shows with the goal. `phase-a/` is this loop run on the DSKY alone. |
| `vehicle.py` | A small model of the lunar module, attached to the socket as if it were hardware (from the 10-10 work). It can start on the pad and has the astronaut's direct controls. |
| `launch.py` | The loop with the vehicle attached: build a map of what each control does, predict, then walk backward from a goal. `phase-c/` is the run where the vehicle took off. `phase-b/` is the earlier run, where a launch wasn't possible; its BREAKDOWN.md explains why. `goalB.py` and `runB.sh` go with `phase-b/`. |

Each `phase-*/` folder and the `nudge-run/` folder has a `BREAKDOWN.md`
that lists what went in first, then what came out, then what it
couldn't do.

## Build and run

```
cd examples/agc-live
./build.sh
./run.sh
```

Three commands, three steps:

1. Open a shell in the folder `examples/agc-live`.
2. Run `./build.sh`.
3. Run `./run.sh`.

`build.sh` compiles `yaAGC` and `yaYUL` with gcc and needs no other tool.
Then it assembles `Luminary099/MAIN.agc`, the program's source code,
into `MAIN.agc.bin`, the rope the emulator loads.

That rope is the same program as `examples/agc/input/luminary099.rope`,
but the two files aren't identical byte for byte. The file in
`examples/agc/input/` packs 15 bits into each word. The emulator's
version uses 16 bits per word, the extra one being a parity bit, a check
bit for catching errors.

Run with no arguments, `run.sh` starts the computer at ten times real
speed, waits one second, and presses `V35E`. That key sequence is the
lamp test, which turns on every light and every digit on the display.
The script keeps the computer running for 8 seconds, then stops it. It
writes three files to `runs/<timestamp>/`:

- `writes.bin`: every write to erasable memory, the part of the
  computer's memory the program can change while it runs
- `channels.bin`: every packet on the hardware socket, in both directions
- `keys.bin`: the packets `channel.py` sent

Then it runs Discovery on `writes.bin` and `channels.bin`. Two more
examples of the command:

```
./run.sh "V16N36E" 20 1      show the mission clock, 20 seconds, real time
./run.sh "V37E00E" 10 20     go to P00 (idle program), 10 seconds, 20x
```

The key letters:

- `V`, `N`, `E` are verb, noun, enter (the DSKY takes a command as a
  verb, what to do, and a noun, what to do it to)
- a digit is that digit
- `+` and `-` are plus and minus
- `C` is clear
- `K` is key release
- `R` is reset
- `P` is proceed

## What a correct run shows

The first thing Discovery does with any file is work out how wide one
record is: it tries widths and sees which one lines the bit patterns
up. This is the frame step. On the recording of memory writes it finds
the record width with no help:

```
FRAME
  width  score
   80    0.830   col  16 at 0.000   col  19 at 0.830
  chosen width 80
```

Each record is 80 bits. The bit positions that are always zero show the
layout of the record:

- bit 16. The instruction word is 15 bits sitting in a 16-bit slot.
- bits 32 to 36. Erasable addresses are below 4096, so the high bits
  are always zero.
- bits 48 and 64. These are the parity positions of the old value and
  the new value.

Discovery read that layout straight out of the signal.

The most common words are the idle loop. With no display and no
hardware attached, the computer has nothing to do, so the part of the
program that hands out work (its executive) repeats the same small set
of writes over and over. Those writes sit at the top of the WORDS table
with equal counts. That's correct.

The classes are the important result. A class is a group of parts that
take the same set of changes. In `example-run/writes.bin.record.txt`,
the class `{0.0}` has ten members, each the same two-write sequence
with only the value being stored different: `...1400`, `...1402`,
through `...1406`. That is one routine the program called ten times
with a different argument each time, and Discovery grouped the ten
calls from the recording alone.

A channel is a numbered signal path between the computer and the
hardware around it; each number is one piece of equipment. On the
channel recording, the frame step picks 16. The true packet is 32 bits,
in two halves that each have a fixed form, so widths 16 and 32 score
the same and the frame step takes the smaller. The flag `--frame 32`
reads whole packets. At either width the WORDS table is the list of
channels the computer used, each with its count:

- 010 is the DSKY display
- 015 is the keys coming in (four packets: V, 3, 5, E)
- 034 and 035 are the downlink, the computer's telemetry stream. It
  sends it whether or not anything is listening.

## The two recordings

**`writes.bin`**: one record for each write to erasable memory, 10
bytes, big-endian (most significant byte first):

| bytes | contents |
|---|---|
| 0-1 | The address of the instruction that did the write, 0 to 36863. This is the same index as the word's position in the rope. |
| 2-3 | The instruction word itself (15 bits). |
| 4-5 | The erasable address the instruction wrote, 0 to 4095. |
| 6-7 | The value at that address before the write. |
| 8-9 | The value at that address after the write. |

Because the instruction address is the rope index, it lines up with
`examples/agc/`: word *n* of the rope is bytes 2*n* and 2*n*+1 of
`MAIN.agc.bin`. The one case where the address is unclear is code that
runs from erasable memory (addresses below 2048), which is rare.

**`channels.bin`**: one packet for each channel event, 4 bytes, in the
emulator's own socket format. `channel.py` has the layout and decodes
the packets. Both directions go into the same file: the packets the
computer sent to the hardware, and the packets the hardware (here,
`channel.py`) sent back.

## The patch

The patch adds three things to the emulator. Each addition is marked
`discovery trace` in the source, and `discovery-trace.patch` shows each
one in full.

1. `agc_engine.c`, in `Assign()`. Every write to erasable memory goes
   through this one function. If the environment variable
   `AGC_TRACE_WRITES` names a file, the function appends the 10-byte
   record to that file.
2. `agc_engine.c`, in `agc_engine()`. Right after the function fetches
   an instruction, it keeps the instruction's address and word, so the
   write record can carry them.
3. `SocketAPI.c`. If `AGC_TRACE_CHANNELS` names a file, the code copies
   every packet going out and every packet coming in to that file.

There's one more addition, for speed. `agc_simulator.c` reads
`AGC_SPEED` and runs the machine that many times faster than real time.
Without it, the emulator runs at the speed of the real computer, which
is right when a person is sitting at the display and slow when the only
job is to make a recording.

## The plan, and how much of it is done

1. **Opcodes by effect.** Step the machine one instruction at a time
   and compare it before and after. That sorts the instructions into
   three groups:
   - the ones that change erasable memory
   - the ones that change only the accumulator (the register
     arithmetic is done in)
   - the ones that move the program counter (the machine's position in
     the code) by something other than one step forward

   Then group the opcode bits by the change each opcode made. The
   result is the instruction set, found from behavior. The write
   recording already gives the first group, the writers: they're the
   instruction words that appear in it.
2. **What each routine reads and writes.** The call structure is
   already in the record from `examples/agc/` (`TC BANKCALL` and its
   targets). Cutting a signal means dividing it into pieces at a
   boundary; cut the write recording at the points where one routine
   calls another.

   For each piece, the memory it writes is its write set. The memory it
   reads before deciding where to go is what it needs. Match what one
   routine needs against what every other routine writes, and the
   result is the order the routines must run in.
3. **Channels against the vehicle.** This stage needs something that
   moves on the other side of the socket: NASSP running in Orbiter
   (Windows), or a small physics model of your own. The channel
   recording and the vehicle's state are then two signals. Discovery's
   bridge is the step that compares two records and sorts what's in
   both from what's only in one; here it finds which channel bits go
   with each motion.
4. **The backward walk.** Start from the "landed" state and trace
   backward through four links:
   - the channels that produce the "landed" state
   - the routines that write those channels
   - the routines those routines need
   - the keys

   This is the multi-hop reasoner described in `notes/open.md`.

Stage 3 is done in `nudge-run/`: the comparator compared two flights and
found the chain from pulses to jets to motion. The backward walk is done
(`walk.py`, `launch.py`) and has run on the DSKY (`phase-a/`) and on
the pad (`phase-c/`).

Stages 1 and 2 are not done: sorting the opcodes by their effect, and
finding what each routine reads and writes from the write recording.

## Sources

- Virtual AGC: https://www.ibiblio.org/apollo/ and
  https://github.com/virtualagc/virtualagc. The project has the
  emulator, the assembler, the source of every flight program, and the
  documentation of the machine. The `virtualagc/` folder here is a copy
  of three folders and one file from it. The licence is GPL; see
  `virtualagc/COPYING`.
- Luminary 099: the flight program of the Apollo 11 Lunar Module,
  public domain. The source is the copy the Virtual AGC project made.
- NASSP: https://github.com/orbiternassp/NASSP. NASSP is the Lunar
  Module and the Command and Service Module inside the Orbiter space
  flight simulator, with the real computer code running inside them.
- Orbiter: http://orbit.medphys.ucl.ac.uk/
- The Apollo 11 flight journal: https://history.nasa.gov/afj/ap11fj/.
  It has every DSKY entry of the descent and the time each was made.
  This folder doesn't use the journal, and the point is *not* to use
  it. It's listed for one reason: you can check a result against what
  the crew actually did.

## Notes

- The emulator looks for a `core` file and continues from it. The
  `--no-resume` flag in `run.sh` makes it start clean every time, and
  the script removes the dump the emulator writes.
- `yaDSKY` is a picture of the DSKY you can click. It's in the Virtual
  AGC repository but not in this folder, and it needs wxWidgets.
  `channel.py` does the same job without the picture.
- `build.sh` also makes `MAIN.agc.symtab`, a symbol table: a list of
  which routine name goes with which address. It's for the emulator's
  debugger, which can then show the routine an address belongs to. It's
  only there to help a person read, in the same way as a lens, a names
  file Discovery uses only when printing so a person can read a name
  next to a number. The recording is addresses, and Discovery works on
  the addresses.
- A full descent takes about 12 minutes at real time. At twenty times
  real time it takes under a minute and writes about 600 MB of
  recording.

  Discovery's mint step compares chunks that look alike and records
  what they share, making a new part from two parts that start or end
  the same way. It sorts its whole pool once per round and is plain
  Python. So cut the recording into pieces (one per routine, or per
  time window) before reading a full recording. The `--limit` flag
  reads only the first part.
