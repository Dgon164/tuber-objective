# How to read a record

The program reads a file at more than one level. At the first level it
works on the file's smallest units. Then it treats each piece it cut out
as a single unit and reads the sequence again one level up, and keeps
going until there is nothing left to cut. Each of those passes is a
level.

A record starts with two summaries, FRAME and LEVELS, and then repeats
the same set of tables for each level. The text record shows the top of
each table; the JSON record has the whole table. Read the tables in
order, because each one builds on the one before it.

## FRAME

```
FRAME   score = spread between the column most often 1 and the column least often 1
  width  score   least-1 column   most-1 column
    8    0.950   col   0 at 0.000   col   2 at 0.950
  picked width 8
    fold to  4: columns differ by 0.1800 on average (wobble by chance 0.0020) -> different
  chosen width 8
  column rates at width 8:
    0.000 0.745 0.950 0.235 0.338 0.477 0.333 0.452
```

This section shows how the program found the width of one unit of the
file, in bits. It lays the bits out in rows of a trial width and looks
at each column; at the right width, each column is a one at its own
steady rate.

- **Score**: for each width, the gap between the column that is a one
  most often and the column that is a one least often. The width with
  the largest gap gets the highest score. If one width stands far above
  the rest, with its multiples a little below it, the signal has a
  clear structure. If every width scores about the same, the signal has
  no fixed structure: random bytes, or data that has been compressed or
  encrypted.
- **Picked, fold, chosen**: "picked" is the width with the best gap.
  "fold" is the check that the picked width isn't just a smaller width
  repeated. "chosen" is the final width.
- **Column rates**: how often each column is a one at the chosen width.
  These rates are the first thing Discovery learns about a signal. A
  column at 0.000 or 1.000 is a bit that never changes. A column near
  0.5 varies the most. The shape of the rates identifies the signal:
  ASCII text has column 0 at zero and a high column 2. A little-endian
  binary has rates that fall across each word. A packed 15-bit machine
  has 15 columns, with the top columns lowest.

## LEVELS

```
LEVELS   each level runs on the runs of the one before; nothing replaced, every structure added to one pool
  level  symbols  distinct     runs  distinct   minted  classes(2+)    added  pool total
      0   144395        73    24167      6466    15980          390    22446       22446
      1    24167      6466     1341      1328     5408          133     6709       29155
      2     1341      1328        5         5        0            0        5       29160
      3        5         5        1         1        0            0        1       29161
  stopped: level 3 left a single run; nothing more to cut
```

Each level does the same four things. It counts the symbols (at level
0, the words). It cuts the sequence at the most common symbol, which is
the separator, so that each piece between two separators is a run. It
compares the runs in pairs and pulls out every shared start and end as
a new part; those new parts are the minted ones. And it groups the
parts that accept the same additions into classes. Everything a level
makes goes into one list, the pool, that all levels share.

The table has one row per level. Level 0 is the signal itself, and its
symbols are the words. The symbols of level 1 are the runs of level 0,
so the runs of level 1 are runs of runs. The classes of level 0 give
level 1 a second way for two symbols to count as the same.

The *added* column is how many new structures the level put into the
pool. There is only one pool, and *pool total* is its running size at
that level. Watch the *added* column shrink to nothing: 22,446, then
6,709, then 5, then 1.

## MEMORY

This section appears when you run the program with `--memory FILE`. A
memory is the pool saved after one signal and loaded before the next,
so the new signal is compared against what the program already found.

```
MEMORY   alice.memory
  before this signal: 16272 parts, from alice-first-half.txt (72215 bytes, frame 8)
  this signal, against memory:
  level  produced  confirmed      added  not seen this time
      0     19925      10588       9337                3491
      1      6711       1420       4510                 769
      2         4          0          4                   3
      3         1          0          1                   1
  after: 30124 parts, saved
```

The section shows what the memory held before this signal and where
that came from. Then, for each level, it gives four counts:

- the parts this signal made (produced)
- the parts that were already in memory (confirmed)
- the parts that are new (added)
- the parts in memory that this signal didn't make (not seen this time)

The parts not seen this time stay in memory; the program doesn't remove
them. A comparison only counts when this signal is one side of it, so a
memory never confirms its own parts. If you run the same signal twice,
the second run confirms what the first run made. A few parts can
differ, because the program compares each part with its neighbor in
the sorted pool, and that neighbor has moved. The second run adds
nothing, or almost nothing.

The record writes the tables below for each level under a `LEVEL n`
heading. At level 0 the first two tables are WORDS and FOLLOWS. At
higher levels they are SYMBOLS and FOLLOWS. The record shows a symbol
as the run it stands for. When a class sits in a position inside a
minted part, the record shows it as `{n.k}`, which means class k of
level n.

