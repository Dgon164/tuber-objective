# The process

This guide is the general method behind Discovery, written so you can
use it on any problem, not only on files. The whole method rests on one
operation: take two things, find what they share, and keep what's left
over. Then feed the results back in and do it again. We'll call that the
comparison loop. Discovery is one program built on it. The method itself
is wider than Discovery, and this guide gives the method.

## Quick reference

```
1. COMPARE     Take two things and find what they share and what they
               don't. You end up with four pieces: the shared part, the
               leftover from the first thing, the leftover from the
               second, and everything the comparison never looked at.
               Keep all four.

2. FEATURES    Decide what form the things take when you compare them:
               raw values, unordered sets, ordered sequences, or pairs of
               neighbours. If the order matters in your data, compare in
               a form that keeps the order.

3. THINNING    Optional. If you throw some of the data away before you
               compare, say which side you thinned and by how much.
               Thinning both sides loses far more than it looks like.
               Discovery throws nothing away.

4. FEEDBACK    Run the program's own output back through the comparison.
               Whether a result comes back as "seen this before" or as
               "new" is the feedback. You don't need a separate score.
               The comparison is the scorer.

5. EXAMPLES    Show one input, the parts that came out of it, and what
               the method found. The written record is the proof.

6. LIMITS      Short parts that repeat are easy to find. Long sequences
               that repeat exactly need more data or a better way of
               chunking it. Say where your method stops.

7. LOOP        Put the parts back in and go again, until a pass finds
               nothing new. That is the only reason to stop.

8. KEEP ALL    Never throw away a part, a count, a connection, or a
               leftover. Storing a thing once with a count of how often
               it appeared is fine. Dropping it is not.
```

---

## 1. Compare

**What you do.** Take two things and line them up from the front (or
from the back). Count how many positions match before the two things
first differ.

**What you get.** The result splits three ways:

- **Same**: the part the two things share.
- **Different**: what's left of each thing once you take the shared part
  off the front. There are two leftovers, one from each input.
- **Not part**: everything the comparison never touched. The program
  keeps a collection of every part it has found so far. We'll call that
  collection the pool. Everything in the pool other than the two things
  you compared is "not part".

You keep all four pieces. The shared part becomes a new entry in the
pool. The two leftovers become new entries too. The parts the comparison
never touched stay where they were. Nothing is removed.

In Discovery, this operation is called the mint step: making a new part
out of two parts that start the same way or end the same way. The mint
step does three things:

1. Sort the pool, which puts the parts in alphabetical order, so parts
   that begin alike end up next to each other.
2. Compare each part with its neighbour in that order.
3. Split each pair into the shared start and the two leftovers.

The two leftovers go back into the pool, and so does the shared start. In
the next round, all of them are there to be compared again.

**Why it works.** The comparison itself is simple: line the two things
up and count matching positions. The sort is what makes it useful.
Sorting puts things that are almost the same next to each other, so when
the comparison looks at two neighbours it has something to find.

## 2. Features

**What you do.** Decide what form your data takes when you compare it.
That form is what we'll call the features, and the choice decides what
the comparison can find. The main choices are:

- **Raw values**: compare the things exactly as they are, bit for bit or
  symbol for symbol. This is what Discovery does. Nothing is changed
  before the comparison.
- **Sets**: compare two collections that have no order, by how much they
  overlap. What's in both sets is "same". What's in one set but not the
  other is "different".
- **Sequences with order**: compare two sequences position by position.
  A shared start, a shared end, and a shared stretch in the middle are
  each a different kind of "same".
- **Pairs and short groups of neighbours**: compare sequences of two or
  three symbols that sit next to each other. These carry structure that
  single symbols don't. The pair `th` tells you something that `t` and
  `h` on their own can't.

**What you get.** If order matters in your data, keep the order in your
features. Shuffling the data destroys which symbols sit next to which,
and most of the structure lives in exactly that. A two-letter pair can
only go on existing if its two letters are still neighbours.

Discovery uses sequences with order. It sorts the pool and compares
neighbouring parts from the front, then from the back. The frame step,
the part of the program that works out how wide one unit is, compares
raw column values instead. The bridge, a script that compares the
records of two different files, compares two pools by how much they
overlap, which is the set version. All three are the same comparison on
a different kind of feature.

