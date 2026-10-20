# How Discovery operates

Discovery does 1 operation. The operation is a comparison. The
comparison takes 2 things and puts the contents of the 2 things into 3
groups:

| group | contents |
|---|---|
| same | what the 2 things have in common |
| different | what remains of each thing after the program removes what is the same |
| not part | what the comparison did not touch |

The whole program is that comparison. The program does the comparison
first on the input. Then the program does the comparison on the results
of the comparison. The program repeats the comparison until a pass makes
nothing new. The program removes nothing.

The file `discovery.py` has 10 numbered sections. This guide explains
the 10 sections in order. The examples come from
`examples/text/alice.txt` and `examples/german/ep-00-01-17.de`, unless
the text names a different file.

## 1. Signal

The program reads the file as raw bytes. The program makes the bytes
into a long string of ones and zeros. The program does nothing more in
this step. Discovery does not look at the file name, the extension, or
the header bytes. A text file, a program, a picture, and a sound file
all enter in the same way.

```python
bits = bin(int.from_bytes(data, 'big'))[2:].zfill(len(data) * 8)
```

## 2. Frame: the width of 1 word

The program puts the bits in rows of a width w. The rows make a grid.
Each column holds every w-th bit of the file.

At the correct width, each column has its own rate of ones. For ASCII
text at width 8, column 0 is a 1 in 0 percent of the rows (the top bit
is never 1). Column 2 is a 1 in approximately 95 percent of the rows
(the letters are in the range 0x60 to 0x7f). At a wrong width, for
example 7, the bits mix across the columns. Each column then goes
toward approximately 50 percent.

The score for a width is the gap between 2 columns. The 2 columns are
the column that is 1 most often and the column that is 1 least often.
The program selects the width with the largest gap.

There is 1 condition. The program compares the score of a wider width
with the score of the narrower width that the program selected before.
The program selects the wider width only if the difference is more than
the `chance` term. The `chance` term is the random noise for that
number of rows.

```python
score[w] = max(cols) - min(cols)
chance   = 1 / rows ** 0.5
if score[w] > score[picked] + chance: picked = w
```

Then the program folds the width that the program selected. To fold a
width is to check if the width is a smaller width repeated. If the
width is a smaller width repeated, the program goes down to the smaller
width. A multiple of the true word width has the columns of the true
width side by side. For example, width 16 on 8-bit text is the same 8
columns 2 times. The gap of the multiple can be a small amount higher
by chance.

Thus the program tests each smaller width that is a factor of the width
that the program selected. The test checks if the column pattern of the
larger width is the column pattern of the smaller width repeated. The
wobble is 0.5 divided by the square root of the number of rows. If the
difference between the 2 column patterns is less than the wobble, the
smaller width is the true width.

```python
wobble = 0.5 / rows ** 0.5
fold[w] = mean(|profile[picked][c] - profile[w][c % w]| for c in range(picked))
if fold[w] <= wobble: frame = w
```

The Apollo Guidance Computer rope in `examples/agc` is the case that
needed the fold step. By the gap, the program selected 60. But 60 is 15
repeated 4 times. The fold step found the true width. The difference
was not more than 0.004.

The record shows:

- the 8 best widths
- the width that the program selected
- each fold test
- the final width
- the rate of each column at the final width

The column rates are the first thing that Discovery learned about the
signal.

With `--frame N`, you set the width. You use `--frame N` to look at a
signal at a width that is different from the width that the frame step
selected. The frame step reads the compiled program in `examples/code`
at 64 bits. Then a second command, with `--frame 8`, reads the compiled
program at 8 bits. The 2 records show different things.

## 3. Words

The program cuts the bit string into words. To cut a sequence is to
divide the sequence into smaller sequences. Each word has the width of
the frame. The program counts each different word. The program counts
each pair of words that occur next to each other.

```python
words        = [int(bits[i:i+w], 2) for i in range(0, len(bits)-w+1, w)]
word_counts  = Counter(words)
word_follows = Counter(zip(words, words[1:]))
```

