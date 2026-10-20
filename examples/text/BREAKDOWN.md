# Breakdown: the novel Alice in Wonderland

## The input

The file `alice.txt` is the full text of *Alice's Adventures in Wonderland*. The file has 144,395 bytes. Discovery gets this file and no other input. No one tells Discovery:

- that the file is text
- that the text is English
- that the text is ASCII

Discovery gets only the raw bytes.

```
python discovery.py examples/text/alice.txt --lens ascii
```

The `ascii` lens makes the output show letters in place of raw numbers. The lens changes only the display. The tables are the same with the lens and without the lens.

## FRAME: 8-bit words, with the top bit always 0

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

Each width that is a multiple of 8 has a score of approximately 0.95. No other width has a score near 0.95. The program picks the narrowest of these widths. Thus the answer is 8.

Column 0 is 1 in 0 percent of the words. This bit is never 1. From column 0, Discovery finds the first result: the words are 8 bits wide, but only 7 of the bits carry information. Column 2 is 1 in approximately 95 percent of the words. Column 2 is the bit that is 1 in each lowercase letter.

## WORDS: 73 different words

```
WORDS   144395 words, 73 distinct
  00100000          25055
  01100101  e       13391
  01110100  t       10217
  01100001  a       8154
  01101111  o       7971
```

There are 73 different words in 144,395 words. The most common word is `00100000`, the space character. The next words are e, t, a, o, h, n, i, s, r. This sequence is the frequency order of the letters of English. The order came from the count alone.

The FOLLOWS table shows the words that occur in pairs. The pair `e` then space occurred 4,423 times. The pair `t` then `h` occurred 3,197 times. The pair `h` then `e` occurred 3,706 times. These pairs are the most common 2-letter sequences of English (`th`, `he`, `in`). The program found the pairs without help.

## RUNS: the words of the language

The space is the most common word. Thus the space becomes the separator. The program cuts the signal at each separator. To cut a signal is to divide the signal into runs. A run is the sequence of words between 2 separators. Here the separator is the space, so the runs are the English words.

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

The RUN FOLLOWS table shows the runs that occur in pairs:

- `said the`, 197 times
- `of the`, 102 times
- `in a`, 84 times
- `Mock Turtle`, 30 times
- `said Alice`, 25 times

## MINT: the parts inside the words

The mint step finds the parts that the English words share. To mint a part is to make a new part from 2 parts that have the same start or the same end.

```
MINT   14 rounds; parts minted per round: 10038 3800 1303 484 176 88 37 22 15 10 4 1 2 0
  pool: 6466 distinct runs in, 22446 parts out
```

The mint loop did 14 rounds. Then the loop stopped, because round 14 made no new parts. The loop started with 6,466 runs. The loop ended with 22,446 parts. The table below lists the parts in order of density. The density of a part is the number of other parts that contain the part.

```
  part   density   whole   inside (sample)
  e         1615       0   the, she, Alice, be
  \n        1544       0   be\n, the\n, dance.\n\n
  s         1275       0   she, said, was, as
  ,         1211       0   Alice,, it,, again,
  t         1113       0   the, to, it, that
  ing        448       0   King, looking, getting, nothing
```

The part `e` occurs inside 1,615 other parts. The part `e` was never a whole run. The newline character (`\n`) is the second part in order of density. The newline character also was never a whole run. Thus the newline character is like a separator that the program did not pick. The record is the source of this hint.

A second run with `--separators 20,0a` (space and newline) uses this hint. In the second run, the class `[+ed, +ing]` increases from 22 members to 27 members. A new class `[+,, +.]` with 44 members also occurs. The members of this new class are words that end a clause or a sentence.

## ENDINGS and BEGINNINGS

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

Punctuation comes first in the ENDINGS table (`+,` `+.` `+'` `+:` `+;`). Then the letters come. Then `+ing` and `+ed` come. No one told the program that a comma is different from a letter. The record shows the comma only as a part that attaches to the end of many different parts. The record shows `ing` in the same way.

## CLASSES: parts that accept the same set of changes