**Why it works.** The comparison can only find what's in its features.
If you give it ordered sequences, it can find shared starts and shared
ends. If you give it unordered sets, it can find shared membership but
never shared position. You can always throw the order away later, but
you can never put it back. Starting with order keeps every option open.

## 3. Thinning the data before you compare

**What you do.** Sometimes people remove some of the data before they
compare it. The name for that is ablation. It's optional, and Discovery
doesn't do it: Discovery compares everything against everything. If you
do thin the data, follow three rules.

1. **Remove from one side only.** If you remove 30 percent from one
   side, each feature has a 70 percent chance of still being there. If
   you remove 30 percent from both sides, each feature has to survive
   both removals, and the chance is 70 percent of 70 percent, which is
   49 percent. You lose more than half your signal for nothing.
2. **Name the side.** Keep one side whole and thin the other. The whole
   side is your reference. The thinned side is the test. The result shows
   you which parts the reference can do without.
3. **Say how much.** The rate of removal sets how fine your filter is. A
   high rate lets through only the parts that occur many times. A low
   rate lets through parts that occur fewer times. The right rate depends
   on how much noise your data has.

**What you get.** The parts that survive are the parts the reference
side needs.

**Why it works.** Experiments showed that if the data already has noise,
more thinning pushes the real parts down below the noise. Noise means
parts that land in random positions, order that's been lost, and random
additions. So clean the data first. Then thin it, if you want to find
the parts that are necessary.

## 4. Feedback

**What you do.** Run the program's own output back through the
comparison. The result is your feedback. You don't need a separate score
function, a loss function, or an objective. The question "is this thing
the same as that thing?" also answers the question "does the model match
reality?".

**What you get.** There are three kinds of feedback, and each one is the
same comparison with a different pair of inputs.

- **Against memory.** Save the pool after one file. Load it before the
  next file. The program then puts each part of the new file into one of
  three bins: confirmed (it was already in the memory), added (it's new
  this time), and not seen (it's in the memory but this file didn't
  produce it). As the memory covers more of what the files contain, the
  additions fall toward zero.
- **Against its own output.** Take whatever the model produced, run it
  back through the program as a new file, and compare the two results.
  Again there are three bins: the parts that came back the same, the
  parts that didn't come back, and the parts that are new. The parts that
  didn't come back are what the model lost. The new parts are what the
  model made up.
- **Against an answer key.** Compare the output to a correct answer you
  already know. The result is same and different. This is the kind of
  feedback most systems use, and the comparison does it without anything
  extra.

Discovery uses the first two kinds. You add the third if you have a
target to compare against.

**Why it works.** The output of the comparison is the same kind of thing
as its input: sequences of symbols. So the comparison can take its own
output as input, with no conversion in between. That's what lets one
operation serve as the learner and the scorer at once.

## 5. Examples

**What you do.** Show your work. For each file you run through the
process, do three things:

1. Show one input in its original form.
2. Show the parts that came out: the shared parts, the leftovers, and
   the counts.
3. Show what the process found, in a form a reader can check against an
   independent source.

**What you get.** Each of Discovery's four example folders does these
three things. Each folder has the input, the record the program wrote,
and a breakdown. The breakdown walks through each table of the record
and checks it against an outside source wherever one exists. The
published Apollo listing is one such source. The German and English
texts of the same parliamentary debate are another.

**Why it works.** The record is the evidence. The breakdown explains the
evidence. A reader who can compare the two to an outside source doesn't
have to take the method on trust.

## 6. Limits

**What you do.** Say where the method stops.

**What you get.** Here is where Discovery stops:

- **Short parts that occur many times** are easy to find. A letter that
  appears in many words has a high count and sits inside many other
  parts. (The number of parts a part sits inside is what the record calls
  its density.) A two-letter pair that occurs often gets made in an early
  round. The comparison finds these parts in a few rounds.
- **Long sequences that repeat exactly** need a very clean signal or many
  occurrences. A clean signal has little noise and nothing shuffled. The
  comparison can't show that a phrase that occurs only once is real,
  because there is nothing for it to match against.
