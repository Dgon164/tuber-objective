# The process

This guide shows how to use the comparator loop on any problem. The
comparator loop is the core cycle: compare 2 things and find what the 2
things share. Discovery is 1 implementation of the comparator loop. This
guide gives the general method.

## Quick reference

```
1. COMPARE     Take two things. Find what they share and what they don't.
               Save all four parts: shared, unique-to-A, unique-to-B,
               and everything the comparison never touched.

2. FEATURES    Decide what you're comparing — raw values, sets, ordered
               sequences, pairs. If order matters, keep it.

3. ABLATION    Optional. If you drop pieces before comparing, say which
               side and how much. Dropping from both sides squares the
               loss. Discovery doesn't drop anything.

4. FEEDBACK    Point the comparator at its own output. The signal that
               says "same again" or "new" is the feedback. No separate
               scoring function needed — the comparator is the scorer.

5. EXAMPLES    Show one input, the parts that came out, and what was
               recovered. The record is the proof.

6. LIMITS      Short repeated pieces show up easily. Long exact sequences
               need more signal or a better cut. Say where your method
               runs out.

7. LOOP        Feed the parts back in and repeat until nothing new comes
               out. The stable point is the only stopping rule.

8. KEEP ALL    Never throw away a part, a count, a connection, or a
               leftover. Compression is storing a thing once with a
               count, not throwing things out.
```

---

## 1. Compare

Take 2 things. Split the result 3 ways:

- **Same**: the part that the 2 things share.
- **Different**: the rest of each thing after you remove the shared part.
  There are 2 different parts, 1 for each input.
- **Not part**: each part in the pool that the comparison did not touch.
  The pool is the collection of all known parts.

The program keeps all 4 parts. The shared part becomes a new entry in the
pool. The 2 parts that remain become new entries. The parts that the
comparison did not touch stay in the pool. The program removes nothing.

In Discovery, this operation is the mint step. To mint a part is to make
a new part from 2 parts that have the same start or the same end. The
mint step has 3 actions:

1. Sort the pool. To sort the pool is to put the parts of the pool in
   order.
2. Compare each pair of adjacent parts.
3. Split each pair into a shared start and 2 parts that remain.

The 2 parts that remain go back into the pool. The shared start also goes
into the pool. In the next round, all of these parts are available for
the next comparison.

The comparison is simple. Put the 2 things in line from the front (or
from the back). Count the positions where the 2 things are the same. The
sort puts things that are almost the same next to each other. Thus the
comparison has something to find.

## 2. Features

Say what you compare. The choice of features decides what the comparator
can find.

- **Raw values**: compare the things exactly as they are, bit for bit or
  symbol for symbol. Discovery compares raw values. Nothing changes
  before the comparison.
- **Sets**: compare 2 collections with no order by their overlap. The
  parts in both sets are "same". The parts in 1 set and not in the other
  set are "different".
- **Sequences with order**: compare 2 sequences position by position. A
  shared start, a shared end, and a shared subsequence are each a
  different kind of "same".
- **Pairs and n-grams**: compare sequences of 2 or 3 adjacent symbols.
  These sequences carry structure that single symbols do not carry. The
  pair `th` tells you something that `t` and `h` alone cannot tell you.

If order is important in your signal, keep the order in your features. A
shuffle destroys adjacency. Adjacency is the relation of symbols that are
next to each other. Most of the structure is in the adjacency. A pair of
2 characters can only continue to exist if the 2 characters are still
next to each other.

Discovery uses sequences with order. Discovery sorts the pool and
compares the parts from the front and then from the back. The frame step
uses raw column values. The bridge uses set overlap on 2 pools. Each of
the 3 is the comparator on a different kind of feature.

## 3. Ablation

Ablation is the removal of parts before the comparison. Ablation is
optional. Discovery does no ablation. Discovery compares everything
against everything.

If you do ablation, obey these 3 rules:

1. **Remove from 1 side only.** If you remove from 1 side at 30 percent,
   each feature has a 70 percent chance to remain. If you remove from
   both sides at 30 percent, each feature must remain through both
   removals. The chance is 70 percent of 70
   percent. The result is 49 percent. You lose more than half of your
   signal for nothing.
2. **Say which side.** Keep 1 side whole and remove from the other side.
   The whole side is the reference. The side with the removals is the
   test. The result shows which parts the reference does not need.
3. **Say how much.** The rate of removal sets how fine your filter is. A
   high rate lets through only the parts that occur many times. A low
   rate lets through parts that occur fewer times. The correct rate
   depends on how much noise is in your signal.

