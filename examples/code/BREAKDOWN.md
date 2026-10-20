# Breakdown: source code and a compiled program

## The input

There are two inputs. `input/discovery.py` is the source code of Discovery itself. `input/hello.c` is a 25-line C program that counts the letters in the text you give it on the command line, and `input/hello` is that same program after the gcc compiler turned it into a runnable file on x86-64 Linux. The runnable file is 16,104 bytes.

```
python discovery.py examples/code/input/discovery.py --lens ascii --out examples/code
python discovery.py examples/code/input/hello --lens ascii --out examples/code
python discovery.py examples/code/input/hello --lens ascii --out examples/code --frame 8
```

## Source code: the same steps as English, with a different result

The program first works out how wide one unit of the file is. It tries many widths, lays the bits out in rows of each width, and measures how often each column of bits is 1; the width where the columns differ the most wins. This is the FRAME table, and for the source file it shows 8 bits with column 0 at 0.000, the same as for Alice. The WORDS table, which counts each different unit, shows 88 different ones. The most common is the space, then `-` (from the `# ----` lines in the comments), then e, o, t, r, n, s. The program takes the most common unit, the space, as the divider and cuts the file at every space. Each stretch between two spaces is a run. The RUNS table lists them:

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

In Alice the most common run was `the`. Here it is `=`, and `in`, `if`, `for`, `return`, `else` are all in the top ten. The most common words of the language come first, and the language here is Python.

Next the program compares the runs with each other. When two runs share a start or an end, it splits them into the shared piece and the leftovers, and each piece becomes a part. It keeps doing this with the new parts until a round finds nothing new. For each part it then counts how many other parts contain it, which the record calls the part's density, and how many times the part appeared on its own as a complete run. The PARTS BY DENSITY table lists the parts with the highest density first, and it shows what makes code different from English prose:

```
  part   density   whole   inside (sample)
  (          498       0   (a,, (top, (\n, ()),
  s          469       4   is, as, this, parts
  e          461       2   the, else, one, are
  '          430      10   say(', %s', %d', ',
  ,          367       0   pool,, made_of,, part_of,, ',
```

In Alice the parts with the highest density were e, newline, s, comma, t. Here `(` is first and `'` is fourth, and `)`, `[`, `]`, `:`, `_` are all in the top 25. The endings, meaning the leftovers that attach to the end of one part to make another, include `+,`, `+\n`, `+s`, `+)`, `+e`, `+:`. The punctuation that gives code its shape shows up as the parts that most often attach to the front and the back of other parts.

The CRYSTAL table gathers everything the record knows about one run into a single entry, like a dictionary entry: the smaller parts it is made of, the larger parts it is part of, what follows it, and what comes before it. The entry for `for` looks like this:

```
  for   seen 81
    made of    fo, or, f, r
    part of    forced, force, form, forc, fore;, for c in range(w):\n col, []\n for, befor
    followed   w 11, (a, 5, q 5, L 5, p 4, r 3
    preceded   []\n 4, '.join(draw(q) 3, frame) 3, c 3, {}\n 2
```

The words that come after `for` are `w`, `(a,`, `q`: loop variables. `for` is also part of `form` and `force`. The program makes a new part whenever two parts start or end the same way, and it can't tell `form` apart from a form of `for`.

The record doesn't know that `for` is a keyword, or that `form` is a word that just happens to start with the same letters. It keeps both. The `changes` line of the entry lists the two side by side. The `part of` line also shows a level-1 part, `for c in range(w):\n col`. When the program has finished one level, it treats each run as a single unit and does everything again one level up, with the most common run as the new divider. For this file that divider is `=`, so this level-1 part is a stretch between two `=` signs that contains `for`.

## The compiled program at 64 bits: the layout of the file

Now the runnable file. The program tries many unit widths and scores each one by how much its columns differ. This is the FRAME table.

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

