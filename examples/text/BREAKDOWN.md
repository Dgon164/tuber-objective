# Breakdown: the novel Alice in Wonderland

## The input

The file `alice.txt` is the full text of *Alice's Adventures in Wonderland*, 144,395 bytes. Discovery, the program this repository is about, gets this file and nothing else. Nobody tells it:

- that the file is text
- that the text is English
- that the text is ASCII

All it gets is the raw bytes.

```
python discovery.py examples/text/alice.txt --lens ascii
```

The `--lens ascii` option is a display setting. It makes the record print each unit of the file as the letter it stands for, instead of as a raw number. It changes only how the output looks. The tables come out the same with it and without it.

## FRAME: the units are 8 bits wide, and the top bit is always 0

The first thing the program works out is how wide one unit of the file is. It tries many widths. For each width, it lays the bits out in rows of that width and measures, column by column, how often the bit in that column is 1. The score for a width is the gap between the column that is 1 most often and the column that is 1 least often. When the bits really do line up at a width, some columns are nearly always 1 and some nearly never, so the gap is large. This is the FRAME table.

```
FRAME
  width  score   least-1 column   most-1 column
   56    0.954   col   0 at 0.000   col  42 at 0.954
   64    0.952   col   0 at 0.000   col  34 at 0.952
   ...
    8    0.950   col   0 at 0.000   col   2 at 0.950
  picked width 8
  chosen width 8
  column rates at width 8:
    0.000 0.745 0.950 0.235 0.338 0.477 0.333 0.452
```

Every width that is a multiple of 8 scores about 0.95, and no other width comes close. When several widths tie like this, the program takes the narrowest one. So the answer is 8 bits: one byte.

The column rates at the bottom are the first thing the program learned about the file. Column 0 is 1 in 0 percent of the units. That bit is never set. So the program's first finding is that the units are 8 bits wide but only 7 of them carry information. That matches ASCII, which uses only 7 of the 8 bits in a byte and leaves the top one at 0. Column 2 is 1 in about 95 percent of the units. That is the bit which is 1 in every lowercase letter.

## WORDS: 73 different words

Next the program cuts the file into 8-bit units and counts how many times each different unit appears. The record calls these units words. A word here is one unit of the width the FRAME step chose, so in this file a word is one byte, not an English word. This is the WORDS table.

```
WORDS   144395 words, 73 distinct
  00100000          25055
  01100101  e       13391
  01110100  t       10217
  01100001  a       8154
  01101111  o       7971
```

There are 73 different words among 144,395. The most common is `00100000`, the space character. After it come e, t, a, o, h, n, i, s, r. That is the frequency order of the letters of English, and you can check it against any published letter-frequency table. The program got the order from counting alone.

The program also counts, for every pair of words that sit next to each other, how often that pair occurs. This is the FOLLOWS table. The pair `e` then space occurred 4,423 times, `t` then `h` 3,197 times, and `h` then `e` 3,706 times. These are the most common two-letter sequences in English (`th`, `he`, `in`). The program found them without help.

## RUNS: the words of the language

The program takes the most common word as the divider, the way a space divides words in a sentence. The record calls the divider the separator. Here the most common word is the space, so the space becomes the separator. The program then cuts the file at every separator, and each stretch between two separators is a run. Because the separator here is the space, the runs are the English words. This is the RUNS table.

```
RUNS   24167 runs between separators, 6466 distinct
  the     1340
  to       634
  and      630
  a        546
  of       433
  she      423
  said     395
  Alice    155
```

The program also counts which run comes after which. This is the RUN FOLLOWS table. The pairs that occur most often are:

- `said the`, 197 times
- `of the`, 102 times
- `in a`, 84 times
- `Mock Turtle`, 30 times
- `said Alice`, 25 times

## MINT: the parts inside the words

Now the program compares the runs with each other. It sorts them so that runs with the same start sit next to each other, then compares each run with its neighbor. When two runs start the same way, it splits them into the shared start and the two leftovers, and each of those three pieces becomes a part. Then it reverses every part and does the same thing again, which finds shared ends. Every part goes into one collection, which the record calls the pool, and the new parts get compared in the next round too. The program keeps going round until a full round finds nothing new. This is the mint step, and the record calls each new part a minted part.

```
MINT   14 rounds; parts minted per round: 10038 3800 1303 484 176 88 37 22 15 10 4 1 2 0
  pool: 6466 distinct runs in, 22446 parts out
```

The mint step ran 14 rounds and stopped because round 14 made no new parts. It started with 6,466 different runs and ended with 22,446 parts.

For each part, the program counts two things: how many other parts contain it, which the record calls the part's density, and how many times it appeared on its own as a complete run, which the record calls its whole count. The PARTS BY DENSITY table lists the parts with the highest density first.

```
  part   density   whole   inside (sample)
  e         1615       0   the, she, Alice, be
  \n        1544       0   be\n, the\n, dance.\n\n
  s         1275       0   she, said, was, as
  ,         1211       0   Alice,, it,, again,
  t         1113       0   the, to, it, that
  ing        448       0   King, looking, getting, nothing
```

The part `e` sits inside 1,615 other parts and was never a whole run by itself. The newline character (`\n`) is second by density, and it was never a whole run either. In other words, the newline behaves like a second divider that the program didn't pick. The record itself is what points this out.

A second run with `--separators 20,0a` takes that hint and uses two separators, the space and the newline (20 and 0a are their byte values, written in hexadecimal). In that run, the group of parts that take both `+ed` and `+ing` (the CLASSES table below explains these groups) grows from 22 members to 27. A new group of 44 parts that take both `+,` and `+.` also appears. Its members are words that end a clause or a sentence.

