# Phase A: the loop on the DSKY, with nothing told about the data path

2026-10-11. The machine is the real Apollo LM flight program running on
the emulator, with its DSKY (the display and keyboard unit) connected
over a socket. The loop (`loop.py`) can press 33 things -- the 32 codes
the key channel accepts (most of them are not actual keys) and PRO
(proceed) -- and it is told nothing about which code is which, which
channel is the display, or what any of it does. It presses something,
records what the machine showed, compares that against what it remembers,
keeps everything, and picks the next press based on what it has tried
least in the state it is in. Then `walk.py` reads the map it built,
working backward from a goal to the key presses that get there, and
`do.py` presses those keys on a fresh machine to check.

## What was given

- The socket, and a list of 33 raw actions (channel 015 values 0-31;
  channel 032 bit 14).
- The record formats: 32-bit packets; 80-bit write records.
- The DSKY as hardware: its display channel carries eleven rows of
  latching relays (think of each row like a sticky switch -- once set,
  it stays that way until it is set again), with each packet replacing
  the row named by its top four bits. What is *showing* is whatever the
  latched rows hold. No information about what any row means.
- A dwell of one moment per press (5 s of machine time), a step budget
  of 250, and a per-step size limit on the write trace (the writes were
  turned off for this run; they slowed each step to 13 s and the map
  does not need them).
- Two tests the machine runs on itself, both using the comparator on
  "nothing pressed": at the start, sixteen windows with no action, where
  any channel whose value differs between any two of them is moving on
  its own; and at every step, any channel still changing in the second
  half of the window (after the action's effect should have landed) is
  moving on its own. Once a channel is seen moving on its own, it stays
  tagged as a self-mover. Self-movers stay in the record but are kept
  out of the decision-making context.

Not given: key names, channel names, what the rows mean, the DSKY's
input grammar, any goal during the loop, any score.

## What it built in 250 presses (`map-decoded.txt`)

From rest, it tried all 33 actions, most of them twice: action 17 opens
the verb row (the row goes blank); action 18 changes the lamp channel;
everything else leaves the machine where it was. Through the lens (our
name-lookup tool): 17 is VERB, 18 is RSET, and a DSKY ignores digits
when there is no verb in progress.

From the opened verb row, keys 1 to 9 each write a different word into
it -- nine words, one per key, and 10 through 16 do nothing (those codes
are not keys). Through the lens: that is the left verb digit, and the
nine words are the DSKY's five-bit codes for the digits 1-9.

From each of those, key 1 writes a second word whose last five bits are
the same every time (`...43`). Through the lens: the right verb digit,
and `00011` is the code for "1".

So: VERB, digit, digit. Found entirely by pressing. The loop had not
reached ENTR in those states within the budget; the map says so by
simply not having it.

The three self-movers it found: the two downlink channels (034, 035),
found at the start; and the lamp channel (163), caught once a key had
set a lamp flashing.

## The walk and the check

`walk.py` takes a goal -- a specific word that should be showing on the
display -- finds every state the machine has been in that shows it, and
steps backward through the map to rest. `do.py` starts a fresh machine,
presses what the walk says, reads the latched display, and checks it
against the goal.

| goal (word on the display) | walk's plan from rest | fresh machine shows | check |
|---|---|---|---|
| `51543` | 17, 3, 1 | row 10 = `51543` | same |
| `51440` | 17, 2 | row 10 = `51440` | same |
| `51743` | 17, 9, 1 | row 10 = `51743` | same |
| `77777` | -- | -- | "no context the machine has seen satisfies this" |

Through the lens: V31, V2_, V91. The last line is the honest stop: a
goal it has never seen gets no plan, not a guess.

That is "I understand this machine" (the map), "I understand what you
want" (the goal word), "now I will do it" (the plan, pressed and
checked). On the DSKY alone, with the inputs listed above and nothing
else.

## What got fixed along the way, and why each fix is the machine's own logic

- The emulator pauses while the loop reads, so a step is exactly one
  moment of machine time instead of however long Discovery takes to
  think. (A signal tells the emulator to pause; its clock picks up again
  on resume.)
- The context was first "what the display sent this window"; but the
  DSKY only sends a row when it changes, so a lit row would vanish from
  the context the next step. The latch fixed that, and the latch is how
  the real hardware works, not a hack.
- The context was first "last value per channel," then "set of values
  per channel," and both let the downlink's wandering values make every
  step look like a brand-new state. The no-action baseline is what
  settled it: if something changes with nothing pressed, it is not a
  meaningful response.
- A flashing lamp started moving after a key was pressed. The per-step
  second-half test caught it; tagging it as a self-mover once seen
  stopped it from sneaking back into the context on a quiet window.

## Where it stops

- Depth. 33 actions per state and a budget of 250 gets you to depth
  three. The chooser is "try the least-tried action in this state"; it
  has no reason to prefer one unexplored branch over another, and it
  should not. More budget means more map.
- Continuous state. The DSKY is discrete (it has a fixed set of possible
  states), so states repeat and the map fills in. A vehicle's state does
  not repeat; Phase B handles the vehicle's changing values by reading
  them as a signal (looking at which fields flipped, as in `nudge-run/`)
  instead of making them part of the decision-making context. Not done
  here.
- The write trace is recorded but was not read in this run (too big).
  With it, each transition would also carry which memory cells and
  routines were involved -- the "understand the code" half.

## Files

`loop.py`, `walk.py`, `do.py` (copies of the live ones one folder up),
`loop.log` (every step), `map.txt` (the map as counts), `map-decoded.txt`
(the map with each state shown as what differs from rest).