In Alice, there are 73 different words in 144,395 words. The most
common word is `00100000`, the space. In the German file, there are 88
different words. The word `11000011` occurs 2,827 times. This word is
the UTF-8 lead byte for characters such as a-umlaut, o-umlaut,
u-umlaut, and sharp-s.

## 4. Runs

The most common word becomes the separator. The program cuts the
sequence of words at each separator. A run is what is between 2
separators.

In text, the separator is the space. Thus the runs are the words of the
language. In a compiled program, the separator is the zero byte. Thus
the runs are all that is between the zero bytes: machine code, function
names, and strings.

The option `--separators 2` uses the 2 most common words as separators.
With `--separators 20,0a`, you select the separators yourself, in hex
(space and newline).

The record shows when you need this option. The sign is a word that has
a high density in the parts table but never occurs as a complete run.
Such a word operates as a separator that the program did not select. In
Alice, that word is the newline. The newline is only the 14th most
common word.

The program counts the runs. The program also counts each pair of runs
that occur one after the other.

## 5. Mint: new parts until nothing new comes

The mint step makes new parts. To mint a part is to make a new part
from 2 parts that have the same start or the same end. The pool starts
with each different run.

The program sorts the pool. After the sort, each part shares its
longest start with a part next to it. No other part in the pool shares
a longer start with that part. The program compares each pair of parts
that are next to each other:

- The program counts the words that the 2 parts share from the start.
- If the count is 0, the program skips the pair.
- If the count is not 0, the program makes 3 new parts: the start that
  the 2 parts share, and what remains of each of the 2 parts. Each new
  part goes into the pool. The program records the whole as "made of"
  its parts. The program records each part as "part of" the whole.

```
   abcd   vs  abef   ->  shared ab    leftovers cd, ef
   walk   vs  walked ->  shared walk  leftover ed   (walk is already whole, so only ed is new)
```

Then the program reverses each part and does the same comparison. This
comparison finds the ends that parts share. For example, `looked` and
`walked` share `ed`.

The program never removes a part. Thus 2 parts that were both in the
pool in the last round were already next to each other in the last
round. So the program compares a pair only when 1 of the 2 parts is
new. When a full round makes nothing new, the loop stops. This is the
only stop rule.

Note: `--cap` is a size limit, not a rule. If the pool becomes too
large, the loop stops early. The record then says so.

```
Alice:   14 rounds   10038 3800 1303 484 176 88 37 22 15 10 4 1 2 0
German:  10 rounds    9291 3641 1205 402 130 42 7 2 1 0
```

Each new part also records what remained when the program made the new
part. What remains after a start that 2 parts share is an ending
(`+ed`, `+ing`, `+en`, `+ung`). What remains before an end that 2 parts
share is a beginning (`be+`, `ge+`, `un+`).

Each part keeps 2 numbers. The first number is the count of times that
the part occurred as a complete run. The second number is the density
of the part. The density is the number of other parts that contain the
part. In Alice, the letter `e` is never a complete run. But 1,615 other
parts contain the letter `e`.

## 6. Crystal: groups of the parts

The pool does not change. The crystal is a second table. The crystal
reads the pool and puts the parts into groups, with no loss of detail.
The operation is the same as the removal of duplicates. To crystallize
a pool is to make the crystal from the pool.

For a part, a change is what makes the part into a larger part that
contains the part. The change from `walk` to `walked` is `+ed`. The
change from `walk` to `walking` is `+ing`.

A class is all the parts that accept the same set of changes. Each stem
that accepts exactly the set `{+ed, +ing}` is in 1 class.

In Alice, that class has 22 members. The members include swallow,
remain, consider, crawl, mutter, nibbl, peep, pull, and rais. In the
German file, the class `{+en, +t}` has 52 members. The class `{+n, +r}`
has 42 members.

The crystal also writes 1 entry for each common run, like a dictionary
entry. The entry shows:

- what the run is made of
- what contains the run
- the changes of the run
- what follows the run
- what comes before the run

The entry for `walk` is: the stem, the forms of the stem, and the runs
that occur next to the stem.

## 7. Levels: crystallize, then loop again, until nothing changes

Sections 3 to 6 are 1 level: count the words, cut the sequence into
runs at the most common word, mint, and crystallize. Then the loop runs
again on what the level made. The loop replaces nothing. The loop adds
everything.

