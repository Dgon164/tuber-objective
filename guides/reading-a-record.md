# How to read a record

A record starts with the FRAME and a LEVELS summary. Then the record
repeats the same set of tables for each level. The text record shows
the top of each table. The JSON record has the full table. Read the
tables in order. Each table uses the table before.

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

- **Score**: the width with the largest difference between its columns
  gets the highest score. If 1 width is far above the rest, with the
  multiples of that width a small amount below, the signal has a clear
  structure. If all widths have approximately the same score, the
  signal has no fixed structure (random bytes, or data after
  compression or encryption).
- **Picked, fold, chosen**: "picked" is the width with the best gap.
  "fold" checks if that width is a smaller width repeated. "chosen" is
  the final width.
- **Column rates**: the column rates are the first thing that Discovery
  learned about the signal. A column at 0.000 or 1.000 is a bit that
  never changes. A column near 0.5 has the most variation. The shape of
  the rates identifies the signal. ASCII text has a column 0 at zero
  and a high column 2. A little-endian binary has rates that decrease
  across each word. A packed 15-bit machine has 15 columns, with the
  top columns lowest.

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

The table has 1 row for each level. Level 0 is the signal. The symbols
of level 0 are words. The symbols of level 1 are the runs of level 0.
The runs of level 1 are runs of runs. The classes of level 0 are a
second way for 2 symbols to be the same.

The *added* column shows the number of new structures that the level
put into the pool. There is only 1 pool. The *pool total* is the total
count at that level. Look at the *added* column to see the growth
decrease to nothing: 22,446, then 6,709, then 5, then 1.

## MEMORY

This section appears when you run the program with `--memory FILE`.

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

The section shows what the memory held before this signal, and the
source of the memory. Then, for each level, the section shows 4 counts:

- the parts that this signal made (produced)
- the parts that were already in memory (confirmed)
- the parts that are new (added)
- the parts in memory that this signal did not make (not seen this
  time)

The parts not seen this time stay in memory. The program does not
remove those parts. A comparison counts only when this signal is part
of the comparison. Thus a memory never counts its own parts as
confirmed. If you run the same signal 2 times, the second run counts as
confirmed what the first run made. A few parts can differ, because the
part next to them in the pool has moved. The second run adds nothing,
or almost nothing.

The record writes the tables below for each level under a `LEVEL n`
heading. At level 0, the first 2 tables are WORDS and FOLLOWS. At
higher levels, the first 2 tables are SYMBOLS and FOLLOWS. The record
shows a symbol as the run that the symbol stands for. The record shows
a class in a position of a part that the program minted as `{n.k}`.
`{n.k}` is class k of level n.

You can find the class in the CLASSES table of level n. The text record
shows only the first 72 characters of a long run of a higher level. The
JSON record has the whole run. A density (the number of things that
contain a part) counts across all levels. A level-0 word that is in
level-1 runs counts those level-1 runs.

## WORDS

The table shows the different words and the count of each word. Compare
the number of different words with the total for a quick view of the
signal. A count of 73 in 144,395 is an alphabet. A count of 9,328 in
36,864 is machine code. A count of 1,904 in 20,000 is a neural net that
uses only a small part of its possible states.

## FOLLOWS

The table shows pairs of words that occurred one after the other. In
text, the pairs are letter pairs (`th`, `he`, `in`). In machine code,
the pairs are instruction pairs. Some words always have 1 of a small
set of words after them. Examples are the UTF-8 lead byte and the
EXTEND prefix. Such a word appears with a constant group of partners.

## SEPARATOR

The separator is the most common word. The program cuts the runs at the
separator. With `--separators N`, the N most common words are all cut
points.

## RUNS and RUN FOLLOWS

The tables show what is between the separators, with counts, and the
run that follows each run. In text, the runs are the words of the
language and the common 2-word sequences. In a binary at the byte
level, the runs are the strings, the function names, and the code
between zero bytes.

## TIME

The table reads the sequence as time: what came before and what came
after. The stretch after a run is the usual distance to the separator
of the next level. On Alice at level 0, the stretch is approximately a
clause. Thus the unit comes from the signal itself.

- **ARROWS**: pairs that occur in both orders, with a count for each
  order. The table shows `said -> Alice` with its count, then the count
  for the other order. The order with the higher count is an arrow.
  Plain text has few pairs that go in both orders. A machine trace has
  many.
- **EFFECTS**: what occurs in the stretch after a run more often than
  the same thing occurs in the whole signal, as `seen/expected`. An
  example is the row for `I` in the Alice record. An effect occurs 2 or
  more times, and at 2 or more times its usual rate. The rule is the
  same as for the classes: 2 occurrences make a pattern. The list is in
  order of the difference, seen minus expected.
- **CHAINS**: the program follows the strongest effect forward from the
  most common runs: `a -> b -> c`.

None of these tables shows a cause. The tables are the before and after
of a signal that was only watched. A cause is an arrow that remains
when you do something. The example `examples/agc-live/` presses a key.
The example compares the signal with the key press against the signal
without the key press. The tables are the same, read across the 2
signals.

## MINT

The table shows the number of rounds of the loop and the number of
parts that each round made. The counts always decrease to 0. That is
the stop rule. With a memory, a second line counts the parts from
memory that this signal made again, round by round. On a signal that
the program read 2 times, the program mints nothing. The second line
then carries the work, and decreases to 0 in the same way.

A line that says `stopped: pool passed the cap` means that the size
limit stopped the loop. The parts tables are then not complete.

## PARTS BY DENSITY

The table shows each part, in order of the number of other parts that
contain the part. *whole* is the number of times that the part occurred
as a complete run. A part with a high density and a whole count of 0 is
never a word by itself. Examples are a letter, a punctuation mark, a
stem, and a machine instruction. A part with a high whole count and a
low density is a word that stands alone and makes no other things.

## ENDINGS and BEGINNINGS

The tables show the changes that make one part into a different part,
with counts. `+ed 427` means that the mint step found 427 pairs. In
each pair, 1 part was the other part plus `ed` at the end. This list is
the account of the suffixes and the prefixes that the signal itself
gives. The list includes punctuation.

## CLASSES

The table shows the parts in groups by the exact set of changes that
the parts accept. `[+ed, +ing]` with 22 members is a class of stems.
The label is the set of changes. The record does not give the class a
name. Classes with many members are the true structure of the signal.
Classes with 2 or 3 members are usually 2 things that were next to each
other in the pool after the sort, by chance.

## CRYSTAL

The table has 1 entry for each common run. The entry collects all data
from the tables above for that run: *made of*, *part of*, *changes*,
*followed*, *preceded*. The entry is the dictionary entry that the
signal writes for that run. Each value in the entry comes from a count
in an earlier table.

## What to trust and what not to trust

Each number in a record is a count of something that occurred in the
signal, or a ratio of 2 such counts. The record does not predict,
estimate, or guess. A table can show something that looks wrong, for
example a stem divided at an unusual position, or `for` in a group with
`format`. Such a result comes from the structure of the signal itself,
from the parts that are next to each other. If you want a correction,
the correction is in the input: more signal, or a different separator.

The lens changes only how the record shows a word. Records of the same
file with 2 different lenses have the same tables.
