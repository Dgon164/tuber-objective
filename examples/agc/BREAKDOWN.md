# Breakdown: a 15-bit machine (the Apollo Guidance Computer)

## The input

The Apollo Guidance Computer, or AGC, was the computer on board the Apollo spacecraft. The Virtual AGC project publishes the flight software of the Apollo 11 Lunar Module as a listing, the assembled program printed out one numeric word per line, in the public domain. Each word in the listing is written as 5 octal digits. Octal is base 8: each digit runs from 0 to 7 and stands for 3 bits, so 5 digits make 15 bits. The AGC used 15-bit words.

The script `make_rope.py` turns the listing into a file of raw bits. It writes each word as exactly 15 bits, one after another, with no padding and no regard for byte boundaries. The file is called the rope because the AGC kept its program in what was called rope memory, with the bits woven in by wire. The script writes 36,864 words into 69,120 bytes. Only every eighth word starts at the beginning of a byte; the other seven start partway through one. The author made the layout hard on purpose, to see whether Discovery could find the word width anyway.

The file `input/luminary099.agc` is the assembly source of the same program: the program as its authors wrote it, with instruction names and comments instead of numbers, all 92 source files joined into one. It is 1.6 MB of text.

Discovery read both files with no option that names the machine:

```
python discovery.py examples/agc/input/luminary099.rope --lens octal --out examples/agc
python discovery.py examples/agc/input/luminary099.agc  --lens ascii --out examples/agc --separators 2
```

The `--lens octal` option is a display setting. It prints each 15-bit word as 5 octal digits, so you can compare the record with the listing. It changes only how the output looks.

## The rope record: FRAME

The program's first step is to find how wide one unit of the file is. It tries many widths. For each one it lays the bits out in rows of that width and measures how often each column is 1. The score for a width is the gap between the column that is 1 most often and the column that is 1 least often. Then, for the best width, it checks whether that width is really a smaller width repeated: it folds the columns down to the smaller width and sees whether they match. This is the FRAME table.

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

Widths 15, 30, 45, and 60 score between 0.21 and 0.23. Every other width scores 0.10 or less. By score alone the program picked 60. Then the fold check compared 60 against the smaller widths.

It found that the 60 columns are the 15 columns repeated four times. The difference between them is within what chance alone would produce at this number of rows (the "wobble" in the output). The smallest width that fits is 15. So the program found the machine's word width from a stream of bits that had no byte boundaries to help it.

The column rates at width 15:

```
0.380 0.321 0.480 0.393 0.411 0.415 0.408 0.411 0.454 0.441 0.406 0.455 0.532 0.477 0.484
```

Columns 0 and 1 are 1 less often than the rest, and column 12 is 1 most often. Someone who knows the AGC knows that the top 3 bits of each word hold the opcode, the bits that say which operation an instruction performs. Discovery doesn't know that. It shows only how often each column is 1.

## The rope record: WORDS

Next the program cuts the file into 15-bit units and counts how many times each different one appears. The record calls these units words. Then it takes the most common word as the divider, which the record calls the separator.

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

The most common word, 00006, becomes the separator. In the AGC instruction set, 00006 is `TC 6`, and the assembler, the tool that turns the written source into numeric words, writes `TC 6` as `EXTEND`. The AGC has more instructions than its 3 opcode bits can name, so some instructions need a marker word in front of them, and EXTEND is that marker. So the divider that Discovery picked from counts alone is the instruction prefix. A run is the stretch between two separators, which here means the code between one EXTEND and the next.

The FOLLOWS table counts how often each word comes right after each other word. It shows what comes right after the prefix:

```
  00006 -> 03012   35
  00006 -> 50116   26
  00006 -> 34755   23
  00006 -> 05012   23
```

It also shows pairs that have nothing to do with the prefix:

```
  04616 -> 20476   44        04616 -> 20334   24
  05353 -> 04024   43        05353 -> 04022   20
  06037 -> 77624   42        06037 -> 77650   18
```

## Check a word against the source

The assembly source is public, so you can check what these words mean. `TC X` is the instruction that jumps to the routine at address X, so a routine that the code calls with `TC X` lives at address X. The first instructions of each routine are in the source. For example, `BANKCALL` starts with these lines:

