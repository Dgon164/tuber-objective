# Phase C: on the pad with the astronaut's controls, and a launch

2026-10-11, afternoon. The machine is the same as in Phases A and B:
the real flight program running on an emulator, a program that imitates
the Apollo Guidance Computer (the AGC, the computer that flew the
spacecraft) instruction by instruction, with the DSKY, the panel of keys
and lit digits the astronauts used to talk to the computer, attached
over its socket. What's new is that the vehicle model starts at rest on
the ground, and it now has the astronaut's own controls, the ones that
work without going through the computer:

- arm
- engine on
- engine off
- throttle up and throttle down
- a hand controller that sends rotation pulses about three axes

`launch.py` is the loop. It presses a control, records every signal,
compares the signals with what it remembers, keeps the result, and
makes a prediction before each press.

Given a goal, it walks its own map backward from the goal to a control.

It's told nothing about what any control does, what any instrument
means, or the laws of physics.

## What went in

Everything on Phase A's list, plus:

- The vehicle model (`vehicle.py --pad`), treated as hardware. The
  model has physics inside, but the loop never looks inside it. The
  model sends a row of instrument readings every 100 ms, with these
  fields:
  - three angles
  - three turn rates
  - the altitude
  - two speeds
  - the thrust
  - two jet words
  - two pulse counts
  - the propellant
  - armed
  - engine

  The loop sees these only as fields 0 through 16. The names are for
  the people reading the output.
- A list of 44 raw actions: the 33 DSKY codes plus PRO, and 11 control
  packets. Nothing says which packet is the throttle.
- The goal, as limits on numbered fields, given only in the goal phase:
  field 6 above 200, and fields 3, 4 and 5 below 5,000. In the model's
  units that's an altitude above 200 m and turn rates below 0.5 degrees
  per second.
- Two definitions the loop applies to every field. Both are built on
  the comparator, Discovery's basic comparison that says whether two
  things are the same, different, or one is part of the other.

  A field *moves* in a window if it changed in more than one row, and
  the definition also gives the direction. This separates a real trend
  from a one-off change: a change in a single row only is a *jump*.

  A field that has ever moved is continuous, and for a continuous
  field only the direction (up or down) goes into the state. A field
  that has only ever jumped gives its value to the state.
- Size limits. The per-step read of the channels is off. A channel is a
  numbered signal path between the computer and the hardware around
  it, and the channel recording goes to disk instead.

The loop was not given:

- what any control does
- what any field means
- the thrust
- the weight
- gravity
- inertia
- a plan
- a score
- a manual

## The model phase: 3,480 presses over three lives

In each life the vehicle starts on the pad, and the loop's memory
carries over from one life to the next. In every state the loop tried
the action it had tried least. It found 43 states and 922 transitions.

From that it made this effects table (`effects-table.txt`). The names
come from the lens, a names file used only when printing so a person
can read the output; the counts come from the machine:

```
action         pressed  effects seen (field: times up / times down)
arm                 41  armed:3/0
engine on           39  thrust:13/0 pipa:13/0 prop:0/13 engine:13/0  (alt:2/0 vz:2/0)
engine off          33  thrust:0/10 pipa:0/10 prop:10/0 engine:0/10  (vz:0/2)
throttle up         37  thrust:14/0  (alt:2/0 vz:3/0)
throttle down       22  -
+roll               22  ax:2/0 wx:2/0 cdu:2/0
-roll, +/-pitch, +/-yaw     -   (tried on the ground, where the legs hold it still)
PRO                 40  -
24 DSKY codes           -   no effect on any instrument field, ever
```

Engine on has four effects:

- the thrust goes up
- the accelerometer pulses go up
- the propellant goes down
- the engine flag goes up

All four happened 13 times out of 13, and the reverse never happened.
Engine off has exactly the reverse effects, 10 out of 10. Throttle up
has one effect, thrust up, 14 out of 14. Arm has one effect: the armed
flag goes up. One roll pulse in flight has three effects:

- the roll angle changes
- the roll rate changes
- the gimbal pulses (the angle readings the vehicle sends the computer)
  change

The DSKY codes never affected any vehicle instrument. So the loop found
the thrust, the propellant burn, and the hand controller, all three
from pressing and watching.

The loop also sorted the fields on its own. It saw eight fields in
continuous motion:

- an angle
- a rate
- the altitude
- the vertical speed
- a jet word
- the pulse counts
- the propellant

The other fields only jump:

- the thrust
- armed
- engine
- the other angles

The other angles didn't move because the loop only tried pitch and yaw
on the ground, where the legs hold the vehicle still.

The numbers in parentheses in the table are confounds: cases where two
things happened in the same window, so a correlation could give a false
answer. The table shows them as they are. Twice the altitude started
moving in the same window as an "engine on" or a "throttle up", and
both times the credit was right: the engine, or the extra notch, lifted
the vehicle.

