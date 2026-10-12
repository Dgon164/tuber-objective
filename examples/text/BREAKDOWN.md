# Breakdown: reading Alice in Wonderland

## What goes in

`alice.txt` is the full text of *Alice's Adventures in Wonderland* — 144,395 bytes. Discovery gets the file and nothing else. It is not told this is text, not told it is English, not told it is ASCII.

```
python discovery.py examples/text/alice.txt --lens ascii
```

The `ascii` lens makes the output show letters instead of raw numbers. It only changes the display — the tables are the same either way.

## Frame: the file uses 8-bit words, and the top bit is always off

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

Every multiple of 8 scores about 0.95. Nothing else comes close. The narrowest one wins, so the answer is 8.

Column 0 is a 1 exactly zero percent of the time — that bit is never on. That is the first thing Discovery learned: the words are 8 bits wide but only 7 bits carry anything. Column 2 is a 1 about 95% of the time, which is where lowercase letters live.

## Words: there are 73 of them

```
WORDS   144395 words, 73 distinct
  00100000          25055
  01100101  e       13391
  01110100  t       10217
  01100001  a       8154
  01101111  o       7971
```

73 different words out of 144,395 total. The most common is `00100000` — the space. Then e, t, a, o, h, n, i, s, r. That is the letter frequency order of English, found just by counting.

The FOLLOWS table shows which words come in pairs: `e` then space happened 4,423 times. `t` then `h` happened 3,197 times. `h` then `e` happened 3,706 times. Those are the most common two-letter combos in English (`th`, `he`, `in`), and they showed up on their own.

## Runs: the actual words of the language

The space is the most common word, so it becomes the separator. A run is what sits between two spaces — which means the runs are the English words.

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

RUN FOLLOWS shows which words come in pairs: `said the` 197 times, `of the` 102, `in a` 84, `Mock Turtle` 30, `said Alice` 25.

## Mint: the parts inside words

```
MINT   14 rounds; parts minted per round: 10038 3800 1303 484 176 88 37 22 15 10 4 1 2 0
  pool: 6466 distinct runs in, 22446 parts out
```

The mint loop ran 14 rounds and then stopped because nothing new came out. It started with 6,466 runs and ended with 22,446 parts. The parts ranked by how many other parts they sit inside:

```
  part   density   whole   inside (sample)
  e         1615       0   the, she, Alice, be
  \n        1544       0   be\n, the\n, dance.\n\n
  s         1275       0   she, said, was, as
  ,         1211       0   Alice,, it,, again,
  t         1113       0   the, to, it, that
  ing        448       0   King, looking, getting, nothing
```

`e` sits inside 1,615 other parts and was never a word on its own. The newline character (`\n`) is the second most connected part and also never a word on its own — it is acting like a separator that was not picked. The record is where this hint comes from. Running again with `--separators 20,0a` (space and newline) acts on it: the class `[+ed, +ing]` grows from 22 members to 27, and a new class `[+,, +.]` of 44 members appears — words that end a clause or a sentence.

## Endings and beginnings

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

Punctuation comes first (`+,` `+.` `+'` `+:` `+;`), then letters, then `+ing` and `+ed`. Nothing told the program that a comma is different from a letter. It just shows up as something that gets attached to the end of many different parts — and so does `ing`.

## Classes: parts that take the same set of changes

```
CLASSES
  [+ed, +ing]
     22 members: swallow, remain, consider, crawl, fann, mutter, nibbl, peep, produc, pull, rais, rubb
  [+,, +.]
     12 members: exclaimed, interesting, middle, civil, deeply, knowledge, Eaglet, spectacles
  [+,, +s]
      6 members: creature, her\nhand, manner, pencil, toe, ucumber-frame
```

The first class is the 22 stems that appear with both `ed` and `ing`: swallow, remain, consider, crawl, mutter, nibbl(e), peep, pull, rais(e). A grammar book would call these verbs. The record just calls them "parts that take `+ed` and `+ing`."

The class `[+,, +s]` holds creature, manner, pencil, toe — things that come in plural and also get a comma after them. The class with `her\nhand` and `ucumber-frame` shows the rough edges a single separator leaves: a line break stuck inside a run, and a stem cut where the pool's neighbors happened to cut it.

## Crystal: one entry per common word

```
  the   seen 1340
    made of    th, he, t, e
    part of    they, their, them, then, there, these, in\nthe, 'the
    changes    +y, +ir, +m, +n, +re, +se, in\n+, '+
    followed   Mock 47, March 25, King 22, Queen 20, White 17, Gryphon 17
    preceded   said 197, of 102, and 60, to 56, in 54, at 48
```

This is everything the record knows about `the`: what it is made of, what bigger words contain it, how it changes into those bigger words, what comes after it (Mock Turtle, March Hare, King, Queen, White Rabbit, Gryphon), and what comes before it (said, of, and, to, in, at). That is the dictionary entry the signal provides — and nothing more.

## Level 1: do the whole thing again, one level up

```
LEVELS
  level  symbols  distinct     runs  distinct   minted  classes(2+)    added  pool total
      0   144395        73    24167      6466    15980          390    22446       22446
      1    24167      6466     1341      1328     5408          133     6709       29155
      2     1341      1328        5         5        0            0        5       29160
      3        5         5        1         1        0            0        1       29161
```

Level 1 takes the runs from level 0 and treats them as its words. The most common one is `the`, so `the` becomes the separator. A level-1 run is the stretch of text between one `the` and the next. The mint finds what those stretches share, and everything it makes goes into the same pool as the level-0 parts: 22,446 parts, then 6,709 more, then 5, then 1, then nothing new.

```
ENDINGS                 BEGINNINGS
  +said    357            and+          154
  +and     181            was+          112
  +to      151            Mock Turtle+   89
  +of      122            she+           83
  +in      120            it+            77
```

What sits right before `the`: `said the`, `and the`, `to the`, `of the`, `in the`, `at the`. What sits right after it: `the ... and`, `the ... was`, `the Mock Turtle`. Level 0 had these as pairs. Level 1 has them as the edges of parts, and the connections pile up on the same words: `said` sits inside 16 level-0 parts and 428 level-1 stretches, so its total density is 444.

## What this adds up to

Starting from a string of bits: 8-bit words with 7 used. 73 symbols. One of them is a separator. The frequency order of the symbols. The common pairs. The words of the language. The pieces words are made of. The endings and beginnings that turn one word into another. The classes of words that take the same endings. And a dictionary entry per word giving its company. All of it is in `alice.txt.record.txt`, and everything — not just the top of each table — is in `alice.txt.record.json`.
