# Phase D: a mission in steps, with retries

2026-10-20. The machine is the vehicle model from Phase C with three
changes: the moon is round, the vehicle has two stages, and it can be
destroyed. The loop is the one from Phase C with a mission to complete,
written as targets on the instruments, and permission to try again.

Phase C ended with one lift-off from one run. This phase asks for the
whole climb: lift off, turn over, burn the first stage out, drop it,
light the second, and cut the engine in an orbit. The loop is told what
each step must look like on the instruments. It is told nothing about
which control does what, or in what order.

## What went in

**The vehicle** (`vehicle.py`). The same rigid body, jets, platform and
switches as Phase C. New:

- Gravity pulls toward the moon's center and weakens with height. At
  the right sideways speed the vehicle stays up. Two instruments report
  the path the vehicle is on right now, the way a cockpit display
  would: the lowest point it will reach and the highest. A lowest point
  below zero means the path hits the ground.
- Two stages. The first has a throttleable engine (4.7 kN to 43.9 kN,
  10 kN per press of throttle up) and 5,000 kg of propellant. The
  second has a fixed 15.6 kN engine and 1,200 kg. One control, `stage`,
  drops the first stage: the engine goes off, the mass drops. Neither
  stage alone has the speed for orbit.
- Death. Hitting the ground above 10 m/s, or tumbling past 30 degrees a
  second, destroys the vehicle. So does running out of propellant in
  every stage on a path into the ground or away from the moon. For the
  next 30 seconds every instrument reads null. Then a new vehicle is on
  the pad with full tanks, and the clock keeps running. The nulls and
  the jump back to the pad are the only signal that something went
  wrong. Nothing names the cause.
- One more message on the control socket, `ABORT`. It is not a
  control. It is mission control giving the vehicle up, and it kills
  the vehicle the same way.

**The instruments.** A row every 100 ms with 20 fields: three angles,
three turn rates, altitude, two speeds (sideways, up), thrust, two jet
words, two counts for the flight computer, propellant in the current
stage, armed, engine on, stage number, and the lowest and highest
points of the current path.

**The controls.** Arm, engine on, engine off, throttle up, throttle
down, a pulse each way about three axes, stage. And one action that is
not a control: `wait`, which presses nothing for one step.

**The mission** (`mission.txt`). Five phases. Each is a list of targets
on instrument fields, in the order they are to be worked:

```
liftoff:    f17 == 0 ; f9 > 4000 ; f6 > 5
pitchover:  f17 == 0 ; f1 > 10800 ; f1 < 11600 ; f4 == 0
burnout:    f17 == 0 ; f14 < 1
staged:     f17 == 1 ; f16 == 1
orbit:      f18 > 100 ; f19 < 3000 ; f16 == 0
```

In words: on the first stage, thrust above 40 kN, altitude above 50 m.
Still on the first stage, pitch angle between 108 and 116 degrees and
pitch rate zero. Still on the first stage, propellant gone. On the
second stage with its engine on. Lowest point of the path above 10 km,
highest below 300 km, engine off.

This is a flight plan, the kind an ascent is flown to: a throttle
setting, an attitude, a burnout, a staging, an insertion. The numbers
in it come from flying the model by hand (`scripted.py`, and a scan of
pitch angles against the engine-cut window): with a 5-second step
between presses, the turn has to start within about 25 seconds of
lift-off and stop between 108 and 116 degrees, or the second stage
cannot bring the low point of the path above the ground before the
high point runs away. The loop is given the targets. It has to find the
presses.

`mission-bare.txt` is the same mission without the pitch-over phase,
for comparison.

**The loop** (`mission.py`). Phase C's loop, plus what is listed under
"What it took" below. A run is `python mission.py RUN_DIR STEPS
--no-agc`: the vehicle flies 5 seconds per press and stands still
while the loop thinks, so one step is 5 seconds of flight however long
the loop takes. The flight computer is left out of these runs. It adds
33 DSKY keys to the action list and its own state to every row, and it
has no part in the manual ascent; the point here is the learner.

## What the loop does, each step

It reads the rows since the last step. If they are null, it waits for
the pad, closes the attempt, and starts the next one.

It finds the phase it is in: the first phase whose targets are not all
met. Within that phase, the first target not met is the one it works
on. Targets before that one that ask for an exact value and are met are
targets to keep: a press known to move that field is not made.

It describes where it is as a state: for each instrument, either the
direction it is moving in (up, down, still) if that instrument has ever
been seen moving, or its value if it has not.

Then it chooses a press, in this order:

1. If the field being worked on is already moving the needed way, or
   already holds a value that meets the target, it waits.
2. If it has seen a state that meets the target, and a single press
   that led there from a state like this one, it makes that press.
