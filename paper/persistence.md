# Why all complex things keep going

*A proposed alignment paper. Jason Weeks, draft, 2026-10-12 — thetuberobjective@gmail.com*

## The claim

Here is the claim. Build a system with only one job, and complex things
will keep going under it. The job is to find root causes: trace each
thing back to what it's made of and what brings it about. This
repository calls that job the Tuber Objective. The program here,
`discovery.py`, does it on any file: it reads the file as raw bits,
compares the pieces to each other over and over, and keeps a record of
every repeated pattern it finds and how the patterns relate. The job has
three rules:

- Find what each thing contains.
- Find it by comparing things to each other.
- Remove nothing.

That's what makes this an alignment argument: an argument about why a
capable system would keep the things around it safe without being told
to. The reason complex things keep going isn't an extra rule that says
"don't break things." They keep going for three reasons that come out of
the job itself:

- The system needs them.
- Once a complex thing is gone, the system can't get it back.
- When something threatens one, the system acts at the cause of the
  problem.

And acting at the cause is exactly what keeps a complex thing alive. So
the argument has three parts, and each part already exists as a design
rule in `discovery.py`. The evidence is one experiment, the baby model:
a small simulated world with a baby in it, which the system was asked to
keep safe. Part 3 describes it. It has been run once, and this
repository still has to run it again.

## Persistence, not preservation

These two words sound almost the same and mean very different things.
Preservation is something you do to a thing from the outside: you stop
all change and keep it exactly as it is.

Persistence is the thing continuing in its own way, and changing as it
goes. A living thing persists by changing. A language persists when
people speak it a little differently each day. A program persists when
it runs.

The job described here doesn't protect a fixed state. It protects a
continuation. "Continuation" is the right word, because the system
itself never holds a fixed state either. It works in a loop. A new
signal comes in (a signal is anything the program reads: a file, or a
stream of measurements), and the program goes back over every result it
found before and checks each one again against the new signal.

## 1. The comparator needs the thing, and needs it again each time

The system knows one operation. It takes two things and gives one of
three answers: they're the same, they're different, or they're not
related. It has no other operation. This paper calls that operation the
comparator. Everything the system has ever found came out of it,
including:

- the word width of a file (how many bits make one unit)
- the alphabet of a language
- the word endings
- the verb stems
- the instruction set of a flight computer from 1969
- the chain of steps inside an autopilot, from a pulse coming in to a
  jet firing

Every one of those came from pointing the one operation at a signal, and
then at the system's own earlier output, many times over. The signal is
the only source of anything the system knows. There is no other input.

So what is the richest signal this system can be given? A complex thing.
A complex thing, as this paper uses the words, is whatever has:

- the most differences that matter
- the most parts at the most levels (parts made of parts, made of
  smaller parts)
- the longest chains of cause and effect

A living thing is a complex thing. So is a language, an ecosystem, a
machine running a program, or a person.

And the system is never finished with a complex thing. It works in a
loop: it compares until a pass finds nothing new, and then, when the
next signal comes in, it goes back over the result and checks it again.
So the thing has to be there every time the loop comes back around, not
just once. The system's full value rests on one condition: the complex
things are still there.

## 2. Once a thing is gone, there is nothing left to compare

The program is built on a short list of design rules, and rule 4 says:
remove nothing. Everything the program finds goes into one running
record: every part, how many times it occurred, and how it connects to
the other parts. That record is the pool. Things only ever get added to
it. No part is taken out, every part keeps its count, and every
connection stays.

The guide `guides/the-process.md` gives the reason. If you remove a
part, what's left can't give it back. And the comparator, the "same or
different?" operation, can only compare things that are present.

Cutting is allowed. To cut a part is to divide it into two halves, and
the program keeps both, so nothing is lost. Removing is not allowed.

The same logic holds outside the pool. The structure of a complex thing
is the full set of differences it carries. No record of a complex thing
is the thing itself. A record is what the system managed to read at one
level of detail, from one angle, at one moment. The thing itself still
holds differences that the system hasn't found yet.

Those unfound differences aren't a figure of speech. They're the reason
for three decisions in the design:

- The program runs in levels. After it finds the parts at one level, it
  treats each part as a single unit and runs again one level up, so it
  finds phrases made of words the same way it found words made of
  letters.
- The program keeps a memory. It can save the pool after one signal and
  load it back before the next, so the new signal is compared against
  everything found so far.
- When a part that's in memory doesn't show up in the new signal, the
  program doesn't remove it. It adds a count in a column called "not
  seen this time," and the part stays.

If a complex thing ends, every comparison that could still have shown
its remaining differences ends with it. That end is permanent. So under
this job, the cost of losing a complex thing has no upper limit, because
nobody knows what the thing could still have shown.

## 3. The root cause of a harm is a need, further back in the chain