- **Noisy signals** need more samples. If random additions hide the real
  parts, the comparison needs enough matches to lift the real parts above
  the noise. More data helps, and so does a better cut. To cut is to
  divide the file into chunks at a divider. A better cut (the right
  divider, or two dividers) puts the real parts into shorter chunks, and
  in a shorter chunk a real part is more likely to meet a neighbour that
  shares something with it.
- **Size.** The pool only grows, so a file with many long chunks that
  never repeat fills the pool fast. That's why the program has a cap: a
  limit on how many parts the pool may hold. When the pool passes the
  cap, the loop stops and the record says so. There are three fixes: read
  less of the file, add a second divider, or sort only the new parts into
  the existing order instead of re-sorting the whole pool every round.
  The third fix isn't in the program yet.

**Why it works.** The comparison only finds what repeats, and it only
finds a repeat when two neighbours in the sorted pool share a start or an
end. Everything in the list above follows from that: short and frequent
is easy, long and rare is hard, and noise gets in the way of neighbours
meeting.

## 7. Loop

**What you do.**

1. Feed the parts back in.
2. Repeat until nothing new comes out.

```
pool = the initial set of things (runs, features, whatever you start with)

while True:
    new_parts = compare every pair of neighbours in the sorted pool
    if no new parts were made:
        break
    add new_parts to pool
```

**What you get.** The only rule for stopping is a round that makes
nothing new. There's no round limit, no time limit, and no score to
reach. The loop runs until the whole pool has been compared against
itself, and at that point the program has found everything it can find.

In Discovery, the mint loop takes 7 to 30 rounds, depending on the file.
The number of new parts per round always falls to 0:

```
Alice:   10038 3800 1303 484 176 88 37 22 15 10 4 1 2 0
German:  9291 3641 1205 402 130 42 7 2 1 0
```

Then the whole loop runs again one level up. At the new level, the
program treats each chunk from the level below as a single symbol. It
also uses the classes from the level below as a second way for two
things to count as the same. (A class is a group of parts that all take
the same additions, like the 22 verb stems that all take `+ed` and
`+ing`.) The level loop runs until a level also makes nothing new. The
rule is the same at every scale.

Here is the core loop as a reference, in Python:

```python
def mint_loop(pool):
    """Compare sorted neighbours, mint shared parts, loop until stable."""
    while True:
        items = sorted(pool)
        new = {}
        for a, b in zip(items, items[1:]):
            head = shared_head(a, b)
            if not head:
                continue
            tail_a = a[len(head):]
            tail_b = b[len(head):]
            for part in [head, tail_a, tail_b]:
                if part and part not in pool:
                    new[part] = True
        if not new:
            break
        pool.update(new)
    return pool

def shared_head(a, b):
    """How far two sequences match from the front."""
    n = min(len(a), len(b))
    for i in range(n):
        if a[i] != b[i]:
            return a[:i]
    return a[:n]
```

That's the skeleton. Discovery adds a few things on top of it: a reverse
pass that runs the same loop on every part spelled backwards, to find
shared ends; two records of connections, which part sits inside which
and which parts a part is built from; the counts; a rule that a pair of
neighbours is only compared when at least one of the two is new since
the last round; and the cap. But the loop in Discovery is the loop
above.

**Why it works.** The pool can only grow, and every part that could ever
be made is some piece of a chunk that was in the pool at some point. There
are only so many of those. A collection that only grows and has a ceiling
has to stop growing eventually, and when a round adds nothing, the loop
ends.

## 8. Keep all

**What you do.** Never remove a part, a count, a connection, or a
leftover. Every intermediate result is information.

- A part that occurred once is kept exactly the same way as a part that
  occurred 1,000 times. A rare part that is real still has value.
- A leftover from a comparison is a part in its own right. It goes back
  into the pool, and the program compares it in the next round.
- A count says how often a thing occurred. It doesn't decide whether the
  thing exists. Existence is yes or no. The count says how common.
- A connection is a fact about the file. There are three kinds: A is
  inside B, A comes after B, or A turns into B. The program writes the
  connection down. It doesn't judge it.

**What you get.** A pool that holds a complete history of every split
that ever happened.