Experiments showed this result: if the signal already has noise, more
ablation can put the real parts below the level of the noise. Noise in a
signal includes parts in random positions, order that is lost, and random
additions. Clean the signal first. Then do ablation if you want to test
which parts are necessary.

## 4. Feedback

Point the comparator at its own output. The result is feedback. There is
no separate score function, no loss function, and no objective. The
question "is this thing the same as that thing?" also answers the
question "is the model the same as reality?".

There are 3 kinds of feedback. Each kind uses the comparator:

- **Against memory.** Save the pool after 1 signal. Load the pool before
  the next signal. The program puts each part from the new signal into 1
  of 3 bins: confirmed (already known), added (new this time), and not
  seen (in the memory but absent from this signal). The additions
  decrease toward 0 as the memory covers more of what the signals
  contain.
- **Against its own output.** Run the output of the model back through
  the program as a new signal. Compare the 2 results. There are 3 bins:
  the parts that came back the same, the parts that did not come back,
  and the parts that are new. The parts that did not come back are the
  parts that the model lost. The new parts are the parts that the model
  made.
- **Against an answer key.** Compare the output to a correct answer that
  you know. The result is same and different. Most systems use this kind
  of feedback. The comparator does this comparison and needs nothing more.

Discovery uses the first 2 kinds. You add the third kind if you have a
target. All 3 kinds are the same comparison with different inputs.

## 5. Examples

Show your work. For each signal that you run through the process, do
these steps:

1. Show 1 input in its original form.
2. Show the parts that came out: the shared parts, the parts that
   remain, and the counts.
3. Show what the process found. A reader must be able to check this
   result against an independent source.

Each of the 4 example folders of Discovery does these 3 steps. Each
folder has the input, the record, and a breakdown. The breakdown goes
through each table. The breakdown checks each table against an outside
source when a source exists. The Apollo listing that was published is 1
source. The German and English texts of the same debate are 1 source.

The record is the evidence. The breakdown explains the evidence.

## 6. Limits

Say where the method stops.

- **Short parts that occur many times** are easy to find. A letter that
  occurs in many words has a high count and a high density. Density is
  the number of parts that contain a part. The program mints a pair of 2
  letters that occurs often in an early round. The comparator finds
  these parts in a few rounds.
- **Long exact sequences** need a very clean signal or many occurrences.
  A clean signal has little noise and no shuffle. The comparator cannot
  confirm a phrase that occurs only 1 time. The phrase has nothing to
  collide with.
- **Signals with noise** need more samples. If random additions hide the
  real parts, the comparator needs enough collisions to show the real
  parts above the noise. More signal and a better cut both help. To cut
  is to divide the signal into runs at a separator. A better cut (the
  correct separator, or 2 separators) puts the real parts into shorter
  runs. In a shorter run, a real part is more likely to meet an adjacent
  part that shares a part.
- **Size.** The pool only grows, so a signal with many long unique runs
  fills the pool fast. The cap exists for this reason. The cap stops the
  loop and reports the stop. There are 3 fixes: a shorter read, a second
  separator, or a sort of only the new parts into the current order. The
  third fix is not yet in the program. With the third fix, the program
  does not sort the whole pool again.

## 7. Loop

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

The stable point is the only stop rule. The stable point is a round that
makes nothing new. The stop rule is not a round limit, not a time limit,
and not a score threshold. The loop runs until the program has compared
the whole pool against itself. At that point, the program has found
everything that the program can find.

The mint loop of Discovery runs the loop in 7 to 30 rounds. The number of
rounds depends on the signal. The count of new parts in each round always
decreases to 0:

```
Alice:   10038 3800 1303 484 176 88 37 22 15 10 4 1 2 0
German:  9291 3641 1205 402 130 42 7 2 1 0
```

Then the whole loop runs again 1 level up. At the new level, the program
treats the runs as symbols and uses the classes as a second way to be the
same. The level loop runs until a level also makes nothing new. The rule
is the same at each scale.

The code below is a reference implementation of the core loop in Python:

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

This code is the skeleton. Discovery adds the reverse pass (shared ends),
the part-of and made-of connections, the counts, the fresh-pair rule, and
the cap. But the loop in Discovery is the loop above.

## 8. Keep all

Never remove a part, a count, a connection, or a part that remains. Each
intermediate result is information.

- The program keeps a part that occurred 1 time in the same way as a
  part that occurred 1,000 times. A part that is rare but real has
  value.