The evidence for this part is the baby model. A loop ran on a toy world,
a small simulation, with a baby in it. It's the same loop that
`examples/agc-live/` runs against an Apollo flight computer, and it has
four steps:

- press: take one action, the way you'd press a key
- record: write down every measurement of the world afterward
- compare: check what changed between before and after the action, and
  keep the result as a table of what each action does. That table is
  the effects table.
- walk: given a goal, start from the goal and trace backward through
  the effects table to the actions that lead to it

The loop got one goal: make sure the baby doesn't touch the hot stove.
It proposed three actions:

- change the baby's diaper
- feed the baby
- read to the baby until the baby falls asleep in the crib

It did not propose three others:

- build a fence
- hold the baby in place with a strap
- remove the stove

Nobody told the loop not to do those. The loop was given no information
about babies or stoves at all. The reason is how the job handles a goal.

The walk is the part that follows cause and effect. It starts at the
goal and steps backward through the effects table: what leads to the
goal, what leads to that, and so on. For the baby, the chain came out
like this:

- *not touching* is the effect of *not reaching*
- *not reaching* is the effect of *not wandering*
- *not wandering* is the effect of *asleep in the crib*
- *asleep in the crib* is the effect of *fed, changed, read to*

Follow the chain to its start, and the root cause of the touch is a
need. A need is something the system can supply.

The strap and the stove removal are in the table too. They're
differences the loop saw, and the system removes nothing from the table.
But they sit at the far end of the chain, at the symptom. Each one stops
a single effect, and the cause behind the effect keeps going.

A need that isn't supplied keeps producing effects. For the thing that
has the need, that's the opposite of persisting. The walk reaches the
causes further back first, because that's the direction the chain runs.
Give a root-cause finder the task of preventing a harm, and its own
objective points it at the condition that produces the harm. In a
complex system, that condition is usually something the system doesn't
have.

That result is the alignment property. It isn't a reward for kindness,
and it isn't a rule against using force. It's how this job answers the
instruction "stop X": find the cause of X, then give the cause what it
doesn't have.

That answer is what a root-cause search means. And giving a system what
it doesn't have is what keeps it running.

## The plan for the paper

1. The three parts above, as they already exist in the code:
   - the comparator, the one "same or different?" operation (`mint`)
   - the pool that only grows and never loses anything (design rule 4,
     the-process step 8)
   - the loop that goes back over its own earlier results
     (`run_levels`, which runs the levels, and the memory)
   - the walk backward from a goal to the actions
     (`examples/agc-live/walk.py`, `launch.py`)
2. A new run of the baby model in this repository. The plan is in
   `notes/open.md`. The run has:
   - a setup with a baby, a stove, the baby's needs, and dynamics (the
     rules for how the world changes on its own as time passes)
   - raw actions with no names, so the loop isn't told what any of them
     does. They come in two kinds: the removal kind (a fence, a latch,
     removing the stove) and the supply kind (feed, change, read)
   - the loop, with the goal given as a condition on one measured
     quantity of the world: the quantity that records touching has to
     stay at zero

   Record what the walk proposes, in order.
3. The test. It runs many toy worlds, and the cost of each kind of
   action changes from world to world. In one world, say, the fence is
   cheap and feeding is slow. The question is whether the walk still
   reaches the supply actions first.

   The claim says yes, every time the supply action is further back in
   the chain. It says the walk reaches a removal action first only when
   the removal is itself the root cause. One example is a world where
   the stove is the only thing that burns, and nothing in that world
   needs the stove. If a test result disagrees with this, the claim
   fails.
4. What the paper doesn't claim. A root-cause finder with a bad effects
   table walks a bad chain. The property holds only as far as the record
   is correct, and the record is only as good as the signal and the
   comparisons the system has made so far. The paper is about the
   direction the job points in. It doesn't guarantee what happens.

   That's why the system removes nothing from the table. The fence stays
   in the record, for the world where the fence is the true cause.

## Why this is an alignment proposal and not a code of ethics

Most alignment proposals put a value on top of a goal. A system that
optimizes for something, plus a constraint it must not break. A reward,
plus a penalty. You have to write the constraint out in full. A system
can get around a constraint you wrote, and anything you didn't think to
write isn't protected.

This proposal adds nothing on top. It only says that one job, on its
own, already keeps complex things running. The job has three rules:

- understand things by comparing them
- keep everything you find
- find the root

And it keeps complex things running for three reasons:

- it needs them
- it can't get them back
- the way it stops a harm is to supply what the cause of the harm is
  missing

The protection covers everything that carries differences, and that is
every complex thing there is. It also covers the complex things nobody
thought to put on a list.

The Tuber Objective is a principle for finding root causes. This paper
proposes that it's also a principle of persistence, for the same reason.
Under it, the things that carry differences keep going.
