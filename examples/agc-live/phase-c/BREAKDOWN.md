# Phase C: on the pad, with the controls of the astronaut, and a launch

2026-10-11, afternoon. The machine is the same machine as Phases A and
B: the real flight program on the emulator, with the DSKY on its socket.
The computer is the AGC (the Apollo Guidance Computer). The DSKY is the
display and keyboard unit of the AGC. In this phase, the vehicle model
starts at rest on the ground. The vehicle model also has the controls
of the astronaut that operate without the computer:

- arm
- engine on
- engine off
- throttle up and throttle down
- a hand controller that sends rotation pulses about 3 axes

The script `launch.py` is the loop. The loop presses a control. The loop
records each signal. The loop compares the signals against the memory.
The loop keeps each result. The loop predicts. When the loop gets a
goal, the loop walks its own map backward from the goal to a control.
The loop got no information about the function of a control, the
meaning of an instrument, or the laws of physics.

## The inputs

The inputs are the list of Phase A, and:

- The vehicle model (`vehicle.py --pad`): hardware. The model has
  physics inside, but the loop does not look inside the model. The
  instrument rows of the model come each 100 ms. Each row has these
  fields:
  - 3 angles
  - 3 turn rates
  - the altitude
  - 2 speeds
  - the thrust
  - 2 jet words
  - 2 pulse counts
  - the propellant
  - armed
  - engine

  The loop sees these fields as fields 0 through 16. The names are only
  for the persons who read the output.
- A list of 44 raw actions: the 33 DSKY codes and PRO, and 11 control
  packets. No input says the packet of the throttle.
- The goal, as limits on field numbers. The loop gets the goal only in
  the goal phase. The limits: field 6 more than 200, and fields 3, 4, 5
  less than 5,000. In the units of the model: an altitude more than
  200 m, and turn rates less than 0.5 deg/s.
- Two definitions that the machine applies to each field. The
  comparator is the tool of Discovery that finds the differences between
  2 things. Both definitions use the comparator. A field *moves* in a
  window if the field changed in more than 1 row. The definition also
  gives the direction. The definition separates a true trend from a
  1-time jump. A change in 1 row only is a *jump*. A field that moved at
  any time is continuous. For a continuous field, only the direction (up
  or down) is part of the state. A field that only jumped gives its
  value to the state.
- Size limits. The channel read at each step is off. A channel is a
  signal path with a number, between the AGC and the hardware. The
  channel trace goes to the disk.

The loop did not get these inputs:

- the function of a control
- the meaning of a field
- the thrust
- the weight
- the gravity
- the inertia
- a plan
- a score
- a manual

## The model phase: 3,480 presses in 3 lives

The vehicle model starts on the pad in each life. The memory continues
from life to life. In each state, the loop tried the action with the
least tries. The loop found 43 states and 922 transitions. The loop made
this effects table (`effects-table.txt`). The lens is the tool that
finds the name of a code. The names come from the lens. The counts come
from the machine:

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

Engine on has 4 effects:

- the thrust goes up
- the accelerometer pulses go up
- the propellant goes down
- the engine flag goes up

The 4 effects occur 13 times of 13. The reverse does not occur. Engine
off has the exact reverse effects, 10 of 10. Throttle up has 1 effect:
the thrust goes up, 14 of 14. Arm has 1 effect: the armed flag goes up.
One roll pulse in flight has 3 effects:

- the roll angle changes
- the roll rate changes
- the gimbal pulses to the computer change

The DSKY codes have no effect on any vehicle instrument, at any time.
Thus the loop found the thrust, the propellant burn, and the hand
controller. The loop found these from presses and observation.

The machine also sorted the fields without help. The machine saw 8
fields in continuous motion: an angle, a rate, the altitude, the
vertical speed, a jet word, the pulse counts, and the propellant. The
other fields only jump: the thrust, armed, engine, and the other angles.
The other angles did not move because the loop tried pitch and yaw only
on the ground. On the ground, the legs hold the vehicle at rest.

The numbers in parentheses in the table are confounds. A confound is a
case in which the correlation can give a false result. The table shows
the confounds as they are. Two times, the altitude started to move in
the same window as an "engine on" or a "throttle up". Both times the
credit was correct: the engine or the extra notch lifted the vehicle.

