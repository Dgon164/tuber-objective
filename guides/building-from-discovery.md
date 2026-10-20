# How to make new things on Discovery

This guide has 3 parts:

- the givens (the base of the program)
- the reason that the set of givens is enough
- how to make new things on the program

The third part shows 3 extensions in `extend/`. Each extension adds a few
lines. Each extension gets results that nothing in the original file gave.

## The givens

Each given is a thing that the program assumes or does. Each given also
says where in the records you can see the given at work.

**1. All storage is bits, and the bits do not say the word width.**
A file is a string of bits. The word width is the number of bits in 1
word. The word width is an agreement between the writer of the file and
the reader of the file. The frame step finds that agreement from the bits
alone. See the given at work in:

- `examples/text` (8 bits for each character, and the top bit is never 1)
- `examples/code` (64-bit words for a modern program, with the
  little-endian decrease visible in the column rates)
- `examples/agc` (15-bit words, from a file where no word starts on a
  byte boundary)

**2. A comparator and a memory are the whole set of tools.** The
comparator gives same, different, and not part. The memory is a place to
keep what the program saw, so the program can compare the next thing
against the memory. See the given at work in `discovery.py`: each
function is a comparison with that 3-way result, or a count of such
results. There is no other operation in the file.

**3. The most common thing is the background.** A run is the content
between 2 occurrences of the most common symbol (the separator). To cut
is to divide the signal into runs at the separator. See the given at work
in these separators:

- the space character in text
- the zero byte in binary
- the zero 64-bit word in a compiled program
- the EXTEND instruction in Apollo guidance code

The separators 1 level up are `the`, the comma, and `#`.

**4. Compare things until nothing new comes out, and keep everything.**
The loop mints parts. To mint a part is to make a new part from 2 parts
that have the same start or the same end. The loop has 5 steps:

1. Sort the pool. To sort the pool is to put the parts of the pool in
   order.
2. Compare adjacent parts.
3. Mint the shared start and the 2 parts that remain.
4. Put the new parts back into the pool.
5. Repeat until the pool is stable.

The program removes nothing. The number of times that a part occurred is
a number on the entry. See the given at work in the MINT line of each
record. The MINT line decreases to 0 in 7 to 30 rounds. Also see `e`: `e`
is never a whole word alone, but `e` is inside 1,615 parts.

**5. The connections of a thing are its definition.** The connections
are:

- what the thing contains
- what contains the thing
- what the thing changes into
- what occurs next to the thing

The density of a part is the number of things that contain the part. See
the given at work in the CRYSTAL entry for `the`, `die`, `Kommission`,
and `for`.

**6. Parts that take the same changes are 1 kind.** See the given at
work in these groups:

- 22 stems with `{+ed, +ing}`
- 52 stems with `{+en, +t}`
- 42 stems with `{+n, +r}`
- the pairs of a capital letter and a small letter `{A+, a+}`

**7. Crystallize, then loop again: replace nothing, add everything.** To
crystallize is to group the parts by the changes that the parts accept.
The program cuts the runs again 1 level up. The classes are a second way
to be the same. Each structure goes into 1 pool. The process repeats
until there is nothing more to cut.

See the given at work in the LEVELS table: 22,446, then 6,709, then 5,
then 1.

**8. Evaluation is the comparator on the output of the model.** The
question "is the model the same as reality?" is the same question as "is
this thing the same as that thing?". Memory closes the loop. See the
given at work in `examples/memory`: the second read of the second half of
Alice confirms 19,833 parts and adds 0 at level 0.

## Proof that the givens are enough

The claim is not that the program does everything. The claim has 2 parts.
First, the program needs nothing more than the givens for what the
program does. Second, each new thing that you point the program at needs
a new target, not a new tool.

- A count is the comparator with memory: the same thing again, add 1.
- A cut is the comparator: this word is the background, the last word was
  not, so there is a border.
- The mint step is the comparator on 2 things at the same time. The result is
  the same start, the 2 different parts that remain, and everything else
  outside the comparison.
- Composition is containment. Containment is a comparison: 1 part is in a
  second part. The mint step finds the containment and keeps the
  containment as a connection.
- A class is the comparator on sets of changes: the same set of changes
  puts things in 1 group.
- A level is the comparator on runs instead of words. `mint()` works on
  tuples. The type of the parts in a tuple is not important to `mint()`.
  Thus level 1 needed no code that level 0 did not already have.
- A second kind of "same" (class membership) is a branch of 4 lines in
  `head()`. The part that the program mints carries the class in the
  position where the 2 parts differ.
- Evaluation is the comparator on the output of the model. Memory is the
  pool that the program saved. Neither of the 2 added an operation. The
  memory added only a file.

Each extension to date is a new thing to compare, not a new way to
compare. That is the argument. The set of tools has not needed a new
tool. The records show the same tool on 4 different kinds of signal and
then on its own memory.

The word "enough" does not cover 2 things. The program names nothing: a
class is its set of changes, not "verb". The program acts on nothing
outside itself: the only actions of the program are to write the record
and to update its memory. A name is a lens on the record. An action on
the outside world is the job of a different system. The guide
`guides/hybrid-systems.md` covers such systems.

## How to extend the program: point the comparator at a new target