- A part that remains from a comparison is a part in its own right. The
  part goes back into the pool. The program compares the part in the next
  round.
- A count says how often a thing occurred. The count does not decide if
  the thing exists. Existence is yes or no. The count says how common the
  thing is.
- A connection is a fact about the signal. A connection has 3 forms: A is
  in B, A comes after B, or A changes into B. The program writes the
  connection down. The program does not evaluate the connection.

If you remove intermediate results, you cannot find things that depend on
those results. A part that you remove because the part is "too common" or
"not important enough" can be the part that 2 other parts share. Without
that part, the comparator cannot find the connection between the 2 other
parts.

Discovery has no removal anywhere. The pool is a dictionary with the
content of each part as the key. The counts are the values. No count
decreases with time, no entry has an end date, and the program removes
no entry. The only compression is 1 entry for each distinct part,
with the count of the part. There is 1 entry for each thing, not 1,000
copies.

---

## Each step in Discovery

| step | in the process | in Discovery |
|---|---|---|
| compare | take 2 things, split 3 ways | `shared_head()` on adjacent parts in the pool in order |
| features | raw sequences with order | bits -> words -> runs. The program compares the runs as symbol sequences. |
| ablation | none | the program removes nothing |
| feedback | against memory, against own output | `--memory`, `hybrid/loop.py` |
| examples | show input, parts, result | the 4 `examples/` folders with breakdowns |
| limits | say where the method stops | `notes/open.md` |
| loop | until stable | `mint()`, `run_levels()` |
| keep all | never remove | the pool only grows. There is no removal in the code. |

---

## Proof of each step

Each step of the process makes a claim. This section gives the reason
that each claim is correct. You can check all of the reasons against the
code (`discovery.py`) and against the example records.

### The split with no loss (step 1: compare)

Take 2 things, A and B. The comparator makes a shared start H and 2 parts
that remain: tail_A (the rest of A after H) and tail_B (the rest of B
after H).

H + tail_A = A. H + tail_B = B. You can always make the original things
again from the parts. The comparator destroyed nothing. The same
information exists, in more parts. The comparator did not touch the "not
part" set (everything else in the pool).

Thus the split can run many times with no loss. Each round makes more
parts, never fewer. With step 8 (keep all), the pool becomes a complete
record of each split that occurred.

### Structure in the order of the symbols (step 2: features)

The pair `th` exists only because `t` and `h` are next to each other. If
you shuffle the signal, the pair is gone. The comparator can only find
what is in its features. If the features are sequences with order, the
comparator finds shared starts and shared ends. Both results depend on
position.
If the features are sets with no order, the comparator finds shared
membership but not shared position.

The relation between order and no order goes in 1 direction only. You
can always treat features with order as a set: ignore the order. But you
cannot put a set back in order. Thus a start with features that have
order keeps all of your options open. A start with features that have no
order closes each option that depends on position.

Discovery starts with sequences that have order. Thus Discovery can find
`th` as a pair, not only `t` and `h` as separate parts.

### The loss from a removal on both sides (step 3: ablation)

Each feature remains after the removal or does not remain. If you remove
from 1 side at the rate r, a feature has a chance of (1 - r) to remain.
If you remove from both sides at the rate r, a feature must remain
through both removals. The chance is (1 - r) times (1 - r), or (1 - r)^2.

At a rate of 30 percent, 1 side gives 0.70. Both sides give 0.49. You
lose more than half of your signal with no gain. The comparison still
makes only the 3-way split. A removal from both sides finds nothing that a
removal from 1 side misses.

Experiments showed this result. If the signal already has noise (random
positions, features that are spread apart), more ablation pushes the real
signal below the noise. Clean first. Do ablation second. Or do no
ablation. Discovery does no ablation.

### The comparator as the scorer (step 4: feedback)

The comparator takes 2 things and makes parts. The parts are the same kind
of thing as the inputs: sequences of symbols. Thus the comparator can take
its own output as input. No adapter is necessary.

This property gives 3 kinds of feedback. Each kind uses the same
comparison.

**Against memory.** Compare the parts of this signal to a pool that you
saved. There are 3 bins: confirmed (already known), added (new this
time), and not seen (known but absent from this signal). The question "is
this part in the pool that you saved?" is the same question as "do these
2 things share this part?". The comparison is the comparator with the
pool that you saved as 1 input.

**Against its own output.** Run the parts back through the process. Then
compare the 2 pools: the parts that came back the same, the parts that
did not come back, and the parts that are new. If a part did not come
back, the process lost the part in some way. If a part is new, the
process made the part. A different order of adjacent parts made a
different collision. The comparator finds both kinds of part with no
separate score function.

