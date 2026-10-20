# How to give Discovery any kind of file

Discovery reads a file as raw bits and has no list of file types. For a
new kind of signal you only decide two things: how to put the signal
into a file, and how wide one unit of the thing you want to see is.

## Signals that are already files

Run the program on the file. The program works out how wide one unit
is by itself; that search is the frame step, and it tries each width
and keeps the one where the bit patterns line up. It calls each unit a
word. The most common word then becomes the separator, the point where
the program cuts the file into pieces, and each piece between two
separators is a run.

| signal | the unit width the frame step usually finds | what the separator usually is |
|---|---|---|
| plain text (ASCII, UTF-8) | 8 | the space |
| source code | 8 | the space or the tab |
| a compiled program (x86-64) | 64 | the zero word. With `--frame 8`, the zero byte |
| a packed word-machine image | the machine's own word width (15 for the AGC) | the machine's most common instruction |
| a raw 16-bit audio file (.wav, .raw) | 16 or a multiple of 16 | the most common sample value |
| raw pixels (8-bit grey, RGB) | 8 or 24 | the most common pixel value |
| a CSV or log file | 8 | the comma, or the space |
| a database file with rows of fixed width | the row width in bits, if that is below `--widest` | the padding byte |

A file that has been compressed or encrypted (zip, png, jpeg, anything
that looks random) gives a flat FRAME table, where every width scores
about the same, and a word table with no repeats. That result is
correct: the signal was made random on purpose, and the frame step is
right to report no structure. For such a file, do this:

1. Decompress the file.
2. Run the program on the contents.

## Signals that are not yet files

Write the signal out as bytes. There is one rule: write each value the
same way every time, so the frame step has something to find.

- **A stream of numbers** (sensor values, prices, a time series): write
  each number as an integer of the same fixed size. Use
  `struct.pack('<h', x)` for 16-bit, and `'<i'` for 32-bit. The frame
  step will find 16 or 32, and the separator will be the most common
  value.
- **A state vector** (the activations of a neural net, the variables of
  a simulation): turn each value into a fixed number of bits, and pack
  the bits in order. The script `hybrid/net_as_lens.py` packs the
  values with one bit per unit, the sign. With 8 bits per unit, each
  unit is a byte, and a state is then a row of bytes.
- **Events** (a log of things that happened): write each event as a
  code of fixed size. Each run between separators is then a sequence of
  events, and the FOLLOWS table, which counts what comes right after
  what, becomes the transition table.
- **An image**: write the pixels row by row, with one byte for each
  color channel. The frame step finds the pixel width. If the image
  width in bits is below `--widest`, a width equal to one row can also
  show up, with one column for each pixel position. For larger images,
  raise `--widest`.

## Which width to look at

The frame step picks the width with the largest difference between its
columns, which is the width where the bits of the signal have the most
order. That is usually, but not always, the width you want to look at.
The compiled program is the best example. At 64 bits, the record is
about the internal layout of the file. At `--frame 8`, it is about the
strings and names that people can read.

Both records are true. If the record at the width the frame step found
shows little, set the next natural size down (`--frame 8`, `--frame
16`) and look again.

## Separators

The most common word is the separator. In some signals, two or three
different words divide the thing you want to see: space and newline,
tab and space, comma and newline. For a signal like that, use
`--separators N`. The record tells you when you need it. The sign is a
word that sits inside a great many other parts, which shows as a high
density in PARTS BY DENSITY, but has a whole count of 0, meaning it
never occurs as a complete piece on its own. A word like that is acting
as a separator the program didn't choose.

## Size

The program compares the pieces of the file in pairs and keeps every
shared part it finds. How long that takes depends on how many different
runs there are and how long they are, not on the size of the file. For
a file with short runs that repeat (text, code, machine words), the
program finishes in seconds at a few hundred kilobytes. A file with
long runs that don't repeat grows the list of parts faster; a log in
which no two lines are the same, or a binary read at the byte level,
are examples. The option `--cap` stops the loop when the list gets too
large, and says so.

Use `--limit` to read only the first part of a large file, or split the
file into smaller files and run each one.
