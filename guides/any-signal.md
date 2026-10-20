# How to give Discovery any signal

Discovery reads a file as raw bits. Discovery has no list of file
types. For a new kind of signal, you must decide only 2 things. The
first is how to put the signal into a file. The second is the word
width of the thing that you want to see.

## Signals that are already files

Run the program on the file. The frame step finds the word width. The
most common word becomes the separator.

| signal | what the frame step usually finds | what the separator usually is |
|---|---|---|
| plain text (ASCII, UTF-8) | 8 | the space |
| source code | 8 | the space or the tab |
| a compiled program (x86-64) | 64 | the zero word. At `--frame 8`, the zero byte |
| a packed word-machine image | the word width of the machine (15 for the AGC) | the most common instruction of the machine |
| a raw 16-bit audio file (.wav, .raw) | 16 or a multiple of 16 | the most common sample value |
| raw pixels (8-bit grey, RGB) | 8 or 24 | the most common pixel value |
| a CSV or log file | 8 | the comma, or the space |
| a database file with rows of fixed width | the row width in bits, if the width is less than `--widest` | the padding byte |

Files after compression or encryption (zip, png, jpeg, anything that
looks random) give a flat FRAME table and a word table with no repeats.
This result is correct. The signal was made random on purpose. The
frame step is correct to report no structure. For such a file, do these
steps:

1. Decompress the file.
2. Run the program on the contents.

## Signals that are not yet files

Write the signal as bytes. There is 1 rule: write each value in the
same way each time, so that the frame step has something to find.

- **A stream of numbers** (sensor values, prices, a time series): write
  each number as an integer of the same fixed size. Use
  `struct.pack('<h', x)` for 16-bit, and `'<i'` for 32-bit. The frame
  step will find 16 or 32. The separator will be the most common
  value.
- **A state vector** (the activations of a neural net, the variables of
  a simulation): make each value into a fixed number of bits, and pack
  the bits in order. The script `hybrid/net_as_lens.py` packs the
  values with 1 bit per unit (the sign). With 8 bits per unit, each
  unit is a byte. A state is then a row of bytes.
- **Events** (a log of things that occurred): write each event as a
  code of fixed size. The run between separators is then an event
  sequence. The FOLLOWS table becomes the transition table (what
  usually occurs after what).
- **An image**: write the pixels row by row, with 1 byte for each color
  channel. The frame step finds the pixel width. If the image width in
  bits is less than `--widest`, a width equal to the row can also
  appear (1 column for each pixel position). For larger images,
  increase `--widest`.

## Grain

The frame step selects the width at which the columns differ the most.
That width is the size at which the bits of the signal have the most
order. That size is usually, but not always, the size that you want to
look at. The compiled program is the best example. At 64 bits, the
record is about the internal layout of the file. At `--frame 8`, the
record is about the strings and the names that people can read.

Both records are true. If the record at the width that the frame step
found shows little, set the next natural size down (`--frame 8`,
`--frame 16`). Then look again.

## Separators

The most common word is the separator. In some signals, 2 or 3
different words divide the thing that you want to see (space and
newline, tab and space, comma and newline). For such a signal, use
`--separators N`. The record shows when you need this option. A word
with a high density in PARTS BY DENSITY and a whole count of 0 operates
as a separator that the program did not select.

## Size

The cost of the mint loop depends on the number of different runs and
on the length of the runs. The cost does not depend on the file size.
For a file with short runs that repeat (text, code, machine words), the
program ends in seconds at a few hundred kilobytes. A file with long
runs that do not repeat grows the pool faster. Examples are a log in
which each line is different, and a binary that the program reads at
the byte level. The option `--cap` stops the loop and says so.

Use `--limit` to read only the first part of a large file. Or divide
the file into smaller files and run each smaller file.
