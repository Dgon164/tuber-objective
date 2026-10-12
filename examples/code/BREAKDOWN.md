# Breakdown: reading source code and a compiled program

## What goes in

Two inputs. `input/discovery.py` is Discovery's own source file. `input/hello.c` is a 25-line C program that counts letters in its command-line text. `input/hello` is that program compiled with gcc on x86-64 Linux, 16,104 bytes.

```
python discovery.py examples/code/input/discovery.py --lens ascii --out examples/code
python discovery.py examples/code/input/hello --lens ascii --out examples/code
python discovery.py examples/code/input/hello --lens ascii --out examples/code --frame 8
```

## Source code: same process as English, different result

Frame: 8 bits, column 0 at 0.000 -- same as Alice. Words: 88 different ones. The most common is the space, then `-` (from the `# ----` lines in the comments), then e, o, t, r, n, s. Runs between spaces:

```
RUNS   3847 runs between separators, 1598 distinct
  =        141
  in       105
  the       94
  if        88
  for       81
  %         68
  return    43
  else      35
```

In Alice the most common run was `the`. In this file it's `=`, and `in`, `if`, `for`, `return`, `else` are in the top ten. The most common words of the language come up first, and the language here is Python.

The parts ranked by density (how many other parts they show up inside) reveal what makes code different from prose:

```
  part   density   whole   inside (sample)
  (          498       0   (a,, (top, (\n, ()),
  s          469       4   is, as, this, parts
  e          461       2   the, else, one, are
  '          430      10   say(', %s', %d', ',
  ,          367       0   pool,, made_of,, part_of,, ',
```

In Alice the densest parts were e, newline, s, comma, t. Here `(` is first, `'` is fourth, and `)`, `[`, `]`, `:`, `_` are all in the top twenty-five. Endings include `+,`, `+\n`, `+s`, `+)`, `+e`, `+:`. The punctuation that structures code shows up as the stuff most often attached to the front and back of other things.

The crystal entry for `for`:

```
  for   seen 81
    made of    fo, or, f, r
    part of    forced, force, form, forc, fore;, for c in range(w):\n col, []\n for, befor
    followed   w 11, (a, 5, q 5, L 5, p 4, r 3
    preceded   []\n 4, '.join(draw(q) 3, frame) 3, c 3, {}\n 2
```

`for` is followed by `w`, `(a,`, `q` -- loop variables. It's also part of `form` and `force`, which the mint can't tell apart from a form of `for`. The record doesn't know that `for` is a keyword and `form` is a word that starts with the same letters. It records both, and the `changes` line shows them side by side. The `part of` line also shows a level-1 part, `for c in range(w):\n col` -- a stretch between two `=` signs that contains `for`.

## Compiled program at 64 bits: the layout of the file

```
FRAME
  width  score   least-1 column   most-1 column
   64    0.130   col  40 at 0.017   col   2 at 0.148
   32    0.092   col  16 at 0.019   col   1 at 0.112
   48    0.080
   16    0.076
    8    0.060   col   0 at 0.030   col   1 at 0.090
  picked width 64
  chosen width 64
```

The score grows with the width: 8, 16, 32, 64. The 64-bit profile isn't the 32-bit profile repeated (a close call, and the record says so). Here are the column rates at 64 bits, laid out by byte:

```
0.091 0.139 0.148 0.138 0.132 0.118 0.108 0.120   byte 0
0.022 0.092 0.101 0.080 0.080 0.105 0.095 0.123   byte 1
0.019 0.083 0.066 0.056 0.057 0.078 0.068 0.055   byte 2
0.028 0.087 0.077 0.045 0.068 0.062 0.067 0.059   byte 3
0.023 0.084 0.076 0.060 0.066 0.078 0.081 0.085   byte 4
0.017 0.079 0.069 0.043 0.052 0.064 0.049 0.058   byte 5
0.020 0.081 0.071 0.053 0.061 0.068 0.056 0.069   byte 6
0.018 0.075 0.072 0.040 0.067 0.068 0.055 0.057   byte 7
```

The first byte of each 64-bit word has the most 1-bits, and the rate drops off toward the last byte. Why? A small number stored in a 64-bit slot puts its bits in the first byte and leaves the rest as zeros -- when the machine stores the low byte first. That's the little-endian layout of x86-64 (where the least significant byte comes first in memory), read straight from the column rates.

```
WORDS   2013 words, 492 distinct
  0000000000000000  1277
  0800000000000000    30
  0200000000000000    16
```

Small numbers, low byte first, and 63% of all words are zero: the headers and tables of an executable file. The program's actual machine code is a small part of a 16 KB file -- most of it is layout.

## The same program at 8 bits: what the program actually does

`--frame 8` reads the same file one byte at a time. The separator becomes the zero byte (13,477 of 16,104). The runs between zero bytes are the file's readable strings, and the parts table holds them whole:

```
usage: hello TEXT            hello.c              main
strlen@GLIBC_2.2.5           puts@GLIBC_2.2.5     __printf_chk@GLIBC_2.3.4
libc.so.6                    /lib64/ld-linux-x86-64.so.2
GCC: (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0
.text  .data  .bss  .rodata  .symtab  .strtab  .dynsym  .eh_frame
```

Now the record tells us, in whole runs: this file was built from `hello.c` with gcc 13.3 on Ubuntu. It links `libc.so.6` through the x86-64 dynamic loader. It calls `strlen`, `puts`, and `printf`. It has a `main`. And it prints `usage: hello TEXT` when you run it the wrong way. That's the program's purpose and its external calls, read from the bytes. The compiler turned the `printf("usage...\n")` of the source into a `puts` call, and the record shows the `puts`.

Parts by density at this grain:

```
  part   density   whole   inside (sample)
  _          196       0   __gmon_start__, _ITM_registerTMCloneTable, __stack_chk_fail
  .          146       0   .symtab, .note.gnu.property
  t          101       1   __bss_start, .rela.plt, _init
  __          95       0   __gmon_start__, __stack_chk_fail, __bss_start
  H           64       0   H\x85\xc0t\t\xff\xe0, H9\xf8t\x15H\x8b
```

The underscore and the period are the densest parts: symbol names and section names are built on them. The byte `H` (0x48) shows up inside 64 parts, none of them names -- every part it's in is machine code. On x86-64, 0x48 is the prefix that makes an instruction work on 64-bit values, so it starts a large share of instructions. The record doesn't know that. It just shows a byte that is dense inside the non-name parts and never a whole run on its own.

## Levels

Both the source and the binary add almost everything at level 0 and a little at level 1. At level 1, the source cuts at `=` (its most common run) and the binary at the byte grain cuts at `\x01`. The stretches between are almost all unique, so level 1 produces few new parts (169 and 93) and the levels after that add a handful and stop.

## Two grains, two readings

At 64 bits the record describes the file's layout and the machine's word habits. At 8 bits it describes what the program is for and what it calls. Both readings are in the same file. The frame step picks which one the word tables are about, and `--frame` exists so you can do the second reading.