1. The sequence of symbols of the next level is the runs of this level,
   with no change.
2. The classes of this level (the classes with 2 or more members)
   become a second way for 2 symbols to be the same. The symbols are
   the same if the symbols are the same run. The symbols are also the
   same if the symbols are 2 runs in the same class. Sometimes 2
   sequences are the same only because a class member is in the same
   position. Then the class itself is in that position of the part
   that the 2 sequences share. This is the 1 place where the output of
   the crystal goes back into the comparison.
3. Each new structure joins the pool. There is only 1 pool. A new
   structure can be a run of runs, a part that the program minted, or
   a class. The connections of the new structure go to the parts that
   the new structure is made of, at each level where those parts are.
   A level-0 word that is in 40 level-1 runs gets 40 more in its
   density.
4. The loop continues until a level has only 1 run. The program cannot
   cut 1 run.

The sequence of each level is shorter than the sequence of the level
before. The separator is always present, and the program cuts the
separator out. Thus the loop ends without help. The additions decrease
to nothing before the loop ends:

```
  level  symbols  distinct     runs  distinct   minted  classes(2+)    added  pool total
      0   144395        73    24167      6466    15980          390    22446       22446
      1    24167      6466     1341      1328     5408          133     6709       29155
      2     1341      1328        5         5        0            0        5       29160
      3        5         5        1         1        0            0        1       29161
```

The pool gets 22,446 parts, then 6,709 more, then 5, then 1, then no
more. The pool only grows. The growth stops.

At level 1 for Alice, the separator is `the`. A run is the sequence
between 2 occurrences of `the`. The endings are what is immediately
before `the` (`+said` 357, `+and` 181, `+to` 151, `+of` 122). The
beginnings are what is immediately after `the` (`and+`, `was+`, `to+`,
`Mock Turtle+`). For the German text, the separator is the comma. The
runs that repeat most are the forms of address (`Herr Kommissar`,
`meine Damen und Herren`, `Frau Prasidentin`).

For the Apollo assembly source, the separator is `#`, the comment mark.
The level-1 parts with the highest density are instruction sequences
such as `TC BANKCALL`, `CAF ZERO`, and `CCS A`. The beginnings are the
words that the programmers used to start a comment: `TO+`, `FOR+`,
`IN+`, `IF+`, `AND+`, `SET+`.

```python
L = run_level(seq, 1, pool, made_of, part_of, cap, class_of, level)
seq, class_of = L['runs'], L['next_class_of']
```

### Memory: compare the new signal with what the program already knows

The question "Does the model agree with reality?" and the question "Is
this the same as that?" are the same question about different things.
The comparison answers both questions. Memory makes the second question
into a loop. The memory is the pool that the program saves after 1
signal and loads before the next signal.

With the option `--memory FILE`, the program does 4 steps:

1. The program loads the pool from FILE. An empty file means an empty
   memory.
2. The program reads the new signal in the usual way. But the parts from
   memory are in the pool, after the sort, next to the new runs. Thus
   the program compares a new run with the parts from memory and also
   with the rest of the signal.

   A comparison counts only when this signal is part of the comparison.
   The program does not compare 2 parts from memory that the signal has
   not reached. The program compared those 2 parts when the program
   minted them. Thus a memory never counts its own parts as confirmed.
   A part from memory that the signal makes again counts as
   **confirmed**. The program then compares that part with the parts
   next to it 1 more time. Thus the signal can also reach what the
   program minted from that part last time.
3. The program puts each thing that the program makes from this signal
   into 1 of 3 groups against the memory:
   - **confirmed**: the part was already in memory, and this signal
     made the part again
   - **added**: the part is new
   - **not seen this time**: the part was in memory, but this signal
     did not make the part. The part stays in memory. The program does
     not remove the part. The program only adds a count to the entry.
4. The program saves the pool back to FILE, with a line in the history
   of the pool for this signal. The file is JSON. A memory holds only
   signals that the program read at 1 frame. The same number means a
   different word at a different width. The program refuses a signal
   at a different width and gives the reason.