The score goes up with the width: 8, 16, 32, 64. The program also checks whether the columns at 64 bits are just the columns at 32 bits repeated twice. They aren't, though the difference is small, and the record says so. Here are the column rates at 64 bits, laid out one byte per row:

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

The first byte of each 64-bit unit has the most 1 bits, and the rate falls off toward the last byte. The reason is this: the machine stores the low byte of a number first, so a small number sitting in a 64-bit slot puts its bits in the first byte and leaves the other bytes at 0.

That is the little-endian layout of x86-64, in which the least significant byte comes first in memory. The column rates alone are enough to show it, and you can check it against any description of how x86-64 stores numbers.

```
WORDS   2013 words, 492 distinct
  0000000000000000  1277
  0800000000000000    30
  0200000000000000    16
```

The units are small numbers with the low byte first. The unit 0 makes up 63 percent of all units. These are the headers and tables of an executable file. The actual machine code of the program is a small part of a 16 KB file. Most of the file is layout.

## The same program at 8 bits: what the program is for

The `--frame 8` option sets the unit width to 8 bits by hand, so the program reads the same file one byte at a time. Now the most common unit is the zero byte (13,477 of the 16,104 bytes), so the zero byte becomes the divider, and the runs between zero bytes are the text strings stored in the file. The parts table holds the whole strings:

```
usage: hello TEXT            hello.c              main
strlen@GLIBC_2.2.5           puts@GLIBC_2.2.5     __printf_chk@GLIBC_2.3.4
libc.so.6                    /lib64/ld-linux-x86-64.so.2
GCC: (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0
.text  .data  .bss  .rodata  .symtab  .strtab  .dynsym  .eh_frame
```

Now the record shows, as whole runs, these facts about the file:

- gcc 13.3 on Ubuntu built it from `hello.c`
- it links `libc.so.6` through the x86-64 dynamic loader
- it calls `strlen`, `puts`, and `printf`
- it has a `main`
- it prints `usage: hello TEXT` when you run it the wrong way

The record read all of this from the bytes. It is what the program is for and what it calls outside itself. One detail: the source said `printf("usage...\n")`, but the compiler turned that into a call to `puts`, and the record shows the `puts`.

The PARTS BY DENSITY table at width 8, the parts with the most other parts containing them, looks like this:

```
  part   density   whole   inside (sample)
  _          196       0   __gmon_start__, _ITM_registerTMCloneTable, __stack_chk_fail
  .          146       0   .symtab, .note.gnu.property
  t          101       1   __bss_start, .rela.plt, _init
  __          95       0   __gmon_start__, __stack_chk_fail, __bss_start
  H           64       0   H\x85\xc0t\t\xff\xe0, H9\xf8t\x15H\x8b
```

The underscore and the period have the highest density, because the symbol names and the section names are full of them. The byte `H` (0x48) sits inside 64 parts, and not one of them is a name. Every part that contains `H` is machine code.

On x86-64, 0x48 is the prefix byte that makes an instruction work on 64-bit values, so many instructions start with it. The record doesn't know what 0x48 does. It shows only a byte with a high density inside the parts that aren't names, and that never appears as a whole run on its own.

## LEVELS

When a level is done, the program treats each run as a single unit and does everything again one level up: it takes the most common run as the new divider, cuts at it, and compares the new runs. The LEVELS table summarizes each level in one row.

The source file and the runnable file each add almost all of their parts at level 0 and a few at level 1. At level 1, the source is cut at `=`, its most common run. The runnable file at width 8 is cut at the byte `\x01`.

The runs between those dividers are almost all different from each other, so level 1 makes few new parts (169 for the source and 93 for the runnable file). The levels after that add a handful of parts and then stop.

## Two widths, two results

At 64 bits, the record describes the layout of the file and the way the machine stores numbers. At 8 bits, it describes what the program is for and what it calls. Both come from the same file. The FRAME step picks the width that the unit tables use, and the `--frame` option exists so that you can get the second result as well.