You can find that class in the CLASSES table of level n. The text
record shows only the first 72 characters of a long run at a higher
level; the JSON record has the whole run. A density, the number of
things that contain a part, counts across all levels, so a level-0 word
that sits inside level-1 runs counts those level-1 runs.

## WORDS

This table lists each different word and how many times it occurs. One
line is one word and its count. Compare the number of different words
with the total for a quick read of the signal. A count of 73 in 144,395
is an alphabet. A count of 9,328 in 36,864 is machine code. A count of
1,904 in 20,000 is a neural net that uses only a small part of its
possible states.

## FOLLOWS

This table lists pairs of words that occurred one right after the
other, with a count for each pair. In text, the pairs are letter pairs
(`th`, `he`, `in`). In machine code, they are instruction pairs. Some
words are always followed by one of a small set of words; the byte that
UTF-8 puts first in an accented character, and EXTEND, the Apollo
computer's instruction prefix, are examples. A word like that shows up
here with the same group of partners every time.

## SEPARATOR

This line names the most common word, which is where the program cuts
the sequence into runs. With `--separators N`, the N most common words
are all cut points.

## RUNS and RUN FOLLOWS

These tables show what lies between the separators, with counts, and
which run follows which. In text, the runs are the words of the
language, and the common two-word sequences. In a binary read at the
byte level, the runs are the strings, the function names, and the code
between zero bytes.

## TIME

This table reads the sequence as time: what came before and what came
after. The program looks at a stretch after each run, and the length of
that stretch is the usual distance to the next level's separator. On
Alice at level 0 the stretch is roughly a clause, so the unit of
measure comes from the signal itself.

- **ARROWS**: pairs that occur in both orders, with a count for each
  order. The table shows `said -> Alice` with its count, then the count
  for the other way round. The order with the higher count is an arrow.
  Plain text has few pairs that go both ways; a machine trace has many.
- **EFFECTS**: what occurs in the stretch after a run more often than
  it occurs in the signal as a whole, written as `seen/expected`. The
  row for `I` in the Alice record is an example. Something counts as an
  effect when it occurs two or more times, and at two or more times its
  usual rate. That is the same rule the classes use: two occurrences
  make a pattern. The list is in order of the difference, seen minus
  expected.
- **CHAINS**: the program follows the strongest effect forward from the
  most common runs, giving `a -> b -> c`.

None of these tables shows a cause. They are the before and after of a
signal that was only watched. A cause is an arrow that is still there
when you do something. The example in `examples/agc-live/` presses a
key, then compares the signal with the key press against the signal
without it. The tables are the same ones, read across the two signals.

## MINT

This table shows how many rounds the comparison loop ran, and how many
parts each round made. The counts always fall to 0; that is the stop
rule. With a memory, a second line counts the parts from memory that
this signal made again, round by round. On a signal the program has
already read once, nothing new is made, so the second line carries all
the work and falls to 0 in the same way.

A line that says `stopped: pool passed the cap` means the size limit
stopped the loop early. The parts tables are then not complete.

## PARTS BY DENSITY

This table lists each part in order of how many other parts contain it,
which is its density. *whole* is how many times the part occurred as a
complete run. A part with a high density and a whole count of 0 is
never a word on its own: a letter, a punctuation mark, a stem, a
machine instruction. A part with a high whole count and a low density
is a word that stands alone and builds nothing else.

## ENDINGS and BEGINNINGS

These tables list the changes that turn one part into another, with
counts. `+ed 427` means the comparison loop found 427 pairs in which one
part was the other part plus `ed` on the end. This is the signal's own
account of its suffixes and prefixes, and the list includes
punctuation.

## CLASSES

This table groups parts by the exact set of changes they accept.
`[+ed, +ing]` with 22 members is a class of stems. The label is the set
of changes; the record gives a class no name. Classes with many members
are the true structure of the signal. Classes with two or three members
are usually two things that happened to land next to each other in the
sorted pool.

## CRYSTAL

This table has one entry for each common run. The entry collects
everything the tables above found about that run: *made of*, *part
of*, *changes*, *followed*, *preceded*. It is the dictionary entry the
signal writes for that run, and each value in it comes from a count in
an earlier table.

## What to trust and what not to trust

Every number in a record is a count of something that occurred in the
signal, or a ratio of two such counts. The record doesn't predict,
estimate, or guess. A table can show something that looks wrong, such
as a stem divided at an odd place, or `for` in a group with `format`.
That comes from the structure of the signal itself, from which parts
ended up next to each other. If you want a correction, it lives in the
input: more signal, or a different separator.

The lens option only changes how the record prints each word. Two
records of the same file made with different lenses have the same
tables.
