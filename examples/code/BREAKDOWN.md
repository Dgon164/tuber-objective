# Breakdown: source code and a compiled program

## The input

There are 2 inputs. The file `input/discovery.py` is the source file of Discovery. The file `input/hello.c` is a C program of 25 lines. The program counts the letters in its command-line text. The file `input/hello` is the same program after gcc compiled the program on x86-64 Linux. The file has 16,104 bytes.

```
python discovery.py examples/code/input/discovery.py --lens ascii --out examples/code
python discovery.py examples/code/input/hello --lens ascii --out examples/code
python discovery.py examples/code/input/hello --lens ascii --out examples/code --frame 8
```

## Source code: the same process as English, with a different result

The FRAME table shows 8 bits, with column 0 at 0.000. The result is the same as for Alice. The WORDS table shows 88 different words. The most common word is the space, then `-` (from the `# ----` lines in the comments), then e, o, t, r, n, s. The runs between spaces are as follows:

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

In Alice, the most common run was `the`. In this file, the most common run is `=`. The runs `in`, `if`, `for`, `return`, `else` are in the top 10. The most common words of the language come first. The language here is Python.

The table below lists the parts in order of density. The density of a part is the number of other parts that contain the part. The table shows what makes code different from English text:

```
  part   density   whole   inside (sample)
  (          498       0   (a,, (top, (\n, ()),
  s          469       4   is, as, this, parts
  e          461       2   the, else, one, are
  '          430      10   say(', %s', %d', ',
  ,          367       0   pool,, made_of,, part_of,, ',
```

In Alice, the parts with the highest density were e, newline, s, comma, t. Here `(` is first and `'` is fourth. The parts `)`, `[`, `]`, `:`, `_` are all in the top 25. The endings include `+,`, `+\n`, `+s`, `+)`, `+e`, `+:`. The punctuation that gives code its structure occurs as the parts that most often attach to the front and the end of other parts.

The crystal entry for `for` is as follows:

```
  for   seen 81
    made of    fo, or, f, r
    part of    forced, force, form, forc, fore;, for c in range(w):\n col, []\n for, befor
    followed   w 11, (a, 5, q 5, L 5, p 4, r 3
    preceded   []\n 4, '.join(draw(q) 3, frame) 3, c 3, {}\n 2
```

The words `w`, `(a,`, `q` come after `for`. These words are loop variables. The word `for` is also part of `form` and `force`. The mint step makes new parts from 2 parts that have the same start or the same end. The mint step does not know the difference between `form` and a form of `for`.

The record does not know that `for` is a keyword. The record does not know that `form` is a word that starts with the same letters. The record keeps both words. The `changes` line shows the 2 words next to each other. The `part of` line also shows a level-1 part, `for c in range(w):\n col`. This level-1 part is a run between 2 `=` signs that contains `for`.

## The compiled program at 64 bits: the layout of the file

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

The score increases with the width: 8, 16, 32, 64. The column rates at 64 bits are not the column rates at 32 bits repeated. The difference is small, and the record says so. The column rates at 64 bits, in rows of 1 byte, are as follows:

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

The first byte of each 64-bit word has the most 1 bits. The rate decreases toward the last byte. The cause is as follows. When the machine stores the low byte first, a small number in a 64-bit slot puts its bits in the first byte. The other bytes stay 0.

The layout is the little-endian layout of x86-64. In the little-endian layout, the least significant byte comes first in memory. The column rates alone show the layout.

```
WORDS   2013 words, 492 distinct
  0000000000000000  1277
  0800000000000000    30
  0200000000000000    16
```

The words are small numbers with the low byte first. The word 0 is 63 percent of all words. These words are the headers and the tables of an executable file. The machine code of the program is a small part of a 16 KB file. Most of the file is layout.

## The same program at 8 bits: the purpose of the program

The flag `--frame 8` reads the same file 1 byte at a time. The separator becomes the zero byte (13,477 of 16,104). The runs between zero bytes are the text strings of the file. The parts table holds the whole strings:

```
usage: hello TEXT            hello.c              main
strlen@GLIBC_2.2.5           puts@GLIBC_2.2.5     __printf_chk@GLIBC_2.3.4
libc.so.6                    /lib64/ld-linux-x86-64.so.2
GCC: (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0
.text  .data  .bss  .rodata  .symtab  .strtab  .dynsym  .eh_frame
```

Now the record shows, in whole runs, these facts about the file:

- gcc 13.3 on Ubuntu made the file from `hello.c`
- the file links `libc.so.6` through the x86-64 dynamic loader
- the file calls `strlen`, `puts`, and `printf`
- the file has a `main`
- the file prints `usage: hello TEXT` when you run the program in the wrong way

The record read these facts from the bytes. These facts are the purpose of the program and its external calls. The compiler changed the `printf("usage...\n")` of the source into a `puts` call. The record shows the `puts`.

The parts by density at width 8 are as follows:

```
  part   density   whole   inside (sample)
  _          196       0   __gmon_start__, _ITM_registerTMCloneTable, __stack_chk_fail
  .          146       0   .symtab, .note.gnu.property
  t          101       1   __bss_start, .rela.plt, _init
  __          95       0   __gmon_start__, __stack_chk_fail, __bss_start
  H           64       0   H\x85\xc0t\t\xff\xe0, H9\xf8t\x15H\x8b
```

The underscore and the period are the parts with the highest density. The symbol names and the section names contain the underscore and the period. The byte `H` (0x48) occurs inside 64 parts. None of these parts is a name. Each part that contains `H` is machine code.

On x86-64, 0x48 is the prefix that makes an instruction operate on 64-bit values. Thus 0x48 starts many of the instructions. The record does not know what 0x48 does. The record shows only a byte that has a high density inside the parts that are not names. The byte is never a whole run on its own.

## LEVELS

The source and the binary each add almost all parts at level 0 and a few parts at level 1. At level 1, the source cuts at `=`, its most common run. To cut a signal is to divide the signal into runs at each separator. At level 1, the binary at width 8 cuts at the byte `\x01`.

The runs between the separators are almost all different from each other. Thus level 1 makes few new parts (169 and 93). The levels after level 1 add a small number of parts and then stop.

## Two widths, two results

At 64 bits, the record describes the layout of the file and the way that the machine stores words. At 8 bits, the record describes the purpose of the program and the calls that the program makes. Both results come from the same file. The frame step picks the width that the word tables use. The flag `--frame` exists so that you can get the second result.