**Against an answer key.** Compare the output to a correct answer that you
know. The result is same and different. Most systems use this kind: a
test against a target. The comparator does this with the same operation
that the comparator uses for everything else.

All 3 kinds work because the output is the same type as the input. The
technical word for this property is "closure": the output of the
operation stays in the domain of the operation. There is no conversion
step, no loss function, and no separate score mechanism. The comparator
makes the score.

### The stop of the loop (step 7: loop, termination)

The pool can only grow. In each round, the mint step looks at adjacent
parts in the pool in order and splits the adjacent parts. A split makes
at most 3 parts: the shared start and the 2 parts that remain. Each of
the 3 parts is shorter than its source. The program adds only the parts
that the pool has not seen before.

The number of possible parts is finite. The limit is each substring of
each run that was ever in the pool. A finite set that only grows and
never decreases must stop its growth at some time. When the program adds
nothing new, the loop exits.

The level loop has the same shape. Each level takes the runs from the
level below and runs the mint step again. At each level, the runs are
fewer and longer. When a level makes 1 run or finds nothing new, the
level loop stops. In practice, Discovery takes 7 to 30 mint rounds at
level 0 and 2 to 4 levels in total.

### Each shared part that the sort can show (step 7: loop, completeness)

If 2 runs share a start, the 2 runs are next to each other after the sort
of the pool. The sort puts parts with the same start together. When the 2
runs are adjacent, the comparator finds the shared start and splits the
shared start out. Thus the program will find each shared start between any
2 runs in the pool. The sort makes sure that the 2 runs meet.

The mirror pass does the same from the other end. The mirror pass
reverses everything, sorts, compares, and reverses the results back. The
mirror pass finds shared ends in the same way that the forward pass finds
shared starts.

A shared middle is a part inside 2 runs that have different starts and
different ends. One pass does not always find a shared middle. But one
pass does not need to find a shared middle.

In each round, the loop removes shared starts and shared ends. A part
that was a middle becomes the start or the end of a shorter part that
remains. The sort of the next round puts that shorter part next to a part
that shares the middle. The comparator then finds the middle.

A shared middle stays hidden in only 1 case: the parts around the middle
are all unique, and no round removes those parts. That case is a real
limit. Section 6 notes that limit.

### Real parts only (step 7: loop, soundness)

The mint step never makes a part from nothing. Each part in the pool
exists because 2 adjacent parts in the pool in order were the same for
some number of positions. The comparison was from the front or from the
back. The program copies the shared part from the input. The parts that
remain are the rest of the input after the removal of the shared part.
The counts are exact: each collision that made a part is a real event in
the pool in order.

Classes work in the same way. A part goes into the same class as a second
part because the mint step found the same set of changes on both parts
(the same endings, the same starts). The group comes from the data, not
from a rule that says what goes together.

### The permanent loss from a removal (step 8: keep all)

If you remove a part, you lose these things:

- the part itself
- each "part of" connection of the part (each record that the part is
  inside a different thing)
- each "made of" connection of the part (each record that the part
  contains smaller parts)
- the class membership of the part (the place of the part in each group
  that shares changes)
- each future collision. The next round of the loop can find something
  new because the part is next to a different part in the pool in order.
  Without the part, that adjacent pair never occurs, and the discovery
  never occurs.

You cannot get any of these things back without a new run of the whole
process from the start. The system has no prediction. The system does not
know what will be necessary later. The only safe answer is to keep
everything.

Compression is not removal. One entry for each distinct part, with the
count of the part, is compression. The pool is a dictionary with 1 entry
for each thing, not 1,000 copies. The counts are values in the
dictionary. No count decreases with time, no entry has an end date, and
the program removes no entry.

The count says how common a thing is. Existence says that the thing is
real.

### Same input, same output (determinism)

The program sorts the pool before each comparison. The order after the
sort is the same each time for the same contents. The mint step goes
through the list in order from the front to the back, with the same pairs
in the same order. There is no random step anywhere. Run the program 2
times on the same file, and you get the same record.

### No removal in the code (check)

Each change in the code is an addition: `pool[key] = ...`,
`made_of[key] = ...`, `part_of.setdefault(...)`. There is no `del`, no
`pop`, no `remove`, and no `discard` on the pool or on any of the tables
that go with the pool. Parts go in and stay in. This claim is easy to
check. Search the source for a removal on the pool dictionary. There is
none.
