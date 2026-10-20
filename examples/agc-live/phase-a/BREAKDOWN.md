# Phase A: the loop on the DSKY, with no information about the data path

2026-10-11. The machine is the real Apollo LM flight program in operation
on the emulator. The AGC is the Apollo Guidance Computer, the computer
that runs the flight program. The DSKY is the display and keyboard unit
of the AGC. A socket connects the DSKY to the emulator. The loop
(`loop.py`) can press 33 things: the 32 codes that the key channel
accepts, and PRO (proceed). Most of the 32 codes are not keys.

A channel is a numbered signal path between the AGC and the hardware.
The loop gets no information about the code of each key, the channel of
the display, or the function of each code. The loop presses a thing. The
loop records what the machine showed. The loop compares the result
against the memory of the loop. The loop keeps each result.

The loop picks the next press: the action that the loop has tried the
least in the current state. Then `walk.py` reads the map that the loop
made. The walk goes backward from a goal to the key presses that get to
the goal. Then `do.py` presses those keys on a fresh machine to check
the plan.

## The inputs

- The socket, and a list of 33 raw actions (channel 015 values 0-31,
  channel 032 bit 14).
- The record formats: 32-bit packets and 80-bit write records.
- The DSKY as hardware. The display channel carries 11 rows of relays
  that latch. A relay that latches keeps its state until a new packet
  sets the relay again. Each packet replaces the row that the top 4 bits
  of the packet name. The display *shows* the contents that the rows
  hold. The loop gets no information about the meaning of a row.
- A dwell of 1 moment for each press (5 s of machine time), a step
  budget of 250, and a size limit on the write trace for each step. The
  write trace was off for this run. The writes made each step 13 s long,
  and the map does not need the writes.
- Two tests that the machine does on itself. The comparator is the tool
  of Discovery that finds the differences between 2 things. Both tests
  use the comparator on the condition "no key pressed". The first test
  is at the start: 16 windows with no action. A channel that has a
  different value in any 2 of the 16 windows moves on its own. The
  second test is at each step. A channel that changes in the second half
  of the window moves on its own. The effect of the action must be
  complete before the second half of the window. When the machine sees a
  channel that moves on its own 1 time, the machine tags the channel as
  a self-mover. The tag stays. A self-mover stays in the record. The
  machine keeps a self-mover out of the context for decisions.

The loop did not get these inputs:

- the key names
- the channel names
- the meaning of the rows
- the input grammar of the DSKY
- a goal during the loop
- a score

## The map from 250 presses (`map-decoded.txt`)

From rest, the loop tried all 33 actions, most of them 2 times. Action
17 opens the verb row (the row goes blank). Action 18 changes the lamp
channel. Each other action leaves the machine in the same state. The
lens is the tool that finds the name of a code. Through the lens: 17 is
VERB, 18 is RSET, and a DSKY does not use a digit when no verb is in
progress.

From the open verb row, each of the keys 1 to 9 writes a different word
into the row: 9 words, 1 for each key. The codes 10 through 16 make no
change. Those codes are not keys. Through the lens: the row is the left
verb digit, and the 9 words are the 5-bit codes of the DSKY for the
digits 1-9.

From each of those 9 states, key 1 writes a second word. The last 5 bits
of the second word are the same each time (`...43`). Through the lens:
the second word is the right verb digit, and `00011` is the code for
"1".

Thus the sequence is: VERB, digit, digit. The loop found the sequence by
presses only. The loop did not get to ENTR in those states within the
budget. The map shows this limit: the map has no ENTR.

The loop found 3 self-movers: the 2 downlink channels (034, 035), at the
start, and the lamp channel (163), after a key set a lamp to flash.

## The walk and the check

The script `walk.py` takes a goal. The goal is a word that must be on
the display. The walk finds each state of the machine that shows the
word. The walk steps backward through the map to rest. The script
`do.py` starts a fresh machine. The script presses the keys that the
walk gives. The script reads the display rows and checks the rows
against the goal.

| goal (word on the display) | plan of the walk from rest | display of the fresh machine | check |
|---|---|---|---|
| `51543` | 17, 3, 1 | row 10 = `51543` | same |
| `51440` | 17, 2 | row 10 = `51440` | same |
| `51743` | 17, 9, 1 | row 10 = `51743` | same |
| `77777` | -- | -- | "no context the machine has seen satisfies this" |

Through the lens: V31, V2_, V91. The last row is the correct stop. A
goal that the machine has not seen gets no plan. The walk does not make
a guess.

The result has 3 parts. The map is "I understand this machine". The
goal word is "I understand what you want". The plan that the script
pressed and checked is "now I will do it". The result comes from the
DSKY alone, with the inputs in the list above and no other input.

## The changes during the work, each a part of the logic of the machine

- The emulator stops for the time that the loop reads. Thus a step is
  exactly 1 moment of machine time, not the time that Discovery takes to
  think. A signal tells the emulator to stop. The clock of the emulator
  starts again when the emulator starts again.
- The first definition of the context was "the packets that the display
  sent in this window". But the DSKY sends a row only when the row
  changes. Thus a row with a light was not in the context at the next
  step. The latch corrected this problem. The latch is the operation of
  the real hardware, not an artificial step.
- The first definition of the context was "the last value of each
  channel". The second definition was "the set of values of each
  channel". With both definitions, the values of the downlink changed at
  each step, and each step appeared to be a new state. The baseline with
  no action corrected this problem. If a value changes when no key is
  pressed, the change is not a response to the action.
- A lamp started to flash after a key press. The second-half test at
  each step found the lamp channel. The tag "self-mover" stays after the
  first time. Thus the lamp channel did not come back into the context
  in a quiet window.

## The limits

- Depth. With 33 actions for each state and a budget of 250, the loop
  gets to depth 3. The rule of the chooser is "try the action with the
  least tries in this state". The chooser has no cause to prefer 1 new
  branch to a different new branch. This is correct. A larger budget
  makes a larger map.
- Continuous state. The DSKY is discrete: the DSKY has a set of possible
  states that does not change. Thus states repeat, and the map fills.
  The state of a vehicle does not repeat. Phase B reads the values of
  the vehicle that change as a signal. Phase B looks at the fields that
  flipped, as in `nudge-run/`. Phase B does not put the values in the
  context for decisions. Phase A does not do this.
- The loop records the write trace, but the loop did not read the write
  trace in this run. The write trace is too large. With the write trace,
  each transition can also carry the memory cells and the routines of
  the transition. That is the "understand the code" half.

## Files

The files are:

- `loop.py`, `walk.py`, `do.py`: copies of the live scripts 1 folder up
- `loop.log`: each step
- `map.txt`: the map as counts
- `map-decoded.txt`: the map. The map shows each state as the
  difference from rest.
