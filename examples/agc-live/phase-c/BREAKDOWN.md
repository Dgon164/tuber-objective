# Phase C: on the pad, with the astronaut's controls. It launched.

2026-10-11, afternoon. Same machine as Phases A and B -- the real flight
program on the emulator, the DSKY on its socket -- but now the vehicle
model starts at rest on the ground. It also has the controls an
astronaut had that work without the computer: arm, engine on, engine
off, throttle up and down, and a hand controller that sends rotation
pulses about three axes. `launch.py` is the loop. It presses, records
every signal, compares against memory, keeps everything, predicts, and
-- once given a goal -- walks its own map backward from the goal to a
control. It was told nothing about what any control does, what any
instrument means, or how physics works.

## What was given

Phase A's list, plus:

- The vehicle model (`vehicle.py --pad`): hardware. It knows physics
  internally, but the loop never looks inside it. Its instrument rows
  come every 100 ms: three angles, three turn rates, altitude, two
  speeds, thrust, two jet words, two pulse counts, propellant, armed,
  engine. The loop sees these as fields 0 through 16. The names are just
  for us humans reading the output.
- 44 raw actions: the 33 DSKY codes and PRO, plus 11 control packets.
  Nothing says which packet is the throttle.
- The goal, given only in the goal phase, as constraints on field
  numbers: field 6 over 200; fields 3, 4, 5 under 5,000 (in the model's
  units: altitude over 200 m, turn rates under 0.5 deg/s).
- Two definitions the machine applies to every field, both using the
  comparator: a field is *moving* in a window if it changed in more than
  one row (to tell apart a genuine trend from a one-time jump), and
  which way; a single-row change is a *jump*. A field that has ever been
  seen moving is treated as continuous and only its direction (up or
  down) matters for state; one that has only ever jumped contributes its
  actual value.
- Size limits (per-step channel reading turned off; the channel log is
  saved to disk).

Not given: what any control does, what any field means, thrust, weight,
gravity, inertia, a plan, a score, a manual.

## The model phase: 3,480 presses over three lives

The vehicle model starts on the pad each life; the memory carries over.
The loop tried the least-tried action in each state it found itself in.
It found 43 states and 922 transitions, and built this effects table
(`effects-table.txt`; names are from the lens, counts are the machine's):

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

Engine on: thrust goes up, accelerometer pulses go up, propellant goes
down, engine flag goes up -- thirteen times out of thirteen, never the
reverse. Engine off: the exact reverse, ten of ten. Throttle up: thrust
goes up, fourteen of fourteen. Arm: the armed flag. One roll pulse in
flight: the roll angle, the roll rate, and the gimbal pulses to the
computer all change. The DSKY codes: nothing, ever, on any vehicle
instrument. That is thrust, propellant burn, and the hand controller,
all figured out by pressing and watching.

The machine also sorted the fields by itself: eight have been seen
moving continuously (angle, rate, altitude, vertical speed, a jet word,
the pulse counts, propellant) and the rest only jump (thrust, armed,
engine, the other angles -- those never moved because pitch and yaw were
only tried on the ground where the legs hold it still).

The numbers in parentheses above are confounds (cases where the
correlation might be misleading), and they are honest. Twice, altitude
started moving during the same window as an "engine on" or a "throttle
up," and both times the credit was deserved -- the engine or the extra
notch is what lifted it. DSKY code 0 also shows `alt:5/0` -- it was
being pressed during exploration when the slow propellant burn happened
to bring the weight down below the thrust, and the vehicle lifted on its
own. The record credits whatever was pressed in that window. The
prediction step and the counts are what separate real effects from
coincidence: 13 of 13 versus 5 of 64.

During exploration the vehicle lifted off twice on a fourth throttle
notch and came back down hard (179 and 152 m/s impact). Nothing in the
explorer reacts to that, and nothing should.

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

`vehicle.out`: lift-off at 103.76 s, thrust 24,670 N against weight of
24,084 N. `vehicle.csv` has the climb row by row. Predictions during the
run: 14,259 right, 4 wrong.

How the walk works at each step: find the states in the map where every
needed field was moving in the needed direction; search backward through
the map's transitions to the current state; press the first action on
that path; then look again from wherever it actually ends up. "walk*"
means the match was on the instrument part of the state alone, because
the AGC's channels at startup differ slightly from life to life.

## What got fixed along the way, each a definition the machine applies, not a fact handed in

- *Holding* was first defined as "the most common row-to-row change is
  zero" -- wrong for the propellant, which changes about one row in
  seven and drifts slowly. Now: unchanged from the start of the window
  to the end.
- A jump (thrust going from 0 to 4,670 in one row) was read as motion
  in its window and then "motion stopped" in the next window, so the
  next press got credit for "thrust down." Now: moving means changed in
  more than one row.
- An action was first credited with everything moving in its window,
  including the propellant burn that was already under way. Now: an
  action's effect is motion it started, stopped, or reversed, or a jump
  while holding. Motion already under way belongs to the state, not to
  the action.
- A moving field's exact rate flickered between readings and made every
  step look like a new state. Now: direction only (up or down).
- A field that had never moved yet was recorded with its value; after it
  started moving, the same situation was recorded as a direction. The
  two descriptions did not match, so old states were invisible to the
  walk. Fix: the walk reads old states through current knowledge.
- The map held one-off transitions (engine-on lifting the vehicle in a
  life where the propellant was nearly gone) and the walk followed them
  into dead ends. Now: the walk prefers the transition that usually
  follows -- seen at least twice, and at least half the time -- and
  falls back to any single-occurrence transition only as a last resort.

## Where it stops

- The goal was reached by thrust alone, straight up. Nothing about
  pitching over, following a trajectory, or coming back down. The hand
  controller's pitch and yaw were never tried in flight; the explorer
  ran out of lives before reaching those states. More lives means more
  map.
- The DSKY was a dead branch for this goal and cost 33 presses per
  state. The machine learned that DSKY codes do nothing to the vehicle
  but had no way to stop trying them in each new state. That is the
  chooser being honest -- it tries everything.
- The computer's own writes and channels were recorded but not read per
  step (too big). The chain from a DSKY key to a routine to a channel
  to the vehicle -- the one the nudge run found -- is on disk, not in
  this loop's working state.
- The walk's fallback ("direct") still trusts raw effect counts, which
  is how DSKY code 0 got one press here. The prediction record is the
  right thing for it to check, and it does not do that yet.
- The time detail was reduced from "level 1 and 2 values" to just
  "moving: which direction." The constants -- gravity showing up as a
  steady second difference in position -- are in `vehicle.csv` and in
  the level-1 pool, and were not needed for this goal. They will be for
  a trajectory.

## Files

`launch.py`, `vehicle.py` (the vehicle model with the pad start and the
controls), `model.log` (the three lives), `goal.log`,
`effects-table.txt`, `vehicle.csv` and `vehicle.out` (the goal life).