```
BANKCALL    DXCH    BUF2        # SAVE INCOMING A,L.
            INDEX   Q           # PICK UP CADR.
            CA      0
            INCR    Q           # SO WE RETURN TO THE LOC. AFTER THE CADR.
```

Assembled, these instructions become a pattern of words that starts with `52xxx` and continues `50002 30000 24002`. Searching the listing for that pattern finds it at address 04616. Doing the same for the other common words gives this table:

| word | times in the rope | the routine that lives at that address | what comes after the call |
|---|---|---|---|
| 04616 | 323 | BANKCALL | the address that the code calls |
| 06037 | 238 | INTPRET (the interpreter) | the interpreter's instruction words, stored as negative numbers |
| 05353 | 120 | PHASCHNG (phase change) | 1 argument word |
| 04674 | 64 | IBNKCALL | the address that the code calls |
| 04635 | 61 | POSTJUMP | the address that the code calls |

So `04616 -> 20476` is a call to BANKCALL followed by its argument. `06037 -> 77624` is a jump into the interpreter followed by the interpreter's first instruction word. The word 00002 is `TC Q`, the jump back to wherever the routine was called from; the assembler writes it as `RETURN`. The record's PARTS BY DENSITY table counts, for each part, how many other parts contain it, and 00002 has the highest count of all (it sits inside 178 larger parts). That is the right result for a return instruction, because a return sits at the end of many different runs.

## The source record

The second record is of the assembly text. Here the units are bytes, and the `--separators 2` option tells the program to use the two most common units as dividers instead of one. Those are the tab and the space, so the runs are the words of the text:

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

The RUN FOLLOWS table counts which run comes after which:

```
  EXTEND\n   -> BZF         294
  CCS        -> A\n         280
  EXTEND\n   -> MP          224
  BANKCALL\n -> CADR        205
  TC         -> BANKCALL\n  199
```

Put the two records side by side:

| in the rope | in the source |
|---|---|
| The word 00006 is the most common word (1,717). | EXTEND is one of the most common runs (1,318). |
| The words 03012, 50116, 34755 come after 00006. | The runs BZF, MP, DCA come after EXTEND. |
| A fixed set of words comes after 04616. | BANKCALL comes after TC, and CADR comes after BANKCALL. |
| The word 00002 sits inside 178 parts. | RETURN ends routines throughout the source. |

Neither record knows the other exists. They agree because both come from the same program.

## LEVELS

When a level is done, the program treats each run as a single unit and does everything again one level up, with the most common run as the new divider. The LEVELS summary for the two records:

```
rope:    8538 parts, then +11, then +1
source:  126406 parts, then +121058, then +11, then +1
```

The rope stops early. It has 1,717 runs between EXTENDs, and 1,665 of them are different. The level-1 separator occurs only a few times, so there is little to compare.

The source goes further. At level 1 it is cut at `#`, the comment marker, so a level-1 run is a stretch of code up to a comment.

The parts of the source with the highest density, the ones that sit inside the most other parts, are the patterns that occur many times:

- `TC BANKCALL`, inside 310 runs
- `CAF ZERO`, inside 287 runs
- `CCS A`, inside 273 runs

The level-1 ENDINGS table shows the instruction that comes right before a comment (`+TS` 1076, `+EXTEND` 1013). The BEGINNINGS table shows the first word of a comment (`TO+` 1798, `FOR+` 1744, `IN+` 1732, `IF+` 1726, `AND+` 1609, `SET+` 1484). The first words of the comments show the writing habits of the people who wrote the program.

## What the record does not do

The record doesn't name a single instruction, and it doesn't say what the program is for. What it finds is:

- the word width
- the most common word
- the word that comes after each word
- the words that sit inside many other words
- the pairs that repeat

The names go on top of the record after the run. Here they come from the listing and the source.

## The memory limit this example found

The first time the 1.6 MB source was run with one separator (the tab), the pool of parts grew bigger than the computer's memory. The runs between tabs include whole comment phrases, and long runs that occur only once produce many long parts. This led to two changes in the program:

- The program now compares two neighboring parts only when one of them is new since the last round. The result is the same, in about half the time.
- The `--cap` option (default 1,000,000 parts) stops the loop when the pool reaches that size and says so in the record.

With `--separators 2` (tab and space), the source runs in well under a minute, all three levels included. Writing the record takes about half of that time. The JSON record lists every connection in both directions, and for this file it is much larger than the other outputs of the run.
