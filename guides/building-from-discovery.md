# How to make new things on Discovery

This guide has three parts:

- the givens: the things the program assumes or does, which everything
  else rests on
- why that set of givens is enough
- how to build new things on top of the program

The third part walks through three extensions in `extend/`. Each one adds
a few lines to the program and gets results that nothing in the original
file gave.

## The givens

Each given is something the program assumes, or something it does. For
each one, this section says what it is in plain words and where in the
records you can see it working.

**1. Every file is a string of bits, and the bits don't say how wide one
unit is.** The program reads a file as one long string of bits. Somewhere
in that string there's a natural unit: 8 bits for a byte of text, 15 bits
for an Apollo word, 64 bits for a modern machine word. But the width of
that unit is an agreement between whoever wrote the file and whoever
reads it, and it isn't written down in the file. The frame step, the part
of the program that works out the width, finds that agreement from the
bits alone, by trying each width and looking for the one where the bit
patterns line up. See it working in:

- `examples/text` (8 bits per character, and the top bit is never 1)
- `examples/code` (64-bit words for a modern program; the numbers in it
  are stored low byte first, a layout called little-endian, and you can
  see that as a falloff in how often each bit position is 1 across the
  word)
- `examples/agc` (15-bit words, from a file where no word starts on a
  byte boundary)

**2. The only tools are one comparison and one memory.** The comparison
takes two things and gives back three results: the part they share,
what's left of each once the shared part is removed, and everything the
comparison didn't touch. The memory is a place to keep what the program
has seen, so that the next thing can be compared against it. See it
working in `discovery.py`: every function in the file is either that
three-way comparison or a count of its results. There is no other
operation in the file.

**3. The most common unit is the background, and the program cuts the
file at it.** Once the program knows the unit width, it counts the units.
The one that occurs most often becomes the divider, the way a space
divides words in text. The program then cuts the file into chunks at
every divider, so a chunk is whatever sits between two dividers. See it
working in the dividers the program found:

- the space character in text
- the zero byte in binary
- the zero 64-bit word in a compiled program
- the EXTEND instruction in Apollo guidance code

One level up, where the chunks themselves are the units, the dividers it
found are `the`, the comma, and `#`.

**4. Compare things until nothing new comes out, and keep everything.**
The program keeps a collection of every part it has found so far; call
that the pool. In each round it makes new parts out of pairs of parts
that start the same way or end the same way. That's called minting a
part. The round has five steps:

1. Sort the pool, which puts the parts in alphabetical order so that
   parts with the same beginning sit next to each other.
2. Compare each part with its neighbour.
3. Make three new parts from each pair: the shared start and the two
   leftovers.
4. Put the new parts back into the pool.
5. Repeat until a round makes nothing new.

The program removes nothing. How many times a part occurred is just a
number stored on its entry. See it working in the MINT line of each
record, where the number of new parts falls to 0 in 7 to 30 rounds. Also
look at `e`: it's never a whole word on its own, but it sits inside
1,615 parts.

**5. A thing is defined by what it's connected to.** The program never
says what a part is. It records what the part is connected to:

- what the part contains
- what contains the part
- what the part turns into
- what sits next to the part

The number of things that contain a part is what the record calls its
density. See it working in the CRYSTAL entry, the record's dictionary-style
entry for a common chunk, for `the`, `die`, `Kommission`, and `for`.

**6. Parts that take the same changes are one kind.** If two parts both
take the same additions, the program puts them in one group. See it
working in these groups:

- 22 stems that take `{+ed, +ing}`
- 52 stems that take `{+en, +t}`
- 42 stems that take `{+n, +r}`
- the pairs of a capital letter and its small letter, `{A+, a+}`

**7. Group the parts, then go up a level: replace nothing, add
everything.** After the pool settles, the program groups the parts by
which changes they accept. That grouping is called crystallizing, and
the groups it makes are the classes. Then the program cuts the chunks
again one level up, treating each chunk as a single unit, and runs the
whole thing again. At the new level, two things count as the same if
they're equal, or if they belong to the same class. Everything the
program finds at every level goes into the one pool. The process repeats
until there's nothing left to cut.

