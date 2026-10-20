# How Discovery works

Discovery does one thing: it compares. A comparison takes two things
and sorts what is in them into three groups:

| group | what goes in it |
|---|---|
| same | what the two things have in common |
| different | what's left of each thing once the shared part is taken out |
| not part | what the comparison never touched |

That comparison is the whole program. The program runs it on the input
first. Then it runs it on the results of that comparison, and on the
results of those, and keeps going until a pass finds nothing new.
Nothing is ever thrown away.

The file `discovery.py` has ten numbered sections, and this guide walks
through them in order. The examples come from `examples/text/alice.txt`
and `examples/german/ep-00-01-17.de` unless the text names a different
file.

## 1. Signal: the file as bits

The program opens the file as raw bytes and turns them into one long
string of ones and zeros. That's all this step does. It doesn't look at
the file name, the extension, or the first few bytes to guess what kind
of file it has. A novel, a compiled program, a picture and a sound
recording all come in the same way.

```python
bits = bin(int.from_bytes(data, 'big'))[2:].zfill(len(data) * 8)
```

## 2. Frame: how wide one unit is

The program works out how many bits make up one unit of the file, the
way one byte is one unit of text. That width is the frame. The program
finds it by trying each width in turn and seeing which one makes the
bit patterns line up.

Here is how. Take a width w and lay the bits out in rows of that width,
so they form a grid. Each column of the grid then holds every w-th bit
of the file. At the right width, each column is a one at its own steady
rate. In ASCII text at width 8, column 0 is a one in 0 percent of the
rows, because the top bit of a byte is never used. Column 2 is a one in
about 95 percent of the rows, because the letters all sit in the range
0x60 to 0x7f. At a wrong width such as 7, the bits get mixed across the
columns, and every column drifts toward about 50 percent.

The program scores each width by the gap between its two extreme
columns: the one that is a one most often and the one that is a one
least often. It picks the width with the largest gap.

There is one condition. When the program weighs a wider width against
the narrower width it has already picked, it only switches to the wider
one if the gap is bigger by more than chance alone could explain. That
allowance is the `chance` term: the amount of random noise you would
expect from that number of rows.

```python
score[w] = max(cols) - min(cols)
chance   = 1 / rows ** 0.5
if score[w] > score[picked] + chance: picked = w
```

Next, the program checks whether the width it picked is really a
smaller width repeated. The record calls this check a fold. A multiple
of the true width shows the true width's columns side by side: width 16
on 8-bit text is the same eight columns twice over. The gap for the
multiple can come out slightly higher by chance alone, so the pick can't
be trusted without this check.

So the program tests each smaller width that divides evenly into the
one it picked. For each, it checks whether the column pattern of the
larger width is just the column pattern of the smaller width repeated.
The allowance here is the wobble, which is 0.5 divided by the square
root of the number of rows: how much the two patterns could differ by
chance. If they differ by less than that, the smaller width is the true
one.

```python
wobble = 0.5 / rows ** 0.5
fold[w] = mean(|profile[picked][c] - profile[w][c % w]| for c in range(picked))
if fold[w] <= wobble: frame = w
```

The Apollo Guidance Computer's flight program, the rope file in
`examples/agc`, is the case that needed this check. By the gap alone, the program picked 60. But 60 is
15 repeated four times, and the fold check found the true width. The
two patterns differed by no more than 0.004.

The record shows:

- the 8 best widths
- the width the program picked
- each fold check
- the final width
- how often each column is a one at the final width

Those column rates are the first thing Discovery learns about a signal.

With `--frame N` you set the width yourself. That lets you look at a
signal at a width other than the one the frame step picked. The frame
step reads the compiled program in `examples/code` at 64 bits. A second
command with `--frame 8` reads the same program at 8 bits, and the two
records show different things.

## 3. Words

The program cuts the bit string into pieces, each one frame wide, and
each piece is a word. Then it counts how often each different word
occurs, and counts each pair of words that occur next to each other.

```python
words        = [int(bits[i:i+w], 2) for i in range(0, len(bits)-w+1, w)]
word_counts  = Counter(words)
word_follows = Counter(zip(words, words[1:]))
```