The program has 4 places where a new target connects. Each of the 3
extensions below uses 1 place. Each extension is short enough to read in
full.

| place to point | what the place changes | extension |
|---|---|---|
| the cut | where the program divides the run sequence | `extend/cut_at_class.py` |
| the kind of same | what is a match | `extend/same_within.py` |
| the comparison target | the 2 things that the program compares | `extend/row_by_row.py` |
| the signal | what goes in | any file (see `guides/any-signal.md`) |

### Cut at a class instead of the most common word

Normally, `discovery.py` cuts level 1 at the most common run (`the`).
This extension cuts at the largest level-0 class instead. Each stem that
takes both `+ed` and `+ing` becomes a separator. Each complete word that
has such a stem also becomes a separator. The runs of level 1 are then
the content between verbs.

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

The words immediately before a verb are `and`, `to`, and `she`. The words
immediately after a verb are `herself`, `out`, `the`, `a`, `at`, and `a
little`. Nothing in the program knew what a verb was. The class was 22
stems that take 2 specific endings. The cut at that class shows the words
that occur next to those stems. New lines of code: 4 lines (the separator
set), plus the call into `run_level` with those separators.

### A new kind of same: numbers within a range

`mint()` takes a `class_of` map. The map goes from a symbol to the
replacement for that symbol when 2 symbols are the same by class. The
main program uses the map for crystal classes (groups of parts that share
the same set of changes). This extension fills the map with ranges
instead.

A pair of 15-bit words is "the same" if the 2 words are within 8 of each
other. On the Apollo rope, 2 runs that differ only by a near
address now collide. The range stands in that position.

```
plain mint:        8538 parts
with same-within:  50319 parts, of which 2580 carry a range (~) in a slot

  05353.~04020             14   e.g. 05353.04022 / 05353.04024
  ~74740.10000             43   e.g. 74745.10000 / 74740.10000.13475
  ~32630.04616.20334.12603 14
```

`05353.~04020` is `TC PHASCHNG` and then an argument in the 04020 range.
The phase-change codes 04022, 04024, and 04026 are within 8 of each
other. Thus the calls to PHASCHNG with any of the 3 codes become 1 part
with 14 occurrences. New lines of code: 1 line (the range map), and 1
line (the display of a range).

### The comparator on adjacent rows

The frame step compares a column with itself 1 row down. A signal with a
time dimension has a second kind of same: a row against the row that
comes before. The extension runs on the reservoir states (32 units, 1 row
for each byte of Alice that goes through the network). The extension
compares each row with the row before that row. A bit that changed between the 2 rows is
a flip. The flips become a new signal. Discovery reads the flips like any
other signal.

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

Units 28, 21, and 2 never move. The column rates said the same thing. Now
the flips show the same thing from the other direction.

The most common change is a flip of 8 specific units together. This
change occurred 149 times. This change is the most common step of the
network. New lines of code: 2 lines (the XOR and the rate for each
column). The extension also writes the flips to a file and calls
`discover` on that file.

### The other 3 extensions in the repository

- A comparison of 2 signals: `examples/german/bridge.py`. The script is
  the comparator on 2 records. The result is the shared parts and the
  parts that contain the shared parts, on each side.
- A different system on either side: `hybrid/`. The scripts make a rule
  table from the record. The scripts put the states of a network into
  Discovery. The scripts loop the output of the model back into
  Discovery.
- Many signals over time: `--memory`. The flag is the comparator on a
  signal against everything in the memory. The bins are confirmed, added,
  and not seen.

## How to add something new

1. Select 1 of the 4 places to point at: the cut, the kind of same, the
   comparison target, or the signal.
2. Write the new thing. The new thing is usually a map, a set, or a line
   that makes a new file.
3. Call `run_level` or `discover` with the new thing. Do not change the
   mint, the crystal, or the levels.
4. Read the record. If the record shows a thing that the plain run did
   not show, keep the lines. If the record shows nothing new, the signal
   did not have the thing.

Each script in `extend/`, `hybrid/`, and `examples/german/bridge.py` has
the same shape. Thus the 1 new thing is the only thing that you must
read. The root is 1 call:

```
import discovery as D

# ---- the signal, as discovery.py reads it -------------------------------
R = D.Root(sys.argv[1])      # read, frame, words, level 0, the shared pool

# ---- NEW: the one new thing ---------------------------------------------
...                          # on R.words, R.L0, R.pool, R.part_of; R.level(...) for one level more

# ---- what it found ------------------------------------------------------
print(...)                   # R.draw(x) draws a part through the lens
```

`Root` takes 3 of the 4 places as arguments: `separators` (the cut),
`same` (the kind of same), and the path (the signal). The comparison
target is what the NEW section does with what `Root` holds. `discover()`
itself is `Root` plus `all_levels()` plus the record. Thus the root of
each program and the root of the program are the same call.

A script that reads a record instead of a signal starts with *the
record, as discovery.py wrote it* (`json.load` of the `.record.json`). A
script with a new thing that makes a new signal has *the ..., as
discovery.py reads it* after the NEW section. That line is a call to
`discover`. The output that each script prints is committed next to the
script.

None of the 3 extensions above took more time to write than to read. That
is the practical result when the givens are enough.
