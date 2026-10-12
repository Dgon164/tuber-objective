# How Discovery works

Discovery does one thing: it compares. Take two things and split them
into three buckets:

| bucket | what goes in it |
|---|---|
| same | whatever the two things have in common |
| different | what's left of each once you pull out the shared stuff |
| not part | everything the comparison never touched |

The whole program is just that comparison, run first on the input, then
on its own results, over and over until a pass produces nothing new.
Nothing gets thrown away. The file has ten numbered sections, and this
guide walks through them in order. The examples come from
`examples/text/alice.txt` and `examples/german/ep-00-01-17.de` unless
another one is mentioned.

## 1. Signal

The file gets read as raw bytes and turned into a long string of ones
and zeroes. That's it. Discovery doesn't look at the file name, the
extension, or any header bytes. A text file, a program, a picture, and
a sound file all come in exactly the same way.

```python
bits = bin(int.from_bytes(data, 'big'))[2:].zfill(len(data) * 8)
```

## 2. Frame -- figuring out how wide one "word" is

Lay the bits out in rows of some width, like a grid. Each column is
every w-th bit in the file.

If you pick the right width, each column has its own personality. For
ASCII text at width 8: column 0 is a 1 zero percent of the time (the
top bit is never on). Column 2 is a 1 about 95% of the time (letters
live in the range 0x60--0x7f). Pick the wrong width -- say 7 -- and the
bits get jumbled across columns, so every column drifts toward about
50%.

The score for a given width is the gap between the column that's a 1
most often and the column that's a 1 least often. The width with the
biggest gap wins. One catch: a wider width only wins if it beats the
narrower one by more than you'd expect from random noise at that number
of rows.

```python
score[w] = max(cols) - min(cols)
chance   = 1 / rows ** 0.5
if score[w] > score[picked] + chance: picked = w
```

Then the winning width gets "folded." A multiple of the real word size
has the real word size's columns laid side by side -- width 16 on 8-bit
text is really just the same 8 columns twice -- and its gap can come out
slightly higher by luck. So for each number that divides evenly into the
winning width, the program checks whether the bigger width's column
pattern is just the smaller one repeated. If the difference is less than
what random wobble would explain (half over the square root of the row
count), the smaller width is the real answer.

```python
wobble = 0.5 / rows ** 0.5
fold[w] = mean(|profile[picked][c] - profile[w][c % w]| for c in range(picked))
if fold[w] <= wobble: frame = w
```

The Apollo guidance computer rope in `examples/agc` is the case that
needed this: the gap picked 60, but 60 is just 15 repeated four times.
The fold step caught it, within 0.004.

The record prints the eight best widths, which one was picked, each fold
test, the final choice, and every column's rate at that width. Those
column rates are the first thing Discovery learned about the signal.

`--frame N` lets you force the width. It's there so you can look at a
signal at a different size than the one the frame step chose. The
compiled program in `examples/code` is read at 64 bits by the frame
step, then again at 8 bits by hand -- the two records show different
things.

## 3. Words

Chop the bit string into chunks that are as wide as the frame. Count
each distinct chunk. Count each pair of chunks that show up next to each
other.

```python
words        = [int(bits[i:i+w], 2) for i in range(0, len(bits)-w+1, w)]
word_counts  = Counter(words)
word_follows = Counter(zip(words, words[1:]))
```

In Alice: 73 distinct words out of 144,395. The most common is
`00100000` -- the space. In the German file: 88 distinct, and
`11000011` (the UTF-8 lead byte for characters like a-umlaut, o-umlaut,
u-umlaut, and sharp-s) shows up 2,827 times.

## 4. Runs

The most common word becomes the separator. A "run" is whatever sits
between two separators. In text the separator is the space, so the runs
are the words of the language. In a compiled program the separator is
the zero byte, so the runs are everything between zero bytes: machine
code, function names, strings.

`--separators 2` uses the two most common words as separators.
`--separators 20,0a` lets you pick them yourself in hex (space and
newline). The record tells you when you want this: a word with a high
density in the parts table but that never appears as a complete run on
its own is acting like a separator that didn't get picked. In Alice,
that's the newline -- it's only the 14th most common word.

Runs get counted, and pairs of runs that follow each other get counted
too.

## 5. Mint -- smash things together until nothing new comes out

The pool starts with every distinct run.

Sort the pool. Two neighbors in sorted order share the longest beginning
that either of them shares with anything else in the pool. Compare each
pair:

- Count how many words they share from the start.
- If zero, skip them.
- Otherwise, make three new parts: the shared beginning, and what's left
  of each of the two. Every new part goes into the pool. The whole gets
  recorded as "made of" its pieces; each piece gets recorded as "part
  of" the whole.