The test in `examples/memory/` has 4 steps:

- the first half of Alice, from nothing
- the second half of Alice, against that memory
- the second half of Alice again
- the German text, against the English memory

```
                              produced  confirmed  added  not seen
first half, from nothing         14079          0  14079         0
second half, against it          19925      10588   9337      3491
second half again                19833      19833      0      3583
German, against the English      32784      14797  17987      8619
```

The second pass over the same text adds nothing at level 0. The second
pass adds 5 parts at level 1. The memory changed the positions of the
parts in the pool after the sort, so 5 new pairs occurred. A third pass
will find even fewer.

The second pass reaches 19,833 of the 19,925 parts that the first pass
made. The rest are heads. A part that the program minted on the first
pass now stands in front of each head. The result shows that the loop
has no more new things to find. The German text against the English
memory counts 14,797 parts as confirmed. Those parts are the short
parts that the 2 alphabets share. The German text adds 17,987 parts
that English never made.

```python
pool, made_of, part_of, history = load_memory(path)
levels, pool, made_of, part_of = run_levels(words, sep, cap, pool, made_of, part_of)
save_memory(path, pool, made_of, part_of, history + [(name, size, frame)])
```

### Time: read the sequence as before and after

The signal is in order. That order is time. FOLLOWS was always 1 way to
read the order. The function `time_tables()` reads the order in 3 more
ways at each level. Each way points the comparison along the sequence:

- **arrows**: a pair of runs that occurs in both orders, with a count
  for each order. The order that occurs more is an arrow (`said ->
  Alice` in `examples/text/alice.txt.record.txt`, level 0).
- **effects**: what occurs in the stretch after a run at 2 or more
  times its usual rate, compared with the rate that you expect. An
  example is the row for `I` in the same table. The stretch is the
  usual distance to the separator of the next level. At level 0 on
  Alice, the stretch is approximately a clause. Thus the unit comes
  from the signal itself. The limit of 2 or more is the same limit
  that the classes use: 2 occurrences make a pattern.
- **chains**: the program follows the strongest effect forward from
  the most common runs (the CHAINS lines of the same table). In
  `examples/agc/luminary099.rope.record.txt`, the instruction flow
  loops back on itself.

These tables are the before and after of a signal that was only
watched. A cause is an arrow that remains when you do something. The
example `examples/agc-live/` presses a key and records each signal.
Then the example compares the signal with the key press against the
signal without the key press. The tables are the same, read across the
2 signals.

## 8. Lens

The lens only controls how the record shows a word on the page. The
lens `raw` shows hex. The lens `ascii` shows the character when the
word is 8 bits wide. The lens `utf8` decodes a whole run as UTF-8. Thus
a-umlaut appears as the character itself and not as `\xc3\xa4`.

The lens `octal` shows a word in base 8. The Apollo listing is printed
in base 8. The algorithm never uses the lens. If you change the lens,
each table has the same contents with different labels.

## 9. Record

The program writes all of the above in 2 ways: a text record that
people can read, and a JSON record that programs can read. The text
record has the FRAME, a LEVELS summary table, and then each table for
each level. The JSON record has each word, pair, run, part, change, and
class for each level, not only the top of each table.

`levels[0]` is the signal itself. `levels[1]` is the first level up.
The densities and the part_of lists come from the pool that all levels
share. Thus a level-0 part lists the level-1 parts that contain the
level-0 part.

## 10. Run

`Root` is the 1 call that a program made on Discovery makes. `Root`
gives:

- the signal as read (sections 1 to 3)
- level 0 on the pool that all levels share (sections 4 to 7)
- a call for each level above level 0

`discover()` is `Root` plus 2 more operations. The first operation runs
the levels to the end. The second operation writes the record (sections
8 and 9). `discover()` returns the paths of the 2 record files.
`main()` reads the command line.

## What is not in the file

The file has no list of file types, no character table, no dictionary,
no grammar, and no training step. The file has no limit value that a
person selected by hand to fit 1 example. The 1 tolerance is the
`chance` term in the frame step. The `chance` term is the random wobble
for the number of rows at that width. The program computes the `chance`
term from the signal itself.
