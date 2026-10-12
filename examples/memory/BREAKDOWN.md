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

`alice-first-half.txt` and `alice-second-half.txt` are the two halves of Alice, cut at a line break near the middle (72,215 and 72,180 bytes). `ep-00-01-17.de` is the German text from `examples/german`.

## Run 1: the first half, starting from nothing

```
MEMORY   alice.memory
  before this signal: 0 parts, from nothing
  level  produced  confirmed      added  not seen this time
      0     14079          0      14079                   0
      1      2485          0       2189                   0
  after: 16272 parts, saved
```

Everything is new. Nothing was in memory to confirm. 16,272 parts go into the memory file.

## Run 2: the second half, against the first

```
MEMORY   alice.memory
  before this signal: 16272 parts, from alice-first-half.txt (72215 bytes, frame 8)
  level  produced  confirmed      added  not seen this time
      0     21278      11941       9337                2138
      1      6967       1664       4510                 525
  after: 30124 parts, saved
```

The second half produces 21,278 parts at level 0. Of those, 11,941 were already in memory from the first half — the letters, the common words, the common pieces of words. 9,337 are new. 2,138 parts the first half produced do not show up in the second half (names and words that only appear early in the book). Those stay in memory — nothing is ever removed.

The remembered parts sat in the sorted pool during this run, so a run from the second half was compared against its nearest remembered neighbor as well as against the rest of the second half.

Without memory, the second half would have added everything it produced. With memory, it only added 9,337 — the memory already covered the rest.

## Run 3: the second half again

```
MEMORY   alice.memory
  before this signal: 30124 parts, from alice-first-half.txt (...), alice-second-half.txt (...)
  level  produced  confirmed      added  not seen this time
      0     21278      21278          0                2138
      1      6971       6174          5                 525
      2         4          4          0                   3
      3         1          1          0                   1
  after: 30129 parts, saved
```

Same signal, second time. Level 0: 21,278 produced, 21,278 confirmed, zero added. Level 1: five parts added. Those five came from class-in-slot parts — stretches that differed only by members of one class in one spot. They were not produced the first time because the classes are computed over the pool, and the pool was bigger this time, so the class now had the members it needed. A third pass would find even fewer.

That is the loop running out of new things: 30,124 → 30,129, then stable.

## Run 4: German, against the English memory

```
MEMORY   alice.memory
  before this signal: 30129 parts, from alice-first-half.txt, alice-second-half.txt, alice-second-half.txt
  level  produced  confirmed      added  not seen this time
      0     36958      18971      17987                4445
      1     22577       5421      15017                1282
  after: 63143 parts, saved
```

A different language against the memory of the first. 18,971 confirmed: the parts the two alphabets share — the letters and the short pieces that occur in both languages (`in`, `er`, `st`, `en`). 17,987 added: everything German builds that English never produced. 4,445 not seen: the English parts the German text does not contain.

This is the same bridge from `examples/german`, but done by memory instead of a separate script. What is the same across the two signals is what gets confirmed.

## What this adds up to

Every run with memory starts with three numbers per level: confirmed, added, not seen. A signal read twice confirms everything and adds nothing (or almost nothing). A new signal adds what it brings and confirms what it shares. Nothing is ever removed — a part not seen this time keeps its place and its count. The additions shrink as the memory covers more of what the signals contain, which is the same shape the levels have inside one run: a lot, then some more, then a little, then almost nothing, then stable.
