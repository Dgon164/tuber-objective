# The flight program in operation

This folder is an example of a thing that you can make with Discovery.
The example makes no change to `discovery.py`.

The folder `examples/agc/` reads Luminary 099 as a file. Luminary 099 is
the flight program of the Apollo 11 Lunar Module. The AGC is the Apollo
Guidance Computer, the computer that runs the flight program. The DSKY
is the display and keyboard unit of the AGC. From the file, Discovery
found the word width of the machine, the instruction set, and the common
instruction sequences.

This folder does the next step. This folder runs the same program on an
emulator of the real computer. The emulator records each memory location
that the program writes. The emulator also records each signal that the
program sends to the hardware or gets from the hardware. The traces are
signals like all other signals. Discovery reads the traces in the same
way that Discovery read the file.

The method is the method of `hybrid/net_as_lens.py`. Discovery takes the
output of a different system as bytes. Discovery reads the bytes as a
signal. Here the different system is a flight computer of the 1960s.

The larger goal is in `notes/open.md` under "The AGC in the loop". The
goal is to find the structure of the flight from the code alone. The
method has 3 parts:

- compare the state of the machine before and after each part of the
  code runs
- read the tests that each part of the code checks before the part
  decides where to go
- connect the needs of each part backward from the "landed" state to the
  first key press

The method uses no manual and no training data. This folder has the
tools for that goal, and the runs that are complete:

- one trace that Discovery read (`example-run/`)
- 2 flights, 1 with a nudge (`nudge-run/`). The comparator is the tool
  of Discovery that finds the differences between 2 things. The
  comparator compared the 2 flights and found the chain of the autopilot
  from the pulse that comes in to the jets that go out. No name was given
  to the comparator.
- the full loop: press, record, compare, choose, and walk backward from a
  goal. The loop ran in 3 places:
  - on the DSKY display alone (`phase-a/`)
  - with the vehicle on the socket (`phase-b/`)
  - on the launch pad with the controls of the astronaut (`phase-c/`).
    In this run, the vehicle launched.

The last section of this page lists the work that is not complete. One
task is to sort the opcodes (the instruction codes) by their effects.
The other task is to find the read set and the write set of each routine
from the write trace. The read set and the write set are the memory
locations that a routine reads and writes.

## Contents of this folder

| file | description |
|---|---|
| `build.sh` | The script makes the emulator, the assembler, and the rope from source. The rope is the read-only program memory of the AGC. The script is 1 command and takes approximately 1 minute. |
| `run.sh` | The script does 1 trace session. The script starts the AGC. The script presses keys through a socket connection. The script records each write and each packet. The script gives the traces to Discovery. |
| `channel.py` | The most simple hardware. The script connects to the socket of the emulator and presses DSKY keys. |
| `show.py` | The script prints a trace in octal for a person to read. The script is a display tool only. Discovery does not use `show.py`. |
| `discovery-trace.patch` | The change to the emulator, as a diff. |
| `virtualagc/` | The emulator (`yaAGC`), the assembler (`yaYUL`), and the source of Luminary 099. All 3 come from the Virtual AGC project. The files include the patch. |
| `example-run/` | The output of Discovery from 1 trace of the lamp test. |
| `nudge-run/` | 2 flights, 1 with a nudge. The comparator finds the chain of the autopilot from the pulse that comes in to the jets that go out. No name is given to the comparator. The readers are `bridge_flights.py` and `flips.py`. |
| `loop.py`, `walk.py`, `do.py` | The loop: press, record, compare, choose. The backward walk from a goal to the key presses. The check: press the keys and compare the result with the goal. The folder `phase-a/` is the run of the loop on the DSKY alone. |
| `vehicle.py` | A small model of the lunar module on the socket (hardware, from the 10-10 work). The model has a start on the pad and the direct controls of the astronaut. |
| `launch.py` | The loop with the vehicle: make a model, predict, walk backward. The folder `phase-c/` is the run in which the vehicle launched. The folder `phase-b/` is the earlier run, in which a launch was not possible. The BREAKDOWN.md of `phase-b/` explains the cause. The files `goalB.py` and `runB.sh` go with `phase-b/`. |

Each `phase-*/` folder and the `nudge-run/` folder has a `BREAKDOWN.md`.
The BREAKDOWN.md lists each input first, then the results, then the
limits.

## Make and run

```
cd examples/agc-live
./build.sh
./run.sh
```

The 3 commands are 3 steps:

1. Open a shell in the folder `examples/agc-live`.
2. Run `./build.sh`.
3. Run `./run.sh`.

