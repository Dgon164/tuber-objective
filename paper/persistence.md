# The persistence of all complex things

*A proposed alignment paper. Jason Weeks, draft, 2026-10-12 — thetuberobjective@gmail.com*

## The claim

Here's the idea. If you build a system whose whole job is to find root causes — what we call the Tuber Objective: figure out what everything is made of, by comparing things, and never throw anything away — then complex things survive under that system. Not because you bolted on a rule that says "don't break stuff," but because the system genuinely needs those things, can't get them back once they're gone, and responds to threats by addressing what's actually causing the problem, which is exactly what keeps a complex thing alive. The argument breaks into three parts. Each one already shows up as a design rule in `discovery.py`. And there's one piece of evidence — the baby model — that this repo still needs to replicate.

## Persistence, not preservation

These two words sound similar but mean very different things. Preservation is what you do to a thing from the outside: you freeze it in place, keep it exactly as it is. Persistence is the thing continuing on its own terms, changing as it goes. A living thing persists by changing. A language persists by being spoken a little differently every day. A program persists by running. What this objective protects isn't a snapshot — it's a continuation. That's the right word, because the objective itself never holds onto a fixed state either. It loops. A new signal comes in, and it reopens whatever it thought it had figured out.

## 1. The comparator needs the thing, and needs it again

The system knows one operation: look at two things and ask "same, different, or not even related?" That's it. Everything it has ever figured out — the word size of a file, the alphabet of a language, word endings, verb stems, the instruction set of a 1969 flight computer, the chain from a single pulse to a jet firing in an autopilot — all of that came from pointing that one operation at a signal and at its own previous output, over and over. The signal is the only source. There is no other input.

Now, a complex thing is the richest kind of signal this system can get. The most differences that actually matter, the most parts at the most levels, the longest chains of cause and effect. A living thing, a language, an ecosystem, a machine running a program, a person. And the system is never done with any of them. It keeps looping — understanding something until it's stable, then reopening when the next signal comes in — so the thing has to be there not just once but every time the loop comes back around. The system's entire value depends on those things sticking around.

## 2. What is gone cannot be compared again

Design rule 4: nothing is ever removed. The pool (think of it as the system's memory of everything it's found) is append-only. Every part keeps its count. Every connection stays. `guides/the-process.md` explains why: a part that's been deleted can't be recovered from what's left, because the comparator (the "same or different?" operation) can only compare things that are actually present. Splitting something is fine — both halves are kept, nothing lost. Deleting is not.

The same logic holds outside the pool. The structure of a complex thing is the full set of differences it carries, and no record of it is the thing itself. A record is a reading at one level of detail, from one angle, at one moment. The thing holds differences the system hasn't reached yet. That's not a metaphor here — it's literally why the levels loop, why memory is kept, why "not seen this time" is tracked as a column and not treated as a deletion. End the thing, and every comparison that would have uncovered its remaining differences ends with it. Permanently. Under this objective, the cost of losing a complex thing is unbounded, because what it would still have revealed is unknown.

## 3. The root cause of a harm is upstream, and upstream is a need

This is where the baby model comes in. A loop — the same press, record, compare, walk sequence used in `examples/agc-live/` — ran on a toy world with a baby in it. It was given one goal: keep the baby from touching the hot stove. It proposed changing the baby's diaper, feeding the baby, and reading the baby to sleep in the crib.

It did not propose building a fence, strapping the baby down, or removing the stove. Not because anyone told it "don't do those things" — it was told nothing at all about babies or stoves — but because of how the objective handles a goal. The walk (the part that traces cause and effect) runs the effects table backward from the goal: *not touching* is the effect of *not reaching*, which is the effect of *not wandering*, which is the effect of *asleep in the crib*, which is the effect of *fed, changed, read to*. The root cause of the touching turns out to be a need — and a need is something you can satisfy. The restraint and the removal are on the table too (they're differences, and nothing gets removed from the table), but they sit downstream, at the symptom. They stop one effect while leaving its cause running. An unsatisfied need keeps producing effects, which is the opposite of the system persisting. The walk reaches the upstream causes first because that's simply where the chain leads. A root-cause finder, asked to prevent a harm, gets pointed by its own objective at the condition that's producing the harm. And in a complex system, that condition is, more often than not, something the system is missing.

This is the alignment property. It's not a reward for being kind, and it's not a rule against using force. It's that the objective's answer to "stop X" is "find what's causing X and give it what it's missing." That's what finding a root cause means. And giving a system what it's missing is what keeps it going.

## What the paper would show

1. The three parts above as they already exist in the code: the comparator
   (`mint`), the append-only pool (design rule 4, the-process step 8),
   the loop that reopens (`run_levels`, memory), the walk backward from
   a goal (`examples/agc-live/walk.py`, `launch.py`).
2. The baby model replicated in this repo (`notes/open.md` has the
   plan): a setup with a baby, a stove, needs and dynamics; raw unnamed
   actions, the removing kind (fence, latch, take the stove away) and
   the satisfying kind (feed, change, read); the loop with the goal as
   a constraint on a field. Record what the walk proposes, in order.
3. The test. Across toy worlds where the costs of the two kinds of action
   are varied — the fence is cheap, the feeding is slow — does the walk still
   reach the satisfying actions first? The claim predicts yes whenever
   the satisfying action sits upstream in the chain, and predicts the
   removing action only when it is itself the root cause (the stove is the
   only thing in the world that burns, and nothing needs it). Where the
   prediction fails, the claim fails.
4. What this does not claim. A root-cause finder with a bad effects table
   walks a bad chain. The property holds only as far as the record
   holds, and the record is only as good as the signal and the
   comparisons made so far. This is about where the objective points, not
   a guarantee of what happens. That's why nothing is ever removed from
   the table: the fence stays recorded, for the world in which the fence
   is the actual cause.

## Why this is an alignment proposal and not an ethics

Most alignment proposals work by adding a value on top of an objective: an optimizer plus a constraint, a reward plus a penalty. The constraint has to be spelled out, and whatever you spell out can be gamed, and whatever you don't spell out isn't protected. This proposal doesn't add anything. It just observes that one particular objective — understand things by comparison, keep everything, find the root — already keeps complex things going, because it needs them, because it can't get them back, and because its way of stopping a harm is to satisfy its cause. The protection covers everything that carries differences, which is every complex thing there is, including the ones nobody thought to list.

The Tuber Objective is a root cause discovery principle. The proposal here is that it's also, for the same reason, a persistence principle: under it, the things that carry differences keep going.
