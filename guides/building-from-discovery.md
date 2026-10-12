# Building from Discovery

Three things: what the program rests on (the givens), why that set is
enough, and how to build on it — shown by actually building, with three
extensions in `extend/` that each add a handful of lines and get
results nothing in the original file gave.

## The givens

Each one is something the program assumes or does, with the place in
the records where you can see it working.

**1. Everything stored is bits, and the chunk size isn't in the bits.**
A file is a string of bits. The word width is an agreement between
whoever wrote the file and whoever reads it. The frame step figures out
that agreement from the bits alone. See it in: `examples/text` (8,
top bit never on), `examples/code` (64 for a modern program, with the
little-endian drop-off visible in the column rates), `examples/agc`
(15, from a file where no word starts on a byte boundary).

**2. A comparator and a memory are the whole kit.** Same, different,
not part — and a place to keep what was seen so there's something to
compare the next thing against. See it in: every function in
`discovery.py` is a comparison with that three-way result, or a count
of such results. There's no other operation in the file.

**3. The most common thing is the background.** A run is what sits
between two of it. See it in: the space, the zero byte, the zero
64-bit word, EXTEND; one level up, `the`, the comma, `#`.

**4. Smash things together until nothing new comes out, and keep
everything.** Sort the pool, compare neighbours, mint the shared
beginning and the two leftovers, let them rejoin, loop until stable.
Nothing removed; how often something appeared is a number on the entry.
See it in: the MINT line of every record, falling to 0 in 7 to 30
rounds; `e` never a whole word and inside 1,615 parts.

**5. A thing's connections are its definition.** What it's made of,
what contains it, what it changes into, what it shows up next to.
Density is the number of things that contain it. See it in: the CRYSTAL
entry for `the`, `die`, `Kommission`, `for`.

**6. Parts that take the same changes are one kind.** See it in: 22
stems with `{+ed, +ing}`; 52 with `{+en, +t}`; 42 with `{+n, +r}`;
capitalised pairs `{A+, a+}`.

**7. Crystallize, then loop again; nothing replaced, everything added.**
The runs cut one level up, the classes as a second way to be the same,
every structure into one pool, until there's nothing left to cut. See
it in: the LEVELS table — 22,446, then 6,709, then 5, then 1.

**8. Evaluation is the comparator pointed at the model's own output.**
"Does the model match reality?" is the same question as "Is this the
same as that?" Memory closes the loop. See it in: `examples/memory` —
the second half of Alice read twice confirms 21,278 and adds 0 at
level 0.

## Why the givens are enough

The claim is not that the program does everything. It's that nothing
beyond the givens is needed for what the program does, and that each
new thing you point it at needs a new target, not a new tool.

- Counting is the comparator with memory: same thing again, add one.
- Cutting is the comparator: this word is the background, the last one
  wasn't — there's a border.
- Minting is the comparator on two things at once: the same beginning,
  the two different leftovers, and everything else not part of the
  comparison.
- Composition is containment, and containment is a comparison: this is
  part of that, found while minting and kept as a connection.
- Classes are the comparator on the change sets: the same set of
  changes.
- Levels are the comparator on runs instead of words. `mint()` works on
  tuples and doesn't care what the elements are, so nothing had to be
  written for level 1 that wasn't already there for level 0.
- A second kind of same (class) is a four-line branch in `head()`. The
  minted part carries the class in the spot where the two differ.
- Evaluation is the comparator on the model's output. Memory is the
  pool saved. Neither added an operation; one added a file.

Every extension built so far has been a new thing to compare, not a new
way to compare. That's the argument: the kit hasn't needed a new tool,
and the records show the same tool reading four different kinds of
signal and then reading its own memory.

What "enough" does not cover, said once: the program doesn't name
anything (a class is its set of changes, not "verb"), and it doesn't
act on anything outside itself (its only action is the record and the
change to its memory). Naming is a lens laid over the record. Acting on
the outside world is another system's job — that's what
`guides/hybrid-systems.md` is for.

## How to expand — by pointing the comparator somewhere new

The program has four places where a new target plugs in. Each of the
three extensions below uses one, and each is short enough to read in
full.

| place to point | what it changes | extension |
|---|---|---|
| the cut | where the run sequence gets divided | `extend/cut_at_class.py` |
| the kind of same | what counts as a match | `extend/same_within.py` |
| the comparison target | which two things get compared | `extend/row_by_row.py` |
| the signal | what goes in | any file; `guides/any-signal.md` |

### Cut at a class instead of the most common word

`discovery.py` cuts level 1 at the most common run (`the`). This
extension cuts at the biggest level-0 class instead: every stem that
takes both `+ed` and `+ing`, and every complete word built on such a
stem, becomes a separator. Level-1 runs are then the stretches between
verbs.