## ENDINGS and BEGINNINGS

When the mint step splits two parts that share a start, each leftover at the end is what you add to the shared start to get one of the parts back. The record calls those leftovers endings. When two parts share an end, the leftover at the front is a beginning. The program counts how many times each ending and each beginning turned one part into another, and lists them in that order.

```
ENDINGS                 BEGINNINGS
  +,     1997             \n+   916
  +e     1034              e+   905
  +s      820              s+   864
  +\n     803              a+   812
  +.      680              t+   701
  +'      652              '+   696
  +ing    518
  +ed     427
```

Punctuation comes first in the ENDINGS table (`+,` `+.` `+'` `+:` `+;`). Then come the letters, then `+ing` and `+ed`. Nobody told the program that a comma is different from a letter. In the record, a comma is just a part that attaches to the end of many different parts. So is `ing`.

## CLASSES: parts that take the same set of changes

A change is what you add to one part to turn it into another: the change from `walk` to `walked` is `+ed`. A class is a group of parts that all take exactly the same set of changes. It is like a group of words that follow the same grammar pattern, except that the program builds it from the changes alone.

```
CLASSES
  [+ed, +ing]
     22 members: swallow, remain, consider, crawl, fann, mutter, nibbl, peep, produc, pull, rais, rubb
  [+,, +.]
     12 members: exclaimed, interesting, middle, civil, deeply, knowledge, Eaglet, spectacles
  [+,, +s]
      6 members: creature, her\nhand, manner, pencil, toe, ucumber-frame
```

The first class holds the 22 stems that appear with both `ed` and `ing`: swallow, remain, consider, crawl, mutter, nibbl(e), peep, pull, rais(e). A grammar book would call these verbs. The record calls them only "parts that take `+ed` and `+ing`".

The class `[+,, +s]` holds creature, manner, pencil, toe. These appear in the plural and also with a comma after them. The same class holds `her\nhand` and `ucumber-frame`, and those two show the two problems that come from using a single separator. `her\nhand` has a line break inside a run, because the newline wasn't a separator. `ucumber-frame` is a stem that got cut in the wrong place. Where the mint step split it depended on which parts happened to sit next to it in the pool.

## CRYSTAL: one entry for each common word

The last table, the CRYSTAL, gathers everything the record knows about one run into a single entry, one entry for each common run. It reads like a dictionary entry, but the program builds it from the file alone.

```
  the   seen 1340
    made of    th, he, t, e
    part of    they, their, them, then, there, these, in\nthe, 'the
    changes    +y, +ir, +m, +n, +re, +se, in\n+, '+
    followed   Mock 47, March 25, King 22, Queen 20, White 17, Gryphon 17
    preceded   said 197, of 102, and 60, to 56, in 54, at 48
```

The entry shows everything the record knows about `the`:

- the smaller parts that make up `the`
- the larger words that contain `the`
- the changes that turn `the` into those larger words
- the words that come after `the` (Mock Turtle, March Hare, King, Queen, White Rabbit, Gryphon)
- the words that come before `the` (said, of, and, to, in, at)

This is the dictionary entry that the file itself gives. The file gives no more than this.

## Level 1: the same steps, one level up

When the first level is done, the program treats each run as a single unit and does everything again: it finds the most common run, uses it as the separator, cuts the file at it, compares the new runs, and adds what it finds to the same pool. The LEVELS table at the top of the record summarizes each level in one row: how many units it started with and how many of them were different, how many runs it cut and how many were different, how many parts the mint step made, how many classes with two or more members it found, how many parts it added to the pool, and the running total of the pool.

```
LEVELS
  level  symbols  distinct     runs  distinct   minted  classes(2+)    added  pool total
      0   144395        73    24167      6466    15980          390    22446       22446
      1    24167      6466     1341      1328     5408          133     6709       29155
      2     1341      1328        5         5        0            0        5       29160
      3        5         5        1         1        0            0        1       29161
```

Level 1 takes the runs from level 0 as its units. The most common run is `the`, so `the` becomes the level-1 separator, and a level-1 run is the stretch of text between one `the` and the next. The mint step then finds what those level-1 runs share, and all of its parts go into the same pool as the parts from level 0.

The pool total grows: 22,446 parts, then 6,709 more, then 5 more, then 1 more, then no more.

```
ENDINGS                 BEGINNINGS
  +said    357            and+          154
  +and     181            was+          112
  +to      151            Mock Turtle+   89
  +of      122            she+           83
  +in      120            it+            77
```

The level-1 ENDINGS table shows the words that come right before `the`: `said the`, `and the`, `to the`, `of the`, `in the`, `at the`. The BEGINNINGS table shows the words that come right after it: `the ... and`, `the ... was`, `the Mock Turtle`. Level 0 had these as pairs of runs. Level 1 has them as the ends and the starts of parts.

Both levels add connections to the same words. The part `said` sits inside 16 level-0 parts and inside 428 level-1 runs, so its total density is 444.

## Summary of the record

The program started from a string of bits. The record shows:

- 8-bit units, with 7 bits in use
- 73 symbols
- 1 symbol that is the separator
- the frequency order of the symbols
- the common pairs
- the words of the language
- the parts that make up the words
- the endings and the beginnings that turn one word into a different word
- the classes of words that take the same endings
- a dictionary entry for each word, with the words that appear next to it

All of this is in `alice.txt.record.txt`, which shows the top of each table. `alice.txt.record.json` has the full tables.