In Alice there are 73 different words in 144,395 words. The most common
is `00100000`, the space. In the German file there are 88 different
words, and the word `11000011` occurs 2,827 times. That is the byte
UTF-8 puts first in characters such as a-umlaut, o-umlaut, u-umlaut and
sharp-s.

## 4. Runs

The program takes the most common word and uses it as the place to cut.
That word is the separator. The program cuts the sequence of words at
every separator, and each stretch of words between two separators is a
run.

In text the separator is the space, so the runs are the words of the
language. In a compiled program the separator is the zero byte, so the
runs are everything that sits between zero bytes: machine code,
function names and strings.

The option `--separators 2` uses the two most common words as
separators. With `--separators 20,0a` you choose the separators
yourself, in hex (that example is space and newline).

The record tells you when you need this option. The sign is a word that
sits inside a great many other parts (the parts table calls that count
its density) but never shows up as a complete run on its own. A word
like that is acting as a separator the program didn't choose. In Alice
that word is the newline, which is only the 14th most common word.

The program counts the runs, and counts each pair of runs that occur one
after the other.

## 5. Mint: new parts until nothing new comes

The program compares the runs in pairs. Whenever two runs start the
same way, it cuts out the shared start, and what's left of each, as new
parts. This is the mint step: to mint a part is to make a new part from
two parts that have the same start or the same end. The step runs until
a round makes nothing new.

The program keeps one list of every part it has found so far. That list
is the pool, and it starts out holding each different run.

The program sorts the pool. Once sorted, each part sits next to the part
it shares the longest start with; no other part in the pool shares a
longer start with it. The program then compares each pair of neighbors:

- It counts how many words the two parts share from the start.
- If they share nothing, it moves on to the next pair.
- Otherwise it makes three new parts: the start the two share, and
  what's left of each of them. Each new part goes into the pool. The
  program records the whole as "made of" its parts, and each part as
  "part of" the whole.

```
   abcd   vs  abef   ->  shared ab    leftovers cd, ef
   walk   vs  walked ->  shared walk  leftover ed   (walk is already whole, so only ed is new)
```

Then the program reverses every part and does the same comparison
again, which finds the ends that parts share. `looked` and `walked`
share `ed`, for example.

The program never removes a part. So two parts that were both in the
pool last round were already neighbors last round and have already been
compared. That is why the program only compares a pair when one of the
two parts is new. When a full round makes nothing new, the loop stops.
That is the only stop rule.

Note: `--cap` is a size limit, not a rule. If the pool grows too large,
the loop stops early, and the record says so.

```
Alice:   14 rounds   10038 3800 1303 484 176 88 37 22 15 10 4 1 2 0
German:  10 rounds    9291 3641 1205 402 130 42 7 2 1 0
```

Each new part also records what was left over when it was made. What's
left after a start that two parts share is an ending (`+ed`, `+ing`,
`+en`, `+ung`). What's left before an end that two parts share is a
beginning (`be+`, `ge+`, `un+`).

Each part keeps two numbers. The first is how many times it showed up
as a complete run. The second is its density: how many other parts
contain it. In Alice, the letter `e` is never a complete run, but 1,615
other parts contain it.

## 6. Crystal: grouping the parts

The program reads back through the pool and groups the parts by what you
can add to them. That grouping is a second table, called the crystal.
The pool itself doesn't change, and no detail is lost: the operation is
the same as removing duplicates. Making the crystal from a pool is
called crystallizing it.

Take any one part. A change is whatever turns it into a larger part that
contains it. The change from `walk` to `walked` is `+ed`. The change
from `walk` to `walking` is `+ing`.

A class is every part that accepts the same set of changes. Each stem
that accepts exactly the set `{+ed, +ing}` lands in one class.

In Alice that class has 22 members, among them swallow, remain,
consider, crawl, mutter, nibbl, peep, pull and rais. In the German file
the class `{+en, +t}` has 52 members, and the class `{+n, +r}` has 42.

The crystal also writes one entry for each common run, like a
dictionary entry. The entry shows:

- what the run is made of
- what contains the run
- the changes the run accepts
- what follows the run
- what comes before the run