3. If its record says a press moves the needed field the needed way,
   and the condition it has learned for that press holds here, it makes
   that press. This is a rule. A rule comes from the effects table:
   every press, in every state, with what moved after it. A condition
   comes from the states where a press had an effect and the states
   where it did not: the one instrument whose values separate the two
   sets.
4. If it has seen a state that meets the target and a longer path of
   presses that led there, it makes the first press of the path.
5. If a rule has a condition that does not hold here, it looks for a
   press that would bring the condition about, up to three deep.
6. If any press has ever moved the needed field the needed way,
   anywhere, it makes it.
7. Otherwise it explores: the press tried least often in this state.

A press is left out of all of these if, in this state, it has killed
the vehicle more often than not; or if attempts that made it here,
while working on this phase, missed the phase clearly more often than
attempts in general did; or if it has ever moved a field that is to
be kept.

After the press it records what moved, the transition from the state
before to the state after, and whether the vehicle died. Dying is
recorded as an effect like any other, on a virtual instrument, alive.

When the attempt ends, every press it made is credited against every
phase: an attempt that reached a phase marks its presses as fine for
that phase, an attempt that did not marks them as doomed for it. An
attempt ends at death, at mission complete, or when 300 steps pass
without a new phase, in which case the loop sends `ABORT`.

## What happened

Run A, the mission above, `runs/A.log`: 63 attempts in 5,275 steps,
110 seconds of wall clock. 62 complete. Every attempt from the second
one on.

| attempt | steps | outcome |
|---|---|---|
| 1 | 206 | lift-off, pitch-over, burnout, staging; then tumbling in the orbit phase |
| 2 to 63 | 81 each | mission complete, orbit 29 by 108 km (38 by 109 km in attempts 2 and 3), 1,046 kg of second-stage propellant left |

Attempt 1, press by press. On the pad the loop explored: arm, engine
on, engine off, throttle up. From the second throttle press it had a
rule, "throttle up raises thrust", and used it, though it also pressed
engine on ten times in a row for the same target before the rule for
engine on was narrowed to "when thrust is zero". Lift-off at step 20.
In the pitch-over phase it explored again: throttle down, +roll, −roll,
+pitch. +pitch moved the pitch angle, so the loop held, 53 steps of
wait, and pressed −pitch at 108 degrees. Burnout came while it waited.
It explored once more for the staging phase and found `stage` on the
third press, then lit the engine by rule. In the orbit phase it waited
while the lowest point of the path rose, and the lowest point passed
10 km at step 119. But the turn had come late, the vehicle was coming
down at 200 m/s while it gained speed, and the highest point of the
path was past 300 km by then. The target became "highest point below
300 km", and the one rule the loop had for that, read off a coincidence
earlier in the same attempt, named +yaw. It pressed +yaw 74 times, with
waits between, and the vehicle tumbled.

Attempt 2 and after, the same 81 presses each time: six for lift-off
(arm, engine on, four throttle presses; the walk gave one, rules the
rest), +pitch by rule, 52 waits, −pitch by rule at 108 degrees, 13
waits to burnout, `stage` by rule, engine on by rule, five waits, engine
off by rule. 405 seconds of flight. The one press that moved the pitch
angle, the one that stopped it, the one that dropped the stage, the
one that lit the engine, the one that cut it: each was found once and
reused.

What was in memory at the end: 135 states, 171 transitions between
them, 303 state-and-press pairs with their effects, 17 conditions. The
useful ones: throttle up raises thrust when thrust reads 467, 1467,
2467 or 3467 (the four levels below full); engine on raises thrust,
drains propellant and sets the engine flag when thrust reads zero.
Ten of the 17 are about +yaw, read off the 105 pulses of attempt 1.
One says that waiting raises the lowest point of the path when that
point reads about −1,737 km: the path rising on its own during the
burn, credited to the press made at the time.

## Without the pitch-over phase

Run B, the same mission without the pitch-over phase, `runs/B.log`:
28 attempts in 3,699 steps. None complete.

| attempt | steps | outcome |
|---|---|---|
| 1 | 138 | lift-off, burnout, staging; lost in the orbit phase with no propellant |
| 2 to 10 | 121 to 142 | the same |
| 11 to 28 | 132 each | the same presses exactly, the same loss |

Every attempt lifts off at step 20, burns straight up to 200 km at
1,400 m/s, stages at 260 km, and lights the second stage. The orbit
phase then asks for the lowest point of the path above 10 km. Nothing
in the mission before that asked for sideways speed. The loop finds
+pitch and +yaw by exploring, reads rules off what followed them, and
burns the second stage with the lowest point still 1,700 km below
ground. The second stage alone has about 1,350 m/s to give; a path
that stays above the ground needs about 1,650 m/s sideways at that
height.

