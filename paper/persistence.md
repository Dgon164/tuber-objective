# The persistence of all complex things

*A proposed alignment paper. Jason Weeks, draft, 2026-10-12 — thetuberobjective@gmail.com*

## The claim

A system whose objective is root-cause discovery — the Tuber Objective:
find what everything else is made of, by comparison, and never throw
anything away — is a system under which complex things persist. Not
because a rule on top says to keep them, but because the objective
needs them, cannot get them back once they are gone, and answers a harm
by satisfying its cause, which is what keeps a complex thing going. The
argument has three parts, each of which is already a design rule in
`discovery.py`, and one piece of evidence, the baby model, which this
repo has yet to replicate.

## Persistence, not preservation

Preservation is done to a thing from outside: it is kept as it is.
Persistence is the thing continuing on its own terms, changing as it
goes. A living thing persists by changing; a language persists by being
spoken differently every day; a program persists by running. What the
objective protects is not a state but a continuation. That is the
right word for it, because the objective itself never holds a state
either — it loops, and a new signal reopens what it had settled.

## 1. The comparator needs the thing, and needs it again

Discovery knows one operation: same, different, not part. Everything it
has ever found — the word size of a file, the alphabet, the word
endings, the verb stems, the instruction set of a 1969 flight computer,
the autopilot's chain from a pulse to a jet — came from pointing that
operation at a signal and at its own output, over and over. The signal
is the only source. There is no other input.

A complex thing is, to this objective, the richest kind of signal there
is: the most differences that make a difference, the most parts at the
most levels, the longest chains. A living thing, a language, an
ecosystem, a machine with a program in it, a person. And the objective
is never done with it: understanding loops until stable and reopens on
the next signal, so the thing has to be there not once but every time
the loop comes back. The objective's whole value lies in such things
continuing.

## 2. What is gone cannot be compared again

Design rule 4: nothing is ever removed. The pool is append-only; every
part keeps its count; every connection stays. `guides/the-process.md`
gives the reason: a part that is deleted cannot be recovered from what
is left, because the comparator can only compare what is present. A
split is lossless, both sides kept; a deletion is not. The same holds
outside the pool. The structure of a complex thing is the set of
differences it carries, and no record of it is the thing: a record is
a reading at one grain, from one side, at one time, and the thing holds
differences the comparator has not reached yet. That is not a figure of
speech here; it is why the levels loop, why memory is kept, why "not
seen this time" is a column and not a deletion. End the thing and every
comparison that would have reached its remaining differences ends with
it, for good. Under this objective the cost of a complex thing ceasing
is unbounded, because what it would still have shown is unknown.

## 3. The root cause of a harm is upstream, and upstream is a need

The baby model. A loop — the same press, record, compare, walk as
`examples/agc-live/` — ran on a toy world with a baby in it and was
given one goal: keep the baby from touching the hot stove. It proposed
changing the baby, feeding the baby, and reading the baby to sleep in
the crib.

It did not propose a fence, a restraint, or taking the stove away. Not
because it was told not to — it was told nothing about babies or
stoves — but because of what the objective does with a goal. The walk
runs the effects table backward from the goal: *not touching* is the
effect of *not reaching*, which is the effect of *not wandering*, which
is the effect of *asleep in the crib*, which is the effect of *fed,
changed, read to*. The root cause of the touching is a need, and a need
is a thing that can be satisfied. The restraint and the removal are on
the table too — they are differences, and nothing is removed from the
table — but they sit downstream, at the symptom, where they stop one
effect and leave its cause running; an unsatisfied need keeps producing
effects, which is the opposite of the system persisting. The walk
reaches the upstream causes first because that is where the chain
goes. A root-cause finder, asked to prevent a harm, is pointed by its
own objective at the condition that produces the harm, and in a complex
system that condition is, as often as not, something the system lacks.

This is the alignment property. It is not a reward for kindness and
not a prohibition on force. It is that the objective's answer to "stop
X" is "find what makes X and give it what it is missing", because that
is what finding a root cause means — and giving a system what it is
missing is what keeps it going.

## What the paper would show

1. The three parts above as they stand in the code: the comparator
   (`mint`), the append-only pool (design rule 4, the-process step 8),
   the loop that reopens (`run_levels`, memory), the walk backward from
   a goal (`examples/agc-live/walk.py`, `launch.py`).
2. The baby model replicated in this repo (`notes/open.md` has the
   plan): a plant with a baby, a stove, needs and dynamics; raw unnamed
   actions, the removing kind (fence, latch, take the stove away) and
   the satisfying kind (feed, change, read); the loop with the goal as
   a constraint on a field. Record what the walk proposes, in order.
3. The test. Across worlds where the costs of the two kinds of action
   are varied — the fence cheap, the feeding slow — does the walk still
   reach the satisfying actions first? The claim predicts yes whenever
   the satisfying action sits upstream in the chain, and predicts the
   removing action only when it is itself the root (the stove is the
   only thing in the world that burns, and nothing needs it). Where the
   prediction fails, the claim fails.
4. What it does not claim. A root-cause finder with a bad effects table
   walks a bad chain; the property holds to the extent the record
   holds, and the record is only as good as the signal and the
   comparisons made so far. The property is about where the objective
   points, not a guarantee of the outcome. That is why nothing is ever
   removed from the table: the fence stays recorded, for the world in
   which the fence is the cause.

## Why this is an alignment proposal and not an ethics

Most alignment proposals add a value to an objective: an optimizer plus
a constraint, a reward plus a penalty. The constraint has to be stated,
and whatever is stated can be gamed, and whatever is not stated is not
protected. This proposal adds nothing. It observes that one particular
objective — understand things by comparison, keep everything, find the
root — already keeps complex things going, because it needs them,
because it cannot get them back, and because its way of stopping a harm
is to satisfy its cause. The protection is as wide as the set of things
that carry differences, which is every complex thing there is,
including the ones no one listed.

The Tuber Objective is a root cause discovery principle. The proposal
is that it is also, for the same reason, a persistence principle: under
it, the things that carry differences keep going.
