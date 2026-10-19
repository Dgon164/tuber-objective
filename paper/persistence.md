# The persistence of all complex things

*A proposed alignment paper. Jason Weeks, draft, 2026-10-12 — thetuberobjective@gmail.com*

## The claim

The claim is as follows. If you make a system with 1 task only, complex
things continue under that system. The task is to find root causes. This
task is the Tuber Objective. The Tuber Objective has 3 rules:

- Find what each thing contains.
- Use comparison to find what each thing contains.
- Remove nothing.

The reason is not an extra rule that says "do not break things." The
complex things continue for 3 reasons:

- The system needs the complex things.
- The system cannot get a complex thing back after the complex thing is
  gone.
- When there is a threat, the system acts at the cause of the problem.

An action at the cause of the problem is exactly what keeps a complex
thing alive. The argument has 3 parts. Each part already exists as a
design rule in `discovery.py`. The evidence is 1 thing: the baby model.
This repository must still run the baby model again.

## Persistence, not preservation

The 2 words sound almost the same. The 2 words have very different
meanings. Preservation is an action that you do to a thing from the
outside. You stop all change in the thing. You keep the thing exactly as
the thing is.

Persistence is the continuation of the thing in its own way. The thing
changes as the thing continues. A thing that is alive persists when the
thing changes. A language persists when people speak the language a
little differently each day. A program persists when the program runs.

This objective does not protect a fixed state. This objective protects a
continuation. Continuation is the correct word, because the objective
itself also keeps no fixed state. The objective loops. A new signal comes
in. The objective then opens again each result that the objective found
before.

## 1. The need of the comparator for the thing, each time

The system knows 1 operation. The operation examines 2 things and gives
1 of 3 answers: the same, different, or not related. The system has no
other operation. Each result that the system found came from this 1
operation. The results include:

- the word width of a file
- the alphabet of a language
- the word endings
- the verb stems
- the instruction set of a flight computer from 1969
- the chain from 1 pulse to a jet that fires, in an autopilot

All of these results came from the 1 operation. The system pointed the
operation at a signal and at the previous output of the system, many
times. The signal is the only source. There is no other input.

A complex thing is the signal with the most content that this system can
get. A complex thing has:

- the most differences that are important
- the most parts at the most levels
- the longest chains of cause and effect

Examples of a complex thing are:

- a thing that is alive
- a language
- an ecosystem
- a machine that runs a program
- a person

The system is never done with a complex thing. The system loops. The
system examines a thing until the result is stable. The system then opens
the result again when the next signal comes in. Thus the thing must be
present each time the loop comes back, not only 1 time. The full value of
the system depends on 1 condition: the complex things remain.

## 2. No more comparisons of a thing that is gone

Design rule 4 says: the system removes nothing. The pool is the memory of
the system for each thing that the system found. The pool is append-only.
Each part keeps its count. Each connection stays.

The guide `guides/the-process.md` gives the reason. The system cannot get
a part back from what remains after the system removes the part. The
comparator is the "same or different?" operation. The comparator can
compare only things that are present.

A cut is permitted. To cut a part is to divide the part into 2 halves.
The system keeps both halves. Nothing is lost. A removal is not
permitted.

The same logic applies outside the pool. The structure of a complex thing
is the full set of differences that the complex thing carries. No record
of a complex thing is the complex thing. A record is what the system
reads at 1 level of detail, from 1 angle, at 1 moment. The complex thing holds differences
that remain for the system to find.

These differences are not a metaphor. These differences are the reason
for 3 design decisions:

- the levels loop
- the system keeps the memory
- the system records "not seen this time" in a column, not as a removal

If the complex thing ends, each comparison that can still show the
differences that remain also ends. The end is permanent. Under this
objective, the cost of the loss of a complex thing has no limit. The
reason is that what the complex thing can still show is not known.

## 3. The root cause of a harm: upstream, and a need

The baby model is the evidence for this part. A loop ran on a toy world
that contained a baby. The loop used the same sequence as
`examples/agc-live/`: press, record, compare, walk. The loop got 1 goal:
make sure that the baby does not touch the hot stove. The loop proposed
3 actions:

- change the diaper of the baby
- feed the baby
- read to the baby until the baby sleeps in the crib

The loop did not propose 3 other actions:

- make a fence
- hold the baby in place with a strap
- remove the stove

No one told the loop "do not do these actions." The loop got no
information about babies or stoves. The reason is the way that the
objective handles a goal.

The walk is the part that follows cause and effect. The walk goes
backward through the effects table from the goal. The chain is as
follows:

- *not touching* is the effect of *not reaching*
- *not reaching* is the effect of *not wandering*
- *not wandering* is the effect of *asleep in the crib*
- *asleep in the crib* is the effect of *fed, changed, read to*

The root cause of the touch is a need. A need is a thing that the system
can supply.

The restraint and the removal are also in the table. The restraint and
the removal are differences. The system removes nothing from the table.
But the restraint and the removal are downstream, at the symptom. The
restraint and the removal stop 1 effect. The cause of the effect
continues.

A need that is not supplied continues to make effects. Effects that
continue from a need are the opposite of the persistence of the system.
The walk reaches the upstream causes first, because the chain goes to the
upstream causes. A root-cause finder can get the task to prevent a harm.
The objective of the root-cause finder then points the root-cause finder
at the condition that makes the harm. In a complex system, the condition
is usually a thing that the system does not have.

This result is the alignment property. The alignment property is not a
reward for kindness. The alignment property is not a rule against the use
of force. The alignment property is the answer of the objective to
"stop X". The answer is: "find the cause of X, then give the cause what
the cause does not have."

This answer is what a root-cause search means. To give a system what
the system does not have keeps the system in operation.

## The plan for the paper

1. The 3 parts above, as the 3 parts already exist in the code:
   - the comparator (`mint`)
   - the append-only pool (design rule 4, the-process step 8)
   - the loop that opens results again (`run_levels`, memory)
   - the walk backward from a goal (`examples/agc-live/walk.py`,
     `launch.py`)
2. A new run of the baby model in this repository. The file
   `notes/open.md` has the plan. The run contains:
   - a setup with a baby, a stove, needs, and dynamics
   - raw actions with no names, of 2 types: the removal type (fence,
     latch, remove the stove) and the supply type (feed, change, read)
   - the loop, with the goal as a constraint on a field

   Record what the walk proposes, in order.
3. The test. The test uses many toy worlds. The costs of the 2 types of
   action change from toy world to toy world. For example, the fence is
   cheap, and the feed action is slow. The test asks if the walk still
   reaches the supply actions first.

   The claim says yes each time the supply action is upstream in the
   chain. The claim says that the walk reaches the removal action first
   only when the removal action is itself the root cause. An example is
   a world where the stove is the only thing that burns. In that
   world, nothing needs the stove. If a test result does not agree with
   the claim, the claim fails.
4. What the paper does not claim. A root-cause finder with a bad effects
   table walks a bad chain. The property is true only as far as the
   record is correct. The record is only as good as the signal and the
   comparisons that the system made so far. The paper is about the
   direction of the objective. The paper does not give a
   guarantee of what occurs.

   For this reason, the system removes nothing from the table. The fence
   stays in the record, for the world where the fence is the true
   cause.

## An alignment proposal and not an ethics: the reason

Most alignment proposals add a value on top of an objective. Examples
are an optimizer plus a constraint, and a reward plus a penalty. You must
write the constraint in full. A system can avoid a constraint that you
write. A thing that you do not write is not protected.

This proposal adds nothing. This proposal only says that 1 objective
already keeps complex things in operation. The objective has 3 rules:

- understand things by comparison
- keep each thing
- find the root

The objective keeps complex things in operation for 3 reasons:

- the objective needs the complex things
- the objective cannot get the complex things back
- the way that the objective stops a harm is to supply the cause of the
  harm

The protection covers each thing that carries differences. The things
that carry differences are all of the complex things that exist. The
protection also covers the complex things that no one thought to list.

The Tuber Objective is a principle for root cause discovery. This paper
proposes that the Tuber Objective is also a persistence principle, for
the same reason. Under the Tuber Objective, the things that carry
differences continue.