```
   abcd   vs  abef   ->  shared ab    leftovers cd, ef
   walk   vs  walked ->  shared walk  leftover ed   (walk is already whole, so only ed is new)
```

Then flip every part backwards and do the same thing -- this catches
shared endings: `looked` and `walked` share `ed`.

Two parts that were both in the pool last round were already neighbors
last round (nothing ever gets removed), so a pair only gets compared
when one of them is new. When a full round produces nothing new, the
loop stops. That's the only stopping rule. (`--cap` is a size limit, not
a rule -- if the pool gets too big it stops early, and the record says
so.)

```
Alice:   14 rounds   10038 3800 1303 484 176 88 37 22 15 10 4 1 2 0
German:  10 rounds    9291 3641 1205 402 130 42 7 2 1 0
```

Each new part also records the leftover that produced it: a leftover
after a shared beginning is an "ending" (`+ed`, `+ing`, `+en`, `+ung`).
A leftover before a shared tail is a "beginning" (`be+`, `ge+`, `un+`).

Every part keeps two numbers: how many times it appeared as a complete
run, and its "density" -- how many other parts it sits inside. The
letter `e` is never a complete run in Alice, but it sits inside 1,615
other parts.

## 6. Crystal -- grouping what was found

The pool stays exactly as it is. The crystal is a second table that
reads the pool and groups parts together without losing any detail --
basically deduplication.

For any part, a "change" is the leftover that turns it into one of the
parts that contain it. `walk` to `walked` is the change `+ed`. `walk`
to `walking` is `+ing`.

A "class" is all the parts that take the exact same set of changes.
Every stem that takes exactly `{+ed, +ing}` lands in one class. In
Alice that class has 22 members: swallow, remain, consider, crawl,
mutter, nibbl, peep, pull, rais, and more. In the German file, `{+en,
+t}` has 52 members and `{+n, +r}` has 42.

The crystal also writes one dictionary-style entry per common run: what
it's made of, what contains it, its changes, what follows it, and what
comes before it. The entry for `walk` is basically: the stem, its forms,
and the company it keeps.

## 7. Levels -- crystallize, then loop again, until nothing changes

Sections 3 through 6 make up one level: count the words, cut runs at
the most common one, mint, crystallize. Then the loop runs again on what
the level just produced, and nothing gets replaced -- everything gets
added.

1. The next level's sequence of symbols is this level's runs, as they
   are.
2. This level's classes (the ones with two or more members) become a
   second way two symbols can count as "the same": either the exact same
   run, or two runs that belong to the same class. When two sequences
   match only because a class member sits in the same spot, the class
   itself stands in that spot of the shared part. (This is the one place
   where the crystal's output feeds back into the comparison.)
3. Every new structure -- a run of runs, a minted part, a class -- joins
   the one shared pool, and its connections land on the parts it's made
   of wherever they live. A level-0 word that sits inside forty level-1
   stretches gains forty to its density.
4. Keep going until a level has only a single run left, which can't be
   cut.

Every level's sequence is shorter than the one before (the separator is
always present and gets cut out), so the loop ends on its own, and the
additions shrink to nothing before it does:

```
  level  symbols  distinct     runs  distinct   minted  classes(2+)    added  pool total
      0   144395        73    24167      6466    15980          390    22446       22446
      1    24167      6466     1341      1328     5408          133     6709       29155
      2     1341      1328        5         5        0            0        5       29160
      3        5         5        1         1        0            0        1       29161
```

22,446 parts, then 6,709 more, then 5, then 1, then stable. The pool
only grows; the growth runs out.

What level 1 looks like for Alice: the separator is `the`. A run is the
stretch between two `the`s. The endings are what sits right before `the`
(`+said` 357, `+and` 181, `+to` 151, `+of` 122). The beginnings are
what sits right after it (`and+`, `was+`, `to+`, `Mock Turtle+`). For
the German text the separator is the comma; the most repeated stretches
are the forms of address (`Herr Kommissar`, `meine Damen und Herren`,
`Frau Prasidentin`). For the Apollo assembly source the separator is
`#`, the comment mark; the densest level-1 parts are instruction
sequences like `TC BANKCALL`, `CAF ZERO`, `CCS A`; and the beginnings
are how the programmers started a comment: `TO+`, `FOR+`, `IN+`, `IF+`,
`AND+`, `SET+`.

```python
L = run_level(seq, 1, pool, made_of, part_of, cap, class_of, level)
seq, class_of = L['runs'], L['next_class_of']
```

### Memory -- checking your work against what you already know

"Does the model match reality?" and "Is this the same as that?" are
really the same question, just asked about different things. The
comparison answers both. What turns the second question into a loop is
memory: the pool saved after one run and loaded before the next.

