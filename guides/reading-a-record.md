# Reading a record

A record starts with the FRAME and a LEVELS summary, then has the same
set of tables for each level. The text record shows the top of each
table; the JSON has all of it. Read them in order — each one is built
from the one before.

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

- **Score**: the width whose columns have the most varied patterns
  scores highest. One width standing far above the rest, with its
  multiples close behind, means a clearly structured signal. All widths
  scoring about the same means a signal with no fixed structure (random
  bytes, compressed or encrypted data).
- **Picked, fold, chosen**: "picked" is the best gap. "fold" checks
  whether that width is really a smaller width repeated. "chosen" is
  the final answer.
- **Column rates**: this is the first thing Discovery learned about the
  signal. A column at 0.000 or 1.000 is a bit that never changes. A
  column near 0.5 carries the most variety. The shape of the rates is
  like a fingerprint of the signal: ASCII text has a zero column 0 and
  a high column 2; a little-endian binary has rates that drop off across
  each word; a packed 15-bit machine has 15 columns with the top ones
  lowest.

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

One row per level. Level 0 is the signal; its symbols are words.
Level 1's symbols are level 0's runs; its runs are runs of runs; and
level 0's classes count as a second way two symbols can be "the same."
The *added* column is how many new structures that level put into the
shared pool. The *pool total* is the running count. Read the *added*
column to see the growth run out: 22,446, then 6,709, then 5, then 1.

## MEMORY

Shows up when the run used `--memory FILE`.

```
MEMORY   alice.memory
  before this signal: 16272 parts, from alice-first-half.txt (72215 bytes, frame 8)
  this signal, against memory:
  level  produced  confirmed      added  not seen this time
      0     21278      11941       9337                2138
      1      6967       1664       4510                 525
  after: 30124 parts, saved
```

What the memory held before this signal and where it came from. Then,
for each level: how many parts this signal produced, how many were
already in memory (confirmed), how many were new (added), and how many
remembered parts this signal didn't produce (not seen this time — they
stay in memory). If you run the same signal twice, the second time
confirms everything and adds nothing (or next to nothing).

The tables below are written for each level under a `LEVEL n` heading.
At level 0 the first two are WORDS and FOLLOWS; at higher levels
they're SYMBOLS and FOLLOWS, where a symbol is drawn as the run it
represents. A class standing in a spot of a minted part is drawn as
`{n.k}` — class k of level n; look it up in that level's CLASSES
table. Long higher-level runs get cut off at 72 characters in the text;
the JSON has them whole. Densities count containment across all levels:
a level-0 word that sits inside level-1 stretches counts them.

## WORDS

The distinct words and how often each one appeared. Compare the number
of distinct words to the total number of words for a quick read on the
signal: 73 out of 144,395 is an alphabet; 9,328 out of 36,864 is
machine code; 1,904 out of 20,000 is a net that uses a small part of
its possible states.

## FOLLOWS

Pairs of words that showed up in sequence. In text these are letter
pairs (`th`, `he`, `in`). In machine code they're instruction pairs. A
word that's always followed by one of a small set (the UTF-8 lead byte,
the EXTEND prefix) shows up as a word with a steady group of partners.

## SEPARATOR

The most common word. Runs get cut here. With `--separators N`, the N
most common words all act as cut points.

## RUNS and RUN FOLLOWS

What sits between separators, counted, and which run follows which. In
text: the words of the language and the common two-word sequences. In a
binary at the byte level: the strings, function names, and the code
between zero bytes.

## TIME

The sequence read as time: before and after. The *stretch* after a run
is the typical distance to the next level's separator (18 words on
Alice at level 0: about a clause), so the unit is the signal's own.

- **ARROWS** — pairs seen in both orders, counted each way. `said ->
  Alice 25, the other way 7`: the order that wins is an arrow. A plain
  text has few pairs that go both ways; a machine trace has many.
- **EFFECTS** — what comes in the stretch after a run more often than it
  comes overall, as `seen/expected`: `I  think 23/5.9, know 24/7.0`.
  An effect is seen at least twice and at least twice its usual rate
  (two make a pattern, as with the classes). The list is ordered by the
  difference, seen minus expected.
- **CHAINS** — the strongest effect, followed forward from the most
  common runs: `a -> b -> c`.

None of this is a cause: it is the before and the after of a signal
that was only watched. A cause is an arrow that holds across a *do* —
`examples/agc-live/` presses a key and compares the run with the press
against the run without it. The same tables, read across the two.

## MINT

How many rounds the loop ran and how many parts each round made. The
counts always fall to 0 — that's the stopping rule. A line saying
`stopped: pool passed the cap` means the loop got cut off by the size
limit and the parts tables are incomplete.

## PARTS BY DENSITY

Every part, ranked by how many other parts it sits inside. *whole* is
how many times it appeared as a complete run on its own. A part with
high density and zero whole count is a piece that's never a word on
its own — a letter, a punctuation mark, a stem, a machine instruction.
A part with a high whole count and low density is a word that stands
alone and doesn't build other things.

## ENDINGS and BEGINNINGS

The leftovers that turn one part into another, counted. `+ed 427` means
the mint found 427 pairs where one part was another plus `ed` on the
end. This list is the signal's own account of its suffixes and
prefixes, including punctuation.

## CLASSES

Parts grouped by the exact set of changes they take. `[+ed, +ing]`
with 22 members is a class of stems. The label is the set of changes;
the record doesn't give the class a name. Classes with many members are
the real structure of the signal. Classes with two or three members are
usually just two things that happened to sit next to each other in the
sorted pool.

## CRYSTAL

One entry per common run, pulling together everything from the tables
above for that one thing: *made of*, *part of*, *changes*, *followed*,
*preceded*. This is the dictionary entry the signal provides for that
run. Everything in it traces back to a count in an earlier table.

## What to trust and what not to

Every number in a record is a count of something that actually happened
in the signal, or a ratio of two such counts. The record doesn't
predict, estimate, or guess. When a table shows something that looks
wrong — a stem cut in an odd place, `for` grouped with `format` — that
comes from the signal's own neighbour structure. The fix, if you want
one, is in the input: more signal, or a different separator.

The lens changes how a word is displayed and nothing else. Two records
of the same file with different lenses have the same tables.
