# Breakdown: memory across signals

## The purpose of the test

The question "Does the model match reality?" and the question "Is this the same as that?" are the same question. The comparator answers both questions. The comparator is the code of the program that checks if 2 parts overlap. The memory makes the loop. The program saves the pool after 1 run and loads the pool before the next run. Thus the program compares each new signal against all parts from the runs before.

There are 4 runs and 1 memory file (`alice.memory`). The runs make the memory file:

```
python ../../discovery.py alice-first-half.txt  --lens ascii --memory alice.memory
python ../../discovery.py alice-second-half.txt --lens ascii --memory alice.memory
python ../../discovery.py alice-second-half.txt --lens ascii --memory alice.memory
python ../../discovery.py ep-00-01-17.de        --lens utf8  --memory alice.memory
```

The files `alice-first-half.txt` and `alice-second-half.txt` are the 2 halves of Alice. The 2 halves divide at a line break near the middle (72,215 and 72,180 bytes). The file `ep-00-01-17.de` is the German text from `examples/german`. The memory file is JSON.

One memory holds signals that the program read at 1 frame. The program reads all 4 signals here at 8 bits. The program does not accept a signal at a different width, and gives the reason.

A comparison counts only when the comparison includes the current signal. The program does not compare 2 parts in memory that the current signal has not reached. The program compared those 2 parts when the program first made them. Thus a memory never confirms itself.

The program confirms a part in memory when the current signal makes the part again. Then the program compares that part with its neighbors one more time. Thus the program can also reach the parts that the program made from that part in the last run.

## Run 1: the first half, with an empty memory

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

All parts are new. There was no part in memory to confirm. The program puts 16,272 parts into the memory file.

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

The second half makes 19,925 parts at level 0. Of these parts, 10,588 were in memory from the first half, and the second half reached these parts again. These parts are the letters, the common words, and the common parts of words. There are 9,337 new parts.

The first half made 3,491 parts that the second half never reached. These parts are names and words that occur only early in the book, and heads that the program finds only with a first-half neighbor. These parts stay in memory. The program never removes a part.

During this run, the parts from memory were in the pool, in order. Thus the program compared a run from the second half against its nearest neighbor in memory and against the rest of the second half.

Without memory, the second half adds all parts that the second half makes. With memory, the second half added only 9,337 parts. The memory covered the rest.

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

The signal is the same signal, a second time. At level 0, the signal made 19,833 parts. The program confirmed 19,833 parts. The program added 0 parts. At level 1, the program added 5 parts.

These 5 parts came from class-in-slot parts. A class-in-slot part is a run that differs from another run only by a member of 1 class in 1 position. The first run did not make these parts, because the program computes the classes over the pool. The pool was larger this time. Thus the class now had the members that the class needed. A third run will find even fewer new parts.

The first run of the second half made 19,925 parts. The second run reaches 19,833 of these parts. The 92 parts that the second run does not reach are parts of the first half. The first run found these 92 parts when the first run compared a run of the second half with a neighbor of the first half. A part that the first run made is now in the pool between the run and the neighbor. Thus the comparison gives that part and not the first-half part.

The parts that a signal makes depend on the neighbors in the pool at that time. The results of 2 reads of the same pool agree to within 0.5 percent.

The MINT line of this run shows that the program minted no parts in 9 rounds. To mint a part is to make a new part from 2 parts that have the same start or the same end. The line under the MINT line shows the parts in memory that this signal made again, round by round. The counts are 11,882, then 2,972, 946, 250, 53, 12, 5, 3, 0. This sequence falls to 0 in the same shape as the mint. The stop rule is the same.

The loop has no more new parts to find: 30,124 parts to 30,129 parts, then no change.

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

This run reads a different language against the memory of the first language. The program confirmed 14,797 parts. These parts are the parts that the 2 alphabets share: the letters and the short parts that occur in both languages (`in`, `er`, `st`, `en`). The program reached these parts when the program compared German runs with English neighbors.

The program added 17,987 parts. These parts are all that German makes and English never made. The program did not see 8,619 parts. These parts are the English parts that the German text does not reach.

The result is the same bridge as in `examples/german`, but through memory and not through a separate script. The parts that are the same across the 2 signals are the parts that the program confirms.

## Summary of the record

Each run with memory starts with 3 numbers for each level: confirmed, added, not seen. A signal that the program reads twice confirms what the signal made the first time. The exception is the few parts that have a different neighbor in the pool. The signal adds no parts, or almost no parts. A new signal adds what the new signal brings and confirms what the new signal shares. The program never removes a part.

A part that the program does not see this time keeps its place and its count. The additions get smaller as the memory covers more of what the signals contain. The shape is the same as the shape of the levels in 1 run: many parts, then some more, then a few, then almost none, then no change.