With `--memory FILE`:

1. The pool is loaded from FILE (an empty file means empty memory).
2. The new signal gets read as usual, but the remembered parts sit in
   the sorted pool right next to the new runs. So a new run gets
   compared against what's remembered as well as against the rest of the
   signal. A comparison only counts when this signal is part of it: two
   remembered parts the signal hasn't reached get left alone (they were
   compared when they were minted), so a memory never confirms itself. A
   remembered part the signal produces again is confirmed, and then gets
   compared with its own neighbors once more, so what was minted from it
   last time can be reached too.
3. Everything the run produces gets sorted into three bins against
   memory: **confirmed** (already remembered, and this signal produced
   it again), **added** (new), and **not seen this time** (remembered
   but this signal didn't produce it -- it stays in memory, it's not
   removed; it just gets a count on the entry).
4. The pool gets saved back to FILE, with a line in its history for this
   signal. The file is JSON. One memory holds signals read at one frame
   -- the same number means a different word at a different width -- and
   a signal at another width is refused with the reason.

The test in `examples/memory/`: first half of Alice from nothing, second
half against that memory, second half again, German text against the
English memory.

```
                              produced  confirmed  added  not seen
first half, from nothing         14079          0  14079         0
second half, against it          19925      10588   9337      3491
second half again                19833      19833      0      3583
German, against the English      32784      14797  17987      8619
```

The second pass over the same text adds nothing at level 0 and five
parts at level 1 (the memory changed which parts sit next to each other
in the sorted pool, so five new collisions happened; a third pass would
find even fewer), and reaches 19,833 of the 19,925 parts the first pass
produced; the rest are heads that a part minted on the first pass now
stands in front of. That's the loop running out of new things. The
German text against the English memory confirms 14,797 parts -- the
short parts the two alphabets share -- and adds 17,987 that English
never produced.

```python
pool, made_of, part_of, history = load_memory(path)
levels, pool, made_of, part_of = run_levels(words, sep, cap, pool, made_of, part_of)
save_memory(path, pool, made_of, part_of, history + [(name, size, frame)])
```

### Time -- reading the sequence as "before and after"

The signal is in order, and that order is time. FOLLOWS was always one
way of reading it; `time_tables()` reads it three more ways at every
level, each one pointing the comparison along the sequence:

- **arrows** -- a pair of runs seen in both orders, counted each way.
  The order that shows up more is an arrow (`said -> Alice` in
  `examples/text/alice.txt.record.txt`, level 0).
- **effects** -- what shows up in the stretch after a run at least twice
  its usual rate, compared to what you'd expect (the row for `I` in the
  same table). The stretch is the typical distance to the next level's
  separator -- roughly a clause at level 0 on Alice -- so the unit comes
  from the signal itself, and "at least twice" is the same bar the
  classes use: two make a pattern.
- **chains** -- the strongest effect followed forward from the most
  common runs (the CHAINS lines of the same table; in
  `examples/agc/luminary099.rope.record.txt` the instruction flow loops
  back on itself).

This is the "before" and "after" of a signal that was only watched. A
cause is an arrow that holds up when you actually *do* something:
`examples/agc-live/` presses a key, records every signal, and compares
the run with the key press against the run without it. Same tables, read
across the two.

## 8. Lens

The lens only controls how a word gets displayed on the page. `raw`
shows hex. `ascii` shows the character when the word is 8 bits wide.
`utf8` decodes a whole run as UTF-8 so `a-umlaut` shows up as the actual
character instead of `\xc3\xa4`. `octal` shows a word in base 8, which
is how the Apollo listing is printed. The lens is never used by the
algorithm. Change the lens and every table has the same contents with
different labels.

## 9. Record

Everything above gets written two ways: a text record people can read
and a JSON record programs can read. The text record has the FRAME, a
LEVELS summary table, and then every table for every level. The JSON has
every word, pair, run, part, change, and class for every level -- not
just the top of each table. `levels[0]` is the signal itself;
`levels[1]` is the first level up. Densities and part_of lists come from
the shared pool, so a level-0 part lists the level-1 parts it sits
inside.

## 10. Run

`Root` is the one call a program built on Discovery makes: the signal as
read (sections 1 to 3), level 0 on a shared pool (4 to 7), and a call
for each further level. `discover()` is `Root` plus the levels run to
the end and the record written (8 and 9), and it returns the paths to
the two record files. `main()` handles the command line.

## What's not in the file

There's no list of file types, no character table, no dictionary, no
grammar, no training, and no threshold that someone hand-picked to fit
one example. The one tolerance (the `chance` term in the frame step) is
the random wobble for the number of rows at that width, computed from
the signal itself.
