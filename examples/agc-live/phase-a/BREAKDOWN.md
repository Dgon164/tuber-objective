# Phase A: the loop on the DSKY, nobody in the data path

2026-10-11. The machine is the real Apollo LM flight program on the
emulator, with its DSKY on a socket. The loop (`loop.py`) can press 33
things — the 32 codes the key channel accepts (most are not keys) and
PRO — and is told nothing about which code is which, which channel is
the display, or what any of it does. It presses, records what the
machine showed, compares against memory, keeps everything, and chooses
the next press by what it has tried least in the state it's in. Then
`walk.py` reads the map it built backward from a goal to key presses,
and `do.py` presses them on a fresh machine and checks.

## What was given

- The socket, and the list of 33 raw actions (channel 015 values 0–31;
  channel 032 bit 14).
- The record formats: 32-bit packets; 80-bit write records.
- The DSKY as hardware: its display channel carries eleven rows of
  latching relays, each packet replacing the row named by its top four
  bits. What is *showing* is the latched rows. Nothing about what a row
  means.
- A dwell of one moment per press (5 s of machine time), a step budget
  of 250, and a per-step size limit on the write trace (the writes were
  switched off for this run; they slowed each step to 13 s and the map
  doesn't need them).
- Two tests the machine runs on itself, both the comparator on "nothing
  pressed": at the start, sixteen windows with no action, and a channel
  whose value differs between any two is moving by itself; and every
  step, a channel still changing in the second half of the window
  (after the action's effect landed) is moving by itself. Once seen
  moving by itself, a channel is kept as a self-mover. Self-movers stay
  in the record and out of the context.

Not given: key names, channel names, row meanings, the DSKY grammar,
any goal during the loop, any score.

## What it built in 250 presses (`map-decoded.txt`)

From rest, all 33 actions, most of them twice: 17 opens the verb row
(the row goes blank); 18 changes the lamp channel; everything else
leaves the machine where it was. With the lens: 17 is VERB, 18 is RSET,
and a DSKY ignores digits with no verb in progress.

From the opened verb row, keys 1 to 9 each write a different word into
it — nine words, one per key, and 10 through 16 do nothing (they are not
keys). With the lens: the left verb digit, and the nine words are the
DSKY's five-bit codes for the digits 1–9.

From each of those, key 1 writes a second word whose last five bits are
the same every time (`…43`). With the lens: the right verb digit, and
`00011` is the code for "1".

VERB, digit, digit. Found by pressing. It had not reached ENTR in those
states inside the budget; the map says so by not having it.

The three self-movers it found: the two downlink channels (034, 035),
at the start; and the lamp channel (163) once a key had set a lamp
flashing.

## The walk and the check

`walk.py` takes a goal — a word that should be showing — finds every
state the machine has seen that shows it, and steps backward through
the map to rest. `do.py` starts a fresh machine, presses what the walk
says, reads the latched display, and compares with the goal.

| goal (word on the display) | walk's plan from rest | fresh machine shows | check |
|---|---|---|---|
| `51543` | 17, 3, 1 | row 10 = `51543` | same |
| `51440` | 17, 2 | row 10 = `51440` | same |
| `51743` | 17, 9, 1 | row 10 = `51743` | same |
| `77777` | — | — | "no context the machine has seen satisfies this" |

With the lens: V31, V2_, V91. The last line is the honest stop: a goal
it has never seen gets no plan, not a guess.

That is "I understand this machine" (the map), "I understand what you
want" (the goal word), "now I'll do it" (the plan, pressed and checked).
On the DSKY alone, with the givens above and nothing else.

## What got fixed on the way, and why each is the machine's own move

- The emulator pauses while the loop reads, so a step is one moment of
  machine time instead of however long Discovery takes. (A signal to
  the emulator; its clock is re-based on resume.)
- The context was first "what the display sent this window"; the DSKY
  only sends a row when it changes, so a lit row vanished from the
  context the next step. The latch fixed that, and it's hardware, not
  knowledge.
- The context was first "last value per channel", then "set of values
  per channel", and both let the downlink's wandering values make every
  step a new state. The no-action baseline is what settled it: what
  moves with nothing pressed is not an answer.
- A flashing lamp started moving after a key. The per-step second-half
  test caught it; keeping it as a self-mover once seen stopped it from
  slipping back in on a quiet window.

## Where it stops

- Depth. 33 actions per state and a budget of 250 reaches depth three.
  The chooser is "least tried in this state"; it has no reason to
  prefer one unexplored branch over another, and shouldn't. More budget
  is more map.
- Continuous state. The DSKY is discrete, so states repeat and the map
  closes. A vehicle's state doesn't repeat; Phase B reads the vehicle's
  rows as a signal (flips, as in `nudge-run/`) rather than as part of
  the choosing context. Not done here.
- The write trace is recorded but was not read in this run (size). With
  it, each transition would also carry which cells and routines moved —
  the "understand the code" half.

## Files

`loop.py`, `walk.py`, `do.py` (copies of the live ones one folder up),
`loop.log` (every step), `map.txt` (the map as counts), `map-decoded.txt`
(the map with each state shown as what differs from rest).