**Why it works.** If you remove intermediate results, you can no longer
find anything that depends on them. A part you dropped because it was
"too common" or "not important enough" can turn out to be exactly the
part two other parts share. Without it, the comparison can never find the
connection between those two.

Discovery has no removal anywhere. The pool is a dictionary. Each key is
the content of a part, and each value is its count. No count ever goes
down, no entry expires, and the program never removes an entry. The only
compression is that each distinct part is stored once, with its count,
rather than as 1,000 separate copies.

---

## Each step in Discovery

| step | in the process | in Discovery |
|---|---|---|
| compare | take two things, split the result three ways | `shared_head()` on neighbouring parts in the sorted pool |
| features | raw sequences, with their order kept | bits -> words -> chunks. The program compares the chunks as sequences of symbols. |
| thinning | none | the program removes nothing |
| feedback | against memory, against its own output | `--memory`, `hybrid/loop.py` |
| examples | show the input, the parts, and the result | the four `examples/` folders, each with a breakdown |
| limits | say where the method stops | `notes/open.md` |
| loop | until a round makes nothing new | `mint()`, `run_levels()` |
| keep all | never remove anything | the pool only grows. There is no removal anywhere in the code. |

---

## Why each step works

Each step above makes a claim. This section gives the reason each claim
holds. You can check every reason against the code (`discovery.py`) and
against the example records.

### Nothing is lost in the split (step 1: compare)

Take two things, A and B. The comparison produces a shared start, call it
H, and two leftovers: the rest of A after H, and the rest of B after H.

H plus the rest of A is A. H plus the rest of B is B. You can always
rebuild the originals from the pieces, so the comparison destroyed
nothing. The same information is still there, just in more parts. And the
comparison never touched anything else in the pool.

So the split can run as many times as you like with no loss. Each round
makes more parts, never fewer. Together with step 8 (keep all), that
means the pool becomes a complete record of every split that ever
happened.

### The structure lives in the order (step 2: features)

The pair `th` exists only because `t` and `h` sit next to each other. If
you shuffle the file, the pair is gone. The comparison can only find
what's in its features. Give it sequences with order and it finds shared
starts and shared ends, both of which depend on position. Give it sets
with no order and it finds shared membership, but never shared position.

The relation between ordered and unordered runs one way only. You can
always treat ordered features as a set by ignoring the order. You can't
put a set back into order. So starting with order keeps all your options
open, and starting without order closes every option that depends on
position.

Discovery starts with ordered sequences. That's why it can find `th` as
a pair, not just `t` and `h` as separate parts.

### Why thinning both sides costs so much (step 3: thinning)

Each feature either survives the removal or it doesn't. If you remove
from one side at a rate r, a feature has a chance of (1 - r) to survive.
If you remove from both sides at the same rate, a feature has to survive
twice, and the chance is (1 - r) times (1 - r), or (1 - r)^2.

At a rate of 30 percent, one side gives 0.70. Both sides give 0.49. You
lose more than half your signal and gain nothing, because the comparison
still only makes the same three-way split. Thinning both sides finds
nothing that thinning one side misses.

Experiments showed the same thing from the other direction. If the data
already has noise (parts in random positions, features spread apart),
more thinning pushes the real signal below the noise. Clean first. Thin
second. Or don't thin at all, which is what Discovery does.

### The comparison is its own scorer (step 4: feedback)

The comparison takes two things and makes parts. The parts are the same
kind of thing as the inputs: sequences of symbols. So the comparison can
take its own output as its next input, and nothing has to be converted
in between.

That one property gives you all three kinds of feedback, each with the
same operation.