The entry for `walk` is the stem, its forms, and the runs that occur
next to it.

## 7. Levels: do it again one level up, until nothing changes

Sections 3 to 6 together are one level: count the words, cut the
sequence into runs at the most common word, mint, and crystallize. Then
the program treats each run as a single unit and runs the same loop
again on what this level produced, so it finds phrases made of words
the same way it found words made of letters. Nothing is replaced;
everything is added.

1. The next level's symbols, the units it counts and cuts, are the runs
   of this level, unchanged.
2. The classes this level found (the ones with two or more members)
   give the next level a second way for two symbols to count as the
   same. Two symbols are the same if they are the same run. They are
   also the same if they are two runs from the same class. Sometimes
   two sequences match only because a member of one class sits in the
   same position in both. When that happens, the class itself goes into
   that position of the part the two sequences share. This is the one
   place where what the crystal produced feeds back into the
   comparison.
3. Every new structure joins the pool, and there is only one pool. A
   new structure can be a run of runs, a part the mint step made, or a
   class. Its connections go to the parts it is made of, at whatever
   level those parts live. A level-0 word that sits inside 40 level-1
   runs gets 40 added to its density.
4. The loop goes on until a level has only one run. One run can't be
   cut.

Each level's sequence is shorter than the one before it, because the
separator is always there and the program cuts it out. So the loop ends
on its own. The additions shrink to nothing before it does:

```
  level  symbols  distinct     runs  distinct   minted  classes(2+)    added  pool total
      0   144395        73    24167      6466    15980          390    22446       22446
      1    24167      6466     1341      1328     5408          133     6709       29155
      2     1341      1328        5         5        0            0        5       29160
      3        5         5        1         1        0            0        1       29161
```

The pool gains 22,446 parts, then 6,709 more, then 5, then 1, then
nothing. The pool only grows, and the growth stops.

At level 1 for Alice, the separator is `the`. A run is the sequence
between two occurrences of `the`. The endings are whatever comes
immediately before `the` (`+said` 357, `+and` 181, `+to` 151, `+of`
122). The beginnings are whatever comes immediately after it (`and+`,
`was+`, `to+`, `Mock Turtle+`). In the German text the separator is the
comma, and the runs that repeat most are the forms of address: `Herr
Kommissar`, `meine Damen und Herren`, `Frau Prasidentin`.

For the Apollo assembly source, the separator is `#`, the comment mark.
The level-1 parts that sit inside the most other parts are instruction
sequences such as `TC BANKCALL`, `CAF ZERO` and `CCS A`. The beginnings
are the words the programmers used to start a comment: `TO+`, `FOR+`,
`IN+`, `IF+`, `AND+`, `SET+`.

```python
L = run_level(seq, 1, pool, made_of, part_of, cap, class_of, level)
seq, class_of = L['runs'], L['next_class_of']
```

### Memory: compare a new signal with what the program already knows

The program can save its pool after reading one file and load it back
before reading the next. That saved pool is the memory. With a memory
loaded, the new file is compared not only against itself but against
everything the program found before.

The question "does the model agree with reality?" and the question "is
this the same as that?" are the same question asked about different
things. The comparison answers both. Memory turns the second question
into a loop.

With the option `--memory FILE`, the program does four things:

1. It loads the pool from FILE. An empty file means an empty memory.
2. It reads the new signal in the usual way, but the parts from memory
   are in the pool, and after the sort they sit next to the new runs.
   So each new run is compared with the parts from memory as well as
   with the rest of the signal.

   A comparison only counts when this signal is one side of it. The
   program doesn't compare two parts from memory that the signal hasn't
   reached; it compared those when it made them. So a memory never
   confirms its own parts. A part from memory that this signal makes
   again counts as **confirmed**. The program then compares that part
   with its neighbors one more time, so the signal can also reach
   whatever was made from that part last time.
3. It puts everything made from this signal into one of three groups
   against the memory:
   - **confirmed**: the part was already in memory, and this signal
     made it again
   - **added**: the part is new
   - **not seen this time**: the part was in memory, but this signal
     didn't make it. The part stays in memory. The program doesn't
     remove it; it only adds a count to the entry.
