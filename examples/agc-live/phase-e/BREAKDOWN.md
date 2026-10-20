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
its model for up to 120 steps, pressing where the plan says and letting
the instruments move as the model says, and grades every step. A plan
that reaches grade zero is judged by the second measure at that moment.
One that does not is judged by the lowest grade it reached and how
soon. One that dies is judged below all of those.

Each step the loop tries about a hundred plans: doing nothing, the rest
of the plan it chose last step, each single press, and variants made
by changing an amount, swapping a press, adding or dropping one. If the
best of them beats doing nothing, it makes that plan's first press,
reads the instruments, and plans again from wherever it is. If nothing
beats doing nothing, it explores: the press tried least often in a
state like this one.

## What happened

todo: runs in progress.

## Not done

todo