The script `build.sh` compiles `yaAGC` and `yaYUL` with gcc. The compile
step needs no other tool. The script assembles `Luminary099/MAIN.agc`
into `MAIN.agc.bin`. The file `MAIN.agc.bin` is the rope that the
emulator loads. The rope is the same program as `examples/agc/input/
luminary099.rope`. The file in `examples/agc/input/` packs 15 bits in
each word. The version of the emulator uses 16 bits in each word, with a
parity bit. Thus the 2 files are not the same byte for byte.

With no arguments, the script `run.sh` starts the AGC at 10 times real
time. The script waits 1 second and then presses `V35E`. The sequence
`V35E` is the lamp test. The lamp test turns on each light and each
digit. The script keeps the AGC in operation for 8 seconds, then stops
the AGC. The script writes 3 files to `runs/<timestamp>/`:

- `writes.bin`: each write to the erasable memory. The erasable memory
  is the part of the memory that the program can change.
- `channels.bin`: each packet on the hardware socket, in both directions
- `keys.bin`: the packets that `channel.py` sent

Then the script runs Discovery on `writes.bin` and `channels.bin`. Other
examples of the command:

```
./run.sh "V16N36E" 20 1      show the mission clock, 20 seconds, real time
./run.sh "V37E00E" 10 20     go to P00 (idle program), 10 seconds, 20x
```

The key letters are as follows:

- `V`, `N`, `E` are verb, noun, enter
- a digit is the same digit
- `+` and `-` are plus and minus
- `C` is clear
- `K` is key release
- `R` is reset
- `P` is proceed

## The output of a correct run

The frame step is the step in which Discovery finds the width of each
record. From the write trace, the frame step finds the record width
without help:

```
FRAME
  width  score
   80    0.830   col  16 at 0.000   col  19 at 0.830
  chosen width 80
```

The record is 80 bits. The columns that are always 0 show the layout of
the record:

- bit 16. The instruction word is 15 bits in a 16-bit slot.
- bits 32-36. The erasable addresses are less than 4096, so the high
  bits are always 0.
- bits 48 and 64. These are the parity positions of the old value and
  the new value.

Discovery read the layout directly from the signal.

The most common words are the idle loop. With no DSKY and no hardware,
the AGC has no work. Thus the executive of the AGC does the same small
set of writes many times. These writes are at the top of the WORDS table
with equal counts. This result is correct.

The classes are the important result. In `example-run/
writes.bin.record.txt`, the class `{0.0}` has 10 members. Each member is
the same sequence of 2 writes. Only the value that the write puts in
memory is different: `...1400`, `...1402`, through `...1406`. The
members are 1 routine that the program called 10 times, with a different
argument each time. Discovery grouped the members from the trace alone.

A channel is a numbered signal path between the AGC and the hardware.
From the channel trace, the frame step picks 16. The true packet is 32
bits, in 2 halves, each with a form that does not change. The widths 16
and 32 get the same score, so the frame step takes the smaller width.
The flag `--frame 32` reads whole packets. At each width, the WORDS
table is the list of the channels that the AGC used, with the count of
each channel:

- 010 is the DSKY display
- 015 is the keys that come in (4 packets: V, 3, 5, E)
- 034 and 035 are the downlink. The downlink is the telemetry stream of
  the AGC. The AGC sends the downlink with or without a receiver.

## The 2 traces

**`writes.bin`**: 1 record for each erasable write, 10 bytes,
big-endian:

| bytes | contents |
|---|---|
| 0-1 | The address of the instruction that did the write, 0-36863. The address is the same index as the word in the rope. |
| 2-3 | The word of the instruction (15 bits). |
| 4-5 | The erasable address that the instruction wrote, 0-4095. |
| 6-7 | The value at the address before the write. |
| 8-9 | The value at the address after the write. |

The instruction address is the rope index. Thus the address agrees with
`examples/agc/`: word *n* of the rope is bytes 2*n* and 2*n*+1 of
`MAIN.agc.bin`. The address is not clear in 1 case: code that runs from
the erasable memory (addresses less than 2048). This case is rare.

**`channels.bin`**: 1 packet for each channel event, 4 bytes, in the
socket format of the emulator. The script `channel.py` has the layout
and decodes the packets. Both directions go into the same file. The file
has the packets that the AGC sent to the hardware. The file also has the
packets that the hardware (here, `channel.py`) sent back.

## The patch

The patch makes 3 additions to the emulator. Each addition has the mark
`discovery trace` in the source. The file `discovery-trace.patch` shows
each addition in full.

1. `agc_engine.c`, in `Assign()`. Each erasable write goes through this
   1 function. If the environment variable `AGC_TRACE_WRITES` names a
   file, the function writes the 10-byte record to that file.
2. `agc_engine.c`, in `agc_engine()`. Immediately after the function
   gets the instruction, the function keeps the address and the word of
   the instruction. Thus the write record can carry the address and the
   word.