See it working in the LEVELS table: 22,446 parts, then 6,709, then 5,
then 1.

**8. To check the model, compare its output the same way.** The question
"does the model match reality?" is the same question as "is this thing
the same as that thing?", and the same comparison answers it. Memory is
what closes the loop: save what one file produced, read the next file
against it. See it working in `examples/memory`: reading the second half
of Alice a second time confirms 19,833 parts and adds 0 at level 0.

## Why the givens are enough

The claim is not that the program does everything. The claim has two
parts. First, the program needs nothing beyond the givens to do what it
does. Second, every new thing you point the program at needs a new
target, not a new tool.

- A count is the comparison plus memory: the same thing again, so add
  one.
- A cut is the comparison: this unit is the background and the last one
  wasn't, so there's a boundary here.
- The mint step is the comparison on two things at once. The result is
  the shared start, the two leftovers, and everything else untouched.
- Composition is containment, and containment is a comparison: one part
  sits inside another. The mint step finds that and keeps it as a
  connection.
- A class is the comparison on sets of changes: the same set of changes
  puts two things in one group.
- A level is the comparison on chunks instead of units. `mint()` works on
  tuples, which are ordered lists of items, and it doesn't care what the
  items are. So level 1 needed no code that level 0 didn't already have.
- A second kind of "same" (belonging to the same class) is a four-line
  branch in `head()`, the function that finds how far two parts match
  from the front. The part it makes carries the class in the position
  where the two parts differ.
- Checking the model is the comparison on the model's output. Memory is
  the pool, saved to a file. Neither of these added an operation. Memory
  added only a file.

Every extension so far has been a new thing to compare, not a new way to
compare. That's the whole argument. The set of tools has never needed a
new tool. The records show the same tool on four different kinds of file
and then on its own memory.

There are two things "enough" doesn't cover. The program names nothing: a
class is its set of changes, not "verb". And the program acts on nothing
outside itself: the only things it ever does are write the record and
update its memory. A name is a way of reading the record, laid over the
top of it. Acting on the outside world is the job of a different system,
and `guides/hybrid-systems.md` covers those.

## How to extend the program: point the comparison at something new

The program has four places where a new target can plug in. Each of the
three extensions below uses one of them. Each is short enough to read in
full.

| place to point | what the place changes | extension |
|---|---|---|
| the cut | where the program divides the sequence of chunks | `extend/cut_at_class.py` |
| the kind of same | what counts as a match | `extend/same_within.py` |
| the comparison target | which two things the program compares | `extend/row_by_row.py` |
| the signal | what goes in | any file (see `guides/any-signal.md`) |

### Cut at a class instead of the most common word

Normally `discovery.py` cuts level 1 at the most common chunk, which in
Alice is `the`. This extension cuts at the largest level-0 class instead.
Every stem that takes both `+ed` and `+ing` becomes a divider, and so
does every complete word built on such a stem. The level-1 chunks are
then whatever sits between one verb and the next.

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

What came out: the words that sit immediately before a verb are `and`,
`to`, and `she`. The words that sit immediately after one are `herself`,
`out`, `the`, `a`, `at`, and `a little`. That's interesting because
nothing in the program knew what a verb was. The class was just 22 stems
that happen to take two particular endings. Cutting at that class is
what shows you the words that live next to those stems. New lines of
code: four (the set of dividers), plus the call into `run_level` with
those dividers.

### A new kind of same: numbers within a range

`mint()` takes a map called `class_of`. For each symbol, the map says
what stands in for it when two symbols count as the same by class. The
main program fills the map with the classes from crystallizing (groups
of parts that share the same set of changes). This extension fills it
with ranges instead.

Two 15-bit words count as "the same" if they're within 8 of each other.
On the Apollo rope, the read-only program memory of the Apollo Guidance
Computer, two chunks that differ only by a nearby address now match. The
range takes the place of the exact number in that position.

