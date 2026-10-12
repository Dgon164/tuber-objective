# Thinking in self-assembly

How to work with a system that finds its own structure. This is not
about the code — it's about what you do and don't do as the person
running it.

## The one rule

**Don't help it. Try it. Then figure out what difference it's missing.**

That's the whole method. Everything below is that sentence unpacked.

## What self-assembly means

A self-assembling system builds structure from its own output. You give
it a signal. It compares, finds what recurs, and builds on what it
found. Each round's output is the next round's input. You don't tell it
what to look for. You don't tell it what it found. You don't correct its
categories or rename its parts. The structure it finds is the structure
the signal has — or the structure the signal doesn't have, which is also
an answer.

This is autocatalysis: the product of the reaction is a catalyst for
more of the same reaction. The comparator's output is what the
comparator compares next. You don't drive it. You set it up and let it
run to stability.

## What you stop doing

**Don't predict what it will find.** You'll be wrong, and then you'll
try to fix the system to match your prediction instead of reading what
it actually found. Discovery found that the Apollo computer's EXTEND
instruction is the separator — the most common word. Nobody would have
guessed that. It's correct.

**Don't define the categories.** If you name the buckets in advance,
you've already decided what the answer is. The system's categories come
from the signal. They might not match yours. That's information.

**Don't filter the input.** Don't clean the data, don't remove outliers,
don't strip punctuation, don't normalize case. Every one of those
decisions is you telling the system what matters. Let it figure that out.
Discovery found that the top bit of ASCII is never on. It found that
because nobody stripped it first.

**Don't score it against your expectations.** The system's own
comparator is the scorer. A part that recurs is meaningful. A part that
doesn't recur is noise. That test is already built in. If you add a
second scoring function, you've split the system into the part that
learns and the part that judges, and now the judge needs its own
justification.

**Don't add special cases.** If it doesn't find something, the answer
is not a rule for that thing. The answer is a missing difference — see
below.

## What you do instead

### 1. Run it

Give it the signal. Read the record. Don't look for what you expected.
Look at what's there.

### 2. Ask what's missing

If the record doesn't show something you know is in the signal, don't
add a detector for that thing. Ask: **what difference would it need to
see to find this on its own?**

The system finds structure by comparison. If it didn't find something,
one of these is true:

- **The difference isn't in the signal.** The information you're looking
  for genuinely isn't there at this resolution. This is a real answer.
  It means you need a different signal, not a different system.

- **The difference is there but doesn't recur enough.** The comparator
  finds what repeats. Something that happens once is a connection, not
  a pattern. More signal, or a different cut, can surface it.

- **The difference is there but the comparator can't reach it.** The
  structure exists but the system's current path doesn't compare the
  right things. This is the interesting case. The fix is not to add a
  rule — it's to point the comparator somewhere new.

### 3. Point the comparator somewhere new

This is what the `extend/` scripts do. Each one is a few lines that
take Discovery's output and run the same comparator on a different
aspect of it:

- `same_slot.py` — compares words by WHERE they stand (same left
  neighbor, same right neighbor), not what they're made of. Finds
  parts of speech.
- `functions.py` — compares changes by what they ACT ON (which parts
  take the same set of changes), not what they look like. Finds
  word-building functions that can make new words.
- `sentence.py` — follows the SEQUENCE (which word comes after which),
  not the parts. Writes sentences.

None of these required changing `discovery.py`. They each point the
existing comparator at a different relationship in the record. The
missing difference was already in the data — it just hadn't been
compared yet.

### 4. Check the cost, not the output

The system's output is what it found. You don't grade that. What you
measure is the cost of finding it: how many failed attempts, how long
it took, how many negative flags it accumulated before it stabilized.

If the cost is high, the system is searching too broadly — it doesn't
have enough differences to narrow the space. The fix is the same: find
the missing difference.

If the cost is low, the system has enough structure to get there
directly. That's the signal that the differences it has are the right
ones.

`functions.py` went through four iterations:
- Open offers, no feedback: 3,341 failures for 100 words.
- Per-ending feedback: 7,871 failures. Worse. The feedback was too
  narrow — one refusal taught nothing about similar refusals.
- Negative groups: 662 failures. Better. The feedback generalized.
- Functions over the record: 985 failures in 6 seconds. The structure
  of the record IS the feedback. No bolted-on mechanism needed.

The cost dropped as the system found the right differences to compare.

### 5. Don't add. Subtract.

If the system is too slow or too noisy, the instinct is to add: add a
filter, add a heuristic, add a special case. Resist it. The answer is
almost always to remove something — to stop comparing things that don't
matter.

`functions.py` was unusable when it treated every fragment as a target.
The letter `e` sits inside 1,615 parts. It takes nearly every change
and says nothing about any one of them. Restricting to whole runs —
parts the signal stood up on its own — dropped from 6.8 million sibling
pairs to 184,000. Same comparator, same logic, less noise. The thing
that was removed was not information. It was a difference that didn't
make a difference.

## The short version

```
1. Run it.
2. Read what it found, not what you expected.
3. If something's missing, find the missing difference.
4. Point the comparator there.
5. If it's slow, remove noise — don't add rules.
6. The cost is the measure. The output is the answer.
```

The system assembles itself. Your job is to give it a signal and, when
it stalls, figure out which comparison it hasn't made yet. That's it.
Everything else is the system's problem.