4. It saves the pool back to FILE, with a line in the pool's history for
   this signal. The file is JSON. A memory holds only signals read at
   one frame, because the same number means a different word at a
   different width. The program refuses a signal at a different width
   and says why.

The test in `examples/memory/` has four steps:

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

The second pass over the same text adds nothing at level 0, and 5 parts
at level 1. The memory changed where the parts sit in the sorted pool,
so five new pairs of neighbors turned up. A third pass would find even
fewer.

The second pass reaches 19,833 of the 19,925 parts the first pass made.
The rest are shared starts that the first pass cut out of two
neighbors. A part the first pass made now stands in front of each of
them in the sorted pool, so the pair that made it the first time is no
longer a pair. The result shows that the loop has nothing more to find.
The German text against the English memory confirms 14,797 parts, which
are the short parts the two alphabets share, and adds 17,987 parts that
English never made.

```python
pool, made_of, part_of, history = load_memory(path)
levels, pool, made_of, part_of = run_levels(words, sep, cap, pool, made_of, part_of)
save_memory(path, pool, made_of, part_of, history + [(name, size, frame)])
```

### Time: reading the sequence as before and after

The file is in order, and that order is time. The program reads along
the sequence to find what tends to come before and after what. FOLLOWS,
the count of which word comes right after which, was always one way of
reading the order. The function `time_tables()` reads it in three more
ways at each level. Each one points the comparison along the sequence:

- **arrows**: a pair of runs that occurs in both orders, with a count
  for each order. The order that occurs more often is an arrow (`said
  -> Alice` in `examples/text/alice.txt.record.txt`, level 0).
- **effects**: what shows up in the stretch after a run at two or more
  times its usual rate, compared with the rate you would expect. The
  row for `I` in the same table is an example. The stretch is the usual
  distance to the next level's separator; at level 0 on Alice that is
  roughly a clause, so the unit comes from the signal itself. The limit
  of two or more is the same limit the classes use: two occurrences
  make a pattern.
- **chains**: the program follows the strongest effect forward from
  the most common runs (the CHAINS lines of the same table). In
  `examples/agc/luminary099.rope.record.txt`, the instruction flow
  loops back on itself.

These tables are the before and after of a signal that was only
watched. A cause is an arrow that is still there when you do something.
The example in `examples/agc-live/` presses a key and records each
signal, then compares the signal with the key press against the signal
without it. The tables are the same ones, read across the two signals.

## 8. Lens: how a word is printed

The lens only controls how the record shows a word on the page. The
`raw` lens shows hex. The `ascii` lens shows the character, when the
word is 8 bits wide. The `utf8` lens decodes a whole run as UTF-8, so
an a-umlaut appears as the character itself and not as `\xc3\xa4`.

The `octal` lens shows a word in base 8, which is how the Apollo listing
is printed. The algorithm never uses the lens. Change the lens and every
table has the same contents under different labels.

## 9. Record: what gets written

The program writes everything above in two forms: a text record that
people can read, and a JSON record that programs can read. The text
record has the FRAME, a LEVELS summary table, and then every table for
every level. The JSON record has each word, pair, run, part, change and
class for each level, not just the top of each table.

`levels[0]` is the signal itself, and `levels[1]` is the first level
up. The densities and the part_of lists come from the pool that all
levels share, so a level-0 part lists the level-1 parts that contain
it.

## 10. Run: the whole program end to end

`Root` is the one call that a program built on Discovery makes. `Root`
gives you:

- the signal as read (sections 1 to 3)
- level 0 on the pool that all levels share (sections 4 to 7)
- a call for each level above level 0

`discover()` is `Root` plus two more operations. The first runs the
levels to the end. The second writes the record (sections 8 and 9).
`discover()` returns the paths of the two record files. `main()` reads
the command line.

## What is not in the file

The file has no list of file types, no character table, no dictionary,
no grammar, and no training step. It has no limit value that someone
picked by hand to fit one example. The one tolerance is the `chance`
term in the frame step: the random wobble you would expect for the
number of rows at that width, and the program computes it from the
signal itself.
