# Phase A: the loop on the DSKY, told nothing about what it's pressing

2026-10-11. The machine is the real Apollo Lunar Module flight program
running on an emulator, a program that imitates the Apollo Guidance
Computer (the AGC, the computer that flew the spacecraft) instruction
by instruction. The DSKY is the panel of keys and lit digits the
astronauts used to talk to the computer. Here it's attached to the
emulator over a network socket, a connection that lets any program act
as a piece of the computer's hardware.

The loop (`loop.py`) can press 33 things: the 32 codes the key channel
accepts, plus PRO (proceed). Most of the 32 codes aren't real keys.

A channel is a numbered signal path between the computer and the
hardware around it; each number is one piece of equipment, like the
display or the keys. The loop isn't told which code is which key, which
channel is the display, or what any code does. It presses something,
records what the machine showed, compares that with everything it has
seen before, and keeps the result.

To pick the next press, the loop takes whichever action it has tried
least in the state the machine is in now. When it's done, `walk.py`
reads the map the loop built, a record of which state the machine was
in, what was pressed, and which state came next, and walks backward
from a goal to the presses that reach it. Then `do.py` presses those
keys on a fresh machine to check the plan.

## What went in

- The socket, and a list of 33 raw actions (channel 015 values 0 to
  31, and channel 032 bit 14).
- The record formats: 32-bit packets and 80-bit write records.
- The DSKY as hardware. The display channel carries 11 rows, and each
  row keeps what was last written to it until something writes it again
  (on the real panel these were latching relays). Each packet replaces
  the row that its top 4 bits name. What the display *shows* is what
  the rows hold. The loop isn't told what any row means.
- Three limits:
  - a dwell of one moment per press, meaning the loop lets the machine
    run for 5 seconds of its own time after each press before reading
  - a step budget of 250
  - a size limit on the write recording per step

  Recording memory writes was turned off for this run. The writes made
  each step take 13 seconds, and the map doesn't need them.
- Two tests the loop does on the machine itself. Both use the
  comparator, Discovery's basic comparison that says whether two things
  are the same, different, or one is part of the other, and both
  compare against the condition "no key pressed".

  The first test runs once at the start: 16 windows with nothing
  pressed. Any channel whose value differs between any two of those 16
  windows is moving on its own. The second test runs at every step: any
  channel that changes in the second half of a window is moving on its
  own, because the effect of a press must be finished by then.

  Once the loop sees a channel move on its own, it tags that channel as
  a self-mover, and the tag stays. A self-mover stays in the recording,
  but the loop leaves it out of the state it uses to make decisions.

The loop was not given:

- the key names
- the channel names
- what any row means
- the DSKY's input grammar (what order verb, noun and digits go in)
- a goal during the loop
- a score

## The map from 250 presses (`map-decoded.txt`)

From rest, the loop tried all 33 actions, most of them twice. Action 17
opens the verb row (the row goes blank). Action 18 changes the lamp
channel. Every other action leaves the machine where it was. A lens is
a names file used only when printing, so a person can read a name next
to each number; Discovery never uses it. Through the lens: 17 is VERB,
18 is RSET, and a DSKY ignores a digit when no verb has been started.

With the verb row open, each of the keys 1 to 9 writes a different word
into the row: nine words, one per key. Codes 10 through 16 do nothing;
they aren't keys. Through the lens: the row is the left verb digit, and
the nine words are the DSKY's 5-bit codes for the digits 1 to 9.

From each of those nine states, key 1 writes a second word, and the
last 5 bits of that second word are the same every time (`...43`).
Through the lens: the second word is the right verb digit, and `00011`
is the code for "1".

So the sequence is VERB, digit, digit, and the loop found it by
pressing alone. It didn't reach ENTR from those states within the
budget, and the map shows that limit: there's no ENTR in it.

The loop found three self-movers: the two downlink channels (034 and
035, the computer's telemetry stream) at the start, and the lamp
channel (163) after a key set a lamp flashing.

## The walk and the check

`walk.py` takes a goal: a word that should be showing on the display.
It finds every state of the machine in which that word shows, then
steps backward through the map until it reaches rest.

`do.py` starts a fresh machine, presses the keys the walk gave, reads
the display rows, and checks them against the goal.

| goal (word on the display) | the walk's plan from rest | what the fresh machine showed | check |
|---|---|---|---|
| `51543` | 17, 3, 1 | row 10 = `51543` | same |
| `51440` | 17, 2 | row 10 = `51440` | same |
| `51743` | 17, 9, 1 | row 10 = `51743` | same |
| `77777` | -- | -- | "no context the machine has seen satisfies this" |

Through the lens: V31, V2_, V91. The last row is the correct refusal. A
goal the machine never saw gets no plan, and the walk doesn't guess.

The result has three parts. The map says "I understand this machine".
The goal word says "I understand what you want". The plan that was
pressed and checked says "now I'll do it". All of it came from the DSKY
alone, with the inputs listed above and nothing else.

## What changed during the work, each a piece of the machine's own logic

- The emulator pauses while the loop reads. So a step is exactly one
  moment of machine time, not however long Discovery takes to think. A
  signal tells the emulator to pause, and its clock starts again when
  it does.
- The first definition of the state was "the packets the display sent
  in this window". But the DSKY only sends a row when the row changes,
  so a row with a light on dropped out of the state at the next step.
  Holding each row's last value fixed that, and that's what the real
  hardware does, not an artificial step.
- The first definition of the state was "the last value on each
  channel"; the second was "the set of values on each channel". With
  both, the downlink's values changed every step, so every step looked
  like a new state. The no-action baseline fixed that: if a value
  changes when no key is pressed, the change isn't a response to the
  press.
- A lamp started flashing after a key press. The second-half test
  caught the lamp channel at that step, and because the self-mover tag
  stays, the channel didn't come back into the state during a later
  quiet window.

## What it couldn't do

- Depth. With 33 actions per state and a budget of 250, the loop
  reaches depth three. The chooser's rule is "try the action tried
  least in this state", and it has no reason to prefer one new branch
  over another. That's correct; a bigger budget gives a bigger map.
- Continuous state. The DSKY is discrete: it has a fixed set of
  possible states, so states repeat and the map fills in.

  A vehicle's state doesn't repeat. Phase B reads the vehicle's
  changing values as a signal and looks at which fields flipped, as in
  `nudge-run/`, but doesn't put the values into the state used for
  decisions. Phase A doesn't read the values as a signal at all.
- The loop records memory writes but didn't read them in this run; the
  recording is too large. With the writes, each transition could also
  carry the memory cells and the routines involved, which is the
  "understand the code" half.

## Files

- `loop.py`, `walk.py`, `do.py`: copies of the live scripts one folder
  up
- `loop.log`: every step
- `map.txt`: the map as counts
- `map-decoded.txt`: the map, with each state shown as its difference
  from rest
