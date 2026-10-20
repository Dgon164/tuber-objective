# Phase E: quantities, a grade of its own, and plans tried in its head

2026-10-20. The vehicle and the mission file are Phase D's. The loop is
new. Phase D's loop knew each effect as a direction and walked through
states it had seen; it could repeat one trajectory and nothing else.
This loop keeps the amounts, grades any state by how many presses it is
from the targets, and chooses by trying plans with amounts in them
against its own model of what happens.

## What went in

- The vehicle from `../phase-d/vehicle.py`: round moon, two stages,
  death, instruments that go null, and the lockstep clock. 5 seconds
  of flight per press.
- A mission file in Phase D's form, plus one line for the second
  measure. `mission.txt` asks for an orbit and nothing else:

  ```
  orbit:   f18 > 100 ; f19 < 3000 ; f16 == 0
  prefer:  steps least
  ```

  The lowest point of the path above 10 km, the highest below 300 km,
  the engine off. Then, among ways of getting there, the fewest steps.
  The second measure can be anything a target can be: `steps most`,
  `f14 most` (the most propellant left), `f19 == 1000` (a highest point
  as close to 100 km as possible).
- `mission-plan.txt` is Phase D's five-phase flight plan with the same
  last line, for comparison.
- `grade.py`, the loop.

## What the loop does, each step

It reads the rows the vehicle wrote during the last step and adds them
to everything it has seen. Every 25 steps it refits its model from all
of it.

**The model** has five parts, all read off the rows:

- What a press does: the jump in every instrument in the first 0.3
  seconds after the press, beyond what the instruments were doing
  already. Kept per press made, with the row it was made from. When
  the loop wants to know what a press would do now, it looks up the
  recorded press made from the most similar row.
- How the instruments move between presses: for any row, the change of
  every instrument over the next 2.5 seconds, as a line fitted through
  the 40 recorded rows most like it. Near rows it has seen, this is
  what happened there. Away from them, it is the nearest trend carried
  on, and never more than twice the biggest change ever seen.
- Things that happen on their own when a reading crosses a line: a
  jump in an instrument that only ever jumps, during a step with no
  press. The thrust dropping to zero when the propellant runs out is
  one.
- Where it dies: the rows that came just before a death, against a
  sample of rows it lived through. An imagined row is dead if it is
  more like a death row than any live one. And the ground: arriving at
  the ground faster than the slowest fatal arrival kills.
- The most each instrument has ever moved in one step, each way.

**The grade** of a row is how many presses it is from the targets of
the phase it is in: for each target not met, the gap divided by the
most that instrument has ever moved that way in one step, plus one.
Zero means every target is met. The targets of earlier phases that ask
for an exact value count too, so that losing one is graded. The loop
writes this grade from its own record.

**A plan** is a list of presses with amounts: `engine on x1, throttle
up x4, +pitch x1, wait 50, -pitch x1`. The loop runs each plan through
its model for up to 100 steps, pressing where the plan says and letting
the instruments move as the model says, and grades every step against
the phase the imagined vehicle is in: when a phase's targets are all
met in the imagination, the next phase's targets take over. A plan is
judged first by how many phases it leaves unreached, then by whether
it dies, then by the lowest grade it reached in the furthest phase,
then by the second measure. So a plan that cuts the engine during the
turn, which the turn's own targets do not mind, is judged by what that
does to the burn and the orbit after it.

Each step the loop tries about sixty plans: doing nothing, the rest of
the plan it chose last step, each single press, and variants made by
changing an amount, swapping a press, adding or dropping one. If the
best of them reaches the end, gets a phase further than doing nothing,
avoids a death that doing nothing meets, or ends at least one press
closer, it makes that plan's first press, reads the instruments, and
plans again from wherever it is. Otherwise it explores: among the
presses the model does not say lose a phase or kill, the one never made
in a state like this, then the one whose past attempts got closest.

An attempt ends at death, at mission complete, after 150 steps without
a new phase, or 30 steps after an exact target has been lost with
nothing on record that ever moved it back. The vehicle is given up each
time and the next attempt starts from the pad. A vehicle given up is
not recorded as a death; the model learns deaths only from the vehicle's
own.

## What happened

Four launches of the two runs, with the loop changed between them.
No launch completed the mission in either run. Phase D's loop, with
the flight plan, completed it 62 times in 63 attempts.

