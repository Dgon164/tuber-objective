# The process

How to use the comparator loop on any problem. Discovery is one
implementation; this is the general method.

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

Take two things and split the result three ways:

- **Same** — the part the two things share.
- **Different** — what's left of each one after you remove the shared
  part. There are two of these, one per input.
- **Not part** — everything in the pool that the comparison never touched.

All four pieces get saved. The shared part is a new thing in the pool.
The two leftovers are new things. What wasn't touched stays where it was.
Nothing is removed.

In Discovery, this is the mint: sort the pool, compare each pair of
neighbours, split them into a shared head and two leftovers. The leftovers
go back in the pool. The shared head goes in too. Next round, all of them
are available for the next comparison.

The comparison itself is simple: line up two things from the front (or
from the back) and count how far they match. The sorted order is what
puts similar things next to each other so the comparison has something
to find.

## 2. Features

State what you're comparing. The choice of features decides what the
comparator can find.

- **Raw values**: compare the things as they are, bit for bit or symbol
  for symbol. This is what Discovery does. Nothing gets transformed
  before the comparison.
- **Sets**: compare two unordered collections by intersection. The
  overlap is same; what's in one set but not the other is different.
- **Ordered sequences**: compare two sequences position by position.
  Shared prefixes, shared suffixes, shared subsequences — each is a
  different kind of "same."
- **Pairs and n-grams**: compare runs of two or three adjacent elements.
  These carry structure that single elements don't — the pair `th` tells
  you something that `t` and `h` alone don't.

If order matters in your signal, keep it in your features. Shuffling
destroys adjacency, and adjacency is where most of the structure lives.
A bigram can only survive if the two elements are still next to each
other.

Discovery uses ordered sequences (the sorted pool, compared from the
front and then from the back). The frame step uses raw column values.
The bridge uses set intersection on two pools. Each is the comparator
on a different kind of feature.

## 3. Ablation

Ablation means dropping pieces before comparing. It's optional. Discovery
doesn't do it — it compares everything against everything.

If you do ablate:

- **One side only.** Ablating one side at a 30% drop rate means each
  feature has a 70% chance of surviving the comparison. Ablating both
  sides at 30% means each feature has a 70% x 70% = 49% chance. You
  lose more than half your signal for no gain.
- **Say which side.** Keep one side whole and drop from the other. The
  whole side is the reference; the ablated side is the test. This is how
  you find which pieces the reference can do without.
- **Say how much.** The drop rate sets how fine the filter is. A high
  drop rate finds only the pieces that show up over and over. A low drop
  rate lets weaker pieces through. The right rate depends on how much
  noise is in the signal.

The lesson from experiment: if the signal is already noisy (pieces
scattered, order lost, random additions), ablation on top of that can
bury the real parts under the noise floor. Clean signal first, then
ablate if you want to test what's load-bearing.

## 4. Feedback

The comparator pointed at its own output is feedback. No separate scoring
function, no loss, no objective — the same "is this the same as that?"
answers "does the model match reality?"

Three kinds of feedback, each using the comparator:

- **Against memory.** Save the pool after one signal. Load it before the
  next. Everything the new signal produces gets sorted into three bins:
  confirmed (already known), added (new), not seen this time (remembered
  but absent). The additions shrink toward zero as the memory covers more
  of what the signals contain.
- **Against its own output.** Run the model's output back through as a
  new signal. Smash the two records together. Three bins: what came back
  the same, what was lost, what's new. The lost parts are what the model
  dropped; the new parts are what the model invented.
- **Against an answer key.** Compare the output to a known answer. Same
  and different. This is the version most systems use. The comparator
  does it with no extra machinery.

Discovery uses the first two. The third is what you'd add if you had a
target to hit. All three are the same comparison with different inputs.

## 5. Examples

Show the work. For any signal you run the process on:

1. Show one input as it went in.
2. Show the parts that came out — the shared pieces, the leftovers, the
   counts.
3. Show what was recovered — what the process found that a reader can
   check against something outside the record.

Discovery's four example folders each do this: the input, the record,
and a breakdown that walks through every table and checks it against
an outside source where one exists (the published Apollo listing, the
German and English texts of the same debate). The record is the evidence.
The breakdown is the reading.

## 6. Limits

Say where the method runs out.

- **Short repeated pieces** show up easily. A letter that appears in
  many words has a high count and high density. A two-letter pair that
  appears often gets minted early. The comparator finds these in a few
  rounds.
- **Long exact sequences** need either a very clean signal (little noise,
  no shuffling) or many repetitions. A phrase that appears once can't be
  confirmed by the comparator — it has nothing to collide with.
- **Noisy signals** need more samples. If the real parts are buried in
  random additions, the comparator needs enough collisions for the real
  parts to rise above the noise. More signal helps. A better cut
  (choosing the right separator, or using two) also helps, because it
  puts the real parts into shorter runs where they're more likely to
  meet a neighbour that shares a piece.
