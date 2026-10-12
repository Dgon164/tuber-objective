# Breakdown: a 15-bit machine (Apollo Guidance Computer)

## What goes in

The Virtual AGC project publishes the flight software of the Apollo 11 Lunar Module as a public-domain listing. Each word is five octal digits. The Apollo Guidance Computer uses 15-bit words.

`make_rope.py` writes every word as exactly 15 bits, one after another, with no padding and no byte boundaries: 36,864 words into 69,120 bytes. A word starts on a byte boundary only every eighth word — the rest start in the middle of a byte.

`input/luminary099.agc` is the assembly source of the same program: the 92 source files joined into one file, 1.6 MB of text.

Both were run with no setting that names the machine:

```
python discovery.py examples/agc/input/luminary099.rope --lens octal --out examples/agc
python discovery.py examples/agc/input/luminary099.agc  --lens ascii --out examples/agc --separators 2
```

The octal lens shows each word as five octal digits so a reader can line the record up with the published listing. It only changes the display.

## The rope record: frame

```
FRAME
  width  score   least-1 column   most-1 column
   60    0.228   col   1 at 0.315   col  27 at 0.543
   30    0.216   col  16 at 0.321   col  27 at 0.536
   45    0.214   col  16 at 0.320   col  42 at 0.533
   15    0.211   col   1 at 0.321   col  12 at 0.532
   55    0.098
  picked width 60
    fold to 15: columns differ by 0.0040 on average (wobble by chance 0.0053) -> same
    fold to 30: columns differ by 0.0033 on average (wobble by chance 0.0053) -> same
  chosen width 15
```

Widths 15, 30, 45, and 60 all stand apart from every other width (0.21–0.23 versus 0.10 and below). The score picked 60, but the fold step found that the 60 columns are the 15 columns repeated four times, within the wobble you would expect by chance at that many rows. The smallest width that fits is 15. The record read the word size of the machine from a bit stream that has no byte boundaries in it.

The column rates at width 15:

```
0.380 0.321 0.480 0.393 0.411 0.415 0.408 0.411 0.454 0.441 0.406 0.455 0.532 0.477 0.484
```

Columns 0 and 1 are 1 less often than the others. Column 12 is 1 most often. Someone who knows the AGC knows the top three bits hold the opcode. Discovery does not know that — it just shows which columns have which habits.

## The rope record: words

```
WORDS   36864 words, 9328 distinct
  00006   1717
  00000    524
  10000    403
  04616    323
  34755    322
  00001    284
  00002    277
  77624    260

SEPARATOR   the most common word: 00006
```

The most common word, 00006, becomes the separator. In the AGC instruction set, word 00006 is `TC 6`, which the assembler writes as `EXTEND` — the prefix that every extended instruction needs. So the separator Discovery picked, just by counting, is the instruction prefix. A run is what sits between one EXTEND and the next.

FOLLOWS shows what comes after the prefix:

```
  00006 -> 03012   35
  00006 -> 50116   26
  00006 -> 34755   23
  00006 -> 05012   23
```

And pairs that have nothing to do with the prefix:

```
  04616 -> 20476   44        04616 -> 20334   24
  05353 -> 04024   43        05353 -> 04022   20
  06037 -> 77624   42        06037 -> 77650   18
```

## Checking a word against the source

The assembly source is open, so a reader can check what these words mean. A subroutine called with `TC X` lives at address X, and the first words of each subroutine are in the source. For example `BANKCALL` begins:

```
BANKCALL    DXCH    BUF2        # SAVE INCOMING A,L.
            INDEX   Q           # PICK UP CADR.
            CA      0
            INCR    Q           # SO WE RETURN TO THE LOC. AFTER THE CADR.
```

Those instructions turn into a word pattern starting with `52xxx` followed by `50002 30000 24002`. Searching the listing for that pattern finds it at address 04616. Doing the same for the other common words:

| word | times in rope | the subroutine at that address | what follows the call |
|---|---|---|---|
| 04616 | 323 | BANKCALL | an address being called |
| 06037 | 238 | INTPRET (the interpreter) | interpreter words in negative form |
| 05353 | 120 | PHASCHNG (phase change) | one argument word |
| 04674 | 64 | IBNKCALL | an address being called |
| 04635 | 61 | POSTJUMP | an address being called |

So `04616 -> 20476` is a call to BANKCALL with its argument. `06037 -> 77624` is a jump into the interpreter followed by its first instruction word. And 00002 is `TC Q`, which the assembler writes as `RETURN` — it is the densest part in the parts table (inside 178 larger parts), which is where a return instruction would be: at the end of many different runs.

## The source record

The second record is of the assembly text. Runs between tabs and spaces:

```
RUNS   257599 runs between separators, 42490 distinct
  #          14597
  THE         3960
  TC          3793
  TO          2942
  TS          2418
  TCF         2161
  CAF         1422
  CA          1349
  EXTEND\n    1318
```

And pairs of runs:

```
  EXTEND\n   -> BZF         294
  CCS        -> A\n         280
  EXTEND\n   -> MP          224
  BANKCALL\n -> CADR        205
  TC         -> BANKCALL\n  199
```

Set the two records next to each other:

| in the rope | in the source |
|---|---|
| 00006 is the most common word (1,717) | EXTEND is among the most common runs (1,318) |
| 00006 is followed by 03012, 50116, 34755 | EXTEND is followed by BZF, MP, DCA |
| 04616 is followed by a steady set of words | TC is followed by BANKCALL; BANKCALL is followed by CADR |
| 00002 sits inside 178 parts | RETURN ends routines throughout |

Neither record knows the other exists. They line up because they are two recordings of the same program.

## Levels

```
rope:    8538 parts, then +11, then +1
source:  126406 parts, then +121058, then +11, then +1
```

The rope stops early: its 1,717 runs between EXTENDs are 1,665 different, the level-1 separator only appears a few times, and there is little to collide. The source goes further: level 1 cuts at `#` (the comment mark), so a level-1 run is a stretch of code up to a comment. Its densest parts are the idioms: `TC BANKCALL` (inside 310 stretches), `CAF ZERO` 287, `CCS A` 273. Its ENDINGS are the instruction right before a comment (`+TS` 1076, `+EXTEND` 1013) and its BEGINNINGS are how a comment opens (`TO+` 1798, `FOR+` 1744, `IN+` 1732, `IF+` 1726, `AND+` 1609, `SET+` 1484) — the writing style of the people who built it.

## What the record does not do

It does not name an instruction. It does not say what the program is for. It finds the word size, the most common word, what follows what, which words sit inside many others, and which pairs repeat. Naming is something you lay over the record afterward — here, using the published listing and the source.

## The memory limit this example found

The first run of the 1.6 MB source with one separator (the tab) grew the pool past memory: runs between tabs include whole comment phrases, and long unique runs produce many long parts. Two things came from that:

- A pair of neighbors only gets compared when one of them is new from the last round (same result, about half the time).
- `--cap` (default 1,000,000 parts) stops the loop and says so in the record.

With `--separators 2` (tab and space) the source runs in well under a minute, three levels and all; about half of that is writing the record (the JSON lists every connection in both directions, and for this file it is by far the largest thing the run writes).