```
level 1 cut at class [+ed, +ing]: 58 separators
  56 runs between them, 56 distinct, 78 parts minted

ENDINGS (right before such a stem)      BEGINNINGS (right after)
  +and      13                            herself+   9
  +to        5                            out+       9
  +she       5                            the+       8
                                          a+         8
                                          at+        8
                                          a little+  7
```

What sits right before a verb: `and`, `to`, `she`. Right after:
`herself`, `out`, `the`, `a`, `at`, `a little`. Nothing in the
program knew what a verb was; the class was 22 stems that take two
endings, and cutting at that class shows the company those stems keep.
New lines of code: four (the separator set), plus the call into
`run_level` with those separators.

### A new kind of same: numbers within a range

`mint()` takes a `class_of` map — from a symbol to what stands in for
it when two symbols match by class. The main program uses this for
crystal classes. This extension fills it with ranges instead: two
15-bit words count as "the same" if they fall within 8 of each other.
On the Apollo rope, two runs that differ only by a nearby address now
collide, and the range stands in that spot.

```
plain mint:        8538 parts
with same-within:  50319 parts, of which 2580 carry a range (~) in a slot

  05353.~04020             14   e.g. 05353.04022 / 05353.04024
  ~74740.10000             43   e.g. 74745.10000 / 74740.10000.13475
  ~32630.04616.20334.12603 14
```

`05353.~04020` is `TC PHASCHNG` followed by an argument in the 04020
range — the phase-change codes 04022, 04024, 04026 are within 8 of
each other, so the calls to PHASCHNG with any of them smash into one
part with 14 instances sitting on it. New lines of code: one (the range
map), one (how a range is displayed).

### The comparator pointed at consecutive rows

The frame step compares a column with itself one row down. A signal
with time in it has a second kind of sameness: this row against the
row before it. On the reservoir states (32 units, one row per byte of
Alice fed through the net): bits that stayed the same stayed, bits that
changed flipped. The flips are a new signal, and Discovery reads them
like any other.

```
frame 32; 20000 rows; 19999 row-to-row comparisons
units that flip least:  unit 28 0.002, unit 21 0.002, unit  2 0.006
units that flip most:   unit 15 0.542, unit 20 0.538, unit 12 0.519
bits flipped per step:  8.38 of 32 on average; 31 steps with no change
most common change (which units flipped together):
  00001000100001000100100000010000  149 times

Discovery on the flips (level 0):
  chosen width 32
WORDS   19999 words, 6701 distinct
RUNS   150 runs between separators, 150 distinct
MINT   7 rounds; parts minted per round: 643 280 61 18 9 2 0
```

Units 28, 21, and 2 never move (the column rates said the same thing;
now the flips say it from the other direction). The most common change —
eight particular units flipping together — happened 149 times. That's
the net's most common step. New lines of code: two (the XOR and the
per-column rate), plus writing the flips to a file and calling
`discover` on it.

### Three more that are already in the repo

- Two signals compared: `examples/german/bridge.py` — the comparator
  on two records; shared parts and their containing parts on each side.
- Another system on either side: `hybrid/` — a rule table from the
  record, a net's states into Discovery, and the loop that reads the
  model's output back.
- Many signals over time: `--memory` — the comparator on a signal
  against everything remembered; confirmed, added, not seen.

## How to add something new

1. Pick which of the four places you're pointing at: the cut, the kind
   of same, the comparison target, or the signal.
2. Write the new thing. It's usually a map, a set, or a line that
   makes a new file.
3. Call `run_level` or `discover` with it. Don't change the mint, the
   crystal, or the levels.
4. Read the record. If it shows something the plain run didn't, keep
   the lines. If it shows nothing new, the signal didn't have it.

Every script in `extend/`, `hybrid/` and `examples/german/bridge.py` has
the same shape, so that the one new thing is the only thing to read.
The root is one call:

```
import discovery as D

# ---- the signal, as discovery.py reads it -------------------------------
R = D.Root(sys.argv[1])      # read, frame, words, level 0, the shared pool

# ---- NEW: the one new thing ---------------------------------------------
...                          # on R.words, R.L0, R.pool, R.part_of; R.level(...) for one level more

# ---- what it found ------------------------------------------------------
print(...)                   # R.draw(x) draws a part through the lens
```

`Root` takes the four places to point as arguments where they are
arguments: `separators` (the cut), `same` (the kind of same), the path
(the signal); the comparison target is what the NEW section does with
what `Root` holds. `discover()` itself is `Root` plus `all_levels()`
plus the record, so the root of every program and the root of the
program are the same call.

A script that reads a record instead of a signal opens with *the
record, as discovery.py wrote it* (`json.load` of the `.record.json`);
one whose new thing makes a new signal has *the ..., as discovery.py
reads it* after the NEW section, as a call to `discover`. The output
each one prints is committed beside it.

None of the three extensions above took longer to write than to read.
That's what the givens being enough looks like in practice.