- **Size.** The pool only grows. A signal with many long unique runs
  fills the pool fast. The cap is there for this — it stops the loop
  and says so. The fix is a shorter read, a second separator, or (when
  built) sorting only the new parts into the existing order instead of
  resorting the whole pool.

## 7. Loop

Feed the parts back in. Repeat until nothing new comes out.

```
pool = the initial set of things (runs, features, whatever you start with)

while True:
    new_parts = compare every pair of neighbours in the sorted pool
    if no new parts were made:
        break
    add new_parts to pool
```

The stable point — a round that produces nothing new — is the only
stopping rule. Not a round limit, not a time limit, not a score
threshold. The loop runs until the pool has been fully compared against
itself and everything that can be found has been found.

Discovery's mint loop does this in 7 to 30 rounds depending on the
signal. The count of new parts per round always falls to zero:

```
Alice:   10038 3800 1303 484 176 88 37 22 15 10 4 1 2 0
German:  9291 3641 1205 402 130 42 7 2 1 0
```

Then the whole thing runs again one level up (the runs as symbols,
the classes as a second way to match), and the level loop runs until
that produces nothing new either. Same rule at every scale.

A reference implementation of the core loop in Python:

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

That's the bones. Discovery adds the reverse pass (shared endings),
the part-of and made-of connections, the counts, the fresh-pair rule,
and the cap. But the loop is this loop.

## 8. Keep all

Never throw away a part, a count, a connection, or a leftover. Every
intermediate result is information.

- A part that appeared once is kept with the same standing as a part
  that appeared a thousand times. Rare but real is worth having.
- A leftover from a comparison is a part in its own right. It goes back
  in the pool and gets compared in the next round.
- A count says how often something happened. It doesn't decide whether
  the thing exists — existence is binary, count is how common.
- A connection (this is part of that, this comes after that, this
  changes into that) is a fact about the signal. It gets written down,
  not evaluated.

Throwing away intermediate results means you can't find things that
depend on them. A part that gets discarded because it's "too common"
or "not significant enough" might be the piece that two other parts
share, and without it, the comparator can't find the connection.

Discovery has no deletion anywhere. The pool is a dictionary keyed by
content. Counts are values. Nothing fades, nothing expires, nothing
gets pruned. The only compression is storing each distinct part once
with its count — one entry per thing, not a thousand copies.

---

## How Discovery does each one

| step | in the process | in Discovery |
|---|---|---|
| compare | take two things, split three ways | `shared_head()` on sorted neighbours |
| features | raw ordered sequences | bits → words → runs, compared as symbol sequences |
| ablation | not used | nothing is dropped |
| feedback | against memory, against own output | `--memory`, `hybrid/loop.py` |
| examples | show input, parts, recovery | the four `examples/` folders with breakdowns |
| limits | says where it runs out | `notes/open.md` |
| loop | until stable | `mint()`, `run_levels()` |
| keep all | never remove | the pool is append-only; no deletion in the code |

---

## Why it works

Each step of the process makes a claim. Here's why each one holds. All
of them can be checked against the code (`discovery.py`) and against the
example records.

### The split is lossless (step 1: compare)

Take two things A and B. The comparator produces a shared head H and
two leftovers: tail_A (what's left of A after H) and tail_B (what's left
of B after H).

H + tail_A = A. H + tail_B = B. You can always rebuild the originals
from the pieces. Nothing was destroyed — the same information exists, in
more pieces. The "not part" set (everything else in the pool) wasn't
touched at all.

This means the split can be run over and over without losing anything.
Each round makes more pieces, never fewer. Combine this with step 8
(keep all) and the pool is a complete record of every split that ever
happened.

### Order carries structure that shuffling destroys (step 2: features)

A pair like `th` only exists because `t` and `h` are next to each other.
Shuffle the signal and the pair is gone. The comparator can only find
what's in its features. If the features are ordered sequences, it finds
shared beginnings and endings — both of which depend on position. If
the features are unordered sets, it finds shared membership but not
shared position.

This is a one-way door. Ordered features can always be treated as a set
(ignore the order), but a set can't be put back in order. So starting
with ordered features keeps all options open. Starting with unordered
features closes off everything that depends on position.

Discovery starts with ordered sequences. That's why it can find `th` as
a pair, not just `t` and `h` separately.

### Ablating both sides squares the loss (step 3: ablation)

Each feature either survives the drop or doesn't. If you drop from one
side at rate r, a feature has a (1 − r) chance of surviving. If you drop
from both sides at rate r, a feature has to survive both drops: (1 − r)
times (1 − r) = (1 − r)².

At 30% drop rate: one side gives 0.70 survival. Both sides gives 0.49.
You've lost more than half your signal for no gain — the comparison still
only produces the three-way split. Ablating both sides doesn't find
anything that ablating one side misses.

The ablation lesson from experiment: if the signal already has noise
(randomized positions, scattered features), ablation on top of that puts
the real signal below the noise floor. Clean first, ablate second. Or
don't ablate at all — Discovery doesn't.