DSKY code 0 also shows `alt:5/0`. The loop happened to press code 0 at
the moment the slow propellant burn made the vehicle lighter than its
thrust, and it lifted off by itself. The recording credits whatever
action was pressed in that window. What separates true effects from
coincidence is the prediction step and the counts: 13 out of 13 against
5 out of 64.

During exploration the vehicle lifted off twice on a fourth throttle
notch and came down hard (179 and 152 m/s at impact). Nothing in the
explorer reacts to an impact, and that's correct.

## The goal phase: 22 presses

```
step 1740  walk*(2 steps) arm           effect: armed+
step 1741  walk*(1 steps) engine on     effect: thrust+ pipa+ prop- engine+
step 1742  walk*(4 steps) throttle up   effect: thrust+
step 1743  walk*(3 steps) throttle up   effect: thrust+
step 1744  walk*(2 steps) throttle up   effect: thrust+
step 1745  walk*(1 steps) throttle up   effect: vz+ thrust+
step 1746  direct         DSKY code 0   effect: alt+
step 1747-1760  hold      DSKY code 3   (the record's least-effect action), climbing
step 1761  GOAL SATISFIED: altitude 223, vz 6.5 m/s, rates 0, propellant 4196, armed, engine on
```

`vehicle.out` shows lift-off at 103.76 s, with 24,670 N of thrust
against 24,084 N of weight. `vehicle.csv` has the climb row by row.
Predictions in the run: 14,259 right, 4 wrong.

At each step of the goal phase the walk does this:

1. Find the states in the map where each goal field moved in the goal
   direction.
2. Search backward through the map's transitions to the state the
   machine is in now.
3. Press the first action on that path.
4. Look again from the state the machine lands in after the press.

The mark "walk*" means the match was on the instrument part of the
state only, because the computer's channels at startup differ slightly
from one life to the next.

## What changed during the work, each a definition the loop applies, not a fact from outside

- The first definition of *hold* was "the most common change from row
  to row is 0". That was wrong for the propellant, which changes in
  roughly one row in seven, slowly. Now: no change from the start of
  the window to the end.
- The loop read a jump (thrust from 0 to 4,670 in one row) as motion in
  its window, then read the next window as "motion stopped", so the
  next press got credit for "thrust down". Now: a field moves only if
  it changed in more than one row.
- At first an action got credit for every motion in its window,
  including a propellant burn that was already under way before the
  press. Now: an action's effect is a motion it started, stopped or
  reversed, or a jump in a field that was holding. A motion already
  under way belongs to the state, not to the action.
- The exact rate of a moving field changed from one read to the next,
  so every step looked like a new state. Now: direction only, up or
  down.
- A field that hadn't moved yet was recorded by its value; after it
  started moving, the same situation was recorded as a direction. The
  two descriptions didn't match, so the walk couldn't see the older
  states. The fix: the walk reads the old states through what it knows
  now.
- The map had transitions seen only once. For example, engine on lifted
  the vehicle in a life with almost no propellant left. The walk
  followed those to dead ends. Now the walk prefers the transition that
  usually follows: one seen at least twice, and in at least half the
  cases. A transition seen only once is the last resort.

## What it couldn't do

- The vehicle reached the goal on thrust alone, straight up. There's no
  pitch-over, no trajectory, and no return to the ground. The loop
  never tried pitch or yaw in flight; it used up its lives before
  reaching those states. More lives would give a bigger map.
- The DSKY was a dead branch for this goal, and it cost 33 presses in
  every state. The loop learned that the DSKY codes don't affect the
  vehicle, but it had no way to stop trying them in each new state.
  The chooser is correct in that it tries every action.
- The loop recorded the computer's memory writes and channels but
  didn't read them at each step; they're too large. The chain from a
  DSKY key to a routine to a channel to the vehicle is on disk, and the
  nudge run found that chain, but it's not in the state this loop
  uses.
- The walk's last resort ("direct") uses the raw effect counts, which
  is why DSKY code 0 got one press here. The right check for the last
  resort is the prediction record, and the walk doesn't do that yet.
- The time detail went down from "the level 1 and level 2 values" (the
  change from row to row, and the change in that change) to "moving:
  which direction". The constants are in `vehicle.csv` and in the
  level 1 pool; gravity, for instance, shows up as a steady second
  difference in the position. This goal didn't need the constants. A
  trajectory will.

## Files

- `launch.py`
- `vehicle.py` (the vehicle model with the pad start and the controls)
- `model.log` (the three lives)
- `goal.log`
- `effects-table.txt`
- `vehicle.csv` and `vehicle.out` (the goal life)
