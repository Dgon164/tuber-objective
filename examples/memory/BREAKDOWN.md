# Breakdown: memory across files

## What this test is for

"Does the model match reality?" and "Is this the same as that?" are the same question. The program's comparison, the piece of code that checks whether two parts overlap, answers both. The program finds parts by comparing stretches of a file with each other: two stretches that start or end the same way get split into the shared piece and the leftovers, each piece becomes a part, and every part goes into one collection, the pool. It keeps comparing, new parts included, until a round finds nothing new. Memory turns that into a loop across files: the program saves the pool after one run and loads it before the next, so every new file gets compared against every part found in the runs before.

There are four runs and one memory file (`alice.memory`). The runs build the memory file:

```
python ../../discovery.py alice-first-half.txt  --lens ascii --memory alice.memory
python ../../discovery.py alice-second-half.txt --lens ascii --memory alice.memory
python ../../discovery.py alice-second-half.txt --lens ascii --memory alice.memory
python ../../discovery.py ep-00-01-17.de        --lens utf8  --memory alice.memory
```

`alice-first-half.txt` and `alice-second-half.txt` are the two halves of Alice, split at a line break near the middle (72,215 and 72,180 bytes). `ep-00-01-17.de` is the German text from `examples/german`. The memory file is JSON.

One memory holds only files that were read at one unit width. All four files here are read at 8 bits. If a file comes in at a different width, the program refuses it and says why.

A comparison counts only when the current file is part of it. The program doesn't compare two parts that are both already in memory and that the current file hasn't touched, because it compared them when it first made them. So a memory never confirms itself.

When the current file produces a part that is already in memory, the program counts that part as confirmed and compares it with its neighbors in the pool one more time. That way the file can also reach the parts that were built from that part in the previous run.

## Run 1: the first half, with an empty memory

Each record from a run with memory has a MEMORY table. It says what was in memory before this file (the record calls the input file a signal). Then, for each level, it says how many parts this file produced, how many of those were already in memory (confirmed), how many were new (added), and how many parts in memory this file never produced (not seen this time).

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

Every part is new. There was nothing in memory to confirm. The program saves 16,272 parts to the memory file.

## Run 2: the second half, against the first half

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

The second half produces 19,925 parts at level 0. Of those, 10,588 were already in memory from the first half, and the second half produced them again: the letters, the common words, and the common pieces of words. The other 9,337 are new.

The first half made 3,491 parts that the second half never produced. These are names and words that appear only early in the book, and shared starts that only turn up when a particular first-half run is the neighbor. They stay in memory. The program never removes a part.

During this run, the parts from memory sat in the pool in sorted order, alongside the new runs. So each run from the second half was compared both against its nearest neighbor from memory and against the rest of the second half.

Without memory, the second half would add every part it makes. With memory, it added only 9,337. The memory covered the rest.

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

The same file, read a second time. At level 0 it produced 19,833 parts, all 19,833 were confirmed, and none were added. At level 1, five were added.

Those five are parts that carry a class in one position. A class is a group of parts that all take the same set of changes, like the 22 stems that take both `+ed` and `+ing`. When two runs differ only by one member of a class in one position, the program makes a part that has the class in that position instead of a single word. The first run of the second half didn't make these five because the classes are computed over the whole pool, and the pool was smaller then, so the class didn't yet have the members it needed. A third run would find even fewer.

The first run of the second half made 19,925 parts; the second run reaches 19,833 of them. The 92 that it doesn't reach belong to the first half. The first run found them by comparing a second-half run with a first-half neighbor. Now a part that the first run made sits in the pool between the run and that neighbor, so the comparison gives that part instead of the first-half one.

Which parts a file produces depends on what its neighbors in the pool are at the time. Two reads of the same pool agree to within 0.5 percent.

The MINT line of this run, which reports how many new parts each round of comparison made, shows none in 9 rounds. The line under it reports how many parts already in memory this file produced again, round by round: 11,882, then 2,972, 946, 250, 53, 12, 5, 3, 0. It falls to 0 in the same shape as the mint line of a run without memory, and the loop stops by the same rule: when a round finds nothing new.

The loop has nothing left to find: 30,124 parts to 30,129, then no change.

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

This run reads a different language against the memory of the first. The program confirmed 14,797 parts: the parts the two alphabets share, meaning the letters and the short pieces that appear in both languages (`in`, `er`, `st`, `en`). It reached them by comparing German runs with their English neighbors in the pool.

It added 17,987 parts, which is everything German makes that English never made. And 8,619 parts went unseen: the English parts that the German text never reaches.

This is the same bridge as in `examples/german`, built through memory instead of a separate script. The parts that are the same across the two files are exactly the parts the program confirms.

## Summary of the record

Each run with memory starts with three numbers for each level: confirmed, added, not seen. A file read twice confirms what it made the first time, apart from the few parts that now have a different neighbor in the pool, and it adds nothing or almost nothing. A new file adds what it brings and confirms what it shares. The program never removes a part.

A part that isn't seen this time keeps its place and its count. The additions shrink as the memory covers more of what the files contain. The shape is the same as the shape of the levels inside one run: many parts, then some more, then a few, then almost none, then no change.
