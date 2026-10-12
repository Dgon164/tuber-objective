# Breakdown: memory across signals

## What this tests

"Does the model match reality?" and "is this the same as that?" are the same question. The comparator answers both. What makes it a loop is memory: the pool saved after one run and loaded before the next, so each new signal gets compared against everything that came before.

Four runs, one memory file (`alice.memory`, built by the runs):

```
python ../../discovery.py alice-first-half.txt  --lens ascii --memory alice.memory
python ../../discovery.py alice-second-half.txt --lens ascii --memory alice.memory
python ../../discovery.py alice-second-half.txt --lens ascii --memory alice.memory
python ../../discovery.py ep-00-01-17.de        --lens utf8  --memory alice.memory
```

`alice-first-half.txt` and `alice-second-half.txt` are the two halves of Alice, cut at a line break near the middle (72,215 and 72,180 bytes). `ep-00-01-17.de` is the German text from `examples/german`. The memory file is JSON, and one memory holds signals read at one frame (all four here read at 8 bits; a signal at another width is refused with the reason).

A comparison counts only when the signal being read is in it. Two remembered parts the signal has not reached are left alone — they were compared when they were minted — so a memory never confirms itself. A remembered part the signal produces again is confirmed, and is then compared with its own neighbours once more, so what was minted from it last time can be reached too.

## Run 1: the first half, starting from nothing

```
MEMORY   alice.memory
  before this signal: 0 parts, from nothing
  level  produced  confirmed      added  not seen this time
      0     14079          0      14079                   0
      1      2485          0       2189                   0
      2         3          0          3                   0
      3         1          0          1                   0
  after: 16272 parts, saved
```

Everything is new. Nothing was in memory to confirm. 16,272 parts go into the memory file.

## Run 2: the second half, against the first

```
MEMORY   alice.memory
  before this signal: 16272 parts, from alice-first-half.txt (72215 bytes, frame 8)
  level  produced  confirmed      added  not seen this time
      0     19925      10588       9337                3491
      1      6711       1420       4510                 769
      2         4          0          4                   3
      3         1          0          1                   1
  after: 30124 parts, saved
```

The second half produces 19,925 parts at level 0. Of those, 10,588 were already in memory from the first half and the second half reached them again — the letters, the common words, the common pieces of words. 9,337 are new. 3,491 parts the first half produced were not reached by the second half (names and words that only appear early in the book, and heads that only a first-half neighbour exposes). Those stay in memory — nothing is ever removed.

The remembered parts sat in the sorted pool during this run, so a run from the second half was compared against its nearest remembered neighbor as well as against the rest of the second half.

Without memory, the second half would have added everything it produced. With memory, it only added 9,337 — the memory already covered the rest.

## Run 3: the second half again

```
MEMORY   alice.memory
  before this signal: 30124 parts, from alice-first-half.txt (...), alice-second-half.txt (...)
  level  produced  confirmed      added  not seen this time
      0     19833      19833          0                3583
      1      6699       5914          5                 785
      2         4          4          0                   3
      3         1          1          0                   1
  after: 30129 parts, saved
```

Same signal, second time. Level 0: 19,833 produced, 19,833 confirmed, zero added. Level 1: five parts added. Those five came from class-in-slot parts — stretches that differed only by members of one class in one spot. They were not produced the first time because the classes are computed over the pool, and the pool was bigger this time, so the class now had the members it needed. A third pass would find even fewer.

The first read produced 19,925; the second reaches 19,833 of them. The 92 it does not reach are first-half parts the first read exposed by colliding a second-half run with a first-half neighbour; a part minted on that first read now sorts between the two, so the collision yields it instead. What a signal produces depends on its neighbours in the pool at the time: the same pool, read twice, agrees to within half a percent.

The MINT line of this run shows nothing minted in nine rounds, and the line under it the remembered parts this signal produced again, round by round: 11,882, then 2,972, 946, 250, 53, 12, 5, 3, 0 — the same falling-to-zero shape as minting, and the same stopping rule.

That is the loop running out of new things: 30,124 → 30,129, then stable.

## Run 4: German, against the English memory

```
MEMORY   alice.memory
  before this signal: 30129 parts, from alice-first-half.txt, alice-second-half.txt, alice-second-half.txt
  level  produced  confirmed      added  not seen this time
      0     32784      14797      17987                8619
      1     21259       4181      15017                2522
      2         9          0          9                   7
      3         1          0          1                   2
  after: 63143 parts, saved
```

A different language against the memory of the first. 14,797 confirmed: the parts the two alphabets share — the letters and the short pieces that occur in both languages (`in`, `er`, `st`, `en`), reached by German runs colliding with English neighbours. 17,987 added: everything German builds that English never produced. 8,619 not seen: the English parts the German text does not reach.

This is the same bridge from `examples/german`, but done by memory instead of a separate script. What is the same across the two signals is what gets confirmed.

## What this adds up to

Every run with memory starts with three numbers per level: confirmed, added, not seen. A signal read twice confirms what it produced the first time, to within the few parts whose neighbour in the pool has changed, and adds nothing (or almost nothing). A new signal adds what it brings and confirms what it shares. Nothing is ever removed — a part not seen this time keeps its place and its count. The additions shrink as the memory covers more of what the signals contain, which is the same shape the levels have inside one run: a lot, then some more, then a little, then almost nothing, then stable.
