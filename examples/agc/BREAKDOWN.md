# Breakdown: a 15-bit machine (Apollo Guidance Computer)

## The input

The Virtual AGC project publishes the flight software of the Apollo 11 Lunar Module as a listing in the public domain. Each word in the listing is 5 octal digits (base-8 numbers). The Apollo Guidance Computer uses 15-bit words.

The script `make_rope.py` writes each word as exactly 15 bits, in sequence, with no extra bits and no byte boundaries. The script writes 36,864 words into 69,120 bytes. Only each eighth word starts on a byte boundary. The other words start in the middle of a byte. The author made the layout difficult. The purpose is to see if Discovery can find the word width in this layout.

The file `input/luminary099.agc` is the assembly source of the same program. The file contains all 92 source files in 1 file. The file has 1.6 MB of text.

Discovery read both files with no flag that names the machine:

```
python discovery.py examples/agc/input/luminary099.rope --lens octal --out examples/agc
python discovery.py examples/agc/input/luminary099.agc  --lens ascii --out examples/agc --separators 2
```

The octal lens shows each word as 5 octal digits. Thus you can compare the record with the listing. The lens changes only the display.

## The rope record: FRAME

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

The widths 15, 30, 45, and 60 have scores from 0.21 to 0.23. All other widths have scores of 0.10 or less. The score picked 60. Then the fold step folded 60 to 15. To fold a width is to check if the columns of the width are the columns of a smaller width, repeated.

The fold step found that the 60 columns are the 15 columns repeated 4 times. The difference between the columns is within the noise that occurs by chance at this number of rows. The smallest width that fits is 15. The record found the word width of the machine from a bit stream that has no byte boundaries.

The column rates at width 15 are as follows:

```
0.380 0.321 0.480 0.393 0.411 0.415 0.408 0.411 0.454 0.441 0.406 0.455 0.532 0.477 0.484
```

Columns 0 and 1 are 1 less often than the other columns. Column 12 is 1 most often. A person who knows the AGC knows that the top 3 bits hold the opcode. The opcode is the bits of the instruction that say what the instruction does. Discovery does not know what the top 3 bits hold. Discovery shows only the rate of each column.

## The rope record: WORDS

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

The most common word, 00006, becomes the separator. In the AGC instruction set, the word 00006 is `TC 6`. The assembler writes `TC 6` as `EXTEND`. EXTEND is the prefix that each extended instruction needs. Thus the separator that Discovery picked from the count alone is the instruction prefix. A run is the sequence between one EXTEND and the next EXTEND.

The FOLLOWS table shows what comes directly after the prefix:

```
  00006 -> 03012   35
  00006 -> 50116   26
  00006 -> 34755   23
  00006 -> 05012   23
```

The FOLLOWS table also shows pairs that have no relation to the prefix:

```
  04616 -> 20476   44        04616 -> 20334   24
  05353 -> 04024   43        05353 -> 04022   20
  06037 -> 77624   42        06037 -> 77650   18
```

## Check a word against the source

The assembly source is public. Thus you can check what these words mean. A subroutine that the code calls with `TC X` is at address X. The first words of each subroutine are in the source. For example, `BANKCALL` starts with these lines:

```
BANKCALL    DXCH    BUF2        # SAVE INCOMING A,L.
            INDEX   Q           # PICK UP CADR.
            CA      0
            INCR    Q           # SO WE RETURN TO THE LOC. AFTER THE CADR.
```

These instructions become a word pattern that starts with `52xxx` and continues with `50002 30000 24002`. A search of the listing for this pattern finds the pattern at address 04616. The same steps for the other common words give this table:

| word | times in rope | the subroutine at the address of the word | the words after the call |
|---|---|---|---|
| 04616 | 323 | BANKCALL | the address that the code calls |
| 06037 | 238 | INTPRET (the interpreter) | interpreter words in negative form |
| 05353 | 120 | PHASCHNG (phase change) | 1 argument word |
| 04674 | 64 | IBNKCALL | the address that the code calls |
| 04635 | 61 | POSTJUMP | the address that the code calls |

Thus `04616 -> 20476` is a call to BANKCALL with its argument. The pair `06037 -> 77624` is a jump into the interpreter and then the first instruction word of the interpreter. The word 00002 is `TC Q`. The assembler writes `TC Q` as `RETURN`. The word 00002 is the part with the highest density in the parts table (inside 178 larger parts). The highest density is the correct result for a return instruction, because a return instruction is at the end of many different runs.

## The source record

The second record is the record of the assembly text. The runs between tabs and spaces are as follows:

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

The pairs of runs are as follows:

```
  EXTEND\n   -> BZF         294
  CCS        -> A\n         280
  EXTEND\n   -> MP          224
  BANKCALL\n -> CADR        205
  TC         -> BANKCALL\n  199
```

Put the 2 records next to each other:

| in the rope | in the source |
|---|---|
| The word 00006 is the most common word (1,717). | EXTEND is one of the most common runs (1,318). |
| The words 03012, 50116, 34755 come after 00006. | The runs BZF, MP, DCA come after EXTEND. |
| A constant set of words comes after 04616. | BANKCALL comes after TC. CADR comes after BANKCALL. |
| The word 00002 is inside 178 parts. | RETURN ends routines in the whole source. |

No record knows that the other record exists. The 2 records agree because each record comes from the same program.

## LEVELS

```
rope:    8538 parts, then +11, then +1
source:  126406 parts, then +121058, then +11, then +1
```

The rope stops early. The rope has 1,717 runs between EXTENDs, with 1,665 different runs. The level-1 separator occurs only a few times. Thus there is little to compare. The source goes to more levels. At level 1, the source cuts at `#` (the comment marker). To cut a signal is to divide the signal into runs at each separator. Thus a level-1 run is a sequence of code up to a comment.

The parts of the source with the highest density are the patterns that occur many times:

- `TC BANKCALL`, inside 310 runs
- `CAF ZERO`, inside 287 runs
- `CCS A`, inside 273 runs

The ENDINGS table shows the instruction directly before a comment (`+TS` 1076, `+EXTEND` 1013). The BEGINNINGS table shows the first word of a comment (`TO+` 1798, `FOR+` 1744, `IN+` 1732, `IF+` 1726, `AND+` 1609, `SET+` 1484). The first words of the comments show the style of the people who wrote the program.

## The limits of the record

The record does not name an instruction. The record does not say what the program is for. The record finds:

- the word width
- the most common word
- the word that comes after each word
- the words that are inside many other words
- the pairs that repeat

You put the names on top of the record after the run. Here, the names come from the listing and the source.

## The memory limit that this example found

In the first run of the 1.6 MB source with 1 separator (the tab), the pool grew larger than the memory of the computer. The runs between tabs include whole comment phrases. Long unique runs make many long parts. This result caused 2 changes:

- The program compares a pair of neighbors only when one of the neighbors is new from the last round. The result is the same, in approximately half the time.
- The flag `--cap` (default 1,000,000 parts) stops the loop and says so in the record.

With `--separators 2` (tab and space), the source runs in much less than 1 minute, with all 3 levels. The write of the record takes approximately half of that time. The JSON lists each connection in both directions. For this file, the JSON is much larger than the other outputs of the run.