| launch | steps each | flight plan: attempts, best phase of 5 | bare: attempts, best low point | what was wrong, fixed before the next |
|---|---|---|---|---|
| 1 | 2,000 | 22, phase 2 twice | 17, never above the ground | a vehicle given up on the pad was recorded as a death, so the pad graded as fatal and any press beat doing nothing; plans were judged on the current phase only; exploration could press anything |
| 2 | 2,000 | 23, phase 2 twice | 17, lowest point −1,590 km | an abort rule for a lost exact target fired on "engine off", an end target the engine has to move away from first |
| 3 | 2,200 of 3,000 | 22, phase 2 twice | 21, −1,457 km | exploration still pressed `stage` on the pad: the guard compared only phases-left and dead-or-not |
| 4 | 3,000 | 34, phase 2 eight times | 24, −1,511 km | see below |

Launch 4, flight plan, `runs/E-plan.log`, 34 attempts in 2.6 hours:

```
reached nothing   4   (3 on the pad, 1 at 10 m)
lift-off only    22   (crashed 13, called off 9)
the turn too      8   (crashed 6, called off 2)
burnout, staging, orbit   0
```

Lift-off is planned, not explored, from attempt 4 on: arm, engine on,
throttle up four times, in 6 to 8 presses. The turn is reached by
tumbling. In two of the three turns examined, the pitch reading entered
108 to 116 degrees with the rate at zero while the vehicle was already
falling at 270 m/s, after roll and yaw presses had swung the reading
through the window. The one sound turn, attempt 22 (pitch 111 degrees,
climbing at 178 m/s), was followed by nine presses, five of them
exploration, the last of which was `stage` at 29 km; that lost the
burnout phase's "stage 0" and the attempt was called off.

Launch 4, bare mission, `runs/E-bare.log`, 24 attempts: 14 ended on
the pad, called off after 150 steps; 7 crashed; 3 ran out of propellant
with the lowest point of the path at −1,684, −1,665 and −1,511 km. The
orbit needs +10 km. Across all four launches the best was −1,457 km.

The model at the end of launch 4 (flight plan): 1,500 drift samples
kept, 2,785 presses recorded, 18 deaths, ground fatal above 10.1 m/s
(the vehicle's rule is 10), and no event ever recorded: the first stage
was never burned out in any attempt.

## What the results say

- The pieces work as pieces. The jump table plans a lift-off in six
  presses. The ground rule is learned to within a tenth of a metre per
  second. Plans with amounts are found and executed and re-planned.
- The grade divides each gap by the biggest one-step change ever seen.
  For propellant, the biggest change ever seen is the drop when a stage
  is dropped, so the grade reads "burnout is one press away" when it is
  seventy steps of burning away. No plan delivers it, the loop falls
  back to exploring, and exploring in the middle of a good flight is
  what wrecked attempt 22. The rate has to be one the vehicle can
  sustain.
- The local line through nearby rows extrapolates along slopes it has
  no business trusting. The planner believed yaw and roll pulses helped
  (launch 3: 473 presses of −yaw against 154 of throttle up), pressed
  them, and the new rows carried the same noise. More ridge toward the
  flat line and more neighbours are the plain remedy; a model that
  checks its own predictions against what followed is the real one.
- The bare mission has a trap the grade cannot see. Pressing `stage` on
  the pad lights the fixed-thrust second stage at once, and those
  flights get the best grades, so the outcome credit steers exploration
  into it. The second stage alone has about 1,350 m/s and orbit needs
  about 1,650 sideways. Nothing in the targets says that the 5,000 kg
  of first-stage propellant is the resource being thrown away; the
  flight plan said so ("stage 0" during the burn), the bare mission does
  not. And since the first stage was never burned out, the model has no
  record of what a full two-stage ascent looks like, so no plan can
  imagine one.
- The flight plan's targets can be met by a tumble. Phase D's loop
  never found that out because it only ever replayed one path. This
  loop searches, and a search finds the letter of a target.

## Not done

- No orbit. Four launches, 0 of 93 attempts with the flight plan, 0 of
  79 without.
- The three changes the results call for are not made: a sustained
  rate in the grade; a model that discounts its own slopes where its
  predictions keep failing; no exploration in the middle of a flight
  that a plan is carrying.
- The second measure (`prefer`) has never come into play, since no plan
  reached the end.
- The step is 5 seconds and the planning costs about 3 seconds of
  wall clock per step, so a launch is two and a half hours.