```
plain mint:        8538 parts
with same-within:  50319 parts, of which 2580 carry a range (~) in a slot

  05353.~04020             14   e.g. 05353.04022 / 05353.04024
  ~74740.10000             43   e.g. 74745.10000 / 74740.10000.13475
  ~32630.04616.20334.12603 14
```

What came out: `05353.~04020` is `TC PHASCHNG` followed by an argument
somewhere in the 04020 range. The phase-change codes 04022, 04024, and
04026 are all within 8 of each other, so a call to PHASCHNG with any of
the three now becomes one part, seen 14 times. That's interesting because
the plain program would have kept those as three separate parts; the
range lets the comparison see that they're the same call. New lines of
code: one (the range map) and one (how to display a range).

### Comparing each row with the row before it

The frame step compares a column with itself one row down. A signal that
unfolds over time has a second kind of same: a row compared against the
row that came before it. This extension runs on the states of a
reservoir, which is a small random network whose connections never
change. The reservoir here has 32 units. Each byte of Alice goes through
it, and after each byte the on/off state of the 32 units is written down
as one row. The extension compares each row with the row before it.

A bit that changed between two rows is a flip. The flips become a new
signal, and Discovery reads them like any other file.

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

What came out: units 28, 21, and 2 never move. The column rates (how
often each bit position is 1) said the same thing when Discovery read
the states directly. Now the flips show it from the other direction.

The most common change is a flip of eight specific units together, and it
happened 149 times. That is the network's most common step. That's
interesting because it's a map of what the network does, made without
looking inside it. New lines of code: two (one to mark which bits differ
between two rows, which in code is a single XOR, and one for the rate
per column). The extension also writes the flips to a file and calls
`discover` on that file.

### The other three extensions in the repository

- Comparing two files: `examples/german/bridge.py`. The script runs the
  comparison on two records. The result is the parts both share, and the
  parts that contain the shared parts, on each side.
- A different system on either side: `hybrid/`. These scripts build a
  rule table out of the record, feed the states of a network into
  Discovery, and loop the output of a model back into Discovery.
- Many files over time: `--memory`. The flag compares a file against
  everything in the memory. The results fall into three bins: confirmed,
  added, and not seen.

## How to add something new

1. Pick one of the four places to point at: the cut, the kind of same,
   the comparison target, or the signal.
2. Write the new thing. It's usually a map, a set, or a line that makes a
   new file.
3. Call `run_level` or `discover` with the new thing. Don't change the
   mint step, the crystallizing step, or the levels.
4. Read the record. If it shows something the plain run didn't, keep the
   lines. If it shows nothing new, the signal didn't have that thing in
   it.

Every script in `extend/`, in `hybrid/`, and `examples/german/bridge.py`
has the same shape, so the one new thing is the only thing you have to
read. The root of each is a single call:

```
import discovery as D

# ---- the signal, as discovery.py reads it -------------------------------
R = D.Root(sys.argv[1])      # read, frame, words, level 0, the shared pool

# ---- NEW: the one new thing ---------------------------------------------
...                          # on R.words, R.L0, R.pool, R.part_of; R.level(...) for one level more

# ---- what it found ------------------------------------------------------
print(...)                   # R.draw(x) draws a part through the lens
```

`Root` takes three of the four places as arguments: `separators` (the
cut), `same` (the kind of same), and the path (the signal). The
comparison target is whatever the NEW section does with what `Root`
holds. `discover()` itself is `Root` plus `all_levels()` plus writing the
record. So the root of every script and the root of the program are the
same call.

A script that reads a record instead of a file starts with *the record,
as discovery.py wrote it* (a `json.load` of the `.record.json`). A script
whose new thing produces a new file has *the ..., as discovery.py reads
it* after the NEW section, and that line is a call to `discover`. The
output each script prints is committed next to the script.

None of the three extensions above took longer to write than to read.
That's the practical result when the givens are enough.