A class is a group of parts that accept the same changes. A class is like a group of words that follow the same grammar pattern.

```
CLASSES
  [+ed, +ing]
     22 members: swallow, remain, consider, crawl, fann, mutter, nibbl, peep, produc, pull, rais, rubb
  [+,, +.]
     12 members: exclaimed, interesting, middle, civil, deeply, knowledge, Eaglet, spectacles
  [+,, +s]
      6 members: creature, her\nhand, manner, pencil, toe, ucumber-frame
```

The first class contains the 22 stems that occur with both `ed` and `ing`: swallow, remain, consider, crawl, mutter, nibbl(e), peep, pull, rais(e). A grammar book calls these stems verbs. The record calls these stems only "parts that accept `+ed` and `+ing`".

The class `[+,, +s]` contains creature, manner, pencil, toe. These parts are things that occur in the plural and also get a comma after them. The class with `her\nhand` and `ucumber-frame` shows 2 problems that come from a single separator. The part `her\nhand` has a line break inside a run. The part `ucumber-frame` is a stem. The neighbors in the pool decided the point where the mint divided this stem.

## CRYSTAL: 1 entry for each common word

A crystal is the entry of the record for 1 word. The crystal is like a dictionary entry. The program makes the crystal from the signal alone.

```
  the   seen 1340
    made of    th, he, t, e
    part of    they, their, them, then, there, these, in\nthe, 'the
    changes    +y, +ir, +m, +n, +re, +se, in\n+, '+
    followed   Mock 47, March 25, King 22, Queen 20, White 17, Gryphon 17
    preceded   said 197, of 102, and 60, to 56, in 54, at 48
```

The crystal shows all that the record knows about `the`:

- the smaller parts that make `the`
- the larger words that contain `the`
- the changes that make `the` into those larger words
- the words that come after `the` (Mock Turtle, March Hare, King, Queen, White Rabbit, Gryphon)
- the words that come before `the` (said, of, and, to, in, at)

The crystal is the dictionary entry that the signal gives. The signal gives no more than the crystal.

## Level 1: the same steps, one level up

```
LEVELS
  level  symbols  distinct     runs  distinct   minted  classes(2+)    added  pool total
      0   144395        73    24167      6466    15980          390    22446       22446
      1    24167      6466     1341      1328     5408          133     6709       29155
      2     1341      1328        5         5        0            0        5       29160
      3        5         5        1         1        0            0        1       29161
```

Level 1 takes the runs from level 0 as its words. The most common run is `the`. Thus `the` becomes the separator of level 1. A level-1 run is the sequence of text between a `the` and the next `the`. The mint step finds what the level-1 runs share. All parts from level 1 go into the same pool as the parts of level 0.

The pool total increases: 22,446 parts, then 6,709 more parts, then 5 more, then 1 more, then no more.

```
ENDINGS                 BEGINNINGS
  +said    357            and+          154
  +and     181            was+          112
  +to      151            Mock Turtle+   89
  +of      122            she+           83
  +in      120            it+            77
```

The ENDINGS table shows the words directly before `the`: `said the`, `and the`, `to the`, `of the`, `in the`, `at the`. The BEGINNINGS table shows the words directly after `the`: `the ... and`, `the ... was`, `the Mock Turtle`. Level 0 had these sequences as pairs. Level 1 has these sequences as the ends and the starts of parts.

Both levels add connections to the same words. The part `said` occurs inside 16 level-0 parts and inside 428 level-1 runs. Thus the total density of `said` is 444.

## Summary of the record

The program started from a sequence of bits. The record shows:

- 8-bit words, with 7 bits in use
- 73 symbols
- 1 symbol that is the separator
- the frequency order of the symbols
- the common pairs
- the words of the language
- the parts that make the words
- the endings and the beginnings that make one word into a different word
- the classes of words that accept the same endings
- a dictionary entry for each word, with the words that occur next to the word

All of these results are in `alice.txt.record.txt`. The file `alice.txt.record.txt` shows the top of each table. The file `alice.txt.record.json` shows the full tables.