### The comparator is its own scorer (step 4: feedback)

The comparator takes two things and produces parts. Those parts are the
same kind of thing as the inputs — sequences of symbols. So the
comparator can take its own output as input. No adapter needed.

This gives three kinds of feedback, all using the same comparison:

**Against memory.** Compare this signal's parts to a saved pool. Three
bins: confirmed (already known), added (new this time), not seen (known
but absent from this signal). This works because "is this part in the
saved pool?" is the same question as "do these two things share this
piece?" — it's the comparator with one input being the saved pool.

**Against its own output.** Run the parts back through the process. Then
compare the two pools: what came back the same, what was lost, what's
new. If a part was lost, the process dropped it somehow. If a part is
new, the process created it — a different neighbour order made a different
collision. The comparator finds both without a separate scoring function.

**Against an answer key.** Compare the output to a known correct answer.
Same and different. This is the version most systems use — a test against
a target. The comparator does it with the same operation it uses for
everything else.

All three work because the output is the same type as the input. The
technical word for this is closure: the operation's output stays in the
operation's domain. There's no conversion step, no loss function, no
separate scoring mechanism. The comparator does the scoring.

### The loop always stops (step 7: loop — termination)

The pool can only grow. Every round, the mint looks at sorted neighbours
and splits them. A split can make at most three pieces (the shared head
and two leftovers), and each piece is shorter than what it came from. Only
pieces the pool hasn't seen before get added. The number of possible
pieces is finite — bounded by every substring of every run that was ever
in the pool. A finite set that only grows and never shrinks must stop
growing. When nothing new is added, the loop exits.

The level loop has the same shape: each level takes the runs from the
level below and re-runs the mint. The runs get fewer and longer at each
level. When a level produces a single run or finds nothing new, it stops.
In practice, Discovery takes 7 to 30 mint rounds at level 0 and 2 to 4
levels total.

### The loop finds everything the sorted order can show (step 7: loop — completeness)

Two runs that share a beginning will end up next to each other when the
pool is sorted, because sorting puts things with the same prefix
together. When they're neighbours, the comparator finds the shared
beginning and splits it out. This means every shared prefix that exists
between any two runs in the pool will be found — sorting guarantees they
meet.

The mirror pass does the same thing from the other end: it reverses
everything, sorts, compares, and reverses the results back. That catches
shared endings (suffixes) the same way the forward pass catches shared
beginnings.

Shared middles — a piece buried inside two runs with different beginnings
and different endings — aren't guaranteed in one pass. But they don't
need to be. As the loop strips off shared beginnings and endings round
after round, what used to be a middle becomes the beginning or ending of
a shorter leftover. The next round's sort puts it next to something that
shares it, and the comparator finds it. The only case where a shared
middle stays hidden is when it never gets exposed this way — when the
pieces around it are all unique and nothing peels them off. That's a real
limit, noted in section 6.

### Every part the loop finds is real (step 7: loop — soundness)

The mint never invents a part. Every part in the pool exists because two
actual neighbours in the sorted pool matched from the front (or back) for
some number of positions. The shared piece is copied from the input, not
generated. The leftovers are what's left of the input after the shared
piece is removed. Counts are exact: each collision that produced a part
is a real event in the sorted pool.

Classes are the same: two parts end up in the same class because the mint
found the exact same set of changes applied to both (same endings added,
same beginnings added). The grouping comes from the data, not from a rule
about what "should" go together.

### Deletion is irreversible (step 8: keep all)

If you delete a part, you lose:

- The part itself.
- Every "part of" connection it carries — every record that it sits
  inside something else.
- Every "made of" connection — every record that it's built from
  smaller pieces.
- Its class membership — its place in any group that shares changes.
- Any future collision. The next round of the loop might have found
  something new because that part was in the sorted pool next to
  something else. Without it, that neighbour pair never happens and the
  discovery never occurs.

None of these can be recovered without re-running the whole process.
The system has no prediction — it doesn't know what will be needed later.
The only safe answer is to keep everything.

Compression is not deletion. Storing each distinct part once with its
count is compression. The pool is a dictionary: one entry per thing, not
a thousand copies. Counts are values in the dictionary. Nothing fades,
nothing expires, nothing gets pruned. The count says how common it is.
Existence says it's real.

### Same input, same output (determinism)

The pool is sorted before every comparison. Sorted order is the same
every time for the same contents. The mint walks the sorted list from
front to back, same pairs in the same order. No randomness anywhere.
Run it twice on the same file, get the same record.

### Nothing is deleted in the code (verification)

Every mutation in the code is an addition: `pool[key] = ...`,
`made_of[key] = ...`, `part_of.setdefault(...)`. There is no `del`, no
`pop`, no `remove`, no `discard` on the pool or any of its related
tables. Parts go in and stay in. This is checkable: search the source
for any deletion on the pool dictionary. There isn't one.