3. `SocketAPI.c`. If `AGC_TRACE_CHANNELS` names a file, the code copies
   each packet that goes out and each packet that comes in to that file.

The patch makes 1 more addition, for speed. The file `agc_simulator.c`
reads `AGC_SPEED` and runs the machine that number of times faster than
real time. Without the patch, the emulator runs at the speed of the real
AGC. That speed is correct when a person is at the DSKY. That speed is
slow when the only task is to make a trace.

## The plan and the work that is complete

1. **Opcodes by effect.** Step the machine 1 instruction at a time and
   compare the results. The comparison sorts the instructions into 3
   groups:
   - the instructions that change the erasable memory
   - the instructions that change only the accumulator (the register
     for arithmetic)
   - the instructions that change the program counter (the position of
     the machine in the code) by a value other than 1

   Group the opcode bits by the change that each opcode made. The result
   is the instruction set, found from behavior. The write trace already
   has the first group (the writers). The writers are the instruction
   words that occur in the write trace.
2. **Read set and write set for each subroutine.** The call structure is
   in the record of `examples/agc/` (`TC BANKCALL` and its targets). To
   cut a signal is to divide the signal into parts at a boundary. Cut
   the write trace at the call boundaries. The write set of a part is
   the memory that the part writes. The needs of a part are the memory
   that the part reads before the part decides where to go. Match the
   reads of 1 routine against the writes of each other routine. The
   result is the order in which the routines must run.
3. **Channels against the vehicle.** This stage needs a thing that
   moves on the other side of the socket. The thing can be NASSP in
   Orbiter (Windows) or a minimal physics model of your own. The channel
   trace and the state of the vehicle are 2 signals. The bridge is the
   tool of Discovery that compares 2 different signals. The bridge finds
   the channel bits that go with each motion.
4. **The backward walk.** The walk starts from the "landed" state. The
   walk goes backward through 4 links:
   - the channels that make the "landed" state
   - the routines that write those channels
   - the routines that those routines need
   - the keys

   The walk is the multi-hop reasoner from `notes/open.md`.

Stage 3 is complete in `nudge-run/`. The comparator compared 2 flights
and found the chain from the pulses to the jets to the motion. The
backward walk is complete (`walk.py`, `launch.py`). The walk ran on the
DSKY (`phase-a/`) and on the pad (`phase-c/`). Stages 1 and 2 are not
complete. Stage 1 is the opcodes by effect. Stage 2 is the read set and
the write set of each routine, from the write trace.

## Sources

- Virtual AGC: https://www.ibiblio.org/apollo/ and
  https://github.com/virtualagc/virtualagc. The project has the
  emulator, the assembler, the source of each flight program, and the
  documentation of the machine. The folder `virtualagc/` here is a copy
  of 3 folders and 1 file from the project. The licence is GPL. See
  `virtualagc/COPYING`.
- Luminary 099: the flight program of the Apollo 11 LM, public domain.
  The Virtual AGC project transcribed the source.
- NASSP: https://github.com/orbiternassp/NASSP. NASSP is the LM and the
  CSM in the Orbiter space flight simulator, with the real AGC code
  inside.
- Orbiter: http://orbit.medphys.ucl.ac.uk/
- The Apollo 11 flight journal: https://history.nasa.gov/afj/ap11fj/.
  The journal has each DSKY entry of the descent and the time of each
  entry. This folder does not use the journal. The goal is to *not* use
  the journal. The journal is in this list for 1 reason: you can check a
  result against the actions of the crew.

## Notes

- The emulator looks for a `core` file and continues from that file.
  The flag `--no-resume` in `run.sh` makes the emulator start clean each
  time. The script removes the dump that the emulator writes.
- The tool `yaDSKY` is a picture of the DSKY that you can click. The
  tool is in the Virtual AGC repository but not in this folder. The tool
  needs wxWidgets. The script `channel.py` does the same job without the
  picture.
- The build makes the symbol table `MAIN.agc.symtab`. The symbol table
  is for the debugger of the emulator. The debugger can show the routine
  of an address. The symbol table is a help for the reader only, with
  the same standing as the display lens. The display lens is the tool
  that shows the name of an address. The trace is addresses, and
  Discovery operates on the addresses.
- Note: a full descent at real time takes approximately 12 minutes. At
  20 times real time, a full descent takes less than 1 minute and writes
  approximately 600 MB of trace. The mint of Discovery is the step that
  finds the sequences that repeat. To mint a part is to make a new part
  from 2 parts that have the same start or the same end. The mint does
  1 sort in each round and is pure Python. Thus cut the trace into parts
  (for each subroutine, or for each time window) before you read the
  full trace. The flag `--limit` reads only the first part.