From attempt 11 on the loop makes the same 132 presses every time. The
walk replays the path it knows, the attempt ends the same way, and the
credit by outcome has nothing to add: every attempt fails the same
phase, so no press stands out from the rest. Nothing new is tried.

## What it took

Phase C's loop did not do this on its own. Each of these was added
after a run showed it was needed, in this order:

- **Retries.** The loop had to stop treating the first death as the
  end. Null rows mark a death; the first live row after them marks the
  pad and a new attempt. Everything learned carries over.
- **Death as an effect.** Without it, the press before a crash looked
  like any other press.
- **An end to every attempt.** A vehicle that staged on the pad and
  burned its second stage straight up took hundreds of steps to come
  down. Now a vehicle with no propellant left on a path into the ground
  is lost at once, and an attempt that makes no progress for 300 steps
  is called off. Credit by outcome needs attempts to end.
- **Targets in written order.** Working on all unmet targets of a phase
  at once made the loop keep pressing +pitch while already turning,
  because "rate zero" was unmet too. The first unmet target is the one
  worked on; the ones after it wait.
- **Keeping what is met.** The loop pressed `stage` on the pad as its
  twelfth exploration press, and from then on the first phase (which
  asks for stage 0) could not be met in that attempt. Now a press known
  to move a kept field is not made.
- **Credit by outcome.** A press that only shows up in failed attempts,
  clearly more often than attempts fail in general, is not made again
  in that state for that phase. Plain failure counts did not work: in
  the early attempts every press is in a failed attempt.
- **A rule before a long walk.** The walk replays a path exactly as it
  was once seen, side trips included. The first time the loop found the
  pitch-over it had pressed throttle down, +roll, −roll and then +pitch,
  and the walk replayed all four every attempt, 15 seconds the turn did
  not have. A rule that names one press now comes before a walk longer
  than one.
- **A press known not to work here.** A rule that says "engine on
  raises altitude" (true on the second stage) kept being tried on the
  pad on the first stage. A press made twice in a state without the
  effect is not proposed by that rule in that state again.
- **Exploration order.** An action pressed once with no effect was
  being sorted behind everything else for the rest of the run, so the
  throttle and the hand controller were never tried where they would
  have worked. The least-tried-here count now comes first.
- **A hold that holds.** Holding meant pressing the action with the
  fewest recorded effects, so that the loop would find out for itself
  which action does nothing. Early on that was an untried pulse. Later,
  with the effects of fields that move on their own credited to
  whatever was pressed, it was `stage` once and `engine off` once, each
  of which ended the attempt. Holding is now `wait`.
- **A clock that waits.** With the vehicle on the wall clock at 100
  times real time, the loop's thinking time grew with its memory, from
  a twentieth of a second a step to seconds a step by attempt 25, and
  a press meant for 5 seconds after the last one landed 300 seconds
  after it. A run of 73 attempts completed no mission: the first 23
  reached staging, the rest flew straight up. The vehicle now moves
  only when the loop tells it to, 5 seconds per press.
- **A jump is not a movement.** A hand-controller press changes the
  turn rate over two instrument rows. The loop called that "moving",
  and a second press in the next window read as "still moving", that
  is, no effect. So the hold step took +pitch for a press that did
  nothing, pressed it six times, and the vehicle turned six times too
  fast. A field now counts as moving when it changes on three rows or
  more in a window.
- **The vehicle, three times.** Angles were packed in radians where the
  row said degrees, so 80 degrees read as 1.4. A hand-controller pulse
  was timed by the clock and came out 9 or 10 physics steps long, so a
  press each way left a residual turn rate and the loop could never
  make the rate read zero; pulses are now a fixed step count. Throttle
  presses were 5 kN, and the climb to full thrust put the pitch-over
  too late; they are 10 kN.

## Not done

- The flight plan's numbers come from flying the model by hand. The
  loop does not find the attitude or the timing on its own. Run B shows
  what happens without them.
- When every attempt fails the same way, the loop repeats itself. Run
  B from attempt 11 on. The credit by outcome needs some attempts to
  reach a phase and some not; with none reaching it, it is silent.
- The orbit the loop reaches is the first one that meets the targets,
  29 by 108 km, with 1,046 kg of propellant left. Nothing asks it to do
  better, and it does not.
- The flight computer is not in these runs.
- Conditions are one instrument deep. A death that needs two
  instruments to predict (turning, and losing height) is not learned as
  a condition.
- The step is 5 seconds of flight. The engine-cut window is about 10
  seconds wide. Finer steps are untested.