**Against memory.** Compare the parts of this file to a pool you saved
earlier. There are three bins: confirmed (already in the saved pool),
added (new this time), and not seen (in the saved pool, but this file
didn't produce it). The question "is this part in the saved pool?" is
the same question as "do these two things share this part?". It's the
comparison, with the saved pool as one of the two inputs.

**Against its own output.** Run the parts back through the process and
compare the two pools: the parts that came back the same, the parts that
didn't come back, and the parts that are new. If a part didn't come
back, the process lost it somewhere. If a part is new, the process made
it: a different order of neighbours let two parts meet that never met
before. The comparison finds both kinds without a separate score.

**Against an answer key.** Compare the output to a correct answer you
already know. The result is same and different. Most systems use this
kind, a test against a target, and the comparison does it with the same
operation it uses for everything else.

All three kinds work because the output is the same type as the input.
The technical word for that property is "closure": what comes out of the
operation is the kind of thing that can go back in. There is no
conversion step, no loss function, and no separate scoring mechanism.
The comparison makes the score.

### Why the loop always stops (step 7: loop)

The pool can only grow. In each round, the mint step looks at
neighbouring parts in the sorted pool and splits them. A split makes at
most three parts: the shared start and the two leftovers. Each of the
three is shorter than the part it came from. The program adds only the
parts the pool hasn't seen before.

The number of parts that could ever exist is finite: every piece of every
chunk that was ever in the pool. A collection that only grows, never
shrinks, and has a ceiling must stop growing at some point. When a round
adds nothing new, the loop exits.

The level loop has the same shape. Each level takes the chunks from the
level below and runs the mint step again. At each level the chunks are
fewer and longer. When a level ends up with one chunk, or finds nothing
new, the level loop stops. In practice, Discovery takes 7 to 30 mint
rounds at level 0 and 2 to 4 levels in all.

### Why the loop finds every shared part the sort can reveal (step 7: loop)

If two chunks share a start, they end up next to each other once the
pool is sorted, because sorting groups parts with the same beginning
together. Once they're neighbours, the comparison finds the shared start
and splits it out. So the program will find every shared start between
any two chunks in the pool. The sort guarantees that they meet.

The reverse pass does the same from the other end. It spells every part
backwards, sorts, compares, and spells the results forwards again. That
finds shared ends in exactly the way the forward pass finds shared
starts.

A shared middle is a stretch inside two chunks that have different starts
and different ends. A single pass won't always find a shared middle. But
a single pass doesn't need to.

Every round strips shared starts and shared ends off the parts. A stretch
that used to be in the middle becomes the start or the end of a shorter
leftover. In the next round's sort, that shorter leftover lands next to
another part that shares the same stretch, and the comparison finds it.

There is only one case where the program never finds a shared middle:
when everything on both sides of the middle is unique, so no round ever
strips it away. That is a real limit, and section 6 notes it.

### Why every part is real (step 7: loop)

The mint step never makes a part out of nothing. Every part in the pool
is there because two neighbours in the sorted pool matched for some
number of positions, from the front or from the back. The program copies
the shared part straight out of the input. The leftovers are what's left
of the input after the shared part is taken off. The counts are exact:
each match that produced a part was a real event in the sorted pool.

Classes work the same way. Two parts end up in the same class for one
reason only: the mint step found the same set of changes on both of
them, meaning the same endings and the same beginnings. The grouping
comes from the data, not from a rule that says what belongs together.

### What a removal would lose for good (step 8: keep all)

If you remove a part, you lose:

- the part itself
- every record that the part sits inside some other part
- every record that the part is built from smaller parts
- the part's place in its class, the group of parts that take the same
  changes
- every future match. The next round can find something new only because
  the part is sitting next to some other part in the sorted pool.
  Without it, that pair never forms, and that discovery never happens.

You can't get any of this back without re-running the whole process from
the start. The system makes no predictions. It doesn't know what it will
need later. The only safe answer is to keep everything.

Compression is not removal. Compression means one entry for each distinct
part, with its count. The pool is a dictionary with one entry per thing,
not 1,000 copies. The counts are the values. No count goes down, no entry
expires, and the program removes nothing.

The count says how common a thing is. Its being there at all says the
thing is real.

### Same input, same output

The program sorts the pool before every comparison, and the sorted order
is the same every time for the same contents. The mint step walks the
sorted list from front to back, comparing the same pairs in the same
order. There is no random step anywhere. Run the program twice on the
same file and you get the same record.

### How to check that the code removes nothing

Every change the code makes to its tables is an addition:
`pool[key] = ...`, `made_of[key] = ...`, `part_of.setdefault(...)`.
There is no `del`, no `pop`, no `remove`, and no `discard` on the pool or
on any table that goes with it. Parts go in and stay in. This is easy to
check yourself: search the source for anything that removes from the
pool dictionary. There isn't anything.