DSKY code 0 also shows `alt:5/0`. The loop pressed code 0 at the time
when the slow propellant burn made the weight less than the thrust. Then
the vehicle lifted on its own. The record gives the credit to the action
that the loop pressed in that window. The prediction step and the counts
separate the true effects from chance: 13 of 13 against 5 of 64.

In the exploration, the vehicle lifted off 2 times on a fourth throttle
notch and came back down hard (179 and 152 m/s impact). No part of the
explorer responds to the impact. This is correct.

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

The file `vehicle.out` shows the lift-off at 103.76 s, with a thrust of
24,670 N against a weight of 24,084 N. The file `vehicle.csv` has the
climb row by row. The predictions in the run: 14,259 correct, 4 wrong.

The walk does these steps at each step of the goal phase:

1. Find the states in the map where each goal field moved in the goal
   direction.
2. Search backward through the transitions of the map to the current
   state.
3. Press the first action on that path.
4. Look again from the state that the machine is in after the press.

The mark "walk*" means that the match was on the instrument part of the
state only. The cause: the channels of the AGC at the start are a small
amount different from life to life.

## The changes during the work, each a definition that the machine applies, not a fact from outside

- The first definition of *hold* was "the most common change from row
  to row is 0". The definition was wrong for the propellant. The
  propellant changes in approximately 1 row of 7 and changes slowly. The
  definition now: no change from the start of the window to the end.
- The loop read a jump (the thrust from 0 to 4,670 in 1 row) as motion
  in its window. The loop read the next window as "motion stopped". Thus
  the next press got the credit for "thrust down". The definition now: a
  field moves if the field changed in more than 1 row.
- At first, an action got the credit for each motion in its window. The
  credit included the propellant burn that was in progress before the
  action. The definition now: the effect of an action is a motion that
  the action started, stopped, or reversed, or a jump in a hold. A
  motion in progress before the action belongs to the state, not to the
  action.
- The exact rate of a field in motion changed from read to read. Thus
  each step appeared to be a new state. The definition now: the
  direction only (up or down).
- The loop recorded a field with no motion to date with its value.
  After the field started to move, the loop recorded the same situation
  as a direction. The 2 descriptions did not agree. Thus the walk did
  not see the old states. The correction: the walk reads the old states
  through the current knowledge.
- The map had transitions that occurred 1 time. An example: engine on
  lifted the vehicle in a life with almost no propellant. The walk
  followed those transitions to dead ends. The rule now: the walk
  prefers the transition that usually follows. That is a transition that
  the loop saw 2 times or more, and in half of the cases or more. The
  walk uses a transition that occurred 1 time only as the last option.

## The limits

- The vehicle got to the goal with thrust only, straight up. The run has
  no pitch over, no trajectory, and no return to the ground. The loop
  did not try the pitch and the yaw of the hand controller in flight.
  The explorer used all its lives before the explorer got to those
  states. More lives make a larger map.
- The DSKY was a dead branch for this goal, and the DSKY cost 33 presses
  in each state. The machine learned that the DSKY codes have no effect
  on the vehicle. But the machine had no method to stop the tries of the
  DSKY codes in each new state. The chooser is correct: the chooser
  tries each action.
- The loop recorded the writes and the channels of the computer, but the
  loop did not read the writes and the channels at each step. The writes
  and the channels are too large. The chain from a DSKY key to a routine
  to a channel to the vehicle is on the disk. The nudge run found that
  chain. The chain is not in the working state of this loop.
- The last option of the walk ("direct") uses the raw effect counts. For
  that reason, DSKY code 0 got 1 press here. The correct check for the
  last option is the prediction record. The walk does not do that check
  yet.
- The time detail went down from "the values of level 1 and 2" to "in
  motion: the direction". The constants are in `vehicle.csv` and in the
  pool of level 1. The gravity is a constant that appears as a steady
  second difference in the position. This goal did not need the
  constants. A trajectory will need the constants.

## Files

The files are:

- `launch.py`
- `vehicle.py` (the vehicle model with the pad start and the controls)
- `model.log` (the 3 lives)
- `goal.log`
- `effects-table.txt`
- `vehicle.csv` and `vehicle.out` (the goal life)
